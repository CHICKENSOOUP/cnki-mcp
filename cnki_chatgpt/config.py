from __future__ import annotations

import os
from dataclasses import dataclass


def _csv(name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(name, default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    value = int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _url(name: str) -> str | None:
    value = os.getenv(name, "").strip().rstrip("/")
    if not value:
        return None
    if not value.startswith(("https://", "http://localhost", "http://127.0.0.1")):
        raise ValueError(f"{name} must be HTTPS in production (localhost HTTP is allowed for development)")
    return value


@dataclass(frozen=True)
class Settings:
    cnki_bin: str = os.getenv("CNKI_BIN", "/usr/local/bin/cnki")
    timeout_seconds: int = _positive_int("CNKI_TIMEOUT_SECONDS", 90)
    max_results: int = _positive_int("CNKI_MAX_RESULTS", 100)
    max_concurrency: int = _positive_int("CNKI_MAX_CONCURRENCY", 2)
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = _positive_int("PORT", 8000)
    allowed_hosts: tuple[str, ...] = _csv(
        "MCP_ALLOWED_HOSTS", "localhost:*,127.0.0.1:*,[::1]:*"
    )
    allowed_origins: tuple[str, ...] = _csv(
        "MCP_ALLOWED_ORIGINS", "http://localhost:*,http://127.0.0.1:*,http://[::1]:*"
    )
    public_base_url: str | None = _url("PUBLIC_BASE_URL")
    publisher_name: str = os.getenv("PUBLISHER_NAME", "CNKI Scholar contributors").strip() or "CNKI Scholar contributors"
    support_email: str = os.getenv("SUPPORT_EMAIL", "").strip()
    openai_apps_challenge: str = os.getenv("OPENAI_APPS_CHALLENGE", "").strip()


settings = Settings()
