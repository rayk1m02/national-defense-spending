-- grain: one row per flagged award
-- flagged when log size is more than 3 iqrs above q3 of its sub-agency, award type, and product group (groups of 30+ awards)
with awards as (

    select
        contract_award_unique_key,
        award_id_piid,
        parent_award_id_piid,
        start_fiscal_year,
        base_action_date,
        award_type,
        sub_agency_name,
        service_group,
        coalesce(psc_portfolio_group, 'Unknown') as psc_portfolio_group,
        recipient_key,
        obligated,
        ln(obligated::double precision) as log_obligated
    from {{ ref('int_awards') }}
    where obligated > 0

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

overrides as (

    select
        recipient_group_uei,
        corrected_group_name
    from {{ ref('recipient_group_overrides') }}

),

-- quartiles of log size per group. All percentiles sort by log_obligated, as redshift requires
baselines as (

    select
        sub_agency_name,
        award_type,
        psc_portfolio_group,
        count(*) as group_awards,
        percentile_cont(0.25) within group (order by log_obligated) as q1,
        percentile_cont(0.50) within group (order by log_obligated) as q2,
        percentile_cont(0.75) within group (order by log_obligated) as q3
    from awards
    where obligated >= 10000
    group by 1, 2, 3

),

flagged as (

    select
        a.*,
        b.group_awards,
        b.q2,
        b.q3,
        greatest(b.q3 - b.q1, ln(2)) as iqr
    from awards as a
    join baselines as b
        on a.sub_agency_name = b.sub_agency_name
        and a.award_type = b.award_type
        and a.psc_portfolio_group = b.psc_portfolio_group
    where b.group_awards >= 30
        and a.log_obligated > b.q3 + 3 * greatest(b.q3 - b.q1, ln(2))

)

select
    f.contract_award_unique_key,
    f.award_id_piid,
    f.parent_award_id_piid,
    f.start_fiscal_year,
    f.base_action_date,
    f.award_type,
    f.sub_agency_name,
    f.service_group,
    f.psc_portfolio_group,
    r.recipient_name,
    coalesce(
        o.corrected_group_name,
        case when r.recipient_parent_uei is not null then r.recipient_parent_name else r.recipient_name end
    ) as recipient_group_name,
    f.obligated,
    f.group_awards,
    exp(f.q2) as group_median_obligated,
    exp(f.q3) as group_q3_obligated,
    exp(f.q3 + 3 * f.iqr) as outlier_threshold_obligated,
    f.obligated / exp(f.q2) as times_group_median,
    (f.log_obligated - f.q3) / f.iqr as iqr_distance
from flagged as f
left join recipients as r
    on f.recipient_key = r.recipient_key
left join overrides as o
    on coalesce(r.recipient_parent_uei, r.recipient_uei) = o.recipient_group_uei