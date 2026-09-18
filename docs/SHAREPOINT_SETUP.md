# SharePoint setup

Use `Cowork Adoption Intellgience V3 - SharePoint.pbit` when the supported CSV
exports are stored in a SharePoint document library. It has the same report,
model, metrics, and file contracts as the local-folder V3 template.

## Before you start

- Use an approved SharePoint site and document-library folder.
- Keep production exports restricted to authorized report and data owners.
- Confirm that the Power BI refresh identity can read the site and folder.
- Place supported CSV files in one folder or its subfolders.

Do not use a sharing link such as `/:f:/r/...`, and remove browser query strings
such as `?web=1`.

## Required parameters

| Parameter | Example |
| --- | --- |
| `SharePointSiteUrl` | `https://contoso.sharepoint.com/sites/CoworkAdoption` |
| `SharePointFolderUrl` | `https://contoso.sharepoint.com/sites/CoworkAdoption/Shared Documents/Exports` |

The folder URL must be inside the configured site URL. Use the canonical
document-library path, replace `%20` with spaces, and omit the trailing slash.

## Load the template

1. Download
   [`Cowork Adoption Intellgience V3 - SharePoint.pbit`](../Cowork%20Adoption%20Intellgience%20V3%20-%20SharePoint.pbit).
2. Open the template in Power BI Desktop.
3. Enter `SharePointSiteUrl` and `SharePointFolderUrl`.
4. Select **Load**.
5. When prompted for credentials, choose **Organizational account**, sign in,
   and select **Connect**.
6. Use the privacy level required by your organization.
7. Refresh and validate the expected users, activity, dates, optional sources,
   and metric data-status indicators.

The template makes one static `SharePoint.Files` call at the site level, filters
recursively to `SharePointFolderUrl`, and reuses each file's binary `Content`
value. This avoids dynamic URL data sources and local-file gateway dependencies.

## Supported files

| Source | Preferred filename |
| --- | --- |
| Purview | Any `.csv` with `RecordId`, `CreationDate`, `Operation`, `UserId`, and `AuditData` |
| Cowork usage | `CoworkUserDetails.csv` or `Cowork Usage.csv` |
| Organization | `CoworkUserOrgDetails.csv` or `Cowork User Organization.csv` |
| Identity | Exact filename `cowork_users.csv` |
| Consumption | `CoworkConsumptionDetails.csv` or `Consumption - Users.csv` |

Keep only one current schema-valid file for each optional source. Purview files
may be split across subfolders; duplicate `RecordId` values are removed.

## Publish and refresh

After publishing, configure the SharePoint data-source credentials in Power BI
Service with the same authorized organizational identity. A local-file
on-premises gateway is not normally required for this edition.

Apply the sensitivity label, access controls, retention policy, and workspace
permissions required by your organization before sharing the refreshed report.

## Rebuild the SharePoint edition

Run the checked-in builder whenever the local V3 template is re-exported:

```powershell
.\tools\New-SharePointPbit.ps1 `
  -InputTemplate '.\Cowork Adoption Intellgience V3.pbit' `
  -OutputTemplate '.\Cowork Adoption Intellgience V3 - SharePoint.pbit' `
  -Force
```

The builder preserves the report package and Public label metadata while
replacing only the compiled model's local-file source expressions.
