# backend/rag/schema.py

from typing import List, Optional
from pydantic import BaseModel


class Project(BaseModel):
    name: Optional[str] = None
    building_type: Optional[str] = None
    style: Optional[str] = None
    budget: Optional[int] = None
    currency: Optional[str] = None


class Plot(BaseModel):
    length: Optional[float] = None
    width: Optional[float] = None
    area: Optional[float] = None
    unit: Optional[str] = None
    facing: Optional[str] = None
    shape: Optional[str] = None
    corner_plot: Optional[bool] = None
    roads: Optional[int] = None


class Building(BaseModel):
    floors: Optional[int] = None
    basement: Optional[bool] = None
    stilt_floor: Optional[bool] = None
    terrace: Optional[bool] = None
    slab: Optional[bool] = None
    roof_type: Optional[str] = None
    future_expansion: Optional[bool] = None


class Rooms(BaseModel):
    living_room: Optional[int] = None
    family_room: Optional[int] = None
    bedrooms: Optional[int] = None
    master_bedrooms: Optional[int] = None
    guest_rooms: Optional[int] = None
    children_rooms: Optional[int] = None

    bathrooms: Optional[int] = None
    attached_bathrooms: Optional[int] = None
    common_bathrooms: Optional[int] = None

    kitchen: Optional[int] = None
    kitchen_type: Optional[str] = None

    dining_room: Optional[int] = None

    pooja_room: Optional[int] = None

    study_room: Optional[int] = None

    office: Optional[int] = None

    library: Optional[int] = None

    gym: Optional[int] = None

    home_theatre: Optional[int] = None

    balcony: Optional[int] = None

    utility_room: Optional[int] = None

    laundry_room: Optional[int] = None

    store_room: Optional[int] = None

    walk_in_closet: Optional[int] = None


class Parking(BaseModel):
    required: Optional[bool] = None
    cars: Optional[int] = None
    bikes: Optional[int] = None


class Outdoor(BaseModel):
    garden: Optional[bool] = None
    backyard: Optional[bool] = None
    front_lawn: Optional[bool] = None
    terrace_garden: Optional[bool] = None
    swimming_pool: Optional[bool] = None


class Construction(BaseModel):
    staircase: Optional[bool] = None
    staircase_type: Optional[str] = None
    staircase_position: Optional[str] = None

    beam_type: Optional[str] = None
    column_type: Optional[str] = None
    wall_thickness: Optional[float] = None
    roof_material: Optional[str] = None


class Preferences(BaseModel):
    vastu: Optional[bool] = None
    cross_ventilation: Optional[bool] = None
    natural_light: Optional[bool] = None
    privacy: Optional[bool] = None
    solar_panels: Optional[bool] = None
    rainwater_harvesting: Optional[bool] = None
    smart_home: Optional[bool] = None


class Requirements(BaseModel):
    project: Project
    plot: Plot
    building: Building
    rooms: Rooms
    parking: Parking
    outdoor: Outdoor
    construction: Construction
    preferences: Preferences
    special_requirements: List[str] = []