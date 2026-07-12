#!/usr/bin/env python3
"""Compatibility wrapper for the public-primary payload safety check."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import public_allowlist_safety_check


def check_candidate_root(root: Path) -> list[public_allowlist_safety_check.Finding]:
    """Scan an already materialized candidate without requiring Git metadata."""

    return public_allowlist_safety_check.check_payload_root(root)


def candidate_files(root: Path) -> list[str]:
    return public_allowlist_safety_check.payload_root_files(root)


def run_self_test() -> int:
    result = public_allowlist_safety_check.run_self_test()
    if result != 0:
        return result

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "README.MD").write_text("# Materialized candidate\n", encoding="utf-8")
        if check_candidate_root(root):
            print("Public-primary payload inventory self-test: FAIL")
            print("- safe non-git candidate was rejected")
            return 1

        (root / "game").mkdir()
        (root / "game" / "BEA.exe").write_bytes(b"not allowed")
        if not any(finding.label == "deny-root" for finding in check_candidate_root(root)):
            print("Public-primary payload inventory self-test: FAIL")
            print("- non-git candidate did not reject a game payload root")
            return 1

    print("Public-primary payload inventory self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--candidate-root", default=".")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.candidate_root).resolve()
    findings = check_candidate_root(root)
    if findings:
        print("Public-primary payload inventory check: FAIL")
        for finding in findings[:200]:
            print(f"- {finding.path}: {finding.label}: {finding.detail}")
        if len(findings) > 200:
            print(f"- ... ({len(findings) - 200} more)")
        return 1

    print("Public-primary payload inventory check: PASS")
    print(f"Public candidate files checked: {len(candidate_files(root))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
