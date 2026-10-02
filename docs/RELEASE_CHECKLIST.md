# Cowork Adoption Intelligence 6.0.0-testing release checklist

Validation date: **2026-10-02**

## Release artifacts

- [x] Root PBIT is `Cowork Adoption Intelligence V6.pbit`.
- [x] Previous preprocessed template is archived as
  `release/archive/Cowork Adoption Intelligence V5.0.0 - Preprocessed Entities.pbit`.
- [x] Editable PBIP source is under `src/` and excludes `.pbi` local state.
- [x] Required PAX parameter defaults are blank in the release source.
- [x] Eight validated page renders are under `images/report-pages/`.

## Report and model

- [x] Page order is:
  1. Cowork Adoption Scorecard
  2. Weekly Adoption & Usage
  3. Scalable Work Patterns
  4. Demand & Capacity Scenario
  5. Adoption Maturity
  6. Category Users
  7. Capacity Assumptions
  8. Adoption Metric Guide
- [x] Report inventory is 8 pages, 296 visuals, and 29 bookmarks.
- [x] Model inventory is 49 tables, 353 measures, and 32 relationships.
- [x] PBIR validation returned zero errors.
- [x] The only PBIR warning was unavailable remote JSON schema retrieval.
- [x] Packaged bookmark target audit returned zero missing targets.
- [x] All eight pages rendered without visual errors, clipping, or overlap.
- [x] Demand & Capacity percentage labels and both department heatmaps rendered.
- [x] Category-task matrix values and three numeric heatmaps rendered.

## Runtime reconciliation

- [x] Observed tasks = 97.
- [x] Task users = 16.
- [x] Modeled assisted hours = 52.0167 under the active Mid assumptions.
- [x] Modeled labor value = 3,745.2 at the loaded QA rate.
- [x] Observed task share totals 100% across categories.
- [x] Modeled assisted-hours share totals 100% across categories.
- [x] After-hours tasks = 34 (35.0515%).
- [x] Custom category minutes were proven to change modeled assisted hours only
  when the Custom basis is selected.

## Template export and label

- [x] `Cowork Adoption Intelligence V6.pbit` is a valid ZIP package.
- [x] PBIT SHA-256 is
  `B9E100D0677D06D6D2B7B6410A77FEF9DECA838A9296EC9833E19D9D96A4C6EF`.
- [x] Package size is 766,803 bytes with 352 ZIP entries.
- [x] Both required PAX parameters are blank in the package.
- [x] Package model contains no local QA paths or source filenames.
- [x] Package contains no imported `DataModel` payload.
- [x] Packaged semantic model loads successfully from BIM.
- [x] Public/Not Restricted label metadata is enabled with `ContentBits=0`.
- [x] Desktop-generated `SecurityBindings` is present (11,110 bytes).

## Documentation and security

- [x] README describes the V6 direct paired-file path and eight-page report.
- [x] SETUP documents local, SharePoint, and OneLake file locations.
- [x] SECURITY documents the two-file data boundary and verified label state.
- [x] Legacy automation/sample packages are identified as V5 resources.
- [x] Interpretation guidance uses the current page order and terminology.
- [x] No customer data, local profile paths, credentials, or `.pbi` state are
  tracked.

## Final publication gate

- [x] Release hashes and counts match `docs/RELEASE_VERIFICATION.json`.
- [x] Repository-relative Markdown links resolve.
- [x] JSON documents parse successfully.
- [x] `git diff --check` passes.
- [x] The final diff contains only release artifacts and directly related docs.
- [x] A focused release commit is created.
- [x] Explicit approval is confirmed before pushing to GitHub.
