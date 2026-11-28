import os
import json
import numpy as np
import faiss
from backend.api.rag.indexing.embedder import (
    EMBEDDING_DIMENSION,
    MODEL,
    embed_text,
)

from backend.data.embeddings.utils.logger import get_logger

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CHUNKS_FILE = os.path.join(BASE_DIR, "chunks", "combined_chunks.jsonl")
CACHE_DIR = os.path.join(BASE_DIR, "embeddings_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "embeddings.npy")
CACHE_INDEX_FILE = os.path.join(CACHE_DIR, "cache_index.json")

os.makedirs(CACHE_DIR, exist_ok=True)

logger = get_logger("embed_chunks")


# =========================
# EMBEDDING MODEL
# =========================
def load_model():
    return MODEL


# =========================
# LOAD CHUNKS
# =========================
def load_chunks():
    chunks = []

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line.strip()))

    return chunks


# =========================
# GENERATE EMBEDDINGS
# =========================
def generate_embeddings(model, chunks):
    if model != MODEL:
        raise ValueError(f"Unsupported embedding model: {model}")
    texts = [c["text"] for c in chunks]

    logger.info(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = np.asarray([embed_text(text) for text in texts], dtype=np.float32)
    if embeddings.ndim != 2 or embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION}-dimensional {MODEL} embeddings."
        )
    faiss.normalize_L2(embeddings)
    return embeddings


# =========================
# SAVE CACHE
# =========================
def save_cache(embeddings, chunks):
    np.save(CACHE_FILE, embeddings)

    cache_index = {
        "model": MODEL,
        "total_chunks": len(chunks),
        "embedding_dim": embeddings.shape[1],
        "mapping": [
            {
                "id": c["id"],
                "source": c["source"],
                "text": c["text"]
            }
            for c in chunks
        ]
    }

    with open(CACHE_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_index, f, indent=2)

    logger.info(f"Saved embeddings → {CACHE_FILE}")
    logger.info(f"Saved cache index → {CACHE_INDEX_FILE}")


# =========================
# MAIN PIPELINE
# =========================
def main():
    logger.info("Loading embedding model...")
    model = load_model()

    logger.info("Loading chunks...")
    chunks = load_chunks()

    if not chunks:
        raise ValueError(f"No chunks found in {CHUNKS_FILE}")

    logger.info(f"Total chunks: {len(chunks)}")

    embeddings = generate_embeddings(model, chunks)

    logger.info("Saving cache...")
    save_cache(embeddings, chunks)

    logger.info("Embedding generation completed successfully!")


if __name__ == "__main__":
    main()