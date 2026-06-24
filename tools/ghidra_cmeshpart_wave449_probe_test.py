#!/usr/bin/env python3
"""Self-tests for the Wave449 CMeshPart load/optimize probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_cmeshpart_wave449_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_cmeshpart_wave449_probe", MODULE_PATH)
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


def test_normalize_address() -> None:
    assert_true(probe.normalize_address("004b4250") == "0x004b4250", "plain address")
    assert_true(probe.normalize_address("0x4af470") == "0x004af470", "short address")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 8, "target count")
    assert_true(("0x004b4250", "CMesh__OptimizeParts") in probe.EXPECTED_XREF_EDGES, "merge caller xref")
    assert_true(("0x004b3180", "CMeshPart__LoadFromStream") in probe.EXPECTED_XREF_EDGES, "material loader nested xref")


def test_signature_ret_cleanup_tokens() -> None:
    load_vertices = probe.TARGETS["0x004af470"]
    weighted_pick = probe.TARGETS["0x004b25d0"]
    assert_true("ret 0x14" in " ".join(load_vertices["commentTokens"]), "load vertices ret cleanup")
    assert_true("void * out_vec4" in weighted_pick["signature"], "random vertex output pointer")


def test_live_probe_passes() -> None:
    status, failures = probe.run_checks(probe.BASE)
    assert_true(status == "PASS", f"live probe status {status}: {failures}")


def main() -> int:
    tests = [
        test_parse_summary,
        test_normalize_address,
        test_expected_targets_and_edges,
        test_signature_ret_cleanup_tokens,
        test_live_probe_passes,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
