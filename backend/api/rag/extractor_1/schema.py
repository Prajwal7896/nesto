
from typing import Dict, List, Optional
import re
from pydantic import BaseModel, Field, validator


class Project(BaseModel):
    name: Optional[str] = None
    building_type: Optional[str] = None
    style: Optional[str] = None
    budget: Optional[float] = None
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

    @validator("roads", pre=True)
    def validate_roads(cls, value):
        if value is None:
            return value

        if isinstance(value, str):
            direction = value.strip().capitalize()

            if direction in {"North", "South", "East", "West"}:
                return 1

            if not value.strip().isdigit():
                raise ValueError("Roads must be an integer.")

            return int(value.strip())

        return value

    @validator("facing", pre=True)
    def validate_facing(cls, value):
        if value is None:
            return value

        if isinstance(value, str):
            value = value.strip().capitalize()

            valid_directions = {
                "North", "South", "East", "West",
                "North-East", "North-West",
                "South-East", "South-West"
            }

            if value not in valid_directions:
                raise ValueError("Invalid plot facing direction.")

        return value



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
    family_room_enclosed: Optional[bool] = None
    floor_allocations: Optional[Dict[str, Dict[str, int]]] = None
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
    front_porch: Optional[bool] = None
    garden: Optional[bool] = None
    backyard: Optional[bool] = None
    front_lawn: Optional[bool] = None
    terrace_garden: Optional[bool] = None
    swimming_pool: Optional[bool] = None


class Construction(BaseModel):
    staircase: Optional[bool] = None
    staircase_type: Optional[str] = None
    staircase_position: Optional[str] = None
    balcony_cantilever_supported: Optional[bool] = None

    beam_type: Optional[str] = None
    column_type: Optional[str] = None
    wall_thickness: Optional[float] = None
    roof_material: Optional[str] = None

    @validator("wall_thickness", pre=True)
    def validate_wall_thickness(cls, value):
        if value is None:
            return value

        if isinstance(value, (int, float)):
            thickness = float(value)

        elif isinstance(value, str):
            match = re.search(
                r"(\d+(?:\.\d+)?)\s*(mm|millimeters?|cm|centimeters?|m|meters?|inches?|in|ft|feet)?",
                value.lower()
            )

            if not match:
                raise ValueError("Invalid wall thickness format.")

            number = float(match.group(1))
            unit = match.group(2) or "mm"

            conversions = {
                "mm": 1,
                "millimeter": 1,
                "millimeters": 1,
                "cm": 10,
                "centimeter": 10,
                "centimeters": 10,
                "m": 1000,
                "meter": 1000,
                "meters": 1000,
                "in": 25.4,
                "inch": 25.4,
                "inches": 25.4,
                "ft": 304.8,
                "feet": 304.8,
            }

            thickness = number * conversions[unit]

        else:
            raise ValueError("Wall thickness must be numeric or a dimension string.")

        if thickness <= 0:
            raise ValueError("Wall thickness must be greater than zero.")

        return thickness


class Preferences(BaseModel):
    vastu: Optional[bool] = None
    cross_ventilation: Optional[bool] = None
    natural_light: Optional[bool] = None
    privacy: Optional[bool] = None
    solar_panels: Optional[bool] = None
    rainwater_harvesting: Optional[bool] = None
    smart_home: Optional[bool] = None


class Requirements(BaseModel):
    project: Project = Field(default_factory=Project)
    plot: Plot = Field(default_factory=Plot)
    building: Building = Field(default_factory=Building)
    rooms: Rooms = Field(default_factory=Rooms)
    parking: Parking = Field(default_factory=Parking)
    outdoor: Outdoor = Field(default_factory=Outdoor)
    construction: Construction = Field(default_factory=Construction)
    preferences: Preferences = Field(default_factory=Preferences)

    special_requirements: List[str] = Field(default_factory=list)
