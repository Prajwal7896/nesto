import os
import json
import uuid
from typing import List, Dict, Any

from utils.text_cleaner import clean_text
from utils.file_utils import read_json, write_jsonl


# =========================
# CONFIG PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "chunks")   # raw JSON files
OUTPUT_DIR = os.path.join(BASE_DIR, "chunks")  # overwrite or same folder


# =========================
# FLATTEN JSON → TEXT CHUNKS
# =========================
def flatten_json(prefix: str, obj: Any) -> List[str]:
    chunks = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            chunks.extend(flatten_json(new_prefix, v))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_prefix = f"{prefix}[{i}]"
            chunks.extend(flatten_json(new_prefix, item))

    else:
        text = f"{prefix}: {obj}"
        chunks.append(text)

    return chunks


# =========================
# CREATE CHUNK OBJECT
# =========================
def create_chunk(text: str, source_file: str, meta: Dict = None) -> Dict:
    return {
        "id": str(uuid.uuid4()),
        "text": clean_text(text),
        "source": source_file,
        "metadata": meta or {}
    }


# =========================
# PROCESS SINGLE FILE
# =========================
def process_file(file_path: str) -> List[Dict]:
    file_name = os.path.basename(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_chunks = flatten_json(file_name.replace(".json", ""), data)

    processed = []

    for chunk in flat_chunks:
        processed.append(
            create_chunk(
                text=chunk,
                source_file=file_name,
                meta={
                    "file": file_name
                }
            )
        )

    return processed


# =========================
# MAIN PIPELINE
# =========================
def build_all_chunks():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_chunks = []

    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(INPUT_DIR, file)

        print(f"📦 Processing: {file}")

        chunks = process_file(file_path)
        all_chunks.extend(chunks)

    output_file = os.path.join(OUTPUT_DIR, "combined_chunks.jsonl")

    write_jsonl(output_file, all_chunks)

    print(f"✅ Chunking complete!")
    print(f"📁 Saved: {output_file}")
    print(f"📊 Total chunks: {len(all_chunks)}")


# =========================
# RUN SCRIPT
# =========================
if __name__ == "__main__":
    build_all_chunks()