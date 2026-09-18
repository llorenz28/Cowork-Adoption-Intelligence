# Cowork Adoption Intelligence: interpretation guide

**Template version:** 3.0.0-testing<br>
**Audience:** adoption leads, program owners, enablement teams, analysts, and Power BI owners

This guide explains what each report page answers, how to read it, what to
investigate, and what can be acted on safely. It is an operating guide, not a
benchmark catalogue.

> The screenshots and packaged sample use deterministic fabricated data. They
> are not customer findings, targets, or benchmarks. Modeled assisted hours
> depend on declared assumptions and must not be presented as observed savings.

## Agenda

1. Version 3 changes and the five-minute reading path
2. Evidence chain and confidence labels
3. Page-by-page walkthrough of all ten report pages
4. Momentum, maturity, champion, and assisted-time methodology
5. Source requirements, validation checks, and defensible decision language

## What's new in version 3

- **Momentum Score Guide** replaces Momentum Settings with a live score,
  component explanations, guardrails, and optional advanced controls.
- The **delegation ladder** is standardized on Not started, Trying, Using,
  Delegating, and Automating with one documented threshold set.
- **Cowork Champions** again includes delegation maturity in its transparent
  40/35/25 evidence score.
- Lifetime scheduled-task grain and date-filter behavior are disclosed.
- Audit Coverage becomes unavailable when a date filter prevents like-for-like
  reconciliation.
- All ten sections of the in-report **Adoption Metric Guide** now document
  dependencies, thresholds, evidence status, and interpretation boundaries.
- A separate SharePoint edition uses the same model and interpretation logic.

## Five-minute orientation

If review time is limited, use this sequence:

| Step | Page | Decision supported |
| --- | --- | --- |
| 1 | **Executive Summary** | Is current adoption broad, recurring, and becoming more mature? |
| 2 | **Weekly Adoption & Usage** | Is the latest result part of a sustained trend or a one-week change? |
| 3 | **User Maturity** | Are users only trying Cowork, or are they handing over deeper and repeatable work? |
| 4 | **What They Use It For** | Which work patterns explain the adoption signal and should inform enablement? |

Use **Cowork Champions** only when the next decision is enablement outreach. Use
**Adoption by Attributes** only after organization enrichment and population
sizes have been checked. Before sharing any result, confirm the definition and
Data Status on **Adoption Metric Guide**.

## The result-context block

Every quoted result should include:

| Context | What to record |
| --- | --- |
| Reporting period | Exact start and end date or the displayed active week |
| Population | Tenant, department, country, category, or selected users |
| Filters | Every active report, page, and visual filter |
| Source status | Purview plus any connected usage, organization, identity, or consumption input |
| Evidence label | Observed, Derived, Convention, Optional input, Modeled, Allocated estimate, or Unavailable |
| Assumptions | Momentum weights and caps; Low/Mid/High assisted-time basis when applicable |

Without this context, a numerically correct result can still be unsuitable for a
decision.

## Evidence chain at a glance

| Source | Model role | What it supports | Required? |
| --- | --- | --- | --- |
| Purview Audit Search CSV | `Fact_CopilotAuditRaw`, `Fact_CoworkDetail`, `Fact_CoworkThread` | Users, observed records, task threads, prompts, dates, skills, resources, duration, and delegation evidence | **Yes** |
| Cowork usage details CSV | `Fact_CoworkUsage` | Reported tasks, scheduled/user-initiated split, active days, and independent reconciliation | Recommended |
| Organization CSV | `Dim_UserOrg` and user attributes | Department, business unit, job family, role, manager, city, country, and cost center | Optional |
| Identity enrichment CSV | `Dim_User` enrichment | Friendly display names for audit identities | Optional |
| Consumption CSV | Supporting consumption facts | Supporting consumption context where available | Optional |
| Template mappings and controls | Skill/category dimensions and disconnected selectors | Category mappings, time assumptions, champion tier, momentum weights, and caps | Included in template |

Purview is the core event evidence. The usage export is a user-level aggregate;
it does not create a historical event timeline. Missing optional inputs mean
**unavailable**, not zero.

## Evidence confidence

| Label | Meaning | Safe wording |
| --- | --- | --- |
| Observed | Counted from a connected source field | "The connected export contains..." |
| Derived | Calculated from observed fields | "The report calculates..." |
| Convention | A template-defined threshold, cap, or weight | "The template defines..." |
| Reference | A definition or interpretation rule | "The guide states..." |
| Optional input | Requires a separate customer-controlled export | "This is available when..." |
| Modeled | Observed activity combined with a declared assumption | "Under the selected assumptions..." |
| Allocated estimate | A modeled total distributed to a lower grain | "The report allocates the estimate..." |
| Unavailable | Required evidence is absent or the current grain is invalid | "This cannot be calculated from the current inputs or filters." |

