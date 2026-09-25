# Cowork Adoption Intelligence V4.1 release checklist

Release target: **4.1.0**
Preprocessor target: **0.1.0**
Validation date: **2026-09-25**

## Release artifacts

- [x] Root `Cowork Adoption Intelligence V4.pbit` is the new data-free,
  preprocessed-ingestion template.
- [x] Editable PBIP source under `src/` matches the released report and model.
- [x] `scripts/Cowork_Purview_Preprocessor_v0.1.0.py` and
  `scripts/cowork-contract.json` are version-matched.
- [x] `scripts/README.md` documents download, operation, safety, and
  troubleshooting.
- [x] Previous raw-Purview and SharePoint V4.0 PBITs are backed up under
  `release/archive/`.
- [x] `release/Cowork-Adoption-Intelligence-Preprocessor-v0.1.0.zip` contains
  the script, contract, instructions, PBIT, and checksum file.
- [x] `docs/RELEASE_VERIFICATION.json` contains final hashes and package
  inventory.

## Model and report validation

- [x] The protected canonical remediation project was not modified.
- [x] Offline TOM/TMDL import passed with 45 tables, 321 measures, 408 columns,
  45 partitions, and 27 active relationships.
- [x] PBIR validation passed with zero errors and zero warnings.
- [x] The exported PBIT prompted only for `PreprocessedOutputPath`.
- [x] A clean Power BI Desktop process loaded all 45 partitions successfully.
- [x] Live DAX reconciliation matched 14,624 Cowork detail rows, 260 thread
  tasks, 21 active users, and 10,816 prompts.
- [x] Champion reconciliation passed at `2 summary / 2 row-level / 0 delta`.
- [x] Both expected Champion identities, ranks, and scores matched.
- [x] All 10 pages, 39 bookmarks, hidden visual states, and required
  interactions were validated before export.

## Preprocessor validation

- [x] The script uses only the Python standard library.
- [x] Input and output paths must be separate and non-overlapping.
- [x] Source discovery is recursive and deterministic.
- [x] Required source/header failures stop the run.
- [x] Malformed `AuditData` JSON stops the run; it is not silently skipped.
- [x] Deduplication uses immutable record identity and payload evidence.
- [x] Output is staged and validated before destination replacement.
- [x] An existing foreign output folder is not overwritten.
- [x] The manifest records versions, hashes, source files, row counts,
  duplicates, and collision checks.
- [x] `--validate-output` verifies the published entities independently.
- [x] The exact repository script and contract pass a fresh sample-data run.
- [x] The exact repository script and contract pass a fresh lower-scale
  regression run.

## Scale evidence

- [x] 70,976-row fixture preprocessing completed in 14.811 seconds.
- [x] The corresponding Desktop load completed in 12.894 seconds and reconciled
  exactly with the validated baseline.
- [x] 1,050,000-row, 70,000-user synthetic preprocessing completed in 200.528
  seconds.
- [x] The enterprise synthetic model loaded with exact core-count parity.
- [x] Documentation states that timings are machine-dependent and not a
  service-level objective.
- [x] Documentation states that the 5.50 GiB large-scale Desktop peak is scale
  evidence, not a safe customer memory target.

## Security and privacy

- [x] The released PBIT contains no imported customer data.
- [x] The released PBIT contains no machine-bound `SecurityBindings` stream.
- [x] The released PBIT stores no local user-profile or fixture path.
- [x] Repository source contains no `.pbi` local state.
- [x] Repository source contains no customer data, credentials, tokens, or
  retained SQLite work database.
- [x] `SECURITY.md` covers raw data, generated entities, manifests, output
  replacement, scheduled refresh, labeling, retention, and least privilege.
- [x] Sample content remains synthetic and uses only reserved example domains.

## Documentation

- [x] `README.md` presents the V4.1 preprocessor workflow as the primary path.
- [x] `SETUP.md` includes sample and production commands.
- [x] `scripts/README.md` explains the 13 entities and `manifest.json`.
- [x] Legacy V4.0 templates are clearly marked as rollback artifacts.
- [x] Power BI Service refresh behavior is explicit: the service reads generated
  files and does not run Python.
- [x] All repository-relative documentation links resolve.

## Final publication gate

- [x] Python syntax and CLI validation pass.
- [x] PBIR and offline TOM/TMDL validation pass against the repository source.
- [x] The release ZIP inventory and internal checksums pass.
- [x] Final hashes in `docs/RELEASE_VERIFICATION.json` match repository files.
- [x] `git diff --check` passes.
- [x] The final Git diff is limited to the validated release, source
  synchronization, script, package, archive, and directly related docs.
- [x] Branch is committed, pushed, and opened as a pull request against
  `microsoft/Cowork-Adoption-Intelligence`.
