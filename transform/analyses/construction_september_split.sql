-- September and October share of FY2017 to FY2025 obligations for new construction (Y) vs maintenance and repair of real property (Z). 
-- An even month is 8.3%.

with by_letter as (

    select
        left(product_or_service_code, 1) as psc_letter,
        sum(federal_action_obligation) as total,
        sum(
            case
                when extract(month from action_date) = 9 then federal_action_obligation
                else 0
            end
        ) as sep_total,
        sum(
            case
                when extract(month from action_date) = 10 then federal_action_obligation
                else 0
            end
        ) as oct_total
    from {{ ref('stg_contract_transactions') }}
    where action_date_fiscal_year between 2017 and 2025
        and left(product_or_service_code, 1) in ('Y', 'Z')
    group by 1

)

select
    psc_letter,
    round(total / 1e9, 1) as total_b,
    round(100.0 * sep_total / nullif(total, 0), 1) as sep_pct,
    round(100.0 * oct_total / nullif(total, 0), 1) as oct_pct
from by_letter
order by 1