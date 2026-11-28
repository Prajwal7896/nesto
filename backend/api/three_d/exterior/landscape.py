"""Landscape object and vegetation generator."""


class LandscapeGenerator:

    SUPPORTED_TYPES = {
        "tree",
        "shrub",
        "flower",
        "rock",
        "bench",
        "lamp_post",
        "pond",
    }

    def generate(self, objects: list[dict]) -> list[dict]:
        result = []

        for index, item in enumerate(objects):
            position = item.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Landscape object {index}: position must be [x, y]")

            object_type = item.get("object_type", "tree").lower()

            if object_type not in self.SUPPORTED_TYPES:
                raise ValueError(f"Unsupported landscape type: {object_type}")

            result.append({
                "object_id": item.get("object_id", f"landscape_{index + 1}"),
                "object_type": object_type,
                "position": position,
                "elevation": float(item.get("elevation", 0)),
                "height": float(item.get("height", 2000)),
                "width": float(item.get("width", 1000)),
                "depth": float(item.get("depth", 1000)),
                "rotation": float(item.get("rotation", 0)),
                "color": item.get("color", "#3F8F45"),
                "model": item.get("model"),
            })

        return result
