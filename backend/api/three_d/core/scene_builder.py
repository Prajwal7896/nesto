
"""High-level builder that converts Nesto's 2D layout output into a 3D scene."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional
from uuid import uuid4

from backend.api.three_d.validation import (
    RoomGeometryValidator,
    RoomConnectivityValidator,
    FurnitureClearanceValidator,
    BathroomFixtureValidator,
    SceneQualityPipeline,
)
from backend.api.three_d.corrections import CorrectionEngine
from backend.api.three_d.validation.floor_alignment_validator import (
    FloorAlignmentValidator,
)
from .coordinate_system import CoordinateSystem
from .geometry_extractor import GeometryExtractor
from .scene_manager import SceneManager
from .scene_models import Scene
from backend.api.three_d.furniture.auto_placement import FurnitureAutoPlacer

logger = logging.getLogger(__name__)

class SceneBuilder:
    """Build the renderer-independent scene consumed by Three.js."""

    def __init__(
        self,
        *,
        coordinate_system: Optional[CoordinateSystem] = None,
        geometry_extractor: Optional[GeometryExtractor] = None,
        wall_height: float = 3000.0,
        wall_thickness: float = 150.0,
        floor_height: float = 3000.0,
    ) -> None:

        self.coordinate_system = coordinate_system or CoordinateSystem()

        self.geometry_extractor = geometry_extractor or GeometryExtractor(
            wall_height=wall_height,
            wall_thickness=wall_thickness,
            floor_height=floor_height,
        )
        self.furniture_placer = FurnitureAutoPlacer(grid_size=100.0)
        self.room_validator = RoomGeometryValidator()
        self.connectivity_validator = RoomConnectivityValidator()
        self.furniture_clearance_validator = FurnitureClearanceValidator()
        self.bathroom_validator = BathroomFixtureValidator()
        self.floor_alignment_validator = FloorAlignmentValidator()
        

        self.quality_pipeline = SceneQualityPipeline()

        self.correction_engine = CorrectionEngine(
            self.quality_pipeline
        )

    def build(
        self,
        layout: Dict[str, Any],
        *,
        scene_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Scene:

        if not isinstance(layout, dict):
            raise TypeError("layout must be a dictionary.")

        started = time.perf_counter()
        timings: dict[str, float] = {}

        def record(name: str, phase_started: float) -> None:
            elapsed = time.perf_counter() - phase_started
            timings[name] = elapsed
            logger.info("stage_timing stage=%s seconds=%.6f", name, elapsed)

        scene = Scene(
            id=scene_id or f"nesto_{uuid4().hex[:12]}",
            source_unit="mm",
            world_unit="m",
            defaults={
                "wall_height": self.geometry_extractor.wall_height,
                "wall_thickness": self.geometry_extractor.wall_thickness,
                "floor_thickness": 150.0,
                "door_height": self.geometry_extractor.door_height,
                "window_height": self.geometry_extractor.window_height,
                "window_sill_height": self.geometry_extractor.window_sill_height,
                "floor_to_floor_height": self.geometry_extractor.floor_height,
            },
            metadata={
                "source": "Nesto 2D planner",
                "coordinate_mapping": "plan_x_to_three_x_plan_y_to_three_z",
                "coordinate_origin": (
                    "plot_center"
                    if self.coordinate_system.centered
                    else "plot_corner"
                ),
            },
        )

        manager = SceneManager(scene)

        phase_started = time.perf_counter()
        extracted_floors = self.geometry_extractor.extract(layout)
        record("3d_geometry_extraction", phase_started)

        for floor in extracted_floors:

            # Phase 0: Generate furniture for every room
            phase_started = time.perf_counter()
            generated_furniture, furniture_warnings = (
                self.furniture_placer.generate_for_floor(floor)
            )
            record(f"3d_furniture_generation_{floor.id}", phase_started)

            floor.furniture = generated_furniture

            # One quality pass produces all four reports; do not rerun the
            # same validators separately before collecting those reports.
            phase_started = time.perf_counter()
            quality_report = (
                self.quality_pipeline.validate_and_correct_floor(
                    floor,
                    auto_correct=False,
                )
            )
            record(f"3d_quality_validation_{floor.id}", phase_started)
            reports = quality_report.get("reports", {})
            geometry_report = reports.get("room_validation", {})
            connectivity_report = reports.get("connectivity_validation", {})
            furniture_report = reports.get("furniture_validation", {})
            bathroom_report = reports.get("bathroom_validation", {})

            # Phase 6: Architectural correction and validation
            phase_started = time.perf_counter()
            correction_report = self.correction_engine.correct_floor(
                floor,
                scene_id=scene.id,
                auto_correct_furniture=False,
            )
            record(f"3d_architectural_validation_{floor.id}", phase_started)

            if floor.metadata is None:
                floor.metadata = {}

            # Save all validation reports
            floor.metadata["scene_quality"] = quality_report
            floor.metadata["correction_report"] = correction_report
            floor.metadata["furniture_generation"] = {
                "generated_count": len(generated_furniture),
                "warnings": furniture_warnings,
            }
            floor.metadata["room_validation"] = geometry_report
            floor.metadata["connectivity_validation"] = connectivity_report
            floor.metadata["furniture_validation"] = furniture_report
            floor.metadata["bathroom_validation"] = bathroom_report
            # Separate architectural validation report
            floor.metadata["architectural_validation"] = (
                correction_report.get("architectural_validation", {})
            )

            manager.add_floor(floor)

        if metadata:
            manager.set_metadata(metadata)

        phase_started = time.perf_counter()
        alignment_report = self.floor_alignment_validator.validate(
            manager.scene.floors
        )
        manager.scene.metadata["floor_alignment_validation"] = alignment_report
        record("3d_floor_alignment_validation", phase_started)

        phase_started = time.perf_counter()
        self._validate_scene(manager.scene)
        record("3d_final_validation", phase_started)
        timings["3d_scene_generation"] = time.perf_counter() - started
        logger.info(
            "stage_timing stage=3d_scene_generation seconds=%.6f",
            timings["3d_scene_generation"],
        )
        manager.scene.metadata["generation_timings"] = timings

        return manager.scene

    def build_dict(
        self,
        layout: Dict[str, Any],
        *,
        scene_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        return self.build(
            layout,
            scene_id=scene_id,
            metadata=metadata,
        ).to_dict()

    @staticmethod
    def _validate_scene(scene: Scene) -> None:

        if not scene.floors:
            raise ValueError(
                "Cannot build a 3D scene without at least one floor."
            )

        floor_ids = [floor.id for floor in scene.floors]

        if len(floor_ids) != len(set(floor_ids)):
            raise ValueError(
                "Scene contains duplicate floor IDs."
            )

        for floor in scene.floors:

            if floor.plot_width <= 0 or floor.plot_depth <= 0:
                raise ValueError(
                    f"Floor '{floor.id}' has invalid plot dimensions."
                )

            room_ids = [room.id for room in floor.rooms]

            if len(room_ids) != len(set(room_ids)):
                raise ValueError(
                    f"Floor '{floor.id}' contains duplicate room IDs."
                )


def build_scene(
    layout: Dict[str, Any],
    *,
    scene_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Scene:

    return SceneBuilder().build(
        layout,
        scene_id=scene_id,
        metadata=metadata,
    )
