import json
import logging
import math
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from google import genai

ROOT_DIR = Path(__file__).resolve().parents[4]
load_dotenv(ROOT_DIR / ".env")

MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 3072

_client = None
logger = logging.getLogger(__name__)


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                f"GEMINI_API_KEY is missing. Check your .env file at {ROOT_DIR / '.env'}"
            )

        try:
            _client = genai.Client(api_key=api_key)
        except Exception as error:
            raise RuntimeError(
                "Unable to initialize the Gemini embedding client."
            ) from error

    return _client


def embed_text(text: Any) -> List[float]:
    if isinstance(text, dict):
        text = json.dumps(text, sort_keys=True, ensure_ascii=False)
    elif not isinstance(text, str):
        text = str(text)

    if not text.strip():
        raise ValueError("Cannot embed empty text.")

    # Cached values are immutable tuples; callers receive their own list.
    return list(_embed_text_cached(text))


@lru_cache(maxsize=128)
def _embed_text_cached(text: str) -> tuple[float, ...]:
    started = time.perf_counter()

    try:
        response = _get_client().models.embed_content(
            model=MODEL,
            contents=text,
            config={"output_dimensionality": EMBEDDING_DIMENSION},
        )
    except Exception as error:
        raise RuntimeError(
            f"Embedding request failed for model {MODEL}."
        ) from error
    finally:
        logger.info(
            "stage_timing stage=embedding_provider seconds=%.6f",
            time.perf_counter() - started,
        )

    if not response.embeddings:
        raise RuntimeError(f"Embedding model {MODEL} returned no embeddings.")

    values = response.embeddings[0].values

    if not values:
        raise RuntimeError(f"Embedding model {MODEL} returned an empty vector.")

    vector = [float(value) for value in values]

    if len(vector) != EMBEDDING_DIMENSION:
        raise RuntimeError(
            f"Embedding model {MODEL} returned {len(vector)} dimensions; "
            f"expected {EMBEDDING_DIMENSION}."
        )

    if not all(math.isfinite(value) for value in vector):
        raise RuntimeError(f"Embedding model {MODEL} returned non-finite values.")

    return tuple(vector)
