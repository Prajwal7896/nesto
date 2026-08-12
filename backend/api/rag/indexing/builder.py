import numpy as np
from .chunker import build_all_chunks
from .embedder import embed_text
from .loader import create_index, save_index


def build_faiss_index():
    chunks = build_all_chunks()
    embeddings = []
    metadata = []

    for chunk in chunks:
        vector = embed_text(chunk["text"])
        embeddings.append(vector)
        metadata.append(chunk)

    embeddings = np.array(embeddings).astype("float32")
    index = create_index(dim=len(embeddings[0]))
    index.add(embeddings)
    save_index(index)

    return {
        "status": "success",
        "chunks_indexed": len(chunks)
    }