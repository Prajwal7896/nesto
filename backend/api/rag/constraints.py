from typing import Any, Dict, List


class ConstraintBuilder:

    def build_constraints(self, requirements: Any, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Converts user requirements + retrieved knowledge into strict constraints."""
        if hasattr(requirements, "model_dump"):
            requirements = requirements.model_dump()

        return {
            "space_constraints": self._space_constraints(requirements),
            "structural_constraints": self._structural_constraints(rag_data),
            "planning_constraints": self._planning_constraints(rag_data),
            "cost_constraints": self._cost_constraints(rag_data),
            "vastu_constraints": self._vastu_constraints(rag_data),
            "engineering_constraints": self._engineering_constraints(rag_data),
        }

    # ---------------------------
    # SPACE / USER REQUIREMENTS
    # ---------------------------
    def _space_constraints(self, req: Dict[str, Any]) -> Dict[str, Any]:
        building = req.get("building", {})
        parking = req.get("parking", {})
        outdoor = req.get("outdoor", {})
        rooms = req.get("rooms", {})
        plot = req.get("plot", {})

        return {
            "rooms": rooms,
            "floors": building.get("floors", 1),
            "parking": parking.get("required", False),
            "balcony": rooms.get("balcony", 0),
            "garden": outdoor.get("garden", False),
            "min_area": plot.get("area"),
            "max_area": plot.get("area"),
        }

    # ---------------------------
    # STRUCTURAL RULES
    # ---------------------------
    def _structural_constraints(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        rules = rag_data.get("structural", [])

        return {
            "beam_spacing": self._extract_value(rules, "beam spacing", "3m"),
            "column_alignment": "grid_based",
            "slab_thickness": self._extract_value(rules, "slab", "125mm"),
            "earthquake_resistance": True,
        }

    # ---------------------------
    # PLANNING RULES
    # ---------------------------
    def _planning_constraints(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        rules = rag_data.get("planning_rules", [])

        return {
            "circulation": self._extract_flag(rules, "circulation", True),
            "privacy": self._extract_flag(rules, "privacy", True),
            "ventilation": self._extract_flag(rules, "ventilation", True),
            "zoning": self._extract_flag(rules, "zoning", True),
        }

    # ---------------------------
    # COST RULES
    # ---------------------------
    def _cost_constraints(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "budget_range": "1200-3000 per sqft",
            "material_level": "standard",
            "optimization_priority": "cost_efficiency",
        }

    # ---------------------------
    # VASTU RULES
    # ---------------------------
    def _vastu_constraints(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "main_entrance_direction": "east_or_north",
            "kitchen_direction": "southeast",
            "master_bedroom_direction": "southwest",
        }

    # ---------------------------
    # ENGINEERING RULES
    # ---------------------------
    def _engineering_constraints(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "drainage": True,
            "electrical_safety": True,
            "hvac_ready": True,
            "water_supply": "gravity_based",
        }

    # ---------------------------
    # HELPERS
    # ---------------------------
    def _extract_value(self, rules: List[str], keyword: str, default: str) -> str:
        for r in rules:
            if keyword.lower() in r.lower():
                return r
        return default

    def _extract_flag(self, rules: List[str], keyword: str, default: bool) -> bool:
        for r in rules:
            if keyword.lower() in r.lower():
                return True
        return default


# Singleton instance
_builder = ConstraintBuilder()


def build_constraints(requirements: Any, rag_data: Dict[str, Any]) -> Dict[str, Any]:
    print(type(requirements))
    print(requirements)
    print(type(rag_data))
    print(rag_data.keys())
    return _builder.build_constraints(requirements, rag_data)