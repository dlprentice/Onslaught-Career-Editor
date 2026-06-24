#!/usr/bin/env python3
"""Self-tests for the Wave452 render/sort static-reaudit probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_render_sort_wave452_probe.py"
spec = importlib.util.spec_from_file_location("ghidra_render_sort_wave452_probe", MODULE_PATH)
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
    assert_true(parsed["renamed"] == 0, "renamed count")
    assert_true(parsed["bad"] == 0, "bad count")


def test_expected_targets_and_edges() -> None:
    assert_true(len(probe.TARGETS) == 8, "target count")
    assert_true(("0x004b5250", "CHudComponent__RenderPassEntry") in probe.EXPECTED_XREF_EDGES, "cycle scalar HUD edge")
    assert_true(("0x004b52c0", "CMeshRenderer__RenderMeshCore") in probe.EXPECTED_XREF_EDGES, "sort key renderer core edge")
    assert_true(("0x004b6350", "CMeshPart__RenderAnimatedRecursive") in probe.EXPECTED_XREF_EDGES, "render mesh meshpart edge")


def test_signature_and_deferral_tokens() -> None:
    cycle = probe.TARGETS["0x004b5250"]
    renderer = probe.TARGETS["0x004b6350"]
    recursive = probe.TARGETS["0x004b5ad0"]
    sphere = probe.TARGETS["0x004b6260"]
    assert_true("float cycle_scalar" in cycle["signature"], "cycle scalar parameter")
    assert_true("byte render_flags" in renderer["signature"], "render flags parameter")
    assert_true("signature-deferred" in recursive["tags"], "meshpart recursive deferral tag")
    assert_true("signature-deferred" in sphere["tags"], "sphere recursive deferral tag")


def test_live_probe_passes() -> None:
    status, failures = probe.run_checks(probe.BASE)
    assert_true(status == "PASS", f"live probe status {status}: {failures}")


def main() -> int:
    tests = [
        test_parse_summary,
        test_expected_targets_and_edges,
        test_signature_and_deferral_tokens,
        test_live_probe_passes,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
