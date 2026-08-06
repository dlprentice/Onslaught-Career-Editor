#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for Gen25 open census instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_residual_gen25_open_census.py"
SPEC = importlib.util.spec_from_file_location("re_open_residual_gen25_open_census", TOOL)
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
PLATE = ROOT / "local-lab" / "open-residual-gen25-census-20260805-v1"
HAS_LAB = GEN25.is_dir() and SPECIMEN.is_file()

# Measured non-police full-cover recovery on Gen25 tip (MULTI_UNIT).
EXPECTED_MULTI_START = "0x005344fc"
EXPECTED_MULTI_BYTES = 212


class UnitTests(unittest.TestCase):
    def test_interior_pad_split_nop_int3_only(self) -> None:
        # body | 4×nop | body — need len>=12
        self.assertTrue(
            mod.interior_pad_split_candidate(
                b"\xE8\x00\x00\x00\x00" + b"\x90" * 4 + b"\xC3\x90\x90"
            )
        )
        self.assertTrue(
            mod.interior_pad_split_candidate(
                b"\x55\x8B\xEC" + b"\xCC" * 4 + b"\x5D\xC3\x90\x90\x90"
            )
        )
        self.assertFalse(mod.interior_pad_split_candidate(b"\x90\x90\x90"))
        self.assertFalse(
            mod.interior_pad_split_candidate(b"\x90" * 8)
        )  # no body both sides
        # bare zero runs are NOT pad delimiters (imm32 noise)
        self.assertFalse(
            mod.interior_pad_split_candidate(
                b"\xE8\x00\x00\x00\x00" + b"\x00" * 4 + b"\xC3\x90\x90"
            )
        )

    def test_constants(self) -> None:
        self.assertEqual(mod.EXPECTED_OPEN_DARK, 99)
        self.assertEqual(mod.EXPECTED_OPEN_EXECUTED, 4)
        self.assertEqual(mod.EXPECTED_RESIDUALS, 6117)


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabCensusTests(unittest.TestCase):
    def test_build_and_verify_ready_multi_plate(self) -> None:
        """Measured plate: READY with exactly one MULTI_UNIT proof; Gen25 unmutated."""
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
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], 1)
        self.assertEqual(pack["n_open_dark_input"], 99)
        self.assertEqual(pack["n_open_executed_input"], 4)
        self.assertEqual(pack["n_e8_inbound_dark_starts"], 0)
        self.assertTrue(pack.get("hold_generation_apply"))
        self.assertEqual(len(pack["proofs"]), 1)
        proof = pack["proofs"][0]
        self.assertEqual(proof["startVa"].lower(), EXPECTED_MULTI_START)
        self.assertEqual(int(proof["bytes"]), EXPECTED_MULTI_BYTES)
        self.assertEqual(proof["kind"], "MULTI_UNIT")
        self.assertEqual(proof["proposedTerminalState"], "TERMINAL_BOUNDED_AMBIGUITY")
        # police OFFSET_ENVELOPE reopens must not be the sole proof lane
        self.assertNotIn("OFFSET_ENVELOPE", proof["kind"])

        summary = json.loads((PLATE / "SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["formalPackStatus"], "READY_FOR_GENERATION")
        self.assertEqual(summary["counts"]["formalPackProofs"], 1)

        integrity = json.loads((PLATE / "INTEGRITY.json").read_text(encoding="utf-8"))
        self.assertTrue(integrity["checks"]["no_gen26_apply"])
        self.assertTrue(integrity["checks"]["gen25_unmutated"])

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
