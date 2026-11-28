from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


ROOM_DIMENSIONS = {
    "living_room": (4800, 4200),
    "family_room": (4200, 3600),
    "master_bedroom": (4200, 4200),
    "bedroom": (3600, 3600),
    "guest_room": (3600, 3300),
    "children_room": (3600, 3300),
    "bathroom": (2100, 1500),
    "attached_bathroom": (2100, 1500),
    "common_bathroom": (2100, 1500),
    "kitchen": (3000, 3000),
    "dining_room": (3600, 3000),
    "pooja_room": (1800, 1800),
    "study_room": (3000, 2700),
    "office": (3600, 3000),
    "library": (3600, 3000),
    "gym": (3600, 3000),
    "home_theatre": (4200, 3600),
    "balcony": (3000, 1500),
    "utility_room": (2400, 1800),
    "laundry_room": (2400, 1800),
    "store_room": (1800, 1800),
    "walk_in_closet": (2100, 1800),
}

SITE_FEATURE_DIMENSIONS = {
    "staircase": (2500, 4000),
    "staircase_landing": (2500, 1500),
    "circulation": (1200, 4000),
    "front_porch": (3000, 1800),
}

BEDROOM_SUBTYPE_COUNTS = ("master_bedrooms", "guest_rooms", "children_rooms")
BATHROOM_SUBTYPE_COUNTS = ("attached_bathrooms", "common_bathrooms")

ROOM_TYPE_ALIASES = {
    "family lounge": "family_room",
    "family_lounge": "family_room",
}

DOOR_ALLOWED_PAIRS = frozenset({
    frozenset(("living_room", "dining_room")),
    frozenset(("living_room", "kitchen")),
    frozenset(("dining_room", "kitchen")),
    frozenset(("living_room", "family_room")),
    frozenset(("family_room", "dining_room")),
    frozenset(("master_bedroom", "attached_bathroom")),
    frozenset(("bedroom", "attached_bathroom")),
    frozenset(("guest_room", "attached_bathroom")),
    frozenset(("children_room", "attached_bathroom")),
    frozenset(("master_bedroom", "bathroom")),
    frozenset(("bedroom", "bathroom")),
    frozenset(("guest_room", "bathroom")),
    frozenset(("children_room", "bathroom")),
    frozenset(("master_bedroom", "balcony")),
    frozenset(("bedroom", "balcony")),
    frozenset(("guest_room", "balcony")),
    frozenset(("children_room", "balcony")),
    frozenset(("pooja_room", "living_room")),
    frozenset(("office", "living_room")),
})

DOOR_FORBIDDEN_PAIRS = frozenset({
    frozenset(("living_room", "common_bathroom")),
    frozenset(("dining_room", "common_bathroom")),
    frozenset(("master_bedroom", "master_bedroom")),
    frozenset(("bedroom", "bedroom")),
    frozenset(("master_bedroom", "bedroom")),
    frozenset(("master_bedroom", "guest_room")),
    frozenset(("master_bedroom", "children_room")),
})


def _canonical_room_type(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "_")
    return ROOM_TYPE_ALIASES.get(normalized, normalized)


