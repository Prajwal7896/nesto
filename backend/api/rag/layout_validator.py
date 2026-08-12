from typing import Any, Dict, List


class LayoutValidator:

    def validate(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        if layout is None:
            return {
                "valid": False,
                "score": 0,
                "errors": ["Layout is None"],
                "warnings": [],
                "summary": {"total_errors": 1, "total_warnings": 0},
            }

        if not isinstance(layout, dict):
            return {
                "valid": False,
                "score": 0,
                "errors": ["Layout must be a dictionary"],
                "warnings": [],
                "summary": {"total_errors": 1, "total_warnings": 0},
            }

        errors: List[str] = []
        warnings: List[str] = []
        score_holder = [100]

        if "rooms" not in layout:
            errors.append("Missing section: rooms")
            return {
                "valid": False,
                "score": 0,
                "errors": errors,
                "warnings": [],
                "summary": {"total_errors": len(errors), "total_warnings": 0},
            }

        self._validate_required_sections(layout, errors, score_holder)
        self._validate_room_requirements(layout, constraints, errors, warnings, score_holder)
        self._validate_area(layout, constraints, errors, warnings, score_holder)
        self._validate_structural_rules(layout, constraints, errors, warnings, score_holder)
        self._validate_planning_rules(layout, constraints, errors, warnings, score_holder)
        self._validate_vastu(layout, constraints, warnings, score_holder)
        self._validate_engineering(layout, constraints, warnings, score_holder)

        valid = len(errors) == 0
        score = max(
            0,
            100 - len(errors) * 20 - len(warnings) * 2,
        )

        return {
            "valid": valid,
            "score": score,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "total_errors": len(errors),
                "total_warnings": len(warnings),
            },
        }

    ##########################################################
    # REQUIRED SECTIONS
    ##########################################################

    def _validate_required_sections(
        self,
        layout: Dict[str, Any],
        errors: List[str],
        score_holder: List[int],
    ) -> None:
        required = ["plot", "rooms", "adjacency_graph", "circulation"]

        for item in required:
            if item not in layout:
                errors.append(f"Missing section: {item}")

    ##########################################################
    # ROOM VALIDATION
    ##########################################################

    def _validate_room_requirements(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
        errors: List[str],
        warnings: List[str],
        score_holder: List[int],
    ) -> None:
        required_rooms = (
            constraints.get("space_constraints", {})
            .get("rooms", {})
        )

        generated_rooms = layout.get("rooms", [])
        generated_room_names: List[str] = []

        if isinstance(generated_rooms, dict):
            generated_room_names = [
                name.lower()
                for name in generated_rooms.keys()
            ]
        elif isinstance(generated_rooms, list):
            for room in generated_rooms:
                if not isinstance(room, dict):
                    continue

                room_type = (
                    room.get("type")
                    or room.get("name")
                    or room.get("room_type")
                    or ""
                ).strip().lower()

                if room_type:
                    generated_room_names.append(room_type)

        ROOM_MAP = {
            "bedrooms": ["bedroom", "master_bedroom", "guest_room", "children_room"],
            "master_bedrooms": ["master_bedroom"],
            "guest_rooms": ["guest_room"],
            "children_rooms": ["children_room"],
            "bathrooms": ["bathroom", "attached_bathroom", "common_bathroom"],
            "attached_bathrooms": ["attached_bathroom"],
            "common_bathrooms": ["common_bathroom"],
            "living_room": ["living_room", "living"],
            "family_room": ["family_room"],
            "kitchen": ["kitchen"],
            "dining_room": ["dining_room", "dining"],
            "pooja_room": ["pooja_room"],
            "study_room": ["study_room"],
            "office": ["office"],
            "library": ["library"],
            "gym": ["gym"],
            "home_theatre": ["home_theatre"],
            "balcony": ["balcony"],
            "utility_room": ["utility_room"],
            "laundry_room": ["laundry_room"],
            "store_room": ["store_room"],
            "walk_in_closet": ["walk_in_closet"],
        }

        for room_name, count in required_rooms.items():
            if not isinstance(count, int) or count <= 0:
                continue

            expected = ROOM_MAP.get(room_name, [room_name])
            found = sum(
                1 for room in generated_room_names
                if room in expected
            )

            if found < count:
                errors.append(f"Missing required room: {expected[0]}")

    ##########################################################
    # AREA VALIDATION
    ##########################################################

    def _validate_area(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
        errors: List[str],
        warnings: List[str],
        score_holder: List[int],
    ) -> None:
        rooms = layout.get("rooms", {})
        total_area = 0

        if isinstance(rooms, list):
            total_area = sum(
                room.get("area", 0)
                for room in rooms
                if isinstance(room, dict)
            )
        elif isinstance(rooms, dict):
            for polygon in rooms.values():
                if isinstance(polygon, list) and len(polygon) >= 4:
                    xs = [p[0] for p in polygon]
                    ys = [p[1] for p in polygon]
                    total_area += (max(xs) - min(xs)) * (max(ys) - min(ys))

        layout["total_area"] = total_area

    ##########################################################
    # STRUCTURAL
    ##########################################################

    def _validate_structural_rules(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
        errors: List[str],
        warnings: List[str],
        score_holder: List[int],
    ) -> None:
        structure = layout.get("structure", {})

        if not structure:
            warnings.append("Structure information missing.")

    ##########################################################
    # PLANNING
    ##########################################################

    def _validate_planning_rules(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
        errors: List[str],
        warnings: List[str],
        score_holder: List[int],
    ) -> None:
        circulation = layout.get("circulation", {})

        if not circulation.get("ventilation", True):
            warnings.append("Cross ventilation not satisfied.")

        if not circulation.get("privacy", True):
            warnings.append("Privacy rule not satisfied.")

    ##########################################################
    # VASTU
    ##########################################################

    def _validate_vastu(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
        warnings: List[str],
        score_holder: List[int],
    ) -> None:
        vastu = constraints.get("vastu_constraints", {})

        if not vastu:
            return

        entrance = layout.get("main_entrance_direction")
        expected = vastu.get("main_entrance_direction")

        if entrance and expected and entrance != expected:
            warnings.append(f"Entrance direction should be {expected}")

    ##########################################################
    # ENGINEERING
    ##########################################################

    def _validate_engineering(
        self,
        layout: Dict[str, Any],
        constraints: Dict[str, Any],
        warnings: List[str],
        score_holder: List[int],
    ) -> None:
        if "engineering" not in layout:
            warnings.append("Engineering information missing.")


_validator = LayoutValidator()


def validate_layout(layout: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
    return _validator.validate(layout, constraints)