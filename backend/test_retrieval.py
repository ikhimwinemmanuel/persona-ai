
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
