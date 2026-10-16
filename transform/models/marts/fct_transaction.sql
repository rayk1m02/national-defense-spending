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

    -- implement

),

with dates as (

   -- implement 

)

select 
    -- implement
from transactions as t
left join recipients as r
    on --implement
left join dates as ad 
    on -- implement for action date
left join dates as ps
    on -- implement for place_of_performance_start_date
left join dates as pe 
    on -- implement for place_of_performance_end_date
left join dates as sd
    on -- implement for solicitation_date