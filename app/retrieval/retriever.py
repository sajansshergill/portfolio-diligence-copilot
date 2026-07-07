import math
import re
from collections import Counter
from typing import Any

from sqlalchemy import text

from app.sync_db import sync_engine


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]+")


def _tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower())


def _score(query: str, content: str) -> float:
    query_counts = Counter(_tokens(query))
    content_counts = Counter(_tokens(content))
    if not query_counts or not content_counts:
        return 0.0

    overlap = sum(min(query_counts[token], content_counts[token]) for token in query_counts)
    return overlap / math.sqrt(sum(content_counts.values()))


def similar_chunks(company_id: int, query: str, k: int = 5) -> list[dict[str, Any]]:
    """Return top chunks using deterministic lexical scoring."""
    sql = text(
        """
        SELECT c.id, c.document_id, c.content, c.metadata, d.filename, d.doc_type
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE d.company_id = :company_id
        """
    )
    with sync_engine.connect() as conn:
        rows = conn.execute(sql, {"company_id": company_id}).mappings().all()

    scored = []
    for row in rows:
        score = _score(query, row["content"])
        if score > 0:
            scored.append(
                {
                    "chunk_id": row["id"],
                    "source_doc_id": row["document_id"],
                    "filename": row["filename"],
                    "doc_type": row["doc_type"],
                    "content": row["content"],
                    "score": round(score, 4),
                    "metadata": row["metadata"] or {},
                }
            )

    return sorted(scored, key=lambda item: item["score"], reverse=True)[:k]
