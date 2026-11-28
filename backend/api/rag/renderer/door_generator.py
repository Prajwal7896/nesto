
from dataclasses import dataclass
from math import degrees

from .geometry.point import Point
from .geometry.line import Line


@dataclass
class Door:
    position: Point
    width: float = 900
    swing_angle: float = 90
    layer: str = "DOORS"


class DoorGenerator:

    def __init__(self, msp):
        self.msp = msp

    def _to_line(self, wall):
        if isinstance(wall, Line):
            return wall

        if isinstance(wall, dict):
            start = wall.get("start")
            end = wall.get("end")

            if not start or not end:
                raise ValueError("Wall requires start and end points")

            return Line(
                Point(*start),
                Point(*end),
            )

        if isinstance(wall, (list, tuple)) and len(wall) == 2:
            return Line(
                Point(*wall[0]),
                Point(*wall[1]),
            )

        raise TypeError(
            "Wall must be a Line, a start/end dictionary, "
            "or a pair of points"
        )

    def place_door_on_wall(
        self,
        wall,
        position_t=0.5,
        width=900,
        swing_angle=90,
        layer="DOORS",
    ):
        wall = self._to_line(wall)

        if not 0 <= position_t <= 1:
            raise ValueError("position_t must be between 0 and 1")

        if width <= 0:
            raise ValueError("Door width must be positive")

        if not 0 < swing_angle <= 180:
            raise ValueError("swing_angle must be between 0 and 180")

        direction = wall.direction.normalize()
        wall_length = (
            (wall.end.x - wall.start.x) ** 2
            + (wall.end.y - wall.start.y) ** 2
        ) ** 0.5

        if width > wall_length:
            raise ValueError("Door width cannot exceed wall length")

        hinge_t = position_t

        if hinge_t * wall_length + width > wall_length:
            hinge_t = (wall_length - width) / wall_length

        hinge = wall.point_at(hinge_t)

        door_end = Point(
            hinge.x + direction.x * width,
            hinge.y + direction.y * width,
        )

        door = Door(
            position=hinge,
            width=width,
            swing_angle=swing_angle,
            layer=layer,
        )

        self._draw_door_line(hinge, door_end, layer)
        self._draw_swing_arc(
            hinge,
            width,
            direction,
            swing_angle,
            layer,
        )

        return door

    def _draw_door_line(self, start, end, layer):
        self.msp.add_line(
            (start.x, start.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

    def _draw_swing_arc(
        self,
        hinge,
        radius,
        direction,
        angle_deg,
        layer,
    ):
        base_angle = degrees(direction.angle) % 360

        self.msp.add_arc(
            center=(hinge.x, hinge.y),
            radius=radius,
            start_angle=base_angle,
            end_angle=(base_angle + angle_deg) % 360,
            dxfattribs={"layer": layer},
        )

    def create_double_door(
        self,
        wall,
        position_t=0.5,
        width=1200,
        layer="DOORS",
    ):
        wall = self._to_line(wall)
        direction = wall.direction.normalize()

        if width <= 0:
            raise ValueError("Door width must be positive")

        wall_length = (
            (wall.end.x - wall.start.x) ** 2
            + (wall.end.y - wall.start.y) ** 2
        ) ** 0.5

        if width > wall_length:
            raise ValueError("Door width cannot exceed wall length")

        half = width / 2
        start_t = position_t - half / wall_length

        if start_t < 0:
            start_t = 0

        first = self.place_door_on_wall(
            wall,
            start_t,
            half,
            90,
            layer,
        )

        second_t = start_t + half / wall_length

        second = self.place_door_on_wall(
            wall,
            second_t,
            half,
            90,
            layer,
        )

        return {
            "type": "double_door",
            "doors": [first, second],
            "width": width,
        }

    def create_sliding_door(
        self,
        wall,
        position_t=0.5,
        width=1000,
        layer="DOORS",
    ):
        wall = self._to_line(wall)

        if not 0 <= position_t <= 1:
            raise ValueError("position_t must be between 0 and 1")

        if width <= 0:
            raise ValueError("Door width must be positive")

        direction = wall.direction.normalize()

        wall_length = (
            (wall.end.x - wall.start.x) ** 2
            + (wall.end.y - wall.start.y) ** 2
        ) ** 0.5

        if width > wall_length:
            raise ValueError("Door width cannot exceed wall length")

        start_t = min(position_t, 1 - width / wall_length)
        hinge = wall.point_at(start_t)

        end = Point(
            hinge.x + direction.x * width,
            hinge.y + direction.y * width,
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
            "width": width,
        }
