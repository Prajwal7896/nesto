"""Switchboard component generator."""

from .electrical_models import ElectricalComponent


class SwitchboardGenerator:

    def generate(self, boards: list[dict]) -> list[ElectricalComponent]:
        result = []

        for index, board in enumerate(boards):
            position = board.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Board {index}: position must be [x, y]")

            result.append(
                ElectricalComponent(
                    component_id=board.get(
                        "component_id", f"switchboard_{index + 1}"
                    ),
                    component_type="switchboard",
                    position=position,
                    elevation=float(board.get("elevation", 1200)),
                    room_id=board.get("room_id"),
                    properties={
                        "switch_count": int(board.get("switch_count", 4)),
                        "socket_count": int(board.get("socket_count", 0)),
                        "orientation": board.get("orientation", "north"),
                        "mounting": board.get("mounting", "wall"),
                    },
                )
            )

        return result
