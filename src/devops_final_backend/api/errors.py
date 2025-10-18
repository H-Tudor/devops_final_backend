"""API Error Handlers

These lamba functions transform known error types into http exception with dedicated error codes
"""

from fastapi import status
from fastapi.responses import JSONResponse

from devops_final_backend.services.llm_generator import errors as llm_errors

HANDLERS = {
    llm_errors.ModelFailedToRespond: lambda _, exc: JSONResponse(
        content={"detail": exc.message}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    ),
    llm_errors.InvalidModelParameters: lambda _, exc: JSONResponse(
        content={"detail": exc.message}, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    ),
    llm_errors.InvalidModelResponse: lambda _, exc: JSONResponse(
        content={"detail": exc.message}, status_code=status.HTTP_424_FAILED_DEPENDENCY
    ),
    Exception: lambda _, exc: JSONResponse(
        content={"detail": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ),
}
