-- Yearly obligations for 050 and each subfunction, with year-over-year change.
-- Also the yearly totals used for the inflation-adjusted comparison in the README.

with by_sub as (
    select fiscal_year, subfunction_label as series, sum(obligated) as amt
    from {{ ref('rpt_spend_monthly') }}
    where fiscal_year between 2017 and 2026
    group by 1, 2
),
total as (
    select fiscal_year, '050 Total' as series, sum(obligated) as amt
    from {{ ref('rpt_spend_monthly') }}
    where fiscal_year between 2017 and 2026
    group by 1
),
combined as (
    select * from by_sub
    union all
    select * from total
)
select
    series,
    fiscal_year,
    round(amt / 1e9, 1) as amt_b,
    round(100.0 * (amt / nullif(lag(amt) over (partition by series order by fiscal_year), 0) - 1), 1) as yoy_pct
from combined
order by series, fiscal_year