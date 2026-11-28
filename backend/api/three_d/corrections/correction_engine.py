
from .furniture_corrector import FurnitureCorrector
from .room_corrector import RoomCorrector
from .doorway_corrector import DoorwayCorrector
from .circulation_analyzer import CirculationAnalyzer
from .correction_report import create_correction_report
from .correction_models import CorrectionAction

from backend.api.three_d.validation.architectural_geometry_validator import (
    ArchitecturalGeometryValidator,
)


class CorrectionEngine:

    def __init__(self, quality_pipeline):
        self.furniture_corrector = FurnitureCorrector(
            quality_pipeline
        )

        self.architectural_validator = ArchitecturalGeometryValidator()
        self.room_corrector = RoomCorrector()
        self.doorway_corrector = DoorwayCorrector()
        self.circulation_analyzer = CirculationAnalyzer()

    def correct_floor(
        self,
        floor,
        scene_id="unknown",
        auto_correct_furniture=False
    ):

        floor_id = (
            floor.id
            if not isinstance(floor, dict)
            else floor.get("id", "unknown")
        )

        report = create_correction_report(
            scene_id,
            floor_id
        )

        # -----------------------------------------
        # 1. Furniture correction (optional)
        # -----------------------------------------
        if auto_correct_furniture:
            result = self.furniture_corrector.correct(floor)

            for index, change in enumerate(
                result.get("changes", [])
            ):
                report.actions.append(
                    CorrectionAction(
                        correction_id=f"furniture_{index + 1}",
                        category="furniture",
                        target_id=change.get("furniture_id", "unknown"),
                        description="Reposition furniture",
                        old_value=change.get("old_position"),
                        new_value=change.get("new_position"),
                        applied=True,
                        reason="Found an alternative position."
                    )
                )

            report.unresolved.extend(
                result.get("unresolved", [])
            )

        # -----------------------------------------
        # 2. Room geometry analysis
        # -----------------------------------------
        room_result = self.room_corrector.correct(floor)

        report.unresolved.extend(
            room_result.get("unresolved", [])
        )

        # -----------------------------------------
        # 3. Doorway analysis
        # -----------------------------------------
        doorway_result = self.doorway_corrector.correct(floor)

        report.unresolved.extend(
            doorway_result.get("unresolved", [])
        )

        # -----------------------------------------
        # 4. Circulation analysis
        # -----------------------------------------
        circulation_result = self.circulation_analyzer.analyze(
            floor
        )

        report.warnings.extend(
            circulation_result.get("warnings", [])
        )

        
        # -----------------------------------------
        # 5. Architectural geometry validation
        # -----------------------------------------
        architectural_report = (
            self.architectural_validator.validate_floor(floor)
        )

        report.warnings.extend(
            architectural_report.get("warnings", [])
        )

        for error in architectural_report.get("errors", []):
            report.unresolved.append({
                "category": "architectural_geometry",
                "reason": error
            })

        report.warnings.append(
            "Architectural validation completed: "
            f"{len(architectural_report.get('errors', []))} errors, "
            f"{len(architectural_report.get('warnings', []))} warnings."
        )

        # -----------------------------------------
        # 6. Return complete report
        # -----------------------------------------
        result = report.to_dict()

        result["architectural_validation"] = architectural_report

        return result

