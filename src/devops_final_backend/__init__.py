"""DevOps Final Backend - LLM Generator

This is the backend of the LLM Generator project for the DevOps Course.
It is a stateless FastAPI app that generates devops related configuration
files using configured LLM integrations
"""

from uvicorn import run

from devops_final_backend.api import app  # noqa: F401
from devops_final_backend.settings import settings  # noqa: F401


def main() -> None:
    """
    Start the FastAPI app as uvicorn application in either debug or production environtment
    Used by the UV project-script `devops_final_backend`
    """
    run("devops_final_backend:app", host="0.0.0.0", port=settings.app_port, reload=settings.debug)


if __name__ == "__main__":
    main()
