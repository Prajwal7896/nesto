"""Construction sequence generation."""

from .construction_stages import ConstructionStages


class ConstructionSequence:

    TYPE_TO_STAGE = {
        "site": "site_preparation",
        "ground": "site_preparation",
        "excavation": "site_preparation",
        "foundation": "foundation",
        "footing": "foundation",
        "column": "structural_frame",
        "beam": "structural_frame",
        "slab": "slab",
        "floor": "slab",
        "wall": "walls",
        "door": "openings",
        "window": "openings",
        "roof": "roof",
        "railing": "roof",
        "pipe": "plumbing",
        "plumbing": "plumbing",
        "water_tank": "plumbing",
        "drainage": "plumbing",
        "wire": "electrical",
        "conduit": "electrical",
        "socket": "electrical",
        "switchboard": "electrical",
        "light": "electrical",
        "duct": "hvac",
        "air_conditioner": "hvac",
        "ventilation": "hvac",
        "furniture": "furniture",
        "bed": "furniture",
        "sofa": "furniture",
        "table": "furniture",
        "chair": "furniture",
        "paint": "finishing",
        "tile": "finishing",
        "finish": "finishing",
        "texture": "finishing",
    }

    def __init__(self):
        self.stages = ConstructionStages.get_all()

    def identify_stage(self, component_type):
        key = str(component_type).lower().strip()

        if key not in self.TYPE_TO_STAGE:
            raise ValueError(
                f"Unknown component type: {component_type}"
            )

        return self.TYPE_TO_STAGE[key]

    def generate(self, components):
        if not isinstance(components, list):
            raise TypeError("Components must be a list")

        sequence = []

        for index, component in enumerate(components):
            if not isinstance(component, dict):
                raise ValueError(f"Component {index} must be a dictionary")

            component_id = component.get("id", f"component_{index}")
            component_type = component.get("type")

            if not component_type:
                raise ValueError(
                    f"Component {component_id} has no type"
                )

            stage_id = component.get("stage_id")

            if stage_id is None:
                stage_id = self.identify_stage(component_type)

            stage = ConstructionStages.get_stage(stage_id)

            sequence.append({
                "component_id": component_id,
                "component_type": component_type,
                "stage_id": stage_id,
                "stage_order": stage["order"],
                "duration": component.get(
                    "duration", stage["duration"]
                ),
                "component": component
            })

        sequence.sort(
            key=lambda item: (
                item["stage_order"],
                str(item["component_id"])
            )
        )

        return {
            "total_components": len(sequence),
            "total_stages": len(self.stages),
            "sequence": sequence
        }

    def get_stage_components(self, sequence, stage_id):
        return [
            item for item in sequence.get("sequence", [])
            if item["stage_id"] == stage_id
        ]
