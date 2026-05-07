"""
Functional tests — basic four-operator arithmetic.

Strategy
--------
* Drive the calculator exclusively through its UI (CalculatorPage).
* For each expression, compare the displayed result against a value
  computed independently by ``src.utils.math_oracle``. The oracle is the
  authoritative truth; tests must never hand-code expected numbers.
* Parametrise over data tables in ``src.data.expressions`` so adding a new
  case is a one-line edit.

Failures here represent **real defects** in the application, not test-suite
issues. Each failure should map cleanly to a bug report (see bug-reports/).
"""

from __future__ import annotations

import pytest

from src.data.expressions import BASIC_ARITHMETIC, Case
from src.pages.calculator_page import CalculatorPage
from src.utils import math_oracle as oracle


pytestmark = [pytest.mark.functional, pytest.mark.regression]


# ---------------------------------------------------------------------------
# Parametrised matrix — every basic arithmetic case
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "case",
    BASIC_ARITHMETIC,
    ids=[c.id for c in BASIC_ARITHMETIC],
)
def test_basic_arithmetic_matches_oracle(
    calculator_page: CalculatorPage,
    case: Case,
) -> None:
    """Every entry in the BASIC_ARITHMETIC table must match the oracle."""
    expected = case.expected_override or oracle.expected(case.expression)
    actual = calculator_page.evaluate(case.expression)
    assert actual == expected, (
        f"[{case.id}] expression={case.expression!r}: " f"expected {expected!r}, got {actual!r}"
    )


# ---------------------------------------------------------------------------
# Sanity: addition is commutative and associative for small integers
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("a", "b"),
    [(1, 2), (4, 5), (7, 8), (9, 0)],
    ids=lambda v: f"v={v}",
)
def test_addition_is_commutative(calculator_page: CalculatorPage, a: int, b: int) -> None:
    """``a+b`` must equal ``b+a`` for any operand pair."""
    forward = calculator_page.evaluate(f"{a}+{b}")
    backward = calculator_page.evaluate(f"{b}+{a}")
    assert (
        forward == backward
    ), f"Addition not commutative: {a}+{b}={forward!r} vs {b}+{a}={backward!r}"


# ---------------------------------------------------------------------------
# Multiplicative identity & zero
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("n", [1, 2, 5, 9], ids=lambda n: f"n={n}")
def test_multiplication_by_one_returns_self(calculator_page: CalculatorPage, n: int) -> None:
    assert calculator_page.evaluate(f"{n}*1") == str(n)


@pytest.mark.parametrize("n", [1, 2, 5, 9], ids=lambda n: f"n={n}")
def test_multiplication_by_zero_returns_zero(calculator_page: CalculatorPage, n: int) -> None:
    assert calculator_page.evaluate(f"{n}*0") == "0"
