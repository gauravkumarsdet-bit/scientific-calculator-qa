"""
Edge-case tests — parentheses, operator precedence, division-by-zero,
malformed input.

Why a separate suite?
---------------------
Smoke is "does it load?" Functional is "do single operations work?"
Edge is "what happens when the user pushes the boundaries — nested
parens, ambiguous-precedence chains, division-by-zero, malformed input?"
Edge cases are where naively-implemented expression parsers tend to
collapse, and that intuition holds here.

Cascade isolation
-----------------
Several outwardly-edge results are actually clean cascades of bugs the
suite has already documented (the broken minus button BUG-001, the
operand-swap BUG-003). Where a result *would* be correct on the
non-broken path, the test is structured so the assertion would still pass
once the underlying defect is fixed. Where the edge case itself is the
defect, it is marked ``@pytest.mark.bug`` and given a clear name.

We deliberately avoid ASCII '-' in inputs (it routes through the broken
minus button) and ASCII '3' digits (BUG-002). Where subtraction or '3'
is needed, we synthesise it via parentheses, alternative arithmetic, or
the JS-bypass set_display_value.
"""

from __future__ import annotations

import pytest

from src.data.expressions import PARENTHESES, PRECEDENCE, Case
from src.pages.calculator_page import CalculatorPage
from src.utils import math_oracle as oracle


pytestmark = [pytest.mark.edge, pytest.mark.regression]


# ===========================================================================
# 1. Parentheses — when nothing follows, results are correct
# ===========================================================================
class TestParenthesesAlone:
    """Parens at the *end* of an expression work correctly."""

    @pytest.mark.parametrize(
        "case",
        # Filter PARENTHESES bank to cases where ')' is the rightmost token,
        # which avoids the BUG-009 parser-truncation defect (covered below).
        [c for c in PARENTHESES if c.expression.rstrip().endswith(")")],
        ids=lambda c: c.id,
    )
    def test_paren_when_closing_is_rightmost_token(
        self, calculator_page: CalculatorPage, case: Case
    ) -> None:
        if "3" in case.expression or "-" in case.expression:
            pytest.skip("Skipping inputs that depend on BUG-001/BUG-002.")
        actual = calculator_page.evaluate(case.expression)
        assert actual == oracle.expected(case.expression)

    def test_redundant_parens_collapse_to_value(self, calculator_page: CalculatorPage) -> None:
        assert calculator_page.evaluate("(((5)))") == "5"

    def test_paren_around_zero(self, calculator_page: CalculatorPage) -> None:
        assert calculator_page.evaluate("(0)") == "0"

    def test_leading_factor_then_parens(self, calculator_page: CalculatorPage) -> None:
        """``4*(2+5)`` — closing paren is rightmost, so works."""
        assert calculator_page.evaluate("4*(2+5)") == "28"


# ===========================================================================
# 2. Parentheses bug — anything after a closing ')' is silently dropped
# ===========================================================================
@pytest.mark.bug
@pytest.mark.xfail(
    strict=True,
    reason="BUG-009: parser silently drops every token after a closing "
    "')' that is not the right-most token.",
)
class TestParserTruncatesAfterClosingParen:
    """The parser drops every token after a closing ``)`` that is not the
    rightmost token in the expression.

    Defect surfaced (BUG-009)
    -------------------------
    In the recursive-descent parser, the ``factor`` rule consumes
    ``(...)`` and *returns immediately* — but the calling ``expr`` /
    ``term`` rule never resumes its outer ``while`` loop because the
    closing ``)`` has already advanced the position past where the loop
    expects an operator. The net effect is that ``(2+5)*4`` evaluates as
    ``(2+5)`` (= 7), silently discarding ``*4``.

    Severity
    --------
    **High** — every reasonably-complex expression that uses parentheses
    in the middle (a normal use case for a scientific calculator) will
    silently produce a wrong-but-plausible answer. This is the kind of
    defect that ships and rots in a customer's spreadsheet for years.
    """

    @pytest.mark.parametrize(
        ("expression", "expected"),
        [
            ("(2+5)*4", "28"),
            ("(2+5)+1", "8"),
            ("(2+5)*4+1", "29"),
            ("1+(2+5)*4", "29"),
            ("(1+1)*(1+1)", "4"),
        ],
        ids=lambda v: f"v={v}" if isinstance(v, str) else f"want={v}",
    )
    def test_tokens_after_closing_paren_must_be_evaluated(
        self,
        calculator_page: CalculatorPage,
        expression: str,
        expected: str,
    ) -> None:
        actual = calculator_page.evaluate(expression)
        assert actual == expected, (
            f"{expression} must equal {expected!r}, got {actual!r} — "
            "tokens after the first ')' are silently dropped (BUG-009)."
        )


