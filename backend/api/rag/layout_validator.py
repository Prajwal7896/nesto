
from typing import Any, Dict, List, Tuple


class LayoutValidator:
    def __init__(
        self,
        margin: int = 500,
        min_spacing: int = 150,
    ):
        self.margin = margin
        self.min_spacing = min_spacing

    def validate(
        self,
        layout: Dict[str, Any],
        strict_spacing: bool = False,
        constraints: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(layout, dict):
            return self._result(
                False,
                ["Layout must be a dictionary."],
                warnings,
            )

        plot = layout.get("plot")
        rooms = layout.get("rooms")

        if not isinstance(plot, dict):
            return self._result(
                False,
                ["Missing or invalid plot information."],
                warnings,
            )

        if not isinstance(rooms, list):
            return self._result(
                False,
                ["The rooms field must be a list."],
                warnings,
            )

        try:
            plot_width = int(plot["width"])
            plot_height = int(plot["height"])
        except (KeyError, TypeError, ValueError):
            return self._result(
                False,
                ["Plot must contain numeric width and height."],
                warnings,
            )

        if plot_width <= 0 or plot_height <= 0:
            return self._result(
                False,
                ["Plot dimensions must be positive."],
                warnings,
            )

        if not rooms:
            warnings.append("The layout contains no rooms.")
            return self._result(False, errors, warnings)

        valid_rooms: List[Tuple[int, Dict[str, Any]]] = []
        seen_ids = set()

        for index, room in enumerate(rooms):
            label = (
                room.get("name", f"room_{index + 1}")
                if isinstance(room, dict)
                else f"room_{index + 1}"
            )

            if not isinstance(room, dict):
                errors.append(f"{label}: room must be an object.")
                continue

            room_id = room.get("id")
            if room_id:
                if room_id in seen_ids:
                    errors.append(f"{label}: duplicate room ID {room_id}.")
                seen_ids.add(room_id)

            required = ("x", "y", "width", "height")
            missing = [key for key in required if key not in room]

            if missing:
                errors.append(
                    f"{label}: missing fields: {', '.join(missing)}."
                )
                continue

            try:
                x = self._number(room["x"])
                y = self._number(room["y"])
                width = self._number(room["width"])
                height = self._number(room["height"])
            except (TypeError, ValueError):
                errors.append(
                    f"{label}: coordinates and dimensions must be finite numbers."
                )
                continue

            if width <= 0 or height <= 0:
                errors.append(
                    f"{label}: width and height must be positive."
                )
                continue

            if room.get("unplaced", False):
                errors.append(
                    f"{label}: room could not be placed."
                )
                continue

            if x < 0 or y < 0:
                errors.append(
                    f"{label}: room has negative coordinates."
                )

            if x + width > plot_width or y + height > plot_height:
                errors.append(
                    f"{label}: room extends outside the plot boundary."
                )

            if x < self.margin or y < self.margin:
                warnings.append(
                    f"{label}: room is closer than the configured margin "
                    "to the top or left plot edge."
                )

            if (
                x + width > plot_width - self.margin
                or y + height > plot_height - self.margin
            ):
                warnings.append(
                    f"{label}: room is closer than the configured margin "
                    "to the right or bottom plot edge."
                )

            polygon_error = self._validate_polygon(room, x, y, width, height)

            if polygon_error:
                errors.append(f"{label}: {polygon_error}")

            valid_rooms.append(
                (
                    index,
                    {
                        "id": room.get("id"),
                        "name": str(label),
                        "type": room.get("type"),
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                    },
                )
            )

        for i in range(len(valid_rooms)):
            _, room_a = valid_rooms[i]

            for j in range(i + 1, len(valid_rooms)):
                _, room_b = valid_rooms[j]

                if room_a["x"] == room_b["x"] and room_a["y"] == room_b["y"]:
                    errors.append(
                        f"Duplicate room coordinates: {room_a['name']} and "
                        f"{room_b['name']}."
                    )

                if self._overlap(room_a, room_b):
                    errors.append(
                        f"{room_a['name']} overlaps {room_b['name']}."
                    )
                    continue

                distance = self._distance_between(room_a, room_b)
                if distance > 0 and distance < self.min_spacing:
                    message = (
                        f"{room_a['name']} and {room_b['name']} have "
                        f"only {distance:g} units of separation."
                    )

                    if strict_spacing:
                        errors.append(message)
                    else:
                        warnings.append(message)

        circulation_rooms = [
            room
            for _, room in valid_rooms
            if room.get("type") not in {
                "parking",
                "garden",
                "front_lawn",
                "backyard",
            }
        ]
        circulation_ids = {
            room.get("id")
            for room in circulation_rooms
            if room.get("id")
        }
        extra_spaces = []
        for key in ("site_features", "open_spaces"):
            spaces = layout.get(key, [])
            if isinstance(spaces, list):
                extra_spaces.extend(spaces)
        for space in extra_spaces:
            if not isinstance(space, dict):
                continue
            space_id = space.get("id")
            if space_id and space_id in circulation_ids:
                continue
            try:
                x = self._number(space["x"])
                y = self._number(space["y"])
                width = self._number(space["width"])
                height = self._number(space["height"])
            except (KeyError, TypeError, ValueError):
                continue
            if width <= 0 or height <= 0:
                continue
            if space.get("type") in {
                "parking",
                "garden",
                "front_lawn",
                "backyard",
            }:
                continue
            circulation_rooms.append(
                {
                    "id": space_id,
                    "name": str(space.get("name", space.get("type"))),
                    "type": space.get("type"),
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                }
            )
            if space_id:
                circulation_ids.add(space_id)

        if not self._circulation_is_connected(circulation_rooms):
            errors.append(
                "Circulation is disconnected: every planned room and "
                "circulation space must connect to the floor layout."
            )

        unplaced = [
            str(room.get("name", f"room_{index + 1}"))
            for index, room in enumerate(rooms)
            if isinstance(room, dict) and room.get("unplaced", False)
        ]

        if unplaced:
            warnings.append(
                "Unplaced rooms: " + ", ".join(unplaced)
            )

        requested_rooms = (
            constraints.get("space_constraints", {}).get("rooms", {})
            if isinstance(constraints, dict)
            else {}
        )
        if requested_rooms:
            expected_count = self._requested_room_count(requested_rooms)
            if expected_count != len(rooms):
                errors.append(
                    f"Incorrect room count: expected {expected_count}, "
                    f"found {len(rooms)}."
                )
            errors.extend(self._validate_doors(layout, rooms))
        return self._result(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
            extra={
                "plot_area": plot_width * plot_height,
                "room_count": len(rooms),
                "validated_room_count": len(valid_rooms),
                "unplaced_rooms": unplaced,
            },
        )

    
    def _validate_doors(
        self,
        layout: Dict[str, Any],
        rooms: List[Dict[str, Any]],
    ) -> List[str]:
        errors = []
        access_areas = []
        for key in ("site_features", "open_spaces"):
            items = layout.get(key, [])
            if isinstance(items, list):
                access_areas.extend(items)
        room_by_id = {
            room["id"]: room
            for room in rooms + access_areas
            if isinstance(room, dict) and room.get("id")
        }

        doors = layout.get("doors", [])
        if not isinstance(doors, list):
            return ["Doors must be provided as a list."]

        for index, door in enumerate(doors):
            label = f"Door {index + 1}"

            if not isinstance(door, dict):
                errors.append(f"{label}: door must be an object.")
                continue

            first_id = door.get("from_id")
            second_id = door.get("to_id")

            if first_id not in room_by_id or second_id not in room_by_id:
                errors.append(
                    f"{label}: references a missing room."
                )
                continue

            first = room_by_id[first_id]
            second = room_by_id[second_id]

            pair = frozenset((first.get("type"), second.get("type")))

            forbidden_pairs = {
                frozenset(("living_room", "common_bathroom")),
                frozenset(("dining_room", "common_bathroom")),
                frozenset(("master_bedroom", "master_bedroom")),
                frozenset(("bedroom", "bedroom")),
            }

            if pair in forbidden_pairs:
                errors.append(
                    f"{label}: invalid direct connection between "
                    f"{first.get('name', first_id)} and "
                    f"{second.get('name', second_id)}."
                )

            try:
                width = self._number(door["width"])
                position = self._number(door["position"])
            except (KeyError, TypeError, ValueError):
                errors.append(
                    f"{label}: width and position must be finite numbers."
                )
                continue

            if width <= 0:
                errors.append(f"{label}: door width must be positive.")

            if not 0 <= position <= 1:
                errors.append(
                    f"{label}: position must be between 0 and 1."
                )

        return errors

    
    def requested_room_count(self, counts: Dict[str, Any]) -> int:
        return self._requested_room_count(counts)

    def _requested_room_count(self, counts: Dict[str, Any]) -> int:
        bedroom_subtypes = (
            "master_bedrooms",
            "guest_rooms",
            "children_rooms",
        )
        bathroom_subtypes = (
            "attached_bathrooms",
            "common_bathrooms",
        )

        bedrooms = max(
            counts.get("bedrooms") or 0,
            sum(counts.get(name) or 0 for name in bedroom_subtypes),
        )
        bathrooms = max(
            counts.get("bathrooms") or 0,
            sum(counts.get(name) or 0 for name in bathroom_subtypes),
        )

        excluded = {
            "bedrooms",
            *bedroom_subtypes,
            "bathrooms",
            *bathroom_subtypes,
            "family_room_enclosed",
        }

        total = bedrooms + bathrooms

        for name, count in counts.items():
            if name in excluded:
                continue

            if name == "family_room":
                if counts.get("family_room_enclosed"):
                    total += max(count or 0, 1)
                else:
                    total += 0
                continue

            total += count or 0

        return total

    @staticmethod
    def _circulation_is_connected(
        rooms: List[Dict[str, Any]],
    ) -> bool:
        if len(rooms) < 2:
            return True

        adjacency = {index: set() for index in range(len(rooms))}
        tolerance = 1.0
        for first_index, first in enumerate(rooms):
            for second_index in range(first_index + 1, len(rooms)):
                second = rooms[second_index]
                vertical_overlap = min(
                    first["y"] + first["height"],
                    second["y"] + second["height"],
                ) - max(first["y"], second["y"])
                horizontal_overlap = min(
                    first["x"] + first["width"],
                    second["x"] + second["width"],
                ) - max(first["x"], second["x"])
                vertical_contact = (
                    abs(
                        first["x"] + first["width"] - second["x"]
                    ) <= tolerance
                    or abs(
                        second["x"] + second["width"] - first["x"]
                    ) <= tolerance
                ) and vertical_overlap > tolerance
                horizontal_contact = (
                    abs(
                        first["y"] + first["height"] - second["y"]
                    ) <= tolerance
                    or abs(
                        second["y"] + second["height"] - first["y"]
                    ) <= tolerance
                ) and horizontal_overlap > tolerance

                if vertical_contact or horizontal_contact:
                    adjacency[first_index].add(second_index)
                    adjacency[second_index].add(first_index)

        visited = set()
        pending = [0]
        while pending:
            index = pending.pop()
            if index in visited:
                continue
            visited.add(index)
            pending.extend(adjacency[index] - visited)

        return len(visited) == len(rooms)


    def _number(self, value: Any) -> float:
        number = float(value)

        if not __import__("math").isfinite(number):
            raise ValueError("Number must be finite.")

        return number

    def _overlap(
        self,
        a: Dict[str, Any],
        b: Dict[str, Any],
    ) -> bool:
        return (
            a["x"] < b["x"] + b["width"]
            and a["x"] + a["width"] > b["x"]
            and a["y"] < b["y"] + b["height"]
            and a["y"] + a["height"] > b["y"]
        )

    def _distance_between(
        self,
        a: Dict[str, Any],
        b: Dict[str, Any],
    ) -> float:
        horizontal = max(
            0.0,
            b["x"] - (a["x"] + a["width"]),
            a["x"] - (b["x"] + b["width"]),
        )

        vertical = max(
            0.0,
            b["y"] - (a["y"] + a["height"]),
            a["y"] - (b["y"] + b["height"]),
        )

        if horizontal == 0:
            return vertical

        if vertical == 0:
            return horizontal

        return (horizontal**2 + vertical**2) ** 0.5

    def _validate_polygon(
        self,
        room: Dict[str, Any],
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> str | None:
        polygon = room.get("polygon")

        if polygon is None:
            return None

        if not isinstance(polygon, list) or len(polygon) != 4:
            return "polygon must contain four corner points."

        try:
            points = [
                (self._number(point[0]), self._number(point[1]))
                for point in polygon
            ]
        except (TypeError, ValueError, IndexError):
            return "polygon contains invalid coordinates."

        expected = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ]

        if points != expected:
            return "polygon does not match the room's coordinates and dimensions."

        return None

    def _result(
        self,
        is_valid: bool,
        errors: List[str],
        warnings: List[str],
        extra: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        result = {
            "valid": is_valid,
            "status": "valid" if is_valid else "invalid",
            "errors": errors,
            "warnings": warnings,
        }

        if extra:
            result.update(extra)

        return result


validator = LayoutValidator()


def validate_layout(
    layout: Dict[str, Any],
    constraints: Dict[str, Any] | bool | None = None,
    strict_spacing: bool = False,
) -> Dict[str, Any]:
    if isinstance(constraints, bool):
        strict_spacing = constraints
        constraints = None
    return validator.validate(
        layout,
        strict_spacing=strict_spacing,
        constraints=constraints,
    )
