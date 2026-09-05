import logging
from typing import Optional, Tuple
from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import settings

logger = logging.getLogger(__name__)


def get_trace_correlation() -> Tuple[Optional[str], Optional[str]]:
    """Return active (trace_id, span_id) hex strings if an active span exists."""
    span = trace.get_current_span()
    ctx = span.get_span_context() if span else None
    if ctx and ctx.is_valid:
        return f"{ctx.trace_id:032x}", f"{ctx.span_id:016x}"
    return None, None


def setup_telemetry(app: FastAPI, engine) -> None:
    """Initialize OpenTelemetry TracerProvider, MeterProvider, LoggerProvider, and auto-instrumentations."""
    if not settings.otel_enabled:
        logger.info("OpenTelemetry is disabled via settings.")
        return

    try:
        resource = Resource.create(
            {
                SERVICE_NAME: settings.service_name,
                SERVICE_VERSION: settings.service_version,
                DEPLOYMENT_ENVIRONMENT: settings.environment,
            }
        )

        # 1. Traces
        tracer_provider = TracerProvider(resource=resource)
        span_exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
        trace.set_tracer_provider(tracer_provider)

        # 2. Metrics
        metric_exporter = OTLPMetricExporter(
            endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
        )
        metric_reader = PeriodicExportingMetricReader(
            metric_exporter, export_interval_millis=10000
        )
        meter_provider = MeterProvider(
            metric_readers=[metric_reader], resource=resource
        )
        metrics.set_meter_provider(meter_provider)

        # 3. OTLP Logs
        try:
            from opentelemetry._logs import set_logger_provider
            from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
            from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
            from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

            logger_provider = LoggerProvider(resource=resource)
            log_exporter = OTLPLogExporter(
                endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
            )
            logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
            set_logger_provider(logger_provider)

            otlp_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
            logging.getLogger().addHandler(otlp_handler)
        except Exception as log_err:
            logger.debug("OTLP log handler setup skipped: %s", log_err)

        # 4. Auto-instrument FastAPI
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            excluded_urls="health,redoc,docs,openapi.json",
        )

        # 5. Auto-instrument SQLAlchemy
        if engine is not None:
            SQLAlchemyInstrumentor().instrument(
                engine=engine, tracer_provider=tracer_provider
            )

        logger.info(
            "OpenTelemetry initialized for %s -> %s",
            settings.service_name,
            settings.otel_exporter_otlp_endpoint,
        )
    except Exception as exc:
        logger.warning("Failed to initialize OpenTelemetry: %s", exc)

