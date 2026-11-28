from dataclasses import dataclass

from .geometry.point import Point


@dataclass
class Slab:
    boundary: list
    thickness: float = 150
    layer: str = "SLAB"


class SlabGenerator:

    def __init__(self, msp):
        self.msp = msp

    def create_slab_from_polygon(
        self,
        polygon,
        thickness=150,
        layer="SLAB"
    ):
        """
        Creates slab from room/boundary polygon.
        """

        slab = Slab(
            boundary=polygon.vertices,
            thickness=thickness,
            layer=layer
        )

        self._draw_boundary(polygon.vertices, layer)

        return slab

    def create_multi_room_slab(
        self,
        polygons,
        thickness=150,
        layer="SLAB"
    ):
        """
        Merges multiple room polygons into one slab system.
        """

        all_vertices = []

        for poly in polygons:
            all_vertices.extend(poly.vertices)

        slab = Slab(
            boundary=all_vertices,
            thickness=thickness,
            layer=layer
        )

        self._draw_boundary(all_vertices, layer)

        return slab

    def create_offset_slab(
        self,
        polygon,
        offset=200,
        thickness=150,
        layer="SLAB"
    ):
        """
        Creates slab with offset (for balconies / terraces).
        """

        offset_vertices = self._offset_polygon(
            polygon.vertices,
            offset
        )

        slab = Slab(
            boundary=offset_vertices,
            thickness=thickness,
            layer=layer
        )

        self._draw_boundary(offset_vertices, layer)

        return slab

    def create_slab_opening(
        self,
        slab_polygon,
        opening_polygon,
        layer="SLAB"
    ):
        """
        Creates a slab with a void (staircase opening / shaft).
        """

        self._draw_boundary(slab_polygon.vertices, layer)
        self._draw_boundary(opening_polygon.vertices, layer)

        return {
            "slab": slab_polygon,
            "opening": opening_polygon
        }

    def _draw_boundary(self, points, layer):

        n = len(points)

        for i in range(n):

            a = points[i]
            b = points[(i + 1) % n]

            self.msp.add_line(
                (a.x, a.y),
                (b.x, b.y),
                dxfattribs={"layer": layer},
            )

    def _offset_polygon(self, points, offset):

        """
        Simple geometric offset (basic version).
        For production, replace with robust polygon offset algorithm.
        """

        cx = sum(p.x for p in points) / len(points)
        cy = sum(p.y for p in points) / len(points)

        offset_points = []

        for p in points:

            dx = p.x - cx
            dy = p.y - cy

            length = (dx ** 2 + dy ** 2) ** 0.5

            if length == 0:
                offset_points.append(p)
                continue

            ux = dx / length
            uy = dy / length

            offset_points.append(
                Point(
                    p.x + ux * offset,
                    p.y + uy * offset
                )
            )

        return offset_points