# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Single-image production build for Railway (and any Docker host):
#   stage 1 builds the React/Vite frontend,
#   stage 2 runs the FastAPI backend AND serves that frontend from one origin.
# The backend serves the SPA + /api/v1 together, so there is no CORS or
# build-time API-URL coordination — the frontend calls a relative /api/v1.
# ─────────────────────────────────────────────────────────────────────────────

FROM node:20-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Relative API base → same-origin requests once served by the backend.
ENV VITE_API_URL=/api/v1
RUN npm run build          # → /web/dist

FROM python:3.12-slim AS app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# tesseract = OCR fallback; libgl/glib = OpenCV (EasyOCR) runtime deps.
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend/ .
# Bake the built frontend in; main.py serves it when ./static exists.
COPY --from=web /web/dist ./static

# Resilient boot: retry migrations (DB warmup), then serve on $PORT.
CMD ["sh", "start.sh"]
