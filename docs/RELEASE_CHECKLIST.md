# Cowork Adoption Intelligence 7.0.0-testing release checklist

Validation date: **2026-10-07**

## Release artifacts

- [x] Root PBIT is `Cowork Adoption Intelligence V7.pbit`.
- [x] Previous direct-PAX template is archived as
  `release/archive/Cowork Adoption Intelligence V6.0.0 - Direct PAX.pbit`.
- [x] Editable V7 PBIP source is synchronized under `src/` and excludes `.pbi`
  local state.
- [x] Required PAX parameter defaults are blank and include direct SharePoint
  HTTPS-path and authentication guidance.
- [x] Eight report pages remain in the focused page order.
- [x] Eight published report previews use deterministic synthetic data only and
  are covered by `images/report-pages/SYNTHETIC_PROVENANCE.json`.
- [x] DRPP, customer, tenant, source-template, and rendered-QA screenshots are
  excluded from the repository.

## Report and model

- [x] Page order is:
  1. Adoption Scorecard
  2. Weekly Adoption & Usage
  3. Scalable Work Patterns
  4. Demand & Capacity Scenario
  5. Adoption Maturity
  6. Category Users
  7. Capacity Assumptions
  8. Adoption Metric Guide
- [x] Report inventory is 8 pages, 296 visuals, and 29 bookmarks.
- [x] Model inventory is 50 tables, 362 measures, and 32 relationships.
- [x] PBIR validation returned zero errors.
- [x] The only PBIR warning was unavailable remote JSON schema retrieval.
- [x] V7 TMDL deserialized successfully.
- [x] Packaged DataModelSchema loaded successfully through TOM.
- [x] Bookmark target audit returned zero missing targets after obsolete
  references were removed.
- [x] Adoption Maturity bookmark state uses `WeekStart`, matching the rendered
  weekly stage chart and accessibility description.
- [x] All eight pages rendered in Fit to page without visual errors against the
  deterministic synthetic dataset.
- [x] Adoption Maturity rendered both `Delegating` and `Uses scheduling` states
  with visible task-count labels.
- [x] Post-fix live Desktop/DAX validation reconciled 212 Delegating tasks and
  688 Uses scheduling tasks to all 900 synthetic tasks.
- [x] The task chart says `Task count by selected users` and does not claim that
  individual tasks were scheduled or automated.
- [x] KPI titles use plain-language labels, including `Delegating / scheduling`
  and `Tasks using 2+ skills`.

## Runtime reconciliation

- [x] The published validation baseline is deterministic synthetic data from
  generator seed `20260907`; it contains no DRPP, tenant, or customer data.
- [x] Observed tasks = 900.
- [x] Task users = 72.
- [x] Modeled assisted hours = 505.8167 under the active assumptions.
- [x] Modeled labor value = 36,418.8 at the loaded synthetic rate.
- [x] After-hours tasks = 665 (73.8889%).
- [x] Reported scheduled tasks = 96 (10.6667% of reported tasks).
- [x] Tasks using 2+ skills = 100% of observed tasks.
- [x] Uses scheduling users = 50; the selected cohort used 688 tasks in total.
- [x] Task mapping classified 876 of 900 tasks as business tasks and 24 as
  orchestration-only; unclassified tasks = 0.

## Template export and label

- [x] `Cowork Adoption Intelligence V7.pbit` is a valid ZIP package.
- [x] PBIT SHA-256 is
  `50D495810EF3ECABD8AA119CBC45582CBED5024D4CFE8E1FDEE8C3436D292CDD`.
- [x] Package size is 840,824 bytes with 355 ZIP entries.
- [x] Both required PAX parameters are blank.
- [x] Package model contains no local QA paths, customer URLs, or customer
  source filenames.
- [x] Package contains no imported `DataModel` payload.
- [x] Public/Not Restricted label metadata is enabled with `ContentBits=0`.
- [x] Desktop-generated `SecurityBindings` is present (11,110 bytes) and was
  preserved while obsolete bookmark targets were removed.

## Documentation and security

- [x] README describes the V7 direct paired-file path and eight-page report.
- [x] SETUP documents local, SharePoint, and OneLake file locations.
- [x] SECURITY documents the two-file boundary, blank parameter defaults, and
  verified label state.
- [x] Legacy automation/sample packages are identified as V5 resources.
- [x] Interpretation guidance retains the current page order and guardrails.
- [x] The only tracked report-page screenshots are the eight approved synthetic
  previews; their hashes and source controls are recorded in the provenance
  manifest.
- [x] No customer data, local profile paths, credentials, or `.pbi` state are
  tracked.

## Final publication gate

- [x] Release hashes and counts match `docs/RELEASE_VERIFICATION.json`.
- [x] Repository-relative Markdown links resolve.
- [x] JSON documents parse successfully.
- [x] `git diff --check` passes.
- [x] The final diff contains only release artifacts, synchronized source, and
  directly related documentation.
- [x] Publication requires an explicit final preview and approval before push.
