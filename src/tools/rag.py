"""
Feature 2 - Retrieval tool over a persisted ChromaDB collection.
The index is built once by scripts/ingest_kb.py and only ever loaded
(never re-embedded) here.
"""
import os

import chromadb
from sentence_transformers import SentenceTransformer

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CHROMA_PATH = os.path.join(_BASE_DIR, "chroma_db")
_COLLECTION_NAME = "electronics_policies"
_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embedder = None
_client = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(_EMBED_MODEL_NAME)
    return _embedder


def _get_collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=_CHROMA_PATH)
    return _client.get_or_create_collection(_COLLECTION_NAME)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """
    Returns top_k chunks: {"text", "source", "chunk_index", "distance"}.
    Returns [] if the collection is empty (index not built yet).
    """
    collection = _get_collection()
    if collection.count() == 0:
        return []

    embedder = _get_embedder()
    query_vec = embedder.encode([query]).tolist()

    results = collection.query(query_embeddings=query_vec, n_results=top_k)

    chunks = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for text, meta, dist in zip(docs, metas, dists):
        chunks.append(
            {
                "text": text,
                "source": meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", -1),
                "distance": dist,
            }
        )
    return chunks
