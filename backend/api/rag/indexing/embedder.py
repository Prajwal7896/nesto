import os
import time
import hashlib

from google import genai


client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


MODEL = "text-embedding-004"


def embed_text(text):

    if isinstance(text, dict):
        text = str(text)


    if not text:
        return fallback_embedding("empty")


    try:

        response = client.models.embed_content(
            model=MODEL,
            contents=text
        )

        return response.embeddings[0].values


    except Exception as e:

        print(
            "Gemini embedding failed:",
            e
        )

        print(
            "Using local fallback embedding"
        )

        return fallback_embedding(text)



def fallback_embedding(text):

    import hashlib

    dimension = 3072

    vector = []

    hash_value = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


    for i in range(dimension):

        value = int(
            hash_value[i % len(hash_value)],
            16
        )

        vector.append(
            value / 15.0
        )


    return vector