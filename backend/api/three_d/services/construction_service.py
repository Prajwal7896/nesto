from backend.api.three_d.construction.construction_sequence import (
    ConstructionSequence,
)
from backend.api.three_d.construction.progress_generator import (
    ProgressGenerator,
)


class ConstructionService:

    def __init__(self):
        self.sequence_generator = ConstructionSequence()
        self.progress_generator = ProgressGenerator()

    def get_components(self, scene):

        components = []

        for floor in scene.get("floors", []):

            floor_id = floor.get("id", "floor")

            components.append({
                "id": f"{floor_id}:floor",
                "type": "floor",
                "floor_id": floor_id,
            })

            for wall in floor.get("walls", []):
                components.append({
                    "id": wall["id"],
                    "type": "wall",
                    "floor_id": floor_id,
                })

            for door in floor.get("doors", []):
                components.append({
                    "id": door["id"],
                    "type": "door",
                    "floor_id": floor_id,
                })

            for window in floor.get("windows", []):
                components.append({
                    "id": window["id"],
                    "type": "window",
                    "floor_id": floor_id,
                })

        return components

    def get_construction(self, scene):

        components = self.get_components(scene)

        sequence = self.sequence_generator.generate(
            components
        )

        timeline = self.progress_generator.generate_timeline(
            sequence
        )

        return {
            "scene_id": scene["id"],
            "components": components,
            "sequence": sequence,
            "timeline": timeline,
        }

    def get_progress(self, scene, timestamp):

        construction = self.get_construction(scene)

        progress = self.progress_generator.get_progress(
            construction["timeline"],
            timestamp,
        )

        return {
            "scene_id": scene["id"],
            **progress,
        }


construction_service = ConstructionService()
