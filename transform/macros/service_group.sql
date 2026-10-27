{% macro service_group(agency_code, sub_agency_name, awarding_office_code) %}
    case
        when {{ agency_code }} = '097' and {{ sub_agency_name }} = 'Department of the Army' then 'Army'
        when {{ agency_code }} = '097' and {{ sub_agency_name }} = 'Department of the Navy' then 'Navy'
        when {{ agency_code }} = '097' and {{ sub_agency_name }} = 'Department of the Air Force' then 'Air Force'
        when {{ agency_code }} = '097' then 'Defense-Wide'
        when {{ agency_code }} = '089' and {{ awarding_office_code }} in ('892330', '892331', '892332') then 'DOE NNSA'
        when {{ agency_code }} = '089' then 'DOE EM'
        when {{ agency_code }} = '070' then 'DHS CISA'
        when {{ agency_code }} = '069' then 'DOT MARAD'
    end
{% endmacro %}