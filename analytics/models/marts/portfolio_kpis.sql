select
    c.company_id,
    c.name,
    c.sector,
    count(f.finding_id) as total_findings,
    count(*) filter (where f.severity = 'high') as high_severity_findings,
    count(*) filter (where f.severity = 'medium') as medium_severity_findings,
    count(*) filter (where f.severity = 'low') as low_severity_findings
from {{ ref('stg_companies') }} c
left join {{ ref('stg_findings') }} f using (company_id)
group by 1, 2, 3
