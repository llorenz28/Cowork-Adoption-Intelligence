# Cowork Adoption Intelligence v2 Testing release checklist

## Report

- [x] PBIR validation reports zero errors.
- [x] All canvas bookmark actions resolve to internal bookmark IDs.
- [x] Filter drawers open and close without cross-page jumps.
- [x] The template opens with only the required `DataFolderPath` prompt.
- [x] The bundled synthetic sample refreshes every supported report capability.
- [x] All nine pages render, including Cowork Champions after User Maturity.
- [x] The category lens recalculates candidates and department coverage.
- [x] All seven category tiles render in one row with readable labels.
- [x] Candidate and coverage panels align; all eight default candidates are
  visible without clipping.
- [x] Selection basis and enablement guidance fill the lower analysis row
  without text truncation.
- [x] Top 5%, Top 10%, and Top 20% return 4, 8, and 15 sample candidates.
- [x] The Champions drawer preserves category/tier state through open and close.
- [x] Start Here navigation opens Cowork Champions.
- [x] Adoption Metric Guide defines the score, floor, tiers, coverage, and
  interpretation boundary.

## Security and portability

- [x] PBIT contains no imported customer data.
- [x] PBIT contains no `SecurityBindings` stream or content-type override.
- [x] PBIP source contains no `.pbi` local state or user-profile paths.
- [x] PBIT retains the tenant Public sensitivity label without encryption.
- [x] Public label metadata remains after the machine-bound security stream is removed.
- [x] Sample identities and URLs use only synthetic `example.com` values.

## Repository

- [x] Existing repository state has a dated rollback reference.
- [x] Existing canonical Adoption template has a dated backup.
- [x] Documentation describes the one-folder setup and classification behavior.
- [x] Unrelated working-tree changes are excluded from the release.
- [x] Final outbound publication approval is received.
