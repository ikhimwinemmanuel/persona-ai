
"""Connect embeddings and hybrid retrieval for PersonaAI."""

from functools import lru_cache
from pathlib import Path

from embeddings import embed_text
from retrieval import load_faiss_index
from hybrid import hybrid_search


INDEX_DIR = Path(__file__).resolve().parent / "index"


@lru_cache(maxsize=1)
def get_knowledge_index():
    """Load the saved knowledge index once per Python process."""
    return load_faiss_index(str(INDEX_DIR))


def retrieve_context(question: str, top_k: int = 3) -> list[dict]:
    """Retrieve relevant professional information."""

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    # Load our existing index and its chunks
    index, chunks = get_knowledge_index()

    # Embed only the visitor's question
    question_embedding = embed_text(question)

    # Search using FAISS and BM25
    results = hybrid_search(
        index,
        chunks,
        question_embedding,
        question,
        top_k=top_k,
    )

    # Attach the original text to each search result
    return [
        {
            "chunk_id": chunks[result["index"]]["chunk_id"],
            "source": chunks[result["index"]]["source"],
            "text": chunks[result["index"]]["text"],
            "score": result["score"],
        }
        for result in results
    ]
