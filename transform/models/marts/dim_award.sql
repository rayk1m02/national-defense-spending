-- grain: one row per award type combination (codes only, descriptions looked up)
-- parent_award_id_piid lives on fct_transaction (one value per parent vehicle, not a type)
with transactions as (

    select
        award_or_idv_flag,
        award_type_code,
        award_type,
        idv_type,
        parent_award_type,
        multiple_or_single_award_idv,
        type_of_idc,
        type_of_contract_pricing_code,
        type_of_contract_pricing
    from {{ ref('stg_contract_transactions') }}

),

-- most common description per code, so a one off spelling does not win
-- (pricing code J has 1 'FIXED PRICE' row vs 32.6M 'FIRM FIXED PRICE')
award_type_names as (

    select
        award_type_code,
        award_type
    from transactions as t
    where award_type_code is not null
        and award_type is not null
    group by 1, 2
    qualify row_number() over (
        partition by award_type_code
        order by count(*) desc, award_type
    ) = 1

),

pricing_names as (

    select
        type_of_contract_pricing_code,
        type_of_contract_pricing
    from transactions as t
    where type_of_contract_pricing_code is not null
        and type_of_contract_pricing is not null
    group by 1, 2
    qualify row_number() over (
        partition by type_of_contract_pricing_code
        order by count(*) desc, type_of_contract_pricing
    ) = 1

),

combos as (

    select distinct
        award_or_idv_flag,
        award_type_code,
        idv_type,
        parent_award_type,
        multiple_or_single_award_idv,
        type_of_idc,
        type_of_contract_pricing_code
    from transactions

)

select 
    {{ dbt_utils.generate_surrogate_key([
        'c.award_or_idv_flag',
        'c.award_type_code',
        'c.idv_type',
        'c.parent_award_type',
        'c.multiple_or_single_award_idv',
        'c.type_of_idc',
        'c.type_of_contract_pricing_code'
    ])}} as award_key,
    c.award_or_idv_flag,
    c.award_type_code,
    an.award_type,
    c.idv_type,
    c.parent_award_type,
    c.multiple_or_single_award_idv,
    c.type_of_idc,
    c.type_of_contract_pricing_code,
    pn.type_of_contract_pricing
from combos as c
left join award_type_names as an
    on c.award_type_code = an.award_type_code
left join pricing_names as pn
    on c.type_of_contract_pricing_code = pn.type_of_contract_pricing_code