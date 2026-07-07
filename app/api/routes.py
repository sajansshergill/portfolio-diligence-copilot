from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm import answer_question
from app.config import settings
from app.db import get_session
from app.models import Company, DiligenceRun, Document, Finding
from app.retrieval.retriever import similar_chunks
from app.schemas import CompanyCreate, CompanyRead, DocumentRead, FindingRead, QueryRequest, QueryResponse, RunRead
from app.services.diligence import run_local_diligence

router = APIRouter()


@router.post("/companies", response_model=CompanyRead)
async def create_company(payload: CompanyCreate, session: AsyncSession = Depends(get_session)):
    company = Company(name=payload.name, sector=payload.sector)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


@router.get("/companies", response_model=list[CompanyRead])
async def list_companies(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Company).order_by(Company.created_at.desc()))
    return result.scalars().all()


@router.get("/companies/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int, session: AsyncSession = Depends(get_session)):
    company = await session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/companies/{company_id}/documents", response_model=DocumentRead)
async def upload_document(
    company_id: int,
    file: UploadFile = File(...),
    doc_type: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    if not await session.get(Company, company_id):
        raise HTTPException(status_code=404, detail="Company not found")

    company_dir = Path(settings.upload_dir) / str(company_id)
    company_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}-{Path(file.filename or 'document.txt').name}"
    path = company_dir / filename
    path.write_bytes(await file.read())

    document = Document(
        company_id=company_id,
        filename=file.filename or filename,
        doc_type=doc_type or "other",
        storage_path=str(path),
        status="uploaded",
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@router.get("/companies/{company_id}/documents", response_model=list[DocumentRead])
async def list_documents(company_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Document).where(Document.company_id == company_id).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.post("/companies/{company_id}/query", response_model=QueryResponse)
async def query_company(company_id: int, payload: QueryRequest):
    contexts = similar_chunks(company_id, payload.question, k=payload.k)
    return QueryResponse(answer=answer_question(payload.question, contexts), contexts=contexts)


@router.post("/companies/{company_id}/runs", response_model=RunRead)
async def create_run(company_id: int, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    if not await session.get(Company, company_id):
        raise HTTPException(status_code=404, detail="Company not found")

    run = DiligenceRun(company_id=company_id, status="pending")
    session.add(run)
    await session.commit()
    await session.refresh(run)

    if settings.use_temporal:
        from temporalio.client import Client

        from app.workflows.diligence_workflow import DiligenceWorkflow

        workflow_id = f"diligence-{company_id}-{run.id}"
        client = await Client.connect(settings.temporal_address)
        await client.start_workflow(
            DiligenceWorkflow.run,
            args=[company_id, run.id],
            id=workflow_id,
            task_queue=settings.temporal_task_queue,
        )
        run.temporal_workflow_id = workflow_id
        await session.commit()
        await session.refresh(run)
    else:
        background_tasks.add_task(run_local_diligence, company_id, run.id)
    return run


@router.get("/companies/{company_id}/runs", response_model=list[RunRead])
async def list_runs(company_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(DiligenceRun).where(DiligenceRun.company_id == company_id).order_by(DiligenceRun.id.desc())
    )
    return result.scalars().all()


@router.get("/runs/{run_id}", response_model=RunRead)
async def get_run(run_id: int, session: AsyncSession = Depends(get_session)):
    run = await session.get(DiligenceRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/companies/{company_id}/findings", response_model=list[FindingRead])
async def list_findings(company_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Finding).where(Finding.company_id == company_id).order_by(Finding.id.desc()))
    return result.scalars().all()
