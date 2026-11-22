
from resources import load_facts, load_summary, load_resume
import json


def load_documents() -> list[dict]:
    """Load professional knowledge into searchable documents."""

    return [
        {
            "source": "facts.json",
            "text": json.dumps(load_facts(), ensure_ascii=False),
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
