from typing import Any

from backend.api.rag.extractor_1.schema import Requirements


def normalize(requirements: Requirements) -> Requirements:
    normalize_project(requirements)
    normalize_plot(requirements)
    normalize_building(requirements)
    normalize_rooms(requirements)
    normalize_parking(requirements)
    normalize_preferences(requirements)
    calculate_area(requirements)
    return requirements


def normalize_project(req: Requirements) -> None:
    if req.project.currency is None:
        req.project.currency = "INR"

    if req.project.style:
        req.project.style = req.project.style.title()

    if req.project.building_type:
        req.project.building_type = req.project.building_type.title()


def normalize_plot(req: Requirements) -> None:
    if req.plot.unit is None:
        req.plot.unit = "Feet"

    if req.plot.facing:
        facing = req.plot.facing.lower().strip()

        mapping = {
            "north": "North",
            "south": "South",
            "east": "East",
            "west": "West",
            "north east": "North-East",
            "north-east": "North-East",
            "north west": "North-West",
            "north-west": "North-West",
            "south east": "South-East",
            "south-east": "South-East",
            "south west": "South-West",
            "south-west": "South-West",
        }

        req.plot.facing = mapping.get(
            facing,
            req.plot.facing.title(),
        )


def normalize_building(req: Requirements) -> None:
    if req.building.basement is None:
        req.building.basement = False

    if req.building.stilt_floor is None:
        req.building.stilt_floor = False

    if req.building.terrace is None:
        req.building.terrace = False

    if req.building.slab is None:
        req.building.slab = False

    if req.building.future_expansion is None:
        req.building.future_expansion = False


def normalize_rooms(req: Requirements) -> None:
    room_fields = [
        "living_room",
        "family_room",
        "bedrooms",
        "master_bedrooms",
        "guest_rooms",
        "children_rooms",
        "bathrooms",
        "attached_bathrooms",
        "common_bathrooms",
        "kitchen",
        "dining_room",
        "study_room",
        "office",
        "library",
        "gym",
        "home_theatre",
        "balcony",
        "utility_room",
        "laundry_room",
        "store_room",
        "walk_in_closet",
        "pooja_room",
    ]

    for room in room_fields:
        value = getattr(req.rooms, room)

        if value is None:
            setattr(req.rooms, room, 0)


def normalize_parking(req: Requirements) -> None:
    if req.parking.required is None:
        req.parking.required = (
            (req.parking.cars or 0) > 0
            or (req.parking.bikes or 0) > 0
        )

    if req.parking.cars is None:
        req.parking.cars = 0

    if req.parking.bikes is None:
        req.parking.bikes = 0


def normalize_preferences(req: Requirements) -> None:
    boolean_fields = [
        "vastu",
        "cross_ventilation",
        "natural_light",
        "privacy",
        "solar_panels",
        "rainwater_harvesting",
        "smart_home",
    ]

    for field in boolean_fields:
        value = getattr(req.preferences, field)

        if value is None:
            setattr(req.preferences, field, False)


def calculate_area(req: Requirements) -> None:
    if (
        req.plot.area is None
        and req.plot.length
        and req.plot.width
    ):
        req.plot.area = req.plot.length * req.plot.width