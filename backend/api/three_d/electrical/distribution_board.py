"""Distribution board generator."""

from .electrical_models import ElectricalComponent


class DistributionBoardGenerator:

    def generate(self, boards: list[dict]) -> list[ElectricalComponent]:
        result = []

        for index, board in enumerate(boards):
            position = board.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Distribution board {index}: position must be [x, y]")

            result.append(
                ElectricalComponent(
                    component_id=board.get(
                        "component_id", f"distribution_board_{index + 1}"
                    ),
                    component_type="distribution_board",
                    position=position,
                    elevation=float(board.get("elevation", 1800)),
                    room_id=board.get("room_id"),
                    properties={
                        "main_breaker_rating": board.get("main_breaker_rating"),
                        "circuit_count": int(board.get("circuit_count", 8)),
                        "phase": board.get("phase", "single"),
                        "circuit_ids": board.get("circuit_ids", []),
                        "orientation": board.get("orientation", "north"),
                    },
                )
            )

        return result
