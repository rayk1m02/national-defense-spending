-- scd2 on recipient_parent_uei, recipient_state_code (ownership change, registered relocation, respectively)
-- transaction level values flap (same company reports different entities in its corporate family)
-- each year we use the value with most dollars
-- grain: one row per recipient per version
with transactions as (

    select
        recipient_uei,
        action_date_fiscal_year as fiscal_year,
        action_date,
        last_modified_date,
        contract_transaction_unique_key,
        federal_action_obligation,
        recipient_name,
        recipient_parent_uei,
        recipient_parent_name,
        recipient_state_code,
        veteran_owned_business,
        woman_owned_business,
        women_owned_small_business,
        minority_owned_business,
        small_disadvantaged_business,
        c8a_program_participant,
        historically_underutilized_business_zone_hubzone_firm,
        domestic_or_foreign_entity_code,
        domestic_or_foreign_entity          
    from {{ ref('stg_contract_transactions') }}

),

-- dominant parent per recipient per fiscal year (using abs dollars)
yearly_parent as (

    select
        recipient_uei,
        recipient_parent_uei,
        fiscal_year,
        -- within each recipient + fiscal year group, prioritize sum($), then count of transactions, then alphabetically on parent UEI as last resort
        row_number() over (
            partition by recipient_uei, fiscal_year
            order by sum(abs(federal_action_obligation)) desc, count(*) desc, recipient_parent_uei
        ) as rn
    from transactions
    group by 1, 2, 3

),

-- dominant state per recipient per fiscal year
yearly_state as (

    select
        recipient_uei,
        recipient_state_code,
        fiscal_year,
        row_number() over (
            partition by recipient_uei, fiscal_year
            order by sum(abs(federal_action_obligation)) desc, count(*) desc, recipient_state_code
        ) as rn
    from transactions
    group by 1, 2, 3

),

-- dominant parent + state combo per fiscal year
yearly as (

    select 
        p.recipient_uei,
        p.fiscal_year,
        p.recipient_parent_uei,
        s.recipient_state_code,
        coalesce(p.recipient_parent_uei, '') || '|' || coalesce(s.recipient_state_code, '') as attrs
    from yearly_parent as p
    join yearly_state as s
        on p.recipient_uei = s.recipient_uei
        and p.fiscal_year = s.fiscal_year
    where p.rn = 1
        and s.rn = 1

),

-- add previous years attrs for same recipient
changes as (

    select
        *,
        lag(attrs) over (partition by recipient_uei order by fiscal_year) as prev_attrs
    from yearly

),

-- one row per version (years where pair differs from previous year)
versions as (

    select 
        recipient_uei,
        recipient_parent_uei,
        recipient_state_code,
        fiscal_year as start_fy,
        lead(fiscal_year) over (partition by recipient_uei order by fiscal_year) as next_start_fy
    from changes
    where prev_attrs is null
        or attrs <> prev_attrs

),

-- one row per recipient (latest transaction and type 1 attributes)
latest as (

    select  
        recipient_uei,
        recipient_name,
        veteran_owned_business,
        woman_owned_business,
        women_owned_small_business,
        minority_owned_business,
        small_disadvantaged_business,
        c8a_program_participant,
        historically_underutilized_business_zone_hubzone_firm,
        domestic_or_foreign_entity_code,
        domestic_or_foreign_entity
    from transactions as t
    qualify row_number() over (
        partition by recipient_uei
        order by action_date desc, last_modified_date desc, contract_transaction_unique_key desc
    ) = 1

),

-- one name for each parent UEI (most recent)
-- name is handled separately in case of spelling differences which would create unwanted combinations/versions
parent_names as (

    select 
        recipient_parent_uei,
        recipient_parent_name
    from transactions as t
    where recipient_parent_uei is not null
        and recipient_parent_name is not null
    qualify row_number() over (
        partition by recipient_parent_uei
        order by action_date desc, recipient_parent_name
    ) = 1

)

select 
    {{ dbt_utils.generate_surrogate_key(['v.recipient_uei', 'v.start_fy']) }} as recipient_key,
    v.recipient_uei,
    l.recipient_name,
    v.recipient_parent_uei,
    pn.recipient_parent_name,
    v.recipient_state_code,
    l.veteran_owned_business,
    l.woman_owned_business,
    l.women_owned_small_business,
    l.minority_owned_business,
    l.small_disadvantaged_business,
    l.c8a_program_participant,
    l.historically_underutilized_business_zone_hubzone_firm,
    l.domestic_or_foreign_entity_code,
    l.domestic_or_foreign_entity,
    -- fiscal year N runs Oct 1 of N-1 through Sep 30 of N
    to_date(cast(v.start_fy - 1 as varchar) || '-10-01', 'YYYY-MM-DD') as effective_start_date,
    case
        when v.next_start_fy is not null
            then to_date(cast(v.next_start_fy - 1 as varchar) || '-09-30', 'YYYY-MM-DD')
    end as effective_end_date,
    (v.next_start_fy is null) as is_current
from versions as v
join latest as l
    on l.recipient_uei = v.recipient_uei
left join parent_names as pn
    on pn.recipient_parent_uei = v.recipient_parent_uei