-- grain: one row per agency, sub-agency combination
-- natural key: agency_code + sub_agency_name
with transactions as (

    select
        awarding_agency_code,
        awarding_agency_name,
        awarding_sub_agency_name,
        funding_agency_code,
        funding_agency_name,
        funding_sub_agency_name
    from {{ ref('stg_contract_transactions') }}

),

-- one generic table for both roles, combining awarding and funding values
agencies as (

    select
        awarding_agency_code as agency_code,
        awarding_agency_name as agency_name,
        awarding_sub_agency_name as sub_agency_name
    from transactions

    union

    select
        funding_agency_code,
        funding_agency_name,
        funding_sub_agency_name
    from transactions

)

select 
    {{ dbt_utils.generate_surrogate_key(['a.agency_code', 'a.sub_agency_name']) }} as agency_key,
    a.agency_code,
    a.agency_name,
    a.sub_agency_name,
    -- describes awarding scope, extraction already filtered DOE, DHS, DOT, to defense rows
    case a.agency_code
        when '097' then '051'
        when '089' then '053'
        when '069' then '054'
        when '070' then '054'
    end as budget_subfunction
from agencies as a