-- Did mergers speed up growth? Yearly dollars for five merger families, buyer and acquired company shown separately.
-- The five are every verified merger in the top 20 groups that moved $0.5B+ in a year (next largest under $0.25B). See top20_parent_changes.sql.
-- Families are matched by UEI where known. Acquired companies are also matched by name, since USASpending replaces old names with current ones.

with fam as (
    select
        fiscal_year,
        case
            when recipient_group_uei in ('SJULQDJ8NZU7', 'XXP4PLFFFGK9')
                then 'L3 + Harris (closed FY2019 Q3)'
            when recipient_group_uei in ('PPLZG8J3N9D4', 'KLW3ZYL15493')
                 or upper(recipient_group_name) like 'ROCKWELL COLLINS%'
                then 'UTC + Rockwell Collins + Raytheon (closed FY2019 Q1, FY2020 Q3)'
            when recipient_group_uei in ('NKVZLJL93QT6', 'GJVCPEBZV574')
                then 'Northrop + Orbital ATK (closed FY2018 Q3)'
            when recipient_group_uei = 'VF58HFRNGEL8'
                 or upper(recipient_group_name) like 'CSRA%'
                then 'General Dynamics + CSRA (closed FY2018 Q3)'
            when upper(recipient_group_name) like 'HUNTINGTON INGALLS%'
                 or upper(recipient_group_name) like 'ALION%'
                then 'HII + Alion (closed FY2021 Q4)'
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