from uvicorn import run

from devops_final_backend.api import app  # noqa: F401


def main() -> None:
    run("devops_final_backend:app", reload=True)
