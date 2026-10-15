# Archived Cowork Adoption Intelligence templates

These data-free templates are retained for rollback and historical comparison:

- `Cowork Adoption Intelligence V5.0.0 - Preprocessed Entities.pbit`
- `Cowork Adoption Intelligence V4.0.0 - Raw Purview.pbit`
- `Cowork Adoption Intelligence V4.0.0 - SharePoint.pbit`
- `Cowork Adoption Intelligence V6.0.0 - Direct PAX.pbit`

The V5 template uses the validated 13-entity preprocessor contract. The V4
templates parse raw Purview or SharePoint inputs inside Power Query.

New deployments should use the root
`Cowork Adoption Intelligence V8.pbit`, which directly accepts the paired PAX
Purview interactions and Entra users CSV files. Existing V5 automation
deployments can continue using the archived preprocessed template and the
versioned automation bundle.