class LayoutPlanner:
    def generate_layout(
        self,
        constraints: Dict[str, Any],
        retry_seed: int = 0,
    ) -> Dict[str, Any]:
        del retry_seed
        space = constraints["space_constraints"]
        plot_width = float(space["plot_width"])
        plot_height = float(space["plot_height"])

        if plot_width <= 0 or plot_height <= 0:
            raise ValueError("Plot dimensions must be positive millimetre values.")

        building = constraints.get("building_constraints", {})
        floor_count = building.get("floors", 1) or 1
        if not isinstance(floor_count, int) or floor_count < 1:
            raise ValueError("Building floor count must be a positive integer.")
        if floor_count > 2:
            raise ValueError(
                f"Cannot generate {floor_count} floors: this planner supports "
                "ground and first floors only."
            )

        room_counts = dict(space.get("rooms") or {})
        canonical_room_counts = {}
        for room_type, count in room_counts.items():
            canonical = _canonical_room_type(room_type)
            if canonical in canonical_room_counts and count is not None:
                canonical_room_counts[canonical] += count
            else:
                canonical_room_counts[canonical] = count
        room_counts = canonical_room_counts
        floor_allocations = space.get("floor_allocations")
        if floor_allocations is None:
            floor_allocations = room_counts.pop("floor_allocations", None)

        if floor_allocations is not None:
            floor_allocations = self._normalize_floor_allocations(floor_allocations)

        family_lounge_allocations = None
        if (
            floor_count == 2
            and floor_allocations is not None
            and not room_counts.get("family_room_enclosed", False)
        ):
            family_lounge_allocations = {
                floor: counts.pop("family_room", 0)
                for floor, counts in floor_allocations.items()
            }
            for floor_name, count in family_lounge_allocations.items():
                if (
                    not isinstance(count, int)
                    or isinstance(count, bool)
                    or count < 0
                ):
                    raise ValueError(
                        "Family lounge allocations must be non-negative integers."
                    )
            lounge_total = sum(family_lounge_allocations.values())
            requested_lounges = room_counts.get("family_room", 0) or 0
            if lounge_total and lounge_total != requested_lounges:
                raise ValueError(
                    "Floor allocations for family lounge must match the "
                    f"requested family_room count ({requested_lounges}); "
                    f"found {lounge_total}."
                )
            if not lounge_total:
                family_lounge_allocations = None

        rooms = self._requested_rooms(room_counts)
        if not rooms:
            raise ValueError("At least one room must be requested.")

        if floor_count == 2:
            ground_rooms, first_rooms = self._split_two_floor_rooms(
                rooms,
                floor_allocations,
            )
        else:
            if floor_allocations is None:
                ground_rooms, first_rooms = rooms, []
            else:
                ground_rooms, first_rooms = self._split_two_floor_rooms(
                    rooms,
                    floor_allocations,
                )
                if first_rooms:
                    raise ValueError(
                        "A one-floor building cannot allocate rooms to first_floor."
                    )

                
        parking = building.get("parking", {})
        ground_features = self._site_features(
            floor="ground_floor",
            floor_count=floor_count,
            parking=parking,
            staircase_required=building.get("staircase", floor_count > 1),
            front_porch_required=building.get("front_porch", False),
            family_lounge_count=(
                room_counts.get("family_room", 0) or 0
                if not room_counts.get("family_room_enclosed", False)
                and floor_count == 1
                else 0
            ),
        )

        first_floor_layout = None

        def place_supported_first_floor(
            ground_placed: Sequence[Dict[str, Any]],
        ) -> bool:
            nonlocal first_floor_layout
            stair = next(
                feature for feature in ground_placed
                if feature.get("type") == "staircase"
            )
            first_features = self._site_features(
                floor="first_floor",
                floor_count=floor_count,
                parking={},
                staircase_required=True,
                fixed_staircase=(stair["x"], stair["y"]),
                front_porch_required=False,
                family_lounge_count=(
                    (
                        family_lounge_allocations.get("first_floor", 0)
                        if family_lounge_allocations
                        else room_counts.get("family_room", 0) or 0
                    )
                    if not room_counts.get("family_room_enclosed", False)
                    else 0
                ),
            )
            support_footprint = [
                *[
                    item for item in ground_placed
                    if item.get("kind") not in ("site_feature", "open_space")
                    and item.get("type") != "balcony"
                ],
                *[
                    item for item in ground_placed
                    if item.get("kind") == "site_feature"
                    and item.get("type") != "parking"
                ],
                *[
                    item for item in ground_placed
                    if item.get("kind") == "open_space"
                ],
            ]
            try:
                first_floor_layout = self._create_floor(
                    "first_floor",
                    first_rooms,
                    first_features,
                    plot_width,
                    plot_height,
                    constraints,
                    support_footprint=support_footprint,
                )
            except ValueError as error:
                if not str(error).startswith(
                    "Unable to place requirements on first floor:"
                ):
                    raise
                first_floor_layout = None
                return False
            return True

        # Generate the ground floor while checking upper-floor feasibility.
        ground = self._create_floor(
            "ground_floor",
            ground_rooms,
            ground_features,
            plot_width,
            plot_height,
            constraints,
            completion_check=(
                place_supported_first_floor if floor_count == 2 else None
            ),
        )

        floors = {"ground_floor": ground}

        # Generate first floor only for a two-floor building
        if floor_count == 2:
            if first_floor_layout is None:
                raise RuntimeError(
                    "Ground-floor placement completed without a supported "
                    "first-floor layout."
                )
            floors["first_floor"] = first_floor_layout

        self.validate_generated_structure(floors, constraints)

        result = dict(ground)
        result["floors"] = floors
        result["room_count"] = sum(len(floor["rooms"]) for floor in floors.values())
        result["total_area"] = sum(
            room["area"]
            for floor in floors.values()
            for room in floor["rooms"]
        )
        result["floor_count"] = floor_count
        result["family_lounge"] = bool(
            room_counts.get("family_room")
            and not room_counts.get("family_room_enclosed", False)
        )
        return result

    def validate_generated_structure(
        self,
        floors: Dict[str, Dict[str, Any]],
        constraints: Dict[str, Any],
    ) -> None:
        if "first_floor" not in floors:
            return

        ground = floors["ground_floor"]
        first = floors["first_floor"]
        ground_stairs = [
            item
            for item in ground["site_features"]
            if item.get("type") == "staircase"
        ]
        first_stairs = [
            item
            for item in first["site_features"]
            if item.get("type") == "staircase"
        ]
        if len(ground_stairs) != 1 or len(first_stairs) != 1:
            raise ValueError(
                "Two-floor layouts require exactly one staircase on each floor."
            )

        stair_fields = ("x", "y", "width", "height")
        if any(
            ground_stairs[0].get(field) != first_stairs[0].get(field)
            for field in stair_fields
        ):
            raise ValueError(
                "The first-floor staircase is not aligned with the ground-floor "
                "staircase."
            )

        landings = [
            item
            for item in first["site_features"]
            if item.get("type") == "staircase_landing"
        ]
        if len(landings) != 1 or not self._contact_length(
            landings[0]["x"],
            landings[0]["y"],
            landings[0]["width"],
            landings[0]["height"],
            first_stairs,
        ):
            raise ValueError(
                "The first floor must contain a landing adjoining the staircase."
            )

        lower_support = [
            item
            for item in (
                ground["rooms"]
                + ground["site_features"]
                + ground["open_spaces"]
            )
            if item.get("type") not in {"parking", "balcony"}
        ]
        cantilever_supported = (
            constraints.get("structural_constraints", {}).get(
                "balcony_cantilever_supported"
            )
            is True
        )
        for item in first["rooms"] + first["site_features"] + first["open_spaces"]:
            if item.get("type") == "staircase":
                continue
            if item.get("type") == "balcony" and cantilever_supported:
                continue
            if not self._within_support_footprint(
                item["x"],
                item["y"],
                item["width"],
                item["height"],
                lower_support,
            ):
                raise ValueError(
                    f"First-floor {item.get('type', item.get('name'))} is not "
                    "supported by the ground-floor layout."
                )

    def validate_floor_circulation(
        self,
        floor: Dict[str, Any],
    ) -> bool:
        rooms = floor.get("rooms", [])
        access_areas = self._circulation_access_areas(
            floor.get("site_features", [])
            + floor.get("open_spaces", [])
        )
        return self._door_graph_connected(
            rooms,
            access_areas,
            floor.get("doors", []),
        )


    def _optimize_floor_dimensions(
        self,
        specs: List[Dict[str, Any]],
        plot_width: float,
        plot_height: float,
    ) -> None:
        plot_area = plot_width * plot_height

        if self._required_area(specs) <= plot_area:
            return

        fixed_specs = [
            spec for spec in specs
            if spec.get("kind") in ("site_feature", "open_space")
            or spec.get("type") == "parking"
        ]

        flexible_specs = [
            spec for spec in specs
            if not (
                spec.get("kind") in ("site_feature", "open_space")
                or spec.get("type") == "parking"
            )
        ]

        fixed_area = self._required_area(fixed_specs)
        flexible_area = self._required_area(flexible_specs)

        target_area = plot_area * 0.95
        available_room_area = target_area - fixed_area

        if available_room_area <= 0 or flexible_area <= 0:
            raise ValueError(
                "Fixed site features leave insufficient space for rooms."
            )

        scale = min(1.0, (available_room_area / flexible_area) ** 0.5)

        if scale < 0.90:
            raise ValueError(
                "The requested layout cannot fit while preserving minimum "
                "room dimensions. Increase the plot size or reduce rooms."
            )

        for spec in flexible_specs:
            original_width = spec["width"]
            original_height = spec["height"]

            min_width = int(original_width * 0.90 / 50) * 50
            min_height = int(original_height * 0.90 / 50) * 50

            spec["width"] = max(
                min_width,
                int(original_width * scale / 50) * 50,
            )

            spec["height"] = max(
                min_height,
                int(original_height * scale / 50) * 50,
            )

    def _create_floor(
        self,
        floor_name: str,
        room_specs: Sequence[Dict[str, Any]],
        feature_specs: Sequence[Dict[str, Any]],
        plot_width: float,
        plot_height: float,
        constraints: Dict[str, Any],
        support_footprint: Optional[Sequence[Dict[str, Any]]] = None,
        completion_check: Optional[
            Callable[[Sequence[Dict[str, Any]]], bool]
        ] = None,
    ) -> Dict[str, Any]:
        specs = [dict(spec) for spec in feature_specs]
        specs.extend(dict(spec) for spec in room_specs)

        self._optimize_floor_dimensions(
            specs,
            plot_width,
            plot_height,
        )
        cantilever_supported = (
            constraints.get("structural_constraints", {}).get(
                "balcony_cantilever_supported"
            )
            is True
        )
        if cantilever_supported:
            for spec in specs:
                if spec.get("type") == "balcony":
                    spec["cantilever_supported"] = True
        specs.sort(
            key=lambda item: (
                {"site_feature": 0, "open_space": 1}.get(
                    item.get("kind"), 2
                ),
                -(item["width"] * item["height"]),
                item["id"],
            )
        )
        if self._required_area(specs) > plot_width * plot_height:
            self._raise_placement_error(
                floor_name, specs, plot_width, plot_height
            )

        completed_geometry = None

        def complete_floor(placed: Sequence[Dict[str, Any]]) -> bool:
            nonlocal completed_geometry
            completed_geometry = None

            circulation_nodes = [
                item for item in placed if item.get("type") != "parking"
            ]
            all_connections = self.create_adjacency(circulation_nodes)
            adjacency = {item["id"]: set() for item in circulation_nodes}
            for connection in all_connections:
                adjacency[connection["from_id"]].add(connection["to_id"])
                adjacency[connection["to_id"]].add(connection["from_id"])
            if not self._graph_connected(adjacency):
                return False

            rooms = [
                item for item in placed
                if item.get("kind") not in ("site_feature", "open_space")
            ]
            room_ids = {room["id"] for room in rooms}
            room_connections = [
                connection for connection in all_connections
                if connection["from_id"] in room_ids
                and connection["to_id"] in room_ids
            ]
            access_areas = self._circulation_access_areas(placed)
            doors, windows = self._openings(
                rooms,
                room_connections,
                plot_width,
                plot_height,
                access_areas,
            )
            if not self._door_graph_connected(rooms, access_areas, doors):
                return False
            if completion_check is not None and not completion_check(placed):
                return False

            completed_geometry = {
                "rooms": rooms,
                "site_features": [
                    item for item in placed if item.get("kind") == "site_feature"
                ],
                "open_spaces": [
                    item for item in placed if item.get("kind") == "open_space"
                ],
                "connections": room_connections,
                "access_areas": access_areas,
                "doors": doors,
                "windows": windows,
                "circulation_connections": self._circulation_connections(
                    rooms,
                    access_areas,
                    doors,
                ),
            }
            return True

        placed = self._pack_rooms(
            specs,
            plot_width,
            plot_height,
            support_footprint=support_footprint,
            completion_check=complete_floor,
        )
        if placed is None:
            self._raise_placement_error(
                floor_name, specs, plot_width, plot_height
            )

        if completed_geometry is None:
            raise RuntimeError("Accepted floor placement lacks validated geometry.")
        rooms = completed_geometry["rooms"]
        site_features = completed_geometry["site_features"]
        open_spaces = completed_geometry["open_spaces"]
        connections = completed_geometry["connections"]
        doors = completed_geometry["doors"]
        windows = completed_geometry["windows"]
        circulation_connections = completed_geometry["circulation_connections"]
        return {
            "floor": floor_name,
            "plot": {"width": plot_width, "height": plot_height},
            "rooms": rooms,
            "site_features": site_features,
            "open_spaces": open_spaces,
            "adjacency_graph": connections,
            "circulation": {
                "ventilation": True,
                "privacy": True,
                "connected": True,
            },
            "doors": doors,
            "windows": windows,
            "structure": {
                "beam_type": constraints.get("structural_constraints", {}).get(
                    "beam_type", "RCC"
                ),
                "column_type": constraints.get("structural_constraints", {}).get(
                    "column_type", "RCC"
                ),
            },
            "engineering": {"electrical": True, "plumbing": True},
            "connections": circulation_connections,
            "connections_count": len(circulation_connections),
            "room_count": len(rooms),
            "total_area": sum(room["area"] for room in rooms),
            "generated": True,
            "planner_version": "v5",
            "metadata": {
                "planner": "Nesto Smart Planner",
                "status": "draft",
                "coordinate_unit": "mm",
            },
        }

    def _split_two_floor_rooms(
        self,
        rooms: Sequence[Dict[str, Any]],
        floor_allocations: Optional[Dict[str, Dict[str, int]]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if floor_allocations is not None:
            if not isinstance(floor_allocations, dict):
                raise ValueError("Floor allocations must be a floor-to-room-count mapping.")

            unsupported_floors = set(floor_allocations) - {
                "ground_floor",
                "first_floor",
            }
            if unsupported_floors:
                raise ValueError(
                    "Unsupported floor allocation(s): "
                    + ", ".join(sorted(unsupported_floors))
                )

            requested = Counter(room["type"] for room in rooms)
            allocated: Counter[str] = Counter()
            allocated_rooms = {
                "ground_floor": [],
                "first_floor": [],
            }
            rooms_by_type: Dict[str, List[Dict[str, Any]]] = {}
            for room in rooms:
                rooms_by_type.setdefault(room["type"], []).append(room)

            for floor_name in ("ground_floor", "first_floor"):
                counts = floor_allocations.get(floor_name, {})
                if not isinstance(counts, dict):
                    raise ValueError(
                        f"Room allocations for {floor_name} must be a mapping."
                    )

                for room_type, count in counts.items():
                    if room_type not in ROOM_DIMENSIONS:
                        raise ValueError(
                            f"Unsupported allocated room type: {room_type}"
                        )
                    if (
                        not isinstance(count, int)
                        or isinstance(count, bool)
                        or count < 0
                    ):
                        raise ValueError(
                            f"Allocation for {room_type} on {floor_name} "
                            "must be a non-negative integer."
                        )

                    available = rooms_by_type.get(room_type, [])
                    start = allocated[room_type]
                    end = start + count
                    if end > len(available):
                        raise ValueError(
                            f"Floor allocations request too many {room_type} rooms."
                        )
                    allocated_rooms[floor_name].extend(available[start:end])
                    allocated[room_type] = end

            if allocated != requested:
                missing = requested - allocated
                extra = allocated - requested
                details = []
                if missing:
                    details.append(
                        "unallocated: "
                        + ", ".join(
                            f"{room_type}={count}"
                            for room_type, count in sorted(missing.items())
                        )
                    )
                if extra:
                    details.append(
                        "overallocated: "
                        + ", ".join(
                            f"{room_type}={count}"
                            for room_type, count in sorted(extra.items())
                        )
                    )
                raise ValueError(
                    "Floor allocations do not match requested room counts ("
                    + "; ".join(details)
                    + ")."
                )

            return allocated_rooms["ground_floor"], allocated_rooms["first_floor"]

        ground_types = {
            "living_room", "kitchen", "dining_room", "guest_room",
            "common_bathroom", "office", "pooja_room",
        }
        ground: List[Dict[str, Any]] = []
        first: List[Dict[str, Any]] = []
        for room in rooms:
            (ground if room["type"] in ground_types else first).append(room)
        return ground, first

    def _normalize_floor_allocations(
        self,
        floor_allocations: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, int]]:
        if not isinstance(floor_allocations, dict):
            raise ValueError("Floor allocations must be a floor-to-room-count mapping.")
        normalized = {}
        for floor_name, counts in floor_allocations.items():
            if not isinstance(counts, dict):
                normalized[floor_name] = counts
                continue
            canonical_counts = {}
            for room_type, count in counts.items():
                canonical = _canonical_room_type(room_type)
                canonical_counts[canonical] = canonical_counts.get(canonical, 0) + count
            normalized[floor_name] = canonical_counts
        return normalized

    def _site_features(
        self,
        floor: str,
        floor_count: int,
        parking: Dict[str, Any],
        staircase_required: bool,
        front_porch_required: bool,
        fixed_staircase: Optional[Tuple[float, float]] = None,
        family_lounge_count: int = 0,
    ) -> List[Dict[str, Any]]:
        features = [
            self._feature_spec(
                "circulation",
                *SITE_FEATURE_DIMENSIONS["circulation"],
                kind="open_space",
            )
        ]
        features.extend(
            self._feature_spec(
                "family_lounge",
                *ROOM_DIMENSIONS["family_room"],
                kind="open_space",
                index=index,
            )
            for index in range(1, family_lounge_count + 1)
        )
        if floor_count > 1 or staircase_required:
            staircase = self._feature_spec(
                "staircase", *SITE_FEATURE_DIMENSIONS["staircase"]
            )
            if fixed_staircase:
                staircase["fixed_x"], staircase["fixed_y"] = fixed_staircase
            features.append(staircase)

        if floor == "ground_floor" and front_porch_required:
            porch = self._feature_spec(
                "front_porch", *SITE_FEATURE_DIMENSIONS["front_porch"]
            )
            porch["fixed_y"] = 0.0
            features.append(porch)

        if floor == "first_floor" and floor_count > 1:
            landing = self._feature_spec(
                "staircase_landing",
                *SITE_FEATURE_DIMENSIONS["staircase_landing"],
            )
            if fixed_staircase:
                landing["fixed_x"] = fixed_staircase[0]
                landing["fixed_y"] = (
                    fixed_staircase[1]
                    + SITE_FEATURE_DIMENSIONS["staircase"][1]
                )
            features.append(landing)

        if floor == "ground_floor" and parking.get("required", False):
            cars = parking.get("cars") or 0
            bikes = parking.get("bikes") or 0
            if cars == 0 and bikes == 0:
                cars = 1
            bike_bays = (bikes + 1) // 2
            width = 2500 * cars + 1000 * bike_bays
            height = max(5000 if cars else 0, 4000 if bikes else 0)
            features.append(self._feature_spec("parking", width, height))
        return features

    def _feature_spec(
        self,
        feature_type: str,
        width: float,
        height: float,
        kind: str = "site_feature",
        index: int = 1,
    ) -> Dict[str, Any]:
        return {
            "id": f"{feature_type}_{index}",
            "type": feature_type,
            "name": f"{feature_type.replace('_', ' ').title()} {index}",
            "width": width,
            "height": height,
            "kind": kind,
        }

    def _raise_placement_error(
        self,
        floor_name: str,
        specs: Sequence[Dict[str, Any]],
        plot_width: float,
        plot_height: float,
    ) -> None:
        required_area = sum(spec["width"] * spec["height"] for spec in specs)
        plot_area = plot_width * plot_height
        names = ", ".join(
            f"{spec['name']} ({spec['width']:g}x{spec['height']:g} mm)"
            for spec in specs
        )
        area_note = (
            f" Their combined area is {required_area:,.0f} mm^2, exceeding "
            f"the floor area of {plot_area:,.0f} mm^2."
            if required_area > plot_area
            else (
                f" Their combined area is {required_area:,.0f} mm^2 of "
                f"{plot_area:,.0f} mm^2; their dimensions and required "
                "circulation cannot be arranged within the plot."
            )
        )
        raise ValueError(
            f"Unable to place requirements on {floor_name.replace('_', ' ')}: "
            f"{names}.{area_note}"
        )

    @staticmethod
    def _required_area(specs: Sequence[Dict[str, Any]]) -> float:
        return sum(spec["width"] * spec["height"] for spec in specs)

    def create_rooms(
        self,
        room_counts: Dict[str, Any],
        plot_width: float,
        plot_height: float,
        vastu: Dict[str, Any],
        retry_seed: int = 0,
    ) -> List[Dict[str, Any]]:
        del vastu
        del retry_seed
        specs = self._requested_rooms(room_counts)
        if not specs:
            raise ValueError("At least one room must be requested.")
        if self._required_area(specs) > plot_width * plot_height:
            self._raise_placement_error("floor", specs, plot_width, plot_height)
        placed = self._pack_rooms(specs, plot_width, plot_height)
        if placed is None:
            self._raise_placement_error("floor", specs, plot_width, plot_height)
        return placed

    def _requested_rooms(self, counts: Dict[str, Any]) -> List[Dict[str, Any]]:
        counts = dict(counts or {})
        family_room_enclosed = counts.pop("family_room_enclosed", False)
        normalized: Dict[str, int] = {}
        for name, value in counts.items():
            if name == "kitchen_type":
                continue
            name = _canonical_room_type(name)
            count = 0 if value is None else value
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Room count for {name} must be a non-negative integer.")
            normalized[name] = count

        bedroom_total = normalized.get("bedrooms", 0)
        specific_bedrooms = sum(
            normalized.get(name, 0) for name in BEDROOM_SUBTYPE_COUNTS
        )
        if specific_bedrooms > bedroom_total:
            if bedroom_total:
                raise ValueError(
                    "Bedroom subtype counts cannot exceed the requested bedroom count."
                )
            bedroom_total = specific_bedrooms

        bathroom_total = normalized.get("bathrooms", 0)
        specific_bathrooms = sum(
            normalized.get(name, 0) for name in BATHROOM_SUBTYPE_COUNTS
        )
        if specific_bathrooms > bathroom_total:
            if bathroom_total:
                raise ValueError(
                    "Bathroom subtype counts cannot exceed the requested bathroom count."
                )
            bathroom_total = specific_bathrooms

        effective_counts = {
            name: count
            for name, count in normalized.items()
            if name not in ("bedrooms", "master_bedrooms", "guest_rooms",
                            "children_rooms", "bathrooms", "attached_bathrooms",
                            "common_bathrooms", "family_room")
        }
        if family_room_enclosed:
            effective_counts["family_room"] = normalized.get("family_room", 0) or 1
        effective_counts.update({
            "bedroom": bedroom_total - specific_bedrooms,
            "attached_bathroom": normalized.get("attached_bathrooms", 0),
            "common_bathroom": normalized.get("common_bathrooms", 0),
            "bathroom": bathroom_total - specific_bathrooms,
            "master_bedroom": normalized.get("master_bedrooms", 0),
            "guest_room": normalized.get("guest_rooms", 0),
            "children_room": normalized.get("children_rooms", 0),
        })

        specs: List[Dict[str, Any]] = []
        indexes: Dict[str, int] = {}
        for room_type, count in effective_counts.items():
            if count <= 0:
                continue
            if room_type not in ROOM_DIMENSIONS:
                raise ValueError(f"Unsupported requested room type: {room_type}")
            width, height = ROOM_DIMENSIONS[room_type]
            for _ in range(count):
                indexes[room_type] = indexes.get(room_type, 0) + 1
                index = indexes[room_type]
                specs.append({
                    "id": f"{room_type}_{index}",
                    "type": room_type,
                    "name": f"{room_type.replace('_', ' ').title()} {index}",
                    "width": width,
                    "height": height,
                })
        return specs

    def requested_room_specs(
        self,
        counts: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        return self._requested_rooms(counts)

    def _pack_rooms(
        self,
        specs: Sequence[Dict[str, Any]],
        plot_width: float,
        plot_height: float,
        support_footprint: Optional[Sequence[Dict[str, Any]]] = None,
        completion_check: Optional[
            Callable[[Sequence[Dict[str, Any]]], bool]
        ] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        placed: List[Dict[str, Any]] = []
        failed_states = set()
        ordered_specs = sorted(
            specs,
            key=lambda spec: (
                4 if spec.get("type") == "parking"
                else 3 if spec.get("type") == "front_porch"
                else 0 if spec.get("fixed_x") is not None
                or spec.get("fixed_y") is not None else 1,
                0 if spec.get("kind") == "site_feature"
                else 1 if spec.get("kind") == "open_space"
                else 2,
                -(spec["width"] * spec["height"]),
                spec["id"],
            ),
        )

        def place(index: int) -> bool:
            if index == len(ordered_specs):
                return (
                    completion_check(placed)
                    if completion_check is not None
                    else True
                )

            state = (
                index,
                tuple(
                    (
                        item["id"],
                        item["x"],
                        item["y"],
                        item["width"],
                        item["height"],
                    )
                    for item in placed
                ),
            )
            if state in failed_states:
                return False

            spec = ordered_specs[index]
            existing_rooms = [
                item
                for item in placed
                if item.get("kind") not in ("site_feature", "open_space")
                and item.get("type") != "parking"
            ]
            candidate_door_rooms = [
                (room_index, room)
                for room_index, room in enumerate(existing_rooms)
                if self._should_have_door(room["type"], spec["type"])
            ]
            candidate_access_areas = [
                item
                for item in placed
                if item.get("kind") == "open_space"
                or item.get("type") == "front_porch"
            ]
            vertical_edges: Dict[float, List[Tuple[float, float]]] = {}
            horizontal_edges: Dict[float, List[Tuple[float, float]]] = {}
            for item in placed:
                left = item["x"]
                right = left + item["width"]
                top = item["y"]
                bottom = top + item["height"]
                vertical_edges.setdefault(left, []).append((top, bottom))
                vertical_edges.setdefault(right, []).append((top, bottom))
                horizontal_edges.setdefault(top, []).append((left, right))
                horizontal_edges.setdefault(bottom, []).append((left, right))

            def indexed_contact(
                x: float,
                y: float,
                width: float,
                height: float,
            ) -> float:
                contact = 0.0
                for edge in (x, x + width):
                    for start, end in vertical_edges.get(edge, ()):
                        contact += max(
                            0.0,
                            min(y + height, end) - max(y, start),
                        )
                for edge in (y, y + height):
                    for start, end in horizontal_edges.get(edge, ()):
                        contact += max(
                            0.0,
                            min(x + width, end) - max(x, start),
                        )
                return contact

            orientations = [(spec["width"], spec["height"])]
            rotated = (spec["height"], spec["width"])
            if (
                rotated != orientations[0]
                and spec.get("fixed_x") is None
                and spec.get("fixed_y") is None
                and spec.get("type") != "staircase"
            ):
                orientations.append(rotated)

            candidates = set()
            for width, height in orientations:
                if width > plot_width or height > plot_height:
                    continue
                fixed_x = spec.get("fixed_x")
                fixed_y = spec.get("fixed_y")
                xs = (
                    {fixed_x}
                    if fixed_x is not None
                    else {0.0, plot_width - width}
                )
                ys = (
                    {fixed_y}
                    if fixed_y is not None
                    else {0.0, plot_height - height}
                )
                needs_support = (
                    support_footprint is not None
                    and spec.get("type") != "staircase"
                    and not (
                        spec.get("type") == "balcony"
                        and spec.get("cantilever_supported") is True
                    )
                )
                boundaries = list(placed)
                if support_footprint:
                    boundaries.extend(support_footprint)

                for boundary in boundaries:
                    bx = boundary["x"]
                    by = boundary["y"]
                    br = bx + boundary["width"]
                    bb = by + boundary["height"]
                    if fixed_x is None:
                        xs.update((bx, bx - width, br, br - width))
                    if fixed_y is None:
                        ys.update((by, by - height, bb, bb - height))

                for x in xs:
                    for y in ys:
                        if (
                            x < 0
                            or y < 0
                            or x + width > plot_width
                            or y + height > plot_height
                        ):
                            continue
                        if (
                            needs_support
                            and not self._within_support_footprint(
                                x, y, width, height, support_footprint
                            )
                        ):
                            continue
                        if any(self._overlap(x, y, width, height, room) for room in placed):
                            continue
                        contact = indexed_contact(x, y, width, height)
                        door_contact = self._candidate_door_contact(
                            spec,
                            x,
                            y,
                            width,
                            height,
                            placed,
                            existing_rooms=existing_rooms,
                            compatible_rooms=candidate_door_rooms,
                            access_areas=candidate_access_areas,
                        )
                        candidates.add(
                            (door_contact, contact, y, x, width, height)
                        )

            for _, _, y, x, width, height in sorted(
                candidates,
                key=lambda item: (
                    -item[0],
                    -item[1],
                    item[2],
                    item[3],
                ),
            ):
                room = self.make_room(
                    spec["type"],
                    x,
                    y,
                    width,
                    height,
                    room_id=spec["id"],
                    name=spec["name"],
                )
                if spec.get("kind"):
                    room["kind"] = spec["kind"]
                if spec.get("cantilever_supported") is True:
                    room["cantilever_supported"] = True
                placed.append(room)
                if place(index + 1):
                    return True
                placed.pop()
            failed_states.add(state)
            return False

        if place(0):
            return placed
        return None

    def _candidate_door_contact(
        self,
        spec: Dict[str, Any],
        x: float,
        y: float,
        width: float,
        height: float,
        placed: Sequence[Dict[str, Any]],
        *,
        existing_rooms: Optional[Sequence[Dict[str, Any]]] = None,
        compatible_rooms: Optional[
            Sequence[Tuple[int, Dict[str, Any]]]
        ] = None,
        access_areas: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> float:
        candidate = {
            "type": spec["type"],
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        if existing_rooms is None:
            existing_rooms = [
                item
                for item in placed
                if item.get("kind") not in ("site_feature", "open_space")
                and item.get("type") != "parking"
            ]
        if spec.get("type") == "front_porch":
            living = next(
                (
                    (index, room)
                    for index, room in enumerate(existing_rooms)
                    if room.get("type") == "living_room"
                ),
                None,
            )
            if living is None:
                return 0.0
            _, _, shared = self._shared_room_access_wall(
                living[0],
                living[1],
                candidate,
            )
            return shared if shared >= 900 else 0.0

        if spec.get("kind") in ("site_feature", "open_space"):
            return 0.0

        candidate_index = len(existing_rooms)
        door_contact = 0.0
        if access_areas is None:
            access_areas = [
                item
                for item in placed
                if item.get("kind") == "open_space"
                or item.get("type") == "front_porch"
            ]
        for area in access_areas:
            wall, _, shared = self._shared_room_access_wall(
                candidate_index,
                candidate,
                area,
            )
            if wall is not None and shared >= 900:
                door_contact += shared

        if compatible_rooms is None:
            compatible_rooms = [
                (room_index, room)
                for room_index, room in enumerate(existing_rooms)
                if self._should_have_door(
                    room["type"],
                    candidate["type"],
                )
            ]
        for room_index, room in compatible_rooms:
            wall, _, shared = self._shared_wall(
                room_index,
                room,
                candidate_index,
                candidate,
            )
            if wall is not None and shared >= 900:
                door_contact += shared

        return door_contact

    def make_room(
        self,
        room_type: str,
        x: float,
        y: float,
        w: float,
        h: float,
        room_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "id": room_id or f"{room_type}_{x}_{y}",
            "type": room_type,
            "name": name or room_type.replace("_", " ").title(),
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "area": w * h,
            "rotation": 90 if (w, h) == (ROOM_DIMENSIONS.get(room_type, (w, h))[1],
                                         ROOM_DIMENSIONS.get(room_type, (w, h))[0]) else 0,
            "polygon": [
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h],
            ],
        }

    def create_adjacency(
        self, rooms: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        connections = []
        tolerance = 1.0

        for i, first in enumerate(rooms):
            for second in rooms[i + 1:]:
                x1 = float(first["x"])
                y1 = float(first["y"])
                w1 = float(first["width"])
                h1 = float(first["height"])

                x2 = float(second["x"])
                y2 = float(second["y"])
                w2 = float(second["width"])
                h2 = float(second["height"])

                vertical_overlap = (
                    min(y1 + h1, y2 + h2) - max(y1, y2)
                )
                horizontal_overlap = (
                    min(x1 + w1, x2 + w2) - max(x1, x2)
                )

                vertical_contact = (
                    abs((x1 + w1) - x2) <= tolerance
                    or abs((x2 + w2) - x1) <= tolerance
                ) and vertical_overlap > tolerance

                horizontal_contact = (
                    abs((y1 + h1) - y2) <= tolerance
                    or abs((y2 + h2) - y1) <= tolerance
                ) and horizontal_overlap > tolerance

                if not (vertical_contact or horizontal_contact):
                    continue

                connections.append({
                    "from": first["type"],
                    "to": second["type"],
                    "from_id": first["id"],
                    "to_id": second["id"],
                })

        return connections

    def _circulation_connected(
        self,
        items: Sequence[Dict[str, Any]],
    ) -> bool:
        nodes = [
            item
            for item in items
            if item.get("type") != "parking"
        ]
        if len(nodes) < 2:
            return True

        adjacency = {item["id"]: set() for item in nodes}
        for connection in self.create_adjacency(list(nodes)):
            adjacency[connection["from_id"]].add(connection["to_id"])
            adjacency[connection["to_id"]].add(connection["from_id"])

        return self._graph_connected(adjacency)

    @staticmethod
    def _graph_connected(adjacency: Dict[str, set[str]]) -> bool:
        if len(adjacency) < 2:
            return True

        visited = set()
        pending = [next(iter(adjacency))]
        while pending:
            node_id = pending.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            pending.extend(adjacency[node_id] - visited)

        return len(visited) == len(adjacency)

    def _placed_circulation_connected(
        self,
        items: Sequence[Dict[str, Any]],
        plot_width: float,
        plot_height: float,
    ) -> bool:
        if not self._circulation_connected(items):
            return False

        rooms = [
            item
            for item in items
            if item.get("kind") not in ("site_feature", "open_space")
            and item.get("type") != "parking"
        ]
        access_areas = self._circulation_access_areas(items)
        doors, _ = self._openings(
            rooms,
            self.create_adjacency(rooms),
            plot_width,
            plot_height,
            access_areas,
        )
        return self._door_graph_connected(rooms, access_areas, doors)

    @staticmethod
    def _circulation_access_areas(
        items: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        return [
            item
            for item in items
            if item.get("kind") == "open_space"
            or item.get("type")
            in {"front_porch", "staircase", "staircase_landing"}
        ]

    def _circulation_connections(
        self,
        rooms: Sequence[Dict[str, Any]],
        access_areas: Sequence[Dict[str, Any]],
        doors: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        items = [*rooms, *access_areas]
        item_by_id = {item["id"]: item for item in items}
        connections = [
            {
                "from_id": door["from_id"],
                "to_id": door["to_id"],
                "kind": "door",
            }
            for door in doors
        ]
        open_areas = [
            area
            for area in access_areas
            if area.get("type") != "front_porch"
        ]
        for connection in self.create_adjacency(list(open_areas)):
            connections.append(
                {
                    "from_id": connection["from_id"],
                    "to_id": connection["to_id"],
                    "kind": "open_flow",
                }
            )

        for connection in connections:
            connection["from"] = item_by_id[connection["from_id"]]["type"]
            connection["to"] = item_by_id[connection["to_id"]]["type"]
        return connections

    def _door_graph_connected(
        self,
        rooms: Sequence[Dict[str, Any]],
        access_areas: Sequence[Dict[str, Any]],
        doors: Sequence[Dict[str, Any]],
    ) -> bool:
        items = [*rooms, *access_areas]
        if not items:
            return True

        adjacency = {item["id"]: set() for item in items}
        for door in doors:
            first_id = door.get("from_id")
            second_id = door.get("to_id")
            if first_id in adjacency and second_id in adjacency:
                adjacency[first_id].add(second_id)
                adjacency[second_id].add(first_id)

        open_areas = [
            area
            for area in access_areas
            if area.get("type") != "front_porch"
        ]
        for connection in self.create_adjacency(list(open_areas)):
            adjacency[connection["from_id"]].add(connection["to_id"])
            adjacency[connection["to_id"]].add(connection["from_id"])

        main_room = next(
            (room for room in rooms if room.get("type") == "living_room"),
            items[0],
        )
        visited = set()
        pending = [main_room["id"]]
        while pending:
            node_id = pending.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            pending.extend(adjacency[node_id] - visited)

        return len(visited) == len(items)

    @staticmethod
    def _should_have_door(
        first_type: str,
        second_type: str,
    ) -> bool:
        pair = frozenset((first_type, second_type))
        if pair in DOOR_FORBIDDEN_PAIRS:
            return False

        return pair in DOOR_ALLOWED_PAIRS

    def _openings(
        self,
        rooms: List[Dict[str, Any]],
        connections: List[Dict[str, str]],
        plot_width: float,
        plot_height: float,
        access_areas: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        doors = []
        windows = []
        room_by_id = {room["id"]: room for room in rooms}
        tolerance = 1.0
        used_door_walls = set()

        def append_door(
            room: Dict[str, Any],
            wall: Optional[int],
            position: float,
            shared: float,
            access_id: str,
        ) -> None:
            if wall is None or shared < 900:
                return

            door_width = min(900.0, shared - 200.0)
            if door_width < 700 or wall in used_door_walls:
                return

            used_door_walls.add(wall)
            doors.append({
                "wall": wall,
                "position": max(0.0, min(1.0, position)),
                "width": door_width,
                "from_id": room["id"],
                "to_id": access_id,
            })

        for area in access_areas or []:
            if (
                area.get("kind") != "open_space"
                and area.get("type") != "front_porch"
            ):
                continue
            for room_index, room in enumerate(rooms):
                if (
                    area.get("type") == "front_porch"
                    and room.get("type") != "living_room"
                ):
                    continue
                wall, position, shared = self._shared_room_access_wall(
                    room_index,
                    room,
                    area,
                )
                append_door(
                    room,
                    wall,
                    position,
                    shared,
                    area["id"],
                )

        for connection in connections:
            first = room_by_id.get(connection["from_id"])
            second = room_by_id.get(connection["to_id"])

            if first is None or second is None:
                continue

            if not self._should_have_door(
                first["type"], second["type"]
            ):
                continue

            first_index = rooms.index(first)
            second_index = rooms.index(second)

            wall, position, shared = self._shared_wall(
                first_index, first, second_index, second
            )
            append_door(
                first,
                wall,
                position,
                shared,
                second["id"],
            )

        for room_index, room in enumerate(rooms):
            x = float(room["x"])
            y = float(room["y"])
            width = float(room["width"])
            height = float(room["height"])

            external_walls = []

            if abs(y) <= tolerance:
                external_walls.append((0, width))

            if abs((x + width) - plot_width) <= tolerance:
                external_walls.append((1, height))

            if abs((y + height) - plot_height) <= tolerance:
                external_walls.append((2, width))

            if abs(x) <= tolerance:
                external_walls.append((3, height))

            for edge, edge_length in external_walls:
                window_width = min(1200.0, edge_length - 400.0)

                if window_width < 600:
                    continue

                windows.append({
                    "wall": room_index * 4 + edge,
                    "position": 0.5,
                    "width": window_width,
                })

        return doors, windows

    @staticmethod
    def _shared_room_access_wall(
        room_index: int,
        room: Dict[str, Any],
        area: Dict[str, Any],
    ) -> Tuple[Optional[int], float, float]:
        room_x = float(room["x"])
        room_y = float(room["y"])
        room_width = float(room["width"])
        room_height = float(room["height"])
        area_x = float(area["x"])
        area_y = float(area["y"])
        area_width = float(area["width"])
        area_height = float(area["height"])
        tolerance = 1.0

        overlap_y = min(room_y + room_height, area_y + area_height) - max(
            room_y,
            area_y,
        )
        if abs(room_x + room_width - area_x) <= tolerance and overlap_y > tolerance:
            center = max(room_y, area_y) + overlap_y / 2
            return (
                room_index * 4 + 1,
                (center - room_y) / room_height,
                overlap_y,
            )
        if abs(area_x + area_width - room_x) <= tolerance and overlap_y > tolerance:
            center = max(room_y, area_y) + overlap_y / 2
            return (
                room_index * 4 + 3,
                (room_y + room_height - center) / room_height,
                overlap_y,
            )

        overlap_x = min(room_x + room_width, area_x + area_width) - max(
            room_x,
            area_x,
        )
        if abs(room_y + room_height - area_y) <= tolerance and overlap_x > tolerance:
            center = max(room_x, area_x) + overlap_x / 2
            return (
                room_index * 4 + 2,
                (room_x + room_width - center) / room_width,
                overlap_x,
            )
        if abs(area_y + area_height - room_y) <= tolerance and overlap_x > tolerance:
            center = max(room_x, area_x) + overlap_x / 2
            return (
                room_index * 4,
                (center - room_x) / room_width,
                overlap_x,
            )

        return None, 0.5, 0.0

    def _shared_wall(
        self,
        first_index: int,
        first: Dict[str, Any],
        second_index: int,
        second: Dict[str, Any],
    ) -> Tuple[Optional[int], float, float]:
        tolerance = 1.0

        first_x = float(first["x"])
        first_y = float(first["y"])
        first_w = float(first["width"])
        first_h = float(first["height"])

        second_x = float(second["x"])
        second_y = float(second["y"])
        second_w = float(second["width"])
        second_h = float(second["height"])

        overlap_y = (
            min(first_y + first_h, second_y + second_h)
            - max(first_y, second_y)
        )

        if (
            abs((first_x + first_w) - second_x) <= tolerance
            and overlap_y > tolerance
        ):
            center = max(first_y, second_y) + overlap_y / 2
            return (
                first_index * 4 + 1,
                (center - first_y) / first_h,
                overlap_y,
            )

        if (
            abs((second_x + second_w) - first_x) <= tolerance
            and overlap_y > tolerance
        ):
            center = max(first_y, second_y) + overlap_y / 2
            return (
                second_index * 4 + 1,
                (center - second_y) / second_h,
                overlap_y,
            )

        overlap_x = (
            min(first_x + first_w, second_x + second_w)
            - max(first_x, second_x)
        )

        if (
            abs((first_y + first_h) - second_y) <= tolerance
            and overlap_x > tolerance
        ):
            center = max(first_x, second_x) + overlap_x / 2
            return (
                first_index * 4 + 2,
                (first_x + first_w - center) / first_w,
                overlap_x,
            )

        if (
            abs((second_y + second_h) - first_y) <= tolerance
            and overlap_x > tolerance
        ):
            center = max(first_x, second_x) + overlap_x / 2
            return (
                second_index * 4 + 2,
                (second_x + second_w - center) / second_w,
                overlap_x,
            )

        return None, 0.5, 0.0
    @staticmethod
    def _within_support_footprint(
        x: float,
        y: float,
        width: float,
        height: float,
        support: Sequence[Dict[str, Any]],
    ) -> bool:
        right = x + width
        bottom = y + height

        # Divide the candidate room into rectangular cells using
        # the boundaries of all intersecting ground-floor elements.
        x_points = {x, right}
        y_points = {y, bottom}

        for item in support:
            sx = item["x"]
            sy = item["y"]
            sr = sx + item["width"]
            sb = sy + item["height"]

            if sr <= x or sx >= right or sb <= y or sy >= bottom:
                continue

            x_points.update((max(x, sx), min(right, sr)))
            y_points.update((max(y, sy), min(bottom, sb)))

        xs = sorted(x_points)
        ys = sorted(y_points)

        # Every cell must be covered by at least one ground-floor element.
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                if xs[i + 1] <= xs[i] or ys[j + 1] <= ys[j]:
                    continue

                mid_x = (xs[i] + xs[i + 1]) / 2
                mid_y = (ys[j] + ys[j + 1]) / 2

                supported = any(
                    item["x"] <= mid_x <= item["x"] + item["width"]
                    and item["y"] <= mid_y <= item["y"] + item["height"]
                    for item in support
                )

                if not supported:
                    return False

        return True
    @staticmethod
    def _overlap(x: float, y: float, width: float, height: float, room: Dict[str, Any]) -> bool:
        return not (
            x + width <= room["x"]
            or room["x"] + room["width"] <= x
            or y + height <= room["y"]
            or room["y"] + room["height"] <= y
        )

    @staticmethod
    def _contact_length(
        x: float,
        y: float,
        width: float,
        height: float,
        rooms: Sequence[Dict[str, Any]],
    ) -> float:
        contact = 0.0
        for room in rooms:
            vertical_overlap = min(y + height, room["y"] + room["height"]) - max(y, room["y"])
            horizontal_overlap = min(x + width, room["x"] + room["width"]) - max(x, room["x"])
            if x + width == room["x"] or room["x"] + room["width"] == x:
                contact += max(0.0, vertical_overlap)
            if y + height == room["y"] or room["y"] + room["height"] == y:
                contact += max(0.0, horizontal_overlap)
        return contact


planner = LayoutPlanner()


def generate_layout(
    constraints: Dict[str, Any],
    retry_seed: int = 0,
) -> Dict[str, Any]:
    return planner.generate_layout(constraints, retry_seed=retry_seed)
