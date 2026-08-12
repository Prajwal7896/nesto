from pathlib import Path
import pickle
from typing import Any, Dict, List

import faiss
import numpy as np

from backend.api.rag.indexing.embedder import embed_text

BASE_DIR = Path("backend/data/embeddings/index")

FAISS_INDEX_PATH = BASE_DIR / "faiss.index"
METADATA_PATH = BASE_DIR / "faiss_metadata.pkl"


class Retriever:

    def __init__(self) -> None:
        self.index = faiss.read_index(str(FAISS_INDEX_PATH))
        with open(METADATA_PATH, "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query: Any, top_k: int = 8) -> Dict[str, List[str]]:
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

        print("Embedding query:")
        print(query)

        # Generate embedding
        embedding = embed_text(query)

        print("Embedding length:", len(embedding))

        query_vector = np.array(
            [embedding],
            dtype=np.float32,
        )

        print(
            "Query vector shape:",
            query_vector.shape,
        )

        print(
            "FAISS dimension:",
            self.index.d,
        )

        faiss.normalize_L2(query_vector)

        distances, indices = self.index.search(
            query_vector,
            top_k,
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