import json
import os
from typing import Any, Dict

import certifi
from dotenv import load_dotenv
from google import genai

from backend.api.rag.extractor_1.prompt import build_prompt

# Fix SSL certificate path
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def parse_with_llm(prompt: str) -> Dict[str, Any]:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_prompt(prompt),
        config={
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    )

    text = response.text.strip()

    print("Gemini Response:")
    print(text)

    if not text:
        raise Exception("Gemini returned empty response")

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        # Remove markdown JSON wrapper if returned
        text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(text)