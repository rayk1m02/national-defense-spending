-- fails if rpt_state_year doesn't match fct_transaction's totals
with rpt as (

    select
        sum(obligated) as obligated,
        sum(transaction_count) as transactions
    from {{ ref('rpt_state_year') }}

),

fct as (

    select
        sum(federal_action_obligation) as obligated,
        count(*) as transactions
    from {{ ref('fct_transaction') }}

)

select *
from rpt
cross join fct
where rpt.obligated <> fct.obligated
    or rpt.transactions <> fct.transactions