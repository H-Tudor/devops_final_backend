from fastapi import status
from fastapi.responses import JSONResponse

from devops_final_backend.services.llm_generator.errors import (
    InvalidModelParameters,
    InvalidModelResponse,
    ModelFailedToRespond,
)

HANDLERS = {
    ModelFailedToRespond: lambda _, exc: JSONResponse(
        content={"detail": exc.message}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    ),
    InvalidModelParameters: lambda _, exc: JSONResponse(
        content={"detail": exc.message}, status_code=status.HTTP_424_FAILED_DEPENDENCY
    ),
    InvalidModelResponse: lambda _, exc: JSONResponse(
        content={"detail": exc.message}, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
    Exception: lambda _, exc: JSONResponse(
        content={"detail": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ),
}