## Five safeguards before interpretation

1. Confirm the reporting period, population, and every active filter.
2. Check source availability and read the metric's Data Status.
3. Separate observed evidence from derived values, conventions, and models.
4. Compare trends and denominators before interpreting a headline.
5. Protect user-level data and never use this report as a personnel scorecard.

---

## Page 1: Start Here

### Purpose

Route a business question to the report page that carries the appropriate
evidence and interpretation boundary.

### Read it in this order

1. Identify the decision: adoption status, weekly momentum, organizational
   differences, maturity, champion outreach, observed activity, work mix, score
   methodology, or metric definitions.
2. Open one destination page.
3. Confirm the period, filters, and source-status notes on that page.
4. Use Adoption Metric Guide before quoting a result.

### Diagnostic questions

- Am I answering an adoption, enablement, work-pattern, or modeled-value
  question?
- Does the destination require an optional source that is not connected?
- Is the question about a weekly trend, the current active week, or a lifetime
  user attribute?

### Action

Use one primary page for the answer and one corroborating page for context.
Avoid building a conclusion from unrelated headline cards.

### Guardrail

Core adoption pages work from Purview. Organization comparisons, lifetime
scheduling, and independent reconciliation require optional inputs.

## Page 2: Executive Summary

### Purpose

Summarize the latest active week's reach, recurrence, intensity, and delegation
maturity.

### Read it in this order

1. **Weekly active users** - distinct users with observed Cowork activity in the
   latest active week.
2. **Weekly task threads** - deduplicated observed task threads for that week.
3. **Prompts per active user** - weekly prompt volume divided by active users.
4. **Active days per user** - average distinct active dates per user in the
   week.
5. **Weekly return rate** - users active in both the current and previous week,
   divided by users active in the previous week.
6. **Adoption momentum score** - the weighted 0-100 composite described on
   Momentum Score Guide.

### Diagnostic questions

- Did weekly active users increase while return rate stayed stable or improved?
- Is a high activity total broad across users, or concentrated in a small
  group?
- Which momentum component is limiting the composite score?
- Does the displayed week have complete export coverage?

### Action

Open Weekly Adoption & Usage to check whether the result is sustained. If the
score is being used in a review, include the week, filters, weights, and caps.

### Guardrail

The score is an adoption signal, not a target, grade, or cross-tenant benchmark.
It becomes blank when the four selected weights do not total 100%.

## Page 3: Weekly Adoption & Usage

### Purpose

Show whether Cowork use is growing, recurring, and distributed across the latest
12 active weeks.

### Read it in this order

1. Use the metric bookmarks to switch among overview, weekly active users,
   momentum, prompts per user, active days, and return rate.
2. Read the trend from left to right; the window ends on the latest week with
   observed activity.
3. Read heatmap numbers for precision. Color represents relative intensity in
   the current visual and filter context.
4. Compare the same population and filters before and after an inflection.

### Diagnostic questions

- Did reach, recurrence, and intensity move together?
- Is a change isolated to one department or country?
- Did a rollout, campaign, holiday, export boundary, or source issue occur at
  the same time?
- Are new users expanding the population while prior users are returning?

### Action

Use the component that changed to choose the response:

| Pattern | Likely enablement response |
| --- | --- |
| Reach up, return flat or down | Improve onboarding and second-use prompts |
| Return up, reach flat | Scale proven workflows to additional teams |
| Prompts up, active days flat | Encourage repeatable use across more days |
| Active days up, maturity flat | Teach multi-step and skill-based delegation |

### Guardrail

Do not call a trend from one point. Investigate sharp changes against export
coverage, rollout timing, holidays, and filter changes.

## Page 4: Adoption by Attributes

### Purpose

Show where adoption and delegation patterns differ across available
organization attributes.

### Read it in this order

1. Confirm organization enrichment is connected and matching audit identities.
2. Select Department or Country.
3. Compare observed task volume and the shared delegation ladder.
4. Check population size before ranking or comparing groups.
5. Drill to user-level detail only when approved for the decision.

### Diagnostic questions

