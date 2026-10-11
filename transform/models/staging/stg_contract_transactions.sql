with source as (

    select * from {{ source('raw_nds', 'contract_transactions') }}

),

cleaned as (

    select
        -- identifiers (stay varchar)
        contract_transaction_unique_key,
        contract_award_unique_key,
        -- ...

        -- dates
        action_date::date as action_date,
        -- ...

        -- money
        federal_action_obligation::numeric(23, 2) as federal_action_obligation,
        -- ...

        -- integers
        action_date_fiscal_year::integer as action_date_fiscal_year,
        -- ...

        -- business type flags
        veteran_owned_business::boolean as veteran_owned_business,
        -- ...

        -- state code fix (pending the query above)

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
    from cleaned
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