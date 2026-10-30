-- Combined obligations of merger families by year, buyer and acquired side shown separately.
-- Pre-merger names are overwritten with current ones in USASpending, so families are set by UEI where known and by name for the acquired companies.

with fam as (
    select
        fiscal_year,
        case
            when recipient_group_uei in ('SJULQDJ8NZU7', 'XXP4PLFFFGK9')
                then 'L3 + Harris (closed FY2019 Q4)'
            when recipient_group_uei in ('PPLZG8J3N9D4', 'KLW3ZYL15493')
                 or upper(recipient_group_name) like 'ROCKWELL COLLINS%'
                then 'UTC + Rockwell Collins + Raytheon (FY2019, FY2020)'
            when recipient_group_uei in ('NKVZLJL93QT6', 'GJVCPEBZV574')
                then 'Northrop + Orbital ATK (FY2018)'
            when recipient_group_uei = 'VF58HFRNGEL8'
                 or upper(recipient_group_name) like 'CSRA%'
                then 'General Dynamics + CSRA (FY2018)'
            when upper(recipient_group_name) like 'HUNTINGTON INGALLS%'
                 or upper(recipient_group_name) like 'ALION%'
                then 'HII + Alion (FY2022)'
        end as family,
        case
            when recipient_group_uei in ('XXP4PLFFFGK9', 'KLW3ZYL15493', 'GJVCPEBZV574')
                 or upper(recipient_group_name) like 'ROCKWELL COLLINS%'
                 or upper(recipient_group_name) like 'CSRA%'
                 or upper(recipient_group_name) like 'ALION%'
                then 'acquired'
            else 'buyer'
        end as role,
        obligated
    from {{ ref('rpt_recipient_year') }}
    where fiscal_year between 2017 and 2025
)
select
    family,
    fiscal_year,
    round(sum(case when role = 'buyer' then obligated else 0 end) / 1e9, 1) as buyer_b,
    round(sum(case when role = 'acquired' then obligated else 0 end) / 1e9, 1) as acquired_b,
    round(sum(obligated) / 1e9, 1) as combined_b
from fam
where family is not null
group by 1, 2
order by 1, 2