from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    sector: str | None = None


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sector: str | None
    created_at: datetime


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    filename: str
    doc_type: str | None
    status: str
    created_at: datetime


class QueryRequest(BaseModel):
    question: str
    k: int = 5


class QueryResponse(BaseModel):
    answer: str
    contexts: list[dict]


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    status: str
    temporal_workflow_id: str | None
    started_at: datetime | None
    finished_at: datetime | None


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    company_id: int
    category: str | None
    severity: str | None
    title: str
    detail: str | None
    source_doc_id: int | None
    created_at: datetime
