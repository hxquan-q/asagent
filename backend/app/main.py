"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .api.v1 import api_router
from .bootstrap import init_db, seed_admin
from .core.config import settings
from .skills import scan_skills

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("asagent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_runtime_secrets()
    settings.ensure_dirs()
    init_db()
    seed_admin()
    scan_skills(settings.skills_path)
    log.info("asagent ready (sandbox=%s)", settings.SANDBOX_BACKEND)
    yield


app = FastAPI(title="asagent", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):  # noqa: ARG001
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):  # noqa: ARG001
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):  # noqa: ARG001
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "app": settings.APP_NAME}


# ---- optional SPA static hosting (single-port deploy) ----
# Default to <repo>/frontend/dist (relative to this file), overridable via settings.
_default_dist = Path(__file__).resolve().parents[2] / "frontend/dist"
_frontend_dist = Path(settings.FRONTEND_DIST) if settings.FRONTEND_DIST else _default_dist
if _frontend_dist.is_dir():
    _dist_root = _frontend_dist.resolve()

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404, "not found")
        candidate = (_frontend_dist / full_path).resolve()
        try:
            candidate.relative_to(_dist_root)  # block path traversal
        except ValueError:
            raise HTTPException(404, "not found") from None
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_frontend_dist / "index.html")
