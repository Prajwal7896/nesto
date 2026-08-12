import math


class SymbolLibrary:

    def __init__(self, msp):
        self.msp = msp

    def north_arrow(
        self,
        x,
        y,
        size=500,
        layer="ANNOTATION"
    ):

        self.msp.add_line(
            (x, y),
            (x, y + size),
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            (x, y + size),
            (x - size * 0.15, y + size * 0.75),
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            (x, y + size),
            (x + size * 0.15, y + size * 0.75),
            dxfattribs={"layer": layer},
        )

        self.msp.add_text(
            "N",
            height=size * 0.20,
            dxfattribs={"layer": layer},
        ).set_placement(
            (x, y + size + size * 0.10)
        )

    def column(
        self,
        x,
        y,
        size=300,
        layer="STRUCTURE"
    ):

        self.msp.add_lwpolyline(
            [
                (x, y),
                (x + size, y),
                (x + size, y + size),
                (x, y + size),
            ],
            close=True,
            dxfattribs={"layer": layer},
        )

    def door_swing(
        self,
        hinge,
        radius,
        start_angle,
        end_angle,
        layer="DOORS"
    ):

        self.msp.add_arc(
            center=hinge,
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
            dxfattribs={"layer": layer},
        )

    def window(
        self,
        start,
        end,
        layer="WINDOWS"
    ):

        self.msp.add_line(
            start,
            end,
            dxfattribs={"layer": layer},
        )

    def sink(
        self,
        x,
        y,
        radius=200,
        layer="FURNITURE"
    ):

        self.msp.add_circle(
            (x, y),
            radius,
            dxfattribs={"layer": layer},
        )

    def toilet(
        self,
        x,
        y,
        layer="FURNITURE"
    ):

        self.msp.add_circle(
            (x, y),
            170,
            dxfattribs={"layer": layer},
        )

        self.msp.add_circle(
            (x, y + 220),
            110,
            dxfattribs={"layer": layer},
        )

    def staircase_arrow(
        self,
        start,
        end,
        layer="STAIRCASE"
    ):

        self.msp.add_line(
            start,
            end,
            dxfattribs={"layer": layer},
        )

        angle = math.atan2(
            end[1] - start[1],
            end[0] - start[0],
        )

        head = 120

        left = (
            end[0] - head * math.cos(angle - 0.5),
            end[1] - head * math.sin(angle - 0.5),
        )

        right = (
            end[0] - head * math.cos(angle + 0.5),
            end[1] - head * math.sin(angle + 0.5),
        )

        self.msp.add_line(
            end,
            left,
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            end,
            right,
            dxfattribs={"layer": layer},
        )

    def electrical_socket(
        self,
        x,
        y,
        radius=60,
        layer="ELECTRICAL"
    ):

        self.msp.add_circle(
            (x, y),
            radius,
            dxfattribs={"layer": layer},
        )

    def light(
        self,
        x,
        y,
        radius=100,
        layer="ELECTRICAL"
    ):

        self.msp.add_circle(
            (x, y),
            radius,
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            (x - radius, y),
            (x + radius, y),
            dxfattribs={"layer": layer},
        )

        self.msp.add_line(
            (x, y - radius),
            (x, y + radius),
            dxfattribs={"layer": layer},
        )