#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen25 residual-split compose instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen25_residual_split.py"
SPEC = importlib.util.spec_from_file_location(
    "re_open_residual_gen25_residual_split", TOOL
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN25 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation25-police-reopen-20260805-v1"
    / "generation-25-residual-terminal-police-reopen"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-residual-gen25-residual-split-20260805-v1"
HAS_LAB = GEN25.is_dir() and SPECIMEN.is_file()


class SegmentUnitTests(unittest.TestCase):
    def test_find_pad_split_requires_interior_nop(self) -> None:
        body = b"\x55\x8B\xEC\xC3" + b"\x90" * 4 + b"\x33\xC0\xC3"
        segs = mod.find_pad_split_segments(body)
        self.assertIsNotNone(segs)
        assert segs is not None
        self.assertGreaterEqual(len(segs), 3)
        self.assertTrue(any(k == "PAD" for k, _, __ in segs))

    def test_zero_runs_are_not_pad_delimiters(self) -> None:
        body = b"\x55\x8B\xEC\xC3" + b"\x00" * 4 + b"\x33\xC0\xC3"
        self.assertIsNone(mod.find_pad_split_segments(body))

    def test_compose_synthetic_pad_between_pads(self) -> None:
        """BODY pure-pad | PAD nops | BODY pure-pad is not dual body — use envelopes."""

        class Mass:
            @staticmethod
            def is_pure_pad(blob: bytes) -> bool:
                return bool(blob) and all(b in (0x00, 0x90, 0xCC) for b in blob)

            @staticmethod
            def try_envelope_at(blob, base, md):
                return None

        class Inb:
            @staticmethod
            def is_full_align_nop_run(blob: bytes) -> bool:
                return False

        class Reject:
            def multi_unit_pack(self, *a, **k):
                return None

            def compose_data_shape(self, *a, **k):
                return None

            def compose_partial_data(self, *a, **k):
                return None

            def compose_small_table(self, *a, **k):
                return None

        # two pure-pad bodies with interior nops: each body classifies as PAD_BODY
        blob = b"\x90\x90" + b"\x90" * 4 + b"\xCC\xCC"
        # wait — pure pad whole residual would not have BODY segments
        # use non-pad body that is_pure_pad false but we force classify via multi
        reject = Reject()

        def multi_ok(part, base, md, mass, **k):
            if len(part) >= 2 and part[0] == 0x55:
                return {"lane": "MULTI_UNIT_CODE_PACK", "n_code": 2}
            return None

        mu = types.SimpleNamespace(multi_unit_pack=multi_ok)
        left = b"\x55\xC3"
        right = b"\x55\xC3"
        blob = left + b"\x90" * 4 + right
        rec = mod.compose_residual_split(
            blob,
            0x401000,
            None,
            Mass(),
            Inb(),
            reject,
            reject,
            reject,
            reject,
            mu,
        )
        self.assertIsNotNone(rec)
        assert rec is not None
        self.assertEqual(rec["lane"], "RESIDUAL_PAD_SPLIT")
        self.assertEqual(rec["n_pad_segments"], 1)
        self.assertIn("MULTI_UNIT", rec["kinds"])


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabResidualSplitTests(unittest.TestCase):
    def test_build_verify_empty_or_ready_hold_apply(self) -> None:
        pre = hashlib.sha256((GEN25 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        rc = mod.main(
            [
                "build",
                "--campaign",
                str(GEN25),
                "--specimen",
                str(SPECIMEN),
                "--out",
                str(PLATE),
            ]
        )
        self.assertEqual(rc, 0)
        post = hashlib.sha256((GEN25 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertIn(pack["status"], {"EMPTY", "READY_FOR_GENERATION"})
        self.assertTrue(pack.get("hold_generation_apply"))
        self.assertEqual(pack["n_open_dark_input"], 99)
        self.assertEqual(pack["n_open_executed_input"], 4)
        # Measured expectation: no full-cover 90/CC split on Gen25 open mass
        self.assertEqual(pack["status"], "EMPTY")
        self.assertEqual(pack["n_proofs"], 0)
        rc2 = mod.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--campaign",
                str(GEN25),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc2, 0)
        post2 = hashlib.sha256((GEN25 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post2)


if __name__ == "__main__":
    unittest.main()
