import os
import json
import pickle
import numpy as np
import faiss
from tqdm import tqdm
from backend.api.rag.indexing.embedder import embed_text
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
    embeddings = []

    for chunk in tqdm(chunks):
        embedding = embed_text(chunk["text"])
        embeddings.append(embedding)

    embeddings = np.array(embeddings, dtype=np.float32)

    faiss.normalize_L2(embeddings)

    return embeddings


# =========================
# BUILD FAISS INDEX
# =========================
def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)  # cosine similarity (normalized)
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
    print("📦 Loading chunks...")
    chunks = load_chunks()

    print("🧠 Creating Gemini embeddings...")
    embeddings = create_embeddings(chunks)

    print("🔍 Building FAISS index...")
    index = build_faiss_index(embeddings)

    print("💾 Saving index...")
    os.makedirs(INDEX_DIR, exist_ok=True)
    os.makedirs(MAPPING_DIR, exist_ok=True)

    save_index(index)
    save_metadata(chunks)

    print("✅ Index build complete!")
    print(f"📁 Saved at: {INDEX_DIR}")


if __name__ == "__main__":
    main()