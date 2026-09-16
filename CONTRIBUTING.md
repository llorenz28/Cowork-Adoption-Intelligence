# Contributing

Thank you for helping improve Cowork Adoption Intelligence.

## Before opening an issue

- Search existing issues.
- Remove tenant names, user identities, URLs, secrets, and export content.
- Reproduce the problem with the included fabricated sample when possible.
- Include the Power BI Desktop version, report version, page name, and exact
  error text.

Do not attach production Purview, usage, organization, identity, or consumption
exports.

## Develop locally

1. Clone the repository on Windows.
2. Open `src\Cowork Adoption Intelligence.pbip` in Power BI Desktop.
3. Use the included `sample_data` folder or regenerate it with:

   ```powershell
   python .\build_sample_data.py
   ```

4. Keep `.pbi` local state and all production data outside commits.
5. Validate every visible page, bookmark action, filter drawer, and navigation
   control.
6. Export a data-free PBIT only after confirming no imported model data or
   machine-bound security binding remains.

## Pull requests

A pull request should:

- explain the user problem and resulting behavior
- keep unrelated changes out of the diff
- update setup or interpretation guidance when behavior changes
- use only fabricated `example.com` data in tests and screenshots
- preserve the one-required-parameter experience
- update `CHANGELOG.md` and release evidence for a release change

By contributing, you agree to follow the
[Microsoft Open Source Code of Conduct](CODE_OF_CONDUCT.md).

