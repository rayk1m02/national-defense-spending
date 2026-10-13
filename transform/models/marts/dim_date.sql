-- 1950 through 2079 covers real pop/solicitation dates, including 50-year contracts ending in the 2070s
with spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('1950-01-01' as date)",
        end_date="cast('2080-01-01' as date)"
    ) }}

)

select 
    date_day,
    case
        when extract(month from date_day) >= 10 then extract(year from date_day)+1
        else extract(year from date_day)
    end as fiscal_year
from spine