# ===========================================================================
# 3. Malformed parentheses
# ===========================================================================
@pytest.mark.bug
@pytest.mark.xfail(
    strict=True,
    reason="BUG-010: malformed paren inputs leak NaN or are silently "
    "truncated; the existing 'Error' pathway should subsume them.",
)
class TestMalformedParenthesesShouldYieldError:
    """Mismatched / empty parens should land on the existing 'Error'
    pathway, not leak 'NaN' or silently truncate.

    Severity: Medium — error pathway already exists for ``(`` alone and
    for trailing operators, so extending it to these inputs is small,
    and the current behaviour is misleading (silently wrong rather than
    explicitly failing).
    """

    @pytest.mark.parametrize(
        "expression",
        [")", "()", "(2+5", "2+5)"],
        ids=lambda e: f"expr={e!r}",
    )
    def test_malformed_paren_input_must_yield_error(
        self, calculator_page: CalculatorPage, expression: str
    ) -> None:
        result = calculator_page.evaluate(expression)
        assert (
            result == "Error"
        ), f"Malformed input {expression!r} must yield 'Error'; got {result!r}."


# ===========================================================================
# 4. Operator precedence (multiplication only — division & subtraction are
#    independently broken and would mask the precedence assertion)
# ===========================================================================
class TestOperatorPrecedenceMultiplicativeOnly:
    """Multiplication-with-addition precedence — the only mixed case that
    can be assessed cleanly while BUG-001 (minus) and BUG-003 (div swap)
    remain unfixed.
    """

    @pytest.mark.parametrize(
        "case",
        [c for c in PRECEDENCE if "/" not in c.expression and "-" not in c.expression],
        ids=lambda c: c.id,
    )
    def test_precedence_matches_oracle(self, calculator_page: CalculatorPage, case: Case) -> None:
        if "3" in case.expression:
            pytest.skip("Skipping inputs that depend on BUG-002.")
        actual = calculator_page.evaluate(case.expression)
        assert actual == oracle.expected(case.expression)

    def test_multiplication_precedes_addition(self, calculator_page: CalculatorPage) -> None:
        """``2 + 5 * 4`` must equal 22, not 28."""
        assert calculator_page.evaluate("2+5*4") == "22"


# ===========================================================================
# 5. Division by zero — what the calculator should display
# ===========================================================================
@pytest.mark.bug
@pytest.mark.xfail(
    strict=True,
    reason="BUG-011: a/0 leaks Infinity / NaN (or 0 via cascade with "
    "BUG-003) instead of the existing 'Error' pathway.",
)
class TestDivisionByZero:
    """``a / 0`` must surface ``Error`` rather than leaking JS Infinity /
    -Infinity / NaN.

    Note: ``5/0`` displays ``'0'`` today, which is itself a *cascade* of
    BUG-003 (operand-swap turns 5/0 into 0/5 = 0). We use ``set_display_value``
    where needed to bypass the input-side defects so this test asserts on
    the division-by-zero handling specifically.
    """

    def test_div_by_zero_via_input_must_show_error(self, calculator_page: CalculatorPage) -> None:
        """Issue: even were operand-swap fixed, dividing by zero would
        still surface ``Infinity`` per JS semantics. The calculator
        should recognise the divide-by-zero and emit ``Error``.

        For the assertion, we set the display directly to '5' and click
        the divide button, then enter '0' and press '='. We can't enter
        the divisor that way without a working operator path, so this
        test uses the click path knowing that operand-swap will yield 0:
        the assertion remains valid because *neither* '0' nor 'Infinity'
        is acceptable; both fail.
        """
        result = calculator_page.evaluate("5/0")
        assert result == "Error", f"5/0 must yield 'Error', got {result!r}."

    def test_zero_div_zero_must_show_error(self, calculator_page: CalculatorPage) -> None:
        """``0/0`` is mathematically undefined; the UI must show 'Error'
        rather than the JS literal 'NaN'.
        """
        result = calculator_page.evaluate("0/0")
        assert result == "Error", f"0/0 must yield 'Error', got {result!r}."


# ===========================================================================
# 6. Idempotence of '=' — pressing equals on a result is a no-op
# ===========================================================================
class TestEqualsIsIdempotent:
    """Pressing ``=`` on an already-evaluated result must not change it."""

    def test_pressing_equals_twice_preserves_result(self, calculator_page: CalculatorPage) -> None:
        # 2+5 avoids '3' and '-' — guaranteed clean.
        first = calculator_page.evaluate("2+5")
        calculator_page.click_equals()
        second = calculator_page.read_display()
        assert first == second == "7"


# ===========================================================================
# 7. Numeric extremes — large & small numbers don't break the display
# ===========================================================================
class TestNumericExtremes:
    """The display must not truncate or mangle representable numbers."""

    def test_large_integer_multiplication(self, calculator_page: CalculatorPage) -> None:
        """``99999999999999999 * 2`` — exercises near-Number.MAX_SAFE_INTEGER."""
        # Use set_display_value to skip slow per-digit clicks.
        calculator_page.set_display_value("99999999999999999*2")
        calculator_page.click_equals()
        # JS: 99999999999999999 * 2 = 200000000000000000 (loses precision but no crash).
        assert calculator_page.read_display() == "200000000000000000"

    def test_very_small_decimal_multiplication(self, calculator_page: CalculatorPage) -> None:
        """``0.0001 * 0.0001`` — JS uses scientific notation for small floats."""
        calculator_page.set_display_value("0.0001*0.0001")
        calculator_page.click_equals()
        assert calculator_page.read_display() == "1e-8"
