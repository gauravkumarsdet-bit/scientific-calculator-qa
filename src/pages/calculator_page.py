"""
Page Object for the Scientific Calculator.

Locator strategy
----------------
The application under test (https://rbihubcodechallenge.github.io/calculator/)
exposes:

* a single ``<input id="display">`` field;
* 23 ``<button>`` elements identified only by their visible glyph
  (``7``, ``8``, ``+``, ``−``, ``sin``, ``√`` …) — there are **no**
  ``id``, ``name`` or ``data-*`` attributes on any button.

We therefore locate buttons by their *visible text* using XPath. This mirrors
how a real user identifies them and — crucially — guarantees we exercise the
button **as displayed**, not as wired internally. That distinction matters
for this app because several handlers do not match their label (a property
the test suite is expected to surface).

The page object stays a *thin* facade: it knows how to drive the UI, not what
the UI is supposed to compute. Math oracles live in ``src/utils`` so tests
remain framework-agnostic and the page object stays reusable.
"""

from __future__ import annotations

from typing import Final

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.base_page import BasePage, Locator
from src.utils.config import settings


def _btn_xpath(label: str) -> str:
    """Build an XPath that matches a ``<button>`` by trimmed visible text."""
    return f"//button[normalize-space(text())='{label}']"


class CalculatorPage(BasePage):
    """Selenium-backed Page Object for the Scientific Calculator."""

    URL: Final[str] = settings.base_url

    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    DISPLAY: Final[Locator] = (By.ID, "display")
    CALCULATOR_CONTAINER: Final[Locator] = (By.CSS_SELECTOR, ".calculator")
    ALL_BUTTONS: Final[Locator] = (By.CSS_SELECTOR, ".buttons button")

    # Digits 0-9 keyed by their visible glyph (which is what users press).
    DIGIT_LABELS: Final[tuple[str, ...]] = tuple(str(d) for d in range(10))

    # Visible operator glyphs — note these are the *displayed* characters
    # (e.g. unicode minus '−', not ASCII '-'). Tests should always work in
    # terms of what the user sees.
    OPERATOR_LABELS: Final[dict[str, str]] = {
        "+": "+",
        "-": "−",  # U+2212 MINUS SIGN — what the button actually shows
        "*": "×",  # U+00D7 MULTIPLICATION SIGN
        "/": "÷",  # U+00F7 DIVISION SIGN
    }

    FUNCTION_LABELS: Final[tuple[str, ...]] = ("sin", "cos", "tan", "√", "log")

    DECIMAL_LABEL: Final[str] = "."
    EQUALS_LABEL: Final[str] = "="
    CLEAR_LABEL: Final[str] = "C"
    OPEN_PAREN_LABEL: Final[str] = "("
    CLOSE_PAREN_LABEL: Final[str] = ")"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def load(self) -> "CalculatorPage":
        """Navigate to the calculator and wait for it to be interactive."""
        self.open(self.URL)
        self.wait_until_loaded()
        return self

    def wait_until_loaded(self) -> None:
        """Block until the display and at least one digit button are ready."""
        WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(self.DISPLAY)
        )
        WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((By.XPATH, _btn_xpath("0")))
        )

    def is_loaded(self) -> bool:
        return self.is_present(self.DISPLAY) and self.is_present(self.ALL_BUTTONS)

    # ------------------------------------------------------------------
    # Atomic button actions
    # ------------------------------------------------------------------
    def _click_button(self, label: str) -> None:
        self.log.debug("Press button: %s", label)
        self.click((By.XPATH, _btn_xpath(label)))

    def click_digit(self, digit: int | str) -> "CalculatorPage":
        d = str(digit)
        if d not in self.DIGIT_LABELS:
            raise ValueError(f"Not a digit: {digit!r}")
        self._click_button(d)
        return self

    def click_operator(self, op: str) -> "CalculatorPage":
        """Click an operator using its ASCII alias (``+ - * /``)."""
        if op not in self.OPERATOR_LABELS:
            raise ValueError(f"Unsupported operator: {op!r} (valid: + - * /)")
        self._click_button(self.OPERATOR_LABELS[op])
        return self

    def click_function(self, name: str) -> "CalculatorPage":
        """Click a scientific function by name: sin, cos, tan, sqrt/√, log."""
        normalised = "√" if name.lower() in {"sqrt", "√"} else name.lower()
        if normalised not in self.FUNCTION_LABELS:
            raise ValueError(f"Unknown function: {name!r}")
        self._click_button(normalised)
        return self

    def click_decimal(self) -> "CalculatorPage":
        self._click_button(self.DECIMAL_LABEL)
        return self

    def click_equals(self) -> "CalculatorPage":
        self._click_button(self.EQUALS_LABEL)
        return self

    def click_clear(self) -> "CalculatorPage":
        self._click_button(self.CLEAR_LABEL)
        return self

    def click_open_paren(self) -> "CalculatorPage":
        self._click_button(self.OPEN_PAREN_LABEL)
        return self

    def click_close_paren(self) -> "CalculatorPage":
        self._click_button(self.CLOSE_PAREN_LABEL)
        return self

    # ------------------------------------------------------------------
    # High-level helpers (compose atomic actions)
    # ------------------------------------------------------------------
    def enter_expression(self, expression: str) -> "CalculatorPage":
        """Click each character of ``expression`` in order, as a real user would.

        Supported characters:
          * digits 0-9
          * operators + - * /  (ASCII; mapped to the displayed glyphs)
          * parentheses ( )
          * decimal point .
          * whitespace (ignored)

        Anything else raises ``ValueError`` so test authors notice typos
        rather than silently get wrong results.
        """
        for ch in expression:
            if ch.isspace():
                continue
            if ch in self.DIGIT_LABELS:
                self.click_digit(ch)
            elif ch in self.OPERATOR_LABELS:
                self.click_operator(ch)
            elif ch == self.DECIMAL_LABEL:
                self.click_decimal()
            elif ch == self.OPEN_PAREN_LABEL:
                self.click_open_paren()
            elif ch == self.CLOSE_PAREN_LABEL:
                self.click_close_paren()
            else:
                raise ValueError(
                    f"Unsupported character {ch!r} in expression {expression!r}. "
                    f"Use digits, + - * /, parentheses, or '.'."
                )
        return self

    def evaluate(self, expression: str) -> str:
        """Convenience: clear, type, press '=' and return the displayed result."""
        self.click_clear()
        self.enter_expression(expression)
        self.click_equals()
        return self.read_display()

    def apply_function(self, name: str, value: float | int | str) -> str:
        """Type ``value`` then click the named scientific function; return display."""
        self.click_clear()
        self.enter_expression(str(value))
        self.click_function(name)
        return self.read_display()

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------
    def read_display(self) -> str:
        """Return the current value shown on the display."""
        return self.find(self.DISPLAY).get_attribute("value") or ""

    def display_is_empty(self) -> bool:
        return self.read_display() == ""

    def wait_for_display_value(self, expected: str, *, timeout: int | None = None) -> None:
        """Block until ``display.value == expected`` (raises on timeout)."""
        WebDriverWait(self.driver, timeout or self.timeout).until(
            lambda _: self.read_display() == expected,
            message=f"Display never became {expected!r} (last seen: {self.read_display()!r})",
        )

    # ------------------------------------------------------------------
    # Introspection (used by smoke tests)
    # ------------------------------------------------------------------
    def visible_button_labels(self) -> list[str]:
        """Return the trimmed visible text of every calculator button."""
        return [b.text.strip() for b in self.find_all(self.ALL_BUTTONS)]

    def display_is_disabled(self) -> bool:
        """True if the display ``<input>`` is rendered as disabled."""
        el = self.find(self.DISPLAY)
        return el.get_attribute("disabled") is not None

    # ------------------------------------------------------------------
    # Test-only input bypass
    # ------------------------------------------------------------------
    def set_display_value(self, value: str) -> "CalculatorPage":
        """Set the display value directly via JavaScript.

        **Use sparingly.** This bypasses the digit / decimal / parenthesis
        button paths and exists only so a function-under-test (sin, cos,
        tan, sqrt, log) can be exercised in isolation when the *input*
        path itself contains known defects (e.g. BUG-002 — the '3' button
        appends '0', so any test that needs '3' on the display would
        otherwise be tracking the input bug, not the function bug).
        """
        self.driver.execute_script(
            "document.getElementById('display').value = arguments[0];", str(value)
        )
        return self
