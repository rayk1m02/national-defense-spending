-- grain: one row per start fiscal year, award type, service group, size bucket, length bucket
with awards as (

    select
        start_fiscal_year,
        award_type,
        service_group,
        obligated,
        duration_days
    from {{ ref('int_awards') }}

),

bucketed as (

    select
        start_fiscal_year,
        award_type,
        service_group,
        obligated,
        duration_days,
        case
            when obligated <= 0 then 'Zero or negative'
            when obligated < 10000 then 'Under $10K'
            when obligated < 250000 then '$10K to $250K'
            when obligated < 1000000 then '$250K to $1M'
            when obligated < 10000000 then '$1M to $10M'
            when obligated < 100000000 then '$10M to $100M'
            when obligated < 1000000000 then '$100M to $1B'
            else '$1B and up'
        end as size_bucket,
        case
            when obligated <= 0 then 1
            when obligated < 10000 then 2
            when obligated < 250000 then 3
            when obligated < 1000000 then 4
            when obligated < 10000000 then 5
            when obligated < 100000000 then 6
            when obligated < 1000000000 then 7
            else 8
        end as size_bucket_order,
        case
            when duration_days is null then 'Unknown'
            when duration_days < 30 then 'Under 1 month'
            when duration_days < 183 then '1 to 6 months'
            when duration_days < 365 then '6 to 12 months'
            when duration_days < 730 then '1 to 2 years'
            when duration_days < 1826 then '2 to 5 years'
            else '5 years and up'
        end as length_bucket,
        case
            when duration_days is null then 7
            when duration_days < 30 then 1
            when duration_days < 183 then 2
            when duration_days < 365 then 3
            when duration_days < 730 then 4
            when duration_days < 1826 then 5
            else 6
        end as length_bucket_order
    from awards

)

select
    start_fiscal_year,
    award_type,
    service_group,
    size_bucket,
    size_bucket_order,
    length_bucket,
    length_bucket_order,
    count(*) as award_count,
    sum(obligated) as obligated,
    sum(duration_days) as duration_days_total,
    count(duration_days) as awards_with_duration,
    min(obligated) as min_obligated,
    max(obligated) as max_obligated,
    min(duration_days) as min_duration_days,
    max(duration_days) as max_duration_days
from bucketed
group by 1, 2, 3, 4, 5, 6, 7