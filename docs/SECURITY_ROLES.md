# Security roles and access

This page defines the least-privilege access needed to collect CSV inputs for
Cowork Adoption Intelligence. Data export, tenant configuration, and Power BI
publication are separate responsibilities.

## What this release does not require

Do not request these solely for the template:

- an app registration, client secret, or certificate
- Microsoft Graph application permissions
- Defender Advanced Hunting permissions
- Global Administrator for routine collection

## Least-privilege matrix

| Task | Recommended minimum | Important boundary |
| --- | --- | --- |
| Search and export Purview audit records | Purview **Audit Reader** role group | Grants `View-Only Audit Logs`; Audit Manager is broader |
| Export identifiable Cowork usage details | `Reports Reader` | Tenant identity concealment still applies |
| Download approved Entra user fields | Existing authorized Identity/HR owner | Tenant policy governs access and permitted fields |
| Open and refresh in Power BI Desktop | No tenant role | Approved local file access is sufficient |
| Publish to a Power BI workspace | Pro/PPU unless qualifying capacity applies, plus workspace `Contributor` | Use `Member` or `Admin` only for app or access management |
| Schedule refresh from local or UNC files | Workspace write role plus gateway connection access | Gateway permissions are separate from workspace roles |

## Why these roles

### Purview

Microsoft Purview **Audit Reader** is the read-only collection role group. It
grants `View-Only Audit Logs`, allowing search and export without permission to
manage auditing.

### Cowork usage

`Reports Reader` can access usage reports with user-level detail when the
tenant's reporting privacy setting allows it. Summary-only roles omit identity
needed for joins. No usage-report role overrides tenant-wide concealment.

If the usage export is anonymized, an existing Global Administrator must decide
whether changing the tenant-wide concealment setting is allowed. Do not grant
Global Administrator to the report operator.

### Organization and identity

Prefer a file from an existing authorized HR or Identity owner. Keep only fields
approved for this reporting purpose.

## Data-owner handoff

| Owner | Responsibility |
| --- | --- |
| Purview owner | Defines the approved UTC window, exports raw audit results, checks export limits, and transfers them securely |
| Microsoft 365 reports owner | Exports Cowork usage details and records **Last updated** |
| HR/Identity owner | Supplies only approved organization and identity fields |
| Power BI owner | Loads working copies, validates source status, labels the refreshed file, and publishes |

No single operator needs every tenant role.

## Copy-ready access request

```text
Subject: Least-privilege exports for Cowork adoption reporting

Please provide these CSV exports for the agreed reporting period:

1. Microsoft Purview Audit
   - Collector: authorized Compliance/Purview owner
   - Role group: Audit Reader
   - Operation: CopilotInteraction
   - Deliverable: complete raw Audit Search CSV export(s), unchanged
   - Record: UTC window, export time, and whether the query exceeded an export limit

2. Microsoft 365 admin center > Copilot > Cowork > Usage
   - Collector: authorized Microsoft 365 reports owner
   - Recommended role: Reports Reader
   - Deliverable: Cowork usage details CSV and Last updated timestamp
   - Identity requirement: user details must be available under approved tenant privacy policy

3. Optional organization/identity export
   - Collector: existing authorized HR/Identity owner
   - Deliverable: only the approved fields documented in SETUP.md

No app registration, secret, Graph application permission, Defender permission,
or Global Administrator assignment is requested for routine report operation.
```

## Assignment and review controls

- Prefer existing data owners over new assignments.
- Use time-bound or just-in-time assignment where available.
- Remove temporary access after delivery.
- Review access for every reporting cycle.
- Do not combine export and report-consumer access by default.
- Record who exported each source, when, for what window, and under which
  approved purpose.

## Microsoft references

- [Purview Audit Reader and Audit Manager](https://learn.microsoft.com/purview/audit-get-started#step-2-assign-permissions-to-search-the-audit-log)
- [Purview search requirements and retention](https://learn.microsoft.com/purview/audit-search#before-you-search-the-audit-log)
- [Purview export limits](https://learn.microsoft.com/purview/audit-log-export-records)
- [Cowork usage access and export](https://learn.microsoft.com/microsoft-365/admin/activity-reports/cowork-usage-report?view=o365-worldwide)
- [Usage-report roles and identity concealment](https://learn.microsoft.com/microsoft-365/admin/activity-reports/activity-reports?view=o365-worldwide#before-you-begin)
- [Download Entra users](https://learn.microsoft.com/entra/identity/users/users-bulk-download)
- [Power BI workspace roles](https://learn.microsoft.com/power-bi/collaborate-share/service-roles-new-workspaces#workspace-roles)
- [On-premises data gateway](https://learn.microsoft.com/data-integration/gateway/service-gateway-onprem)

Role names, navigation, licensing, and export schemas can change. Confirm the
linked Microsoft guidance, actual CSV headers, and tenant policy before each
production collection.

