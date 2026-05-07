"""
Scientific-function tests — sin / cos / tan / √ / log.

Strategy
--------
The scientific functions read whatever number is in the display and replace
it with the function's result. Two distinct concerns therefore must be
tested separately:

1. **The function itself is mathematically correct**
   (e.g. ``Math.cos(0)`` should be ``1``).

2. **Domain errors are surfaced cleanly** as ``'Error'`` rather than as
   raw JS values like ``'NaN'`` / ``'-Infinity'`` leaking to the UI.

For (1), trig inputs are seeded directly via
``CalculatorPage.set_display_value`` to bypass the *input* layer, which
already has a documented defect in digit ``3`` (see BUG-002). Mixing the
two would either falsely flag ``cos`` as broken (because ``3.14159…`` gets
typed as ``0.14159…``) or hide a real cos defect behind an input bug.
Isolating the layer under test is the only sound approach.

For sqrt / log positive cases, regular click input is used because none of
the chosen values contain digit ``3``.

For domain errors, ``set_display_value`` is used because the broken minus
button (BUG-001) makes negative-number entry through the UI itself a
defect-in-defect path.
"""

from __future__ import annotations

import math

import pytest

from src.data.expressions import SCIENTIFIC, FuncCase
from src.pages.calculator_page import CalculatorPage
from src.utils import math_oracle as oracle


pytestmark = [pytest.mark.scientific, pytest.mark.regression]


# ===========================================================================
# Helpers
# ===========================================================================
_FUNC_TO_ORACLE = {
    "sin": oracle.expected_sin,
    "cos": oracle.expected_cos,
    "tan": oracle.expected_tan,
    "sqrt": oracle.expected_sqrt,
    "log": oracle.expected_log10,
}


def _expected_for(case: FuncCase) -> str:
    return _FUNC_TO_ORACLE[case.function](case.value)


# ===========================================================================
# 1. Function correctness (input layer bypassed for clean isolation)
# ===========================================================================
_TRIG_XFAIL = {
    # sin always returns 1 — BUG-007. sin_pi_over_2_approx happens to land on
    # 1 by mathematical coincidence so it is NOT xfailed.
    "sin_zero": "BUG-007: sin handler is `display.value = 434563^434562` (always 1).",
    "sin_pi": "BUG-007: sin handler ignores its input.",
}


def _trig_params():
    for c in (c for c in SCIENTIFIC if c.function in ("sin", "cos", "tan")):
        marks = (
            (pytest.mark.xfail(strict=True, reason=_TRIG_XFAIL[c.id]),)
            if c.id in _TRIG_XFAIL
            else ()
        )
        yield pytest.param(c, marks=marks, id=c.id)


class TestTrigFunctions:
    """sin / cos / tan in radians — Math.{sin,cos,tan} semantics."""

    @pytest.mark.parametrize("case", list(_trig_params()))
    def test_trig_function_matches_oracle_with_clean_input(
        self, calculator_page: CalculatorPage, case: FuncCase
    ) -> None:
        """Seed the display with the exact numeric value, then click the
        function button. Compare result against the oracle.
        """
        calculator_page.set_display_value(str(case.value))
        calculator_page.click_function(case.function)
        actual = calculator_page.read_display()
        expected = _expected_for(case)
        assert actual == expected, (
            f"[{case.id}] {case.function}({case.value}) expected {expected!r}, " f"got {actual!r}"
        )


class TestSquareRoot:
    """Positive-domain sqrt — exercised through the normal click path."""

    @pytest.mark.parametrize(
        "case",
        [c for c in SCIENTIFIC if c.function == "sqrt"],
        ids=lambda c: c.id,
    )
    def test_sqrt_positive_matches_oracle(
        self, calculator_page: CalculatorPage, case: FuncCase
    ) -> None:
        if "3" in str(case.value):
            pytest.skip("Avoids BUG-002 (digit '3' input defect).")
        actual = calculator_page.apply_function("sqrt", case.value)
        expected = _expected_for(case)
        assert (
            actual == expected
        ), f"[{case.id}] sqrt({case.value}) expected {expected!r}, got {actual!r}"


class TestLogarithm:
    """Positive-domain log10 — exercised through the normal click path."""

    @pytest.mark.parametrize(
        "case",
        [c for c in SCIENTIFIC if c.function == "log"],
        ids=lambda c: c.id,
    )
    def test_log10_positive_matches_oracle(
        self, calculator_page: CalculatorPage, case: FuncCase
    ) -> None:
        if "3" in str(case.value):
            pytest.skip("Avoids BUG-002 (digit '3' input defect).")
        actual = calculator_page.apply_function("log", case.value)
        expected = _expected_for(case)
        assert (
            actual == expected
        ), f"[{case.id}] log10({case.value}) expected {expected!r}, got {actual!r}"


