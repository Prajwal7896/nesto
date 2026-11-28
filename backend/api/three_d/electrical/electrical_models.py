"""Core data models for Nesto electrical visualization."""

from dataclasses import dataclass, field, asdict


@dataclass
class ElectricalComponent:
    component_id: str
    component_type: str
    position: list[float]
    elevation: float = 0.0
    room_id: str | None = None
    properties: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class WireSegment:
    wire_id: str
    start: list[float]
    end: list[float]
    elevation_start: float = 0.0
    elevation_end: float = 0.0
    wire_type: str = "copper"
    circuit_id: str = "circuit_1"
    voltage: float = 230.0
    current_rating: float | None = None
    connected_to: list[str] = field(default_factory=list)

    def length(self) -> float:
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        dz = self.elevation_end - self.elevation_start
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def to_dict(self):
        data = asdict(self)
        data["length"] = self.length()
        return data


@dataclass
class ConduitSegment:
    conduit_id: str
    start: list[float]
    end: list[float]
    diameter: float = 20.0
    elevation_start: float = 0.0
    elevation_end: float = 0.0
    material: str = "PVC"
    connected_to: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class ElectricalSystem:
    system_id: str
    components: list[ElectricalComponent] = field(default_factory=list)
    wires: list[WireSegment] = field(default_factory=list)
    conduits: list[ConduitSegment] = field(default_factory=list)

    def to_dict(self):
        return {
            "system_id": self.system_id,
            "components": [item.to_dict() for item in self.components],
            "wires": [item.to_dict() for item in self.wires],
            "conduits": [item.to_dict() for item in self.conduits],
        }
