
"""BM25 keyword search for PersonaAI."""

import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase searchable words."""
    return re.findall(r"[a-z0-9]+", text.lower())


def search_bm25(
    chunks: list[dict],
    question: str,
    top_k: int = 3,
) -> list[dict]:
    """Rank document chunks using BM25."""

    if top_k < 1:
        raise ValueError("top_k must be positive")

    if not chunks or not question.strip():
        return []

    documents = [tokenize(chunk["text"]) for chunk in chunks]
    query_terms = set(tokenize(question))

    avg_length = sum(len(doc) for doc in documents) / len(documents)
    if avg_length == 0:
        return []

    document_frequency = Counter()
    for doc in documents:
        document_frequency.update(set(doc))

    k1 = 1.5
    b = 0.75
    results = []

    for index, doc in enumerate(documents):
        frequencies = Counter(doc)
        score = 0.0

        for term in query_terms:
            tf = frequencies[term]
            if tf == 0:
                continue

            df = document_frequency[term]
            idf = math.log(
                1 + (len(documents) - df + 0.5) / (df + 0.5)
            )

            denominator = tf + k1 * (
                1 - b + b * len(doc) / avg_length
            )

            score += idf * (tf * (k1 + 1)) / denominator

        if score > 0:
            results.append({
                "index": index,
                "score": score,
            })

    return sorted(
        results,
        key=lambda result: result["score"],
        reverse=True,
    )[:top_k]
