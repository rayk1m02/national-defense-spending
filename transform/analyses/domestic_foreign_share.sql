-- Share of each year's obligations by recipient domestic/foreign group.

select
    fiscal_year,
    domestic_foreign_group,
    round(sum(obligated) / 1e9, 1) as obligated_b,
    round(100.0 * sum(obligated) / sum(sum(obligated)) over (partition by fiscal_year), 2) as pct_of_year
from {{ ref('rpt_spend_monthly') }}
where fiscal_year between 2017 and 2026
group by 1, 2
order by 1, 2