from dataclasses import dataclass
from math import radians, sin, cos

from .geometry.point import Point
from .geometry.line import Line


@dataclass
class Door:
    position: Point          # hinge point
    width: float = 900       # mm
    swing_angle: float = 90  # degrees
    layer: str = "DOORS"


class DoorGenerator:

    def __init__(self, msp):
        self.msp = msp

    def place_door_on_wall(
        self,
        wall: Line,
        position_t: float = 0.5,
        width: float = 900,
        swing_angle: float = 90,
        layer: str = "DOORS"
    ):
        
        # Convert dict/list into Line
        if isinstance(wall, dict):
            wall = Line(
                Point(*wall["start"]),
                Point(*wall["end"])
            )

        elif isinstance(wall, list):
            wall = Line(
                Point(*wall[0]),
                Point(*wall[1])
            )
        """
        Places a door on a wall using parametric position (0-1).
        """

        hinge = wall.point_at(position_t)

        direction = wall.direction.normalize()

        door_end = Point(
            hinge.x + direction.x * width,
            hinge.y + direction.y * width
        )

        door = Door(
            position=hinge,
            width=width,
            swing_angle=swing_angle,
            layer=layer
        )

        self._draw_door_line(hinge, door_end, layer)
        self._draw_swing_arc(hinge, width, direction, swing_angle, layer)

        return door

    def _draw_door_line(self, start: Point, end: Point, layer: str):

        self.msp.add_line(
            (start.x, start.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

    def _draw_swing_arc(
        self,
        hinge: Point,
        radius: float,
        direction,
        angle_deg: float,
        layer: str
    ):
        """
        Draws door swing arc (standard CAD representation).
        """

        base_angle = direction.angle

        start_angle = base_angle
        end_angle = base_angle + angle_deg

        self.msp.add_arc(
            center=(hinge.x, hinge.y),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
            dxfattribs={"layer": layer},
        )

    def create_double_door(
        self,
        wall: Line,
        position_t: float = 0.5,
        width: float = 1200,
        layer: str = "DOORS"
    ):
        """
        Creates a double door (two leafs).
        """

        hinge = wall.point_at(position_t)
        direction = wall.direction.normalize()

        half = width / 2

        mid = Point(
            hinge.x + direction.x * half,
            hinge.y + direction.y * half
        )

        self.place_door_on_wall(
            wall,
            position_t,
            half,
            90,
            layer
        )

        self.place_door_on_wall(
            wall,
            position_t + 0.01,
            half,
            90,
            layer
        )

        return {
            "type": "double_door",
            "center": mid,
            "width": width
        }

    def create_sliding_door(
        self,
        wall: Line,
        position_t: float = 0.5,
        width: float = 1000,
        layer: str = "DOORS"
    ):
        """
        Sliding door (no swing arc).
        """

        hinge = wall.point_at(position_t)
        direction = wall.direction.normalize()

        end = Point(
            hinge.x + direction.x * width,
            hinge.y + direction.y * width
        )

        self.msp.add_line(
            (hinge.x, hinge.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

        return {
            "type": "sliding_door",
            "start": hinge,
            "end": end,
            "width": width
        }