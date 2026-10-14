# Set up Cowork Adoption Intelligence V7

V7 reads two paired CSV files produced by one PAX Cowork Adoption run. It does
not require the previous Python preprocessor or a folder of generated entity
files.

## Before you start

- Install the current [Power BI Desktop](https://powerbi.microsoft.com/desktop/).
- Obtain the paired PAX outputs from an authorized collection owner.
- Store production files outside the cloned repository in an approved protected
  location.
- Read [Security roles and access](docs/SECURITY_ROLES.md) and
  [SECURITY.md](SECURITY.md).

## Required files

| Power BI parameter | Required PAX output |
| --- | --- |
| `Cowork Adoption Purview File` | Purview Cowork interactions CSV |
| `Cowork Adoption Users File` | Entra users, organization, and Microsoft 365 Copilot licensing CSV |

Use files from the same PAX run. Do not combine reporting windows or manually
merge rows. The files must retain the PAX `_Entity` records and keys used by the
model.

## Generate the files with PAX

Use the official Microsoft
[Portable Audit eXporter (PAX)](https://github.com/microsoft/PAX) Purview Audit
Log Processor. V7 requires the PAX v2 Cowork Adoption entity contract produced
by `-Dashboard CoworkAdoption`.

> [!IMPORTANT]
> PAX v2 and Cowork Adoption Intelligence V7 are currently prerelease/testing
> artifacts. Do not present this workflow as production-supported until both
> projects publish production-ready releases and the repository completes a
> matching release validation.

Use the [Mini-Kitchen Cowork Adoption preset](https://microsoft.github.io/PAX-Cookbook/mini-kitchen/)
to generate a command for the current PAX v2 prerelease. Do not substitute PAX
v1.11.15 with `-Dashboard AIO`: those AIO rollup files do not contain the
required `_Entity` and `_RowId` columns and V7 will reject them.

### PAX prerequisites

- PowerShell 7 or later for the default Microsoft Graph mode.
- Unified Audit Logging enabled in the tenant.
- Microsoft Graph `AuditLogsQuery.Read.All` for `CopilotInteraction` records.
- Microsoft Graph `User.Read.All` and `Organization.Read.All` for Entra user,
  organization, and Microsoft 365 Copilot licensing enrichment.
- Tenant-admin consent and organizational approval for the selected delegated,
  app-registration, or managed-identity authentication method.
- A protected output location outside the Git working tree.

PAX requests permissions conditionally. Review its current permission table and
have security, privacy, and compliance owners approve the collection before use.

### Interactive prerelease validation example

The V7 model consumes the Cowork Adoption entity pair. For a first validation
run, use a short custom UTC range and local protected output.

Create the protected destination first:

```powershell
New-Item -ItemType Directory -Force -Path "C:\CoworkAdoption\PAXOutput"
```

Copy the exact current prerelease filename from the PAX release page into the
script path. Example one-line command:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File ".\PAX_Purview_Audit_Log_Processor_v2.0.0-prerelease-20261009-10.ps1" -Auth WebLogin -StartDate 2026-09-01 -EndDate 2026-09-08 -Dashboard CoworkAdoption -Rollup -CombineOutput -IncludeUserInfo -OutputPath "C:\CoworkAdoption\PAXOutput\" -OutputPathUserInfo "C:\CoworkAdoption\PAXOutput\"
```

Replace the example dates and output path. `StartDate` is inclusive,
`EndDate` is exclusive, and both use UTC `yyyy-MM-dd` values. Start with a short
window to validate permissions and output before collecting a long history.
PAX requires exactly one destination for the Entra users stream when
`-IncludeUserInfo` is selected. Omitting `-OutputPathUserInfo` stops the
preflight check before authentication or collection.

PAX creates several artifacts. Bind Power BI to the two **rolled-up** files from
the same run:

- the file ending `_Interactions.csv` -> `Cowork Adoption Purview File`
- the file ending `_Users.csv` -> `Cowork Adoption Users File`

Before opening Power BI, confirm that both selected files contain `_Entity` and
`_RowId` headers. Do not select the raw Purview audit CSV, an AIO
`_Interactions.csv`, or the pre-rollup `EntraUsers_MAClicensing_<timestamp>.csv`.
Use `-Auth DeviceCode`, `AppRegistration`, or `ManagedIdentity` only as
documented by PAX for the target environment; never place client secrets in the
repository or command history.

## Supported locations

Each parameter accepts one complete file path or URL.

### Local or network path

```text
C:\CoworkAdoption\CoworkAdoption_Interactions.csv
\\server\protected-share\CoworkAdoption_Users.csv
```

Power BI Service requires an approved gateway for local or UNC paths.

### SharePoint URL

```text
https://contoso.sharepoint.com/sites/analytics/Shared%20Documents/Cowork/CoworkAdoption_Interactions.csv
```

Use the complete file URL. URL-encoded characters and query strings are handled
by the template.

### OneLake URL

```text
https://onelake.dfs.fabric.microsoft.com/<workspace>/<lakehouse>.Lakehouse/Files/Cowork/CoworkAdoption_Interactions.csv
```

The equivalent `abfss://` OneLake form is also supported.

## Load the template

1. Open
   [`Cowork Adoption Intelligence V7.pbit`](Cowork%20Adoption%20Intelligence%20V7.pbit).
2. Enter `Cowork Adoption Purview File`.
3. Enter `Cowork Adoption Users File`.
4. Select **Load**.
5. Configure credentials and privacy levels approved by your organization.
6. Wait for all queries and visuals to finish.
7. Confirm all eight pages render without visual errors.
8. Confirm the report displays the sensitivity label required by policy.

## Reconcile before use

For the same reporting window, verify:

- total observed Cowork tasks
- distinct task users
- organization and department coverage
- model-attribution availability
- category totals and task mix
- after-hours task count
- visible date range

The two normalized category-share series on **Demand & Capacity Scenario** must
each total 100% in the current external filter context.

## Review modeled assumptions

Open **Capacity Assumptions** before presenting assisted-time results.

- Low, Mid, and High use the cited category defaults.
- Custom uses the eight synchronized customer-controlled minute values.
- Modeled assisted hours equal observed tasks multiplied by selected category
  minutes, divided by 60.
- Modeled labor value applies the loaded hourly rate to modeled assisted hours.

These outputs are scenarios. They are not measured human attention, realized
savings, available staff capacity, or guaranteed financial value.

## Scheduled refresh

- For local or network paths, configure an approved on-premises data gateway.
- For SharePoint or OneLake, configure the corresponding organizational
  credentials in Power BI Service.
- Replace or update both paired files as one controlled reporting-window change.
- Refresh only after the PAX run succeeds and both files are available.
- Reconcile the refreshed report before distribution.

The automation bundle under `release/` belongs to the previous V5
preprocessed-entity deployment. It is retained for existing installations and
is not required by V7.

## Publish safely

1. Keep PAX exports outside Git.
2. Restrict source and report access to approved owners.
3. Record the reporting window, source owner, export time, active assumptions,
   and reconciliation results.
4. Apply the organization-required sensitivity label after customer data loads.
5. Review screenshots, PDFs, and presentations for identifiers and tenant URLs.

The distributed PBIT is labeled **Public** because it contains no imported
customer data. A refreshed customer report must be relabeled according to
organizational policy before sharing.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Parameter prompt rejects a path | Use one full file path or URL; remove surrounding whitespace and confirm the file exists |
| Local file cannot refresh in Power BI Service | Configure and map an approved gateway connection |
| SharePoint file is not found | Use the complete file URL and verify access with the configured identity |
| OneLake file is not found | Confirm workspace, lakehouse, `Files` path, and permissions |
| Organization visuals are blank | Confirm the Users file is from the same run and contains matching user keys |
| Copilot model shows unavailable | The Purview source did not provide model-attribution values for those tasks |
| Custom minutes do not change results | Select **Custom** in the synchronized assumption-basis control |
| Final period looks low | Check whether the final reporting period is incomplete |
