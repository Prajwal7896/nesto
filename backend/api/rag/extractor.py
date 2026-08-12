from backend.api.rag.extractor_1.llm_parser import parse_with_llm
from backend.api.rag.extractor_1.normalizer import normalize
from backend.api.rag.extractor_1.prompt import build_prompt
from backend.api.rag.extractor_1.schema import Requirements
from backend.api.rag.extractor_1.validator import validate_requirements


def extract_requirements(user_prompt: str) -> Requirements:
    prompt = build_prompt(user_prompt)
    data = parse_with_llm(prompt)

    requirements = Requirements.model_validate(data)
    requirements = validate_requirements(requirements)
    requirements = normalize(requirements)

    return Requirements.model_validate(requirements)