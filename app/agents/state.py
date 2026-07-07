from typing import Any, TypedDict


class DiligenceState(TypedDict, total=False):
    company_id: int
    run_id: int
    route: str
    financial_context: list[dict[str, Any]]
    risk_context: list[dict[str, Any]]
    financial_findings: list[dict[str, Any]]
    risk_findings: list[dict[str, Any]]
    findings: list[dict[str, Any]]
