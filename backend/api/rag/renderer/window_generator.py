from dataclasses import dataclass

from .geometry.point import Point
from .geometry.line import Line


@dataclass
class Window:
    start: Point
    end: Point
    sill_height: float = 900
    height: float = 1200
    layer: str = "WINDOWS"


class WindowGenerator:

    def __init__(self, msp):
        self.msp = msp

    def place_window_on_wall(
        self,
        wall: dict,
        position_t: float = 0.5,
        width: float = 1200,
        layer: str = "WINDOWS"
    ):

        x1, y1 = wall["start"]
        x2, y2 = wall["end"]

        cx = x1 + (x2 - x1) * position_t
        cy = y1 + (y2 - y1) * position_t

        dx = x2 - x1
        dy = y2 - y1

        length = (dx**2 + dy**2) ** 0.5

        ux = dx / length
        uy = dy / length

        half = width / 2

        start = (cx - ux * half, cy - uy * half)
        end = (cx + ux * half, cy + uy * half)

        self.msp.add_line(start, end, dxfattribs={"layer": layer})

    def _draw_window_frame(
        self,
        start: Point,
        end: Point,
        layer: str
    ):

        self.msp.add_line(
            (start.x, start.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

    def _draw_glass_line(
        self,
        start: Point,
        end: Point,
        layer: str
    ):

        mid = Point(
            (start.x + end.x) / 2,
            (start.y + end.y) / 2
        )

        self.msp.add_line(
            (start.x, start.y),
            (end.x, end.y),
            dxfattribs={"layer": layer},
        )

        # center glass indicator
        self.msp.add_line(
            (mid.x, mid.y - 50),
            (mid.x, mid.y + 50),
            dxfattribs={"layer": layer},
        )

    def create_corner_window(
        self,
        wall1: Line,
        wall2: Line,
        width: float = 1200,
        layer: str = "WINDOWS"
    ):
        """
        Creates a corner window between two walls.
        """

        p1 = wall1.point_at(1.0)
        p2 = wall2.point_at(0.0)

        self.msp.add_line(
            (p1.x, p1.y),
            (p2.x, p2.y),
            dxfattribs={"layer": layer},
        )

        return {
            "type": "corner_window",
            "start": p1,
            "end": p2
        }

    def create_strip_window(
        self,
        wall: Line,
        segments: int = 3,
        width: float = 300,
        gap: float = 200,
        layer: str = "WINDOWS"
    ):
        """
        Creates multiple small windows along a wall (modern facade style).
        """

        windows = []

        t = 0.1

        step = 0.6 / segments

        for i in range(segments):

            center = wall.point_at(t)

            direction = wall.direction.normalize()

            half = width / 2

            start = Point(
                center.x - direction.x * half,
                center.y - direction.y * half
            )

            end = Point(
                center.x + direction.x * half,
                center.y + direction.y * half
            )

            self._draw_window_frame(start, end, layer)

            windows.append((start, end))

            t += step

        return windows