"""Exterior gate generator."""


class GateGenerator:

    def generate(self, gates: list[dict]) -> list[dict]:
        result = []

        for index, gate in enumerate(gates):
            position = gate.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Gate {index}: position must be [x, y]")

            width = float(gate.get("width", 3000))
            height = float(gate.get("height", 1800))

            if width <= 0 or height <= 0:
                raise ValueError(f"Gate {index}: dimensions must be positive")

            result.append({
                "gate_id": gate.get("gate_id", f"gate_{index + 1}"),
                "position": position,
                "width": width,
                "height": height,
                "depth": float(gate.get("depth", 80)),
                "gate_type": gate.get("gate_type", "sliding"),
                "material": gate.get("material", "steel"),
                "orientation": gate.get("orientation", "north"),
                "opening_angle": float(gate.get("opening_angle", 0)),
                "color": gate.get("color", "#333333"),
            })

        return result
