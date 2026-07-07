from typing import Any


SEVERITY_TERMS = {
    "high": ("breach", "default", "covenant", "litigation", "customer concentration", "going concern"),
    "medium": ("renewal", "termination", "churn", "margin", "debt", "liquidity"),
}


def _severity(text: str) -> str:
    lowered = text.lower()
    for severity, terms in SEVERITY_TERMS.items():
        if any(term in lowered for term in terms):
            return severity
    return "low"


def extract_findings(category: str, contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for context in contexts[:4]:
        content = context.get("content", "")
        if not content:
            continue
        title = content[:96].rstrip(" .,;:")
        findings.append(
            {
                "category": category,
                "severity": _severity(content),
                "title": title,
                "detail": content[:700],
                "source_doc_id": context.get("source_doc_id"),
            }
        )
    return findings


def answer_question(question: str, contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        return "I could not find relevant ingested context for that company yet."

    evidence = "\n".join(
        f"- {context.get('filename', 'document')}: {context.get('content', '')[:280]}"
        for context in contexts[:4]
    )
    return f"Based on the retrieved data-room context for: {question}\n\n{evidence}"
