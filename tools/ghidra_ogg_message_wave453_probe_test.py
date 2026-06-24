#!/usr/bin/env python3
"""Self-tests for the Wave453 Ogg/message static-reaudit probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_ogg_message_wave453_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_ogg_message_wave453_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=5 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 5, "updated count")
    assert_true(parsed["renamed"] == 0, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 5, "target count")
    assert_true(("0x004b6cd0", "COggLoader__readerSubobject_scalar_deleting_dtor") in probe.EXPECTED_XREF_EDGES, "reader dtor edge")
    assert_true(("0x004b6d90", "<no_function>") in probe.EXPECTED_XREF_EDGES, "vtable edge")
    assert_true(("0x004b6e50", "IScript__PlaySoundWithFadeAndPriority") in probe.EXPECTED_XREF_EDGES, "mission script message edge")


def test_signature_and_tag_tokens() -> None:
    ctor = probe.TARGETS["0x004b6d30"]
    reader_dtor = probe.TARGETS["0x004b6df0"]
    message_ctor = probe.TARGETS["0x004b6e50"]
    assert_true("COggLoader__ctor_base" in ctor["signature"], "ogg ctor name")
    assert_true("void * this, byte flags" in reader_dtor["signature"], "scalar deleting this/flags")
    assert_true("short * message_text" in message_ctor["signature"], "message text parameter")
    assert_true("constructor" in message_ctor["tags"], "message constructor tag")


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
