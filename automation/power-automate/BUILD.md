# Build the Cowork refresh cloud flow

Create this as a solution-aware cloud flow so connection references and
environment variables can move between environments. The flow starts and
monitors the processing job; it never reads or loops over audit records.

## Connections and environment variables

Create these solution environment variables:

| Name | Value |
| --- | --- |
| `CoworkAzureSubscriptionId` | Azure subscription GUID |
| `CoworkAzureResourceGroup` | Resource group containing the ACA Job |
| `CoworkContainerAppsJobName` | Default `cowork-adoption-refresh` |
| `CoworkPowerBIWorkspaceId` | Power BI workspace GUID |
| `CoworkPowerBISemanticModelId` | Power BI semantic-model GUID |

Create:

1. An **HTTP with Microsoft Entra ID** connection for
   `https://management.azure.com`.
2. A **Power BI** connection permitted to refresh the target semantic model and
   read its refresh history.
3. Optional Outlook or Teams connection for generic failure notification.

Assign the ARM connection principal the custom role from
`deploy/CoworkJobStarterRole.json` at the specific ACA Job scope. Job-start
permission is privileged because a caller can submit an execution-template
override; do not grant it broadly.

## Trigger

Add **Recurrence**:

- Frequency: `Day`
- Interval: `1`
- Time zone: the operating time zone
- Run after the UTC day has closed and after the configured six-hour lag
- Trigger concurrency control: **On**
- Degree of parallelism: `1`

## Variables

Add these actions:

| Action name | Type | Initial value |
| --- | --- | --- |
| `Initialize_SubscriptionId` | String variable `SubscriptionId` | Insert `CoworkAzureSubscriptionId` environment-variable dynamic content |
| `Initialize_ResourceGroup` | String variable `ResourceGroup` | Insert `CoworkAzureResourceGroup` environment-variable dynamic content |
| `Initialize_JobName` | String variable `JobName` | Insert `CoworkContainerAppsJobName` environment-variable dynamic content |
| `Initialize_RunStartedUtc` | String variable `RunStartedUtc` | `utcNow()` |
| `Initialize_ExecutionName` | String variable `ExecutionName` | empty |
| `Initialize_ExecutionStatus` | String variable `ExecutionStatus` | `Pending` |
| `Initialize_RefreshStartedUtc` | String variable `RefreshStartedUtc` | empty |
| `Initialize_RefreshStatus` | String variable `RefreshStatus` | `Unknown` |

Use the action names exactly when copying the expressions below.

## Main scope

Add a scope named `Main`.

### 1. Start the ACA Job

Add **HTTP with Microsoft Entra ID** named `Start_Cowork_ACA_Job`:

- Method: `POST`
- URI:

```text
@{concat(
  'https://management.azure.com/subscriptions/',
  variables('SubscriptionId'),
  '/resourceGroups/',
  variables('ResourceGroup'),
  '/providers/Microsoft.App/jobs/',
  variables('JobName'),
  '/start?api-version=2026-07-01'
)}
```

- Body: leave empty
- Retry policy: exponential, 4 retries
- Timeout: `PT2M`
- Secure inputs and outputs: On

Do not send an execution-template override. The deployed job definition owns
the image, command, managed identity, resources, and environment variables.

Set `ExecutionName` to:

```text
@{coalesce(body('Start_Cowork_ACA_Job')?['name'], '')}
```

The start API can return either `200` with the execution name or `202` with a
location header. The discovery loop below handles the latter.

### 2. Discover the execution when Start returned 202

Add a condition:

```text
@equals(variables('ExecutionName'), '')
```

In the **Yes** branch add a **Do until** named
`Discover_Cowork_execution` with:

- Exit condition: `@not(equals(variables('ExecutionName'), ''))`
- Count: `20`
- Timeout: `PT10M`

Inside it:

1. Delay `PT15S`.
2. HTTP GET named `List_recent_Cowork_executions`:

```text
@{concat(
  'https://management.azure.com/subscriptions/',
  variables('SubscriptionId'),
  '/resourceGroups/',
  variables('ResourceGroup'),
  '/providers/Microsoft.App/jobs/',
  variables('JobName'),
  '/executions?api-version=2026-07-01'
)}
```

