"""Configuration management for AIConexus"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Main application settings"""

    # Application
    app_name: str = "AIConexus"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False

    # Database
    database_url: str = "postgresql://aiconexus:aiconexus@localhost:5432/aiconexus"
    database_echo: bool = False
    database_pool_size: int = 20
    database_pool_pre_ping: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # Registry
    registry_heartbeat_interval_ms: int = 30000
    registry_heartbeat_timeout_ms: int = 60000
    registry_max_agents: int = 1000000

    # Execution
    execution_timeout_ms: int = 5000
    execution_max_retries: int = 3
    execution_retry_backoff_factor: float = 2.0

    # Economics
    currency_default: str = "AIC"
    transaction_settlement_batch_size: int = 100
    transaction_settlement_interval_seconds: int = 60

    # Monitoring
    metrics_enabled: bool = True
    tracing_enabled: bool = False
    tracing_endpoint: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience access
settings = get_settings()
