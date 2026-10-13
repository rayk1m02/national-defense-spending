with transactions as (

    select
        primary_place_of_performance_country_name,
        primary_place_of_performance_state_code,
        primary_place_of_performance_state_name,
        primary_place_of_performance_county_name,
        primary_place_of_performance_city_name,
        action_date
    from {{ ref('stg_contract_transactions') }}

),

-- latest non-null name per state code (eg. FM has two spellings)
state_names as (

    select primary_place_of_performance_state_code, primary_place_of_performance_state_name
    from transactions as t
    where primary_place_of_performance_state_code is not null
        and primary_place_of_performance_state_name is not null
    qualify row_number() over (
        partition by primary_place_of_performance_state_code
        order by action_date desc nulls last, primary_place_of_performance_state_name
    ) = 1

),

-- grain: country + state + county + city combos (including nulls)
locations as (

    select distinct
        primary_place_of_performance_country_name,
        primary_place_of_performance_state_code,
        primary_place_of_performance_county_name,
        primary_place_of_performance_city_name
    from transactions

)

select
    {{ dbt_utils.generate_surrogate_key([
        'l.primary_place_of_performance_country_name',
        'l.primary_place_of_performance_state_code',
        'l.primary_place_of_performance_county_name',
        'l.primary_place_of_performance_city_name'
    ])}} as location_key,
    l.primary_place_of_performance_country_name,
    l.primary_place_of_performance_state_code,
    s.primary_place_of_performance_state_name,
    l.primary_place_of_performance_county_name,
    l.primary_place_of_performance_city_name
from locations l
left join state_names as s
    on l.primary_place_of_performance_state_code = s.primary_place_of_performance_state_code