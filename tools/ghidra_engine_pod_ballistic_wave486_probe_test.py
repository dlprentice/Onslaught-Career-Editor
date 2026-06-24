#!/usr/bin/env python3
"""Tests for the Wave486 engine/pod/ballistic probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_engine_pod_ballistic_wave486_probe as probe


class EnginePodBallisticWave486ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.txt"
            path.write_text(
                "updated=4 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            self.assertEqual(
                probe.parse_summary(path),
                {
                    "updated": 4,
                    "skipped": 0,
                    "created": 0,
                    "would_create": 0,
                    "renamed": 1,
                    "would_rename": 0,
                    "missing": 0,
                    "bad": 0,
                },
            )

    def test_compact_token_present(self) -> None:
        text = "void __fastcall CUnit__ComputeBallisticLaunchVelocity(void *this)"
        self.assertTrue(probe.token_present(text, "void __fastcall CUnit__ComputeBallisticLaunchVelocity(void * this)"))

    def test_stale_name_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "post-decomp").mkdir()
            for address, target in probe.TARGETS.items():
                (base / "post-decomp" / f"{address[2:]}_{target['name']}.c").write_text(
                    target["decompile_tokens"][0],
                    encoding="utf-8",
                )
            stale_path = base / "post-decomp" / f"{probe.CPOD_SLOT66[2:]}_{probe.TARGETS[probe.CPOD_SLOT66]['name']}.c"
            stale_path.write_text(
                "void __fastcall CPod__VFunc_66_UpdateMotionAndAccumulateScalar(void *this) { CEngine__AdvanceAndAccumulateMotionScalar(this); }",
                encoding="utf-8",
            )
            failures: list[str] = []
            probe.check_decompile(base, failures)
            self.assertTrue(any("stale decompile token" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
