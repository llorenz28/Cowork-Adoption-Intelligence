# Cowork Adoption Intelligence: interpretation guide

This guide explains the question each report page answers, how to read it, and
what to verify before acting.

> The screenshots and packaged sample use fabricated data. They are not customer
> findings, targets, or benchmarks. Modeled hours depend on declared assumptions
> and must not be presented as observed savings.

## Five safeguards before interpretation

1. Confirm the reporting period and every active filter.
2. Check source availability in the report and the Adoption Metric Guide.
3. Read each metric's Data Status before interpreting it.
4. Compare trends and denominators before interpreting a single headline.
5. Protect user-level data and never use this report as a personnel scorecard.

## Metric confidence

| Label | Meaning | Safe wording |
| --- | --- | --- |
| Observed | Counted from a connected source field | "The connected export contains..." |
| Derived | Calculated from observed fields | "The report calculates..." |
| Modeled | Observed activity combined with a declared assumption | "Under the selected assumptions..." |
| Allocated estimate | A modeled total distributed to a lower grain | "The report allocates the estimate..." |
| Unavailable | Required evidence is absent | "This cannot be calculated from the current inputs." |
| Convention | A template-defined threshold, cap, or weight | "The template defines..." |
| Reference | A definition or interpretation rule | "The guide states..." |
| Optional input | Requires a separate customer-controlled export | "This is available when..." |

## 1. Start Here

**Purpose:** Route a business question to the correct report page.

**How to read it:** Begin with the decision, not the largest number. The ten
pages separate executive status, weekly trends, organizational patterns, user
maturity, potential champions, work mix, modeled assisted hours, score guidance,
and metric definitions.

**What to do next:** Open one destination, then confirm its date range, filters,
and data-status notes before quoting a result.

## 2. Executive Summary

**Purpose:** Summarize the latest active week's adoption reach, consistency,
intensity, and delegation maturity.

**How to read it:** Read weekly active users and weekly tasks first, then prompts
per active user, active days per user, and weekly return rate. The 0-100 adoption
momentum index defaults to:

- 35% weekly return rate
- 25% active-day consistency, capped at three days
- 25% prompt intensity, capped at 12 prompts per active user
- 15% share of active users on delegation rung 3 or 4

The defaults and optional controls are explained on **Momentum Score Guide**.
The index returns blank when the four weights do not total 100%. A
customer-tuned index is comparable only over time under the same settings, not
across tenants.

**What to do next:** Open Weekly Adoption & Usage to inspect the component trend.
State the active week, filter context, weights, and caps whenever sharing the
index.

## 3. Weekly Adoption & Usage

**Purpose:** Show whether Cowork use is growing, recurring, and distributed
across the latest 12 active weeks.

**How to read it:** Use the bookmarks to switch among usage overview, weekly
active users, adoption momentum, prompts per user, active days, and return rate.
The display ends on the latest week containing observed Cowork activity. Darker
heatmap cells indicate higher relative intensity in the filtered visual; read
the number for precision.

**What to do next:** Compare the same dates and population. Investigate sharp
changes against export coverage, holidays, rollout timing, and filter changes.

## 4. Adoption by Attributes

**Purpose:** Show where adoption and maturity patterns differ across available
organization attributes.

**How to read it:** Task volume is observed from Purview. Department and country
depend on matching optional organization enrichment. Prompt-volume and
delegation tiers use the same conventions documented on User Maturity.

**What to do next:** Treat a blank organizational breakdown as unavailable
enrichment, not zero activity. Confirm population sizes before comparing groups.

## 5. User Maturity

**Purpose:** Describe how deeply users delegate work and how consistently they
use Cowork.

**How to read it:** One ladder is used throughout the report:

| Rung | Definition |
| --- | --- |
| Not started | No observed tasks in the selected period |
| Trying | Shorter single-skill work |
| Using | Average elapsed task duration is at least five minutes |
| Delegating | At least 30% of observed tasks are multi-skill |
| Automating | Any lifetime scheduled-task total in the optional usage export |

