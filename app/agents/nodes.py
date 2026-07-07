"""LangGraph agent nodes. Each node is a discrete, testable step."""
from app.retrieval.retriever import similar_chunks
from app.agents.llm import extract_findings
from app.agents.state import DiligenceState

FINANCIAL_LENS = "revenue growth margins customer concentration liquidity debt covenants EBITDA cash flow"
RISK_LENS = "contract termination change of control auto-renewal litigation key person compliance breach"


def router_node(state: DiligenceState) -> DiligenceState:
    # A real router could branch by available doc types; here we run the full pass.
    return {"route": "full"}


def retrieval_node(state: DiligenceState) -> DiligenceState:
    cid = state["company_id"]
    return {
        "financial_context": similar_chunks(cid, FINANCIAL_LENS, k=6),
        "risk_context": similar_chunks(cid, RISK_LENS, k=6),
    }


def financial_node(state: DiligenceState) -> DiligenceState:
    return {"financial_findings": extract_findings("financial", state.get("financial_context", []))}


def risk_node(state: DiligenceState) -> DiligenceState:
    return {"risk_findings": extract_findings("legal", state.get("risk_context", []))}


def synthesis_node(state: DiligenceState) -> DiligenceState:
    merged = state.get("financial_findings", []) + state.get("risk_findings", [])
    return {"findings": merged}


def eval_node(state: DiligenceState) -> DiligenceState:
    """Groundedness gate: drop findings with no source document or empty detail."""
    kept = [
        f for f in state.get("findings", [])
        if f.get("source_doc_id") is not None and (f.get("detail") or "").strip()
    ]
    return {"findings": kept}