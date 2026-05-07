"""
Functional tests — button label vs. handler integrity.

Each test in this module proves a specific UI button performs the action
its visible label promises. This is *exactly* where label/handler
mismatches surface and where the suite earns its keep on this assessment.

Each ``test_*`` here is intentionally *one assertion = one bug*. That makes
the pytest report itself a defect inventory:

    FAILED tests/functional/test_button_label_integrity.py::test_minus_button_subtracts
    FAILED tests/functional/test_button_label_integrity.py::test_digit_three_button_inserts_three
    FAILED tests/functional/test_button_label_integrity.py::test_division_uses_correct_operand_order
    ...

Each failure maps 1:1 to a Markdown bug report under ``bug-reports/``.

Bug-tracking note
-----------------
These tests are deliberately *not* marked ``xfail`` in the initial commit so
the reviewer can see the failures themselves and judge severity. Step 12
introduces strict-xfail markers tied to bug-report IDs, which both keeps
green CI sustainable and auto-detects a regression-toward-fix.
"""

from __future__ import annotations

import pytest

from src.pages.calculator_page import CalculatorPage


pytestmark = [pytest.mark.functional, pytest.mark.bug, pytest.mark.regression]


# ---------------------------------------------------------------------------
# Digit buttons — visible label MUST equal what is appended to the display
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "digit",
    [
        pytest.param(
            d,
            marks=(
                pytest.mark.xfail(
                    strict=True,
                    reason="BUG-002: digit '3' button is wired to append('0').",
                )
                if d == 3
                else ()
            ),
        )
        for d in range(10)
    ],
    ids=lambda d: f"digit={d}",
)
def test_digit_button_inserts_its_own_label(calculator_page: CalculatorPage, digit: int) -> None:
    """Pressing the digit ``N`` button must append exactly the character
    ``N`` to the display — never anything else.

    Defect surfaced: the ``3`` button is wired to ``append('0')`` in
    ``index.html``, so pressing ``3`` shows ``'0'``. Every other digit is
    wired correctly. Parametrising over all 10 digits keeps the *shape* of
    the assertion uniform and makes the misbehaving digit obvious in the
    test report.
    """
    calculator_page.click_clear()
    calculator_page.click_digit(digit)
    actual = calculator_page.read_display()
    assert actual == str(
        digit
    ), f"Pressing button '{digit}' should display '{digit}', got {actual!r}"


# ---------------------------------------------------------------------------
# The minus ('−') button MUST perform subtraction, not division
# ---------------------------------------------------------------------------
@pytest.mark.xfail(
    strict=True,
    reason="BUG-001: minus button's onclick handler is append('/'), so "
    "it performs division instead of subtraction.",
)
def test_minus_button_subtracts(calculator_page: CalculatorPage) -> None:
    """Pressing ``9 − 4 =`` must display ``5``.

    Defect surfaced: the minus button's onclick handler is
    ``append('/')`` rather than ``append('-')``, so the displayed glyph
    ``−`` actually performs division. ``9 − 4 =`` therefore yields
    ``9/4 = 2.25`` (operand-swap bug compounded with this one means the
    actual displayed value is ``4/9`` ≈ ``0.4444...``).

    The expected value here is ``5``, which is what the *user reading the
    button* would expect.
    """
    result = calculator_page.evaluate("9-4")
    assert result == "5", (
        f"'9 − 4 =' must display '5'. Got {result!r}. "
        "Likely cause: minus button's onclick handler appends '/' instead "
        "of '-'."
    )


# ---------------------------------------------------------------------------
# Division — operand order must be left/right, not right/left
# ---------------------------------------------------------------------------
@pytest.mark.xfail(
    strict=True,
    reason="BUG-003: division operands are swapped in the parser "
    "(_0x692a / _0x831edg instead of _0x831edg / _0x692a).",
)
@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("8/2", "4"),
        ("9/3", "3"),
        ("100/4", "25"),
    ],
    ids=lambda v: f"expr={v}" if isinstance(v, str) else f"want={v}",
)
def test_division_uses_correct_operand_order(
    calculator_page: CalculatorPage,
    expression: str,
    expected: str,
) -> None:
    """``a / b`` must compute ``a`` divided by ``b``, not ``b`` divided
    by ``a``.

    Defect surfaced: the parser swaps operands for division. In source,
    the ``term`` rule contains ``_0x831edg = _0x692a / _0x831edg`` where
    ``_0x692a`` is the right-hand operand and ``_0x831edg`` is the
    left-hand accumulator — they should be the other way round. So
    ``8 / 2 =`` displays ``0.25`` (= ``2/8``) instead of ``4``.
    """
    result = calculator_page.evaluate(expression)
    assert result == expected, (
        f"{expression} must equal {expected!r}, got {result!r}. "
        "Likely cause: division operands are swapped in the parser."
    )
