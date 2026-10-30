# Data Plan

Questions the project answers, grouped by theme. Each lists the suggested visual and the tables it uses. Phase 1 questions are answered from summary tables in `marts_nds`:

| Summary table        | Grain                                                                                                                 | Answers                                                                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `rpt_spend_monthly`  | fiscal month, awarding agency, service group, product group, competition bucket, action category, domestic vs foreign | spend trends, service share, competition, domestic vs foreign, product mix, seasonality, new vs modifications, inflation-adjusted        |
| `rpt_recipient_year` | recipient UEI, fiscal year (with corrected recipient group and group ranks)                                           | top 10 share, consolidation, top 10 award size and contract types, small business                                                        |
| `rpt_state_year`     | fiscal year, place of performance state, recipient state                                                              | geographic questions                                                                                                                     |
| `rpt_idv`            | single-award IDIQ                                                                                                     | IDV utilization                                                                                                                          |
| `rpt_award_profile`  | start year, award type, service group, size bucket, length bucket                                                     | contract profiling, duration vs value                                                                                                    |
| `rpt_award_stats`    | start year, award type                                                                                                | medians, size vs length correlation                                                                                                      |
| `rpt_award_outliers` | flagged award                                                                                                         | outlier detection                                                                                                                        |

Inflation-adjusted trends use BLS CPI-U annual averages applied to fiscal year totals, outside dbt. The small business goals comparison is in Phase 2 (it needs a goals seed).

## Phase 1

### Spend trends over time

- What's the year-over-year obligated total for 050, split by 051/053/054, FY2017 to present? *Trend line.*
  - Tables: fct_transaction, dim_date, dim_agency
- Are there detectable step-changes in the obligated total for 050 or any of its subfunctions, and if so, in which years, and what events might explain them? *Trend line with change-point annotations.*
  - Tables: fct_transaction, dim_date, dim_agency

### Agency/subagency concentration

- What share of total obligations does each service (Army, Navy, Air Force including Space Force, Defense-Wide, DOE defense offices) hold by fiscal year, and which are growing the most? *100% stacked area over time.*
  - DOE has no sub-agency level, so it's split by `awarding_office_code` into NNSA and Environmental Management (EM includes its Hanford and Office of River Protection field offices).
  - Space Force awards appear under the Department of the Air Force and stay combined with it (Space Force only exists from December 2019).
  - Tables: fct_transaction, dim_date, dim_agency, `awarding_office_code` (staging) for DOE

### Contractor market concentration

- What share of obligated dollars do the top 10 recipients capture each fiscal year, and is that share growing or shrinking? *Ranked top-10 table plus a CR10 (top-10 concentration ratio) trend line.*
  - Recipients are counted at the parent level: the parent UEI from the dim_recipient version in effect at each transaction, or the recipient's own UEI when there's no parent.
  - Corporate families that USASpending splits or misnames are corrected by a seed for the largest companies (reporting errors and renames only, never acquisitions inside the window).
  - Tables: fct_transaction, dim_date, dim_recipient

### Contractor consolidation (SCD2)

- Of the top 20 cumulative recipients, which show a UEI or parent UEI change (proxy for a merger or acquisition restructuring) in the window, and what does their combined obligation trend look like before and after? *Entity-level trend lines, before/after comparison.*
  - Tables: fct_transaction, dim_date, dim_recipient

### Competition analysis

- What's the full-and-open (open to any qualified vendor) vs sole-source (awarded without competition) vs limited-competition (bid from a restricted pool) split of obligated dollars by fiscal year, and is sole-source share growing? *Stacked trend line.*
  - Tables: fct_transaction, dim_date, dim_competition
- Domestic vs foreign entity contract share.
  - Tables: fct_transaction, dim_date, dim_recipient

### NAICS/PSC mix

- How has the obligated split across R&D, supplies/equipment, services, and construction shifted year over year? *Stacked area trend.*
  - Tables: fct_transaction, dim_date, dim_product

### Geographic distribution

