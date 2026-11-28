import os
import json
import numpy as np
import faiss
import pickle

from backend.data.embeddings.utils.logger import get_logger
from backend.api.rag.indexing.embedder import (
    EMBEDDING_DIMENSION,
    MODEL,
    embed_text,
)

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CHUNKS_FILE = os.path.join(BASE_DIR, "chunks", "combined_chunks.jsonl")

INDEX_PATH = os.path.join(BASE_DIR, "index", "faiss.index")
META_PATH = os.path.join(BASE_DIR, "index", "faiss_metadata.pkl")
INDEX_CONFIG_PATH = os.path.join(BASE_DIR, "index", "index_config.json")
BUILD_MARKER = os.path.join(BASE_DIR, "index", ".building")

CACHE_PATH = os.path.join(BASE_DIR, "embeddings_cache", "embeddings.npy")
CACHE_INDEX_PATH = os.path.join(BASE_DIR, "embeddings_cache", "cache_index.json")

logger = get_logger("update_index")


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
# LOAD EXISTING INDEX
# =========================
def load_index():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("FAISS index not found. Run build_index.py first.")

    if os.path.exists(BUILD_MARKER):
        raise RuntimeError("FAISS index rebuild is in progress.")
    with open(INDEX_CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    if (
        config.get("model_name") != MODEL
        or config.get("embedding_provider") != "google-genai"
        or config.get("dimension") != EMBEDDING_DIMENSION
        or config.get("index_type") != "IndexFlatIP"
        or not config.get("normalize_embeddings")
    ):
        raise RuntimeError(
            "Existing index does not use the configured embedding model. "
            "Rebuild it with python -m backend.data.embeddings.build_index."
        )
    index = faiss.read_index(INDEX_PATH)
    if index.d != EMBEDDING_DIMENSION or index.metric_type != faiss.METRIC_INNER_PRODUCT:
        raise RuntimeError("FAISS index metric or dimension is incompatible; rebuild the index.")
    with open(META_PATH, "rb") as metadata_file:
        metadata = pickle.load(metadata_file)
    if index.ntotal != len(metadata) or config.get("total_vectors") != index.ntotal:
        raise RuntimeError("FAISS index and metadata counts do not match; rebuild the index.")
    return index


# =========================
# LOAD CACHE
# =========================
def load_cache():
    embeddings = np.load(CACHE_PATH, allow_pickle=True)

    with open(CACHE_INDEX_PATH, "r", encoding="utf-8") as f:
        cache_index = json.load(f)

    if (
        cache_index.get("model") != MODEL
        or cache_index.get("embedding_dim") != EMBEDDING_DIMENSION
        or embeddings.ndim != 2
        or embeddings.shape[1] != EMBEDDING_DIMENSION
    ):
        raise RuntimeError(
            "Embedding cache is incompatible with the FAISS model. "
            "Rebuild embeddings with python -m backend.data.embeddings.pipeline.embed_chunks."
        )
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
    if model != MODEL:
        raise ValueError(f"Unsupported embedding model: {model}")
    texts = [c["text"] for c in new_chunks]

    embeddings = np.asarray([embed_text(text) for text in texts], dtype=np.float32)
    if embeddings.ndim != 2 or embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(f"Expected {EMBEDDING_DIMENSION}-dimensional {MODEL} embeddings.")
    faiss.normalize_L2(embeddings)
    return embeddings


# =========================
# UPDATE FAISS INDEX
# =========================
def update_index(index, new_embeddings):
    if new_embeddings.ndim != 2 or new_embeddings.shape[1] != index.d:
        raise ValueError("New embeddings do not match the FAISS index dimension.")
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


def update_index_metadata(new_chunks, total_vectors):
    with open(META_PATH, "rb") as metadata_file:
        metadata = pickle.load(metadata_file)
    metadata.extend(new_chunks)
    with open(META_PATH, "wb") as metadata_file:
        pickle.dump(metadata, metadata_file)

    with open(INDEX_CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    config["total_vectors"] = total_vectors
    with open(INDEX_CONFIG_PATH, "w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2)


# =========================
# MAIN
# =========================
def main():
    logger.info(f"Using embedding model {MODEL}...")
    model = load_model()

    logger.info("Loading chunks...")
    all_chunks = load_chunks()

    logger.info("Loading cache...")
    _, cache_index = load_cache()

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

    os.makedirs(os.path.dirname(BUILD_MARKER), exist_ok=True)
    with open(BUILD_MARKER, "w", encoding="utf-8") as marker:
        marker.write(MODEL)
    logger.info("Updating FAISS index...")
    index = update_index(index, new_embeddings)
    save_index(index)
    update_index_metadata(new_chunks, index.ntotal)
    update_cache(cache_index, new_chunks, new_embeddings)
    os.remove(BUILD_MARKER)

    logger.info("Index update completed successfully!")


if __name__ == "__main__":
    main()