-- Group records of $100M+ for the largest families. 
-- A family with more than one record (other than intended separate ones: acquisitions inside the window, joint ventures) needs rows in seeds/recipient_group_overrides.csv. 
-- Rerun after each data refresh.

select
    recipient_group_uei,
    recipient_group_name,
    min(fiscal_year) as first_fy,
    max(fiscal_year) as last_fy,
    round(sum(obligated) / 1e9, 2) as obligated_b,
    min(group_rank_in_year) as best_rank_in_a_year
from {{ ref('rpt_recipient_year') }}
where fiscal_year between 2017 and 2026
  and (   upper(recipient_group_name) like '%LOCKHEED%'
       or upper(recipient_group_name) like '%NORTHROP%'
       or upper(recipient_group_name) like '%BOEING%'
       or upper(recipient_group_name) like '%GENERAL DYNAMICS%'
       or upper(recipient_group_name) like '%BATH IRON%'
       or upper(recipient_group_name) like '%HONEYWELL%'
       or upper(recipient_group_name) like '%RESIDEO%'
       or upper(recipient_group_name) like '%L3HARRIS%'
       or upper(recipient_group_name) like '%RTX%'
       or upper(recipient_group_name) like '%RAYTHEON%')
group by 1, 2
having sum(obligated) >= 0.1e9
order by 2, 5 desc