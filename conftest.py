"""
Top-level pytest configuration.

Responsibilities
----------------
1. Make ``src`` importable as a package.
2. Provide the ``driver`` fixture — a Chrome WebDriver with the right options
   for both local-dev and CI (headless), backed by ``webdriver-manager`` so
   no driver binary needs to be hand-installed.
3. On test failure, attach a screenshot to the HTML report and persist it
   under ``reports/screenshots/`` for offline triage.
4. Enrich the HTML report with environment metadata (browser, base URL,
   resolution, headless state).

The actual Page Object fixtures (e.g. ``calculator_page``) are added in the
next commit alongside ``CalculatorPage``.
"""

from __future__ import annotations

import datetime as _dt
import re as _re
import sys
from pathlib import Path
from typing import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------------------------
# 1. Bootstrap import path so tests can do `from src.pages... import ...`
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Imports below intentionally come *after* the sys.path tweak.
from src.pages.calculator_page import CalculatorPage  # noqa: E402
from src.utils.config import SCREENSHOTS_DIR, settings  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# 2. WebDriver factory & fixture
# ---------------------------------------------------------------------------
def _build_chrome_options() -> ChromeOptions:
    """Compose Chrome options that work both locally and in CI."""
    opts = ChromeOptions()

    if settings.headless:
        # The "new" headless mode is a real Chrome process — required for
        # JavaScript-heavy pages and for accurate viewport rendering in CI.
        opts.add_argument("--headless=new")

    # CI hardening (necessary on GitHub Actions / containerised runners,
    # harmless locally).
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument(f"--window-size={settings.window_width},{settings.window_height}")

    # Reduce noise & speed up cold starts.
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-notifications")
    opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    return opts


@pytest.fixture(scope="function")
def driver() -> Generator[WebDriver, None, None]:
    """Function-scoped WebDriver — fresh browser per test for isolation."""
    log.info(
        "Launching %s (headless=%s, %dx%d)",
        settings.browser,
        settings.headless,
        settings.window_width,
        settings.window_height,
    )

    if settings.browser != "chrome":
        pytest.skip(f"Browser '{settings.browser}' is not supported by this suite (Chrome only).")

    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=_build_chrome_options())
    drv.set_page_load_timeout(settings.page_load_timeout)
    if settings.implicit_wait:
        drv.implicitly_wait(settings.implicit_wait)

    try:
        yield drv
    finally:
        log.info("Quitting WebDriver")
        drv.quit()


# ---------------------------------------------------------------------------
# 3. Page Object fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def calculator_page(driver: WebDriver) -> CalculatorPage:
    """Return a freshly-loaded ``CalculatorPage`` ready for interaction."""
    return CalculatorPage(driver).load()


# ---------------------------------------------------------------------------
# 4. Screenshot-on-failure + HTML report attachment
# ---------------------------------------------------------------------------
# Filename whitelist: actions/upload-artifact@v4 rejects paths containing any
# of  <  >  :  "  /  \  |  ?  *  and additionally chokes on  (  )  [  ]  in
# practice (Windows-compatible naming rules). pytest's parametrised IDs
# routinely contain `[` `]` `(` `)` `*` `+` so we *must* sanitise before
# touching the filesystem.
_FILENAME_SAFE_RE = _re.compile(r"[^A-Za-z0-9._-]+")


def _safe_filename(raw: str, *, max_len: int = 120) -> str:
    """Convert any pytest item name into a portable, artifact-uploadable
    filename. Strips runs of unsafe characters down to a single underscore."""
    cleaned = _FILENAME_SAFE_RE.sub("_", raw).strip("._")
    return cleaned[:max_len] or "test"


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Capture a screenshot when a test fails *unexpectedly* (i.e. not
    because of a known-defect xfail)."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or report.passed:
        return
    # Don't waste disk / artifact-bandwidth on xfail outcomes — they are
    # *expected* failures already documented in bug-reports/. Only capture
    # screenshots for genuinely-unexpected failures and errors.
    if getattr(report, "wasxfail", False):
        return
    if not settings.screenshot_on_failure:
        return

    drv: WebDriver | None = item.funcargs.get("driver")
    if drv is None:
        return

    timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = _safe_filename(item.name)
    screenshot_path = SCREENSHOTS_DIR / f"{safe_name}_{timestamp}.png"

    try:
        drv.save_screenshot(str(screenshot_path))
        log.warning("Saved failure screenshot: %s", screenshot_path)
    except Exception as exc:  # pragma: no cover - best-effort diagnostic
        log.warning("Could not save screenshot: %s", exc)
        return

    # Attach into pytest-html if present.
    extras = getattr(report, "extras", [])
    try:
        from pytest_html import extras as html_extras  # type: ignore[import-not-found]

        relative = screenshot_path.relative_to(_PROJECT_ROOT / "reports")
        extras.append(html_extras.image(str(relative)))
        report.extras = extras
    except Exception:  # pragma: no cover - pytest-html not installed in CI minimal mode
        pass


# ---------------------------------------------------------------------------
# 5. Enrich HTML report metadata
# ---------------------------------------------------------------------------
def pytest_metadata(metadata: dict) -> None:
    """Hook from ``pytest-metadata`` — adds env info to the HTML report."""
    metadata.update({f"Calc/{k}": v for k, v in settings.as_dict().items()})
