# Cowork Adoption Intelligence automation

> [!IMPORTANT]
> **Legacy V5 deployment path.** Cowork Adoption Intelligence V6 directly
> consumes paired PAX Purview and Entra CSV files and does not require this
> preprocessor or 13-entity pipeline. Retain this package only for existing V5
> preprocessed deployments.

This package automates the supported Cowork Adoption Intelligence
preprocessed-ingestion path without making Power Automate process audit rows. It
is paired with the 5.0.0-testing recommended-layout report.

## Recommended architecture

```text
Power Automate recurrence
  -> start and monitor one Azure Container Apps Job
     -> PAX v1.11.15 collects bounded CopilotInteraction windows
     -> PAX appends/deduplicates one protected raw CSV on Azure Files
     -> Cowork_Purview_Preprocessor_v0.1.0.py rebuilds 13 entity CSVs
     -> both Cowork validators must succeed
     -> watermark and run status are published
  -> refresh the Power BI semantic model only after job success
```

Power Automate is intentionally the orchestrator. Sending one million audit
records through cloud-flow loops or Dataverse row writes would add connector
throttling, payload, duration, retention, and cost risks. PAX already provides
bounded Graph queries, paging, retry, saturation subdivision, checkpointing,
streaming output, and duplicate-safe append behavior.

## Package contents

| Path | Purpose |
| --- | --- |
| `container/Invoke-CoworkPipeline.ps1` | Locks the data root, runs PAX, runs Cowork preprocessing, validates, and advances the watermark only on success |
| `container/Cowork_Purview_Preprocessor_v0.1.0.py` | Exact source copy of the final validated Cowork processor |
| `container/cowork-contract.json` | Version-matched Cowork classification and entity contract |
| `container/Validate-CoworkCompatibility.py` | Additional 13-file, AppHost, ThreadId, and reconciliation guard |
| `container/Dockerfile` | Pinned PAX/Cowork runtime for Azure Container Apps Jobs |
| `deploy/Deploy-CoworkAcaJob.ps1` | Builds the image, mounts Azure Files, and creates or updates the manual job |
| `deploy/CoworkJobStarterRole.json` | Least-privilege role template for the Power Automate ARM connection |
| `power-automate/BUILD.md` | Exact cloud-flow actions, expressions, gates, and retry limits |
| `power-automate/CoworkRefreshOrchestrator.logic.json` | Machine-readable implementation map; it is not an importable solution ZIP |

## Prerequisites

- Azure Container Registry
- Azure Container Apps environment
- Azure Storage account with Azure Files
- User-assigned managed identity for the job
- Python is already included in the container
- Power BI workspace and semantic-model IDs
- On-premises data gateway host that can read the Azure Files UNC path
- Power Automate premium access for the Microsoft Entra ID HTTP connector

Grant the job identity the PAX permissions required for this collection mode:

- Microsoft Graph application permission `AuditLogsQuery.Read.All`
- `AcrPull` on the container registry
- Admin consent for `AuditLogsQuery.Read.All`

The packaged runner does not pass `-IncludeUserInfo`, `-GroupNames`, or
`-IncludeM365Usage`. Do not grant `User.Read.All`, `Organization.Read.All`,
`GroupMember.Read.All`, or the M365 audit-query bundles unless a customized
runner enables the corresponding PAX feature.

