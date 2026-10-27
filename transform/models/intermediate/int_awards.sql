-- grain: one row per award (no IDVs) whose base record (modification 0) is in the data window
-- shared by rpt_award_profile, rpt_award_stats, rpt_award_outliers
with transactions as (

    select
        contract_award_unique_key,
        award_id_piid,
        transaction_number,
        modification_number,
        award_key,
        awarding_agency_key,
        awarding_office_code,
        recipient_key,
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

-- each award's base row for its descriptive columns; some awards have several mod 0 rows, keep one
award_base as (

    select
        t.contract_award_unique_key,
        t.award_id_piid,
        d.fiscal_year as start_fiscal_year,
        a.award_type,
        ag.agency_code,
        ag.sub_agency_name,
        {{ service_group('ag.agency_code', 'ag.sub_agency_name', 't.awarding_office_code') }} as service_group,
        t.recipient_key
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

)

-- inner join keeps only awards that started in the window; negative durations are bad dates
select
    ab.contract_award_unique_key,
    ab.award_id_piid,
    ab.start_fiscal_year,
    ab.award_type,
    ab.agency_code,
    ab.sub_agency_name,
    ab.service_group,
    ab.recipient_key,
    atl.obligated,
    atl.start_date,
    atl.end_date,
    case
        when datediff(day, atl.start_date, atl.end_date) >= 0
            then datediff(day, atl.start_date, atl.end_date)
    end as duration_days
from award_base as ab
join award_totals as atl
    on ab.contract_award_unique_key = atl.contract_award_unique_key