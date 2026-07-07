import hashlib
import math

EMBEDDING_DIM = 1536


def embed_text(text: str, dimensions: int = EMBEDDING_DIM) -> list[float]:
    """Return a deterministic pseudo-embedding for local/offline runs."""
    values = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dimensions
        values[idx] += 1.0

    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [round(v / norm, 6) for v in values]


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(v) for v in values) + "]"
