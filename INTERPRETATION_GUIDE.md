# Cowork Adoption Intelligence: interpretation guide

Use this guide to turn the eight-page report into defensible adoption and
enablement decisions. It separates observed evidence, optional enrichment,
modeled scenarios, and customer-controlled assumptions.

## Evidence chain

| Layer | Examples | Interpretation |
| --- | --- | --- |
| Observed Cowork evidence | Paired PAX Purview interactions: events, threads, skills, resources, and timestamps | What the approved audit source recorded |
| User and organization context | Paired PAX Entra users, organization, and licensing records | Segmentation and population context for authorized users |
| Derived metrics | Active weeks, repeat activity, maturity, task classifications | Reproducible calculations from the paired files |
| Modeled scenarios | Assisted time and labor value | Observed activity combined with editable category-minute assumptions |

Do not describe a modeled scenario as observed savings, realized ROI, future
demand, or guaranteed capacity.

## Five safeguards

1. Confirm the reporting window and source coverage.
2. Distinguish missing data from zero activity.
3. Keep organization filters visible when comparing cohorts.
4. Treat small cohorts and narrow periods as directional.
5. Record the Capacity Assumptions values used for every exported result.

## Page 1: Cowork Adoption Scorecard

![Cowork Adoption Scorecard](images/report-pages/01-cowork-adoption-scorecard.png)

**Purpose:** Provide a decision-ready starting point and route the reader to the
right evidence page. Start Here guidance is integrated into this page.

**Read in this order:**

1. Confirm date and organization filters.
2. Read the adoption and usage headline indicators.
3. Review the context or evidence statements beside the scorecard.
4. Use the navigation prompts to move to trend, segmentation, work-pattern,
   maturity, enablement, scenario, assumption, or metric evidence.

**Action:** Choose one question to investigate and preserve the filter context
when moving to the supporting page.

**Guardrail:** A scorecard is a summary, not a diagnosis. Do not present a
headline without its period, population, and source-coverage context.

## Page 2: Weekly Adoption & Usage

![Weekly Adoption & Usage](images/report-pages/02-weekly-adoption-and-usage.png)

**Purpose:** Show whether adoption is expanding and whether users return over
time.

**Read in this order:**

1. Confirm the weekly window and cohort.
2. Compare active-user breadth with task or prompt activity.
3. Look for sustained movement across several weeks rather than one spike.
4. Check whether activity concentration is changing.

**Action:** Investigate material changes by department, role, location, or work
pattern before selecting an intervention.

**Guardrail:** A partial final week, a changed export window, retention limits,
or collection gaps can look like a decline. Repeat activity is not equivalent to
business value or quality.

## Page 3: Scalable Work Patterns

![Scalable Work Patterns](images/report-pages/03-scalable-work-patterns.png)

**Purpose:** Identify observed task patterns that repeat across users or periods
and understand where assisted capacity is concentrated.

**Read in this order:**

1. Compare category and task activity.
2. Look for patterns repeated by more than one user and across more than one
   period.
3. Review the underlying volume and user breadth.
4. Compare modeled assisted time only after validating its assumptions.

**Action:** Select repeatable, policy-compliant patterns for playbooks,
demonstrations, training, or further qualitative validation.

**Guardrail:** Classification is an analytical grouping. A frequent pattern is
not automatically suitable for automation, and modeled time is not measured
human attention or realized savings.

## Page 4: Demand & Capacity Scenario

![Demand & Capacity Scenario](images/report-pages/04-demand-and-capacity-scenario.png)

**Purpose:** Compare observed Cowork task demand with modeled assisted-work hours
and labor value under editable category-minute assumptions.

**Read in this order:**

1. Confirm the observed period and included population.
2. Review demand volume and distribution.
3. Confirm the active assumption set.
4. Compare observed task share with modeled assisted-hours share.
5. Test a bounded alternative rather than replacing the baseline immediately.

**Action:** Use scenarios to identify questions for staffing, enablement,
prioritization, and workload review.

**Guardrail:** This page does not predict future demand. It does not prove cost
savings, employee capacity, service levels, or financial return.

## Page 5: Adoption Maturity

![Adoption Maturity](images/report-pages/05-adoption-maturity.png)

**Purpose:** Show progression from initial activity toward sustained delegation
and automation evidence.

**Read in this order:**

1. Review the maturity distribution for the selected cohort.
2. Compare user breadth and evidence volume at each stage.
3. Check active weeks and task diversity before interpreting progression.
4. Look for cohorts moving over several periods.

**Action:** Match enablement to the evidence: onboarding for first use, repeatable
work examples for returning users, and governance for advanced patterns.

**Guardrail:** Maturity is an adoption construct, not a judgment of competence,
productivity, seniority, or job performance. Stage labels depend on the available
audit window.

