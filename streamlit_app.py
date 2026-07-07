from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import streamlit as st

from app.agents.llm import answer_question, extract_findings
from app.ingestion.chunking import chunk_text


@dataclass
class UploadedContext:
    filename: str
    doc_type: str
    content: str
    chunks: list[str]


def score(query: str, content: str) -> int:
    query_terms = Counter(query.lower().split())
    content_terms = Counter(content.lower().split())
    return sum(min(query_terms[term], content_terms[term]) for term in query_terms)


def retrieve_contexts(documents: list[UploadedContext], query: str, k: int = 5) -> list[dict]:
    contexts: list[dict] = []
    for doc_id, document in enumerate(documents, start=1):
        for chunk_id, chunk in enumerate(document.chunks, start=1):
            contexts.append(
                {
                    "chunk_id": chunk_id,
                    "source_doc_id": doc_id,
                    "filename": document.filename,
                    "doc_type": document.doc_type,
                    "content": chunk,
                    "score": score(query, chunk),
                }
            )

    return sorted(contexts, key=lambda item: item["score"], reverse=True)[:k]


st.set_page_config(page_title="Portfolio Diligence Copilot", page_icon="PDC", layout="wide")

st.title("Portfolio Diligence Copilot")
st.caption("Streamlit-hosted demo: upload company documents, run an offline diligence pass, and ask questions.")

with st.sidebar:
    company_name = st.text_input("Company name", value="DemoCo")
    sector = st.text_input("Sector", value="B2B SaaS")
    doc_type = st.selectbox("Document type", ["financials", "contract", "board_deck", "other"])
    uploads = st.file_uploader(
        "Upload data-room files",
        type=["txt", "md", "csv"],
        accept_multiple_files=True,
        help="The Streamlit demo reads text-like files directly in memory.",
    )

documents: list[UploadedContext] = []
for upload in uploads:
    text = upload.getvalue().decode("utf-8", errors="ignore")
    documents.append(
        UploadedContext(
            filename=upload.name,
            doc_type=doc_type,
            content=text,
            chunks=chunk_text(text),
        )
    )

left, right = st.columns([0.42, 0.58], gap="large")

with left:
    st.subheader("Portfolio Company")
    st.metric("Company", company_name)
    st.metric("Sector", sector)
    st.metric("Uploaded documents", len(documents))
    st.metric("Chunks indexed", sum(len(document.chunks) for document in documents))

    st.subheader("Run Diligence")
    run_clicked = st.button("Run diligence", type="primary", disabled=not documents)
    if not documents:
        st.info("Upload at least one text-like document to run the demo.")

with right:
    st.subheader("Source-Cited Findings")
    if run_clicked:
        financial_context = retrieve_contexts(
            documents,
            "revenue growth margins customer concentration liquidity debt covenants EBITDA cash flow",
            k=6,
        )
        risk_context = retrieve_contexts(
            documents,
            "contract termination change of control auto-renewal litigation key person compliance breach",
            k=6,
        )
        findings = extract_findings("financial", financial_context) + extract_findings("legal", risk_context)
        findings = [finding for finding in findings if finding.get("source_doc_id") is not None]
        st.session_state["findings"] = findings

    findings = st.session_state.get("findings", [])
    if findings:
        for finding in findings:
            with st.container(border=True):
                st.markdown(f"**{finding['severity'].upper()} · {finding['category']}**")
                st.write(finding["title"])
                st.caption(f"Source document id: {finding['source_doc_id']}")
                st.write(finding["detail"])
    else:
        st.write("No findings yet.")

st.divider()
st.subheader("Ask the Data Room")
question = st.text_input("Question", placeholder="Where are the biggest diligence risks?")
if st.button("Ask", disabled=not documents or not question):
    contexts = retrieve_contexts(documents, question, k=5)
    st.write(answer_question(question, contexts))
    with st.expander("Retrieved context"):
        for context in contexts:
            st.markdown(f"**{context['filename']}** · score `{context['score']}`")
            st.write(context["content"][:800])
