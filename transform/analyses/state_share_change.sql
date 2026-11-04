-- Measures how each place of performance state's share of total obligations changed from FY2017 to FY2025, in percentage points, comparing the first two years with the last two.

with s as (

    select
        pop_state,
        sum(case when fiscal_year in (2017, 2018) then obligated else 0 end) as early_amt,
        sum(case when fiscal_year in (2024, 2025) then obligated else 0 end) as late_amt
    from {{ ref('rpt_state_year') }}
    group by 1

),

t as (

    select 
        sum(early_amt) as early_total, 
        sum(late_amt) as late_total
    from s

)

select
    pop_state,
    round(100.0 * early_amt / early_total, 2) as early_pct,
    round(100.0 * late_amt / late_total, 2) as late_pct,
    round(
        (100.0 * late_amt / late_total)       -- late share
        - (100.0 * early_amt / early_total),  -- minus early share
        2
    ) as change_pts,
    round(late_amt / 1e9, 1) as late_b
from s
cross join t
order by change_pts desc