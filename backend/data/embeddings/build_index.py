import os
import json
import pickle
import numpy as np
import faiss
from tqdm import tqdm
from backend.api.rag.indexing.embedder import (
    EMBEDDING_DIMENSION,
    MODEL,
    embed_text,
)
# =========================
# CONFIG PATHS
# =========================
BASE_DIR = os.path.dirname(__file__)

CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
INDEX_DIR = os.path.join(BASE_DIR, "index")
MAPPING_DIR = os.path.join(BASE_DIR, "mapping")
CACHE_DIR = os.path.join(BASE_DIR, "embeddings_cache")

INDEX_FILE = os.path.join(INDEX_DIR, "faiss.index")
META_FILE = os.path.join(INDEX_DIR, "faiss_metadata.pkl")
INDEX_CONFIG_FILE = os.path.join(INDEX_DIR, "index_config.json")
BUILD_MARKER = os.path.join(INDEX_DIR, ".building")

# =========================
# READ JSONL FILES
# =========================
def load_chunks():
    data = []

    for file in os.listdir(CHUNKS_DIR):
        if not file.endswith(".jsonl"):
            continue

        path = os.path.join(CHUNKS_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line.strip())

                data.append({
                    "id": item.get("id"),
                    "text": item.get("text"),
                    "source": item.get("source"),
                    "metadata": item.get("metadata", {})
                })

    return data


# =========================
# BUILD EMBEDDINGS
# =========================
def create_embeddings(chunks):
    if not chunks:
        raise ValueError("No chunks found; refusing to build an empty FAISS index.")

    embeddings = []

    for chunk in tqdm(chunks):
        embedding = embed_text(chunk["text"])
        embeddings.append(embedding)

    embeddings = np.array(embeddings, dtype=np.float32)
    if embeddings.ndim != 2 or embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION}-dimensional {MODEL} embeddings."
        )

    faiss.normalize_L2(embeddings)

    return embeddings


# =========================
# BUILD FAISS INDEX
# =========================
def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index


# =========================
# SAVE METADATA
# =========================
def save_metadata(chunks):
    with open(META_FILE, "wb") as f:
        pickle.dump(chunks, f)


# =========================
# SAVE INDEX
# =========================
def save_index(index):
    faiss.write_index(index, INDEX_FILE)


# =========================
# MAIN PIPELINE
# =========================
def main():
    os.makedirs(INDEX_DIR, exist_ok=True)
    with open(BUILD_MARKER, "w", encoding="utf-8") as marker:
        marker.write(MODEL)

    print("📦 Loading chunks...")
    chunks = load_chunks()

    print(f"🧠 Creating {MODEL} embeddings...")
    embeddings = create_embeddings(chunks)

    print("🔍 Building FAISS index...")
    index = build_faiss_index(embeddings)

    print("💾 Saving index...")
    os.makedirs(MAPPING_DIR, exist_ok=True)

    save_index(index)
    save_metadata(chunks)
    with open(INDEX_CONFIG_FILE, "w", encoding="utf-8") as config_file:
        json.dump({
            "index_type": "IndexFlatIP",
            "metric": "cosine",
            "embedding_provider": "google-genai",
            "model_name": MODEL,
            "dimension": int(embeddings.shape[1]),
            "normalize_embeddings": True,
            "total_vectors": int(index.ntotal),
        }, config_file, indent=2)
    os.remove(BUILD_MARKER)

    print("✅ Index build complete!")
    print(f"📁 Saved at: {INDEX_DIR}")


if __name__ == "__main__":
    main()