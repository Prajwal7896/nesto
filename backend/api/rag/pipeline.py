
import logging
import re
import inspect
import time
from collections import Counter
from typing import Any

from backend.api.rag.extractor import extract_requirements
from backend.api.rag.extractor_1.normalizer import normalize
from backend.api.rag.extractor_1.validator import validate_requirements
from backend.api.rag.layout_validator import validate_layout
from backend.api.rag.merger import merge
from backend.api.rag.planner import LayoutPlanner, generate_layout
from backend.api.rag.renderer.renderer import Renderer
from backend.api.rag.retriever import search
from backend.memory.conversation import (
    create_project_id,
    get_project,
    load,
    save,
)

logger = logging.getLogger(__name__)


UNIT_TO_MM = {
    "mm": 1.0,
    "millimeter": 1.0,
    "millimeters": 1.0,
    "cm": 10.0,
    "centimeter": 10.0,
    "centimeters": 10.0,
    "m": 1000.0,
    "meter": 1000.0,
    "meters": 1000.0,
    "in": 25.4,
    "inch": 25.4,
    "inches": 25.4,
    "ft": 304.8,
    "foot": 304.8,
    "feet": 304.8,
}


def _plot_dimensions_mm(requirements: Any) -> tuple[float, float]:
    plot = getattr(requirements, "plot", None)

    if plot is None:
        raise ValueError("Plot information is missing.")

    unit = str(getattr(plot, "unit", None) or "feet").strip().lower()

    factor = UNIT_TO_MM.get(unit)

    if factor is None:
        raise ValueError(f"Unsupported plot unit: {unit}")

    width = getattr(plot, "width", None)
    length = getattr(plot, "length", None)

    if width is None or length is None:
        raise ValueError("Plot width and length are required.")

    width = float(width)
    length = float(length)

    if width <= 0 or length <= 0:
        raise ValueError("Plot dimensions must be positive.")

    return width * factor, length * factor


