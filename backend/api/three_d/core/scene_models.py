"""Typed, serializable data models for Nesto's renderer-independent 3D scene."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List, Optional, Tuple


Vector3 = Tuple[float, float, float]
Point2 = Tuple[float, float]


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


@dataclass
class SceneOpening:
    """Door or window cutout attached to a generated wall."""

    id: str
    kind: str
    wall_id: str
    position: float
    width: float
    height: float
    sill_height: float = 0.0
    source_wall_index: Optional[int] = None
    source: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _json_value(self)


@dataclass
class SceneWall:
    """A wall edge derived from a room polygon."""

    id: str
    room_id: str
    start: Point2
    end: Point2
    height: float
    thickness: float
    edge_index: int
    openings: List[SceneOpening] = field(default_factory=list)
    source: Dict[str, Any] = field(default_factory=dict)

    @property
    def length(self) -> float:
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return (dx * dx + dy * dy) ** 0.5

    def to_dict(self) -> Dict[str, Any]:
        return _json_value(self)


@dataclass
class SceneRoom:
    """A room or enclosed site feature on one floor."""

    id: str
    type: str
    name: str
    x: float
    y: float
    width: float
    depth: float
    area: float
    rotation: float = 0.0
    polygon: List[Point2] = field(default_factory=list)
    kind: str = "room"
    walls: List[SceneWall] = field(default_factory=list)
    source: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _json_value(self)


@dataclass
class SceneFloor:
    """All extracted geometry and metadata for one building floor."""

    id: str
    name: str
    elevation: float
    plot_width: float
    plot_depth: float
    rooms: List[SceneRoom] = field(default_factory=list)
    site_features: List[SceneRoom] = field(default_factory=list)
    open_spaces: List[SceneRoom] = field(default_factory=list)
    walls: List[SceneWall] = field(default_factory=list)
    doors: List[SceneOpening] = field(default_factory=list)
    windows: List[SceneOpening] = field(default_factory=list)
    furniture: List[Dict[str, Any]] = field(default_factory=list)
    connections: List[Dict[str, Any]] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)
    engineering: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _json_value(self)


@dataclass
class Scene:
    """Complete 3D scene description ready for Three.js rendering."""

    id: str
    coordinate_system: str = "threejs_x_y_z"
    source_unit: str = "mm"
    world_unit: str = "m"
    floors: List[SceneFloor] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, float] = field(
        default_factory=lambda: {
            "wall_height": 3000.0,
            "wall_thickness": 150.0,
            "floor_thickness": 150.0,
            "door_height": 2100.0,
            "window_height": 1200.0,
            "window_sill_height": 900.0,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        return _json_value(self)

    def to_json_dict(self) -> Dict[str, Any]:
        """Alias emphasizing that the returned value is JSON-serializable."""
        return self.to_dict()
