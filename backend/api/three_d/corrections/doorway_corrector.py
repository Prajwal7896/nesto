class DoorwayCorrector:

    def correct(self, floor):
        return {
            "changes": [],
            "unresolved": [
                {
                    "category": "doorway",
                    "reason": (
                        "Automatic door creation is disabled until "
                        "wall geometry and opening positions are verified."
                    )
                }
            ]
        }