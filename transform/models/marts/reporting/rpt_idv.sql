-- grain: one row per single-award IDIQ that started in our window. An IDV's starting record is its modification_number = '0' row.
with transactions as (

    select
        contract_award_unique_key,
        award_id_piid,
        parent_award_id_piid,
        modification_number,
        action_date_key,
        award_key,
        awarding_agency_key,
        recipient_key,
        federal_action_obligation,
        potential_total_value_of_award
    from {{ ref('fct_transaction') }}

),

awards as (

    select
        award_key,
        award_or_idv_flag,
        idv_type,
        multiple_or_single_award_idv
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
        sub_agency_name,
        budget_subfunction
    from {{ ref('dim_agency') }}

),

recipients as (

    select
        recipient_key,
        recipient_name
    from {{ ref('dim_recipient') }}

),

-- each IDV's starting row
idv_base as (

    select
        t.contract_award_unique_key as idv_key,
        t.award_id_piid,
        d.fiscal_year as base_fiscal_year,
        ag.sub_agency_name,
        ag.budget_subfunction,
        r.recipient_name
    from transactions as t
    left join awards as a on t.award_key = a.award_key
    left join dates as d on t.action_date_key = d.date_day
    left join agencies as ag on t.awarding_agency_key = ag.agency_key
    left join recipients as r on t.recipient_key = r.recipient_key
    where a.award_or_idv_flag = 'IDV'
        and a.idv_type = 'IDC'
        and a.multiple_or_single_award_idv = 'SINGLE AWARD'
        and t.modification_number = '0'

),

-- each IDV's ceiling (same on every row of an award, max chooses one)
idv_ceiling as (

    select
        contract_award_unique_key as idv_key,
        max(potential_total_value_of_award) as ceiling
    from transactions
    group by 1

),

-- orders summed under their parent IDV, key rebuilt from the order's own key
orders as (

    select
        'CONT_IDV_' || split_part(contract_award_unique_key, '_', 5)
            || '_' || split_part(contract_award_unique_key, '_', 6) as parent_idv_key,
        sum(federal_action_obligation) as orders_obligated,
        count(distinct contract_award_unique_key) as order_count
    from transactions
    where parent_award_id_piid is not null
    group by 1

)

select
    ib.idv_key,
    ib.award_id_piid,
    ib.base_fiscal_year,
    ib.sub_agency_name,
    ib.budget_subfunction,
    ib.recipient_name,
    ic.ceiling,
    coalesce(o.orders_obligated, 0) as orders_obligated,
    coalesce(o.order_count, 0) as order_count,
    coalesce(o.orders_obligated, 0)::double precision / ic.ceiling as utilization
from idv_base as ib
left join idv_ceiling as ic
    on ib.idv_key = ic.idv_key
left join orders as o
    on ib.idv_key = o.parent_idv_key
where ic.ceiling > 0