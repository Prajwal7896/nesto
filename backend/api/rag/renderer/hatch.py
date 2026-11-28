
from dataclasses import dataclass


@dataclass
class Hatch:
    boundary: list
    pattern: str = "ANSI31"
    scale: float = 1.0
    angle: float = 0.0
    layer: str = "HATCH"
    color: str | None = None


class HatchGenerator:

    def __init__(self, msp):
        self.msp = msp

    @staticmethod
    def _hex_to_rgb(color):
        """Convert #RRGGBB into an RGB integer supported by DXF."""
        if not isinstance(color, str):
            raise ValueError("Color must be a hexadecimal string.")

        color = color.strip().lstrip("#")

        if len(color) != 6:
            raise ValueError("Color must use the format #RRGGBB.")

        try:
            return int(color, 16)
        except ValueError as exc:
            raise ValueError(f"Invalid hexadecimal color: {color}") from exc

    def _normalize_polygon(self, polygon):

        if polygon is None:
            return []

        if hasattr(polygon, "vertices"):
            polygon = polygon.vertices

        if not isinstance(polygon, (list, tuple)):
            return []

        vertices = []

        for point in polygon:
            if hasattr(point, "x") and hasattr(point, "y"):
                vertices.append((float(point.x), float(point.y)))
            elif isinstance(point, (list, tuple)) and len(point) >= 2:
                vertices.append((float(point[0]), float(point[1])))

        return vertices

    def create_hatch(
        self,
        polygon,
        pattern="ANSI31",
        scale=1.0,
        angle=0.0,
        layer="HATCH",
        color=None,
    ):

        vertices = self._normalize_polygon(polygon)

        if len(vertices) < 3:
            return None

        rgb = self._hex_to_rgb(color) if color else None

        hatch = self.msp.add_hatch(
            color=7,
            dxfattribs={"layer": layer},
        )

        hatch.paths.add_polyline_path(
            vertices,
            is_closed=True,
        )

        if pattern.upper() == "SOLID":
            hatch.set_solid_fill(color=7)
        else:
            hatch.set_pattern_fill(
                name=pattern,
                scale=scale,
                angle=angle,
            )

        if rgb is not None:
            hatch.dxf.true_color = rgb

        return Hatch(
            boundary=vertices,
            pattern=pattern,
            scale=scale,
            angle=angle,
            layer=layer,
            color=color,
        )

    def floor_hatch(
        self,
        polygon,
        layer="HATCH",
        color="#E8E8E8",
        pattern="SOLID",
    ):
        return self.create_hatch(
            polygon,
            pattern=pattern,
            scale=50,
            angle=0,
            layer=layer,
            color=color,
        )

    def slab_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="AR-CONC",
            scale=100,
            angle=0,
            layer=layer,
        )

    def soil_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="EARTH",
            scale=80,
            angle=0,
            layer=layer,
        )

    def roof_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="BRICK",
            scale=60,
            angle=0,
            layer=layer,
        )

    def insulation_hatch(self, polygon, layer="HATCH"):
        return self.create_hatch(
            polygon,
            pattern="ANSI37",
            scale=40,
            angle=45,
            layer=layer,
        )
