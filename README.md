# Cowork Adoption Intelligence

> **Understand how Microsoft 365 Copilot Cowork is being adopted, how consistently
> people return, what work they delegate, and where potential enablement champions
> are emerging.**

[![Status](https://img.shields.io/badge/status-testing-D83B96)](CHANGELOG.md)
[![Power BI](https://img.shields.io/badge/Power%20BI-PBIT%20%2B%20PBIP-F2C811)](src/)
[![Template data](https://img.shields.io/badge/template-data--free-008272)](SECURITY.md)
[![Sample data](https://img.shields.io/badge/sample-fabricated-0078D4)](sample_data/)

> [!IMPORTANT]
> **Template status: Testing.** This report template is under active validation
> and may change before a production-ready release. Validate its outputs and
> metric definitions before using findings for production decisions.

Cowork Adoption Intelligence is a data-free Power BI template for Microsoft 365
Copilot Cowork program owners, adoption leads, and enablement teams. It turns
approved Microsoft Purview audit exports into a ten-page adoption report with
activation, sustained usage, action patterns, delegation maturity, and potential
champion signals.

> **Data source:** The core report uses Microsoft Purview Audit
> `CopilotInteraction` records whose `CopilotEventData.AppHost` identifies
> Cowork. Optional Microsoft 365 usage and organization files add reconciliation
> and segmentation.

![Cowork Adoption Intelligence executive summary populated with fabricated sample data](images/report-pages/02-executive-summary.png)

> **Cowork Adoption Intelligence Walkthrough:** a narrated executive tour of
> adoption momentum, usage maturity, potential champions, work patterns, and
> transparent modeled value.

[Watch or download the MP4](media/Cowork-Adoption-Intelligence-Walkthrough.mp4) ·
[Read the transcript](media/Cowork-Adoption-Intelligence-Walkthrough-transcript.md) ·
[Download subtitles](media/Cowork-Adoption-Intelligence-Walkthrough.srt)

---

## New here? Start in 3 steps

1. Download the
   [local-folder Power BI template](Cowork%20Adoption%20Intellgience%20V3.pbit)
   and the
   [fabricated sample package](release/Cowork-Adoption-Intelligence-Sample-Data.zip).
2. Extract the sample ZIP, open the `.pbit`, and set `DataFolderPath` to the
   extracted folder.
3. Select **Load**, refresh, and confirm the report shows 72 fictional users.

The sample path takes about 10 minutes and requires no tenant role. Follow the
[step-by-step setup guide](SETUP.md#path-a-try-the-report-with-fabricated-data)
for screenshots, validation checks, production data collection, and
troubleshooting. Use the
[interpretation guide](INTERPRETATION_GUIDE.md) before presenting results.

To refresh directly from a SharePoint document library, download the
[SharePoint edition](Cowork%20Adoption%20Intellgience%20V3%20-%20SharePoint.pbit)
and follow the [SharePoint setup guide](docs/SHAREPOINT_SETUP.md).

> **Not ready to collect production data?** Start with the sample. It is
> deterministic, fabricated, and uses only `@example.com` identities and
> `tenant.example.com` URLs.

---

## What the report answers

| Page | Business question |
| --- | --- |
| **Start Here** | Which page should I use for my question? |
| **Executive Summary** | How broad, active, and mature is Cowork adoption? |
| **Weekly Adoption & Usage** | Are users and task activity growing and recurring? |
| **Adoption by Attributes** | Where do adoption and maturity patterns differ across available organization attributes? |
| **User Maturity** | Are people progressing from first use to sustained delegation? |
| **Cowork Champions** | Who shows strong, consistent category-level engagement for possible enablement outreach? |
| **Activity & Assisted Hours** | Which observed work patterns account for activity and modeled assisted time? |
| **What They Use It For** | What kinds of work are people delegating, and which records explain the totals? |
| **Momentum Score Guide** | What does the adoption momentum score mean, and when should its optional weights or caps be tuned? |
| **Adoption Metric Guide** | How is each metric calculated and how should it be interpreted? |

Potential champion results are enablement signals, not employee-performance
ratings. Confirm role fit, willingness, and manager support before outreach.

![Weekly adoption and usage page populated with fabricated sample data](images/report-pages/03-weekly-adoption.png)

## Why use this template

- Separate adoption and enablement questions from billing and financial reporting.
- Measure activation, active weeks, repeat activity, task depth, and skill usage.
- Compare Purview-observed Cowork activity with the optional Microsoft 365 Cowork
  usage export.
- Find potential category champions with a documented score, eligibility floor,
  and Top 5%, Top 10%, or Top 20% lens.
- Keep every production input outside the Git repository and under customer
  control.
- Start with a packaged-data smoke test before requesting tenant access.

## Choose your path

| | Fabricated sample | Production exports |
| --- | --- | --- |
| **Best for** | Evaluation, training, and troubleshooting | Ongoing organization reporting |
| **Setup time** | About 10 minutes | Depends on data-owner handoffs |
| **Tenant role** | None | Purview `Audit Reader`; optional `Reports Reader` |
| **Identity data** | Fictional `@example.com` users | Customer-controlled approved exports |
| **Instructions** | [Path A](SETUP.md#path-a-try-the-report-with-fabricated-data) | [Path B](SETUP.md#path-b-connect-production-exports) |

| Source edition | Required parameters | Scheduled refresh |
| --- | --- | --- |
| **Local folder** | `DataFolderPath` | Requires an on-premises data gateway after publishing |
| **SharePoint** | `SharePointSiteUrl`, `SharePointFolderUrl` | Uses the cloud SharePoint connector; no local-file gateway |

## Before you start

- Windows with a current
  [Power BI Desktop](https://powerbi.microsoft.com/desktop/).
- A local folder for the sample or protected production working copies, or an
  approved SharePoint document-library folder for the SharePoint edition.
- For production, an authorized Purview owner who can export Audit Search
  results. The Power BI operator does not need every tenant role.
- The ability to apply your organization's required sensitivity label before
  sharing a refreshed customer-data report.

## Production inputs

| Input | Required | What it adds |
| --- | --- | --- |
| Purview Audit Search CSV files | **Yes** | Users, task threads, skills, resources, dates, categories, and delegation signals |
| Cowork usage details CSV | Recommended | Admin-center totals, active days, scheduled/user-initiated split, and reconciliation |
| Organization CSV | Optional | Department, business unit, role, manager, and geography |
| Identity enrichment CSV | Optional | Friendly display names for audit identities |
| Consumption CSV | Optional | Supporting consumption fields where available; not required for core adoption analysis |

All supported files can live under one protected folder. The local edition
prompts for `DataFolderPath`. The SharePoint edition prompts for
`SharePointSiteUrl` and `SharePointFolderUrl`. Both discover supported files in
the selected folder and its subfolders.

See [Setup](SETUP.md) for exact filenames, headers, owner handoffs, and
validation checks. See [Security roles and access](docs/SECURITY_ROLES.md)
before requesting permissions.

## Release kit

| Resource | Open or download |
| --- | --- |
| Local-folder Power BI template | [`Cowork Adoption Intellgience V3.pbit`](Cowork%20Adoption%20Intellgience%20V3.pbit) |
| SharePoint Power BI template | [`Cowork Adoption Intellgience V3 - SharePoint.pbit`](Cowork%20Adoption%20Intellgience%20V3%20-%20SharePoint.pbit) · [`Setup`](docs/SHAREPOINT_SETUP.md) |
| Fabricated sample package | [`release/Cowork-Adoption-Intelligence-Sample-Data.zip`](release/Cowork-Adoption-Intelligence-Sample-Data.zip) |
| Step-by-step setup | [`SETUP.md`](SETUP.md) |
| Interpretation guide | [`INTERPRETATION_GUIDE.md`](INTERPRETATION_GUIDE.md) |
| Narrated walkthrough | [`MP4`](media/Cowork-Adoption-Intelligence-Walkthrough.mp4) · [`Transcript`](media/Cowork-Adoption-Intelligence-Walkthrough-transcript.md) · [`Subtitles`](media/Cowork-Adoption-Intelligence-Walkthrough.srt) · [`Build notes`](media/README.md) |
| Editable PBIP source | [`src/Cowork Adoption Intelligence.pbip`](src/Cowork%20Adoption%20Intelligence.pbip) |
| Unpacked sample and generator | [`sample_data/`](sample_data/) · [`build_sample_data.py`](build_sample_data.py) |
| Security guidance | [`SECURITY.md`](SECURITY.md) · [`docs/SECURITY_ROLES.md`](docs/SECURITY_ROLES.md) |
| Release evidence | [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) · [`docs/RELEASE_VERIFICATION.json`](docs/RELEASE_VERIFICATION.json) |

## Repository structure

```text
Cowork Adoption Intellgience V3.pbit
Cowork Adoption Intellgience V3 - SharePoint.pbit
README.md
SETUP.md
build_sample_data.py
docs/
  RELEASE_CHECKLIST.md
  RELEASE_VERIFICATION.json
  SHAREPOINT_SETUP.md
  SECURITY_ROLES.md
images/report-pages/
media/
  Cowork-Adoption-Intelligence-Walkthrough.mp4
  Cowork-Adoption-Intelligence-Walkthrough-transcript.md
  Cowork-Adoption-Intelligence-Walkthrough.srt
release/
  Cowork-Adoption-Intelligence-Sample-Data.zip
sample_data/
src/
  Cowork Adoption Intelligence.pbip
  Cowork Adoption Intelligence.Report/
  Cowork Adoption Intelligence.SemanticModel/
tools/
  New-SharePointPbit.ps1
```

## Security and privacy

The distributable `.pbit` contains no imported customer data and no
machine-bound `SecurityBindings` stream. The included sample is fabricated.
Production Purview and organization exports can contain personal and business
information; never commit them, attach them to an issue, or place them in an
unapproved location.

Read [SECURITY.md](SECURITY.md) before using production data.

## Interpretation boundaries

Read the [interpretation guide](INTERPRETATION_GUIDE.md) for page-by-page
definitions, safe wording, and recommended follow-up checks.

- Purview coverage depends on licensing, retention, permissions, and emitted
  fields.
- The Microsoft 365 usage export is a user-level aggregate, not an event
  timeline.
- Scheduled and user-initiated task counts come from the optional usage export.
- Task duration is elapsed time between the first and last audit event in a
  thread, not measured human attention.
- Modeled value combines observed task activity with published assumptions or
  customer-selected inputs; it is not a financial audit.
- Champion scores identify engagement evidence for enablement planning, not
  performance, aptitude, or promotion readiness.

## Release status

The current release is **3.0.0-testing**. Review the
[changelog](CHANGELOG.md) and
[release checklist](docs/RELEASE_CHECKLIST.md) before broad distribution.

For problems with the template or documentation, open a
[GitHub issue](https://github.com/microsoft/Cowork-Adoption-Intelligence/issues)
without attaching tenant exports, credentials, customer identifiers, or
identifiable screenshots.

## License

This project is licensed under the [MIT License](LICENSE).

## Trademarks

This project may contain Microsoft trademarks or logos. Use of Microsoft
trademarks or logos must follow
[Microsoft's Trademark and Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks).
Modified versions must not cause confusion or imply Microsoft sponsorship.
