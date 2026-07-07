select
    id as finding_id,
    run_id,
    company_id,
    category,
    severity,
    title,
    detail,
    source_doc_id,
    created_at
from public.findings