# ===========================================================================
# 2. Bug-tracking — sin(x) is constant
# ===========================================================================
@pytest.mark.bug
class TestSinIsConstant:
    """sin must depend on its input.

    Defect surfaced: in the obfuscated source, the sin handler is
    ``display.value = 434563^434562`` — a bitwise-XOR of two integer
    literals that always evaluates to ``1``. The input is read but never
    used. Severity: **Critical** (function is unusable).
    """

    @pytest.mark.parametrize(
        ("value", "expected_result"),
        [
            pytest.param(
                0,
                "0",
                marks=pytest.mark.xfail(
                    strict=True,
                    reason="BUG-007: sin always returns 1.",
                ),
                id="v=0",
            ),
            pytest.param(
                1,
                "0.8414709848078965",
                marks=pytest.mark.xfail(
                    strict=True,
                    reason="BUG-007: sin always returns 1.",
                ),
                id="v=1",
            ),
            pytest.param(
                math.pi,
                "1.2246467991473532e-16",
                marks=pytest.mark.xfail(
                    strict=True,
                    reason="BUG-007: sin always returns 1.",
                ),
                id="v=pi",
            ),
            pytest.param(
                math.pi / 2,
                "1",
                # NO xfail: sin(π/2) coincidentally equals 1, so this passes
                # despite BUG-007. Once BUG-007 is fixed it will continue to
                # pass — that asymmetry is itself documentation of the defect.
                id="v=pi/2",
            ),
        ],
    )
    def test_sin_uses_its_input(
        self, calculator_page: CalculatorPage, value: float, expected_result: str
    ) -> None:
        calculator_page.set_display_value(str(value))
        calculator_page.click_function("sin")
        actual = calculator_page.read_display()
        assert actual == expected_result, (
            f"sin({value}) must equal {expected_result!r}, got {actual!r}. "
            "The handler ignores its input and always returns 1."
        )


# ===========================================================================
# 3. Bug-tracking — domain errors leak NaN / -Infinity
# ===========================================================================
@pytest.mark.bug
class TestDomainErrorsAreReported:
    """Out-of-domain inputs must surface 'Error' instead of 'NaN'/'-Infinity'.

    The application already has a working ``Error`` pathway (see
    ``isNaN(parseFloat(...))`` branch in ``func()``). It is, however, only
    triggered when ``parseFloat`` itself fails. When the display already
    holds a parseable but out-of-domain number, ``Math.sqrt(-4)`` returns
    ``NaN`` and ``Math.log10(0)`` returns ``-Infinity``, both of which are
    coerced to strings and shown verbatim. That is the defect.
    """

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-008: Math.sqrt(-x) returns NaN; func() does not "
        "normalise non-finite results to 'Error'.",
    )
    def test_sqrt_of_negative_must_show_error(self, calculator_page: CalculatorPage) -> None:
        calculator_page.set_display_value("-4")
        calculator_page.click_function("sqrt")
        result = calculator_page.read_display()
        assert result == "Error", f"√(-4) must yield 'Error', got {result!r} — raw JS NaN leaked."

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-008: Math.log10(0) returns -Infinity; func() does not "
        "normalise non-finite results to 'Error'.",
    )
    def test_log_of_zero_must_show_error(self, calculator_page: CalculatorPage) -> None:
        calculator_page.set_display_value("0")
        calculator_page.click_function("log")
        result = calculator_page.read_display()
        assert (
            result == "Error"
        ), f"log(0) must yield 'Error', got {result!r} — raw JS -Infinity leaked."

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-008: Math.log10(-x) returns NaN; func() does not "
        "normalise non-finite results to 'Error'.",
    )
    def test_log_of_negative_must_show_error(self, calculator_page: CalculatorPage) -> None:
        calculator_page.set_display_value("-1")
        calculator_page.click_function("log")
        result = calculator_page.read_display()
        assert result == "Error", f"log(-1) must yield 'Error', got {result!r} — raw JS NaN leaked."


# ===========================================================================
# 4. Sanity — function-then-arithmetic chains work
# ===========================================================================
class TestFunctionThenArithmetic:
    """A scientific function's result must be a valid LHS for further ops."""

    def test_sqrt_result_can_be_added_to(self, calculator_page: CalculatorPage) -> None:
        """``√4 + 1 = 3`` — proves the function-result is a real number on the
        display, not a stale string blocking further input.
        """
        calculator_page.click_clear()
        calculator_page.click_digit(4)
        calculator_page.click_function("sqrt")
        assert calculator_page.read_display() == "2"
        calculator_page.click_operator("+")
        calculator_page.click_digit(1)
        calculator_page.click_equals()
        assert calculator_page.read_display() == "3"


# ===========================================================================
# 5. Function pressed with empty display
# ===========================================================================
class TestFunctionWithEmptyDisplay:
    """The application correctly shows 'Error' when a function is pressed
    with no operand. Pin the working behaviour so a regression flips this.
    """

    @pytest.mark.parametrize("function", ["sin", "cos", "tan", "sqrt", "log"])
    def test_function_on_empty_display_shows_error(
        self, calculator_page: CalculatorPage, function: str
    ) -> None:
        calculator_page.click_clear()
        calculator_page.click_function(function)
        assert (
            calculator_page.read_display() == "Error"
        ), f"{function}() with empty display must show 'Error'."
