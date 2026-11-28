"""Core data models for Nesto HVAC."""

from dataclasses import dataclass, field, asdict


@dataclass
class HVACComponent:
    component_id: str
    component_type: str
    position: list[float]
    elevation: float = 0.0
    room_id: str | None = None
    properties: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class DuctSegment:
    duct_id: str
    start: list[float]
    end: list[float]
    elevation_start: float = 0.0
    elevation_end: float = 0.0
    width: float = 200.0
    height: float = 150.0
    material: str = "GI"
    connected_to: list[str] = field(default_factory=list)

    def length(self):
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        dz = self.elevation_end - self.elevation_start
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def to_dict(self):
        data = asdict(self)
        data["length"] = self.length()
        return data


@dataclass
class HVACSystem:
    system_id: str
    components: list[HVACComponent] = field(default_factory=list)
    ducts: list[DuctSegment] = field(default_factory=list)

    def to_dict(self):
        return {
            "system_id": self.system_id,
            "components": [item.to_dict() for item in self.components],
            "ducts": [item.to_dict() for item in self.ducts],
        }
