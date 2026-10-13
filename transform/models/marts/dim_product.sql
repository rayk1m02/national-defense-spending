with transactions as (
    
    select
        naics_code,
        naics_description,
        product_or_service_code,
        product_or_service_code_description,
        action_date
    from {{ ref('stg_contract_transactions') }}

), 

-- latest non-null description per code
naics as (

    select naics_code, naics_description
    from transactions t
    where naics_code is not null
        and naics_description is not null
    qualify row_number() over (
        partition by naics_code
        order by action_date desc nulls last, naics_description
    ) = 1

),

psc as (

    select product_or_service_code, product_or_service_code_description
    from transactions as t
    where product_or_service_code is not null
        and product_or_service_code_description is not null
    qualify row_number() over (
        partition by product_or_service_code
        order by action_date desc nulls last, product_or_service_code_description
    ) = 1

),

-- grain: every naics + psc pair in the data (including null pairs)
t_pairs as (

    select distinct naics_code, product_or_service_code
    from transactions

)

select
    {{ dbt_utils.generate_surrogate_key(
        ['tp.naics_code', 'tp.product_or_service_code']
    ) }} as product_key,
    tp.naics_code,
    n.naics_description,
    tp.product_or_service_code,
    p.product_or_service_code_description,
    -- first character of psc
    -- digit=product, A=R&D, Y/Z=construction, other=services
    case
        when tp.product_or_service_code is null then null
        when left(tp.product_or_service_code, 1) between '1' and '9' then 'Supplies/Equipment'
        when left(tp.product_or_service_code, 1) = 'A' then 'R&D'
        when left(tp.product_or_service_code, 1) in ('Y', 'Z') then 'Construction'
        else 'Services'
    end as psc_portfolio_group
from t_pairs as tp
left join naics as n
    on tp.naics_code = n.naics_code
left join psc as p
    on tp.product_or_service_code = p.product_or_service_code