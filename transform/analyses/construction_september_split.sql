-- September and October share of FY2017 to FY2025 obligations for new construction (Y) vs maintenance and repair of real property (Z). 
-- An even month is 8.3%.

select
    left(product_or_service_code, 1) as psc_letter,
    round(sum(federal_action_obligation) / 1e9, 1) as total_b,
    round(100.0 * sum(case when extract(month from action_date) = 9
                           then federal_action_obligation else 0 end)
          / nullif(sum(federal_action_obligation), 0), 1) as sep_pct,
    round(100.0 * sum(case when extract(month from action_date) = 10
                           then federal_action_obligation else 0 end)
          / nullif(sum(federal_action_obligation), 0), 1) as oct_pct
from {{ ref('stg_contract_transactions') }}
where action_date_fiscal_year between 2017 and 2025
  and left(product_or_service_code, 1) in ('Y', 'Z')
group by 1
order by 1