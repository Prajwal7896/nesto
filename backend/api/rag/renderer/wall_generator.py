from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .geometry.point import Point


@dataclass
class Wall:
    start: Point
    end: Point
    thickness: float = 200
    layer: str = "WALLS"


class WallGenerator:
    def __init__(self, msp):
        self.msp = msp

    def generate_from_edge(self, wall: dict, layer="WALLS"):
        self._draw_line(wall["start"], wall["end"], layer)

    def generate_from_polygon(self, polygon, layer="WALLS"):
        vertices = (
            polygon.vertices
            if hasattr(polygon, "vertices")
            else polygon
        )

        if len(vertices) < 3:
            return

        for i in range(len(vertices)):
            start = vertices[i]
            end = vertices[(i + 1) % len(vertices)]
            self._draw_line(start, end, layer)

    def generate_polygon_with_openings(
        self,
        polygon,
        room_index: int,
        doors: List[Dict[str, Any]] = None,
        windows: List[Dict[str, Any]] = None,
        layer: str = "WALLS",
    ):
        vertices = (
            polygon.vertices
            if hasattr(polygon, "vertices")
            else polygon
        )

        if len(vertices) < 3:
            return

        doors = doors or []
        windows = windows or []

        for edge in range(len(vertices)):
            start = self._xy(vertices[edge])
            end = self._xy(vertices[(edge + 1) % len(vertices)])
            wall_id = room_index * 4 + edge

            openings = []

            for opening in doors + windows:
                if opening.get("wall") != wall_id:
                    continue

                width = float(opening.get("width", 0))
                position = float(opening.get("position", 0.5))

                if width <= 0 or not 0 <= position <= 1:
                    continue

                openings.append((position, width))

            self._draw_edge_with_openings(
                start,
                end,
                openings,
                layer,
            )

    def _draw_edge_with_openings(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        openings: List[Tuple[float, float]],
        layer: str,
    ):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx * dx + dy * dy) ** 0.5

        if length <= 0:
            return

        intervals = []

        for position, width in openings:
            half = width / (2 * length)
            left = max(0.0, position - half)
            right = min(1.0, position + half)

            if right > left:
                intervals.append((left, right))

        intervals.sort()

        merged = []
        for left, right in intervals:
            if merged and left <= merged[-1][1]:
                merged[-1] = (
                    merged[-1][0],
                    max(merged[-1][1], right),
                )
            else:
                merged.append((left, right))

        cursor = 0.0

        for left, right in merged:
            if left > cursor:
                self._draw_line(
                    self._interpolate(start, end, cursor),
                    self._interpolate(start, end, left),
                    layer,
                )
            cursor = max(cursor, right)

        if cursor < 1.0:
            self._draw_line(
                self._interpolate(start, end, cursor),
                end,
                layer,
            )

    @staticmethod
    def _interpolate(start, end, t):
        return (
            start[0] + (end[0] - start[0]) * t,
            start[1] + (end[1] - start[1]) * t,
        )

    def _draw_line(self, start, end, layer):
        self.msp.add_line(
            self._xy(start),
            self._xy(end),
            dxfattribs={"layer": layer},
        )

    def _xy(self, point):
        if hasattr(point, "x"):
            return (point.x, point.y)

        return (point[0], point[1])