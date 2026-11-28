"""Construction progress and timeline generation."""


class ProgressGenerator:

    @staticmethod
    def _clamp(value, minimum=0.0, maximum=1.0):
        return max(minimum, min(maximum, value))

    def generate_timeline(self, sequence):
        items = sequence.get("sequence", [])

        if not items:
            return {
                "total_duration": 0.0,
                "timeline": []
            }

        timeline = []
        current_time = 0.0

        for item in items:
            duration = float(item.get("duration", 1.0))

            if duration <= 0:
                raise ValueError("Component duration must be positive")

            start_time = current_time
            end_time = start_time + duration

            timeline.append({
                **item,
                "start_time": start_time,
                "end_time": end_time
            })

            current_time = end_time

        return {
            "total_duration": current_time,
            "timeline": timeline
        }

    def get_progress(self, timeline, timestamp):
        total_duration = float(timeline.get("total_duration", 0.0))

        if timestamp < 0:
            raise ValueError("Timestamp cannot be negative")

        if total_duration <= 0:
            return {
                "timestamp": timestamp,
                "progress": 100.0,
                "completed_components": [],
                "active_components": [],
                "pending_components": []
            }

        current_time = min(timestamp, total_duration)

        completed = []
        active = []
        pending = []

        for item in timeline.get("timeline", []):
            start = item["start_time"]
            end = item["end_time"]

            if current_time >= end:
                completed.append(item["component_id"])

            elif current_time >= start:
                active.append({
                    "component_id": item["component_id"],
                    "component_type": item["component_type"],
                    "stage_id": item["stage_id"],
                    "component_progress": self._clamp(
                        (current_time - start) / (end - start)
                    )
                })

            else:
                pending.append(item["component_id"])

        return {
            "timestamp": current_time,
            "total_duration": total_duration,
            "progress": round(
                (current_time / total_duration) * 100, 2
            ),
            "completed_components": completed,
            "active_components": active,
            "pending_components": pending
        }
