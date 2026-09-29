# Cowork Adoption Intelligence 5.0.0-testing release checklist

Validation date: **2026-09-29**

## Release artifacts

- [x] Root PBIT is `Cowork Adoption V3.pbit`.
- [x] Editable PBIP source uses the recommended-layout manifest and excludes
  `.pbi` local state.
- [x] Report and model source match the validated nine-page build.
- [x] `automation/` contains the container, deployment, and Power Automate
  implementation.
- [x] `release/Cowork-Adoption-Intelligence-Automation-v0.1.0.zip` matches the
  checked-in automation source.
- [x] Fabricated sample data remains separate from the report template.
- [x] Prior V4.0 templates remain under `release/archive/` for rollback reference
  only.

## Report and model

- [x] Page order is:
  1. Cowork Adoption Scorecard
  2. Weekly Adoption & Usage
  3. Adoption by Attributes
  4. Scalable Work Patterns
  5. Demand & Capacity Scenario
  6. Adoption Maturity
  7. Enablement Partners
  8. Capacity Assumptions
  9. Adoption Metric Guide
- [x] Start Here guidance is integrated into Cowork Adoption Scorecard.
- [x] Report inventory is 9 pages, 284 visuals, and 27 bookmarks.
- [x] PBIR validation returned zero errors.
- [x] The only PBIR warnings were four unavailable remote JSON schemas.
- [x] All nine pages rendered in Power BI Desktop.
- [x] Adoption Metric Guide rendered after pending model changes were applied.
- [x] The template prompts only for `PreprocessedOutputPath`.

## Template export and label

- [x] The template was exported from the authoritative PBIP source.
- [x] The template was opened in a clean Power BI Desktop process.
- [x] Fabricated sample entities loaded successfully.
- [x] The Public sensitivity label was applied before the final export.
- [x] The final PBIT was reopened and the Public label persisted.
- [x] The package contains no imported `DataModel` payload.
- [x] The package contains a Desktop-generated `SecurityBindings` stream.
- [x] Package label metadata records content bits `0` and therefore no label
  encryption.
- [x] The final PBIT contains 9 page definitions and 27 bookmark definitions.

## Python and compatibility validation

- [x] The exact bundled processor generated 13 entity CSVs plus `manifest.json`
  from the fabricated sample.
- [x] Sample reconciliation returned 3,342 Cowork audit rows, 900 task threads,
  72 active users, and 2,225 prompts.
- [x] `Validate-CoworkCompatibility.py` returned `status: valid`.
- [x] The automation package preserves the processor validated at 1,050,000 audit
  rows and 70,000 users.
- [x] Python syntax validation passes against the checked-in automation files.
- [x] PowerShell parsing passes against the checked-in automation scripts.
- [x] Automation JSON parses successfully.

## Power Automate and Azure

- [x] Power Automate is the orchestrator and does not process audit rows.
- [x] Trigger concurrency is documented as one.
- [x] The flow starts and monitors one Azure Container Apps Job.
- [x] Power BI refresh is gated on successful collection, preprocessing, and
  validation.
- [x] Generic notifications exclude private audit, user, path, tenant, and
  manifest details.
- [x] The custom ACA job-start role is included.
- [x] The logic JSON is identified as an implementation map, not an importable
  solution ZIP.

## Documentation and security

- [x] README describes the nine-page layout and combined automation path.
- [x] SETUP covers fabricated, manual production, and scheduled automation paths.
- [x] Interpretation guidance covers all nine pages and separates observed,
  optional, derived, and modeled evidence.
- [x] SECURITY documents the verified Public label and `SecurityBindings` state.
- [x] Obsolete current-release SharePoint and raw-Purview instructions were
  removed.
- [x] Old ten-page screenshots, walkthrough media, and storyboard were removed
  from the current release surface.
- [x] All repository-relative Markdown links resolve.
- [x] No secrets, customer data, local profile paths, or `.pbi` state are tracked.

## Final publication gate

- [x] Release hashes and byte counts are reconciled in
  `docs/RELEASE_VERIFICATION.json`.
- [x] `git diff --check` passes.
- [x] The final diff contains only the release artifacts and directly related
  documentation.
- [x] A focused local commit includes the required Copilot co-author trailer.
- [x] The exact public commit contents are recorded in the release commit and
  publication summary.
- [x] Explicit user approval has been received before pushing to GitHub.