## Page 6: Category Users

![Category Users](images/report-pages/06-category-users.png)

**Purpose:** Show the users and departments with observed activity in a selected
work category and support authorized enablement outreach.

**Read in this order:**

1. Select the work category and population.
2. Review eligibility and evidence breadth.
3. Compare consistency, activity, and maturity evidence.
4. Check department coverage before selecting outreach candidates.
5. Review a person's evidence only when authorized.

**Action:** Confirm role relevance, willingness, manager support, and training
needs through human review.

**Guardrail:** Results are not employee ratings and must not be used for
promotion, compensation, discipline, surveillance, or automated employment
decisions.

## Page 7: Capacity Assumptions

![Capacity Assumptions](images/report-pages/07-capacity-assumptions.png)

**Purpose:** Make the customer-controlled inputs behind demand, capacity, and
assisted-time scenarios visible and editable.

**Read in this order:**

1. Review every active task-level assumption.
2. Confirm units and whether the value is per task, user, week, or other grain.
3. Identify the source and owner for each changed value.
4. Test the effect on the scenario pages.
5. Record the final assumption set with the reporting output.

**Action:** Replace defaults only with customer-approved evidence, preserve the
baseline, and document the rationale.

**Guardrail:** Defaults are starting assumptions, not Microsoft commitments,
benchmarks, or measured customer outcomes. Category-wide substitutions should
not replace the individual task controls.

## Page 8: Adoption Metric Guide

![Adoption Metric Guide](images/report-pages/08-adoption-metric-guide.png)

**Purpose:** Provide definitions, calculation boundaries, sources, and safe
interpretation language.

**Read in this order:**

1. Find the metric used in the decision.
2. Confirm numerator, denominator, grain, and filter behavior.
3. Identify whether it is observed, optional, derived, or modeled.
4. Read the limitation and recommended wording.

**Action:** Cite the metric definition and active filters in exported slides,
emails, and decision records.

**Guardrail:** If the metric guide is empty after opening the PBIP source, apply
pending model changes or refresh before distributing the report.

## Core interpretation rules

### Active users and adoption

An active user is supported by qualifying Cowork evidence in the selected
period. It is not the same as a licensed, assigned, enabled, or trained user.
Adoption rates require a documented eligible-population denominator.

### Tasks, prompts, and threads

Prompts, interactions, and task threads have different grains. Do not compare
their totals without the metric definition. Thread duration is elapsed time
between observed events, not continuous human effort.

### Usage reconciliation

The paired PAX files can contain different entity grains. Reconcile the common
reporting window and user keys before interpreting a mismatch as activity.

### Classification

Task, category, skill, plugin, and resource classifications are reproducible
analytical groupings based on the paired-file contract. Review uncategorized or
low-confidence records before drawing category conclusions.

### Assisted time and capacity

Modeled assisted time combines observed task activity with task-specific
assumptions. Capacity scenarios use those outputs with additional adjustable
inputs. Report them as modeled estimates or scenarios and disclose the active
assumption set.

### Category users and enablement outreach

Engagement evidence can identify people to ask about examples, training, or
peer-learning needs. It cannot establish quality, expertise, willingness, or
performance. Human review is mandatory.

## Data quality review

Before presenting results, confirm:

- both paired PAX files are from the same successful run
- the source files record the intended reporting period
- required `_Entity` records and user keys are present
- no collection gap overlaps the analysis window
- user and organization joins resolve as expected
- final-week or final-month periods are complete
- cohort sizes are sufficient and privacy-safe
- Capacity Assumptions values and owners are recorded
- Adoption Metric Guide is populated
- the refreshed report has the sensitivity label required by policy

## Recommended decision language

Prefer:

- "Observed Cowork activity increased across the selected period."
- "This cohort has lower repeat activity and may benefit from targeted
  enablement."
- "These users show category-level engagement evidence and may be appropriate to
  contact for peer-learning validation."
- "Under the recorded assumptions, the scenario indicates available capacity."

Avoid:

- "Cowork caused productivity to increase."
- "These employees are the top performers."
- "The organization saved this many hours."
- "Demand will reach this level."
- "The scenario proves ROI."

## Minimum decision record

Record:

- report and processor version
- source owner and extraction timestamps
- analysis period and filters
- metric definitions used
- missing or optional sources
- assumption values and owners
- known collection or join gaps
- sensitivity label and audience
- decision, reviewer, and review date

## Usage and compliance disclaimer

This template is technical and analytical guidance, not legal, compliance, HR,
financial, or records-management advice. Customers are responsible for lawful
collection, access control, retention, employee consultation, metric approval,
labeling, and use of Microsoft 365 and Power BI data.
