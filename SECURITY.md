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
- Restrict raw and normalized files to approved collection and report owners.
- Use least privilege and time-bound access where available.
- Preserve raw exports; transform only protected working copies.
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
machine-bound `SecurityBindings` stream. It carries the tenant **Public**
sensitivity label without encryption. Opening the template can cause the
generated report to receive the tenant's default label. Before sharing a
refreshed customer-data report, apply or confirm the label and protection
required by organizational policy.

## Storage and service refresh

- Store customer exports outside the repository and limit folder permissions.
- Publishing a report does not make local paths cloud-accessible.
- For scheduled refresh from local or UNC paths, use an approved on-premises
  data gateway and grant the semantic model owner access to its connection.

