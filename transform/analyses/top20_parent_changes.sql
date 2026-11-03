/**
In analyses/merger_before_after.sql, we use 5 merger families to analyze obligation trends before and after merges. 

This file is the evidence behind those selection of 5 merger families.

data plan question: 

Of the top 20 cumulative recipients, which show a UEI or parent UEI change (proxy for a merger or acquisition restructuring) in the window?
What does their combined obligation trend look like before and after?
*/

-- top 20 groups by greatest obligation from 2017 - 2026
with top_groups as (

    select
        recipient_group_uei,
        recipient_group_name,
        sum(obligated) as obligated
    from {{ ref('rpt_recipient_year') }}
    where fiscal_year >= 2017 and fiscal_year <= 2026
    group by 1, 2
    order by sum(obligated) desc
    limit 20

),

-- all the distinct companies that were under the top 20 groups at any given point
group_recipients as (

    select distinct
        ry.recipient_uei
    from top_groups tg
    join {{ ref('rpt_recipient_year') }} ry on tg.recipient_group_uei = ry.recipient_group_uei

),

-- all the companies that have had a change in parent uei from the group_recipients
changed_uei as (

    select
        recipient_uei
    from {{ ref('rpt_recipient_year') }}  ry
    where ry.recipient_uei in (
        select recipient_uei from group_recipients
    )
    group by recipient_uei
    having count(distinct recipient_group_uei) > 1
    
), 

-- each changed recipient's group next to its previous year's group
history as (

    select
        ry.recipient_uei,
        ry.recipient_name,
        ry.fiscal_year,
        ry.recipient_group_uei,
        ry.recipient_group_name,
        ry.obligated,
        lag(ry.recipient_group_uei) over (
            partition by ry.recipient_uei
            order by ry.fiscal_year
        ) as prev_group_uei,
        lag(ry.recipient_group_name) over (
            partition by ry.recipient_uei
            order by ry.fiscal_year
        ) as prev_group_name
    from {{ ref('rpt_recipient_year') }} as ry
    join changed_uei as cu
        on ry.recipient_uei = cu.recipient_uei

),

-- only the years a recipient switched groups
switches as (

    select *
    from history
    where prev_group_uei is not null
        and recipient_group_uei <> prev_group_uei

)

-- group to group moves, largest first
select
    prev_group_name,
    recipient_group_name as new_group_name,
    fiscal_year,
    count(*) as recipients,
    round(sum(obligated) / 1e9, 2) as obligated_b
from switches
group by 1, 2, 3
order by obligated_b desc