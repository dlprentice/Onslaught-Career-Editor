#!/usr/bin/env python3
"""Self-tests for the Wave457 world occupancy/pathfinding probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_world_occupancy_wave457_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_world_occupancy_wave457_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=13 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 13, "updated count")
    assert_true(parsed["renamed"] == 0, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 13, "target count")
    assert_true(("0x004bc260", "0x0050d5cb", "CWorld__InitLODLists") in probe.EXPECTED_XREF_EDGES, "LOD occupancy init edge")
    assert_true(("0x004bc510", "0x004be254", "CExplosionInitThing__BuildGridPathWithFallbackSearch") in probe.EXPECTED_XREF_EDGES, "grid path blocked edge")
    assert_true(("0x004be050", "0x0050d363", "CWorld__LoadWorld") in probe.EXPECTED_XREF_EDGES, "world load bitplane edge")
    assert_true(("0x004beea0", "0x004be40a", "CExplosionInitThing__BuildGridPathWithFallbackSearch") in probe.EXPECTED_XREF_EDGES, "path simplify edge")


def test_signature_and_tag_tokens() -> None:
    init = probe.TARGETS["0x004bc260"]
    blocked = probe.TARGETS["0x004bc510"]
    load_chunk = probe.TARGETS["0x004be050"]
    assert_true("float max_slope_degrees" in init["signature"], "occupancy init threshold parameter")
    assert_true("uint end_grid_y" in blocked["signature"], "grid segment end y parameter")
    assert_true("void * mem_buffer" in load_chunk["signature"], "load chunk buffer parameter")
    assert_true("world-occupancy-wave457" in init["tags"], "wave tag")


def test_live_probe_passes() -> None:
    status, failures = probe.run_checks(probe.BASE)
    assert_true(status == "PASS", f"live probe status {status}: {failures}")


def main() -> int:
    tests = [
        test_parse_summary,
        test_expected_targets_and_edges,
        test_signature_and_tag_tokens,
        test_live_probe_passes,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
