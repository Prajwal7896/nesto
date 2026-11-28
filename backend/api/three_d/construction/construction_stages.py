"""Construction stage definitions for Nesto 3D."""

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class ConstructionStage:
    stage_id: str
    name: str
    order: int
    duration: float
    description: str
    component_types: List[str]

    def to_dict(self):
        return asdict(self)


class ConstructionStages:

    DEFAULT_STAGES = [
        ConstructionStage(
            "site_preparation", "Site Preparation", 1, 3.0,
            "Prepare and clear the construction site.",
            ["site", "ground", "excavation"]
        ),
        ConstructionStage(
            "foundation", "Foundation", 2, 5.0,
            "Construct foundations and footings.",
            ["foundation", "footing"]
        ),
        ConstructionStage(
            "structural_frame", "Structural Frame", 3, 6.0,
            "Construct columns and beams.",
            ["column", "beam"]
        ),
        ConstructionStage(
            "slab", "Floor Slabs", 4, 4.0,
            "Construct floor slabs.",
            ["slab", "floor"]
        ),
        ConstructionStage(
            "walls", "Wall Construction", 5, 6.0,
            "Build internal and external walls.",
            ["wall"]
        ),
        ConstructionStage(
            "openings", "Doors and Windows", 6, 3.0,
            "Install doors and windows.",
            ["door", "window"]
        ),
        ConstructionStage(
            "roof", "Roof Construction", 7, 4.0,
            "Construct roof elements.",
            ["roof", "railing"]
        ),
        ConstructionStage(
            "plumbing", "Plumbing Installation", 8, 4.0,
            "Install water supply and drainage systems.",
            ["pipe", "plumbing", "water_tank", "drainage"]
        ),
        ConstructionStage(
            "electrical", "Electrical Installation", 9, 4.0,
            "Install electrical wiring and fixtures.",
            ["wire", "conduit", "socket", "switchboard", "light"]
        ),
        ConstructionStage(
            "hvac", "HVAC Installation", 10, 3.0,
            "Install ventilation and air conditioning.",
            ["duct", "air_conditioner", "ventilation"]
        ),
        ConstructionStage(
            "furniture", "Furniture Placement", 11, 3.0,
            "Place furniture and interior equipment.",
            ["furniture", "bed", "sofa", "table", "chair"]
        ),
        ConstructionStage(
            "finishing", "Finishing", 12, 5.0,
            "Apply finishing materials and surface treatments.",
            ["paint", "tile", "finish", "texture"]
        ),
        ConstructionStage(
            "complete", "Completed House", 13, 1.0,
            "Display the completed house.",
            ["complete"]
        )
    ]

    @classmethod
    def get_all(cls):
        return [stage.to_dict() for stage in cls.DEFAULT_STAGES]

    @classmethod
    def get_stage(cls, stage_id):
        for stage in cls.DEFAULT_STAGES:
            if stage.stage_id == stage_id:
                return stage.to_dict()

        raise ValueError(f"Unknown construction stage: {stage_id}")

    @classmethod
    def get_by_order(cls, order):
        for stage in cls.DEFAULT_STAGES:
            if stage.order == order:
                return stage.to_dict()

        raise ValueError(f"Unknown construction stage order: {order}")
