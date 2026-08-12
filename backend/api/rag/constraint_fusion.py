from typing import Any, Dict


class ConstraintFusion:

    def __init__(self):
        self.weights = {
            "structural": 0.35,
            "planning_rules": 0.20,
            "room_standards": 0.20,
            "vastu": 0.10,
            "cost": 0.10,
            "architecture": 0.03,
            "engineering": 0.02,
        }

    def build(self, requirements: Any, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {
            "structure": {},
            "layout": {},
            "rooms": {},
            "vastu": {},
            "cost": {},
            "engineering": {},
            "rules": [],
            "priorities": [],
        }

        self._apply_room_constraints(constraints, requirements, rag_data)
        self._apply_structural_constraints(constraints, requirements, rag_data)
        self._apply_planning_constraints(constraints, rag_data)
        self._apply_vastu_constraints(constraints, requirements, rag_data)
        self._apply_cost_constraints(constraints, requirements, rag_data)
        self._apply_engineering_constraints(constraints, rag_data)
        self._assign_priorities(constraints)

        return constraints

    def _apply_room_constraints(self, constraints: Dict[str, Any], req: Any, rag: Dict[str, Any]) -> None:
        rooms = req.rooms

        constraints["rooms"] = {
            "bedrooms": rooms.bedrooms,
            "bathrooms": rooms.bathrooms,
            "kitchen": rooms.kitchen,
            "living_room": rooms.living_room,
            "dining_room": rooms.dining_room,
        }

        constraints["room_standards"] = rag.get("room_standards", [])

    def _apply_structural_constraints(self, constraints: Dict[str, Any], req: Any, rag: Dict[str, Any]) -> None:
        building = req.building

        constraints["structure"] = {
            "floors": building.floors,
            "basement": building.basement,
            "stilt_floor": building.stilt_floor,
            "slab": building.slab,
            "terrace": building.terrace,
        }

        constraints["structural_rules"] = rag.get("structural", [])

    def _apply_planning_constraints(self, constraints: Dict[str, Any], rag: Dict[str, Any]) -> None:
        constraints["planning_rules"] = rag.get("planning_rules", [])

    def _apply_vastu_constraints(self, constraints: Dict[str, Any], req: Any, rag: Dict[str, Any]) -> None:
        if getattr(req.preferences, "vastu", False):
            constraints["vastu"] = rag.get("vastu", {})

    def _apply_cost_constraints(self, constraints: Dict[str, Any], req: Any, rag: Dict[str, Any]) -> None:
        constraints["cost"] = {
            "budget": req.project.budget,
            "rules": rag.get("cost", []),
        }

    def _apply_engineering_constraints(self, constraints: Dict[str, Any], rag: Dict[str, Any]) -> None:
        constraints["engineering"] = rag.get("engineering", [])

    def _assign_priorities(self, constraints: Dict[str, Any]) -> None:
        priorities = []

        if constraints["structure"].get("floors", 1) > 1:
            priorities.append("staircase_priority_high")

        budget = constraints["cost"].get("budget")
        if budget is not None and budget < 3000000:
            priorities.append("cost_optimization_high")

        if constraints.get("vastu"):
            priorities.append("vastu_alignment_required")

        if len(constraints["rooms"]) > 6:
            priorities.append("space_efficiency_required")

        constraints["priorities"] = priorities