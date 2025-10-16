from uvicorn import run

from devops_final_backend.api import app  # noqa: F401
from devops_final_backend.settings import settings  # noqa: F401


def main() -> None:
    """
    Start the FastAPI app as uvicorn application in either debug or production environtment
    Used by the UV project-script `devops_final_backend`
    """
    if settings.debug:
        run("devops_final_backend:app", reload=True, port=8000)
    else:
        run("devops_final_backend:app", host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()