- Are differences driven by population size or by activity per user?
- Does a group have enough matched users for a stable comparison?
- Is the pattern consistent across reach, prompts, and delegation?
- Could role mix, rollout timing, or work type explain the difference?

### Action

Prioritize groups with sufficient population and a clearly defined enablement
gap. Validate the proposed action with local role and rollout context.

### Guardrail

A blank organizational breakdown means enrichment is unavailable or unmatched,
not that activity is zero. Organizational comparisons must not be interpreted
as employee-performance comparisons.

## Page 5: User Maturity

### Purpose

Describe how deeply people delegate work and how consistently they use Cowork.

### Delegation ladder

The model evaluates users in this order:

| Rung | Rule | Grain |
| --- | --- | --- |
| Not started | No observed task threads | Selected period |
| Trying | Observed tasks, but no higher rule is met | Selected period |
| Using | Average elapsed task duration is at least 5 minutes | Selected period |
| Delegating | At least 30% of observed tasks are multi-skill | Selected period |
| Automating | Any reported scheduled-task total is greater than zero | **Lifetime user total from optional usage export** |

The five-minute and 30% thresholds are template conventions. The ladder index
assigns rung scores 0 through 4 and divides the summed score by the maximum score
for active users.

### Rolling 12-week prompt-volume tiers

| Tier | Rule |
| --- | --- |
| Power users | Top 10% by prompt volume and active in at least 9 of 12 weeks |
| Habitual users | Top 40% and active in at least 9 of 12 weeks |
| Novice users | Top 80% |
| Low users | Below the top 80% |
| Inactive | No prompts in the rolling window |
| Insufficient sample | Fewer than 20 prompt-active users for percentile calculation |

### Read it in this order

1. Read the ladder distribution and rolling prompt-volume tiers together.
2. Use multi-skill share, elapsed duration, steps per task, skills per task, and
   skills per user to explain the distributions.
3. Read the lifetime scheduling disclosure before interpreting Automating.
4. Use Audit Coverage only in an un-narrowed date context with an independent
   usage export.

### Diagnostic questions

- Is maturity rising because more users are delegating, or because a few users
  are doing deeper work?
- Are usage frequency and delegation depth moving together?
- Is Automating populated from a current and matched usage export?
- Do sampled source threads support the interpretation of complex or repeatable
  work?

### Action

Target enablement by rung: onboarding for Trying, workflow expansion for Using,
peer sharing for Delegating, and governance review for Automating.

### Guardrail

Task duration is elapsed time between the first and last observed event in a
thread, not measured human attention. Scheduled totals do not respond to the
date filter.

## Page 6: Cowork Champions

### Purpose

Identify potential enablement partners and category or department coverage gaps.

### Eligibility and scoring

1. A user must have at least **3 observed task threads across 2 active weeks** in
   the current date, category, and organization context.
2. Eligible users receive a 0-100 evidence score:
   - 40% category task-activity percentile
   - 35% active-week consistency percentile
   - 25% normalized delegation rung
3. The selected Top 5%, Top 10%, or Top 20% tier is applied to the eligible
   population. Top 10% is the default.
4. At least one candidate is returned when an eligible population exists; the
   cutoff is rounded up and deterministic tie-breaking is applied.

### Read it in this order

1. Confirm the selected category and tier.
2. Check eligible-user count and cohort size.
3. Review candidate score, tasks, active weeks, maturity stage, and last
   activity together.
4. Check department coverage to find eligible groups without a candidate.

### Diagnostic questions

- Is the candidate list stable under a reasonable date range?
- Are results concentrated in one category or department?
- Does the cohort contain fewer than ten eligible users?
- Is organization enrichment available for the coverage view?

### Action

Validate role fit, willingness, manager support, and appropriate data use.
Invite willing candidates to share repeatable workflows; do not automatically
publish or contact a ranked list.

### Guardrail

This is comparative engagement evidence for enablement planning. It does not
measure expertise, influence, aptitude, performance, or promotion readiness.

## Page 7: Activity & Assisted Hours

### Purpose

Connect observed Cowork activity with transparent, assumption-based assisted
time.

### Read it in this order

1. Read active users, observed activity records, and tasks by category.
2. Confirm the selected Low, Mid, or High estimate basis.
3. Read assisted hours as a scenario:

   `Assisted hours = sum(category task count x category minutes for selected basis) / 60`

4. Treat category-level values as allocated estimates.
5. Open source citations and category assumptions before presenting the result.

### Diagnostic questions

- Which categories contribute most because of task volume, assumed minutes, or
  both?