- What's the state-level share of place-of-performance dollars by fiscal year, and has the top-5-states share grown or shrunk? (Where the contract work actually happens: which states get the most defense dollars, and is there a concentration shift.) *Ranked list/map plus a concentration ratio trend.*
  - Tables: fct_transaction, dim_date, dim_location
- Which states gained or lost the most share over the window? *Ranked list of deltas.*
  - Tables: fct_transaction, dim_date, dim_location
- Which states are the winning contractors based in (the recipient's registered state at the time of each transaction), and how does that differ from where the work is performed? (e.g. how much of the money awarded to Virginia- and Maryland-based firms is performed in other states) *Ranked list by recipient state, plus a recipient-state vs place-of-performance comparison.*
  - Tables: fct_transaction, dim_date, dim_recipient, dim_location

### Contract lifecycle / lead time

- For IDVs, what fraction of ceiling value gets obligated before the vehicle's period of performance ends (i.e. average utilization rate across IDVs)? *Distribution or histogram.*
  - Orders are linked to their IDV through the parent PIID and agency in the order's award key, and summed against the IDV's ceiling.
  - Single-award IDIQs only: multiple-award ceilings are shared across awardees and BPA ceilings are nominal.
  - IDV records carry no end date, so utilization is shown by base award year cohort; older cohorts are mostly finished.
  - Covers IDVs awarded by the four in-scope agencies and the orders they placed.
  - Tables: fct_transaction, dim_date, dim_award
- (Profiling step) Compute statistical descriptions of all contracts (average duration, amount, min/max, etc.).
  - Awards only (IDVs carry no money), counted by size and length bucket; medians and correlation are precomputed per start year and award type.
  - Tables: fct_transaction, dim_date
- Is there a correlation between a contract's duration (period of performance length) and its total obligated value? Do longer contracts tend to be worth more, or is duration independent of size? *Scatter plot with trend line.*
  - Tables: fct_transaction, dim_date
- Do top 10 recipients (by parent, as above) get larger average award sizes than the rest of the market, and do they see a different mix of contract types (fixed-price vs cost-reimbursement) that could reflect more favorable terms? *Comparison bar chart or table.*
  - Average award size uses awards started per recipient-year and their lifetime obligations.
  - Tables: fct_transaction, dim_date, dim_recipient, dim_award

### Small business / set-asides

- What share of obligated dollars goes to small business, 8(a) (program for socially/economically disadvantaged owners, who get sole-source and set-aside eligibility for up to 9 years), veteran-owned (stands in for SDVOSB, which isn't in the kept columns), WOSB (women owned), and HUBZone (businesses based in economically distressed areas) recipients by year? *Per-category trend lines.*
  - Small business uses the contracting officer's size determination (dim_competition).
  - The other categories use each transaction's own flag (on fct_transaction), not dim_recipient's latest value, since firms enter and leave these programs (2,873 recipients have a changing 8(a) flag).
  - Category dollars count only on contracts the contracting officer determined small, as the SBA counts them.
  - Tables: fct_transaction, dim_date, dim_competition

### Fiscal year-end seasonality

- What fraction of each fiscal year's total lands in August/September versus an even monthly baseline, and is that spike more pronounced within specific subfunctions in 050? (The "use it or lose it" pattern.) *Monthly distribution by year, plus a comparison ratio.*
  - Tables: fct_transaction, dim_date, dim_agency
- Is there a difference in product category spend as the fiscal year's end gets closer?
  - Tables: fct_transaction, dim_date, dim_product

### New awards vs recompetes

- What share of each year's total comes from genuinely new contract actions versus renewals or modifications of existing work? *Stacked bar.*
  - Tables: fct_transaction, dim_date

### Inflation-adjusted trends

- How do the spend trend lines change once adjusted by CPI (Consumer Price Index)? Restate them in real terms to see whether spending actually grew or only grew because prices did. *Nominal vs real growth table in the README.*
  - Fiscal year totals deflated with BLS CPI-U annual averages. CPI tracks consumer prices, so it's a proxy for defense purchase prices.
  - Tables: fct_transaction, dim_date, dim_agency

### Outlier / anomaly detection

- Which individual awards are statistical outliers relative to their agency's or contractor's typical award size (same z-score/IQR method as the EIA project, new dataset)? *Ranked list of flagged awards, maybe a scatter with baseline band.*
  - IQR on log award size, flagged above Q3 + 3 IQR within sub-agency, award type, and product group (groups of 30+).
  - Baselines use awards of $10K or more, so token orders don't set the typical size; the IQR is floored at a doubling.
  - Tables: fct_transaction, dim_date, dim_award, dim_agency, dim_recipient, dim_product

## Phase 2

### Agency/subagency concentration

- Within Defense-Wide, how does the DLA (Defense Logistics Agency) / DISA (Defense Information Systems Agency) / other split look, and has that mix shifted? *Ranked breakdown per year.*
  - Tables: fct_transaction, dim_date, dim_agency

### Contractor market concentration

- How has an HHI (Herfindahl-Hirschman Index) computed across all 051 recipients moved over the data window? *Single ratio, trend line.*
  - Tables: fct_transaction, dim_date, dim_recipient

### Contractor consolidation (SCD2)

- Is there a visible step-change in combined award volume in the 12 months following an identified merger date? *Before/after comparison, small multiples per contractor.*
  - Tables: fct_transaction, dim_date, dim_recipient

### Competition analysis

- Is sole-source share structurally higher for R&D-heavy PSC categories than for routine procurement, and has that gap changed? *Two trend lines or a grouped comparison.*
  - Tables: fct_transaction, dim_date, dim_competition, dim_product

### NAICS/PSC mix

- Does 053 spend show a structurally different PSC mix than 051? *Side-by-side ranked comparison for a snapshot year, or two stacked-area trends.*
  - Tables: fct_transaction, dim_date, dim_product, dim_agency

### Contract lifecycle / lead time

- How close to expiration do recompetes typically land, gap or overlap? *Distribution of days-to-recompete.*
  - Tables: fct_transaction, dim_date
- How long does it typically take from award to the start of the period of performance (the closest lead-time proxy available, since USASpending has no solicitation-to-award timestamp), and does that lag scale with award size or vary by agency? *Distribution, plus a scatter against award value.*
  - Tables: fct_transaction, dim_date, dim_agency

### Small business / set-asides

- What share of small-business set-aside dollars goes to R&D-heavy PSC categories vs routine hardware/services?
  - Tables: fct_transaction, dim_date, dim_competition, dim_product
- Does the recipient-type mix differ between subfunction 051 (DoD) and 053 (DOE nuclear), or across Army vs Navy vs Air Force?
  - Tables: fct_transaction, dim_date, dim_recipient, dim_agency
- How do the small business category shares track against statutory goals (small business contracting targets Congress sets by law)? Goals are government-wide, shown as reference lines (none for veteran-owned, since the goal is for service-disabled firms); 8(a) has no goal of its own (it counts toward the small disadvantaged business goal). *Per-category trend lines with goal reference lines.*
  - Tables: fct_transaction, dim_date, dim_competition, goals seed

### Fiscal year-end seasonality

- Does the year-end spike disproportionately favor contract types that are quick to execute (fixed-price) over more complex ones (e.g. cost-reimbursement)? *Stacked comparison, ties back to the competition analysis category.*
  - Tables: fct_transaction, dim_date, dim_award

### New awards vs recompetes

- Has the average size of new awards changed relative to the average size of modifications? Are agencies leaning more on modifying existing contracts instead of issuing new ones? *Dual trend line.*
  - Tables: fct_transaction, dim_date, dim_agency

### Inflation-adjusted trends

- Chart the spend trend lines in real terms with a CPI seed, nominal vs real as dual series (Phase 1 answers this in the README only).
  - Tables: fct_transaction, dim_date, dim_agency, CPI seed

### Outlier / anomaly detection

- Are outlier awards concentrated in particular NAICS/PSC categories or agencies, or spread evenly? *Heatmap.*
  - Tables: fct_transaction, dim_date, dim_product, dim_agency
- Do outliers cluster around fiscal year-end, tying into the seasonality theme? *Time distribution.*
  - Tables: fct_transaction, dim_date