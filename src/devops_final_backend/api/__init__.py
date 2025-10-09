from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from devops_final_backend.services.auth.dependencies import get_current_user
from devops_final_backend.settings import settings

from .errors import HANDLERS
from .vNext import router as router_v_next

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/", tags=["Home"])
def index():
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return RedirectResponse("/docs", status.HTTP_302_FOUND)


app.include_router(router_v_next, tags=["vNext"], dependencies=[Depends(get_current_user)])

for error_type, handler in HANDLERS.items():
    app.add_exception_handler(error_type, handler)
