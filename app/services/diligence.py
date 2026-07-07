from datetime import UTC, datetime

from sqlalchemy import select

from app.agents.graph import run_diligence
from app.db import SessionLocal
from app.ingestion.pipeline import ingest_company
from app.models import DiligenceRun, Finding


async def persist_findings(run_id: int, company_id: int, findings: list[dict]) -> int:
    async with SessionLocal() as session:
        for finding in findings:
            session.add(
                Finding(
                    run_id=run_id,
                    company_id=company_id,
                    category=finding.get("category"),
                    severity=finding.get("severity"),
                    title=finding.get("title") or "Untitled finding",
                    detail=finding.get("detail"),
                    source_doc_id=finding.get("source_doc_id"),
                )
            )
        await session.commit()
        return len(findings)


async def mark_run(run_id: int, status: str) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(DiligenceRun).where(DiligenceRun.id == run_id))
        run = result.scalar_one()
        run.status = status
        if status == "running":
            run.started_at = datetime.now(UTC)
        if status in {"completed", "failed"}:
            run.finished_at = datetime.now(UTC)
        await session.commit()


async def run_local_diligence(company_id: int, run_id: int) -> int:
    await mark_run(run_id, "running")
    try:
        async with SessionLocal() as session:
            await ingest_company(session, company_id)
        findings = run_diligence(company_id, run_id)
        count = await persist_findings(run_id, company_id, findings)
        await mark_run(run_id, "completed")
        return count
    except Exception:
        await mark_run(run_id, "failed")
        raise
