with transactions as (

    select
        extent_competed,
        type_of_set_aside,
        other_than_full_and_open_competition,
        contracting_officers_determination_of_business_size
    from {{ ref('stg_contract_transactions') }}

)

select distinct
    {{ dbt_utils.generate_surrogate_key([
        't.extent_competed',
        't.type_of_set_aside',
        't.other_than_full_and_open_competition',
        't.contracting_officers_determination_of_business_size'
    ])}} as competition_key,
    t.extent_competed,
    t.type_of_set_aside,
    t.other_than_full_and_open_competition,
    t.contracting_officers_determination_of_business_size
from transactions as t