import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from .config import settings
from .telemetry import get_trace_correlation

# Shared ContextVar for request-level correlation
from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id_ctx", default="")


class StructuredJsonFormatter(logging.Formatter):
    """Outputs log records formatted as single-line JSON with OpenTelemetry trace correlation."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service_name": settings.service_name,
            "environment": settings.environment,
        }

        # Inject request_id if present in context
        req_id = request_id_ctx.get()
        if req_id:
            log_data["request_id"] = req_id

        # Inject trace_id and span_id from active OpenTelemetry span
        trace_id, span_id = get_trace_correlation()
        if trace_id:
            log_data["trace_id"] = trace_id
            log_data["span_id"] = span_id

        # Attach exception details if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Decode structured fields because OTEL attributes only support scalar values.
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, str):
            try:
                extra_fields = json.loads(extra_fields)
            except json.JSONDecodeError:
                extra_fields = None

        if isinstance(extra_fields, dict):
            # Mask sensitive keys
            masked = {}
            for k, v in extra_fields.items():
                if any(sens in k.lower() for sens in ("password", "secret", "token", "auth")):
                    masked[k] = "***"
                else:
                    masked[k] = v
            log_data["extra"] = masked

        return json.dumps(log_data)


def setup_logging() -> None:
    """Configures the root logging subsystem for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing default handlers to prevent duplicate lines
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    if settings.log_format.lower() == "console" and settings.environment == "development":
        stream_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    else:
        stream_handler.setFormatter(StructuredJsonFormatter())

    root_logger.addHandler(stream_handler)

    # Quiet down overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

