
from resources import load_facts, load_summary, load_resume
import json
import faiss
import numpy as np


def format_facts(facts: dict) -> str:
    """Convert structured facts into readable text."""

    lines = []

    for key, value in facts.items():
        label = key.replace("_", " ").title()

        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)

        lines.append(f"{label}: {value}")

    return "\n".join(lines)


def load_documents() -> list[dict]:
    """Load professional knowledge into searchable documents."""

    return [
        {
            "source": "facts.json",
            "text": format_facts(load_facts()),
        },
        {
            "source": "summary.txt",
            "text": load_summary(),
        },
        {
            "source": "Emmanuel_Resume.pdf",
            "text": load_resume(),
        },
    ]


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 120,
    overlap: int = 20,
) -> list[dict]:
    """Split documents into overlapping word-based chunks."""

    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    chunks = []
    step = chunk_size - overlap

    for document in documents:
        words = document["text"].split()

        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]

            chunks.append({
                "source": document["source"],
                "chunk_id": f"{document['source']}:{start}",
                "text": " ".join(chunk_words),
            })

            if start + chunk_size >= len(words):
                break

    return chunks


def build_faiss_index(embeddings: list[list[float]]):
    """Build a FAISS index from document embeddings."""

    vectors = np.asarray(embeddings, dtype=np.float32)

    if vectors.ndim != 2 or len(vectors) == 0:
        raise ValueError("Embeddings must be a non-empty 2D array")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    return index


def search_faiss(index, query_embedding: list[float], top_k: int = 3):
    """Find the most similar document vectors."""

    query = np.asarray([query_embedding], dtype=np.float32)

    scores, indices = index.search(query, top_k)

    return [
        {"index": int(idx), "score": float(score)}
        for idx, score in zip(indices[0], scores[0])
        if idx != -1
    ]
