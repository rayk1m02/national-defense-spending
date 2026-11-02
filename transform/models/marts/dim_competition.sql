-- grain: one row per extent_competed, type_of_set_aside, other_than_full_and_open_competition, business size combination
with transactions as (

    select
        extent_competed, -- was it competed, how? (full and open, not competed, competed under SAP, etc)
        type_of_set_aside, -- if competition was limited to a group, which group? (Small business, 8(a), HUBZone, SDVOSB, etc)
        other_than_full_and_open_competition, -- if it wasn't competed, what's the legal justification? (only one source, URGENCY, NATIONAL SECURITY, etc)
        contracting_officers_determination_of_business_size
    from {{ ref('stg_contract_transactions') }}

)

select distinct
    {{ dbt_utils.generate_surrogate_key([
        't.extent_competed',
        't.type_of_set_aside',
        't.other_than_full_and_open_competition',
        't.contracting_officers_determination_of_business_size'
    ]) }} as competition_key,
    t.extent_competed,
    t.type_of_set_aside,
    t.other_than_full_and_open_competition,
    t.contracting_officers_determination_of_business_size
from transactions as t