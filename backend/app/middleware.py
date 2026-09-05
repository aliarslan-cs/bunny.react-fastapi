import json
import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from .logging_config import request_id_ctx
from .telemetry import get_trace_correlation

logger = logging.getLogger("app.access")


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages request correlation IDs, OpenTelemetry headers,
    and structured request logging.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract existing X-Request-ID or generate a new one
        incoming_req_id = request.headers.get("X-Request-ID")
        request_id = incoming_req_id if incoming_req_id else f"req-{uuid.uuid4().hex[:12]}"

        # Set in contextvar for logging
        token = request_id_ctx.set(request_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Attach headers to response
            response.headers["X-Request-ID"] = request_id

            trace_id, _ = get_trace_correlation()
            if trace_id:
                response.headers["X-Trace-ID"] = trace_id

            # Avoid spamming logs with frequent health checks
            if not request.url.path.endswith("/health"):
                logger.info(
                    "%s %s -> %d (%.2f ms)",
                    request.method,
                    request.url.path,
                    response.status_code,
                    duration_ms,
                    extra={
                        "extra_fields": json.dumps({
                            "http_method": request.method,
                            "http_path": request.url.path,
                            "http_status": response.status_code,
                            "duration_ms": round(duration_ms, 2),
                            "client_ip": request.client.host if request.client else "unknown",
                        })
                    },
                )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "Unhandled exception on %s %s after %.2f ms: %s",
                request.method,
                request.url.path,
                duration_ms,
                exc,
                extra={
                    "extra_fields": json.dumps({
                        "http_method": request.method,
                        "http_path": request.url.path,
                        "duration_ms": round(duration_ms, 2),
                    })
                },
            )
            raise
        finally:
            request_id_ctx.reset(token)

