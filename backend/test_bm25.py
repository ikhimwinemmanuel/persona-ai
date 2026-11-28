
from bm25 import search_bm25


def test_bm25_search():
    chunks = [
        {"text": "Emmanuel studied Artificial Intelligence."},
        {"text": "Emmanuel built an AI agent at BILLINI using LangGraph."},
        {"text": "PersonaAI is deployed on AWS Lambda."},
    ]

    results = search_bm25(
        chunks,
        "BILLINI LangGraph",
        top_k=2,
    )

    assert results[0]["index"] == 1
    assert results[0]["score"] > 0


def test_bm25_no_match():
    chunks = [{"text": "Python and AWS"}]

    results = search_bm25(chunks, "elephant")

    assert results == []
