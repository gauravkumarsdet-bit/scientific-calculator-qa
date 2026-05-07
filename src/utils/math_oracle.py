"""
Math oracle — the authoritative source of *correct* expected results.

Tests must never hand-code expected numbers; instead they call
``oracle.expected(expression)`` (or one of the function-specific helpers)
and compare against that. This buys us:

* a single audit point if the spec ever changes (e.g. trig in degrees);
* test inputs that double as documentation of the expected behaviour;
* protection against the very class of bugs we're hunting (operator swaps,
  wrong-handler wiring) — because the oracle is computed independently in
  Python, not by re-reading the same JS the calculator uses.

The oracle's evaluator is a *small, deliberate* parser, not ``eval()``.
Using ``eval`` would happily accept arbitrary Python and silently mask
expression-syntax bugs we want to catch.
"""

from __future__ import annotations

import math
import re
from typing import Final

from src.utils.display_format import js_number_to_string


# ---------------------------------------------------------------------------
# Float comparison
# ---------------------------------------------------------------------------
DEFAULT_REL_TOL: Final[float] = 1e-9
DEFAULT_ABS_TOL: Final[float] = 1e-12


def floats_equal(
    a: float,
    b: float,
    *,
    rel_tol: float = DEFAULT_REL_TOL,
    abs_tol: float = DEFAULT_ABS_TOL,
) -> bool:
    """Tolerant float equality, NaN-safe (``NaN != NaN`` always)."""
    if math.isnan(a) or math.isnan(b):
        return False
    if math.isinf(a) or math.isinf(b):
        return a == b
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


# ---------------------------------------------------------------------------
# Recursive-descent expression evaluator
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(r"\s*(\d+\.\d+|\.\d+|\d+|[+\-*/()])")


class _Parser:
    """Grammar (left-associative, standard precedence)::

    expr   := term   (('+'|'-') term)*
    term   := factor (('*'|'/') factor)*
    factor := number | '(' expr ')' | ('+'|'-') factor
    """

    def __init__(self, expression: str) -> None:
        self.tokens = self._tokenize(expression)
        self.pos = 0

    @staticmethod
    def _tokenize(expression: str) -> list[str]:
        tokens: list[str] = []
        i = 0
        while i < len(expression):
            m = _TOKEN_RE.match(expression, i)
            if not m:
                raise ValueError(f"Unexpected character at position {i}: {expression[i]!r}")
            tokens.append(m.group(1))
            i = m.end()
        return tokens

    def _peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _consume(self) -> str:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self) -> float:
        result = self._expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected trailing token: {self.tokens[self.pos]!r}")
        return result

    def _expr(self) -> float:
        value = self._term()
        while self._peek() in ("+", "-"):
            op = self._consume()
            rhs = self._term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def _term(self) -> float:
        value = self._factor()
        while self._peek() in ("*", "/"):
            op = self._consume()
            rhs = self._factor()
            if op == "*":
                value = value * rhs
            else:
                # Mirror JS semantics: division by zero yields Infinity / -Infinity / NaN.
                if rhs == 0:
                    if value == 0:
                        value = float("nan")
                    else:
                        value = math.copysign(float("inf"), value)
                else:
                    value = value / rhs
        return value

    def _factor(self) -> float:
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if tok == "(":
            self._consume()
            value = self._expr()
            if self._peek() != ")":
                raise ValueError("Missing closing parenthesis")
            self._consume()
            return value
        if tok in ("+", "-"):
            sign = self._consume()
            return -self._factor() if sign == "-" else self._factor()
        # number
        self._consume()
        return float(tok)


def evaluate(expression: str) -> float:
    """Return the numerically-correct value of ``expression`` as a Python float."""
    return _Parser(expression).parse()


def expected(expression: str) -> str:
    """Return the *display string* the calculator should show for ``expression``.

    This is what tests compare against::

        assert calculator_page.evaluate("8/2") == oracle.expected("8/2")  # "4"
    """
    return js_number_to_string(evaluate(expression))


# ---------------------------------------------------------------------------
# Scientific-function oracles (mirror Math.* in radians, log10 for log)
# ---------------------------------------------------------------------------
def expected_sin(value: float) -> str:
    return js_number_to_string(math.sin(value))


def expected_cos(value: float) -> str:
    return js_number_to_string(math.cos(value))


def expected_tan(value: float) -> str:
    return js_number_to_string(math.tan(value))


def expected_sqrt(value: float) -> str:
    if value < 0:
        return js_number_to_string(float("nan"))
    return js_number_to_string(math.sqrt(value))


def expected_log10(value: float) -> str:
    """The calculator uses ``Math.log10``."""
    if value == 0:
        return js_number_to_string(float("-inf"))
    if value < 0:
        return js_number_to_string(float("nan"))
    return js_number_to_string(math.log10(value))
