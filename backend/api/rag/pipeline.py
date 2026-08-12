from typing import Any, Dict

from backend.api.rag.constraints import build_constraints
from backend.api.rag.extractor import extract_requirements
from backend.api.rag.extractor_1.normalizer import normalize
from backend.api.rag.extractor_1.validator import validate_requirements
from backend.api.rag.layout_validator import validate_layout
from backend.api.rag.merger import merge
from backend.api.rag.optimizer import optimize
from backend.api.rag.planner import generate_layout
from backend.api.rag.renderer.renderer import Renderer
from backend.api.rag.retriever import search
from backend.memory.conversation import load, save


def generate(prompt: str, user_id: str) -> Dict[str, Any]:
    # 1. Extract requirements
    current = extract_requirements(prompt)
    print(current.rooms)

    # 2. Load memory
    previous = load(user_id)

    # 3. Merge memory + current
    requirements = merge(previous, current)

    # 4. Normalize
    requirements = normalize(requirements)
    requirements = validate_requirements(requirements)

    # 5. Save memory
    save(user_id, requirements)

    # 6. RAG retrieval (single call)
    rag_data = search(requirements)

    # 7. Constraints (building full strict layout-bound dictionary constraints)
    constraints = {
        "space_constraints": {
            "plot_width": requirements.plot.width * 300,
            "plot_height": requirements.plot.length * 300,
            "rooms": requirements.rooms.model_dump(),
        },
        "planning_constraints": {
            "privacy": requirements.preferences.privacy,
            "ventilation": requirements.preferences.cross_ventilation,
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
        },
        "engineering_constraints": {},
        "cost_constraints": {
            "budget": requirements.project.budget,
        },
    }

    layout = generate_layout(constraints)

    best_valid_layout = None
    validation_result = None

    # 9. Optimization loop (safe version)
    for _ in range(5):
        layout = optimize(layout)

        validation_result = validate_layout(
            layout,
            constraints,
        )

        if validation_result["valid"]:
            best_valid_layout = layout
            break

    if best_valid_layout is None:
        validation_result = validate_layout(
            layout,
            constraints,
        )
        print(validation_result)
        best_valid_layout = layout

    files = Renderer().render(
        best_valid_layout,
        prompt,
        user_id,
    )

    files["png_url"] = f"/output/floorplan_{user_id}.png"
    files["svg_url"] = f"/output/floorplan_{user_id}.svg"
    files["dxf_url"] = f"/output/floorplan_{user_id}.dxf"

    return {
        "status": "success",
        "prompt": prompt,
        "requirements": requirements,
        "rag_data": rag_data,
        "constraints": constraints,
        "layout": best_valid_layout,
        "validation": validation_result,
        "files": files,
    }