# backend/api/rag/validator.py

import math
from backend.api.rag.extractor_1.schema import Requirements


def validate_requirements(req: Requirements) -> Requirements:
    validate_project(req)
    validate_plot(req)
    validate_building(req)
    validate_rooms(req)
    validate_parking(req)
    validate_construction(req)
    calculate_missing_values(req)
    return req


def validate_project(req):
    if req.project.budget is not None and req.project.budget <= 0:
        raise ValueError("Budget must be greater than zero.")


def validate_plot(req):
    if req.plot.length is not None and req.plot.length <= 0:
        raise ValueError("Plot length invalid")
    if req.plot.width is not None and req.plot.width <= 0:
        raise ValueError("Plot width invalid")

    valid_faces = {"North", "South", "East", "West", "North-East", "North-West", "South-East", "South-West"}
    if req.plot.facing and req.plot.facing not in valid_faces:
        raise ValueError("Invalid facing")


def validate_building(req):
    if req.building.floors and req.building.floors < 1:
        raise ValueError("Invalid floors")


def validate_rooms(req):
    for room in ["living_room", "bedrooms", "bathrooms", "kitchen", "dining_room"]:
        val = getattr(req.rooms, room)
        if val is not None and val < 0:
            raise ValueError(f"{room} invalid")

    allocations = req.rooms.floor_allocations
    if allocations is None:
        return

    invalid_floors = set(allocations) - {"ground_floor", "first_floor"}
    if invalid_floors:
        raise ValueError(
            "Invalid floor allocation key(s): "
            + ", ".join(sorted(invalid_floors))
        )

    for floor_name, room_counts in allocations.items():
        for room_type, count in room_counts.items():
            if count < 0:
                raise ValueError(
                    f"{room_type} allocation on {floor_name} cannot be negative."
                )


def validate_parking(req):
    if req.parking.cars and req.parking.cars < 0:
        raise ValueError("Invalid cars")
    if req.parking.bikes and req.parking.bikes < 0:
        raise ValueError("Invalid bikes")


def validate_construction(req):
    if req.building.terrace:
        req.building.slab = True
    if not req.building.roof_type:
        req.building.roof_type = "Flat RCC"
    return req


def calculate_missing_values(req):
    if req.plot.area is None and req.plot.length and req.plot.width:
        req.plot.area = req.plot.length * req.plot.width

    if req.rooms.master_bedrooms is None and req.rooms.bedrooms:
        req.rooms.master_bedrooms = 1

    if req.rooms.living_room is None:
        req.rooms.living_room = 1
    if req.rooms.kitchen is None:
        req.rooms.kitchen = 1
    if req.rooms.dining_room is None:
        req.rooms.dining_room = 1

    if req.rooms.bedrooms and req.rooms.bathrooms is None:
        req.rooms.bathrooms = math.ceil(req.rooms.bedrooms / 2)

    if req.building.terrace:
        req.building.slab = True
    if req.building.roof_type is None:
        req.building.roof_type = "Flat RCC"
    if req.construction.beam_type is None:
        req.construction.beam_type = "RCC"
    if req.construction.column_type is None:
        req.construction.column_type = "RCC"
    if req.construction.wall_thickness is None:
        req.construction.wall_thickness = 230


def validate(layout, constraints=None):
    errors = []
    rooms = layout.get("rooms", [])
    plot = layout.get("plot", {})
    plot_width = plot.get("width", 0)
    plot_height = plot.get("height", 0)

    if not rooms:
        errors.append("No rooms generated")

    for room in rooms:
        if room["x"] + room["width"] > plot_width:
            errors.append(f"{room['id']} outside plot width")
        if room["y"] + room["height"] > plot_height:
            errors.append(f"{room['id']} outside plot height")

    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            if overlap(rooms[i], rooms[j]):
                errors.append(f"Overlap {rooms[i]['id']} {rooms[j]['id']}")

    return {"valid": len(errors) == 0, "errors": errors}


def overlap(a, b):
    return not (
        a["x"] + a["width"] <= b["x"] or
        b["x"] + b["width"] <= a["x"] or
        a["y"] + a["height"] <= b["y"] or
        b["y"] + b["height"] <= a["y"]
    )