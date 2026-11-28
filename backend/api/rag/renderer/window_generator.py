from dataclasses import dataclass
from math import hypot

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

    @staticmethod
    def _xy(point):
        if hasattr(point, "x"):
            return float(point.x), float(point.y)

        return float(point[0]), float(point[1])

    def place_window_on_wall(
        self,
        wall: dict,
        position_t: float = 0.5,
        width: float = 1200,
        layer: str = "WINDOWS",
    ):
        if not 0 <= position_t <= 1:
            raise ValueError("position_t must be between 0 and 1")

        if width <= 0:
            raise ValueError("Window width must be positive")

        x1, y1 = self._xy(wall["start"])
        x2, y2 = self._xy(wall["end"])

        dx = x2 - x1
        dy = y2 - y1
        length = hypot(dx, dy)

        if length <= 0:
            raise ValueError("Cannot place a window on a zero-length wall")

        actual_width = min(float(width), length)
        ux = dx / length
        uy = dy / length

        cx = x1 + dx * position_t
        cy = y1 + dy * position_t
        half = actual_width / 2

        start = (cx - ux * half, cy - uy * half)
        end = (cx + ux * half, cy + uy * half)

        nx = -uy
        ny = ux
        frame_offset = 50.0

        frame_start_1 = (
            start[0] + nx * frame_offset,
            start[1] + ny * frame_offset,
        )
        frame_end_1 = (
            end[0] + nx * frame_offset,
            end[1] + ny * frame_offset,
        )
        frame_start_2 = (
            start[0] - nx * frame_offset,
            start[1] - ny * frame_offset,
        )
        frame_end_2 = (
            end[0] - nx * frame_offset,
            end[1] - ny * frame_offset,
        )

        self.msp.add_line(
            frame_start_1,
            frame_end_1,
            dxfattribs={"layer": layer},
        )
        self.msp.add_line(
            frame_start_2,
            frame_end_2,
            dxfattribs={"layer": layer},
        )
        self.msp.add_line(
            start,
            end,
            dxfattribs={"layer": layer},
        )

        return {
            "type": "window",
            "start": start,
            "end": end,
            "width": actual_width,
        }

    def _draw_window_frame(
        self,
        start: Point,
        end: Point,
        layer: str = "WINDOWS",
    ):
        self.msp.add_line(
            self._xy(start),
            self._xy(end),
            dxfattribs={"layer": layer},
        )

    def _draw_glass_line(
        self,
        start: Point,
        end: Point,
        layer: str = "WINDOWS",
    ):
        self.msp.add_line(
            self._xy(start),
            self._xy(end),
            dxfattribs={"layer": layer},
        )

        sx, sy = self._xy(start)
        ex, ey = self._xy(end)
        mx = (sx + ex) / 2
        my = (sy + ey) / 2

        dx = ex - sx
        dy = ey - sy
        length = hypot(dx, dy)

        if length <= 0:
            return

        nx = -dy / length
        ny = dx / length

        self.msp.add_line(
            (mx - nx * 50, my - ny * 50),
            (mx + nx * 50, my + ny * 50),
            dxfattribs={"layer": layer},
        )

    def create_corner_window(
        self,
        wall1: Line,
        wall2: Line,
        width: float = 1200,
        layer: str = "WINDOWS",
    ):
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
            "end": p2,
            "width": width,
        }

    def create_strip_window(
        self,
        wall: Line,
        segments: int = 3,
        width: float = 300,
        gap: float = 200,
        layer: str = "WINDOWS",
    ):
        if segments < 1 or width <= 0 or gap < 0:
            raise ValueError("Invalid strip-window dimensions")

        direction = wall.direction.normalize()
        wall_length = hypot(
            wall.end.x - wall.start.x,
            wall.end.y - wall.start.y,
        )

        total_width = segments * width + (segments - 1) * gap

        if total_width > wall_length:
            raise ValueError("Strip windows exceed wall length")

        windows = []
        start_offset = (wall_length - total_width) / 2

        for i in range(segments):
            center_distance = (
                start_offset
                + i * (width + gap)
                + width / 2
            )
            t = center_distance / wall_length
            center = wall.point_at(t)
            half = width / 2

            start = Point(
                center.x - direction.x * half,
                center.y - direction.y * half,
            )
            end = Point(
                center.x + direction.x * half,
                center.y + direction.y * half,
            )

            self._draw_window_frame(start, end, layer)
            windows.append((start, end))

        return windows