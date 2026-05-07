"""
Helpers that convert Python numbers to the exact string form a browser
``<input>`` field would show after a JavaScript ``Number.toString()`` round-trip.

Why this matters
----------------
The calculator renders results with::

    display.value = <number>;

…and HTML inputs coerce the assigned value to a string using JS rules:

* ``2``  -> ``"2"``                 (no trailing ``.0``)
* ``2.5`` -> ``"2.5"``
* ``1/3`` -> ``"0.3333333333333333"`` (17 significant digits, no trailing zeros)
* ``Math.tan(0)`` -> ``"0"``        (not ``"0.0"``)
* ``Infinity`` -> ``"Infinity"``
* ``NaN`` -> ``"NaN"``

Python's default ``str(float)`` differs in subtle ways (e.g. ``str(0.0)`` is
``"0.0"``). This module implements the JS rules so test oracles produce
exactly the strings the UI is expected to show, eliminating an entire class
of false-negative comparisons.
"""

from __future__ import annotations

import math
from typing import Final

# The string the application uses to signal evaluation failure.
ERROR_TOKEN: Final[str] = "Error"


def js_number_to_string(value: float | int) -> str:
    """Replicate JavaScript's ``Number.prototype.toString`` for finite numbers,
    plus the ``Infinity`` / ``NaN`` literals JS shows when coerced to string.

    The algorithm is "shortest round-trippable representation" — the same
    approach Python's ``repr(float)`` uses for floats — with one caveat:
    integer-valued floats are rendered without a fractional part (so ``4.0``
    becomes ``"4"`` rather than ``"4.0"``). That matches what JS does and
    what the calculator displays.
    """
    if isinstance(value, bool):  # bool is a subclass of int — guard against surprises
        raise TypeError("Booleans are not valid numeric display values")

    if isinstance(value, int):
        return str(value)

    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"

    # Integer-valued floats: emit without a decimal point.
    if value.is_integer():
        return str(int(value))

    # Python's repr already gives the shortest round-trippable form for
    # IEEE-754 doubles, which is identical to V8's Number#toString output
    # for the vast majority of values.
    return repr(value)
