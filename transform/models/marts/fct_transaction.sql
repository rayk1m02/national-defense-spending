-- grain: one row per contract transaction
-- dimension keys are recomputed with same columns / order as each dimension instead of joined:
    -- a join does not match NULLs (hash does)
    -- computing a hash on 41M rows is cheaper than joining them to six dimensions
    -- no dependency on most dimension tables
-- recipient (by date range) and dates (to stay within dim_dates window) are joined
with transactions as (

    select * from {{ ref('stg_contract_transactions') }}

),

recipients as (

    select
        recipient_key,
        recipient_uei,
        effective_start_date,
        effective_end_date
    from {{ ref('dim_recipient') }}

),

dates as (

    select
        date_day
    from {{ ref('dim_date') }}

)

select
    -- degenerate dimensions
    t.contract_transaction_unique_key,
    t.contract_award_unique_key,
    t.award_id_piid,
    t.parent_award_id_piid,
    t.transaction_number,
    t.modification_number,
    t.action_type_code,
    t.action_type,
    -- date keys (null when outside dim_dates window)
    ad.date_day as action_date_key,
    ps.date_day as pop_start_date_key,
    pe.date_day as pop_end_date_key,
    sd.date_day as solicitation_date_key,
    -- dimension keys
     {{ dbt_utils.generate_surrogate_key(['t.awarding_agency_code', 't.awarding_sub_agency_name']) }} as awarding_agency_key,
     {{ dbt_utils.generate_surrogate_key(['t.funding_agency_code', 't.funding_sub_agency_name']) }} as funding_agency_key,
    r.recipient_key,
    {{ dbt_utils.generate_surrogate_key([
        't.primary_place_of_performance_country_name',
        't.primary_place_of_performance_state_code',
        't.primary_place_of_performance_county_name',
        't.primary_place_of_performance_city_name'
    ])}} as location_key,
    {{ dbt_utils.generate_surrogate_key(['t.naics_code', 't.product_or_service_code']) }} as product_key,
        {{ dbt_utils.generate_surrogate_key([
        't.award_or_idv_flag',
        't.award_type_code',
        't.idv_type',
        't.parent_award_type',
        't.multiple_or_single_award_idv',
        't.type_of_idc',
        't.type_of_contract_pricing_code'
    ]) }} as award_key,
    {{ dbt_utils.generate_surrogate_key([
        't.extent_competed',
        't.type_of_set_aside',
        't.other_than_full_and_open_competition',
        't.contracting_officers_determination_of_business_size'
    ]) }} as competition_key,
    -- measures
    t.federal_action_obligation,
    t.total_dollars_obligated,
    t.total_outlayed_amount_for_overall_award,
    t.current_total_value_of_award,
    t.potential_total_value_of_award,
    t.number_of_offers_received
from transactions as t
left join recipients as r
    on t.recipient_uei = r.recipient_uei
        and t.action_date >= r.effective_start_date
        and (t.action_date <= r.effective_end_date or r.effective_end_date is null)
left join dates as ad 
    on t.action_date = ad.date_day
left join dates as ps
    on t.period_of_performance_start_date = ps.date_day
left join dates as pe 
    on t.period_of_performance_current_end_date = pe.date_day
left join dates as sd
    on t.solicitation_date = sd.date_day