"""
Top-level pytest configuration.

Real fixtures (WebDriver lifecycle, page-object factories, screenshot-on-failure
hook, etc.) are introduced in a later commit alongside the page-object model.
This file currently exists only to:

* mark the project root for pytest's rootdir discovery;
* expose the ``src`` package on ``sys.path`` so tests can do
  ``from src.pages.calculator_page import CalculatorPage``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent
_SRC = _PROJECT_ROOT / "src"

if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
