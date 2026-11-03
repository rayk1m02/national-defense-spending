-- Data quality check for recipient grouping (not used by a model or dashboard).
-- A company split across several group records has its dollars divided, which understates its top 10 rank and CR10 (Concentration ratio for share of total dollars).
-- Lists each group record of $100M+ for the largest families. More than one record per family means rows are missing from seeds/recipient_group_overrides.csv, unless intended (acquisitions inside the window, joint ventures).
-- Rerun after each data refresh, since new parent records can appear.

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