-- grain: one row per fiscal year, fiscal month, awarding agency/sub-agency, PSC portfolio group, competition bucket, new vs modified, domestic vs foreign
with transactions as (

    select
        action_date_key,
        awarding_agency_key,
        recipient_key,
        product_key,
        competition_key,
        awarding_office_code,
        modification_number,
        parent_award_id_piid,
        action_type_code,
        federal_action_obligation
    from {{ ref('fct_transaction') }}

),

dates as (

    select 
        date_day,
        fiscal_year
    from {{ ref('dim_date') }}

),

agencies as (

    select
        agency_key, 
        agency_code, 
        sub_agency_name, 
        budget_subfunction
    from {{ ref('dim_agency') }}

),

products as (

    select 
        product_key,
        psc_portfolio_group
    from {{ ref('dim_product') }}

),

competitions as (

    select  
        competition_key,
        extent_competed
    from {{ ref('dim_competition') }}

),

recipients as (

    select
        recipient_key,
        domestic_or_foreign_entity
    from {{ ref('dim_recipient') }}

),

labeled as (

    select 
        fiscal_year,
        budget_subfunction,
        agency_code,
        sub_agency_name,
        psc_portfolio_group,
        domestic_or_foreign_entity,
        federal_action_obligation,
        mod(extract(month from action_date_key) + 2, 12) + 1 as fiscal_month,
        date_trunc('month', action_date_key)::date as month_start_date,
        {{ service_group('agency_code', 'sub_agency_name', 'awarding_office_code') }} as service_group,
        case
            when extent_competed = 'FULL AND OPEN COMPETITION' then 'Full and open'
            when extent_competed in (
                'FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES', 
                'COMPETED UNDER SAP', 
                'COMPETITIVE DELIVERY ORDER') then 'Limited'
            when extent_competed in (
                'NOT COMPETED',
                'NOT AVAILABLE FOR COMPETITION',
                'NOT COMPETED UNDER SAP',
                'NON-COMPETITIVE DELIVERY ORDER',
                'FOLLOW ON TO COMPETED ACTION'
                ) then 'Sole source'
            when extent_competed is null then 'Not reported'
        end as competition_bucket,
        case 
            when modification_number = '0' and parent_award_id_piid is null then 'New contract or IDV'
            when modification_number = '0' then 'New order under an IDV'
            when action_type_code = 'G' then 'Option exercise'
            when action_type_code = 'C' then 'Funding only'
            else 'Other modification'
        end as action_category,
        case
            when domestic_or_foreign_entity in (
                'U.S. OWNED BUSINESS', 
                'OTHER U.S. ENTITY (E.G. GOVERNMENT)'
                ) then 'U.S.'
            when domestic_or_foreign_entity = 'FOREIGN-OWNED BUSINESS INCORPORATED IN THE U.S.' then 'Foreign-owned, U.S.-incorporated'
            when domestic_or_foreign_entity in (
                'FOREIGN-OWNED BUSINESS NOT INCORPORATED IN THE U.S.',
                'OTHER FOREIGN ENTITY (E.G. FOREIGN GOVERNMENT)'
                ) then 'Foreign'
            when domestic_or_foreign_entity is null then 'Not reported'
        end as domestic_foreign_group
    from transactions t
    left join dates d on t.action_date_key = d.date_day
    left join agencies a on t.awarding_agency_key = a.agency_key
    left join products p on t.product_key = p.product_key
    left join competitions c on t.competition_key = c.competition_key
    left join recipients r on t.recipient_key = r.recipient_key

)

select
    fiscal_year,
    fiscal_month,
    month_start_date,
    budget_subfunction,
    case budget_subfunction
        when '051' then '051 DoD'
        when '053' then '053 DOE Defense'
        when '054' then '054 DHS CISA, DOT MARAD'
    end as subfunction_label,
    agency_code,
    sub_agency_name,
    service_group,
    psc_portfolio_group,
    competition_bucket,
    action_category,
    domestic_or_foreign_entity,
    domestic_foreign_group,
    sum(federal_action_obligation) as obligated,
    count(*) as transaction_count
from labeled
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13