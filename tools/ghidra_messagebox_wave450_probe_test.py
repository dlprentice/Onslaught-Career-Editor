#!/usr/bin/env python3
"""Self-tests for the Wave450 MessageBox/portrait probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_messagebox_wave450_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_messagebox_wave450_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=17 skipped=0 created=0 would_create=0 renamed=10 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 17, "updated count")
    assert_true(parsed["renamed"] == 10, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 17, "target count")
    assert_true(("0x004b7b80", "CMessageBox__RequestQueueAdvance") in probe.EXPECTED_XREF_EDGES, "queue advance edge")
    assert_true(("0x004b7ca0", "IScript__PlaySoundWithFadeAndPriority") in probe.EXPECTED_XREF_EDGES, "script sound edge")
    assert_true(("0x004b8800", "CDXEngine__RenderMessageBoxOverlay") in probe.EXPECTED_XREF_EDGES, "overlay stop edge")


def test_signature_cleanup_tokens() -> None:
    scalar_dtor = probe.TARGETS["0x004b7300"]
    wrap = probe.TARGETS["0x004b6f70"]
    battle_line = probe.TARGETS["0x004b82b0"]
    assert_true("byte flags" in scalar_dtor["signature"], "scalar deleting dtor flags")
    assert_true("line_buffer" in wrap["signature"], "word-wrap line buffer")
    assert_true("screen_x" in battle_line["signature"], "battleline screen x")


def test_live_probe_passes() -> None:
    status, failures = probe.run_checks(probe.BASE)
    assert_true(status == "PASS", f"live probe status {status}: {failures}")


def main() -> int:
    tests = [
        test_parse_summary,
        test_expected_targets_and_edges,
        test_signature_cleanup_tokens,
        test_live_probe_passes,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
