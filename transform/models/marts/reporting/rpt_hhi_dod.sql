-- how has hhi moved for DoD contractors FY2017 to 2025
-- has market become more or less concentrated for DoD contractors over the years?
-- hhi: sum of each parent company's squared market share

with transactions as (
    
    select
        action_date_key,
        recipient_key,
        federal_action_obligation,
        awarding_agency_key
    from {{ ref('fct_transaction') }}

),

dod_transactions as (

    select
        t.action_date_key,
        t.recipient_key,
        t.federal_action_obligation,
        t.awarding_agency_key
    from transactions t
    join {{ ref('dim_agency') }} a on t.awarding_agency_key = a.agency_key
    where a.budget_subfunction = '051'

),

dates as (

    select
        date_day,
        fiscal_year
    from {{ ref('dim_date') }}

),

recipients as (

    select
        recipient_key,
        recipient_uei,
        recipient_name,
        recipient_parent_uei,
        recipient_parent_name
    from {{ ref('dim_recipient') }}

),

labeled as (

    select
        d.fiscal_year,
        r.recipient_uei,
        r.recipient_name,
        coalesce(recipient_parent_uei, recipient_uei) as recipient_group_uei,
        case
            when recipient_parent_uei is not null then recipient_parent_name
            else recipient_name
        end as recipient_group_name,
        dt.federal_action_obligation
    from dod_transactions dt
    left join dates d on dt.action_date_key = d.date_day
    left join recipients r on dt.recipient_key = r.recipient_key
    where d.fiscal_year >= 2017 and d.fiscal_year <= 2025

),

overrides as (

    select
        recipient_group_uei,
        corrected_group_uei,
        corrected_group_name
    from {{ ref('recipient_group_overrides') }}

),

recipient_years as (

    select
        l.recipient_uei,
        l.recipient_name,
        coalesce(o.corrected_group_uei, l.recipient_group_uei) as recipient_group_uei,
        coalesce(o.corrected_group_name, l.recipient_group_name) as recipient_group_name,
        l.fiscal_year,
        sum(l.federal_action_obligation) as obligated
    from labeled as l
    left join overrides as o
        on l.recipient_group_uei = o.recipient_group_uei
    group by 1, 2, 3, 4, 5

),

total_recipient_yearly as (

    select
        recipient_group_uei,
        fiscal_year,
        sum(obligated) as total_recipient
    from recipient_years
    group by 1, 2
    having sum(obligated) > 0

),

total_market_yearly as (

    select
        fiscal_year,
        sum(total_recipient) as total_market
    from total_recipient_yearly
    group by 1

),

shares as (

    select
        tr.recipient_group_uei,
        tr.fiscal_year,
        (tr.total_recipient::double precision / tm.total_market) * 100.0 as share_pct
    from total_recipient_yearly tr
    left join total_market_yearly tm on tr.fiscal_year = tm.fiscal_year

)

select
    s.fiscal_year,
    sum(power(s.share_pct, 2)) as hhi,
    sum(s.share_pct) as total_share_pct
from shares s
group by s.fiscal_year
order by s.fiscal_year

/**
Lockheed

select
    s.fiscal_year,
    round(sum(case when s.recipient_group_uei = 'ZFN2JJXBLZT3' then s.share_pct else 0 end), 2) as lockheed_share_pct,
    round(sum(case when s.recipient_group_uei = 'ZFN2JJXBLZT3' then power(s.share_pct, 2) else 0 end), 0) as lockheed_hhi,
    round(sum(power(s.share_pct, 2)), 0) as total_hhi,
    round(
        100.0 * sum(case when s.recipient_group_uei = 'ZFN2JJXBLZT3' then power(s.share_pct, 2) else 0 end)
            / sum(power(s.share_pct, 2)),
        1
    ) as lockheed_pct_of_hhi
from shares s
group by s.fiscal_year
order by s.fiscal_year
*/