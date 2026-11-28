"""Garden area and planting generator."""


class GardenGenerator:

    def generate(self, gardens: list[dict]) -> list[dict]:
        result = []

        for index, garden in enumerate(gardens):
            position = garden.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Garden {index}: position must be [x, y]")

            width = float(garden.get("width", 3000))
            depth = float(garden.get("depth", 3000))

            if width <= 0 or depth <= 0:
                raise ValueError(f"Garden {index}: dimensions must be positive")

            plants = garden.get("plants", [])

            result.append({
                "garden_id": garden.get("garden_id", f"garden_{index + 1}"),
                "position": position,
                "width": width,
                "depth": depth,
                "surface": garden.get("surface", "grass"),
                "grass_color": garden.get("grass_color", "#4C9A52"),
                "plants": plants,
                "irrigation": bool(garden.get("irrigation", False)),
                "fence": bool(garden.get("fence", False)),
            })

        return result
