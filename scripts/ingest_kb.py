
import os

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KB_DIR = os.path.join(_BASE_DIR, "data", "knowledge_base")
_CHROMA_PATH = os.path.join(_BASE_DIR, "chroma_db")
_COLLECTION_NAME = "electronics_policies"
_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_CHUNK_SIZE = 600
_CHUNK_OVERLAP = 100


def load_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if c]


def main():
    print("Loading embedding model...")
    embedder = SentenceTransformer(_EMBED_MODEL_NAME)

    client = chromadb.PersistentClient(path=_CHROMA_PATH)
    try:
        client.delete_collection(_COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(_COLLECTION_NAME)

    files = sorted(os.listdir(_KB_DIR))
    if len(files) < 5:
        print(f"Warning: only {len(files)} files found in {_KB_DIR}, assignment requires >= 5.")

    all_ids, all_docs, all_metas = [], [], []
    for filename in files:
        path = os.path.join(_KB_DIR, filename)
        if not os.path.isfile(path):
            continue
        text = load_text(path)
        chunks = chunk_text(text, _CHUNK_SIZE, _CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            all_ids.append(f"{filename}::{i}")
            all_docs.append(chunk)
            all_metas.append({"source": filename, "chunk_index": i})
        print(f"  {filename}: {len(chunks)} chunks")

    print(f"Embedding {len(all_docs)} chunks...")
    embeddings = embedder.encode(all_docs).tolist()

    collection.add(ids=all_ids, documents=all_docs, metadatas=all_metas, embeddings=embeddings)
    print(f"Done. Collection '{_COLLECTION_NAME}' now has {collection.count()} chunks, "
          f"persisted at {_CHROMA_PATH}")


if __name__ == "__main__":
    main()