3. Filter array named `Filter_executions_started_by_this_run`:
   - From: `@body('List_recent_Cowork_executions')?['value']`
   - Advanced condition:

```text
@greaterOrEquals(
  ticks(item()?['properties']?['startTime']),
  ticks(variables('RunStartedUtc'))
)
```

4. Condition:

```text
@greater(length(body('Filter_executions_started_by_this_run')), 0)
```

5. In its **Yes** branch set `ExecutionName`:

```text
@first(body('Filter_executions_started_by_this_run'))?['name']
```

The cloud-flow trigger and ACA Job both enforce one writer, so no second
execution should match this interval.

### 3. Poll the exact execution

Add **Do until** named `Wait_for_Cowork_job`:

- Exit condition:

```text
@or(
  equals(variables('ExecutionStatus'), 'Succeeded'),
  equals(variables('ExecutionStatus'), 'Failed'),
  equals(variables('ExecutionStatus'), 'Stopped'),
  equals(variables('ExecutionStatus'), 'Degraded')
)
```

- Count: `720`
- Timeout: `PT12H`

Inside it:

1. Delay `PT1M`.
2. HTTP GET named `List_Cowork_executions` using the same executions URI.
3. Filter array named `Filter_exact_Cowork_execution`:
   - From: `@body('List_Cowork_executions')?['value']`
   - Condition:

```text
@equals(item()?['name'], variables('ExecutionName'))
```

4. If the filtered array has a row, set `ExecutionStatus`:

```text
@first(body('Filter_exact_Cowork_execution'))?['properties']?['status']
```

After the loop, add a condition:

```text
@equals(variables('ExecutionStatus'), 'Succeeded')
```

In the **No** branch add **Terminate** with status `Failed` and a generic
message such as `Cowork preprocessing job did not succeed.` Do not place audit,
manifest, user, schedule, or file details in the termination text.

### 4. Refresh Power BI

In the successful branch:

1. Set `RefreshStartedUtc` to `@utcNow()`.
2. Add Power BI **Refresh a semantic model** (the connector may display the
   legacy label **Refresh a dataset**) with the configured workspace and model.
3. Add **Do until** named `Wait_for_Power_BI_refresh`:
   - Exit condition:

```text
@or(
  equals(variables('RefreshStatus'), 'Completed'),
  equals(variables('RefreshStatus'), 'Failed'),
  equals(variables('RefreshStatus'), 'Cancelled'),
  equals(variables('RefreshStatus'), 'Disabled')
)
```

   - Count: `120`
   - Timeout: `PT2H`

Inside it:

1. Delay `PT1M`.
2. Add Power BI **Get refresh history** for the same semantic model.
3. Filter the returned refresh records to those whose `startTime` is at or
   after `RefreshStartedUtc`.
4. If a record exists, set `RefreshStatus` from its `status`.

After the loop, require:

```text
@equals(variables('RefreshStatus'), 'Completed')
```

Terminate as failed for every other terminal status.

## Failure scope

Add a scope named `Notify_failure` after `Main`. Configure **run after** for
failed, timed out, and skipped.

The optional notification must be generic:

```text
Cowork Adoption Intelligence refresh failed. Review the protected ACA Job logs and Power BI refresh history.
```

Do not include audit content, user names, source paths, organization details,
or extracted error payloads. End the scope with **Terminate: Failed**.

## Success notification

Success notification is optional. If enabled, keep it generic:

```text
Cowork Adoption Intelligence refresh completed successfully.
```

## Acceptance test

1. Keep the recurrence trigger disabled.
2. Start the ACA Job once manually.
3. Confirm `status/latest.json` says `succeeded`.
4. Confirm `preprocessed/manifest.json` has format
   `cowork-python-preprocessor-manifest-v1`.
5. Run the flow manually.
6. Confirm it tracks the exact ACA execution and starts Power BI only after
   job success.
7. Force a safe test failure, such as an invalid test-only initial date in a
   nonproduction deployment, and confirm Power BI is not refreshed.
8. Re-enable the production schedule only after the backfill is caught up.
