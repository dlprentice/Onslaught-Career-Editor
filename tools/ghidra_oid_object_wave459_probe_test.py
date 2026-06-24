#!/usr/bin/env python3
"""Self-tests for the Wave459 OID/object-init probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_oid_object_wave459_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_oid_object_wave459_probe", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_parse_summary() -> None:
    text = "SUMMARY updated=12 skipped=0 created=0 would_create=0 renamed=8 would_rename=0 missing=0 bad=0"
    parsed = probe.parse_summary(text)
    assert_true(parsed["updated"] == 12, "updated count")
    assert_true(parsed["renamed"] == 8, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 12, "target count")
    assert_true(("0x004bfa60", "0x004bf183", "OID__CreateObject") in probe.EXPECTED_XREF_EDGES, "target-data init xref")
    assert_true(("0x004bfd20", "0x004bf2d1", "OID__CreateObject") in probe.EXPECTED_XREF_EDGES, "base-object init xref")
    assert_true(("0x004bfde0", "0x005dc834", "<no_function>") in probe.EXPECTED_XREF_EDGES, "escape pod vtable xref")


def test_signature_and_comment_tokens() -> None:
    create = probe.TARGETS["0x004bf090"]
    shared = probe.TARGETS["0x004bfd00"]
    render = probe.TARGETS["0x004bfab0"]
    assert_true("int object_id" in create["signature"], "object id parameter")
    assert_true("byte flags" in shared["signature"], "shared destructor flags")
    assert_true("render state 0x1b" in render["commentTokens"], "render-state token")
    assert_true("oid-object-wave459" in shared["tags"], "wave tag")


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
