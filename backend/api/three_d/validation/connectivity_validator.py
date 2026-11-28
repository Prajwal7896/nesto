
from collections import deque


class RoomConnectivityValidator:
    """Validates room connectivity using actual door connections."""

    def _get(self, obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _door_endpoints(self, door):
        source = self._get(door, "source", {}) or {}

        from_id = self._get(source, "from_id")
        to_id = self._get(source, "to_id")

        # Support endpoints stored directly on a door too.
        if not from_id:
            from_id = self._get(door, "from_id")
        if not to_id:
            to_id = self._get(door, "to_id")

        return from_id, to_id

    def _components(self, graph):
        visited = set()
        components = []

        for start in graph:
            if start in visited:
                continue

            component = []
            queue = deque([start])
            visited.add(start)

            while queue:
                current = queue.popleft()
                component.append(current)

                for neighbor in graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

        return components

    def validate_floor(self, floor):
        rooms = self._get(floor, "rooms", []) or []
        open_spaces = self._get(floor, "open_spaces", []) or []
        site_features = self._get(floor, "site_features", []) or []
        doors = self._get(floor, "doors", []) or []
        connections = self._get(floor, "connections", []) or []

        room_ids = {
            self._get(room, "id")
            for room in rooms
            if self._get(room, "id")
        }
        open_space_ids = {
            self._get(space, "id")
            for space in open_spaces
            if self._get(space, "id")
        }
        access_feature_ids = {
            self._get(feature, "id")
            for feature in site_features
            if self._get(feature, "id")
            and self._get(feature, "type")
            in {"front_porch", "staircase", "staircase_landing"}
        }
        node_ids = room_ids | open_space_ids | access_feature_ids

        graph = {node_id: set() for node_id in node_ids}
        errors = []
        warnings = []
        door_connections = []

        # Build the graph using actual door endpoints.
        for door in doors:
            door_id = self._get(door, "id", "unknown_door")
            from_id, to_id = self._door_endpoints(door)

            if not from_id or not to_id:
                warnings.append(
                    f"{door_id}: missing from_id or to_id in door source."
                )
                continue

            if from_id not in node_ids or to_id not in node_ids:
                errors.append(
                    f"{door_id}: references an unknown room or access space "
                    f"({from_id} -> {to_id})."
                )
                continue

            if from_id == to_id:
                errors.append(
                    f"{door_id}: connects a room to itself."
                )
                continue

            graph[from_id].add(to_id)
            graph[to_id].add(from_id)

            door_connections.append({
                "door_id": door_id,
                "from_id": from_id,
                "to_id": to_id
            })

        # Compare declared room connections with actual doors.
        actual_pairs = {
            frozenset((item["from_id"], item["to_id"]))
            for item in door_connections
        }

        missing_door_connections = []

        for connection in connections:
            from_id = self._get(connection, "from_id")
            to_id = self._get(connection, "to_id")
            connection_kind = self._get(connection, "kind", "door")

            if not from_id or not to_id:
                warnings.append(
                    "A declared connection is missing from_id or to_id."
                )
                continue

            if from_id not in node_ids or to_id not in node_ids:
                warnings.append(
                    f"Declared connection references an unknown room or "
                    f"access space: "
                    f"{from_id} -> {to_id}."
                )
                continue

            if connection_kind == "open_flow":
                graph[from_id].add(to_id)
                graph[to_id].add(from_id)
                continue

            pair = frozenset((from_id, to_id))

            if pair not in actual_pairs:
                missing_door_connections.append({
                    "from_id": from_id,
                    "to_id": to_id
                })

        for item in missing_door_connections:
            warnings.append(
                "Declared connection has no matching physical door: "
                f"{item['from_id']} -> {item['to_id']}."
            )

        # Find disconnected room groups.
        components = self._components(graph)

        # Prefer the living room as the main circulation reference.
        main_room = next(
            (
                room_id for room_id in room_ids
                if "living_room" in room_id.lower()
            ),
            None
        )

        if main_room is None and room_ids:
            main_room = next(iter(room_ids))

        reachable = set()
        if main_room:
            queue = deque([main_room])
            reachable.add(main_room)

            while queue:
                current = queue.popleft()

                for neighbor in graph[current]:
                    if neighbor not in reachable:
                        reachable.add(neighbor)
                        queue.append(neighbor)

        disconnected_nodes = sorted(node_ids - reachable)
        disconnected_rooms = sorted(room_ids - reachable)

        for room_id in disconnected_nodes:
            warnings.append(
                f"{room_id} is not reachable from the main room "
                "through physical doors or open circulation."
            )

        return {
            "floor_id": self._get(floor, "id"),
            "valid": len(errors) == 0 and len(warnings) == 0,
            "room_count": len(room_ids),
            "access_space_count": len(node_ids - room_ids),
            "door_count": len(door_connections),
            "declared_connection_count": len(connections),
            "physical_connection_count": len(door_connections),
            "main_room": main_room,
            "connected_components": components,
            "disconnected_rooms": disconnected_rooms,
            "disconnected_nodes": disconnected_nodes,
            "missing_door_connections": missing_door_connections,
            "door_connections": door_connections,
            "errors": errors,
            "warnings": warnings
        }