The five-minute and 30% thresholds are conventions. The Automating rung is
lifetime-scoped because the admin-center usage export has no date grain; every
other rung is period-scoped. Scheduled share also does not respond to date
filters. Audit Coverage compares like-for-like totals only in an un-narrowed date
context and returns blank under a date filter.

Rolling 12-week prompt-volume tiers are population-relative: Power is the top
10% and active in at least 9 of 12 weeks; Habitual is the top 40% and active in
at least 9 weeks; Novice is the top 80%; Low is below that; Inactive has no
prompts. Fewer than 20 active users returns Insufficient sample.

**What to do next:** Pair maturity with role and work-category context. Sample
approved source records before describing activity as complex or automated.

## 6. Cowork Champions

**Purpose:** Identify potential enablement champions and category or department
coverage gaps.

**How to read it:** Eligibility requires at least three observed task threads
across at least two active weeks in the current date and category context. The
0-100 evidence score combines 40% task-activity percentile, 35% active-week
consistency percentile, and 25% normalized delegation maturity. The tier returns
the Top 5%, Top 10%, or Top 20% after deterministic tie-breaking; Top 10% is the
default.

**What to do next:** Treat the list as an outreach starting point, not a
performance rating. Confirm role fit, willingness, manager support, and
appropriate data use before naming or contacting anyone.

## 7. Activity & Assisted Hours

**Purpose:** Connect observed Cowork activity with transparent, assumption-based
assisted-time estimates.

**How to read it:** Activity records and active users are observed. Estimated
hours saved are modeled from observed category task volume and declared Low,
Mid, or High time-saved assumptions. Category results are allocated estimates,
not direct per-skill metering or a time study.

**What to do next:** Confirm the selected estimate basis and source citations.
Present a range and label estimated hours as modeled, not realized savings.

## 8. What They Use It For

**Purpose:** Explain what kinds of work users ask Cowork to perform.

**How to read it:** Observed skill and tool invocations are grouped into task
categories. High, Mid, and Low action-value tiers are reference attributes based
on declared category ranges, not measured value or user ratings. The Usage
Explorer bookmarks switch between action and user detail while preserving
filters.

**What to do next:** Review unmapped skills first. Validate dominant categories
against approved source records and business context before recommending a new
workflow.

## 9. Momentum Score Guide

**Purpose:** Explain the live 0-100 adoption momentum score before exposing its
optional tuning controls.

**How to read it:** Start with the live score and the four plain-language
components. The score is an adoption signal, not an employee-performance
rating. Advanced settings retain default weights of return 35%, consistency
25%, intensity 25%, and maturity 15%. Default caps are three active days and 12
prompts per active user. If weights do not total 100%, the index becomes blank
and Momentum Weight Status explains the issue.

**What to do next:** Record any changes with the reporting period. Do not compare
indexes produced under different settings or across tenants with different
conventions.

## 10. Adoption Metric Guide

**Purpose:** Define every page's metrics, thresholds, dependencies, and
interpretation boundaries.

**How to read it:** The Section filter lists all ten report page display names in
report order. Read each definition with its Data Status. Missing optional data
means unavailable evidence, not zero activity.

**What to do next:** Copy the metric definition, reporting period, filters, and
Data Status into presentations and decision records.

## Recommended decision language

| Scenario | Defensible wording |
| --- | --- |
| Adoption is broadening | "Weekly active users increased in the selected period while return rate remained stable or improved." |
| Use is concentrated | "Observed activity is concentrated among the displayed users or departments; role and rollout context should be checked." |
| Maturity is increasing | "The report calculates a higher delegation index from observed activity and the disclosed lifetime scheduling attribute." |
| Champion outreach | "These users meet the report's engagement evidence floor and selected percentile tier; role fit and willingness still require confirmation." |
| Assisted-time scenario | "Under the selected time-saved basis, the report models the displayed assisted hours." |

Avoid wording that claims Cowork caused productivity gains, proves automation,
measures employee performance, or replaces billing and compliance records.

## Usage and compliance disclaimer

Coverage depends on licensing, audit settings, retention, product behavior,
permissions, export completeness, optional source availability, and identity
matching. Follow organizational privacy, labor, works-council, security,
retention, and sensitivity-label requirements.
