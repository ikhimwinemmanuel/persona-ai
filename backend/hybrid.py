
"""Combine FAISS and BM25 retrieval results."""

from retrieval import search_faiss
from bm25 import search_bm25


def reciprocal_rank_fusion(
    rankings: list[list[dict]],
    top_k: int = 3,
    rrf_k: int = 60,
) -> list[dict]:
    """Combine ranked lists without mixing raw scores."""

    if top_k < 1 or rrf_k < 1:
        raise ValueError("top_k and rrf_k must be positive")

    combined_scores = {}

    for results in rankings:
        for rank, result in enumerate(results, start=1):
            index = result["index"]

            combined_scores[index] = (
                combined_scores.get(index, 0.0)
                + 1 / (rrf_k + rank)
            )

    ranked = sorted(
        combined_scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return [
        {"index": index, "score": score}
        for index, score in ranked[:top_k]
    ]


def hybrid_search(
    index,
    chunks: list[dict],
    query_embedding: list[float],
    question: str,
    top_k: int = 3,
) -> list[dict]:
    """Search with FAISS and BM25, then combine results."""

    if top_k < 1:
        raise ValueError("top_k must be positive")

    candidate_k = min(len(chunks), max(top_k, 10))

    semantic_results = search_faiss(
        index, query_embedding, top_k=candidate_k
    )

    keyword_results = search_bm25(
        chunks, question, top_k=candidate_k
    )

    return reciprocal_rank_fusion(
        [semantic_results, keyword_results],
        top_k=top_k,
    )
