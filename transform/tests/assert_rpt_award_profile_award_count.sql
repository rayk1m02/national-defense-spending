-- fails if rpt_award_profile doesn't count each in-window award exactly once
with profile as (

    select sum(award_count) as awards
    from {{ ref('rpt_award_profile') }}

),

expected as (

    select count(distinct f.contract_award_unique_key) as awards
    from {{ ref('fct_transaction') }} as f
    join {{ ref('dim_award') }} as a
        on f.award_key = a.award_key
    where a.award_or_idv_flag = 'AWARD'
        and f.modification_number = '0'

)

select *
from profile
cross join expected
where profile.awards <> expected.awards