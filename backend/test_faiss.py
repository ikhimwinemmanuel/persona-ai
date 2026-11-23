
from retrieval import build_faiss_index, search_faiss


def test_faiss_search():
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]

    index = build_faiss_index(embeddings)

    results = search_faiss(
        index,
        query_embedding=[1.0, 0.0, 0.0],
        top_k=2,
    )

    assert index.ntotal == 3
    assert results[0]["index"] == 0
    assert results[0]["score"] == 1.0
    assert len(results) == 2
