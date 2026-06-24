#!/usr/bin/env python3
"""Self-tests for the Wave454 CMusic static-reaudit probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_music_wave454_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_music_wave454_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=11 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 11, "updated count")
    assert_true(parsed["renamed"] == 6, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 11, "target count")
    assert_true(("0x004bb530", "CGame__MainLoop") in probe.EXPECTED_XREF_EDGES, "game main loop update edge")
    assert_true(("0x004bb7e0", "CMusic__FadeVolumes") in probe.EXPECTED_XREF_EDGES, "fade queued play edge")
    assert_true(("0x004bb8c0", "CGame__PlayMusicForCurrentLevel") in probe.EXPECTED_XREF_EDGES, "game selection edge")


def test_signature_and_tag_tokens() -> None:
    play = probe.TARGETS["0x004bb450"]
    play_from_list = probe.TARGETS["0x004bb7e0"]
    selection = probe.TARGETS["0x004bb8c0"]
    assert_true("char * filename" in play["signature"], "filename parameter")
    assert_true("void * song_entry" in play_from_list["signature"], "song entry parameter")
    assert_true("int music_selection" in selection["signature"], "selection parameter")
    assert_true("source-parity" in selection["tags"], "selection source tag")


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