The official pinned PAX prerequisite implementation is
[`fabric_resources/Prereqs/Grant-PAXPermissions.ps1`](https://github.com/microsoft/PAX/blob/945b634705f355ffaada4310de096af47adf44c5/fabric_resources/Prereqs/Grant-PAXPermissions.ps1).
Review it with the tenant administrator before granting permissions.

## Deploy

Run from PowerShell after signing in with Azure CLI:

```powershell
.\deploy\Deploy-CoworkAcaJob.ps1 `
  -SubscriptionId '<subscription-guid>' `
  -ResourceGroup '<container-apps-resource-group>' `
  -EnvironmentName '<container-apps-environment>' `
  -AcrName '<registry-name>' `
  -ManagedIdentityResourceId '<managed-identity-resource-id>' `
  -ManagedIdentityClientId '<managed-identity-client-id>' `
  -TenantId '<tenant-guid>' `
  -StorageAccountName '<storage-account-name>' `
  -StorageAccountResourceGroup '<storage-resource-group>' `
  -InitialStartUtc '2026-01-01T00:00:00Z'
```

The deployment defaults are:

- 4 vCPU / 8 GiB
- one replica and one writer
- 12-hour execution timeout
- one-day UTC collection windows
- one-day overlap
- six-hour end lag
- up to seven windows per execution
- PAX 15-minute internal blocks and maximum concurrency 6

The first run begins at `InitialStartUtc`. The date is normalized to midnight
UTC because PAX v1.11.15 accepts `yyyy-MM-dd` boundaries. For a long initial
backfill, keep the Power Automate flow disabled, temporarily raise
`MaxWindowsPerRun`, and manually start the job until `status/latest.json` shows
`"caughtUp": true`.

## Durable folder contract

The Azure Files share is mounted at `/data` in the job:

```text
active/
  purview_audit/
    CoworkPurviewAudit.csv
  CoworkUserDetails.csv              optional
  CoworkConsumptionDetails.csv       optional
  CoworkUserOrgDetails.csv           optional
  identity/
    cowork_users.csv                 optional
preprocessed/
  manifest.json
  entity-*.csv                       exactly 13 files
state/
  watermark.json
  pipeline.lock
status/
  latest.json
  history/
logs/
metrics/
```

PAX owns `active/purview_audit/CoworkPurviewAudit.csv`. Publish only one current
schema-valid file for each optional source. Use the exact Cowork filenames and
headers documented by the template.

The runner does not advance `state/watermark.json` unless collection,
preprocessing, structural validation, and compatibility validation all
succeed. A failed retry intentionally re-queries the overlap; PAX and the
Cowork processor converge by `RecordId`.

## Connect Power BI

Set the template's `PreprocessedOutputPath` parameter to:

```text
\\<storage-account>.file.core.windows.net\<file-share>\preprocessed
```

Configure the on-premises data gateway with a service identity that has read
access to that Azure Files share. The semantic model reads only the validated
`preprocessed` folder; it does not run Python.

Build the cloud flow from `power-automate/BUILD.md`. Keep trigger concurrency at
one. The flow must not refresh Power BI when the ACA execution is failed,
stopped, degraded, or timed out.

## Performance behavior

The final included processor was validated at 1,050,000 audit rows and 70,000
users. Its manifest reported 74.948 seconds of preprocessing and the isolated
process completed in 85.224 seconds wall time. All 13 entity CSVs were
byte-identical to the previously validated scale output. The earlier Power BI
Desktop scale load took 331.107 seconds with a reported 5.50-GiB Desktop peak.
These results are correctness and scale evidence, not an SLA or a controlled
before/after performance comparison.

This package preserves the optimized entity contract, including
`Fact_CoworkUserDayModel`, and avoids raw parsing in Power Query. It does not
change the report model or the tested Python transformation. Daily runs still
perform a full deterministic entity rebuild, so monitor `manifest.json`
timings and increase job memory before increasing query concurrency.

## Security

Purview audit, generated entities, metrics, manifests, and logs may contain
identifiers, prompts, responses, URLs, and organization attributes. Treat the
entire share as highly confidential:

- restrict storage, job, gateway, and Power BI access
- use private networking where required
- enable encryption and approved retention controls
- do not put source data or status details in Teams/email notifications
- grant job-start permission only to a trusted Power Automate connection
- apply the required sensitivity label to the published Power BI content

`Container Apps Jobs Operator` can read job secrets through a wildcard action.
Prefer the narrower custom role template in `deploy/CoworkJobStarterRole.json`
and assign it only at the job scope.
