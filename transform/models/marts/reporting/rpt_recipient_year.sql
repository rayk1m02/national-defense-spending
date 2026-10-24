-- grain: one row per UEI per fiscal year
with transactions as (

    select
        action_date_key,
        recipient_key,
        award_key,
        competition_key,
        federal_action_obligation,
        c8a_program_participant,
        small_disadvantaged_business,
        women_owned_small_business,
        historically_underutilized_business_zone_hubzone_firm,
        veteran_owned_business
    from {{ ref('fct_transaction') }}
        
),

dates as (

    select
        date_day,
        fiscal_year
    from {{ ref('dim_date') }}

),

recipients as (

    select
        recipient_key,
        recipient_uei,
        recipient_name,
        recipient_parent_uei,
        recipient_parent_name
    from {{ ref('dim_recipient') }}


), 

awards as (

    select
        award_key,
        type_of_contract_pricing_code
    from {{ ref('dim_award') }}

),

competitions as (

    select
        competition_key,
        contracting_officers_determination_of_business_size
    from {{ ref('dim_competition') }}

),

labeled as (

    select 
        d.fiscal_year,
        r.recipient_uei,
        r.recipient_name,
        coalesce(recipient_parent_uei, recipient_uei) as recipient_group_uei,
        case
            when recipient_parent_uei is not null then recipient_parent_name
            else recipient_name
        end as recipient_group_name,
        case
            when type_of_contract_pricing_code in ('J', 'L', 'K', 'B', 'M', 'A') then 'Fixed price'
            when type_of_contract_pricing_code in ('U', 'V', 'R', 'S', 'T') then 'Cost reimbursement'
            when type_of_contract_pricing_code in ('Y', 'Z') then 'Time and materials'
            else 'Other'
        end as pricing_bucket,
        (c.contracting_officers_determination_of_business_size = 'SMALL BUSINESS') as is_small,
        t.c8a_program_participant,
        t.small_disadvantaged_business,
        t.women_owned_small_business,
        t.historically_underutilized_business_zone_hubzone_firm,
        t.veteran_owned_business,
        t.federal_action_obligation
    from transactions t
    left join dates d on t.action_date_key = d.date_day
    left join recipients r on t.recipient_key = r.recipient_key
    left join awards a on t.award_key = a.award_key
    left join competitions c on t.competition_key = c.competition_key

)

select
    recipient_uei,
    fiscal_year,
    recipient_name,
    recipient_group_uei,
    recipient_group_name,
    sum(federal_action_obligation) as obligated,
    count(*) as transaction_count,
    sum(case when pricing_bucket = 'Fixed price' then federal_action_obligation else 0 end) as obligated_fixed_price,
    sum(case when pricing_bucket = 'Cost reimbursement' then federal_action_obligation else 0 end) as obligated_cost_reimbursement,
    sum(case when pricing_bucket = 'Time and materials' then federal_action_obligation else 0 end) as obligated_time_and_materials,
    sum(case when pricing_bucket = 'Other' then federal_action_obligation else 0 end) as obligated_other,
    sum(case when is_small then federal_action_obligation else 0 end) as obligated_small_business,
    sum(case when c8a_program_participant and is_small then federal_action_obligation else 0 end) as obligated_8a,
    sum(case when small_disadvantaged_business and is_small then federal_action_obligation else 0 end) as obligated_sdb,
    sum(case when women_owned_small_business and is_small then federal_action_obligation else 0 end) as obligated_wosb,
    sum(case when historically_underutilized_business_zone_hubzone_firm and is_small then federal_action_obligation else 0 end) as obligated_hubzone,
    sum(case when veteran_owned_business and is_small then federal_action_obligation else 0 end) as obligated_veteran_owned
from labeled
group by 1, 2, 3, 4, 5