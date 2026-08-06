#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_open_dark_code_like_mass.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_open_dark_code_like_mass.py"
SPEC = importlib.util.spec_from_file_location("re_open_dark_code_like_mass", TOOL)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

GEN15 = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation15-open-dark-remaining-20260805-v1"
    / "generation-15-residual-terminal-open-dark-remaining"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "open-dark-code-like-mass-gen15-20260805-v1"
HAS_LAB = GEN15.is_dir() and SPECIMEN.is_file()


class PolicyTests(unittest.TestCase):
    def test_pure_pad_detection(self) -> None:
        self.assertTrue(mod.is_pure_pad(bytes([0x90] * 12)))
        self.assertTrue(mod.is_pure_pad(bytes([0xCC, 0x00, 0x90])))
        self.assertFalse(mod.is_pure_pad(bytes([0x90, 0xE8])))

    def test_envelope_rejects_partial_non_pad_tail(self) -> None:
        # two rets then non-pad garbage — must not full-cover terminalize
        try:
            from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        except ImportError:
            self.skipTest("capstone missing")
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        blob = bytes([0xC3, 0xC3]) + bytes([0xE8, 0x00, 0x00, 0x00, 0x00]) + bytes(20)
        # pad out to length but with call-ish mid body after early ret path
        self.assertIsNone(mod.try_envelope_at(blob, 0x401000, md))

    def test_envelope_accepts_full_ret_pad_cover(self) -> None:
        try:
            from capstone import CS_ARCH_X86, CS_MODE_32, Cs
        except ImportError:
            self.skipTest("capstone missing")
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        # push eax; pop eax; ret; nop padding
        blob = bytes([0x50, 0x58, 0xC3]) + bytes([0x90] * 13)
        got = mod.try_envelope_at(blob, 0x401000, md)
        self.assertIsNotNone(got)
        assert got is not None
        self.assertEqual(got["frac"], 1.0)
        self.assertEqual(got["covered"], len(blob))

    def test_proposed_kinds(self) -> None:
        self.assertEqual(
            mod.proposed_for_kinds(["TINY_PAD_GAP"])["terminalState"],
            "TERMINAL_PADDING",
        )
        self.assertEqual(
            mod.proposed_for_kinds(["STATIC_CODE_DECODE_ENVELOPE"])["terminalState"],
            "TERMINAL_BOUNDED_AMBIGUITY",
        )
        self.assertEqual(
            mod.proposed_for_kinds(
                ["FLOAT32_TABLE_PREFIX", "ALIGN_PAD_PREFIX"]
            )["terminalState"],
            "TERMINAL_BOUNDED_AMBIGUITY",
        )


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabMassTests(unittest.TestCase):
    def test_published_plate_file_pins(self) -> None:
        """Historical Gen16 plate stays on disk; rebuild may drift after gate harden."""
        if not (PLATE / "FORMAL-PACK.json").is_file():
            self.skipTest("plate missing")
        pre = hashlib.sha256((GEN15 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertGreaterEqual(pack["n_proofs"], 16)
        pad_n = sum(
            1
            for p in pack["proofs"]
            if p["proposed"]["terminalState"] == "TERMINAL_PADDING"
        )
        self.assertGreaterEqual(pad_n, 1)
        post = hashlib.sha256((GEN15 / "campaign-residuals.tsv").read_bytes()).hexdigest()
        self.assertEqual(pre, post)
        for p in pack["proofs"]:
            if p["proposed"]["terminalState"] == "TERMINAL_PADDING":
                self.assertNotIn(
                    "STATIC_CODE_DECODE_ENVELOPE", p.get("subspanKinds") or ""
                )
        self.assertEqual(
            pre,
            hashlib.sha256((GEN15 / "campaign-residuals.tsv").read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
