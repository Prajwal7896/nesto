from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CorrectionAction:
    correction_id: str
    category: str
    target_id: str
    description: str
    old_value: Any = None
    new_value: Any = None
    applied: bool = False
    reason: str = ""


@dataclass
class CorrectionReport:
    scene_id: str
    floor_id: str
    actions: List[CorrectionAction] = field(default_factory=list)
    unresolved: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "scene_id": self.scene_id,
            "floor_id": self.floor_id,
            "actions": [
                vars(action) for action in self.actions
            ],
            "unresolved": self.unresolved,
            "warnings": self.warnings,
            "total_corrections": len(self.actions),
            "applied_corrections": sum(
                action.applied for action in self.actions
            ),
        }