select
    company_id,
    severity,
    count(*) as finding_count
from {{ ref('stg_findings') }}
group by 1, 2
