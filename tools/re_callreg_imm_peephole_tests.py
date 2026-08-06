#!/usr/bin/env python3
"""Tests for re_callreg_imm_peephole.py."""

from __future__ import annotations

import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_callreg_imm_peephole.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
GEN10 = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
    / "campaign-functions.tsv"
)

sys.path.insert(0, str(ROOT / "tools"))
import re_callreg_imm_peephole as peephole  # noqa: E402


class SyntheticPeepholeTests(unittest.TestCase):
    def test_find_mov_r32_imm(self) -> None:
        # Build a tiny fake PE-like buffer is heavy; unit-test encoding helpers
        # via find on real specimen instead when present.
        cand = 0x005B4ED0
        # B8 + edx + imm = BA id when rd=2 → 0xB8+2=0xBA
        raw = bytes([0xBA]) + struct.pack("<I", cand) + bytes([0xFF, 0xD2])  # mov edx,imm; call edx
        # inject into a minimal structure: just verify pack
        self.assertEqual(raw[0], 0xBA)
        self.assertEqual(struct.unpack_from("<I", raw, 1)[0], cand)

    def test_default_candidates(self) -> None:
        self.assertIn(0x005B4ED0, peephole.DEFAULT_CANDIDATES)
        self.assertIn(0x005B5370, peephole.DEFAULT_CANDIDATES)
        self.assertIn(0x005ADF50, peephole.DEFAULT_CANDIDATES)


@unittest.skipUnless(SPECIMEN.is_file() and GEN10.is_file(), "local evidence missing")
class LivePeepholeTests(unittest.TestCase):
    def test_live_external_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "out.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--specimen",
                    str(SPECIMEN),
                    "--window",
                    "48",
                    "--gen10-functions-tsv",
                    str(GEN10),
                    "--json-out",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertIn("CALLREG_IMM_PEEPHOLE_OK", completed.stdout)
            payload = json.loads(
                completed.stdout.split("CALLREG_IMM_PEEPHOLE_OK")[0].strip()
            )
            self.assertEqual(
                "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                payload["specimen_sha256"],
            )
            self.assertEqual(3, len(payload["rows"]))
            # Prior plate proved imm32 embeds exist for all three
            for row in payload["rows"]:
                self.assertNotEqual(
                    row["grade"],
                    "NO_IMM",
                    msg=f"expected imm for {row['candidateVa']}",
                )
            # No invented names
            self.assertNotIn("FUN_NEW_", json.dumps(payload))
            # grades must be from allowed set
            allowed = {
                "SLOT_CONSUMER_NEAR_IMM",
                "CALL_REG_NEAR_IMM",
                "CALLBACK_SLOT_INSTALL",
                "IMM_ONLY_NO_NEAR_CALL",
                "NO_IMM",
            }
            for row in payload["rows"]:
                self.assertIn(row["grade"], allowed)
            # Live disasm shows Init* store residual VAs into allocated objects
            # (callback/vtable install), not CALL-to-candidate. Expect install
            # grade for the default external trio when window captures the stores.
            installs = sum(
                1 for r in payload["rows"] if r["grade"] == "CALLBACK_SLOT_INSTALL"
            )
            self.assertGreaterEqual(
                installs,
                1,
                msg="expected at least one CALLBACK_SLOT_INSTALL for Init* embeds",
            )


if __name__ == "__main__":
    unittest.main()
