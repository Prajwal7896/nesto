import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from utils.logger import get_logger
from utils.file_utils import read_jsonl

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CHUNKS_FILE = os.path.join(BASE_DIR, "chunks", "combined_chunks.jsonl")

INDEX_PATH = os.path.join(BASE_DIR, "index", "faiss.index")
META_PATH = os.path.join(BASE_DIR, "index", "faiss_metadata.pkl")

CACHE_PATH = os.path.join(BASE_DIR, "embeddings_cache", "embeddings.npy")
CACHE_INDEX_PATH = os.path.join(BASE_DIR, "embeddings_cache", "cache_index.json")

logger = get_logger("update_index")


# =========================
# LOAD MODEL
# =========================
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


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
# LOAD EXISTING INDEX
# =========================
def load_index():
    if not os.path.exists(INDEX_PATH):
        raise Exception("FAISS index not found. Run build_index.py first.")

    index = faiss.read_index(INDEX_PATH)
    return index


# =========================
# LOAD CACHE
# =========================
def load_cache():
    embeddings = np.load(CACHE_PATH, allow_pickle=True)

    with open(CACHE_INDEX_PATH, "r", encoding="utf-8") as f:
        cache_index = json.load(f)

    return embeddings, cache_index


# =========================
# GET NEW CHUNKS ONLY
# =========================
def get_new_chunks(existing_cache, all_chunks):
    existing_ids = set([item["id"] for item in existing_cache["mapping"]])

    new_chunks = [c for c in all_chunks if c["id"] not in existing_ids]

    return new_chunks


# =========================
# EMBED NEW CHUNKS
# =========================
def embed_new_chunks(model, new_chunks):
    texts = [c["text"] for c in new_chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings


# =========================
# UPDATE FAISS INDEX
# =========================
def update_index(index, new_embeddings):
    index.add(new_embeddings)
    return index


# =========================
# UPDATE CACHE FILE
# =========================
def update_cache(existing_cache, new_chunks, new_embeddings):
    existing_cache["total_chunks"] += len(new_chunks)

    for c in new_chunks:
        existing_cache["mapping"].append({
            "id": c["id"],
            "source": c["source"],
            "text": c["text"]
        })

    np.save(CACHE_PATH, np.vstack([np.load(CACHE_PATH), new_embeddings]))

    with open(CACHE_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_cache, f, indent=2)


# =========================
# SAVE INDEX
# =========================
def save_index(index):
    faiss.write_index(index, INDEX_PATH)


# =========================
# MAIN
# =========================
def main():
    logger.info("Loading model...")
    model = load_model()

    logger.info("Loading chunks...")
    all_chunks = load_chunks()

    logger.info("Loading cache...")
    embeddings, cache_index = load_cache()

    logger.info("Detecting new chunks...")
    new_chunks = get_new_chunks(cache_index, all_chunks)

    if not new_chunks:
        logger.info("No new chunks found. Index is up to date.")
        return

    logger.info(f"New chunks found: {len(new_chunks)}")

    logger.info("Loading FAISS index...")
    index = load_index()

    logger.info("Embedding new chunks...")
    new_embeddings = embed_new_chunks(model, new_chunks)

    logger.info("Updating FAISS index...")
    index = update_index(index, new_embeddings)

    logger.info("Saving index...")
    save_index(index)

    logger.info("Updating cache...")
    update_cache(cache_index, new_chunks, new_embeddings)

    logger.info("Index update completed successfully!")


if __name__ == "__main__":
    main()