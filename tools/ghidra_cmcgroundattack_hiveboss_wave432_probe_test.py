#!/usr/bin/env python3
"""Unit tests for the Wave432 CMCGroundAttack / CMCHiveBoss probe."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_cmcgroundattack_hiveboss_wave432_probe.py"

spec = importlib.util.spec_from_file_location("wave432_probe", MODULE_PATH)
assert spec is not None and spec.loader is not None
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def test_summary_parser_handles_create_counts() -> None:
    text = "SUMMARY updated=11 skipped=0 created=3 would_create=0 renamed=8 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == probe.EXPECTED_APPLY


def test_summary_parser_rejects_old_shape() -> None:
    text = "SUMMARY: updated=11 skipped=0 renamed=8 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) is None


def test_missing_artifacts_fail() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = probe.run(Path(tmp))
    assert result["status"] == "FAIL"
    assert_true(any("apply_dry.log" in item for item in result["failures"]), "expected missing dry log failure")


def test_address_normalization() -> None:
    assert probe.normalize_address("496540") == "0x00496540"
    assert probe.normalize_address("0x4976d0") == "0x004976d0"


def main() -> int:
    tests = [
        test_summary_parser_handles_create_counts,
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
