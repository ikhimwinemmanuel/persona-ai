
import pytest

from hybrid import reciprocal_rank_fusion, hybrid_search
from retrieval import build_faiss_index


def test_reciprocal_rank_fusion():
    semantic = [
        {"index": 0, "score": 0.9},
        {"index": 1, "score": 0.8},
    ]

    keyword = [
        {"index": 1, "score": 10.0},
        {"index": 2, "score": 5.0},
    ]

    results = reciprocal_rank_fusion(
        [semantic, keyword],
        top_k=3,
    )

    assert results[0]["index"] == 1
    assert len(results) == 3


def test_hybrid_search():
    chunks = [
        {"text": "Emmanuel studied Artificial Intelligence"},
        {"text": "BILLINI internship using LangGraph"},
        {"text": "PersonaAI uses AWS Lambda"},
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]

    index = build_faiss_index(embeddings)

    results = hybrid_search(
        index,
        chunks,
        query_embedding=[0.0, 1.0, 0.0],
        question="BILLINI LangGraph",
        top_k=2,
    )

    assert results[0]["index"] == 1


def test_invalid_top_k():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], top_k=0)
