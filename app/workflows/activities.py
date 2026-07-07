from temporalio import activity

from app.agents.graph import run_diligence
from app.db import SessionLocal
from app.ingestion.pipeline import ingest_company
from app.services.diligence import mark_run, persist_findings


@activity.defn
async def ingest_activity(company_id: int) -> int:
    async with SessionLocal() as session:
        return await ingest_company(session, company_id)


@activity.defn
async def analyze_activity(company_id: int, run_id: int) -> list[dict]:
    return run_diligence(company_id, run_id)


@activity.defn
async def persist_findings_activity(run_id: int, company_id: int, findings: list[dict]) -> int:
    return await persist_findings(run_id, company_id, findings)


@activity.defn
async def mark_run_activity(run_id: int, status: str) -> None:
    await mark_run(run_id, status)
