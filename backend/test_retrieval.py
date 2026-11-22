
from retrieval import load_documents


def test_load_documents():
    documents = load_documents()

    assert len(documents) == 3

    expected_sources = {
        "facts.json",
        "summary.txt",
        "Emmanuel_Resume.pdf",
    }

    assert {doc["source"] for doc in documents} == expected_sources

    assert all(doc["text"].strip() for doc in documents)


from retrieval import chunk_documents


def test_chunk_documents():
    documents = [{
        "source": "test.txt",
        "text": " ".join(f"word{i}" for i in range(250)),
    }]

    chunks = chunk_documents(documents)

    assert len(chunks) == 3

    assert all(
        len(chunk["text"].split()) <= 120
        for chunk in chunks
    )

    assert all(
        chunk["source"] == "test.txt"
        for chunk in chunks
    )

    first = chunks[0]["text"].split()
    second = chunks[1]["text"].split()

    assert first[-20:] == second[:20]
