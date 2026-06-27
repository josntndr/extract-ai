"""Security middleware: hardened response headers and a rate limiter."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Allow self-hosted assets + Google Fonts (used by the built frontend). Inline
# styles are permitted because Framer Motion writes element style attributes.
_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'"
)

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": _CSP,
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response


def _client_ip(request: Request) -> str:
    """Best-effort real client IP.

    Behind a reverse proxy (Railway, nginx) request.client.host is the proxy,
    so trust the first hop of X-Forwarded-For. (For untrusted ingress this
    should be tightened to a known proxy allowlist.)
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "anonymous"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP.

    Adds a stricter limit on auth endpoints to blunt credential brute-force,
    and periodically evicts idle buckets so memory stays bounded.

    Single-process only — back this with Redis for a multi-replica deployment.
    """

    def __init__(
        self,
        app,
        max_requests: int = 120,
        window_seconds: int = 60,
        auth_max_requests: int = 10,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self.auth_max = auth_max_requests
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._last_sweep = 0.0

    def _sweep(self, now: float) -> None:
        """Drop buckets whose newest hit has aged out — bounds memory."""
        if now - self._last_sweep < self.window:
            return
        self._last_sweep = now
        cutoff = now - self.window
        for key in [k for k, d in self._hits.items() if not d or d[-1] <= cutoff]:
            del self._hits[key]

    async def dispatch(self, request: Request, call_next) -> Response:
        now = time.monotonic()
        self._sweep(now)

        path = request.url.path
        is_auth = path.startswith("/api/v1/auth/")
        limit = self.auth_max if is_auth else self.max_requests
        # Separate buckets so heavy normal traffic can't mask auth abuse.
        key = f"{'auth' if is_auth else 'gen'}:{_client_ip(request)}"

        hits = self._hits[key]
        while hits and hits[0] <= now - self.window:
            hits.popleft()
        if len(hits) >= limit:
            retry_after = int(self.window - (now - hits[0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(retry_after)},
            )
        hits.append(now)
        return await call_next(request)
