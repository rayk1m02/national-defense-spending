-- grain: one row per start fiscal year, award type
-- medians and size vs length correlation. Not additive, so they're computed at this level only
with awards as (

    select
        start_fiscal_year,
        award_type,
        obligated,
        duration_days
    from {{ ref('int_awards') }}

),

-- redshift requires all median() calls in one query to sort by the same column, so one cte per median
size_median as (

    select
        start_fiscal_year,
        award_type,
        count(*) as award_count,
        median(obligated) as median_obligated
    from awards
    group by 1, 2

),

length_median as (

    select
        start_fiscal_year,
        award_type,
        median(duration_days) as median_duration_days
    from awards
    group by 1, 2

),

-- pearson correlation on log size and log (length + 1), positive size and known length only
correlation_inputs as (

    select
        start_fiscal_year,
        award_type,
        ln(obligated::double precision) as x,
        ln(duration_days::double precision + 1) as y
    from awards
    where obligated > 0
        and duration_days is not null

),

correlation as (

    select
        start_fiscal_year,
        award_type,
        count(*) as correlation_awards,
        (count(*) * sum(x * y) - sum(x) * sum(y))
            / nullif(
                sqrt(
                    (count(*) * sum(x * x) - sum(x) * sum(x))
                    * (count(*) * sum(y * y) - sum(y) * sum(y))
                ),
                0
            ) as size_length_correlation
    from correlation_inputs
    group by 1, 2

)

select
    sm.start_fiscal_year,
    sm.award_type,
    sm.award_count,
    sm.median_obligated,
    lm.median_duration_days,
    c.size_length_correlation,
    c.correlation_awards
from size_median as sm
left join length_median as lm
    on sm.start_fiscal_year = lm.start_fiscal_year
    and sm.award_type = lm.award_type
left join correlation as c
    on sm.start_fiscal_year = c.start_fiscal_year
    and sm.award_type = c.award_type