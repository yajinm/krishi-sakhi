"""
Configuration management for Krishi Sakhi backend.

Uses Pydantic Settings for type-safe configuration with environment variable support.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = Field(default="Krishi Sakhi", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    timezone: str = Field(default="Asia/Kolkata", env="TIMEZONE")

    # Database
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="krishi_sakhi", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Assemble database URL from components if not provided."""
        if isinstance(v, str):
            return v
        return (
            f"postgresql+asyncpg://{values.get('postgres_user')}:"
            f"{values.get('postgres_password')}@{values.get('postgres_host')}:"
            f"{values.get('postgres_port')}/{values.get('postgres_db')}"
        )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_cache_url: str = Field(default="redis://localhost:6379/1", env="REDIS_CACHE_URL")

    # JWT
    jwt_private_key_path: str = Field(default="./keys/private.pem", env="JWT_PRIVATE_KEY_PATH")
    jwt_public_key_path: str = Field(default="./keys/public.pem", env="JWT_PUBLIC_KEY_PATH")
    jwt_algorithm: str = Field(default="RS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # OTP
    otp_dev_code: str = Field(default="000000", env="OTP_DEV_CODE")
    otp_expire_minutes: int = Field(default=5, env="OTP_EXPIRE_MINUTES")
    otp_max_attempts: int = Field(default=3, env="OTP_MAX_ATTEMPTS")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")

    # External Services
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    fcm_server_key: Optional[str] = Field(default=None, env="FCM_SERVER_KEY")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # Provider Configuration
    asr_provider: str = Field(default="dummy", env="ASR_PROVIDER")
    tts_provider: str = Field(default="dummy", env="TTS_PROVIDER")
    weather_provider: str = Field(default="openweather", env="WEATHER_PROVIDER")
    embed_model_name: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2", env="EMBED_MODEL_NAME"
    )
    llm_provider: str = Field(default="local", env="LLM_PROVIDER")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")

    # Azure
    azure_speech_key: Optional[str] = Field(default=None, env="AZURE_SPEECH_KEY")
    azure_speech_region: Optional[str] = Field(default=None, env="AZURE_SPEECH_REGION")

    # Google
    google_application_credentials: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )

    # File Storage
    media_root: str = Field(default="./media", env="MEDIA_ROOT")
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    allowed_audio_formats: List[str] = Field(default=["wav", "mp3", "m4a"], env="ALLOWED_AUDIO_FORMATS")
    allowed_image_formats: List[str] = Field(default=["jpg", "jpeg", "png"], env="ALLOWED_IMAGE_FORMATS")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/2", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/3", env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    celery_accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    celery_timezone: str = Field(default="Asia/Kolkata", env="CELERY_TIMEZONE")

    # OpenTelemetry
    otel_exporter_otlp_endpoint: Optional[str] = Field(
        default=None, env="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    otel_service_name: str = Field(default="krishi-sakhi-api", env="OTEL_SERVICE_NAME")
    otel_service_version: str = Field(default="1.0.0", env="OTEL_SERVICE_VERSION")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")

    # Advisory
    advisory_batch_size: int = Field(default=100, env="ADVISORY_BATCH_SIZE")
    advisory_check_interval_minutes: int = Field(default=30, env="ADVISORY_CHECK_INTERVAL_MINUTES")

    # Knowledge Base
    kb_chunk_size: int = Field(default=500, env="KB_CHUNK_SIZE")
    kb_chunk_overlap: int = Field(default=50, env="KB_CHUNK_OVERLAP")
    kb_embedding_dimension: int = Field(default=384, env="KB_EMBEDDING_DIMENSION")

    # Notifications
    notification_batch_size: int = Field(default=50, env="NOTIFICATION_BATCH_SIZE")
    notification_retry_attempts: int = Field(default=3, env="NOTIFICATION_RETRY_ATTEMPTS")
    notification_retry_delay_seconds: int = Field(default=60, env="NOTIFICATION_RETRY_DELAY_SECONDS")

    # Privacy
    data_retention_days: int = Field(default=2555, env="DATA_RETENTION_DAYS")  # 7 years
    audit_log_retention_days: int = Field(default=365, env="AUDIT_LOG_RETENTION_DAYS")
    consent_required: bool = Field(default=True, env="CONSENT_REQUIRED")

    # Development
    dev_mode: bool = Field(default=False, env="DEV_MODE")
    mock_external_services: bool = Field(default=True, env="MOCK_EXTERNAL_SERVICES")
    enable_swagger_ui: bool = Field(default=True, env="ENABLE_SWAGGER_UI")
    enable_redoc: bool = Field(default=True, env="ENABLE_REDOC")

    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    health_check_interval_seconds: int = Field(default=30, env="HEALTH_CHECK_INTERVAL_SECONDS")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"], env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], env="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # WebSocket
    ws_heartbeat_interval: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    ws_max_connections: int = Field(default=1000, env="WS_MAX_CONNECTIONS")

    # Backup
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2 AM
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("allowed_audio_formats", pre=True)
    def parse_audio_formats(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse audio formats from string or list."""
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(",")]
        return v

    @validator("allowed_image_formats", pre=True)
    def parse_image_formats(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse image formats from string or list."""
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(",")]
        return v

    @validator("celery_accept_content", pre=True)
    def parse_celery_content(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse Celery accept content from string or list."""
        if isinstance(v, str):
            return [content.strip() for content in v.split(",")]
        return v

    @validator("cors_allow_methods", pre=True)
    def parse_cors_methods(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @validator("cors_allow_headers", pre=True)
    def parse_cors_headers(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @property
    def media_path(self) -> Path:
        """Get media directory path."""
        return Path(self.media_root)

    @property
    def keys_path(self) -> Path:
        """Get keys directory path."""
        return Path("./keys")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.dev_mode

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