def _apply_prompt_plot_dimensions(requirements: Any, prompt: str) -> Any:
    plot = getattr(requirements, "plot", None)

    if plot is None:
        return requirements

    text = prompt.lower()

    number = r"(\d+(?:\.\d+)?)"

    unit = (
        r"(millimeters?|mm|centimeters?|cm|"
        r"meters?|m|inches?|inch|in|feet|foot|ft)"
    )

    separator = r"(?:x|×|by)"

    # Example: 30 feet x 40 feet
    pattern = (
        rf"{number}\s*{unit}\s*{separator}\s*"
        rf"{number}\s*{unit}"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        width = float(match.group(1))
        width_unit = match.group(2).lower()
        length = float(match.group(3))
        length_unit = match.group(4).lower()

    else:
        # Example: plot size 30 x 40 feet
        pattern = (
            rf"(?:plot|land|site)\s*"
            rf"(?:size|dimensions?)?\s*[:=]?\s*"
            rf"{number}\s*{separator}\s*"
            rf"{number}\s*{unit}"
        )

        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            # Example: 30 x 40 ft plot
            pattern = (
                rf"{number}\s*{separator}\s*"
                rf"{number}\s*{unit}\s*"
                rf"(?:plot|land|site)"
            )

            match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            return requirements

        width = float(match.group(1))
        length = float(match.group(2))
        width_unit = length_unit = match.group(3).lower()

    if width <= 0 or length <= 0:
        return requirements

    width_factor = UNIT_TO_MM.get(width_unit)
    length_factor = UNIT_TO_MM.get(length_unit)

    if width_factor is None or length_factor is None:
        raise ValueError("Unsupported plot dimension unit.")

    # Store all dimensions consistently in millimeters.
    plot.width = width * width_factor
    plot.length = length * length_factor
    plot.unit = "mm"

    plot.area = plot.width * plot.length

    return requirements


def _model_dump(value: Any) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    if isinstance(value, dict):
        return value

    return {}


def _safe_error(
    stage: str,
    error: Exception,
    timings: dict[str, float] | None = None,
) -> dict:
    logger.exception("Nesto generation failed during %s", stage)

    return {
        "status": "failed",
        "reason": f"{stage} failed: {str(error)}",
        "stage": stage,
        "timings": timings or {},
    }


def _run_timed(timings: dict[str, float], name: str, function, *args, **kwargs):
    started = time.perf_counter()
    try:
        return function(*args, **kwargs)
    finally:
        elapsed = time.perf_counter() - started
        timings[name] = elapsed
        logger.info("stage_timing stage=%s seconds=%.6f", name, elapsed)


def _explicitly_requests(prompt: str, phrase: str) -> bool:
    for match in re.finditer(re.escape(phrase), prompt, re.IGNORECASE):
        prefix = prompt[max(0, match.start() - 24):match.start()]
        if re.search(
            r"\b(?:no|without|omit|exclude)\s+(?:(?:a|an|the|any)\s+)?$",
            prefix,
            re.IGNORECASE,
        ):
            continue
        return True
    return False


def _has_explicit_floor_room_allocation(prompt: str) -> bool:
    text = prompt.lower()
    return bool(
        re.search(r"\bground[- ]floor\b", text)
        and re.search(r"\b(first|upper)[- ]floor\b", text)
    )


def _validate_generated_layout(
    layout: dict,
    constraints: dict | None = None,
) -> dict:
    floors = layout.get("floors")

    if not isinstance(floors, dict) or not floors:
        raise ValueError(
            "Planner did not return a valid floors dictionary."
        )

    if "ground_floor" not in floors:
        raise ValueError(
            "Generated layout does not contain ground_floor."
        )

    floor_validations = {}

    for floor_name, floor_layout in floors.items():

        if not isinstance(floor_layout, dict):
            raise ValueError(
                f"Invalid layout data for {floor_name}."
            )

        rooms = floor_layout.get("rooms")

        if not isinstance(rooms, list):
            raise ValueError(
                f"Rooms must be a list in {floor_name}."
            )

        validation_layout = dict(floor_layout)

        validation_layout["rooms"] = (
            rooms
            + floor_layout.get("site_features", [])
            + floor_layout.get("open_spaces", [])
        )

        result = validate_layout(validation_layout)

        if not isinstance(result, dict):
            raise ValueError(
                f"Invalid validation response for {floor_name}."
            )

        floor_validations[floor_name] = result

    errors = []
    checks = {}
    planner = LayoutPlanner()
    checks["circulation"] = {}
    for floor_name, floor_layout in floors.items():
        connected = planner.validate_floor_circulation(floor_layout)
        checks["circulation"][floor_name] = connected
        if not connected:
            errors.append(
                f"{floor_name} has disconnected room or access-space "
                "circulation."
            )

    room_counts = {}
    floor_allocations = {}
    building_constraints = {}
    if isinstance(constraints, dict):
        space_constraints = constraints.get("space_constraints", {})
        room_counts = dict(space_constraints.get("rooms") or {})
        embedded_allocations = room_counts.pop("floor_allocations", {})
        floor_allocations = (
            space_constraints.get("floor_allocations")
            or embedded_allocations
        )
        building_constraints = constraints.get("building_constraints", {})

    if room_counts:
        expected_types = Counter(
            room["type"]
            for room in planner.requested_room_specs(room_counts)
        )
        actual_types = Counter(
            room.get("type")
            for floor_layout in floors.values()
            for room in floor_layout["rooms"]
        )
        checks["room_counts"] = {
            "expected": dict(expected_types),
            "generated": dict(actual_types),
        }
        if expected_types != actual_types:
            errors.append(
                "Generated room types/counts do not match the requested "
                f"counts: expected {dict(expected_types)}, "
                f"found {dict(actual_types)}."
            )

        if floor_allocations:
            for floor_name, requested in floor_allocations.items():
                actual_floor = floors.get(floor_name)
                if actual_floor is None:
                    errors.append(
                        f"Requested room allocation references missing "
                        f"{floor_name}."
                    )
                    continue
                expected_floor = Counter(
                    {
                        room_type: count
                        for room_type, count in requested.items()
                        if count
                    }
                )
                actual_floor_types = Counter(
                    room.get("type")
                    for room in actual_floor["rooms"]
                )
                checks.setdefault("floor_room_counts", {})[floor_name] = {
                    "expected": dict(expected_floor),
                    "generated": dict(actual_floor_types),
                }
                if expected_floor != actual_floor_types:
                    errors.append(
                        f"{floor_name} room allocation mismatch: expected "
                        f"{dict(expected_floor)}, found "
                        f"{dict(actual_floor_types)}."
                    )

    room_ids = [
        room.get("id")
        for floor_layout in floors.values()
        for room in floor_layout["rooms"]
        if room.get("id")
    ]
    if len(room_ids) != len(set(room_ids)):
        errors.append("Generated room assignments contain duplicate room IDs.")

    floor_count = building_constraints.get("floors") or len(floors)
    if floor_count > 1:
        if "first_floor" not in floors:
            errors.append(
                "A multi-floor request did not generate first_floor."
            )
        stairs_by_floor = {}
        for floor_name in ("ground_floor", "first_floor"):
            floor_layout = floors.get(floor_name)
            stairs = [
                feature
                for feature in (floor_layout or {}).get("site_features", [])
                if feature.get("type") == "staircase"
            ]
            stairs_by_floor[floor_name] = stairs
            if len(stairs) != 1:
                errors.append(
                    f"{floor_name} must contain exactly one staircase."
                )

        if all(len(stairs) == 1 for stairs in stairs_by_floor.values()):
            stair_fields = ("x", "y", "width", "height")
            if any(
                stairs_by_floor["ground_floor"][0].get(field)
                != stairs_by_floor["first_floor"][0].get(field)
                for field in stair_fields
            ):
                errors.append(
                    "First-floor staircase is not aligned with the "
                    "ground-floor staircase."
                )
            landing_count = sum(
                feature.get("type") == "staircase_landing"
                for feature in floors["first_floor"].get("site_features", [])
            )
            if landing_count != 1:
                errors.append(
                    "First floor must contain exactly one staircase landing."
                )
            checks["staircase_alignment"] = landing_count == 1 and not any(
                error.startswith("First-floor staircase is not aligned")
                for error in errors
            )
        if "first_floor" in floors:
            try:
                planner.validate_generated_structure(
                    floors,
                    constraints or {},
                )
                checks["structural_support"] = True
            except (KeyError, TypeError, ValueError) as error:
                checks["structural_support"] = False
                errors.append(f"Structural validation failed: {error}")

    if building_constraints.get("front_porch"):
        porch_count = sum(
            feature.get("type") == "front_porch"
            for feature in floors["ground_floor"].get("site_features", [])
        )
        checks["front_porch"] = porch_count == 1
        if porch_count != 1:
            errors.append(
                "The ground floor must contain exactly one requested front porch."
            )

    family_room_count = room_counts.get("family_room") or 0
    if family_room_count and not room_counts.get("family_room_enclosed", False):
        lounge_floor = "first_floor" if floor_count > 1 else "ground_floor"
        lounge_count = sum(
            area.get("type") == "family_lounge"
            for area in floors.get(lounge_floor, {}).get("open_spaces", [])
        )
        checks["family_lounge"] = lounge_count == family_room_count
        if lounge_count != family_room_count:
            errors.append(
                f"{lounge_floor} must contain {family_room_count} "
                "unenclosed family lounge space(s)."
            )

    for floor_name, result in floor_validations.items():

        if not result.get("valid", False):

            floor_errors = result.get("errors", [])

            errors.extend(
                f"{floor_name}: {error}"
                for error in floor_errors
            )

    return {
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "floors": floor_validations,
        "checks": checks,
    }


def _generate_plan_with_rag(constraints: dict, rag_data: Any):
    """
    Preserve compatibility with existing planner signatures.
    Pass RAG data only when the planner explicitly accepts it.
    """

    signature = inspect.signature(generate_layout)

    if "rag_data" in signature.parameters:
        return generate_layout(
            constraints,
            rag_data=rag_data
        )

    return generate_layout(constraints)

def generate(
    prompt: str,
    user_id: str,
    customization: dict | None = None,
    mode: str = "new",
    project_id: str | None = None,
):
    stage = "initialization"
    timings: dict[str, float] = {}

    try:
        customization = customization or {}

        if not isinstance(customization, dict):
            raise ValueError("Customization must be a dictionary.")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # 1. Extract requirements
        stage = "requirement_extraction"

        current = _run_timed(
            timings, "requirement_extraction", extract_requirements, prompt
        )

        if current is None:
            raise ValueError("Requirement extraction returned empty data.")

        current = _apply_prompt_plot_dimensions(current, prompt)

        logger.info("Requirements extracted successfully.")

        # 2. Determine project mode
        stage = "project_selection"

        mode = (mode or "new").strip().lower()

        if mode not in {"new", "modify"}:
            raise ValueError("Mode must be either 'new' or 'modify'.")

        if mode == "new":
            project_id = create_project_id()
            previous = None

        else:
            if not project_id:
                raise ValueError(
                    "Select an existing project before modifying it."
                )

            project = get_project(user_id, project_id)

            if not project:
                raise ValueError(
                    "Project not found or you do not have access to it."
                )

            previous = load(user_id, project_id)

            if previous is None:
                raise ValueError(
                    "Saved requirements for this project were not found."
                )

        # 3. Merge requirements
        stage = "requirement_merging"

        requirements = _run_timed(
            timings, "requirement_merging", merge, previous, current
        )

        if requirements is None:
            raise ValueError(
                "Requirement merging returned empty data."
            )

        requirements = _apply_prompt_plot_dimensions(
            requirements,
            prompt
        )

        # 4. Normalize
        stage = "normalization"

        requirements = _run_timed(
            timings, "normalization", normalize, requirements
        )

        # 5. Validate requirements
        stage = "requirement_validation"

        requirements = _run_timed(
            timings,
            "requirement_validation",
            validate_requirements,
            requirements,
        )

        if requirements is None:
            raise ValueError(
                "Requirement validation returned empty data."
            )

        room_counts = _model_dump(requirements.rooms)
        floor_allocations = room_counts.pop("floor_allocations", None)
        floor_count = requirements.building.floors or 1
        outdoor = _model_dump(requirements.outdoor)

        if (
            floor_count > 1
            and _has_explicit_floor_room_allocation(prompt)
            and not floor_allocations
        ):
            raise ValueError(
                "The request assigns rooms to specific floors, but "
                "requirement extraction did not preserve those allocations."
            )
        if (
            _explicitly_requests(prompt, "porch")
            and outdoor.get("front_porch") is not True
        ):
            raise ValueError(
                "The request includes a porch, but requirement extraction "
                "did not preserve it."
            )
        if (
            _explicitly_requests(prompt, "family lounge")
            and not room_counts.get("family_room")
        ):
            raise ValueError(
                "The request includes a family lounge, but requirement "
                "extraction did not preserve it."
            )

        # 6. Convert plot dimensions
        stage = "plot_validation"

        plot_width_mm, plot_height_mm = _plot_dimensions_mm(
            requirements
        )

        # 7. RAG retrieval
        stage = "rag_retrieval"

        rag_data = _run_timed(timings, "rag_retrieval", search, requirements)

        # 8. Build constraints
        stage = "constraint_generation"

        constraints = {
            "space_constraints": {
                "plot_width": plot_width_mm,
                "plot_height": plot_height_mm,
                "rooms": room_counts,
                "floor_allocations": floor_allocations,
            },
            "building_constraints": {
                "floors": floor_count,
                "staircase": requirements.construction.staircase,
                "front_porch": outdoor.get("front_porch") is True,
                "parking": _model_dump(requirements.parking),
            },
            "planning_constraints": {
                "privacy": requirements.preferences.privacy,
                "ventilation": (
                    requirements.preferences.cross_ventilation
                ),
                "natural_light": (
                    requirements.preferences.natural_light
                ),
                "zoning": True,
            },
            "vastu_constraints": {
                "enabled": requirements.preferences.vastu,
                "kitchen_direction": "south-east",
                "master_bedroom_direction": "south-west",
            },
            "structural_constraints": {
                "beam_type": requirements.construction.beam_type,
                "column_type": requirements.construction.column_type,
                "balcony_cantilever_supported": (
                    requirements.construction.balcony_cantilever_supported
                    is True
                ),
                "wall_thickness": (
                    requirements.construction.wall_thickness
                ),
            },
            "engineering_constraints": {},
            "cost_constraints": {
                "budget": requirements.project.budget,
            },
        }

        # 9. Generate layout
        stage = "layout_generation"

        layout = _run_timed(
            timings,
            "layout_planning",
            _generate_plan_with_rag,
            constraints,
            rag_data,
        )

        if not isinstance(layout, dict):
            raise ValueError(
                "Planner returned an invalid generation response."
            )

        # 10. Validate layout
        stage = "layout_validation"

        validation_result = _run_timed(
            timings,
            "layout_validation",
            _validate_generated_layout,
            layout,
            constraints,
        )

        if not validation_result["valid"]:
            return {
                "status": "failed",
                "reason": (
                    "Generated layout failed geometry validation. "
                    "It was not rendered."
                ),
                "layout": layout,
                "validation": validation_result,
                "constraints": constraints,
                "stage": stage,
                "timings": timings,
            }

        # 11. Render each floor
        stage = "rendering"

        renderer = Renderer()
        floor_files = {}

        for floor_name, floor_layout in layout["floors"].items():

            base_name = (
                f"floorplan_{user_id}_{project_id}"
                if floor_name == "ground_floor"
                else f"floorplan_{user_id}_{project_id}_{floor_name}"
            )

            floor_files[floor_name] = _run_timed(
                timings,
                f"floorplan_rendering_{floor_name}",
                renderer.render,
                floor_layout,
                prompt,
                user_id,
                base_name=base_name,
                customization=customization,
                prevalidated=True,
            )

        # 12. Verify ground floor files
        if "ground_floor" not in floor_files:
            raise ValueError(
                "Ground floor rendering did not produce output."
            )

        files = dict(floor_files["ground_floor"])
        files["floors"] = floor_files

        files.setdefault(
            "png_url",
            f"/output/floorplan_{user_id}_{project_id}.png"
        )

        files.setdefault(
            "svg_url",
            f"/output/floorplan_{user_id}_{project_id}.svg"
        )

        files.setdefault(
            "dxf_url",
            f"/output/floorplan_{user_id}_{project_id}.dxf"
        )

        # 13. Save requirements after successful rendering
        stage = "memory_saving"

        _run_timed(
            timings,
            "memory_saving",
            save,
            user_id=user_id,
            project_id=project_id,
            requirements=requirements,
            prompt=prompt,
        )

        logger.info(
            "Nesto generation completed successfully for user %s",
            user_id
        )

        # 14. Final response
        return {
            "status": "success",
            "project_id": project_id,
            "project_name": prompt.strip()[:60],
            "mode": mode,
            "prompt": prompt,
            "requirements": _model_dump(requirements),
            "rag_data": rag_data,
            "constraints": constraints,
            "layout": layout,
            "validation": validation_result,
            "files": files,
            "timings": timings,
        }

    except Exception as error:
        return _safe_error(stage, error, timings)

