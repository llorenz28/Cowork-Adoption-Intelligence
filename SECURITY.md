<!-- BEGIN MICROSOFT SECURITY.MD V1.0.0 BLOCK -->

## Reporting security issues

Microsoft takes the security of our software products and services seriously,
including all source code repositories managed through our GitHub organizations.

**Do not report security vulnerabilities through public GitHub issues.**

For security reporting information, contact details, and policies, review the
latest guidance at [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md).

<!-- END MICROSOFT SECURITY.MD BLOCK -->

## Data sensitivity

Production PAX Purview interactions and Entra users files can contain personal,
tenant, resource, licensing, organization, and business information. Refreshed
Power BI reports, screenshots, exports, PDFs, and presentations can expose the
same information.

Never commit production source files, paste their content into public issues, or
store them in an unapproved location.

## Required controls

- Keep production PAX files outside the Git working tree.
- Use the Purview and Users files from the same controlled PAX run.
- Restrict source files, gateway connections, semantic models, reports, and
  exports to approved owners.
- Use least privilege and organizational identities for SharePoint, OneLake,
  gateway, and Power BI access.
- Never place credentials, tokens, connection strings, or browser session data
  in parameters, scripts, logs, screenshots, or notifications.
- Record source owner, reporting window, export time, transformations,
  assumptions, reconciliation results, and exceptions.
- Apply approved retention and deletion requirements.
- Review all exported media for identifiers and tenant URLs.
- Apply the required sensitivity label before sharing a refreshed customer
  report.

## Release template classification

Repository visibility, sensitivity labeling, and encryption are separate
controls. This repository is public. Never place customer data, credentials,
tenant URLs, identifiable screenshots, or local profile paths in commits,
branches, pull requests, or issues.

`Cowork Adoption Intelligence V6.pbit` is data-free. It contains a model schema
and two blank required customer parameters:

- `Cowork Adoption Purview File`
- `Cowork Adoption Users File`

Package validation found no imported `DataModel` payload, no local QA paths, and
no customer source filenames. The package contains 8 report pages, 296 visuals,
29 bookmarks, 49 model tables, 353 measures, and 32 relationships.

The verified package carries the tenant **Public** label. Package metadata
records:

- label ID `87867195-f2b8-4ac2-b0b6-6bb73cb33afc`
- internal label name `Not Restricted`
- content bits `0`
- encryption disabled
- Desktop-generated `SecurityBindings` present (11,110 bytes)

Do not strip, replace, or hand-edit package streams. Opening or saving the
PBIT in another tenant can reissue label and security metadata according to that
tenant's policy.

## Source and refresh controls

- Local and UNC paths require an approved gateway for Power BI Service refresh.
- SharePoint and OneLake sources require approved organizational credentials.
- Update both paired PAX files as one reporting-window change.
- Refresh only after both files are available and access checks succeed.
- Reconcile source and report totals after every refresh.
- Treat blank enrichment as missing data, not zero activity.

## Interpretation and employment safeguards

- Category-user and enablement signals are not employee-performance ratings.
- Do not use the report for automated employment, promotion, compensation,
  disciplinary, aptitude, or surveillance decisions.
- Modeled assisted hours and labor value are scenarios, not realized savings,
  measured attention, available headcount capacity, or guaranteed ROI.
- Small cohorts and narrow periods can create privacy and inference risk.

## Legacy automation

The automation, preprocessor, and fabricated sample packages under `release/`
are retained for existing V5 preprocessed-entity deployments. They are not the
V6 ingestion path. Their security and operating guidance remains under
`automation/` and must not be presented as the V6 setup flow.
