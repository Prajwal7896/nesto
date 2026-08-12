from copy import deepcopy
from typing import Any, Dict


class LayoutOptimizer:

    def optimize(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        layout = deepcopy(layout)

        # safety
        if "metadata" not in layout:
            layout["metadata"] = {}

        if "rooms" not in layout:
            layout["rooms"] = []

        if "plot" not in layout:
            layout["plot"] = {
                "width": 12000,
                "height": 18000,
            }

        self._place_rooms(layout)
        self._resolve_overlaps(layout)
        self._fit_inside_plot(layout)
        self._update_polygons(layout)

        layout["metadata"]["status"] = "optimized"

        return layout

    def _place_rooms(self, layout: Dict[str, Any]) -> None:
        x = 500
        y = 500
        row_height = 0
        plot_width = layout["plot"]["width"]

        for room in layout["rooms"]:
            width = room["width"]
            height = room["height"]

            if x + width > plot_width - 500:
                x = 500
                y += row_height + 500
                row_height = 0

            room["x"] = x
            room["y"] = y

            x += width + 500
            row_height = max(row_height, height)

    def _resolve_overlaps(self, layout: Dict[str, Any]) -> None:
        rooms = layout["rooms"]

        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                r1 = rooms[i]
                r2 = rooms[j]

                attempts = 0

                while self._overlap(r1, r2) and attempts < 10:
                    r2["x"] += 500
                    attempts += 1

    def _fit_inside_plot(self, layout: Dict[str, Any]) -> None:
        plot_w = layout["plot"]["width"]
        plot_h = layout["plot"]["height"]

        for room in layout["rooms"]:
            if room["x"] + room["width"] > plot_w:
                room["x"] = max(
                    500,
                    plot_w - room["width"] - 500,
                )

            if room["y"] + room["height"] > plot_h:
                room["y"] = max(
                    500,
                    plot_h - room["height"] - 500,
                )

    def _update_polygons(self, layout: Dict[str, Any]) -> None:
        for room in layout["rooms"]:
            x = room["x"]
            y = room["y"]
            w = room["width"]
            h = room["height"]

            room["polygon"] = [
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h],
            ]

    def _overlap(self, a: Dict[str, Any], b: Dict[str, Any]) -> bool:
        return not (
            a["x"] + a["width"] <= b["x"]
            or b["x"] + b["width"] <= a["x"]
            or a["y"] + a["height"] <= b["y"]
            or b["y"] + b["height"] <= a["y"]
        )


optimizer = LayoutOptimizer()


def optimize(layout: Dict[str, Any]) -> Dict[str, Any]:
    return optimizer.optimize(layout)