-- Yearly obligations in nominal and FY2017 dollars, deflated with CPI-U (seeds/cpi_u_annual.csv).
-- Calendar-year CPI is applied to the matching fiscal year.

with yearly as (
    select fiscal_year, sum(obligated) as nominal
    from {{ ref('rpt_spend_monthly') }}
    where fiscal_year between 2017 and 2025
    group by 1
),
joined as (
    select
        y.fiscal_year,
        y.nominal,
        c.cpi_u,
        y.nominal * base.cpi_u / c.cpi_u as real_2017
    from yearly as y
    join {{ ref('cpi_u_annual') }} as c on c.calendar_year = y.fiscal_year
    cross join (select cpi_u from {{ ref('cpi_u_annual') }} where calendar_year = 2017) as base
)
select
    fiscal_year,
    round(nominal / 1e9, 1) as nominal_b,
    cpi_u,
    round(real_2017 / 1e9, 1) as real_2017_b,
    round(100.0 * (nominal / first_value(nominal) over (order by fiscal_year rows between unbounded preceding and unbounded following) - 1), 1) as nominal_growth_pct,
    round(100.0 * (real_2017 / first_value(real_2017) over (order by fiscal_year rows between unbounded preceding and unbounded following) - 1), 1) as real_growth_pct
from joined
order by fiscal_year