import json
from pathlib import Path

DATA_DIR = Path("backend/data")


def extract_texts_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []

    def recurse(obj, source):
        if isinstance(obj, dict):
            for k, v in obj.items():
                recurse(v, source)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item, source)
        else:
            text = str(obj).strip()
            if len(text) > 10:
                chunks.append({
                    "text": text,
                    "source": str(source)
                })

    recurse(data, str(file_path))
    return chunks


def build_all_chunks():
    all_chunks = []

    for file in DATA_DIR.rglob("*.json"):
        chunks = extract_texts_from_json(file)
        all_chunks.extend(chunks)

    return all_chunks