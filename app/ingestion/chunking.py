import re


def chunk_text(text: str, max_chars: int = 1_200, overlap: int = 160) -> list[str]:
    """Split text into stable, overlapping chunks without external parsers."""
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(". ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary + 1
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        start = max(0, end - overlap)
    return chunks
