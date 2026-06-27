"""Extract AI — FastAPI application entrypoint."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware

# Built frontend is copied here in the production image (see root Dockerfile).
STATIC_DIR = (Path(__file__).resolve().parent.parent / "static").resolve()

configure_logging()

# Interactive API docs and the OpenAPI schema are useful in dev but are an
# information-disclosure surface in production, so disable them there.
_DOCS_ENABLED = settings.ENVIRONMENT != "production"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="AI-Powered Document Intelligence & OCR Platform",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if _DOCS_ENABLED else None,
    docs_url="/docs" if _DOCS_ENABLED else None,
    redoc_url="/redoc" if _DOCS_ENABLED else None,
)

# Middleware order: outermost first. Security headers wrap everything; CORS and
# rate limiting are applied per-request. The limiter is process-global state, so
# we skip it under tests where it would otherwise bleed across cases.
app.add_middleware(SecurityHeadersMiddleware)
if settings.ENVIRONMENT != "test":
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
    def spa(full_path: str):
        # Never resolve API paths through the SPA fallback — return a JSON 404
        # so unmatched API routes don't masquerade as 200/HTML.
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        # Containment check: the resolved target MUST stay inside STATIC_DIR.
        # Without this, "../" traversal would read arbitrary files (CWE-22).
        target = (STATIC_DIR / full_path).resolve()
        if full_path and target.is_file() and target.is_relative_to(STATIC_DIR):
            return FileResponse(target)
        return FileResponse(STATIC_DIR / "index.html")
