from fastapi import APIRouter

from devops_final_backend.services.llm_generator import ComposeGenerator, LLMResponse

from .models import ComposeGenerationParameters

router = APIRouter(prefix="/vNext")


@router.post("/gen/compose")
def generate_compose(params: ComposeGenerationParameters) -> list[LLMResponse]:
    """Api Endpoint for generating Docker Compose Files

    Args:
        params (ComposeGenerationParameters): generation parameters as expected from request

    Returns:
        list[LLMResponse]: the generated file contents
    """

    return ComposeGenerator().run(params.model_dump())
