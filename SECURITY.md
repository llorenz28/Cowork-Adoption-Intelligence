<!-- BEGIN MICROSOFT SECURITY.MD V1.0.0 BLOCK -->

## Reporting security issues

Microsoft takes the security of our software products and services seriously,
including all source code repositories managed through our GitHub organizations.

**Do not report security vulnerabilities through public GitHub issues.**

For security reporting information, contact details, and policies, review the
latest guidance at [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md).

<!-- END MICROSOFT SECURITY.MD BLOCK -->

## Data sensitivity

Production Purview, usage, organization, and identity exports can contain
personal, tenant, resource, and business information. Never commit those files,
paste their content into an issue, or store them in an unapproved location.

## Required controls

- Keep production exports outside the Git working tree.
- Restrict raw and generated files to approved collection and report owners.
- Use least privilege and time-bound access where available.
- Preserve raw exports; transform only protected working copies.
- Keep preprocessor input and output in separate, non-overlapping folders.
- Treat generated entity files and `manifest.json` as customer data.
- Keep the version-matched `cowork-contract.json` beside the script or verify
  an explicitly supplied contract before use.
- Never store credentials, access tokens, or browser session data in scripts or
  parameter defaults.
- Record source owner, reporting window, export time, transformations, and report
  assumptions.
- Apply retention and deletion requirements to raw and transformed files.
- Review screenshots, videos, PDFs, and report exports for identifiers and URLs.
- Apply the organization's required sensitivity label to refreshed reports
  before sharing.

## Template classification

Repository visibility, sensitivity labels, and encryption are separate controls.
This repository is public. Never place customer exports, credentials, tenant
URLs, or identifiable screenshots in commits, branches, pull requests, or
issues.

The distributable testing PBIT contains no imported customer data or
machine-bound `SecurityBindings` stream. `PreprocessedOutputPath` is blank.
Opening the template can cause the generated report to receive the tenant's
default label. Before sharing a refreshed customer-data report, apply or
confirm the label and protection required by organizational policy.

The Python preprocessor uses only the standard library and makes no network
calls. It writes to a staging folder, validates every entity and hash, then
atomically replaces only a destination previously created by the same tool.
Malformed required data stops the run rather than being silently skipped.

## Storage and service refresh

- Store customer exports, generated entities, manifests, and optional retained
  work databases outside the repository and limit folder permissions.
- Publishing a report does not make local paths cloud-accessible.
- For scheduled refresh from local or UNC paths, use an approved on-premises
  data gateway and grant the semantic model owner access to its connection.
- Power BI does not execute the Python preprocessor. Rerun or automate it before
  the report refresh whenever source exports change.
