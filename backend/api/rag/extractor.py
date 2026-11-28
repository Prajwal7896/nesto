
from backend.api.rag.extractor_1.llm_parser import parse_with_llm
from backend.api.rag.extractor_1.prompt import build_prompt
from backend.api.rag.extractor_1.schema import Requirements


def extract_requirements(user_prompt: str) -> Requirements:
    prompt = build_prompt(user_prompt)
    data = parse_with_llm(prompt)

    if isinstance(data, dict):
        plot = data.get("plot")

        if isinstance(plot, dict):
            roads = plot.get("roads")

            if isinstance(roads, str):
                direction = roads.strip().lower()

                directions = {
                    "north", "south", "east", "west",
                    "north-east", "north-west",
                    "south-east", "south-west"
                }

                if direction in directions:
                    plot["facing"] = plot.get("facing") or direction.title()
                    plot["roads"] = 1

            data["plot"] = plot

    return Requirements.model_validate(data)
