import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT_DIR / "backend" / "data"

ALLOWED_DIRECTORIES = {
    "architecture",
    "building_codes",
    "cost",
    "engineering",
    "furniture",
    "materials",
    "optimization",
    "planning_rules",
    "structural",
    "templates",
    "vastu",
}

MAX_CHUNK_CHARS = 1400


def collect_facts(obj: Any, path: str, facts: List[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_path = f"{path}.{key}" if path else str(key)
            collect_facts(value, next_path, facts)

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            next_path = f"{path}[{index}]"
            collect_facts(item, next_path, facts)

    elif obj is not None:
        if isinstance(obj, str):
            value = obj.strip()
        else:
            value = json.dumps(obj, ensure_ascii=False)

        if value:
            facts.append(f"{path}: {value}")


def group_facts(facts: List[str]) -> List[str]:
    chunks = []
    current = []

    for fact in facts:
        if len(fact) > MAX_CHUNK_CHARS:
            if current:
                chunks.append("\n".join(current))
                current = []

            prefix, separator, value = fact.partition(": ")

            if not separator:
                chunks.append(fact[:MAX_CHUNK_CHARS])
                continue

            available = MAX_CHUNK_CHARS - len(prefix) - 2
            words = value.split()
            part = []

            for word in words:
                candidate = " ".join(part + [word])

                if len(candidate) > available and part:
                    chunks.append(f"{prefix}: {' '.join(part)}")
                    part = [word]
                else:
                    part.append(word)

            if part:
                chunks.append(f"{prefix}: {' '.join(part)}")

            continue

        candidate = "\n".join(current + [fact])

        if len(candidate) > MAX_CHUNK_CHARS and current:
            chunks.append("\n".join(current))
            current = [fact]
        else:
            current.append(fact)

    if current:
        chunks.append("\n".join(current))

    return chunks


def process_file(file_path: Path) -> List[Dict]:
    relative_path = file_path.relative_to(DATA_DIR).as_posix()

    try:
        with file_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[SKIPPED] {relative_path}: {error}")
        return []

    facts = []
    collect_facts(data, "$", facts)

    text_chunks = group_facts(facts)
    processed = []

    for index, text in enumerate(text_chunks):
        processed.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "source": relative_path,
            "metadata": {
                "file": relative_path,
                "chunk_index": index,
                "fact_count": len(text.splitlines()),
            },
        })

    if processed:
        print(f"[OK] {relative_path}: {len(processed)} chunks")
    else:
        print(f"[EMPTY] {relative_path}")

    return processed


def build_all_chunks() -> List[Dict]:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {DATA_DIR}")

    all_chunks = []
    scanned_files = 0
    skipped_files = 0

    for directory in sorted(ALLOWED_DIRECTORIES):
        source_dir = DATA_DIR / directory

        if not source_dir.exists():
            print(f"[MISSING DIRECTORY] {directory}")
            continue

        for file_path in sorted(source_dir.rglob("*.json")):
            scanned_files += 1
            chunks = process_file(file_path)

            if chunks:
                all_chunks.extend(chunks)
            else:
                skipped_files += 1

    if not all_chunks:
        raise ValueError("No valid knowledge chunks were generated.")

    print("\n========== CHUNKING REPORT ==========")
    print(f"Files scanned: {scanned_files}")
    print(f"Files without chunks: {skipped_files}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Knowledge directories: {len(ALLOWED_DIRECTORIES)}")
    print("====================================")

    return all_chunks


if __name__ == "__main__":
    chunks = build_all_chunks()
    print(f"\nGenerated {len(chunks)} chunks successfully.")
