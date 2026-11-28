"""Unified coordinate conversion for Nesto 2D and Three.js."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple


@dataclass(frozen=True)
class CoordinateSystem:
    source_unit: str = "mm"
    world_unit: str = "m"
    centered: bool = False

    def __post_init__(self):
        if self.source_unit != "mm" or self.world_unit != "m":
            raise ValueError("Only mm-to-m conversion is supported.")

    @property
    def scale(self) -> float:
        return 0.001

    @staticmethod
    def _finite(value, name: str) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a finite number.") from exc

        if not __import__("math").isfinite(number):
            raise ValueError(f"{name} must be a finite number.")

        return number

    def length(self, value: float) -> float:
        return self._finite(value, "length") * self.scale

    def point(
        self,
        x: float,
        y: float,
        *,
        plot_width: float = 0.0,
        plot_height: float = 0.0,
        elevation: float = 0.0,
    ) -> Tuple[float, float, float]:

        x = self._finite(x, "x")
        y = self._finite(y, "y")
        elevation = self._finite(elevation, "elevation")

        if self.centered:
            x -= self._finite(plot_width, "plot_width") / 2
            y -= self._finite(plot_height, "plot_height") / 2

        return (
            x * self.scale,
            elevation * self.scale,
            y * self.scale,
        )

    def vector(self, dx: float, dy: float) -> Tuple[float, float]:
        return (
            self._finite(dx, "dx") * self.scale,
            self._finite(dy, "dy") * self.scale,
        )

    def dimensions(self, width: float, depth: float) -> Tuple[float, float]:
        return self.length(width), self.length(depth)

    def polygon(
        self,
        vertices: Iterable[Sequence[float]],
        *,
        plot_width: float = 0.0,
        plot_height: float = 0.0,
        elevation: float = 0.0,
    ) -> list[Tuple[float, float, float]]:

        return [
            self.point(
                vertex[0],
                vertex[1],
                plot_width=plot_width,
                plot_height=plot_height,
                elevation=elevation,
            )
            for index, vertex in enumerate(vertices)
            if len(vertex) >= 2
        ]
