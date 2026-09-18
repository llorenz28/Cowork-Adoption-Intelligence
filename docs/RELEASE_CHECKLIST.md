# Cowork Adoption Intelligence V3 Testing release checklist

## Report

- [x] PBIR validation reports zero errors.
- [x] All canvas bookmark actions resolve to internal bookmark IDs.
- [x] Filter drawers open and close without cross-page jumps.
- [x] The local template opens with only the required `DataFolderPath` prompt.
- [x] The SharePoint template opens with only the required
  `SharePointSiteUrl` and `SharePointFolderUrl` prompts.
- [x] The bundled synthetic sample refreshes every supported report capability.
- [x] All ten pages render, including Cowork Champions after User Maturity.
- [x] The category lens recalculates candidates and department coverage.
- [x] All seven category tiles render in one row with readable labels.
- [x] Candidate and coverage panels align; all eight default candidates are
  visible without clipping.
- [x] Selection basis and enablement guidance fill the lower analysis row
  without text truncation.
- [x] Champion delegation maturity contributes to the score: the synthetic
  sample reaches 100.0 instead of the pre-fix cap at 75.0.
- [x] Top 5%, Top 10%, and Top 20% were re-measured after the scoring correction
  and return 4, 8, and 15 sample candidates.
- [x] The Champions drawer preserves category/tier state through open and close.
- [x] Start Here navigation opens Cowork Champions.
- [x] Adoption Metric Guide defines the score, floor, tiers, coverage, and
  interpretation boundary.
- [x] Momentum Score Guide shows the live score, explains all four components,
  states that it is not a performance rating, and keeps tuning optional.

## Security and portability

- [x] Both PBIT editions contain no imported customer data.
- [x] Both PBIT editions contain no `SecurityBindings` stream or content-type
  override.
- [x] PBIP source contains no `.pbi` local state or user-profile paths.
- [x] PBIT retains the tenant Public sensitivity label without encryption.
- [x] Public label metadata remains after the machine-bound security stream is removed.
- [x] Sample identities and URLs use only synthetic `example.com` values.

## Repository

- [x] Existing repository state has a dated rollback reference.
- [x] Existing canonical Adoption template has a dated backup.
- [x] Documentation describes the one-folder setup and classification behavior.
- [x] SharePoint setup documents the canonical site and folder URL parameters,
  Organizational account authentication, recursive discovery, and rebuild
  command.
- [x] The checked-in SharePoint builder reproduces the published SharePoint
  edition from the local V3 template.
- [x] Interpretation guidance covers all ten pages and separates observed,
  derived, optional, reference, and modeled evidence.
- [x] Walkthrough is 1920x1080, 30 fps, H.264/AAC, narrated, and
  transcript-aligned.
- [x] Walkthrough follows the Adoption-to-enablement story, identifies the
  template as testing, and uses only fabricated report screenshots.
- [x] Unrelated working-tree changes are excluded from the release.
- [x] Final outbound publication approval is received.
