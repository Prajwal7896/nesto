from dataclasses import dataclass

from .geometry.point import Point


@dataclass
class Furniture:
    type: str
    position: Point
    width: float = 0
    depth: float = 0
    layer: str = "FURNITURE"


class FurnitureGenerator:

    def __init__(self, msp):
        self.msp = msp

    def place_furniture(
        self,
        room_polygon,
        room_type: str = "living"
    ):
        """
        Auto places furniture based on room type.
        """

        if hasattr(room_polygon, "vertices"):
            vertices = room_polygon.vertices
        else:
            vertices = room_polygon

        center = self._centroid(vertices)

        items = []

        if room_type in (
            "bedroom",
            "master_bedroom",
            "guest_room",
            "children_room"
        ):
            items += self._bedroom(center)

        elif room_type == "kitchen":
            items += self._kitchen(center)

        elif room_type in (
            "living",
            "living_room",
            "family_room"
        ):
            items += self._living_room(center)

        elif room_type in (
            "bathroom",
            "attached_bathroom",
            "common_bathroom"
        ):
            items += self._bathroom(center)

        else:
            items += self._generic(center)

        return items


    def _bedroom(self, center):

        items = []

        bed = Furniture(
            "bed",
            center,
            2000,
            1800
        )

        self._draw_rect(
            center,
            2000,
            1800,
            "BED"
        )

        items.append(bed)


        wardrobe_pos = Point(
            center.x + 2500,
            center.y
        )

        wardrobe = Furniture(
            "wardrobe",
            wardrobe_pos,
            2000,
            600
        )

        self._draw_rect(
            wardrobe_pos,
            2000,
            600,
            "WARDROBE"
        )

        items.append(wardrobe)

        return items


    def _kitchen(self, center):

        counter = Furniture(
            "counter",
            center,
            3000,
            600
        )

        self._draw_rect(
            center,
            3000,
            600,
            "KITCHEN"
        )


        sink_pos = Point(
            center.x + 1200,
            center.y
        )

        sink = Furniture(
            "sink",
            sink_pos,
            600,
            600
        )

        self._draw_rect(
            sink_pos,
            600,
            600,
            "SINK"
        )

        return [
            counter,
            sink
        ]


    def _living_room(self, center):

        sofa = Furniture(
            "sofa",
            center,
            2500,
            900
        )

        self._draw_rect(
            center,
            2500,
            900,
            "SOFA"
        )


        table_pos = Point(
            center.x + 1200,
            center.y
        )

        table = Furniture(
            "table",
            table_pos,
            1200,
            800
        )

        self._draw_rect(
            table_pos,
            1200,
            800,
            "TABLE"
        )

        return [
            sofa,
            table
        ]


    def _bathroom(self, center):

        toilet = Furniture(
            "toilet",
            center,
            700,
            400
        )

        self._draw_rect(
            center,
            700,
            400,
            "TOILET"
        )


        basin_pos = Point(
            center.x + 800,
            center.y
        )

        basin = Furniture(
            "basin",
            basin_pos,
            500,
            500
        )

        self._draw_rect(
            basin_pos,
            500,
            500,
            "BASIN"
        )

        return [
            toilet,
            basin
        ]


    def _generic(self, center):

        block = Furniture(
            "block",
            center,
            1000,
            1000
        )

        self._draw_rect(
            center,
            1000,
            1000,
            "BLOCK"
        )

        return [block]


    def _draw_rect(
        self,
        center,
        width,
        depth,
        layer="FURNITURE"
    ):
        x, y = self._to_xy(center)

        w = width / 2
        d = depth / 2

        self.msp.add_lwpolyline(
            [
                (x - w, y - d),
                (x + w, y - d),
                (x + w, y + d),
                (x - w, y + d),
            ],
            close=True,
            dxfattribs={
                "layer": "FURNITURE"
            }
        )


    def _centroid(self, points):

        points = [
            self._to_point(p)
            for p in points
        ]

        x = sum(
            p.x for p in points
        ) / len(points)

        y = sum(
            p.y for p in points
        ) / len(points)

        return Point(x, y)


    def _to_xy(self, p):

        if hasattr(p, "x"):
            return p.x, p.y

        return p[0], p[1]


    def _to_point(self, p):

        if isinstance(p, Point):
            return p

        if hasattr(p, "x"):
            return Point(
                p.x,
                p.y
            )

        return Point(
            p[0],
            p[1]
        )