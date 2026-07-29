"""Application configuration loaded from YAML + environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


def _load_yaml_config() -> dict[str, Any]:
    """Load config.yaml from project root."""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


class DiscordConfig(BaseSettings):
    tokens: list[str] = [""]
    guild_id: str = ""
    owner_role: str = ""
    member_role: str = ""
    role_id: str = ""
    welcome_channel: str = ""
    leaderboard_channel: str = ""
    log_channel: str = ""
    notifier_channel: str = ""
    transcript_channel: str = ""
    ticket_category: str = ""
    notifier_webhook: str = ""
    webhook_url: str = ""


class LicenseConfig(BaseSettings):
    trial_duration: str = "8h"
    jwt_secret: str = ""
    auth_key: str = ""
    captcha_key: str = ""


class RateLimitConfig(BaseSettings):
    default: int = 30
    window: int = 60


class APIConfig(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"
    workers: int = 3
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)


class SMTPConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 25


class DatabaseConfig(BaseSettings):
    url: str = "postgresql+asyncpg://autosecure:aUt0S3cur3DB!2026@localhost:5432/autosecure"
    pool_size: int = 20
    max_overflow: int = 10
    echo: bool = False


class RedisConfig(BaseSettings):
    url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300


class SecurityConfig(BaseSettings):
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_expiry: int = 900  # 15 minutes
    jwt_refresh_expiry: int = 604800  # 7 days
    session_secret: str = ""


class HcaptchaConfig(BaseSettings):
    site_key: str = ""
    secret_key: str = ""
    verify_url: str = "https://api.hcaptcha.com/siteverify"
    enabled: bool = True


class SecurityDetectorConfig(BaseSettings):
    rate_limit_per_minute: int = 100
    rate_limit_block_minutes: int = 15
    login_burst_max: int = 5
    login_burst_window_minutes: int = 10
    login_burst_block_minutes: int = 30
    bot_block_minutes: int = 30
    session_hijack_window_seconds: int = 300


class MicrosoftConfig(BaseSettings):
    auth_url: str = "https://login.live.com/ppsecure/post.srf"
    redirect_uri: str = "https://www.xbox.com/auth/msa/blank.html"


class APIsConfig(BaseSettings):
    donutsmp: str = "https://api.donutsmp.net"
    mctiers: str = "https://mctiers.com/api"
    hypixel: str = "https://api.hypixel.net"
    mc_head: str = "https://mc-heads.net"
    visage: str = "https://visage.surgeplay.com"
    hypixel_api_key: str = ""


class HTTPConfig(BaseSettings):
    timeout: int = 10
    max_retries: int = 3
    user_agents: list[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    ]


class TaskConfig(BaseSettings):
    license_check: int = 10000
    invoice_check: int = 60000
    leaderboard_update: int = 300000
    quarantine_check: int = 60000
    quarantine_expiry: int = 86400000
    notification_poll: int = 30000
    role_sync: int = 1800000
    autoclean: int = 3600000


class EmailConfig(BaseSettings):
    code_length: list[int] = [6, 7]
    poll_interval: int = 1000
    watch_timeout: int = 30000
    max_checks: int = 10
    blocked_emails: list[str] = []
    ignore_emails: list[str] = []


class UIConfig(BaseSettings):
    default_pfp: str = ""
    thumbnail_url: str = ""
    banner_url: str = ""
    footer_text: str = "AutoSecure"
    footer_icon: str = ""


class LoggingConfig(BaseSettings):
    level: str = "INFO"
    json_format: bool = True
    file: str = "logs/autosecure.log"


class Settings(BaseSettings):
    """Root application settings."""

    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    owners: list[str] = []
    domains: list[str] = ["autosecure.me"]
    domain: str = "autosecure.me"
    license: LicenseConfig = Field(default_factory=LicenseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    hcaptcha: HcaptchaConfig = Field(default_factory=HcaptchaConfig)
    security_detector: SecurityDetectorConfig = Field(default_factory=SecurityDetectorConfig)
    microsoft: MicrosoftConfig = Field(default_factory=MicrosoftConfig)
    apis: APIsConfig = Field(default_factory=APIsConfig)
    http: HTTPConfig = Field(default_factory=HTTPConfig)
    tasks: TaskConfig = Field(default_factory=TaskConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = {"env_prefix": "AUTOSECURE_", "env_nested_delimiter": "__"}


def load_settings() -> Settings:
    """Load settings from YAML config with environment variable overrides."""
    yaml_data = _load_yaml_config()
    return Settings(**yaml_data)


settings = load_settings()
