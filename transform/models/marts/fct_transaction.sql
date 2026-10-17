-- grain: one row per contract transaction
-- dimension keys are recomputed with same columns / order as each dimension instead of joined:
    -- a join does not match NULLs (hash does)
    -- computing a hash on 41M rows is cheaper than joining them to six dimensions
    -- no dependency on most dimension tables
-- recipient (by date range) and dates (to stay within dim_dates window) are joined
with transactions as (

    select * from {{ ref('stg_contract_transactions') }}

),

with recipients as (

    select
        recipient_key,
        recipient_uei,
        effective_start_date,
        effective_end_date
    from {{ ref('dim_recipient') }}

),

with dates as (

    select
        date_day
    from {{ ref('dim_date') }}

)

select 
    -- implement
from transactions as t
left join recipients as r
    on t.recipient_uei = r.recipient_uei
        and t.action_date >= r.effective_start_date
        and t.action_date <= r.effective_end_date
left join dates as ad 
    on t.action_date = ad.date_day
left join dates as ps
    on t.place_of_performance_start_date = ps.date_day
left join dates as pe 
    on t.place_of_performance_end_date = pe.date_day
left join dates as sd
    on t.soliciation_date = sd.date_day