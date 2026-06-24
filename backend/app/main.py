"""Extract AI — FastAPI application entrypoint."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware

# Built frontend is copied here in the production image (see root Dockerfile).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="AI-Powered Document Intelligence & OCR Platform",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware order: outermost first. Security headers wrap everything; CORS and
# rate limiting are applied per-request.
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.ENVIRONMENT}


# ─── Single-origin frontend (production only) ──────────────────────────────
# When a built frontend is present, serve it from the same service: static
# assets by path, with an index.html fallback for client-side routes. The API
# (/api/v1/*), /health, /docs, /redoc and /openapi.json are registered above
# and therefore take precedence over this catch-all. In local dev STATIC_DIR
# does not exist, so this is skipped and the frontend runs on its own server.
if STATIC_DIR.is_dir():

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
