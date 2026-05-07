"""
Centralised, environment-driven configuration for the test suite.

Every value can be overridden by an environment variable, which makes the
suite trivially configurable for CI matrices (e.g. run twice, once with
``HEADLESS=true`` and once with ``HEADLESS=false``).

Usage::

    from src.utils.config import settings

    driver.get(settings.base_url)
    driver.implicitly_wait(settings.implicit_wait)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
REPORTS_DIR: Final[Path] = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR: Final[Path] = REPORTS_DIR / "screenshots"


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable in a forgiving way."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Immutable configuration object, populated from environment variables."""

    base_url: str = field(
        default_factory=lambda: os.getenv(
            "BASE_URL",
            "https://rbihubcodechallenge.github.io/calculator/index.html",
        )
    )
    browser: str = field(default_factory=lambda: os.getenv("BROWSER", "chrome").lower())
    headless: bool = field(default_factory=lambda: _env_bool("HEADLESS", True))
    window_width: int = field(default_factory=lambda: _env_int("WINDOW_WIDTH", 1280))
    window_height: int = field(default_factory=lambda: _env_int("WINDOW_HEIGHT", 800))

    implicit_wait: int = field(default_factory=lambda: _env_int("IMPLICIT_WAIT", 0))
    explicit_wait: int = field(default_factory=lambda: _env_int("EXPLICIT_WAIT", 10))
    page_load_timeout: int = field(default_factory=lambda: _env_int("PAGE_LOAD_TIMEOUT", 30))

    screenshot_on_failure: bool = field(
        default_factory=lambda: _env_bool("SCREENSHOT_ON_FAILURE", True)
    )

    def as_dict(self) -> dict[str, object]:
        """Return a dict view (handy for HTML-report metadata)."""
        return {
            "base_url": self.base_url,
            "browser": self.browser,
            "headless": self.headless,
            "window": f"{self.window_width}x{self.window_height}",
            "implicit_wait_s": self.implicit_wait,
            "explicit_wait_s": self.explicit_wait,
            "page_load_timeout_s": self.page_load_timeout,
        }


# Single source of truth, imported wherever needed.
settings: Final[Settings] = Settings()

# Make sure report directories exist on import — pytest-html otherwise fails
# the first time it runs in a clean checkout.
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
