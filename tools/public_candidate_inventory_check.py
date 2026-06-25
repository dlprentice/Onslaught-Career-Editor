#!/usr/bin/env python3
"""Compatibility wrapper for the public-primary payload safety check."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import public_allowlist_safety_check


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--candidate-root", default=".")
    args = parser.parse_args()

    if args.self_test:
        result = public_allowlist_safety_check.run_self_test()
        if result != 0:
            return result

    root = Path(args.candidate_root).resolve()
    findings = public_allowlist_safety_check.check_repo(root)
    if findings:
        print("Public-primary payload inventory check: FAIL")
        for finding in findings[:200]:
            print(f"- {finding.path}: {finding.label}: {finding.detail}")
        if len(findings) > 200:
            print(f"- ... ({len(findings) - 200} more)")
        return 1

    print("Public-primary payload inventory check: PASS")
    print(f"Public candidate files checked: {len(public_allowlist_safety_check.public_candidate_files(root))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
