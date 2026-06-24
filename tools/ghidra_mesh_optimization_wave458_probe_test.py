#!/usr/bin/env python3
"""Self-tests for the Wave458 mesh optimization/NamedMesh probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_mesh_optimization_wave458_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_mesh_optimization_wave458_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=5 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 5, "updated count")
    assert_true(parsed["renamed"] == 1, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 5, "target count")
    assert_true(("0x004bae70", "0x004ab549", "CMesh__OptimizeParts") in probe.EXPECTED_XREF_EDGES, "strict optimize xref")
    assert_true(("0x004bb040", "0x004ab44e", "CMesh__OptimizeParts") in probe.EXPECTED_XREF_EDGES, "merge optimize xref")
    assert_true(("0x004bb210", "0x004ab772", "CMesh__OptimizeParts") in probe.EXPECTED_XREF_EDGES, "mesh constraints xref")
    assert_true(("0x004bc050", "0x00418460", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh") in probe.EXPECTED_XREF_EDGES, "named mesh cleanup xref")


def test_signature_and_comment_tokens() -> None:
    strict = probe.TARGETS["0x004bae70"]
    named_cleanup = probe.TARGETS["0x004bc050"]
    named_init = probe.TARGETS["0x004bbcd0"]
    assert_true("void * part" in strict["signature"], "strict part pointer parameter")
    assert_true("CNamedMesh__VFunc02_RemoveFromOccupancyAndForward" in named_cleanup["name"], "named mesh cleanup name")
    assert_true("EAX-carried init pointer" in named_init["commentTokens"], "named mesh EAX init boundary token")
    assert_true("mesh-optimization-wave458" in strict["tags"], "wave tag")


def test_live_probe_passes() -> None:
    status, failures = probe.run_checks(probe.BASE)
    assert_true(status == "PASS", f"live probe status {status}: {failures}")


def main() -> int:
    tests = [
        test_parse_summary,
        test_expected_targets_and_edges,
        test_signature_and_comment_tokens,
        test_live_probe_passes,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
