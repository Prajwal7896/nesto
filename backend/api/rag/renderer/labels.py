from dataclasses import dataclass

from .geometry.point import Point


@dataclass
class Label:
    text: str
    position: Point
    height: float = 200
    layer: str = "LABELS"


class LabelGenerator:

    def __init__(self, msp):
        self.msp = msp

    def _to_point(self, p):
        return p if hasattr(p, "x") else Point(p[0], p[1])
    
    def add_room_label(
        self,
        room_polygon,
        name: str,
        layer: str = "LABELS"
    ):

        vertices = [
            self._to_point(p) for p in room_polygon.vertices
        ]

        center = self._centroid(vertices)

        label = Label(
            text=name,
            position=center,
            height=250,
            layer=layer
        )

        self._draw_text(label)

        return label

    def add_area_label(
        self,
        room_polygon,
        area: float,
        layer: str = "LABELS"
    ):

        vertices = (
            room_polygon.vertices
            if hasattr(room_polygon, "vertices")
            else room_polygon
        )

        center = self._centroid(vertices)

        text = f"{area:.2f} m²"

        label = Label(
            text=text,
            position=center,
            height=180,
            layer=layer
        )

        self._draw_text(label)

        return label

    def add_title_block(
        self,
        position: Point,
        title: str,
        subtitle: str = "",
        layer: str = "LABELS"
    ):
        """
        Adds sheet title block.
        """

        self._draw_text(
            Label(title, position, 300, layer)
        )

        if subtitle:

            sub_pos = Point(
                position.x,
                position.y - 400
            )

            self._draw_text(
                Label(subtitle, sub_pos, 180, layer)
            )

    def add_north_label(
        self,
        position: Point,
        layer: str = "LABELS"
    ):
        """
        North direction indicator text.
        """

        label = Label(
            text="NORTH ↑",
            position=position,
            height=220,
            layer=layer
        )

        self._draw_text(label)

        return label

    def add_custom_label(
        self,
        text: str,
        position: Point,
        height: float = 200,
        layer: str = "LABELS"
    ):
        """
        Generic annotation label.
        """

        label = Label(
            text=text,
            position=position,
            height=height,
            layer=layer
        )

        self._draw_text(label)

        return label

    def _draw_text(self, label: Label):
        
        x, y = (
            (label.position.x, label.position.y)
            if hasattr(label.position, "x")
            else label.position
        )

        self.msp.add_text(
            label.text,
            dxfattribs={
                "layer": label.layer,
                "height": label.height
            }
        ).set_placement((x, y))

    def _centroid(self, points):
        points = [self._to_point(p) for p in points]

        x = sum(p.x for p in points) / len(points)
        y = sum(p.y for p in points) / len(points)

        return Point(x, y)