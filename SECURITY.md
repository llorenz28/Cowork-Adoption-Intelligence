<!-- BEGIN MICROSOFT SECURITY.MD V1.0.0 BLOCK -->

## Reporting security issues

Microsoft takes the security of our software products and services seriously,
including all source code repositories managed through our GitHub organizations.

**Do not report security vulnerabilities through public GitHub issues.**

For security reporting information, contact details, and policies, review the
latest guidance at [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md).

<!-- END MICROSOFT SECURITY.MD BLOCK -->

## Data sensitivity

Production Purview, usage, organization, identity, generated entity, manifest,
log, status, metric, and report data can contain personal, tenant, resource,
prompt, response, and business information. Never commit those files, paste their
content into an issue, or store them in an unapproved location.

## Required controls

- Keep production input and generated output outside the Git working tree.
- Restrict raw, generated, gateway, job, and Power BI data to approved owners.
- Use least privilege, scoped roles, managed identities, and time-bound access.
- Preserve immutable raw exports; transform only protected working copies.
- Keep processor input and output in separate, non-overlapping locations.
- Treat all 13 entity files and `manifest.json` as customer data.
- Keep the version-matched `cowork-contract.json` with the processor.
- Never place credentials, access tokens, connection strings, or browser session
  data in scripts, flow definitions, parameters, logs, or notifications.
- Record source owner, reporting window, export time, transformations,
  assumptions, and exceptions.
- Apply approved retention and deletion requirements to raw, generated, status,
  metric, log, and report content.
- Review screenshots, exports, PDFs, and presentations for identifiers and URLs.
- Apply the required sensitivity label before sharing any refreshed report.

## Release template classification

Repository visibility, sensitivity labeling, and encryption are separate
controls. This repository is public. Never place customer data, credentials,
tenant URLs, or identifiable screenshots in commits, branches, pull requests, or
issues.

`Cowork Adoption V3.pbit` contains no imported customer data and no `DataModel`
payload. It contains a model schema and one blank customer-supplied parameter,
`PreprocessedOutputPath`.

The verified package carries the tenant **Public** label. Package metadata records
label ID `87867195-f2b8-4ac2-b0b6-6bb73cb33afc`, internal label name
`Not Restricted`, and content bits `0`, so the release label does not encrypt the
template. Power BI Desktop also emitted a `SecurityBindings` stream for that
label. This is expected for the validated artifact; do not strip, replace, or
hand-edit package streams.

Opening or saving the template in another tenant can reissue label and security
metadata according to that tenant's policy. Before sharing a report refreshed
with customer data, apply or confirm the classification and protection required
by the organization.

## Processor behavior

The Python processor:

- writes to a staging directory
- validates required headers and `AuditData` JSON
- deduplicates by immutable record identity and payload evidence
- validates every entity's required structure and reconciliation totals
- atomically replaces only a destination previously created by the processor
- stops on malformed required data instead of silently skipping it

The compatibility validator independently verifies the 13-file contract,
Cowork AppHost evidence, ThreadId requirements, and reconciliation checks.

## Power Automate and Azure controls

Power Automate starts and monitors an Azure Container Apps Job. It must not read,
loop through, or include audit records in flow state. Trigger concurrency and job
writer concurrency must both remain one.

- Use a user-assigned managed identity for the job.
- Grant PAX Graph application permissions only after tenant review and admin
  consent.
- Use the custom job-start role in
  `automation/deploy/CoworkJobStarterRole.json` at the specific job scope.
- Do not grant broad `Container Apps Jobs Operator` access when the custom role is
  sufficient.
- Use private networking, encryption, firewall rules, and approved storage
  controls where required.
- Turn on secure inputs and outputs for ARM actions.
- Keep success and failure notifications generic.
- Never include audit content, user names, source paths, manifest details, tenant
  identifiers, or raw error payloads in Teams or email notifications.
- Refresh Power BI only after collection, preprocessing, and both validators
  succeed.

## Storage and service refresh

- Store customer content in approved locations with limited permissions.
- Publishing a report does not make local or UNC paths cloud-accessible.
- For scheduled refresh, configure an approved gateway and map the validated
  `preprocessed` folder.
- Power BI reads entity files; it does not execute PAX or Python.
- Rerun or automate collection and preprocessing before Power BI refresh whenever
  source exports change.
