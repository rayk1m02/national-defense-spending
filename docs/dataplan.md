# Data Plan

Questions the project answers, grouped by theme. Each lists the suggested visual and the tables it uses. Phase 1 questions are answered from four summary tables in `marts_nds`:

| Summary table        | Grain                                                                                                 | Answers                                                                                                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `rpt_spend_monthly`  | fiscal year, month, awarding agency, PSC group, competition, new vs modification, domestic vs foreign | spend trends, agency share, competition, domestic vs foreign, product mix, seasonality, new vs modifications, inflation-adjusted trends |
| `rpt_recipient_year` | recipient parent, fiscal year                                                                         | top 10 share, consolidation, top 10 award size and contract types, small business                                                       |
| `rpt_state_year`     | fiscal year, place-of-performance state, recipient state                                              | geographic questions                                                                                                                    |
| `rpt_award`          | award (contract or IDV)                                                                               | IDV utilization, contract profiling, duration vs value, outliers                                                                        |

## Phase 1

### Spend trends over time

- What's the year-over-year obligated total for 050, split by 051/053/054, FY2017 to present? *Trend line.*
  - Tables: fct_transaction, dim_date, dim_agency
- Are there detectable step-changes in the obligated total for 050 or any of its subfunctions, and if so, in which years, and what events might explain them? *Trend line with change-point annotations.*
  - Tables: fct_transaction, dim_date, dim_agency

### Agency/subagency concentration

- What share of total obligations does each service (Army, Navy, Air Force including Space Force, Defense-Wide, DOE defense offices) hold by fiscal year, and which are growing the most? *100% stacked area over time.*
  - DOE has no sub-agency level, so it's split by `awarding_office_code` (NNSA, Environmental Management, Hanford, Office of River Protection).
  - Space Force awards appear under the Department of the Air Force and stay combined with it (Space Force only exists from December 2019).
  - Tables: fct_transaction, dim_date, dim_agency, `awarding_office_code` (staging) for DOE

### Contractor market concentration

- What share of obligated dollars do the top 10 recipients capture each fiscal year, and is that share growing or shrinking? *Ranked top-10 table plus a CR10 (top-10 concentration ratio) trend line.*
  - Recipients are counted at the parent level: the parent UEI from the dim_recipient version in effect at each transaction, or the recipient's own UEI when there's no parent.
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
  - Obligations are summed over each IDV's child orders by `parent_award_id_piid` against the IDV's ceiling, for IDVs whose period of performance has ended (open vehicles would drag the average down).
  - Tables: fct_transaction, dim_date, dim_award
- (Profiling step) Compute statistical descriptions of all contracts (average duration, amount, min/max, etc.).
  - Tables: fct_transaction, dim_date
- Is there a correlation between a contract's duration (period of performance length) and its total obligated value? Do longer contracts tend to be worth more, or is duration independent of size? *Scatter plot with trend line.*
  - Tables: fct_transaction, dim_date
- Do top 10 recipients (by parent, as above) get larger average award sizes than the rest of the market, and do they see a different mix of contract types (fixed-price vs cost-reimbursement) that could reflect more favorable terms? *Comparison bar chart or table.*
  - Tables: fct_transaction, dim_date, dim_recipient, dim_award

### Small business / set-asides

- What share of obligated dollars goes to small business, 8(a) (program for socially/economically disadvantaged owners, who get sole-source and set-aside eligibility for up to 9 years), SDVOSB (service-disabled veteran owned), WOSB (women owned), and HUBZone (businesses based in economically distressed areas) recipients by year, and how does that track against statutory goals (small business contracting targets Congress sets by law)? *Per-category trend lines with goal reference lines.*
  - Small business uses the contracting officer's size determination (dim_competition).
  - The other categories use each transaction's own flag from staging, not dim_recipient's latest value, since firms enter and leave these programs (2,873 recipients have a changing 8(a) flag).
  - Goals are government-wide, shown as reference lines. 8(a) has no goal of its own; it counts toward the small disadvantaged business goal.
  - Tables: fct_transaction, dim_date, dim_competition, business flags from stg_contract_transactions, goals seed

### Fiscal year-end seasonality

- What fraction of each fiscal year's total lands in August/September versus an even monthly baseline, and is that spike more pronounced within specific subfunctions in 050? (The "use it or lose it" pattern.) *Monthly distribution by year, plus a comparison ratio.*
  - Tables: fct_transaction, dim_date, dim_agency
- Is there a difference in product category spend as the fiscal year's end gets closer?
  - Tables: fct_transaction, dim_date, dim_product

### New awards vs recompetes

- What share of each year's total comes from genuinely new contract actions versus renewals or modifications of existing work? *Stacked bar.*
  - Tables: fct_transaction, dim_date

### Inflation-adjusted trends

- How do the spend trend lines change once adjusted by CPI (Consumer Price Index)? Replot them in real terms to see whether spending actually grew or only grew because prices did. *Same trend line, nominal vs real as dual series.*
  - Tables: fct_transaction, dim_date, dim_agency

### Outlier / anomaly detection

- Which individual awards are statistical outliers relative to their agency's or contractor's typical award size (same z-score/IQR method as the EIA project, new dataset)? *Ranked list of flagged awards, maybe a scatter with baseline band.*
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

### Fiscal year-end seasonality

- Does the year-end spike disproportionately favor contract types that are quick to execute (fixed-price) over more complex ones (e.g. cost-reimbursement)? *Stacked comparison, ties back to the competition analysis category.*
  - Tables: fct_transaction, dim_date, dim_award

### New awards vs recompetes

- Has the average size of new awards changed relative to the average size of modifications? Are agencies leaning more on modifying existing contracts instead of issuing new ones? *Dual trend line.*
  - Tables: fct_transaction, dim_date, dim_agency

### Outlier / anomaly detection

- Are outlier awards concentrated in particular NAICS/PSC categories or agencies, or spread evenly? *Heatmap.*
  - Tables: fct_transaction, dim_date, dim_product, dim_agency
- Do outliers cluster around fiscal year-end, tying into the seasonality theme? *Time distribution.*
  - Tables: fct_transaction, dim_date
