#!/usr/bin/env python3
"""Self-tests for the Wave455 InfluenceMap follow-up probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_influencemap_followup_wave455_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_influencemap_followup_wave455_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=8 skipped=0 created=0 would_create=0 renamed=5 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 8, "updated count")
    assert_true(parsed["renamed"] == 5, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 8, "target count")
    assert_true(("0x004d39d0", "0x004ae319", "CMeshPart__CreatePolyBucket") in probe.EXPECTED_XREF_EDGES, "polybucket init caller")
    assert_true(("0x004d3a00", "0x004ab143", "CMesh__Deserialize") in probe.EXPECTED_XREF_EDGES, "polybucket free caller")
    assert_true(("0x0050b950", "0x0050b933", "CInfluenceMapManager__scalar_deleting_dtor") in probe.EXPECTED_XREF_EDGES, "manager destructor caller")


def test_signature_and_tag_tokens() -> None:
    tracked = probe.TARGETS["0x004ad7f0"]
    polybucket = probe.TARGETS["0x004d39d0"]
    manager = probe.TARGETS["0x0050b930"]
    assert_true("void * tracked_thing" in tracked["signature"], "tracked thing parameter")
    assert_true("CPolyBucket__InitFields" == polybucket["name"], "polybucket owner correction")
    assert_true("byte flags" in manager["signature"], "byte flags parameter")
    assert_true("owner-corrected" in manager["tags"], "manager owner tag")


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
