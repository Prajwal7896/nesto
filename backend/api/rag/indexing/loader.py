import faiss
import numpy as np
import os

INDEX_PATH = "backend/data/embeddings/index/faiss.index"


def create_index(dim=768):
    return faiss.IndexFlatL2(dim)


def save_index(index):
    faiss.write_index(index, INDEX_PATH)


def load_index():
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    return None
