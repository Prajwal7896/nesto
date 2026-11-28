"""Core data models for the Nesto plumbing system."""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PipeSegment:
    pipe_id: str
    system_type: str
    start: list[float]
    end: list[float]
    diameter: float
    elevation_start: float = 0.0
    elevation_end: float = 0.0
    material: str = "PVC"
    slope_percent: float = 0.0
    flow_direction: str = "forward"
    connected_to: list[str] = field(default_factory=list)
    insulated: bool = False

    def length(self) -> float:
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        dz = self.elevation_end - self.elevation_start
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def to_dict(self) -> dict:
        data = asdict(self)
        data["length"] = self.length()
        return data


@dataclass
class PlumbingFixture:
    fixture_id: str
    fixture_type: str
    position: list[float]
    elevation: float = 0.0
    room_id: Optional[str] = None
    connections: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WaterTank:
    tank_id: str
    position: list[float]
    width: float
    depth: float
    height: float
    tank_type: str = "overhead"
    material: str = "plastic"

    @property
    def capacity_litres(self) -> float:
        return self.width * self.depth * self.height / 1_000_000

    def to_dict(self) -> dict:
        data = asdict(self)
        data["capacity_litres"] = self.capacity_litres
        return data


@dataclass
class PlumbingSystem:
    system_id: str
    system_type: str
    pipes: list[PipeSegment] = field(default_factory=list)
    fixtures: list[PlumbingFixture] = field(default_factory=list)
    tanks: list[WaterTank] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "system_id": self.system_id,
            "system_type": self.system_type,
            "pipes": [pipe.to_dict() for pipe in self.pipes],
            "fixtures": [fixture.to_dict() for fixture in self.fixtures],
            "tanks": [tank.to_dict() for tank in self.tanks],
        }
