with source as (

    select * from {{ source('raw_nds', 'contract_transactions') }}

),

cleaned as (

    select
        -- identifiers (stay varchar)
        contract_transaction_unique_key,
        contract_award_unique_key,
        award_id_piid,
        transaction_number,
        modification_number,
        action_type,
        action_type_code,

        -- agency
        awarding_agency_code,
        awarding_agency_name,
        awarding_sub_agency_name,
        funding_agency_code,
        funding_agency_name,
        funding_sub_agency_name,

        -- recipient
        recipient_uei,
        recipient_name,
        recipient_parent_uei,
        recipient_parent_name,
        contracting_officers_determination_of_business_size,
        domestic_or_foreign_entity_code,
        domestic_or_foreign_entity,

        -- place of performance
        primary_place_of_performance_state_code,
        primary_place_of_performance_state_name,
        primary_place_of_performance_city_name,
        primary_place_of_performance_county_name,
        primary_place_of_performance_country_name,

        -- product/service
        naics_code,
        naics_description,
        product_or_service_code,
        product_or_service_code_description,

        -- award type
        award_or_idv_flag,
        award_type_code,
        award_type,
        idv_type,
        parent_award_id_piid,
        parent_award_type,
        multiple_or_single_award_idv,
        type_of_idc,
        type_of_contract_pricing_code,
        type_of_contract_pricing,

        -- competition
        extent_competed,
        type_of_set_aside,
        other_than_full_and_open_competition,

        -- dates
        action_date::date as action_date,
        period_of_performance_start_date::date as period_of_performance_start_date,
        period_of_performance_current_end_date::date as period_of_performance_current_end_date,
        solicitation_date::date as solicitation_date,

        -- money
        federal_action_obligation::numeric(23, 2) as federal_action_obligation,
        total_dollars_obligated::numeric(23, 2) as total_dollars_obligated,
        total_outlayed_amount_for_overall_award::numeric(23, 2) as total_outlayed_amount_for_overall_award,
        current_total_value_of_award::numeric(23, 2) as current_total_value_of_award,
        potential_total_value_of_award::numeric(23, 2) as potential_total_value_of_award,

        -- integers
        action_date_fiscal_year::integer as action_date_fiscal_year,
        number_of_offers_received::integer as number_of_offers_received,

        -- business type flags
        (veteran_owned_business = 't') as veteran_owned_business,
        (woman_owned_business = 't') as woman_owned_business,
        (women_owned_small_business = 't') as women_owned_small_business,
        (minority_owned_business = 't') as minority_owned_business,
        (small_disadvantaged_business = 't') as small_disadvantaged_business,
        (c8a_program_participant = 't') as c8a_program_participant,
        (historically_underutilized_business_zone_hubzone_firm = 't') as historically_underutilized_business_zone_hubzone_firm,

        -- state code fix
        case
            when recipient_state_code = 'VIRGINIA' then 'VA'
            when recipient_state_code = 'GEORGIA' then 'GA'
            when len(recipient_state_code) = 2 then recipient_state_code
        end as recipient_state_code,

        -- pipeline
        last_modified_date::timestamp as last_modified_date,
        correction_delete_ind,
        awarding_office_code,
        federal_accounts_funding_this_award,
        source,
        source_file,
        _loaded_at

    from source

),

deduped as (

    select *
    from cleaned as c
    qualify row_number() over (
        partition by contract_transaction_unique_key
        order by
            last_modified_date desc,
            case when source_file like '%/delta/%' then 0 else 1 end
    ) = 1

)

select *
from deduped
where correction_delete_ind is null
   or correction_delete_ind <> 'D'