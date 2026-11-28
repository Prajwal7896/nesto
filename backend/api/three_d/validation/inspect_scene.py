import json
from pathlib import Path

scene_dir = Path("output/three_d/scenes")
files = sorted(
    scene_dir.glob("*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

if not files:
    print("No generated scene JSON found.")
    raise SystemExit(1)

with files[0].open("r", encoding="utf-8") as f:
    scene = json.load(f)

print("\nLATEST SCENE:", files[0].name)

for floor in scene.get("floors", []):
    print("\n========== FLOOR ==========")
    print("Floor ID:", floor.get("id"))

    print("\n--- ROOMS ---")
    for room in floor.get("rooms", []):
        print({
            "id": room.get("id"),
            "type": room.get("type"),
            "x": room.get("x"),
            "y": room.get("y"),
            "width": room.get("width"),
            "depth": room.get("depth"),
            "polygon": room.get("polygon")
        })

    print("\n--- DOORS ---")
    for door in floor.get("doors", []):
        print(door)

    print("\n--- CONNECTIONS ---")
    for connection in floor.get("connections", []):
        print(connection)