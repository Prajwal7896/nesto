import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("backend/data")
REPORT_FILE = "json_scan_report.json"

SYSTEM_DIRS = {
    "index",
    "mapping",
    "embeddings_cache",
}

SYSTEM_FILES = {
    "cache_index.json",
    "index_config.json",
    "index_stats.json",
    "id_to_category.json",
    "id_to_metadata.json",
    "id_to_source.json",
    "id_to_text.json",
    "mapping_index.json",
    "chunking_strategy.json",
    "embedding_model.json",
    "retrieval_config.json",
    "vector_config.json",
}


def flatten_json(value: Any, prefix: str = "") -> list[str]:
    lines = []

    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            lines.extend(flatten_json(item, path))

    elif isinstance(value, list):
        for index, item in enumerate(value):
            lines.extend(flatten_json(item, f"{prefix}[{index}]"))

    elif value is not None:
        lines.append(f"{prefix}: {value}")

    return lines


def scan_json_files():
    results = []

    files = sorted(
        path for path in DATA_DIR.rglob("*.json")
        if "__pycache__" not in path.parts
        and path.name != REPORT_FILE
    )

    for path in files:
        relative = path.relative_to(DATA_DIR)
        relative_path = relative.as_posix()

        is_system = (
            path.name in SYSTEM_FILES
            or any(part in SYSTEM_DIRS for part in relative.parts[:-1])
            or relative.parts[0] == "config"
            if relative.parts
            else False
        )

        result = {
            "source": relative_path,
            "status": "SCANNED",
            "type": "SYSTEM" if is_system else "KNOWLEDGE",
            "characters": 0,
        }

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            content = "\n".join(flatten_json(data))
            result["characters"] = len(content)

            if is_system:
                result["status"] = "SYSTEM_FILE"
            elif not content.strip():
                result["status"] = "EMPTY"
            else:
                result["status"] = "READY_FOR_PROCESSING"

        except Exception as error:
            result["status"] = "INVALID_JSON"
            result["error"] = str(error)

        results.append(result)

    total = len(results)

    report = {
        "total_scanned": total,
        "knowledge_files": sum(
            r["type"] == "KNOWLEDGE" for r in results
        ),
        "system_files": sum(
            r["type"] == "SYSTEM" for r in results
        ),
        "ready_for_processing": sum(
            r["status"] == "READY_FOR_PROCESSING" for r in results
        ),
        "invalid": sum(
            r["status"] == "INVALID_JSON" for r in results
        ),
        "empty": sum(
            r["status"] == "EMPTY" for r in results
        ),
        "results": results,
    }

    return report


if __name__ == "__main__":
    report = scan_json_files()

    print("\n========== NESTO COMPLETE JSON SCAN ==========\n")
    print("Total scanned:", report["total_scanned"])
    print("Knowledge files:", report["knowledge_files"])
    print("System files:", report["system_files"])
    print("Ready for processing:", report["ready_for_processing"])
    print("Invalid:", report["invalid"])
    print("Empty:", report["empty"])

    for item in report["results"]:
        print(
            f'{item["status"]:22} '
            f'{item["source"]:65} '
            f'{item["characters"]} characters'
        )

    output = DATA_DIR / REPORT_FILE
    output.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nReport saved:", output)
