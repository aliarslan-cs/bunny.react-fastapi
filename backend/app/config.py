from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./bunny.db"
    jwt_secret: str = "local-development-secret"
    cors_origins: str = "http://localhost:5173"
    cold_start: bool = True

    # Observability & OpenTelemetry settings
    service_name: str = "bunny-api"
    service_version: str = "0.1.0"
    environment: str = "development"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_enabled: bool = True
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "console"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()