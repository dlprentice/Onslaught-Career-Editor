#!/usr/bin/env python3
"""Self-tests for the Wave448 CMeshPart transform/cache probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_cmeshpart_wave448_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_cmeshpart_wave448_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=8 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 8, "updated count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_compact_token_present() -> None:
    text = "RET 0x44 confirms a 12-dword parent transform block"
    assert_true(probe.token_present(text, "ret 0x44 confirms"), "compact token")


def test_normalize_address() -> None:
    assert_true(probe.normalize_address("004b24d0") == "0x004b24d0", "plain address")
    assert_true(probe.normalize_address("0x4b0800") == "0x004b0800", "short address")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 8, "target count")
    assert_true(("0x004b24d0", "CMeshPart__EvaluatePoseTransformForFrame") in probe.EXPECTED_XREF_EDGES, "frame resolver xref")


def test_live_probe_passes() -> None:
    status, failures = probe.run_checks(probe.BASE)
    assert_true(status == "PASS", f"live probe status {status}: {failures}")


def main() -> int:
    tests = [
        test_parse_summary,
        test_compact_token_present,
        test_normalize_address,
        test_expected_targets_and_edges,
        test_live_probe_passes,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
