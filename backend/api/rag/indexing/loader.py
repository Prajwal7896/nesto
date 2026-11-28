import faiss
import os
from backend.api.rag.indexing.embedder import EMBEDDING_DIMENSION

INDEX_PATH = "backend/data/embeddings/index/faiss.index"


def create_index(dim=EMBEDDING_DIMENSION):
    return faiss.IndexFlatIP(dim)


def save_index(index):
    faiss.write_index(index, INDEX_PATH)


def load_index():
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    return None
