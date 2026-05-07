"""
Smoke tests — the floor of the suite.

Purpose
-------
Prove the calculator is *reachable, rendered and minimally interactive*. If
any of these fail, deeper tests are pointless and CI should bail early.

These tests deliberately avoid asserting any business logic that could itself
be defective (operator correctness, scientific functions, etc.). Such
assertions live in the functional / scientific / edge-case suites.
"""

from __future__ import annotations

import pytest

from src.pages.calculator_page import CalculatorPage


pytestmark = pytest.mark.smoke


# ---------------------------------------------------------------------------
# 1. Page reachability & basic rendering
# ---------------------------------------------------------------------------
class TestPageRenders:
    """Can a user actually open the page?"""

    def test_page_title_is_correct(self, calculator_page: CalculatorPage) -> None:
        assert calculator_page.page_title == "Scientific Calculator"

    def test_calculator_container_is_visible(self, calculator_page: CalculatorPage) -> None:
        container = calculator_page.find(CalculatorPage.CALCULATOR_CONTAINER)
        assert container.is_displayed(), "Calculator container is not visible"

    def test_display_field_is_present_and_empty_on_load(
        self, calculator_page: CalculatorPage
    ) -> None:
        assert calculator_page.display_is_empty(), (
            f"Display should be empty on load, " f"got: {calculator_page.read_display()!r}"
        )


# ---------------------------------------------------------------------------
# 2. Required button surface
# ---------------------------------------------------------------------------
EXPECTED_BUTTON_LABELS: frozenset[str] = frozenset(
    # Digits
    [str(d) for d in range(10)]
    # Operators & misc
    + ["+", "−", "×", "÷", "(", ")", ".", "=", "C"]
    # Scientific
    + ["sin", "cos", "tan", "√", "log"]
)


class TestButtonSurface:
    """Every button a user expects must be on the page and clickable."""

    def test_all_required_button_labels_are_rendered(self, calculator_page: CalculatorPage) -> None:
        rendered = set(calculator_page.visible_button_labels())
        missing = EXPECTED_BUTTON_LABELS - rendered
        assert not missing, f"Missing buttons: {sorted(missing)} (rendered: {sorted(rendered)})"

    @pytest.mark.parametrize(
        "label",
        sorted(EXPECTED_BUTTON_LABELS),
        ids=lambda lbl: f"label={lbl!r}",
    )
    def test_button_is_clickable(self, calculator_page: CalculatorPage, label: str) -> None:
        # Navigating to the page already proved presence; here we assert
        # the element is enabled and ready for interaction.
        from selenium.webdriver.common.by import By

        elem = calculator_page.find_clickable(
            (By.XPATH, f"//button[normalize-space(text())='{label}']")
        )
        assert elem.is_enabled(), f"Button {label!r} is not enabled"


# ---------------------------------------------------------------------------
# 3. Happy path — proves end-to-end click -> display chain
# ---------------------------------------------------------------------------
class TestHappyPath:
    """A single trivial calculation that exercises the whole click->display chain.

    Note on chosen operands
    -----------------------
    We use ``7+2`` rather than the more obvious ``2+3`` because manual
    exploration revealed the ``3`` button is wired to append ``'0'`` (see
    the functional suite for the asserted-on, bug-tracked test case). The
    smoke suite must not flag *that* defect — its job is only to prove the
    end-to-end click->display chain works, so we pick digits that do not
    overlap any known defect. If even this trivial path failed, no deeper
    test would be worth running and CI should bail.
    """

    def test_simple_addition_round_trip(self, calculator_page: CalculatorPage) -> None:
        result = calculator_page.evaluate("7+2")
        assert result == "9", f"Expected '9', got {result!r}"
