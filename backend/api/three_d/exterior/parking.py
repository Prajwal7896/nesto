"""Parking space generator."""


class ParkingGenerator:

    DEFAULT_DIMENSIONS = {
        "car": {"width": 2500, "length": 5000},
        "bike": {"width": 1000, "length": 2000},
        "suv": {"width": 3000, "length": 5500},
    }

    def generate(self, spaces: list[dict]) -> list[dict]:
        result = []

        for index, space in enumerate(spaces):
            position = space.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Parking {index}: position must be [x, y]")

            vehicle_type = space.get("vehicle_type", "car").lower()

            if vehicle_type not in self.DEFAULT_DIMENSIONS:
                raise ValueError(f"Unsupported vehicle type: {vehicle_type}")

            defaults = self.DEFAULT_DIMENSIONS[vehicle_type]
            width = float(space.get("width", defaults["width"]))
            length = float(space.get("length", defaults["length"]))

            if width <= 0 or length <= 0:
                raise ValueError(f"Parking {index}: dimensions must be positive")

            result.append({
                "parking_id": space.get("parking_id", f"parking_{index + 1}"),
                "position": position,
                "width": width,
                "length": length,
                "vehicle_type": vehicle_type,
                "rotation": float(space.get("rotation", 0)),
                "covered": bool(space.get("covered", False)),
                "surface": space.get("surface", "concrete"),
                "color": space.get("color", "#777777"),
            })

        return result
