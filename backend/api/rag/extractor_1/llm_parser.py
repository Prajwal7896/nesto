
import json
import logging
import os
import re
import time
from typing import Any, Dict

import certifi
from dotenv import load_dotenv
from google import genai

from backend.api.rag.extractor_1.prompt import build_prompt

logger = logging.getLogger(__name__)

# Environment configuration
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from environment variables.")

client = genai.Client(api_key=API_KEY)


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract and validate a JSON object from Gemini response.
    """

    if not text or not text.strip():
        raise ValueError("Gemini returned an empty response.")

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s*```$", "", text).strip()

    # First attempt: direct JSON parsing
    try:
        result = json.loads(text)

    except json.JSONDecodeError:
        # Fallback: locate a JSON object in surrounding text
        start = text.find("{")

        if start == -1:
            raise ValueError(
                "Gemini response does not contain a JSON object."
            )

        try:
            result, _ = json.JSONDecoder().raw_decode(text[start:])

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Gemini returned malformed JSON: {error}"
            ) from error

    if not isinstance(result, dict):
        raise ValueError(
            f"Expected JSON object, received {type(result).__name__}."
        )

    return result


def parse_with_llm(prompt: str) -> Dict[str, Any]:
    """
    Convert user requirements into structured architectural data.
    """

    if not prompt or not prompt.strip():
        raise ValueError("House plan prompt cannot be empty.")

    try:
        started = time.perf_counter()
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=build_prompt(prompt),
                config={
                    "temperature": 0,
                    "response_mime_type": "application/json",
                },
            )
        finally:
            logger.info(
                "stage_timing stage=gemini_extraction seconds=%.6f",
                time.perf_counter() - started,
            )

        response_text = response.text

        if not response_text:
            raise ValueError(
                "Gemini returned no text. Check response candidates "
                "and finish reason."
            )

        logger.info("Gemini response received successfully.")

        logger.debug(
            "Gemini raw response:\n%s",
            response_text
        )

        result = extract_json(response_text)

        logger.info(
            "Gemini JSON parsed successfully. Top-level keys: %s",
            list(result.keys())
        )

        return result

    except Exception:
        logger.exception("Gemini extraction or JSON parsing failed.")
        raise
