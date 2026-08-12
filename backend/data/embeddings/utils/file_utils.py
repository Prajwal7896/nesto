import os
import json
from typing import List, Dict, Any


# =========================
# READ JSON FILE
# =========================
def read_json(path: str) -> Dict[str, Any]:
    """
    Read a standard JSON file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# WRITE JSON FILE
# =========================
def write_json(path: str, data: Dict[str, Any]):
    """
    Write dictionary to JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================
# READ JSONL FILE
# =========================
def read_jsonl(path: str) -> List[Dict[str, Any]]:
    """
    Read JSONL (one JSON object per line).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSONL file not found: {path}")

    data = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))

    return data


# =========================
# WRITE JSONL FILE
# =========================
def write_jsonl(path: str, data: List[Dict[str, Any]]):
    """
    Write list of dictionaries to JSONL file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# =========================
# APPEND TO JSONL FILE
# =========================
def append_jsonl(path: str, data: List[Dict[str, Any]]):
    """
    Append new records to JSONL file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# =========================
# SAFE FILE CHECK
# =========================
def file_exists(path: str) -> bool:
    """
    Check if file exists.
    """
    return os.path.exists(path)


# =========================
# CREATE DIRECTORY IF NOT EXISTS
# =========================
def ensure_dir(path: str):
    """
    Create directory if it doesn't exist.
    """
    os.makedirs(path, exist_ok=True)