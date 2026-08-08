#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Retired 2026-08-05 Gen9–24 fixed-matrix scaffold.

The generated historical review records remain under
``local-lab/per-gen-review-20260805-v1``.  Re-running this owner would recreate
a mandatory six-cell matrix and request a retired DeepSeek model, contradicting
the current situational reviewer policy.  Active work selects an explicit
reviewer subset under ``reverse-engineering/REVIEW-PROTOCOL.md`` instead.
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "RETIRED_REVIEW_SCAFFOLD: historical Gen9-24 evidence is preserved, "
        "but active reviews must select an explicit situational subset under "
        "reverse-engineering/REVIEW-PROTOCOL.md",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
