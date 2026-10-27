-- grain: one row per start fiscal year, award type, service group, size bucket, length bucket
-- awards only (no IDVs), and only awards whose base record (modification 0) is in the data window
with transactions as (

    select
        transaction_number,
        contract_award_unique_key,
        modification_number,
        award_key,
        awarding_agency_key,
        awarding_office_code,
        action_date_key,
        pop_start_date_key,
        pop_end_date_key,
        federal_action_obligation
    from {{ ref('fct_transaction') }}

),

awards as (

    select
        award_key,
        award_or_idv_flag,
        award_type
    from {{ ref('dim_award') }}

),

dates as (

    select
        date_day,
        fiscal_year
    from {{ ref('dim_date') }}

),

agencies as (

    select
        agency_key,
        agency_code,
        sub_agency_name
    from {{ ref('dim_agency') }}

),

-- one row per award: total obligated, start from the base row, latest end date
award_totals as (

    select
        t.contract_award_unique_key,
        sum(t.federal_action_obligation) as obligated,
        min(case when t.modification_number = '0' then t.pop_start_date_key end) as start_date,
        max(t.pop_end_date_key) as end_date
    from transactions as t
    join awards as a on t.award_key = a.award_key
    where a.award_or_idv_flag = 'AWARD'
    group by 1

),

-- each award's base row (modification 0) for its descriptive columns
award_base as (

    select
        t.contract_award_unique_key,
        d.fiscal_year as start_fiscal_year,
        a.award_type,
        {{ service_group('ag.agency_code', 'ag.sub_agency_name', 't.awarding_office_code') }} as service_group
    from transactions as t
    join awards as a on t.award_key = a.award_key
    left join dates as d on t.action_date_key = d.date_day
    left join agencies as ag on t.awarding_agency_key = ag.agency_key
    where a.award_or_idv_flag = 'AWARD'
        and t.modification_number = '0'
    qualify row_number() over (
        partition by t.contract_award_unique_key
        order by t.action_date_key, t.transaction_number
    ) = 1

),

-- inner join keeps only awards that started in the window. Negative durations are bad dates
award_measures as (

    select
        ab.start_fiscal_year,
        ab.award_type,
        ab.service_group,
        atl.obligated,
        case
            when datediff(day, atl.start_date, atl.end_date) >= 0
                then datediff(day, atl.start_date, atl.end_date)
        end as duration_days
    from award_base as ab
    join award_totals as atl
        on ab.contract_award_unique_key = atl.contract_award_unique_key

),

bucketed as (

    select
        start_fiscal_year,
        award_type,
        service_group,
        obligated,
        duration_days,
        case
            when obligated <= 0 then 'Zero or negative'
            when obligated < 10000 then 'Under $10K'
            when obligated < 250000 then '$10K to $250K'
            when obligated < 1000000 then '$250K to $1M'
            when obligated < 10000000 then '$1M to $10M'
            when obligated < 100000000 then '$10M to $100M'
            when obligated < 1000000000 then '$100M to $1B'
            else '$1B and up'
        end as size_bucket,
        case
            when obligated <= 0 then 1
            when obligated < 10000 then 2
            when obligated < 250000 then 3
            when obligated < 1000000 then 4
            when obligated < 10000000 then 5
            when obligated < 100000000 then 6
            when obligated < 1000000000 then 7
            else 8
        end as size_bucket_order,
        case
            when duration_days is null then 'Unknown'
            when duration_days < 30 then 'Under 1 month'
            when duration_days < 183 then '1 to 6 months'
            when duration_days < 365 then '6 to 12 months'
            when duration_days < 730 then '1 to 2 years'
            when duration_days < 1826 then '2 to 5 years'
            else '5 years and up'
        end as length_bucket,
        case
            when duration_days is null then 7
            when duration_days < 30 then 1
            when duration_days < 183 then 2
            when duration_days < 365 then 3
            when duration_days < 730 then 4
            when duration_days < 1826 then 5
            else 6
        end as length_bucket_order
    from award_measures

)

select
    start_fiscal_year,
    award_type,
    service_group,
    size_bucket,
    size_bucket_order,
    length_bucket,
    length_bucket_order,
    count(*) as award_count,
    sum(obligated) as obligated,
    sum(duration_days) as duration_days_total,
    count(duration_days) as awards_with_duration,
    min(obligated) as min_obligated,
    max(obligated) as max_obligated,
    min(duration_days) as min_duration_days,
    max(duration_days) as max_duration_days
from bucketed
group by 1, 2, 3, 4, 5, 6, 7