-- grain: one row per fiscal year, place of performance state, recipient state.
with transactions as (

    select
        action_date_key,
        location_key,
        recipient_key,
        federal_action_obligation
    from {{ ref('fct_transaction') }}

),

dates as (

    select
        date_day,
        fiscal_year
    from {{ ref('dim_date') }}

),

locations as (

    select
        location_key,
        primary_place_of_performance_country_name,
        primary_place_of_performance_state_code
    from {{ ref('dim_location') }}

),

recipients as (

    select
        recipient_key,
        recipient_state_code,
        domestic_or_foreign_entity
    from {{ ref('dim_recipient') }}

)

select
    d.fiscal_year,
    case
        when l.primary_place_of_performance_state_code is not null then l.primary_place_of_performance_state_code
        when l.primary_place_of_performance_country_name is not null
            and l.primary_place_of_performance_country_name <> 'UNITED STATES' then 'Foreign'
        else 'Unknown'
    end as pop_state,
    case
        when r.recipient_state_code is not null then r.recipient_state_code
        when r.domestic_or_foreign_entity in ('FOREIGN-OWNED BUSINESS NOT INCORPORATED IN THE U.S.', 'OTHER FOREIGN ENTITY (E.G. FOREIGN GOVERNMENT)') then 'Foreign'
        else 'Unknown'
    end as recipient_state,
    sum(t.federal_action_obligation) as obligated,
    count(*) as transaction_count
from transactions t
left join dates d on t.action_date_key = d.date_day
left join locations l on t.location_key = l.location_key
left join recipients r on t.recipient_key = r.recipient_key
group by 1, 2, 3