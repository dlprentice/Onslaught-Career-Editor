#!/usr/bin/env python3
"""Unit tests for the Wave442 range probe."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_menuitem_range_wave442_probe.py"

spec = importlib.util.spec_from_file_location("wave442_probe", MODULE_PATH)
assert spec is not None and spec.loader is not None
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def test_summary_parser_handles_verify_counts() -> None:
    text = "SUMMARY updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == probe.EXPECTED_VERIFY_DRY


def test_summary_parser_rejects_old_shape() -> None:
    text = "SUMMARY: updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) is None


def test_missing_artifacts_fail() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = probe.run(Path(tmp))
    assert result["status"] == "FAIL"
    assert_true(any("apply_verify_dry.log" in item for item in result["failures"]), "expected missing verify log failure")


def test_address_normalization() -> None:
    assert probe.normalize_address("4a45c0") == "0x004a45c0"
    assert probe.normalize_address("0x5dc650") == "0x005dc650"


def main() -> int:
    tests = [
        test_summary_parser_handles_verify_counts,
        test_summary_parser_rejects_old_shape,
        test_missing_artifacts_fail,
        test_address_normalization,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
