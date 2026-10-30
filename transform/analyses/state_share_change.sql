-- Change in each place-of-performance state's share, FY2017 and FY2018 vs FY2024 and FY2025.
-- Two-year pairs so one large contract doesn't set a state's result. late_b is the two-year total.

with s as (
    select
        pop_state,
        sum(case when fiscal_year in (2017, 2018) then obligated else 0 end) as early_amt,
        sum(case when fiscal_year in (2024, 2025) then obligated else 0 end) as late_amt
    from {{ ref('rpt_state_year') }}
    group by 1
),
t as (
    select sum(early_amt) as early_total, sum(late_amt) as late_total
    from s
)
select
    pop_state,
    round(100.0 * early_amt / early_total, 2) as early_pct,
    round(100.0 * late_amt / late_total, 2) as late_pct,
    round(100.0 * late_amt / late_total - 100.0 * early_amt / early_total, 2) as change_pts,
    round(late_amt / 1e9, 1) as late_b
from s
cross join t
order by change_pts desc