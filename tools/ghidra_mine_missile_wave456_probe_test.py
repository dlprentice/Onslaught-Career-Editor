#!/usr/bin/env python3
"""Self-tests for the Wave456 Mine/Missile/MotionController probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_mine_missile_wave456_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_mine_missile_wave456_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=8 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 8, "updated count")
    assert_true(parsed["renamed"] == 6, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 8, "target count")
    assert_true(("0x004ba150", "0x005e1ba8", "<no_function>") in probe.EXPECTED_XREF_EDGES, "CMine init vtable data edge")
    assert_true(("0x004baae0", "0x005e3bc8", "<no_function>") in probe.EXPECTED_XREF_EDGES, "CMissile init vtable data edge")
    assert_true(("0x004bae30", "0x0049c3e3", "CMCMine__Constructor") in probe.EXPECTED_XREF_EDGES, "motion controller constructor caller")
    assert_true(("0x004bae50", "0x0049c434", "CMCMine__Destructor") in probe.EXPECTED_XREF_EDGES, "motion controller destructor caller")


def test_signature_and_tag_tokens() -> None:
    mine_init = probe.TARGETS["0x004ba150"]
    missile_dispatch = probe.TARGETS["0x004bac10"]
    motion_ctor = probe.TARGETS["0x004bae30"]
    assert_true("void * init" in mine_init["signature"], "mine init parameter")
    assert_true("int arg1" in missile_dispatch["signature"], "missile dispatch arg1 parameter")
    assert_true("CMotionController__ctor_base" == motion_ctor["name"], "motion controller constructor name")
    assert_true("signature-corrected" in motion_ctor["tags"], "motion controller constructor tag")


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
