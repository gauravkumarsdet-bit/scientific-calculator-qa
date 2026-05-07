"""
Tiny logging helper.

We deliberately avoid a heavyweight logging framework — pytest already does
structured CLI logging (configured in ``pytest.ini``), so all we need is a
factory that returns a properly-named ``logging.Logger`` and ensures the root
logger's level is sensible when the suite is invoked outside pytest (e.g. via
``python -m`` for a quick smoke check).
"""

from __future__ import annotations

import logging
from typing import Final

_DEFAULT_FORMAT: Final[str] = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
_DEFAULT_DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with a sensible default handler & format.

    Idempotent: calling repeatedly with the same name does not duplicate
    handlers (important inside pytest, which imports modules many times).
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT, _DEFAULT_DATEFMT))
        logger.addHandler(handler)
        logger.propagate = False

    return logger
