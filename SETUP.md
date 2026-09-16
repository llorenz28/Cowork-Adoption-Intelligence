# Set up Cowork Adoption Intelligence

This guide starts with a short packaged-data smoke test, then walks through
production collection. No single person needs every tenant role.

## Before you start

For the sample path:

- Windows
- A current [Power BI Desktop](https://powerbi.microsoft.com/desktop/)
- About 10 minutes

For production, also identify:

- an authorized Purview owner with the **Audit Reader** role group
- an optional Microsoft 365 reports owner with **Reports Reader**
- an optional HR or Identity data owner
- a Power BI owner who will load, validate, label, and publish the report

Read [Security roles and access](docs/SECURITY_ROLES.md) before requesting
permissions. This CSV-fed release does not require an app registration, client
secret, Microsoft Graph application permission, Defender permission, or routine
Global Administrator assignment.

---

## Path A: try the report with fabricated data

Use this path first. It separates report or desktop problems from tenant
permissions and production export formats.

### Step 1: download the two files

Download:

1. [`Cowork Adoption Intelligence v2 Testing.pbit`](Cowork%20Adoption%20Intelligence%20v2%20Testing.pbit)
2. [`Cowork-Adoption-Intelligence-Sample-Data.zip`](release/Cowork-Adoption-Intelligence-Sample-Data.zip)

On GitHub, open each file and select **Download raw file**.

### Step 2: extract the sample package

1. Create a folder such as `C:\CoworkAdoptionSample`.
2. Extract the ZIP directly into that folder.
3. Confirm the folder contains:

```text
C:\CoworkAdoptionSample\
  _VERIFY.txt
  cowork_users.csv
  CoworkConsumptionDetails.csv
  CoworkUserDetails.csv
  CoworkUserOrgDetails.csv
  purview_audit\
    CoworkAudit-Synthetic-Part01.csv
    CoworkAudit-Synthetic-Part02.csv
```

Every person is fictional. All email addresses end in `@example.com`, and all
resource URLs use `tenant.example.com`.

### Step 3: open the Power BI template

1. Double-click `Cowork Adoption Intelligence v2 Testing.pbit`.
2. Power BI Desktop opens a parameter screen.
3. For `DataFolderPath`, enter:

```text
C:\CoworkAdoptionSample
```

Use the extraction folder itself, not its parent and not the
`purview_audit` subfolder.

### Step 4: load the files

1. Select **Load**.
2. If Power BI asks for a privacy level, select the local-file privacy level
   approved by your organization.
3. Wait for the model to finish loading.
4. Select **Home > Refresh** if the report does not refresh automatically.

### Step 5: confirm the sample worked

Check these results:

- Executive Summary shows **72 users** and populated task activity.
- Weekly Adoption & Usage has a multi-month trend.
- Skills, categories, and maturity visuals contain data.
- Cowork Champions defaults to **8 Top-10% candidates**.
- Top 5%, Top 10%, and Top 20% show **4, 8, and 15** candidates.
- Selecting **Analysis & Research** on Cowork Champions shows **5** candidates.
- No visual displays an error banner.

If those checks pass, the template and local Power BI environment are ready.
Continue to Path B only when you are ready to use approved production exports.

---

## Path B: connect production exports

### Step 1: assign data owners

| Owner | Deliverable | Recommended minimum |
| --- | --- | --- |
| Compliance/Purview owner | Raw Audit Search CSV files | Purview `Audit Reader` |
| Microsoft 365 reports owner | Cowork usage details CSV | `Reports Reader` |
| HR/Identity owner | Optional organization and identity files | Existing approved access |
| Power BI owner | Loads working copies, validates, labels, and publishes | No tenant role for Desktop |

Prefer exports from existing authorized owners over assigning every role to the
Power BI operator.

### Step 2: create a protected working folder

Create a folder outside the cloned Git repository:

```text
C:\CoworkAdoptionData\
  purview_audit\
    Purview-Cowork-2026-08-01-to-2026-08-31.csv
  CoworkUserDetails.csv
  CoworkUserOrgDetails.csv
  identity\
    cowork_users.csv
```

Keep immutable raw exports in a separately protected location. Normalize only
working copies. Record the source owner, reporting window, export time, and any
header or value transformations.

### Step 3: export required Purview audit records

**Access:** Ask the authorized collector to use the Microsoft Purview
**Audit Reader** role group.

1. Sign in to [Microsoft Purview](https://purview.microsoft.com/).
2. Select **Audit**. If needed, select **View all solutions > Audit**.
3. Create a search with UTC start and end times for the reporting period.
4. In **Activities - operation names**, enter `CopilotInteraction`.
5. Run the search and wait for it to complete.
6. Select **Export** and preserve the downloaded raw CSV unchanged.
7. Copy a protected working copy into
   `C:\CoworkAdoptionData\purview_audit`.
8. Confirm these required outer columns exist:

```csv
RecordId,CreationDate,Operation,UserId,AuditData
```

9. Confirm at least one row has `Operation = CopilotInteraction`.
10. Confirm its `AuditData` JSON contains
    `CopilotEventData.AppHost` with `cowork`, case-insensitively.

Do not expand, reformat, or hand-edit the JSON in `AuditData`. If the portal
export uses different outer headers, create a protected working copy and
normalize the headers without changing `AuditData`.

Audit searches accept a maximum 180-day range. Large periods may need
non-overlapping exports in the same `purview_audit` folder. The model combines
valid files and removes duplicate `RecordId` values.

Microsoft references:
[Audit permissions](https://learn.microsoft.com/purview/audit-get-started#step-2-assign-permissions-to-search-the-audit-log),
[search instructions](https://learn.microsoft.com/purview/audit-search),
[export limits](https://learn.microsoft.com/purview/audit-log-export-records),
and [Copilot audit fields](https://learn.microsoft.com/purview/audit-copilot).

### Step 4: export recommended Cowork usage details

**Access:** `Reports Reader`.

1. Sign in to the [Microsoft 365 admin center](https://admin.microsoft.com/).
2. Select **Copilot > Cowork > Usage**.
3. Select the reporting period and record **Last updated**.
4. Above **Cowork usage details**, select **Export**.
5. Preserve the raw download.
6. Save a normalized working copy as
   `C:\CoworkAdoptionData\CoworkUserDetails.csv`.
7. Use these headers:

```csv
UserPrincipalName,DisplayName,TotalTasks,ScheduledTasks,UserInitiatedTasks,ActiveDays,LastActivityDate
```

| Microsoft export | Template header |
| --- | --- |
| `User ID` | `UserPrincipalName` |
| `Display name` | `DisplayName` |
| `Total tasks` | `TotalTasks` |
| `Scheduled tasks` | `ScheduledTasks` |
| `User-initiated tasks` | `UserInitiatedTasks` |
| `Active days` | `ActiveDays` |
| `Last activity date` | `LastActivityDate` |

User identities are concealed by default in Microsoft 365 usage reports. A
`Reports Reader` assignment does not override that setting. If the export is
anonymized, an existing Global Administrator must decide whether the tenant-wide
concealment setting may be changed under organizational privacy policy. Do not
grant Global Administrator to the report operator.

Microsoft reference:
[Cowork usage report](https://learn.microsoft.com/microsoft-365/admin/activity-reports/cowork-usage-report?view=o365-worldwide).

### Step 5: prepare optional organization and identity files

Use an authorized HR or Identity data owner.

#### Organization file

Save the normalized working copy as
`C:\CoworkAdoptionData\CoworkUserOrgDetails.csv` with these exact,
case-sensitive headers:

```csv
userPrincipalName,displayName,department,jobTitle,jobFamily,city,country,costCenter,manager,businessUnit
```

Cells may be blank when an approved source does not provide a value. Only users
whose `userPrincipalName` matches detected Cowork activity appear.

#### Identity enrichment file

Save `C:\CoworkAdoptionData\identity\cowork_users.csv` with:

```csv
id,displayName,userPrincipalName
```

For an Entra bulk export, rename `objectId` to `id` in the working copy and keep
only approved fields.

Use lowercase UPNs consistently across all working copies. Optional-source joins
are case-sensitive.

Microsoft reference:
[Download Entra users](https://learn.microsoft.com/entra/identity/users/users-bulk-download).

### Step 6: check the folder

Set `DataFolderPath` to `C:\CoworkAdoptionData`. Discovery is recursive.

| Source | Preferred filename |
| --- | --- |
| Purview | Any `.csv` with the required audit columns |
| Cowork usage | `CoworkUserDetails.csv` or `Cowork Usage.csv` |
| Organization | `CoworkUserOrgDetails.csv` or `Cowork User Organization.csv` |
| Identity | Exact filename `cowork_users.csv` |

Keep only one current schema-valid file for each optional source. If several
files have the same schema, the model takes the first enumerated match; it does
not choose the newest file.

### Step 7: load and validate

1. Open `Cowork Adoption Intelligence v2 Testing.pbit`.
2. Set `DataFolderPath` to `C:\CoworkAdoptionData`.
3. Select **Load**.
4. Use the privacy level approved by your organization.
5. Refresh.
6. Validate sources in this order:

| Check | Expected result |
| --- | --- |
| Purview | Cowork users, task threads, skills, categories, and dates populate |
| Usage | Scheduled/user-initiated metrics and reconciliation populate |
| Identity | Friendly names appear without dropping unmatched audit users |
| Organization | Department and business-unit visuals populate |
| Champion lens | Results change with category and tier selections |
| Metric guide | Definitions and interpretation boundaries are visible |

Compare report totals with the source export for the same period. Investigate
large gaps before publishing. Read the
[interpretation guide](INTERPRETATION_GUIDE.md) before presenting findings or
using champion and modeled-value signals.

### Step 8: publish safely

1. Confirm production files remain outside the Git repository.
2. Review every page for identifiers and unexpected values.
3. Apply or confirm the sensitivity label required by organizational policy.
4. Publish with Power BI Pro/PPU unless qualifying capacity applies and workspace
   `Contributor` or higher.
5. Configure an
   [on-premises data gateway](https://learn.microsoft.com/data-integration/gateway/service-gateway-onprem)
   for scheduled refresh from local or UNC paths.

Publishing does not make `C:\CoworkAdoptionData` cloud-accessible.

## Quick help

| You see | Likely cause | What to do |
| --- | --- | --- |
| Folder error during load | `DataFolderPath` is missing or inaccessible | Select the existing narrow data folder |
| No Cowork users | No valid Cowork `CopilotInteraction` rows | Check audit headers, JSON integrity, period, and `AppHost` |
| Optional file ignored | Filename or header contract failed | Use a preferred filename and exact headers |
| Unexpected optional file selected | Several compatible files are present | Keep one current working file per optional schema |
| Usage split is blank | Usage export is absent, anonymized, or unmatched | Normalize headers, align UPN case, and review concealment |
| Department visuals are blank | Organization file is absent or unmatched | Confirm all ten headers and UPN overlap |
| Champion list is empty | The selected cohort is too small or below the eligibility floor | Widen the period or clear narrow filters |
| Service refresh fails | Power BI Service cannot reach local files | Configure and map an on-premises gateway |

## Security reminders

- Do not upload production exports to GitHub or attach them to issues.
- Use temporary or just-in-time role assignments where available.
- Restrict raw and normalized exports to approved owners.
- Preserve raw files; transform only protected working copies.
- Never store credentials, access tokens, or browser session data in scripts or
  Power BI parameter defaults.
- Apply your organization's retention and deletion requirements.
