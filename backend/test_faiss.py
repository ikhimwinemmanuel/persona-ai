
from retrieval import build_faiss_index, search_faiss
from retrieval import save_faiss_index, load_faiss_index

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





def test_save_and_load_faiss_index(tmp_path):
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    chunks = [
        {"chunk_id": "test:0", "source": "test.txt", "text": "Python"},
        {"chunk_id": "test:1", "source": "test.txt", "text": "AWS"},
    ]

    index = build_faiss_index(embeddings)

    save_faiss_index(index, chunks, str(tmp_path))

    loaded_index, loaded_chunks = load_faiss_index(str(tmp_path))

    assert loaded_index.ntotal == 2
    assert loaded_chunks == chunks

    results = search_faiss(
        loaded_index,
        query_embedding=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert results[0]["index"] == 0
    assert loaded_chunks[results[0]["index"]]["text"] == "Python"
