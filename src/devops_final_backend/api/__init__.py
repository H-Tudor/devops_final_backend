"""API Layer

The API of this application consists of a version endpoint that indicates the current stable version.
The app uses semantic versioning (but for package order consistency use versions <= 99 and write them
on 2 characters)

The next version of the API, which is still under development is stored in the v_next package and
is enabled as a api version if the app is started with the debug variable set to True or if the
current version is set to vNext.

If the application is started in the debuggin mode, the application will expose the generated
documentation links and the index of the application will redired to the openapi (swagger) interactive
page (otherwise will return a 404 Not Found error)

The errors encoutered (or intentionally thrown) during the exection of the api call flow can be intercepted
by declaring a handler lambda function in the error.py file (but for each endpoint, you must declare in the
responses attribute the response codes you anticipate can be returned)
"""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from devops_final_backend.services.auth import get_current_user
from devops_final_backend.settings import settings

from .errors import HANDLERS
from .v_next import router as router_v_next

__all__ = ["app"]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


for error_type, handler in HANDLERS.items():
    app.add_exception_handler(error_type, handler)


@app.get(
    "/",
    tags=["Home"],
    responses={
        status.HTTP_302_FOUND: {"description": "Redirect to docs page in dev environment"},
        status.HTTP_404_NOT_FOUND: {"description": "Page Unavailable in production"},
    },
)
async def index() -> RedirectResponse:
    """
    Root Route that will automatically redirect to the docs page if the application is in debug mode,
    else will return a 404 route not found
    """
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return RedirectResponse("/docs", status.HTTP_302_FOUND)


@app.get(
    "/version",
    tags=["Version"],
    responses={status.HTTP_200_OK: {"description": "returns the lastest stable version of the api"}},
)
async def get_version() -> str:
    """
    Controll endpoint that validates the app is alive and return's the desired api version to be used
    """
    return settings.app_version


if settings.debug or settings.app_version == "vNext":
    app.include_router(router_v_next, prefix="/vNext", tags=["vNext"], dependencies=[Depends(get_current_user)])
