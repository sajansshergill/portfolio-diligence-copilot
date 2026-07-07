import json
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.chunking import chunk_text
from app.ingestion.embeddings import embed_text, vector_literal
from app.models import Document


async def ingest_company(session: AsyncSession, company_id: int) -> int:
    """Chunk and embed every uploaded document for a company."""
    result = await session.execute(select(Document).where(Document.company_id == company_id))
    documents = result.scalars().all()

    chunk_count = 0
    for document in documents:
        if not document.storage_path:
            continue

        path = Path(document.storage_path)
        if not path.exists():
            document.status = "failed"
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(content)
        await session.execute(text("DELETE FROM chunks WHERE document_id = :document_id"), {"document_id": document.id})

        for index, chunk in enumerate(chunks):
            await session.execute(
                text(
                    "INSERT INTO chunks (document_id, content, embedding, metadata) "
                    "VALUES (:document_id, :content, :embedding, CAST(:metadata AS jsonb))"
                ),
                {
                    "document_id": document.id,
                    "content": chunk,
                    "embedding": vector_literal(embed_text(chunk)),
                    "metadata": json.dumps({"chunk_index": index, "filename": document.filename}),
                },
            )
            chunk_count += 1

        document.status = "embedded" if chunks else "failed"

    await session.commit()
    return chunk_count
