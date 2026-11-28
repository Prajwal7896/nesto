import hashlib
import json
import os
import pickle
import time
from collections import deque
from pathlib import Path

import faiss
import numpy as np

from .chunker import build_all_chunks
from .embedder import EMBEDDING_DIMENSION, MODEL, embed_text

ROOT_DIR = Path(__file__).resolve().parents[4]
INDEX_DIR = ROOT_DIR / "backend" / "data" / "embeddings" / "index"
CACHE_DIR = ROOT_DIR / "backend" / "data" / "embeddings" / "embeddings_cache" / "rag_builder"

INDEX_FILE = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "faiss_metadata.pkl"
CONFIG_PATH = INDEX_DIR / "index_config.json"
BUILD_MARKER = INDEX_DIR / ".building"

TOKEN_LIMIT = 24000
WINDOW_SECONDS = 60
MAX_RETRIES = 5

request_history = deque()


def estimate_tokens(text):
    return max(1, len(text) // 3)


def wait_for_token_capacity(token_count):
    while True:
        now = time.monotonic()

        while request_history and now - request_history[0][0] >= WINDOW_SECONDS:
            request_history.popleft()

        used_tokens = sum(item[1] for item in request_history)

        if used_tokens + token_count <= TOKEN_LIMIT:
            request_history.append((now, token_count))
            return

        if not request_history:
            return

        wait_seconds = WINDOW_SECONDS - (now - request_history[0][0]) + 1

        print(f"[RATE LIMIT] Waiting {wait_seconds:.1f} seconds...")
        time.sleep(max(1, wait_seconds))


def is_rate_limit_error(error):
    current = error

    while current is not None:
        message = str(current).upper()

        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            return True

        current = current.__cause__

    return False


def get_cache_path(text):
    key = f"{MODEL}:{EMBEDDING_DIMENSION}:{text}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.npy"


def get_embedding(text):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_path = get_cache_path(text)

    if cache_path.exists():
        vector = np.load(cache_path)

        if vector.shape == (EMBEDDING_DIMENSION,) and np.isfinite(vector).all():
            return vector.astype(np.float32)

    tokens = estimate_tokens(text)

    for attempt in range(MAX_RETRIES):
        wait_for_token_capacity(tokens)

        try:
            vector = np.asarray(embed_text(text), dtype=np.float32)

            if vector.shape != (EMBEDDING_DIMENSION,):
                raise ValueError(
                    f"Expected {EMBEDDING_DIMENSION} dimensions, got {vector.shape}"
                )

            if not np.isfinite(vector).all():
                raise ValueError("Embedding contains invalid values.")

            temp_path = cache_path.with_suffix(".tmp.npy")
            np.save(temp_path, vector)
            os.replace(temp_path, cache_path)

            return vector

        except Exception as error:
            if not is_rate_limit_error(error):
                raise

            if attempt == MAX_RETRIES - 1:
                raise

            delay = 35 * (attempt + 1)
            print(
                f"[GEMINI 429] Retry {attempt + 1}/{MAX_RETRIES} "
                f"after {delay} seconds..."
            )
            time.sleep(delay)

    raise RuntimeError("Embedding generation failed.")


def build_faiss_index():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    with open(BUILD_MARKER, "w", encoding="utf-8") as marker:
        marker.write(MODEL)

    try:
        print("[1/4] Loading knowledge chunks...")
        chunks = build_all_chunks()

        if not chunks:
            raise ValueError("No chunks found.")

        print(f"Total chunks: {len(chunks)}")

        embeddings = []

        print("[2/4] Generating embeddings...")

        for index, chunk in enumerate(chunks, start=1):
            vector = get_embedding(chunk["text"])
            embeddings.append(vector)

            print(
                f"\rEmbedded: {index}/{len(chunks)} "
                f"({index * 100 // len(chunks)}%)",
                end="",
                flush=True,
            )

        print("\n[3/4] Creating FAISS index...")

        matrix = np.asarray(embeddings, dtype=np.float32)
        faiss.normalize_L2(matrix)

        index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
        index.add(matrix)

        print("[4/4] Saving index and metadata...")

        temp_index = INDEX_DIR / "faiss.tmp.index"
        temp_metadata = INDEX_DIR / "faiss_metadata.tmp.pkl"
        temp_config = INDEX_DIR / "index_config.tmp.json"

        faiss.write_index(index, str(temp_index))

        with open(temp_metadata, "wb") as file:
            pickle.dump(chunks, file)

        config = {
            "index_type": "IndexFlatIP",
            "metric": "cosine",
            "embedding_provider": "google-genai",
            "model_name": MODEL,
            "dimension": EMBEDDING_DIMENSION,
            "normalize_embeddings": True,
            "total_vectors": int(index.ntotal),
            "unique_sources": len(set(c["source"] for c in chunks)),
            "cached_embeddings": True,
        }

        with open(temp_config, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

        os.replace(temp_index, INDEX_FILE)
        os.replace(temp_metadata, METADATA_PATH)
        os.replace(temp_config, CONFIG_PATH)

        return {
            "status": "success",
            "chunks_indexed": len(chunks),
            "vectors": int(index.ntotal),
            "unique_sources": config["unique_sources"],
        }

    finally:
        if BUILD_MARKER.exists():
            BUILD_MARKER.unlink()


if __name__ == "__main__":
    print(build_faiss_index())
