from dataclasses import dataclass


@dataclass
class Hatch:
    boundary: list
    pattern: str = "ANSI31"
    scale: float = 1.0
    angle: float = 0.0
    layer: str = "HATCH"


class HatchGenerator:

    def __init__(self, msp):
        self.msp = msp

    def create_hatch(
        self,
        polygon,
        pattern: str = "ANSI31",
        scale: float = 1.0,
        angle: float = 0.0,
        layer: str = "HATCH"
    ):

        vertices = self._normalize_polygon(polygon)

        if not vertices or len(vertices) < 3:
            return None  # prevent DXF crash

        hatch = Hatch(
            boundary=vertices,
            pattern=pattern,
            scale=scale,
            angle=angle,
            layer=layer
        )

        self._draw_hatch(vertices, pattern, scale, angle, layer)

        return hatch

    def floor_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="ANSI31",
            scale=50,
            angle=0,
            layer=layer
        )

    def slab_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="AR-CONC",
            scale=100,
            angle=0,
            layer=layer
        )

    def soil_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="EARTH",
            scale=80,
            angle=0,
            layer=layer
        )

    def roof_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="BRICK",
            scale=60,
            angle=0,
            layer=layer
        )

    def insulation_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="ANSI37",
            scale=40,
            angle=45,
            layer=layer
        )

    # -------------------------
    # FIXED CORE LOGIC
    # -------------------------

    def _normalize_polygon(self, polygon):

        if polygon is None:
            return []

        # already list of coordinates
        if isinstance(polygon, list):

            # list of [x, y]
            if len(polygon) > 0 and isinstance(polygon[0], (list, tuple)):
                return polygon

            # list of Point objects
            if len(polygon) > 0 and hasattr(polygon[0], "x"):
                return [(p.x, p.y) for p in polygon]

        # fallback
        if hasattr(polygon, "vertices"):
            verts = polygon.vertices
            return self._normalize_polygon(verts)

        return []

    def _draw_hatch(self, points, pattern, scale, angle, layer):

        if not points:
            return

        hatch = self.msp.add_hatch(
            dxfattribs={
                "layer": layer
            }
        )

        vertices = [
            (x, y)
            for x, y in points
        ]

        hatch.paths.add_polyline_path(
            vertices,
            is_closed=True
        )

        hatch.set_pattern_fill(
            name=pattern,
            scale=scale,
            angle=angle
        )