- How wide is the Low-to-High range?
- Are dominant categories based on mapped skills?
- Would the decision change under the Low basis?

### Action

Present Low, Mid, and High as a range. Name the selected basis and distinguish
observed activity from modeled assisted time.

### Guardrail

Assisted hours are not direct per-skill metering, a time study, realized
savings, employee capacity, or financial-audit evidence. One task thread can
produce multiple observed action records.

## Page 8: What They Use It For

### Purpose

Explain what kinds of work users ask Cowork to perform and preserve the records
behind the category totals.

### Read it in this order

1. Review observed skills and mapped work categories.
2. Use the bookmarks to switch between outcome/action and user detail without
   clearing the current filters.
3. Review unmapped skills before interpreting category shares.
4. Inspect source records for the dominant categories.
5. Use the discussion prompts as facilitation aids, not measured findings.

### Category value tiers

Value tiers are references based on the category's declared Mid assumption:

| Tier | Mid-band category minutes |
| --- | --- |
| High | 30 minutes or more |
| Mid | 10-29 minutes |
| Low | Less than 10 minutes |

### Diagnostic questions

- Is activity concentrated in one category, skill, or small user group?
- Are unmapped skills large enough to alter the conclusion?
- Does the observed detail match the plain-language category definition?
- Which repeatable workflow is ready for enablement or governance review?

### Action

Select a high-volume, well-mapped category; validate examples with the business
owner; document a repeatable scenario; and test whether it broadens reach,
return, or maturity.

### Guardrail

Action-value tiers are declared category references. They are not measured
business value, user ratings, or evidence that a particular task saved the
declared number of minutes.

## Page 9: Momentum Score Guide

### Purpose

Explain the live 0-100 adoption momentum signal and its optional tuning controls.

### Default formula

The latest active week is scored as:

`100 x (0.35 x return + 0.25 x consistency + 0.25 x intensity + 0.15 x maturity)`

Where:

| Component | Normalization |
| --- | --- |
| Return | Weekly return rate, bounded from 0 to 1 |
| Consistency | Average active days per user divided by the active-day cap; default cap 3 |
| Intensity | Prompts per active user divided by the prompt cap; default cap 12 |
| Maturity | Share of active users on Delegating or Automating |

All components are bounded from 0 to 1. The score is rounded to a whole number.
The default weights are 35%, 25%, 25%, and 15%.

### Diagnostic questions

- Which component is limiting the score?
- Did the component change because of the numerator, denominator, or population?
- Have weights or caps changed since the comparison period?
- Do the four weights total 100%?

### Action

Keep default settings until a documented program rationale exists. If settings
change, record the owner, date, reason, old values, and new values. Recalculate
the baseline before comparing trends.

### Guardrail

The score is blank when weights do not total 100%. Scores produced under
different settings or in different tenants are not directly comparable.

## Page 10: Adoption Metric Guide

### Purpose

Define every report metric, threshold, dependency, filter behavior, and
interpretation boundary.

### Read it in this order

1. Filter to the report page being discussed.
2. Find the exact metric name.
3. Read the definition and Data Status together.
4. Confirm threshold, time grain, optional dependency, and bookmark behavior.
5. Carry the definition and context into the decision record.

### Decision-record minimum

- Metric name and definition
- Reporting period and population
- Active filters
- Data Status
- Optional source status
- Convention or assumption values
- Report/template version

### Action

Use the in-report guide during reviews to resolve ambiguous language before it
enters presentations, action plans, or executive summaries.

### Guardrail

Missing optional evidence means unavailable, not zero. A correct metric can
still be unsuitable when its period, population, coverage, status, or
assumptions are unstated.

---

## Methodology: adoption momentum

The score intentionally balances four different adoption behaviors:

| Behavior | Why it is included | Common misread |
| --- | --- | --- |
| Return | Shows whether previous-week users came back | Not the share of all licensed users |
| Consistency | Rewards use across multiple days | Not time spent in Cowork |
| Intensity | Represents prompts per active user | Not task complexity or value |
| Maturity | Represents users on Delegating or Automating | Automating partly uses a lifetime optional input |

Caps prevent a small number of high values from dominating. They are
conventions, not empirical targets. A score increase is most defensible when
reach is stable or growing and at least two components improve.

## Methodology: maturity and time grain

| Metric or attribute | Responds to date filter? | Source |
| --- | --- | --- |
| Task threads, prompts, multi-skill share, elapsed duration | Yes | Purview |
| Delegation rungs Not started through Delegating | Yes | Purview |
| Automating rung and Scheduled Share | **No - lifetime user total** | Optional usage export |
| Prompt-volume tiers | Rolling 12 active weeks | Purview |
| Audit Coverage | Only in an un-narrowed date context | Purview plus independent usage export |

