"""Electrical socket generator."""

from .electrical_models import ElectricalComponent


class SocketGenerator:

    def generate(self, sockets: list[dict]) -> list[ElectricalComponent]:
        result = []

        for index, socket in enumerate(sockets):
            position = socket.get("position", [0, 0])

            if len(position) != 2:
                raise ValueError(f"Socket {index}: position must be [x, y]")

            result.append(
                ElectricalComponent(
                    component_id=socket.get(
                        "component_id", f"socket_{index + 1}"
                    ),
                    component_type="socket",
                    position=position,
                    elevation=float(socket.get("elevation", 300)),
                    room_id=socket.get("room_id"),
                    properties={
                        "socket_type": socket.get("socket_type", "5A"),
                        "voltage": float(socket.get("voltage", 230)),
                        "orientation": socket.get("orientation", "north"),
                        "weatherproof": bool(socket.get("weatherproof", False)),
                    },
                )
            )

        return result
