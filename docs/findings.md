# Findings

Answers to the Phase 1 questions in [dataplan.md](dataplan.md), in the same order. Data is through USASpending's October 2026 publish. FY2026 is incomplete because DoD reports contract data with a 90-day lag, so trends stop at FY2025 unless noted. FY2027 (6 rows, $0) is excluded.

Each answer names its source: a dashboard page (screenshots in [images/](images/)) or a query in `transform/analyses/`.

## Spend trends over time

**Year-over-year total for 050, split by subfunction**

- Obligations grew from $339.7B (FY2017) to $525.9B (FY2025), +55%.
- 051 DoD is about 95% of the total every year: $321.4B to $491.8B.
- 053 DOE Defense roughly doubled, $17.5B to $33.2B ($36.8B in FY2026, which is close to final since DOE has no reporting lag).
- 054 DHS CISA and DOT MARAD is under 0.3% of the total: $0.5B to $1.4B a year.
- Source: Overview page, `step_changes.sql`

**Step-changes**

- 050 grew 6.6% to 11.6% in most years. Two drops: FY2021 (-7.5%, after FY2020's +10.0%) and FY2024 (-1.9%).
- The FY2021 drop follows a year that included pandemic spending (CARES Act) and coincides with a continuing resolution through late December 2020. The FY2024 drop coincides with the defense appropriation being enacted in late March 2024, almost six months into the fiscal year.
- FY2018's +11.6% coincides with the [Bipartisan Budget Act of 2018](https://www.csis.org/analysis/making-sense-bipartisan-budget-act-2018-and-what-it-means-defense) (February 2018), which raised the defense caps for FY2018 and FY2019.
- 053 rose every year (3.5% to 15.1%), with no step-change.
- 054 jumped in FY2022 (+30%) and FY2023 (+66%), driven by MARAD.
- The data has no appropriation dates, so these are coincidences in timing, not tested causes.
- Source: `step_changes.sql`

## Agency/subagency concentration

**Share by service, and which are growing the most**

- Navy is the largest service at about 28% to 34% of each year's obligations. NNSA is about 79% of DOE's defense contract dollars.
- Growth FY2017 to FY2025: DOT MARAD +138%, DOE NNSA +100%, Navy +62%, Air Force +60%, DOE EM +56%, Defense-Wide +51%, Army +37%, DHS CISA -70%.
- MARAD's growth is on a small base. NNSA is the fastest growing large group.
- CISA's drop is in contracts CISA awards itself: its office (70RNPP, renamed 70RCSA in FY2019) went from $385M in FY2017 to $152M to $171M from FY2020 on. Contracts other offices award for CISA aren't in scope, since the project scopes by awarding agency.
- Source: Services and Products page, `cisa_awarding_offices.sql`

## Contractor market concentration

**Top 10 share (CR10)**

- The top 10 parent companies take 36.85% (FY2024) to 41.98% (FY2020) of each year's dollars, with no trend. FY2026 so far: 42.41%.
- FY2025 top 10: Lockheed Martin ($74.0B), RTX, General Dynamics, Boeing, Northrop Grumman, Huntington Ingalls, Honeywell, BAE Systems, Cencora, L3Harris.
- Honeywell ranks mostly because it runs Sandia National Laboratories for NNSA. COVID-era pharma purchases (Pfizer, Moderna, Regeneron, Lilly) appear in the FY2021 and FY2022 top 25.
- USASpending splits large companies across several parent records, and the split changes over time. A seed (`recipient_group_overrides.csv`, 76 rows) merges them for every family that reached a yearly top 25. `recipient_group_gaps.sql` finds new records to add after a data refresh.
- Source: Contractors page

## Contractor consolidation (SCD2)

**Parent changes among the top 20, and the trend before and after**

- Ownership changes in the window: CSRA to General Dynamics (FY2018), Orbital ATK to Northrop Grumman (FY2018), Rockwell Collins to UTC (FY2019), L3 and Harris (FY2020), Raytheon and UTC as RTX (FY2020), Alion to Huntington Ingalls (FY2022).
- Sandia's operator moving from a Lockheed subsidiary to Honeywell (FY2018) shows up as a parent change but is a contract change, not a merger.
- Average yearly dollars after vs before each deal (deal year excluded), against the whole market over the same years:

| Family                             | Before | After  | Change | Market |
|------------------------------------|--------|--------|--------|--------|
| General Dynamics + CSRA            | $14.9B | $22.3B | +50%   | +34%   |
| HII + Alion                        | $7.6B  | $10.0B | +32%   | +25%   |
| Northrop + Orbital ATK             | $11.6B | $13.9B | +20%   | +34%   |
| UTC + Rockwell Collins + Raytheon  | $22.9B | $26.8B | +17%   | +25%   |
| L3 + Harris                        | $7.3B  | $6.6B  | -9%    | +24%   |

- Three of five families lost share after their deal. General Dynamics gained, mostly from a jump in FY2025 ($21.2B to $32.3B), years after it bought CSRA.
- This counts defense contract dollars from the four in-scope agencies only, not company revenue. Five deals is a small sample.
- Source: `merger_before_after.sql`

## Competition analysis

**Full and open vs limited vs sole source**

- Full and open 41% to 47%, limited 10% to 16%, sole source 38% to 46% of each year's dollars. No sustained growth in sole source.
- Orders under IDVs inherit the IDV's competition status, which likely understates sole source.
- Source: Spending Patterns page

**Domestic vs foreign entity share**

- U.S. companies take 88.8% to 91.8% of each year's dollars. Foreign-owned, U.S.-incorporated companies take 3.9% to 5.5%, foreign companies 2.3% to 3.0%, not reported 1.5% to 4.4% (highest in FY2017).
- No trend. Foreign defense companies mostly win through U.S. subsidiaries.
- Ownership differs from work location: in FY2025, about $25B of work was performed abroad, but foreign-based companies received about $12B.
- Source: `domestic_foreign_share.sql`, Geography page

## NAICS/PSC mix

**R&D, supplies/equipment, services, construction**

- Supplies/Equipment is about half of every year, Services 35% to 40%, R&D and Construction each under 10%.
- The mix barely changes over the decade. Services peaked in FY2024 and fell back in FY2025.
- Construction includes real property maintenance and repair (PSC Z) as well as new construction (PSC Y).
- Source: Services and Products page

## Geographic distribution

**State share and the top 5 states**

- FY2025 top places of performance: Texas $62.9B, Virginia $53.4B, California $43.1B, Connecticut $34.6B, Florida $25.5B, then foreign $24.7B and Pennsylvania $24.5B.
- The top 5 states take 37.9% (FY2024) to 43.3% (FY2020) of all place of performance dollars, with no trend. The top 5 is picked each year and the denominator includes foreign work.
- Source: Geography page

**States that gained or lost the most share** (FY2017 and FY2018 vs FY2024 and FY2025, percentage points)

| Gained       | Change | Lost        | Change |
|--------------|--------|-------------|--------|
| Connecticut  | +1.73  | California  | -1.78  |
| Pennsylvania | +0.99  | Texas       | -1.69  |
| Florida      | +0.81  | Washington  | -0.90  |
| Virginia     | +0.72  | Foreign     | -0.89  |
| Utah         | +0.56  | Missouri    | -0.69  |
| Hawaii       | +0.45  | Minnesota   | -0.55  |

- Texas and California are still the top two, but both lost share. Two-year pairs keep one large contract from setting a state's result.
- Source: `state_share_change.sql`

**Where contractors are based vs where the work happens**

- In FY2025, Virginia has about $74B by contractor base but $53B by work performed, consistent with headquarters around Washington, DC. Maryland and Ohio also skew to contractor base.
- Pennsylvania, Alabama, and foreign locations skew to work performed.
- Source: Geography page

## Contract lifecycle / lead time

**IDV utilization**

- Finished single-award IDIQs use about 55% to 62% of their ceiling. Median utilization outside DLA rises with vehicle age, from 8% (FY2026 starts) to 62% (FY2017 starts).
- DLA's are much lower at every age (17% to 31% for FY2017 to FY2019 starts, 3% to 7% from FY2020). DLA's new single-award IDIQs nearly tripled from FY2019 (4,627) to FY2020 (12,942). The data doesn't show why.
- Single-award only: multiple-award ceilings are shared across awardees and BPA ceilings are nominal. IDV records carry no end date, so utilization is shown by start year.
- Source: Awards page

**Contract profiling**

- 86% of awards started FY2017 on are under $10K but carry under 1% of dollars. 337 awards of $1B and up carry about 29%, and the 4,119 awards of $100M and up about half.
- Medians (FY2019 and FY2023 starts): delivery order about $430 to $510 and 3 days; BPA call $1.7K to $2.1K, 17 to 27 days; purchase order $2.3K to $2.6K, 96 to 120 days; definitive contract $750K to $1M, about 600 days.
- Definitive contracts are 0.4% of awards but 49% of dollars.
- Source: Awards page, `rpt_award_stats`

**Duration vs value**

- Longer awards tend to be larger. Average length rises with every size bucket, from 25 days (under $10K) to 2,880 days ($1B and up).
- Correlation of log size and log length: about 0.47 to 0.49 for definitive contracts, 0.39 to 0.54 for BPA calls, 0.39 to 0.40 for purchase orders, 0.23 to 0.26 for delivery orders. Length explains only part of size.
- Source: Awards page, `rpt_award_stats`

**Top 10 award size and contract types**

- FY2025: the top 10's average award was $146,368 vs $60,275 for everyone else (2.4 times). Cost reimbursement was 36.6% of the top 10's dollars vs 31.7% (FY2019 35.9% vs 29.2%, FY2023 35.5% vs 28.7%).
- The size gap depends on who's in the top 10. It was 16 times in FY2019 ($1,145,509 vs $70,900) and 36 times in FY2023 ($2,464,624 vs $68,542). In FY2025, Cencora (pharmaceutical distribution) started about 516,000 small orders, most of the top 10's awards, which pulls the top 10 average down.
- The contract type gap is modest and likely reflects the top 10's R&D and development work, so it doesn't show more favorable terms.
- Source: Contractors page

## Small business / set-asides

**Small business and category shares**

- Small business takes about 18% to 21% of each year's dollars, fairly steady.
- 8(a) drifts down from about 4% to about 3%, veteran-owned about 3.5%, WOSB rises from about 1.6% to 2.7%, HUBZone about 1.5%.
- Small business uses the contracting officer's size determination per contract. Category dollars count only on contracts determined small, as the SBA counts them.
- Veteran-owned stands in for service-disabled veteran-owned, which wasn't kept. The small disadvantaged business flag undercounts (below the 8(a) share it should contain), so it's left out.
- Source: Contractors page

## Fiscal year-end seasonality

**Year-end spike by subfunction**

- DoD puts about 15.5% of its annual dollars in September and DHS/DOT about 16.4%, roughly double an even month (8.3%).
- DOE is the opposite: low in September (about 5%) and high at the start of quarters (October about 17%, January about 19%, April about 16%).
- Source: Spending Patterns page

**Product mix near year-end**

- Construction is the most end-loaded group: 29.9% of its dollars in September, 3.6 times an even month. Supplies/Equipment about 15%, R&D and Services about 12%.
- Maintenance and repair (32.4% in September) spikes only slightly more than new construction (28.1%), so one-year funding is at most part of the reason. Both are low in October (3.8% and 2.3%).
- Source: Services and Products page, `construction_september_split.sql`

## New awards vs recompetes

**New awards vs existing work**

- About 38% to 45% of each year's dollars go to new awards. Brand new contracts and IDVs are 9% to 14%; the rest of the new money is new orders under existing IDVs.
- The rest funds existing awards: funding-only modifications, option exercises, and other modifications.
- Source: Spending Patterns page

## Inflation-adjusted trends

**Nominal vs real growth**

| Metric                      | FY2017  | FY2024  | FY2025  |
|-----------------------------|---------|---------|---------|
| Obligations                 | $339.7B | $475.8B | $525.9B |
| CPI-U annual average        | 245.1   | 313.7   | 322.1   |
| Nominal growth since FY2017 |         | +40%    | +55%    |
| Real growth since FY2017    |         | +9%     | +18%    |

- About two thirds of the growth since FY2017 is inflation. In FY2017 dollars, FY2025 is $400B.
- Calendar-year CPI is applied to fiscal years. The 2025 value averages BLS's two half-year indexes, since October 2025 wasn't collected during the shutdown.
- CPI tracks consumer prices, so it's a proxy for defense purchase prices.
- Source: `inflation_adjusted.sql`, CPI values in `seeds/cpi_u_annual.csv` from [BBER CPI-U annual averages](https://bber.unm.edu/data/cpi) and [FRED CUUS0000SA0](https://fred.stlouisfed.org/data/CUUS0000SA0)

## Outlier / anomaly detection

**Unusually large awards**

- About 26,700 awards are flagged, $1.13T in total, mostly delivery orders.
- The top of the list is DLA weapon system support orders (RTX, Bell Boeing, Northrop Grumman, Boeing) at 10,000 to 38,000 times DLA's typical order, plus cases outside DLA such as a $146M DARPA services contract at 424 times its group's typical award.
- Method: IQR on log award size, flagged above Q3 + 3 IQR, within sub-agency, award type, and product group (groups of 30+). Baselines use awards of $10K or more and the IQR is floored at a doubling, so token orders and near-identical award sizes don't flag ordinary awards.
- Source: Awards page

## Caveats

- Scope is contracts and IDVs awarded by DoD, DOE's defense offices, DHS CISA, and DOT MARAD. Totals don't reconcile to the national defense budget, which includes non-contract spending.
- DoD totals include Corps of Engineers civil works funding: $0.08B to $8.1B a year, under 2% of DoD obligations. It's tagged inconsistently, so these are lower bounds, and it's left in.
- USASpending overwrites recipient names with current ones, so a company's past name isn't recoverable (Harris shows as L3Harris before the merger).