Never combine lifetime scheduling and period-scoped activity without stating the
mixed grain.

## Methodology: champion population

The champion score is recalculated inside the selected date, category, and
organization context. Narrow filters change the eligible population,
percentiles, score, and cutoff.

Use this review sequence:

1. Check the evidence floor.
2. Check eligible cohort size.
3. Check the category and date range.
4. Review all score components.
5. Confirm organization coverage.
6. Perform a human validation step before outreach.

When fewer than ten users are eligible, review all qualifying users instead of
treating the percentile ranking as stable.

## Methodology: assisted-time allocation

The model contains Low, Mid, and High minute assumptions for each work category,
with source citations. The report multiplies observed category task counts by
the selected assumption and converts minutes to hours.

This approach supports scenario comparison. It does not establish causal time
savings. Category detail inherits both mapping uncertainty and assumption
uncertainty; therefore, lower-grain results are described as allocated
estimates.

## Data pipeline and refresh contract

### Required Purview evidence

- Outer columns: `RecordId`, `CreationDate`, `Operation`, `UserId`, `AuditData`
- `Operation = CopilotInteraction`
- `AuditData.CopilotEventData.AppHost` contains `cowork`, case-insensitively
- Non-overlapping exports for large periods
- Duplicate `RecordId` values are removed by the model

### Optional inputs

| Input | Preferred filename | Critical join or grain |
| --- | --- | --- |
| Cowork usage | `CoworkUserDetails.csv` or `Cowork Usage.csv` | Lowercase UPN; user-level aggregate |
| Organization | `CoworkUserOrgDetails.csv` or `Cowork User Organization.csv` | Lowercase UPN; user attributes |
| Identity | Exact filename `cowork_users.csv` | Audit identity to friendly name |
| Consumption | Supported consumption export | Supporting fields only; not required for core adoption |

The model searches recursively under the configured folder. Keep only one
current schema-valid optional file of each type; when several files match, the
model does not select by newest modified date.

### Validation sequence

1. Confirm Purview users, threads, skills, categories, and dates.
2. Confirm the displayed period matches the intended export period.
3. Reconcile usage totals only in a compatible, un-narrowed date context.
4. Check identity and organization match coverage.
5. Check skill mapping coverage and unmapped records.
6. Confirm champion counts change predictably with tier and category.
7. Confirm the Momentum Weight Status says weights total 100%.
8. Confirm no page or visual displays an error.

## Recommended decision language

| Scenario | Defensible wording |
| --- | --- |
| Adoption is broadening | "Weekly active users increased in the selected period while return rate remained stable or improved." |
| Return is weakening | "A smaller share of previous-week users returned in the latest active week; export coverage and rollout context should be checked." |
| Use is concentrated | "Observed activity is concentrated among the displayed users or groups; role and rollout context should be checked." |
| Maturity is increasing | "The report calculates a larger share of users on higher delegation rungs under the documented thresholds." |
| Champion outreach | "These users meet the report's engagement evidence floor and selected percentile tier; role fit and willingness still require confirmation." |
| Assisted-time scenario | "Under the selected category assumptions, the report models the displayed assisted-hour range." |
| Optional data missing | "This breakdown cannot be calculated from the current connected inputs." |

Avoid wording that claims Cowork caused productivity gains, proves automation,
measures employee performance, replaces billing or compliance records, or
establishes a cross-tenant benchmark.

## Presenter checklist

Before a review:

- Confirm template version, refresh time, reporting period, and filters.
- Confirm source status and any missing optional inputs.
- Confirm momentum settings and assisted-time basis.
- Prepare one corroborating visual for each headline.
- Remove or protect user-level identifiers as required.

During a review:

- State the evidence label before the conclusion.
- Separate observed, derived, and modeled statements.
- Explain denominators and mixed time grains.
- Treat champion output as an enablement starting point.

After a review:

- Record metric definitions, filters, statuses, assumptions, and owners.
- Assign validation owners before enablement or governance action.
- Apply organizational privacy, labor, works-council, security, retention, and
  sensitivity-label requirements.

## Usage and compliance disclaimer

Coverage depends on licensing, audit settings, retention, product behavior,
permissions, export completeness, optional source availability, identity
matching, and template version. Validate the report against approved source
records before production decisions.
