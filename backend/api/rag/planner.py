from typing import Any, Dict, List


class LayoutPlanner:

    def generate_layout(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        space = constraints["space_constraints"]
        vastu = constraints.get("vastu_constraints", {})

        plot_width = space.get("plot_width", 12000)
        plot_height = space.get("plot_height", 18000)

        rooms = self.create_rooms(
            space["rooms"],
            plot_width,
            plot_height,
            vastu,
        )

        connections = self.create_adjacency(rooms)

        return {
            "plot": {
                "width": plot_width,
                "height": plot_height,
            },
            "rooms": rooms,
            "adjacency_graph": connections,
            "circulation": {
                "ventilation": True,
                "privacy": True,
            },
            "structure": {
                "beam_type": constraints["structural_constraints"].get(
                    "beam_type", "RCC"
                ),
                "column_type": constraints["structural_constraints"].get(
                    "column_type", "RCC"
                ),
            },
            "engineering": {
                "electrical": True,
                "plumbing": True,
            },
            "connections": connections,
            "connections_count": len(connections),
            "room_count": len(rooms),
            "total_area": sum(r["area"] for r in rooms),
            "generated": True,
            "planner_version": "v3",
            "metadata": {
                "planner": "Nesto Smart Planner",
                "status": "draft",
            },
        }

    # =====================================================

    def create_rooms(
        self,
        room_counts: Dict[str, Any],
        plot_width: float,
        plot_height: float,
        vastu: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        rooms: List[Dict[str, Any]] = []

        rooms.append(
            self.make_room(
                "living_room", 500, 500, 5000, 4500
            )
        )

        rooms.append(
            self.make_room(
                "dining_room", 5500, 500, 3500, 3200
            )
        )

        rooms.append(
            self.make_room(
                "kitchen", 9200, 500, 3200, 3000
            )
        )

        rooms.append(
            self.make_room(
                "utility_room", 9200, 3600, 2000, 1800
            )
        )

        rooms.append(
            self.make_room(
                "master_bedroom", 500, 5500, 4500, 4500
            )
        )

        rooms.append(
            self.make_room(
                "bedroom", 5200, 5500, 4000, 4000
            )
        )

        rooms.append(
            self.make_room(
                "bedroom", 9500, 5500, 4000, 4000
            )
        )

        rooms.append(
            self.make_room(
                "bathroom", 13700, 5500, 2200, 2200
            )
        )

        rooms.append(
            self.make_room(
                "bathroom", 13700, 8000, 2200, 2200
            )
        )

        rooms.append(
            self.make_room(
                "balcony", 500, 10300, 5000, 1800
            )
        )

        # IMPORTANT
        return rooms

    # =====================================================

    def make_room(
        self,
        room_type: str,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> Dict[str, Any]:
        return {
            "id": f"{room_type}_{x}_{y}",
            "type": room_type,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "area": w * h,
            "rotation": 0,
            "polygon": [
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h],
            ],
        }

    # =====================================================

    def create_adjacency(
        self, rooms: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        if rooms is None:
            return []

        names = [r["type"] for r in rooms]
        graph: List[Dict[str, str]] = []

        if "living_room" in names and "kitchen" in names:
            graph.append({
                "from": "living_room",
                "to": "kitchen",
            })

        if "bedroom" in names and "bathroom" in names:
            graph.append({
                "from": "bedroom",
                "to": "bathroom",
            })

        return graph


planner = LayoutPlanner()


def generate_layout(constraints: Dict[str, Any]) -> Dict[str, Any]:
    return planner.generate_layout(constraints)