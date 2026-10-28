-- fails if rpt_recipient_year's awards_started doesn't account for every award in int_awards
with rpt as (

    select sum(awards_started) as awards
    from {{ ref('rpt_recipient_year') }}

),

expected as (

    select count(*) as awards
    from {{ ref('int_awards') }}

)

select *
from rpt
cross join expected
where rpt.awards <> expected.awards