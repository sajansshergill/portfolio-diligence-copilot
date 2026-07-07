from app.agents.llm import answer_question, extract_findings
from app.ingestion.chunking import chunk_text
from app.ingestion.embeddings import EMBEDDING_DIM, embed_text


def test_chunk_text_splits_and_preserves_content():
    text = "Revenue is recurring. " * 200
    chunks = chunk_text(text, max_chars=200, overlap=25)

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    assert "Revenue is recurring" in chunks[0]


def test_embed_text_is_deterministic_and_sized():
    first = embed_text("customer concentration covenant")
    second = embed_text("customer concentration covenant")

    assert first == second
    assert len(first) == EMBEDDING_DIM


def test_extract_findings_keeps_source_citations():
    findings = extract_findings(
        "financial",
        [{"content": "Top customer concentration is 42% of ARR.", "source_doc_id": 7}],
    )

    assert findings[0]["source_doc_id"] == 7
    assert findings[0]["severity"] == "high"


def test_answer_question_handles_empty_context():
    assert "could not find" in answer_question("What are the risks?", []).lower()
