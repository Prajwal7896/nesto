class FurnitureCorrector:

    def __init__(self, quality_pipeline):
        self.quality_pipeline = quality_pipeline

    def correct(self, floor):
        changes, unresolved = (
            self.quality_pipeline._correct_furniture(floor)
        )

        return {
            "changes": changes,
            "unresolved": unresolved,
            "success": len(unresolved) == 0
        }