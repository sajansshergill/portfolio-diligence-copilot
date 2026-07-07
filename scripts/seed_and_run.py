import asyncio
from pathlib import Path

from app.agents.graph import run_diligence
from app.db import SessionLocal
from app.ingestion.pipeline import ingest_company
from app.models import Company, DiligenceRun, Document
from app.services.diligence import mark_run, persist_findings


DEMO_MEMO = """
Revenue grew 18% year over year, but gross margin declined due to higher support costs.
The top customer represents 42% of ARR and has a termination for convenience clause.
The credit agreement includes a leverage covenant that tightens next quarter.
Several enterprise contracts auto-renew unless notice is provided 90 days before renewal.
"""


async def main() -> None:
    upload_dir = Path("uploads/demo")
    upload_dir.mkdir(parents=True, exist_ok=True)
    memo_path = upload_dir / "demo-memo.txt"
    memo_path.write_text(DEMO_MEMO.strip(), encoding="utf-8")

    async with SessionLocal() as session:
        company = Company(name="DemoCo", sector="B2B SaaS")
        session.add(company)
        await session.flush()
        document = Document(
            company_id=company.id,
            filename="demo-memo.txt",
            doc_type="board_deck",
            storage_path=str(memo_path),
            status="uploaded",
        )
        session.add(document)
        run = DiligenceRun(company_id=company.id, status="pending")
        session.add(run)
        await session.commit()
        company_id = company.id
        run_id = run.id

    await mark_run(run_id, "running")
    async with SessionLocal() as session:
        chunks = await ingest_company(session, company_id)
    findings = run_diligence(company_id, run_id)
    count = await persist_findings(run_id, company_id, findings)
    await mark_run(run_id, "completed")

    print(f"Seeded DemoCo, embedded {chunks} chunks, persisted {count} findings.")
    for finding in findings:
        print(f"- [{finding['severity']}] {finding['title']}")


if __name__ == "__main__":
    asyncio.run(main())
