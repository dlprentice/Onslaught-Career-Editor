#!/usr/bin/env python3
"""Fail fast when a Windows-only repository command runs on another host."""

from __future__ import annotations

import os
import sys


def main() -> int:
    if os.name == "nt":
        return 0
    print(
        "This command requires Windows. Run it inside the configured isolated "
        "Windows VM; Linux static checks are not native WinUI or Windows-runtime evidence.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
