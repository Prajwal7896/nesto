from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Room:
    id: str
    type: str
    width: float
    height: float
    area: float
    x: float = 0
    y: float = 0
    rotation: int = 0
    preferred_direction: str = "flexible"


@dataclass
class Layout:

    plot: Dict

    rooms: List[Room] = field(default_factory=list)

    connections: List[Dict] = field(default_factory=list)

    dimensions: Dict = field(default_factory=dict)

    structure: Dict = field(default_factory=dict)

    engineering: Dict = field(default_factory=dict)

    cost: Dict = field(default_factory=dict)

    metadata: Dict = field(default_factory=dict)