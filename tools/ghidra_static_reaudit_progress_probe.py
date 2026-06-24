#!/usr/bin/env python3
"""Compatibility wrapper for the static re-audit accounting guard.

The active measurable authority moved to unique-address accounting in
``static_reaudit_accounting_guard.py``. Keep this script as a stable command
surface, but do not duplicate counters here.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "tools" / "static_reaudit_accounting_guard.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("static_reaudit_accounting_guard", GUARD)
    if spec is None or spec.loader is None:
        raise ImportError(GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
