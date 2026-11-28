class RoomCorrector:

    def correct(self, floor):
        return {
            "changes": [],
            "unresolved": [
                {
                    "category": "room_geometry",
                    "reason": (
                        "Automatic room movement is disabled until "
                        "room adjacency and wall constraints are verified."
                    )
                }
            ]
        }