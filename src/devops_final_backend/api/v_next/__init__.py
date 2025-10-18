"""vNext

This is the development version with the features that will be included in the next release.

This version's router contains all the endpoints that will be presented (if this were a more
complex application then the router would have included sub-routers)

Within this package there are the model definitions which are versioned as well
"""

from fastapi import APIRouter, Body, status

from devops_final_backend.services.llm_generator import ComposeGenerator
from devops_final_backend.services.llm_generator import models as llm_models
from devops_final_backend.settings import settings

from .models import ComposeGenerationParameters

__all__ = ["router"]

router = APIRouter()


@router.post(
    "/gen/compose",
    responses={
        status.HTTP_200_OK: {"description": "Returned LLM Response"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Failed Bearer Token Authentification"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Failed Parameters Validation"},
        status.HTTP_424_FAILED_DEPENDENCY: {"description": "Failed Response Validation"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Server Side Logic Error"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Model Failed to generate response"},
    },
)
async def generate_compose(params: ComposeGenerationParameters = Body(...)) -> list[llm_models.LLMResponse]:
    """Api Endpoint for generating Docker Compose Files

    Args:
        params (ComposeGenerationParameters): generation parameters as expected from request

    Returns:
        list[LLMResponse]: the generated file contents
    """

    return ComposeGenerator(settings.llm_dry_run).run(params.model_dump())
