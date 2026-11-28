class CirculationAnalyzer:

    MINIMUM_CORRIDOR_WIDTH_MM = 900.0

    def _get(self, obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def analyze(self, floor):
        rooms = self._get(floor, "rooms", []) or []
        doors = self._get(floor, "doors", []) or []

        warnings = []

        for door in doors:
            width = float(self._get(door, "width", 0))

            if width <= 0:
                warnings.append(
                    f"{self._get(door, 'id')}: invalid door width."
                )
            elif width < self.MINIMUM_CORRIDOR_WIDTH_MM:
                warnings.append(
                    f"{self._get(door, 'id')}: door width is below "
                    f"{self.MINIMUM_CORRIDOR_WIDTH_MM:.0f} mm. "
                    "Review accessibility and intended use."
                )

        return {
            "floor_id": self._get(floor, "id"),
            "room_count": len(rooms),
            "door_count": len(doors),
            "warnings": warnings
        }