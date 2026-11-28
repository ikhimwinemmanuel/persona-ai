
import rag_pipeline


def test_retrieve_context(monkeypatch):
    chunks = [
        {
            "chunk_id": "summary.txt:0",
            "source": "summary.txt",
            "text": "Emmanuel worked at BILLINI.",
        }
    ]

    # Replace real AWS and index operations with test data
    monkeypatch.setattr(
        rag_pipeline,
        "get_knowledge_index",
        lambda: ("fake_index", chunks),
    )

    monkeypatch.setattr(
        rag_pipeline,
        "embed_text",
        lambda question: [0.1, 0.2],
    )

    monkeypatch.setattr(
        rag_pipeline,
        "hybrid_search",
        lambda *args, **kwargs: [
            {"index": 0, "score": 0.0328}
        ],
    )

    results = rag_pipeline.retrieve_context(
        "What did Emmanuel do at BILLINI?"
    )

    assert len(results) == 1
    assert results[0]["source"] == "summary.txt"
    assert results[0]["chunk_id"] == "summary.txt:0"
    assert "BILLINI" in results[0]["text"]
