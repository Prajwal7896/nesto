import os
import json
import numpy as np
from tqdm import tqdm

from sentence_transformers import SentenceTransformer

from utils.file_utils import read_jsonl
from utils.logger import get_logger

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
# LOAD MODEL
# =========================
def load_model():
    # Lightweight + fast model (you can replace with OpenAI later)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


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
    texts = [c["text"] for c in chunks]

    logger.info(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # IMPORTANT for cosine similarity
    )

    return embeddings


# =========================
# SAVE CACHE
# =========================
def save_cache(embeddings, chunks):
    np.save(CACHE_FILE, embeddings)

    cache_index = {
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
        logger.error("No chunks found!")
        return

    logger.info(f"Total chunks: {len(chunks)}")

    embeddings = generate_embeddings(model, chunks)

    logger.info("Saving cache...")
    save_cache(embeddings, chunks)

    logger.info("Embedding generation completed successfully!")


if __name__ == "__main__":
    main()