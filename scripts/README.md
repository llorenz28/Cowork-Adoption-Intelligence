# Cowork Purview preprocessor

`Cowork_Purview_Preprocessor_v0.1.0.py` converts approved Microsoft Purview
Audit exports and optional supporting CSVs into the deterministic entity files
loaded by Cowork Adoption Intelligence V4.1.

The script uses only the Python standard library. It does not install packages,
call Microsoft 365 APIs, upload data, or modify the source folder.

## Download

The recommended download is the complete
[`Cowork-Adoption-Intelligence-Preprocessor-v0.1.0.zip`](https://github.com/microsoft/Cowork-Adoption-Intelligence/raw/main/release/Cowork-Adoption-Intelligence-Preprocessor-v0.1.0.zip).
It contains the script, contract, instructions, Power BI template, and SHA-256
checksums.

Keep these files together:

```text
Cowork_Purview_Preprocessor_v0.1.0.py
cowork-contract.json
Cowork Adoption Intelligence V4.pbit
README.md
SETUP.md
LICENSE
SHA256SUMS.txt
```

## Requirements

- Windows, macOS, or Linux
- Python 3.11 or later
- Read access to a protected raw-input folder
- Write access to a separate protected output folder
- Enough free disk space for the generated entities and temporary SQLite state

No administrator role, app registration, client secret, or third-party Python
package is required to run the script.

## Quick start

From PowerShell:

```powershell
python .\Cowork_Purview_Preprocessor_v0.1.0.py `
  --input C:\CoworkAdoptionData `
  --output C:\CoworkAdoptionPreprocessed
```

Validate the output independently:

```powershell
python .\Cowork_Purview_Preprocessor_v0.1.0.py `
  --validate-output C:\CoworkAdoptionPreprocessed
```

Open `Cowork Adoption Intelligence V4.pbit` and set
`PreprocessedOutputPath` to the validated output folder.

Run `--help` for all supported arguments:

```powershell
python .\Cowork_Purview_Preprocessor_v0.1.0.py --help
```

## Supported input

The script discovers CSV files recursively. Keep one current schema-valid file
for each optional source.

| Source | Required | Recognition |
| --- | --- | --- |
| Purview Audit | Yes | CSV with `AuditData`, `RecordId`, and `CreationDate` |
| Cowork usage detail | No | Usage-detail schema or preferred usage filename |
| Cowork organization detail | No | Organization schema or preferred organization filename |
| Cowork consumption | No | Consumption schema or preferred consumption filename |
| Identity enrichment | No | Exact filename `cowork_users.csv` |

The Purview export can be split across multiple CSV files. Rows must contain
valid JSON in `AuditData`. The script selects only `CopilotInteraction` events
whose `CopilotEventData.AppHost` is classified as Cowork by
`cowork-contract.json`.

For the complete column contracts and export guidance, see
[`SETUP.md`](https://github.com/microsoft/Cowork-Adoption-Intelligence/blob/main/SETUP.md#path-b-connect-production-exports),
or open the
`SETUP.md` included at the root of the downloaded bundle.

## Generated output

A successful run creates:

```text
entity-Dim_User.csv
entity-Fact_CopilotAuditRaw.csv
entity-Bridge_CoworkPlugin.csv
entity-CoworkClassification.csv
entity-Bridge_CoworkResource.csv
entity-Fact_CoworkThread.csv
entity-Fact_CoworkUsage.csv
entity-Dim_UserOrg.csv
entity-Fact_Consumption.csv
entity-Fact_CoworkUserDayModel.csv
entity-Fact_Tasks.csv
entity-Dim_CoworkSkill.csv
entity-Dim_ModelProvider.csv
manifest.json
```

`manifest.json` records the preprocessor and contract versions, source files,
row counts, hashes, duplicate counts, and collision checks used to validate the
run. A successful manifest has `"status": "valid"`.

## Safety behavior

- **Separate paths are mandatory.** Input and output cannot be the same folder,
  and neither can contain the other.
- **No partial publish.** Files are written to a staging folder and validated
  before the destination is replaced.
- **No silent malformed-row skipping.** Invalid JSON or required-field failures
  stop the run with a nonzero exit code.
- **No foreign-folder overwrite.** An existing output is replaced only when it
  contains a valid manifest created by this preprocessor.
- **Deterministic deduplication.** Audit rows are resolved by immutable record
  identity and payload evidence rather than source enumeration order.
- **Temporary state is removed.** The SQLite working database is deleted after
  every successful or failed run.

Treat both raw inputs and generated outputs as customer data. The entity files
can contain user principal names, prompts, responses, resource URLs, and
organization attributes. Store them only in approved protected locations.

## Updating data

The Power BI template reads generated entity files; it does not execute Python.
When source exports change:

1. Put the current exports in the protected input folder.
2. Rerun the preprocessor with the same validated output path.
3. Confirm `--validate-output` returns `"status": "valid"`.
4. Refresh the Power BI report.

For unattended use, run the command from an organization-approved scheduler,
pipeline, or automation host before the Power BI refresh window.

## Troubleshooting

| Error | Resolution |
| --- | --- |
| Contract file not found | Keep `cowork-contract.json` beside the script; re-extract the bundle if it is missing |
| No Purview audit CSV was found | Confirm a CSV has `AuditData`, `RecordId`, and `CreationDate` |
| Ambiguous optional source | Remove stale or duplicate schema-compatible files |
| Malformed `AuditData` JSON | Re-export the affected Purview batch |
| Output exists but is not owned by this tool | Choose an empty output folder; do not delete unknown data automatically |
| Output validation failed | Do not load the folder in Power BI; inspect the reported entity or hash mismatch and rerun |

## Validation evidence

Version 0.1.0 was exercised against:

- A 70,976-row fixture, which preprocessed in 14.811 seconds and reconciled the
  live report exactly, including Champion `2 summary / 2 row-level / 0 delta`.
- A 1,050,000-row, 70,000-user synthetic fixture, which preprocessed in 200.528
  seconds and matched core model counts after loading.

Times are machine- and data-dependent. The large test proves scale and parity;
it is not a service-level objective or a safe memory guarantee for every
customer device.
