"""Builds and runs the diligence agent graph:
router -> retrieval -> financial -> risk -> synthesis -> eval
"""
from langgraph.graph import StateGraph, START, END

from app.agents.state import DiligenceState
from app.agents.nodes import (
    router_node,
    retrieval_node,
    financial_node,
    risk_node,
    synthesis_node,
    eval_node,
)


def build_graph():
    g = StateGraph(DiligenceState)
    g.add_node("router", router_node)
    g.add_node("retrieval", retrieval_node)
    g.add_node("financial", financial_node)
    g.add_node("risk", risk_node)
    g.add_node("synthesis", synthesis_node)
    g.add_node("eval", eval_node)

    g.add_edge(START, "router")
    g.add_edge("router", "retrieval")
    g.add_edge("retrieval", "financial")
    g.add_edge("financial", "risk")
    g.add_edge("risk", "synthesis")
    g.add_edge("synthesis", "eval")
    g.add_edge("eval", END)
    return g.compile()


_GRAPH = build_graph()


def run_diligence(company_id: int, run_id: int) -> list[dict]:
    """Run the graph and return the final, evaluated findings."""
    result = _GRAPH.invoke({"company_id": company_id, "run_id": run_id})
    return result.get("findings", [])