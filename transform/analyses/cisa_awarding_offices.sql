-- DHS (CISA) obligations by awarding office, FY2017 to FY2021.
-- 70RNPP (NPPD) became 70RCSA (CISA) in FY2019. guard_m checks for Federal Protective Service work (PSC S206).

select
    action_date_fiscal_year as fy,
    awarding_office_code,
    round(sum(federal_action_obligation) / 1e6, 1) as obligated_m,
    round(sum(case when product_or_service_code = 'S206'
                   then federal_action_obligation else 0 end) / 1e6, 1) as guard_m
from {{ ref('stg_contract_transactions') }}
where awarding_agency_code = '070'
  and action_date_fiscal_year between 2017 and 2021
group by 1, 2
order by 1, 3 desc