"""
Functional tests — digit composition, decimal handling, clear & error
semantics.

Coverage rationale
------------------
The smoke suite proved every digit *button* is on the page; the
``test_button_label_integrity`` module proved each digit appends its own
label (modulo the known ``3`` defect). This module goes further:

* **Composition** — multi-digit numbers, leading zeros, two-digit operands.
* **Decimal point** — single decimals, leading dot, trailing dot, the
  pathological ``1.2.4`` and ``1..5`` inputs (the page exposes no
  validation on the ``.`` button).
* **Clear** — ``C`` empties the display, repeated clears are idempotent.
* **Error pathway consistency** — the app already has an ``Error`` state for
  syntactically invalid input; this module verifies it is reached
  consistently.

Assertions are again derived from ``math_oracle.expected`` wherever the
input is well-formed, and from explicit literals (``'Error'``, ``''``) where
the expected behaviour is a UI state rather than a number.
"""

from __future__ import annotations

import pytest

from src.pages.calculator_page import CalculatorPage
from src.utils import math_oracle as oracle


pytestmark = [pytest.mark.functional, pytest.mark.regression]


# ===========================================================================
# 1. Digit composition
# ===========================================================================
class TestDigitComposition:
    """Pressing successive digits must produce the natural left-to-right number."""

    @pytest.mark.parametrize(
        "digits",
        ["12", "45", "907", "10000"],
        ids=lambda d: f"digits={d}",
    )
    def test_multi_digit_number_composes_left_to_right(
        self, calculator_page: CalculatorPage, digits: str
    ) -> None:
        """Avoids digit '3' so this passes on a healthy implementation."""
        if "3" in digits:
            pytest.skip("'3' button defect tracked separately; excluded here.")
        calculator_page.click_clear()
        for ch in digits:
            calculator_page.click_digit(int(ch))
        assert calculator_page.read_display() == digits

    def test_single_zero_displays_zero(self, calculator_page: CalculatorPage) -> None:
        calculator_page.click_clear()
        calculator_page.click_digit(0)
        assert calculator_page.read_display() == "0"

    def test_two_digit_operand_arithmetic(self, calculator_page: CalculatorPage) -> None:
        """End-to-end: 12 + 45 = 57 — no '3' or '/' on the path."""
        assert calculator_page.evaluate("12+45") == oracle.expected("12+45")  # '57'


# ===========================================================================
# 2. Decimal point handling
# ===========================================================================
class TestDecimalPoint:
    """Decimal input — including pathological inputs that today succeed silently."""

    @pytest.mark.parametrize(
        "expression",
        ["1.5+2.5", "0.5/0.25", "1.0+1.0", "0.1+0.2"],
        ids=lambda e: f"expr={e}",
    )
    def test_decimal_arithmetic_matches_oracle(
        self, calculator_page: CalculatorPage, expression: str
    ) -> None:
        """Skip cases that depend on the broken division path; covered elsewhere."""
        if "/" in expression:
            pytest.skip("Division operand-swap defect tracked separately.")
        assert calculator_page.evaluate(expression) == oracle.expected(expression)

    def test_leading_dot_decimal_is_accepted(self, calculator_page: CalculatorPage) -> None:
        """``.5 + .5 = 1`` — the lexer/parser accepts a leading dot."""
        assert calculator_page.evaluate(".5+.5") == oracle.expected(".5+.5")  # '1'

    def test_trailing_dot_evaluates_as_integer(self, calculator_page: CalculatorPage) -> None:
        """``5.`` evaluates as ``5`` — acceptable behaviour, asserted to pin it."""
        assert calculator_page.evaluate("5.") == "5"

    # ------------------------------------------------------------------
    # Bug-tracking tests — multi-decimal-point inputs
    # ------------------------------------------------------------------
    @pytest.mark.bug
    def test_multiple_decimal_points_must_be_rejected(
        self, calculator_page: CalculatorPage
    ) -> None:
        """``1.2.4`` is not a valid number; the calculator must surface an
        error rather than silently truncate the trailing fractional digits.

        Defect surfaced: the lexer accepts ``[\\d.]+`` as a single number
        token, so ``1.2.4`` is fed to ``parseFloat`` which silently returns
        ``1.2`` — the user gets a wrong-but-plausible result with no signal
        that part of their input was discarded. Severity: high (silent
        data loss).
        """
        result = calculator_page.evaluate("1.2.4")
        assert result == "Error", (
            f"'1.2.4' must yield 'Error' (or similar non-numeric signal), "
            f"got {result!r} — silent decimal-point truncation."
        )

    @pytest.mark.bug
    def test_consecutive_decimal_points_must_be_rejected(
        self, calculator_page: CalculatorPage
    ) -> None:
        """``1..5`` is malformed; same root cause as above with a worse
        symptom: ``parseFloat('1..5')`` returns ``1`` so the entire
        fractional half is silently dropped.
        """
        result = calculator_page.evaluate("1..5")
        assert result == "Error", (
            f"'1..5' must yield 'Error', got {result!r} — silent truncation "
            "of the second-and-onward fractional digits."
        )


