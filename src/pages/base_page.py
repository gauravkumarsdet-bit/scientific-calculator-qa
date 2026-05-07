"""
Abstract base class for all Page Objects.

Goals
-----
* Centralise Selenium boilerplate (explicit waits, navigation, screenshots)
  so feature pages stay short and intention-revealing.
* Force every interaction to go through an explicit wait — implicit waits are
  intentionally *off* in our config (see ``src/utils/config.py``) because
  mixing them with explicit waits leads to non-deterministic timeouts.
* Be framework-friendly: nothing here knows about the calculator. This class
  can be reused unchanged when the suite is later extended to other pages.
"""

from __future__ import annotations

from typing import Tuple

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.config import settings
from src.utils.logger import get_logger

# A locator is a (By, value) tuple — Selenium's idiomatic shape.
Locator = Tuple[str, str]


class BasePage:
    """Common building blocks shared by every Page Object."""

    def __init__(self, driver: WebDriver, *, default_timeout: int | None = None) -> None:
        self.driver = driver
        self.timeout = default_timeout if default_timeout is not None else settings.explicit_wait
        self.log = get_logger(self.__class__.__name__)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def open(self, url: str) -> None:
        """Navigate to ``url`` and wait for the document to be ready."""
        self.log.info("GET %s", url)
        self.driver.get(url)
        self._wait_for_document_ready()

    def _wait_for_document_ready(self) -> None:
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    # ------------------------------------------------------------------
    # Element lookup with explicit waits
    # ------------------------------------------------------------------
    def find(self, locator: Locator, *, timeout: int | None = None) -> WebElement:
        """Return the first element matching ``locator`` once it is present in DOM."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator: Locator, *, timeout: int | None = None) -> WebElement:
        """Return the element once it is both visible and enabled."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    def find_all(self, locator: Locator, *, timeout: int | None = None) -> list[WebElement]:
        """Return all elements matching ``locator`` (waits for at least one)."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))

    def is_present(self, locator: Locator, *, timeout: int = 1) -> bool:
        """Best-effort presence check that never raises."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def click(self, locator: Locator, *, timeout: int | None = None) -> None:
        """Wait for clickability, then click."""
        self.find_clickable(locator, timeout=timeout).click()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def take_screenshot(self, path: str) -> None:
        """Save a PNG screenshot to ``path`` (best-effort, never raises)."""
        try:
            self.driver.save_screenshot(path)
        except Exception as exc:  # pragma: no cover - diagnostic helper
            self.log.warning("Could not save screenshot to %s: %s", path, exc)

    @property
    def page_title(self) -> str:
        return self.driver.title

    @property
    def current_url(self) -> str:
        return self.driver.current_url
