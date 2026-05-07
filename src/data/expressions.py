"""
Curated expression banks for parametrised tests.

Each record is a ``Case`` with:

* ``id`` — short, stable identifier used by pytest ids (``-k`` selection &
  human-readable test names in reports).
* ``expression`` — the literal characters a user would press, in order.
  Restricted to: digits, ``+ - * /``, parentheses, ``.``.
* ``expected_override`` — set only when the truth cannot be derived from the
  oracle (e.g. testing the *bug* of empty-input behaviour where the
  application emits ``"undefined"``).
* ``tags`` — informational; lets tests cherry-pick (``"negative"``,
  ``"precedence"`` …).

Keeping data flat and parametrised rather than embedded in tests scales:
adding a new arithmetic case is a one-line edit, not a new test method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class Case:
    id: str
    expression: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    expected_override: str | None = None  # only when oracle cannot compute it


# ---------------------------------------------------------------------------
# Basic arithmetic — every operator, positive operands, single op
# ---------------------------------------------------------------------------
BASIC_ARITHMETIC: Final[tuple[Case, ...]] = (
    Case("add_small", "2+3", tags=("addition",)),
    Case("add_zero", "0+0", tags=("addition", "boundary")),
    Case("add_large", "999+1", tags=("addition",)),
    Case("sub_simple", "9-4", tags=("subtraction",)),
    Case("sub_to_zero", "7-7", tags=("subtraction", "boundary")),
    Case("sub_negative_result", "2-9", tags=("subtraction", "negative")),
    Case("mul_simple", "6*7", tags=("multiplication",)),
    Case("mul_by_zero", "8*0", tags=("multiplication", "boundary")),
    Case("mul_by_one", "5*1", tags=("multiplication", "identity")),
    Case("div_clean", "8/2", tags=("division",)),
    Case("div_recurring", "1/3", tags=("division", "irrational")),
    Case("div_one", "7/1", tags=("division", "identity")),
)

# ---------------------------------------------------------------------------
# Decimal handling
# ---------------------------------------------------------------------------
DECIMAL: Final[tuple[Case, ...]] = (
    Case("dec_add", "1.5+2.5", tags=("decimal", "addition")),
    Case("dec_sub", "10.0-0.1", tags=("decimal", "subtraction", "ieee754")),
    Case("dec_mul", "0.1*0.2", tags=("decimal", "multiplication", "ieee754")),
    Case("dec_div", "0.5/0.25", tags=("decimal", "division")),
    Case("dec_leading_dot", ".5+.5", tags=("decimal", "lexer")),
    Case("dec_trailing_zero", "2.50+1.50", tags=("decimal",)),
)

# ---------------------------------------------------------------------------
# Parentheses & operator precedence
# ---------------------------------------------------------------------------
PARENTHESES: Final[tuple[Case, ...]] = (
    Case("paren_simple", "(2+3)*4", tags=("parentheses", "precedence")),
    Case("paren_nested", "((1+2)*3)", tags=("parentheses", "nested")),
    Case("paren_redundant", "(((5)))", tags=("parentheses", "redundant")),
    Case("paren_then_op", "2*(3+4)", tags=("parentheses",)),
)

PRECEDENCE: Final[tuple[Case, ...]] = (
    Case("prec_mul_before_add", "2+3*4", tags=("precedence",)),
    Case("prec_div_before_sub", "10-6/2", tags=("precedence",)),
    Case("prec_left_assoc_sub", "10-3-2", tags=("precedence", "left-assoc")),
    Case("prec_left_assoc_div", "100/5/2", tags=("precedence", "left-assoc")),
    Case("prec_mixed", "2+3*4-5/5", tags=("precedence", "mixed")),
)

# ---------------------------------------------------------------------------
# Edge cases — these often expose real defects
# ---------------------------------------------------------------------------
# Use ``expected_override`` only when the value cannot come from the oracle.
EDGE_CASES_DIV_BY_ZERO: Final[tuple[Case, ...]] = (
    Case("div_zero_pos", "5/0", tags=("edge", "div-by-zero")),
    Case("div_zero_neg", "(0-5)/0", tags=("edge", "div-by-zero", "negative")),
    Case("div_zero_zero", "0/0", tags=("edge", "div-by-zero", "indeterminate")),
)


# ---------------------------------------------------------------------------
# Scientific functions — operate on a single value already on the display
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FuncCase:
    id: str
    function: str  # 'sin' | 'cos' | 'tan' | 'sqrt' | 'log'
    value: float
    tags: tuple[str, ...] = field(default_factory=tuple)


SCIENTIFIC: Final[tuple[FuncCase, ...]] = (
    # sin / cos / tan operate in **radians** in the app (Math.sin etc.)
    FuncCase("sin_zero", "sin", 0, tags=("trig", "boundary")),
    FuncCase("sin_pi_over_2_approx", "sin", 1.5707963267948966, tags=("trig",)),
    FuncCase("sin_pi", "sin", 3.141592653589793, tags=("trig",)),
    FuncCase("cos_zero", "cos", 0, tags=("trig", "boundary")),
    FuncCase("cos_pi", "cos", 3.141592653589793, tags=("trig",)),
    FuncCase("tan_zero", "tan", 0, tags=("trig", "boundary")),
    FuncCase("tan_pi_over_4", "tan", 0.7853981633974483, tags=("trig",)),
    FuncCase("sqrt_perfect", "sqrt", 16, tags=("sqrt",)),
    FuncCase("sqrt_zero", "sqrt", 0, tags=("sqrt", "boundary")),
    FuncCase("sqrt_two", "sqrt", 2, tags=("sqrt", "irrational")),
    FuncCase("log_one", "log", 1, tags=("log", "boundary")),  # log10(1) = 0
    FuncCase("log_ten", "log", 10, tags=("log", "boundary")),  # log10(10) = 1
    FuncCase("log_hundred", "log", 100, tags=("log",)),
    FuncCase("log_decimal", "log", 0.1, tags=("log",)),
)

SCIENTIFIC_INVALID: Final[tuple[FuncCase, ...]] = (
    FuncCase("sqrt_negative", "sqrt", -4, tags=("sqrt", "invalid", "domain")),
    FuncCase("log_zero", "log", 0, tags=("log", "invalid", "domain")),
    FuncCase("log_negative", "log", -5, tags=("log", "invalid", "domain")),
)