# ===========================================================================
# 3. Clear & error semantics
# ===========================================================================
class TestClearAndErrors:
    """``C`` must reset the display; error pathways must be consistent."""

    def test_clear_empties_a_populated_display(self, calculator_page: CalculatorPage) -> None:
        calculator_page.enter_expression("12+45")
        assert calculator_page.read_display() != ""
        calculator_page.click_clear()
        assert calculator_page.read_display() == ""

    def test_clear_is_idempotent(self, calculator_page: CalculatorPage) -> None:
        calculator_page.click_clear()
        calculator_page.click_clear()
        assert calculator_page.read_display() == ""

    def test_clear_after_result_resets(self, calculator_page: CalculatorPage) -> None:
        """Press '=', see a result, then press 'C' — display empties."""
        calculator_page.evaluate("7+2")
        assert calculator_page.read_display() == "9"
        calculator_page.click_clear()
        assert calculator_page.read_display() == ""

    def test_trailing_operator_yields_error(self, calculator_page: CalculatorPage) -> None:
        """The application's existing 'Error' pathway works for ``1+``."""
        assert calculator_page.evaluate("1+") == "Error"

    # ------------------------------------------------------------------
    # Bug-tracking tests — inconsistent error pathway
    # ------------------------------------------------------------------
    @pytest.mark.bug
    def test_pressing_equals_with_empty_display_must_not_show_undefined(
        self, calculator_page: CalculatorPage
    ) -> None:
        """Pressing ``=`` with nothing entered must NOT leak the JS literal
        ``undefined`` into the display.

        Defect surfaced: ``evaluateExpression`` returns ``undefined`` for
        an empty token list; the assignment ``display.value = undefined``
        coerces to the string ``'undefined'`` and shows it to the user.
        Acceptable behaviours would be: leave the display empty, or show
        ``'Error'`` like other malformed inputs do.
        """
        calculator_page.click_clear()
        calculator_page.click_equals()
        result = calculator_page.read_display()
        assert result in {"", "Error", "0"}, (
            f"Empty input + '=' must leave display empty / 'Error' / '0'; "
            f"got {result!r}. The literal 'undefined' is leaking from JS."
        )

    @pytest.mark.bug
    def test_leading_operator_must_yield_error_consistent_with_trailing(
        self, calculator_page: CalculatorPage
    ) -> None:
        """``+5 =`` must show ``Error`` (same as ``1+`` does), not ``NaN``.

        Defect surfaced: the parser treats a leading binary operator as a
        unary application against an undefined left-hand side, producing
        ``NaN`` which leaks to the UI. The application already has a
        clean ``Error`` state — it should be reached here too for
        consistency.
        """
        calculator_page.click_clear()
        calculator_page.click_operator("+")
        calculator_page.click_digit(5)
        calculator_page.click_equals()
        result = calculator_page.read_display()
        assert result == "Error", (
            f"Leading '+' must yield 'Error' for consistency with the "
            f"trailing-operator path (`1+` -> 'Error'); got {result!r}."
        )


# ===========================================================================
# 4. Robustness — long expressions
# ===========================================================================
class TestRobustness:
    """No crashes / hangs on long but well-formed input."""

    def test_long_chained_addition(self, calculator_page: CalculatorPage) -> None:
        """Twenty consecutive ``+1`` operations must sum to 20."""
        expression = "1" + "+1" * 19
        assert calculator_page.evaluate(expression) == "20"
