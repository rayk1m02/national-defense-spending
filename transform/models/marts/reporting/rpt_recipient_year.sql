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

),

overrides as (

    select
        recipient_group_uei,
        corrected_group_uei,
        corrected_group_name 
    from {{ ref('recipient_group_overrides') }}

),

recipient_years as (

    select
        l.recipient_uei,
        l.fiscal_year,
        l.recipient_name,
        coalesce(o.corrected_group_uei, l.recipient_group_uei) as recipient_group_uei,
        coalesce(o.corrected_group_name, l.recipient_group_name) as recipient_group_name,
        sum(l.federal_action_obligation) as obligated,
        count(*) as transaction_count,
        sum(case when l.pricing_bucket = 'Fixed price' then l.federal_action_obligation else 0 end) as obligated_fixed_price,
        sum(case when l.pricing_bucket = 'Cost reimbursement' then l.federal_action_obligation else 0 end) as obligated_cost_reimbursement,
        sum(case when l.pricing_bucket = 'Time and materials' then l.federal_action_obligation else 0 end) as obligated_time_and_materials,
        sum(case when l.pricing_bucket = 'Other' then l.federal_action_obligation else 0 end) as obligated_other,
        sum(case when l.is_small then l.federal_action_obligation else 0 end) as obligated_small_business,
        sum(case when l.c8a_program_participant and l.is_small then l.federal_action_obligation else 0 end) as obligated_8a,
        sum(case when l.small_disadvantaged_business and l.is_small then l.federal_action_obligation else 0 end) as obligated_sdb,
        sum(case when l.women_owned_small_business and l.is_small then l.federal_action_obligation else 0 end) as obligated_wosb,
        sum(case when l.historically_underutilized_business_zone_hubzone_firm and l.is_small then l.federal_action_obligation else 0 end) as obligated_hubzone,
        sum(case when l.veteran_owned_business and l.is_small then l.federal_action_obligation else 0 end) as obligated_veteran_owned
    from labeled as l
    left join overrides as o
        on l.recipient_group_uei = o.recipient_group_uei
    group by 1, 2, 3, 4, 5

),

-- each group's rank within its fiscal year (top 10 per year, CR10)
group_years as (

    select
        fiscal_year,
        recipient_group_uei,
        rank() over (partition by fiscal_year order by sum(obligated) desc) as group_rank_in_year
    from recipient_years
    group by 1, 2

),

-- each group's rank across all years (top 20 cumulative)
group_overall as (

    select
        recipient_group_uei,
        rank() over (order by sum(obligated) desc) as group_rank_overall
    from recipient_years
    group by 1

)

select
    ry.*,
    gy.group_rank_in_year,
    go.group_rank_overall
from recipient_years as ry
left join group_years as gy
    on ry.fiscal_year = gy.fiscal_year
    and ry.recipient_group_uei = gy.recipient_group_uei
left join group_overall as go
    on ry.recipient_group_uei = go.recipient_group_uei