from pathlib import Path
import pickle
import json
import logging
import time
from typing import Any, Dict, List

import faiss
import numpy as np

from backend.api.rag.indexing.embedder import (
    EMBEDDING_DIMENSION,
    MODEL,
    embed_text,
)

BASE_DIR = Path("backend/data/embeddings/index")
logger = logging.getLogger(__name__)

FAISS_INDEX_PATH = BASE_DIR / "faiss.index"
METADATA_PATH = BASE_DIR / "faiss_metadata.pkl"
INDEX_CONFIG_PATH = BASE_DIR / "index_config.json"
BUILD_MARKER = BASE_DIR / ".building"


class Retriever:
    def __init__(self) -> None:
        self.index = None
        self.metadata = None

    def _load_index(self) -> None:
        if self.index is not None:
            return
        started = time.perf_counter()
        if BUILD_MARKER.exists():
            raise RuntimeError("FAISS index rebuild is in progress; retry after it completes.")
        if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
            raise RuntimeError(self._rebuild_message("FAISS index or metadata is missing"))
        if not INDEX_CONFIG_PATH.exists():
            raise RuntimeError(self._rebuild_message("FAISS embedding model is not recorded"))

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
                self._rebuild_message(
                    "FAISS index was built with an incompatible embedding model or configuration"
                )
            )

        index = faiss.read_index(str(FAISS_INDEX_PATH))
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
        if index.d != EMBEDDING_DIMENSION or index.metric_type != faiss.METRIC_INNER_PRODUCT:
            raise RuntimeError(self._rebuild_message("FAISS index dimensions or metric do not match"))
        if index.ntotal != len(metadata) or config.get("total_vectors") != index.ntotal:
            raise RuntimeError(self._rebuild_message("FAISS index and metadata counts do not match"))

        self.index = index
        self.metadata = metadata
        logger.info(
            "stage_timing stage=faiss_index_load seconds=%.6f vectors=%d",
            time.perf_counter() - started,
            index.ntotal,
        )

    @staticmethod
    def _rebuild_message(reason: str) -> str:
        return (
            f"{reason}. Rebuild the index with "
            "'python -m backend.data.embeddings.build_index' before retrieval."
        )

    def search(self, query: Any, top_k: int = 8) -> Dict[str, List[str]]:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")
        self._load_index()

        # Convert Requirements object to text
        if hasattr(query, "project"):
            query = f"""
            Building Type: {query.project.building_type}
            Style: {query.project.style}

            Rooms:
            Living Room: {query.rooms.living_room}
            Bedrooms: {query.rooms.bedrooms}
            Bathrooms: {query.rooms.bathrooms}
            Kitchen: {query.rooms.kitchen}
            Dining Room: {query.rooms.dining_room}

            Special Requirements:
            {', '.join(query.special_requirements)}
            """

        # Convert dictionary to text
        elif isinstance(query, dict):
            query = " ".join(
                f"{k}: {v}" for k, v in query.items()
            )

        # Generate embedding
        embedding_started = time.perf_counter()
        embedding = embed_text(query)
        logger.info(
            "stage_timing stage=query_embedding seconds=%.6f",
            time.perf_counter() - embedding_started,
        )

        query_vector = np.array(
            [embedding],
            dtype=np.float32,
        )
        if query_vector.shape[1] != self.index.d:
            raise RuntimeError("Query embedding dimension does not match the FAISS index.")

        faiss.normalize_L2(query_vector)

        search_started = time.perf_counter()
        _, indices = self.index.search(
            query_vector,
            top_k,
        )
        logger.info(
            "stage_timing stage=faiss_search seconds=%.6f",
            time.perf_counter() - search_started,
        )

        results = []

        for idx in indices[0]:
            if idx == -1:
                continue

            if idx < len(self.metadata):
                results.append(
                    self.metadata[idx]
                )

        return self._post_process(results)

    def _post_process(self, results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        grouped: Dict[str, List[str]] = {
            "room_standards": [],
            "planning_rules": [],
            "structural": [],
            "vastu": [],
            "cost": [],
            "architecture": [],
            "engineering": [],
            "other": [],
        }

        for item in results:
            source = item.get("source", "")
            text = item.get("text", "")

            category = self._detect_category(source)
            grouped[category].append(text)

        return grouped

    def _detect_category(self, source: str) -> str:
        source = source.lower()

        if "room_standards" in source:
            return "room_standards"

        if "planning_rules" in source:
            return "planning_rules"

        if "structural" in source:
            return "structural"

        if "vastu" in source:
            return "vastu"

        if "cost" in source:
            return "cost"

        if "architecture" in source:
            return "architecture"

        if "engineering" in source:
            return "engineering"

        return "other"


# -----------------------------
# Singleton wrapper
# -----------------------------
_retriever = Retriever()


def search(query: Any, top_k: int = 8) -> Dict[str, List[str]]:
    return _retriever.search(query, top_k)
