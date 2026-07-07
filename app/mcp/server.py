"""MCP server exposing the diligence capability as enterprise tools.

Run with:  python -m app.mcp.server
Any MCP client (Claude Desktop, a Slack bot, another app) can then call
`query_company` and `list_findings` without touching the internals.
"""
from mcp.server.fastmcp import FastMCP

from app.sync_db import sync_engine
from app.retrieval.retriever import similar_chunks
from app.agents.llm import answer_question
from sqlalchemy import text

mcp = FastMCP("portfolio-diligence")


@mcp.tool()
def query_company(company_id: int, question: str, k: int = 5) -> str:
    """Answer a question about a portfolio company using its ingested data room."""
    contexts = similar_chunks(company_id, question, k=k)
    return answer_question(question, contexts)


@mcp.tool()
def list_findings(company_id: int) -> list[dict]:
    """List diligence findings recorded for a portfolio company."""
    sql = text(
        "SELECT category, severity, title, detail, source_doc_id "
        "FROM findings WHERE company_id = :cid ORDER BY id DESC"
    )
    with sync_engine.connect() as conn:
        rows = conn.execute(sql, {"cid": company_id}).all()
    return [
        {"category": r[0], "severity": r[1], "title": r[2], "detail": r[3], "source_doc_id": r[4]}
        for r in rows
    ]


if __name__ == "__main__":
    mcp.run()