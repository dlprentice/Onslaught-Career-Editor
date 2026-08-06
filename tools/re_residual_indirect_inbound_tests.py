#!/usr/bin/env python3
"""Tests for re_residual_indirect_inbound.py."""

from __future__ import annotations

import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_residual_indirect_inbound.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
GEN10 = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
    / "campaign-functions.tsv"
)
SPANS = (
    ROOT
    / "local-lab"
    / "function-envelope-open-islands-20260804-v1"
    / "spans.json"
)

sys.path.insert(0, str(ROOT / "tools"))
import re_residual_indirect_inbound as rii  # noqa: E402


class DecodeModrmTests(unittest.TestCase):
    def test_disp32_call(self) -> None:
        # FF 15 xx xx xx xx  = CALL [disp32]
        disp = 0x00655000
        raw = bytes([0xFF, 0x15]) + struct.pack("<I", disp)
        # fake: data buffer = raw only; rawptr=0, base_va=0x401000
        data = raw
        dec = rii.decode_modrm_mem(data, 0, 0, 0x401000, 0x400000)
        self.assertIsNotNone(dec)
        self.assertEqual(dec["kind"], "CALL")
        self.assertEqual(dec["form"], "disp32")
        self.assertEqual(dec["operandVa"], disp)
        self.assertEqual(dec["siteVa"], 0x401000)

    def test_call_reg_form(self) -> None:
        # FF D0 = CALL eax
        data = bytes([0xFF, 0xD0])
        dec = rii.decode_modrm_mem(data, 0, 0, 0x401000, 0x400000)
        self.assertIsNotNone(dec)
        self.assertEqual(dec["form"], "reg")
        self.assertIsNone(dec["operandVa"])


@unittest.skipUnless(
    SPECIMEN.is_file() and GEN10.is_file() and SPANS.is_file(),
    "local evidence missing",
)
class LiveIndirectInboundTests(unittest.TestCase):
    def test_live_three_spans(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "out.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--specimen",
                    str(SPECIMEN),
                    "--spans-json",
                    str(SPANS),
                    "--gen10-functions-tsv",
                    str(GEN10),
                    "--json-out",
                    str(out),
                    "--summary-only",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertIn("RESIDUAL_INDIRECT_INBOUND_OK", completed.stdout)
            payload = json.loads(
                completed.stdout.split("RESIDUAL_INDIRECT_INBOUND_OK")[0].strip()
            )
            self.assertEqual(
                "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                payload["specimen_sha256"],
            )
            self.assertEqual(3, payload["n_spans"])
            self.assertGreater(payload["ff_rm_scan"]["n_ff_rm_ops"], 100)
            by = {s["startVa"]: s for s in payload["spanSummaries"]}
            # Absolute ptrs previously measured into these spans must still appear
            self.assertGreaterEqual(by["0x005b8e9e"]["absolutePtrCountIntoSpan"], 1)
            self.assertGreaterEqual(by["0x005ad820"]["absolutePtrCountIntoSpan"], 1)
            # Block-coeff entry 0x005adb60 was known to have 1 abs ptr
            grades = {
                c["entryVa"]: c["grade"]
                for c in by["0x005ad820"]["candidateGrades"]
            }
            if "0x005adb60" in grades:
                self.assertIn(
                    grades["0x005adb60"],
                    ("ABS_PTR_ONLY", "INDIRECT_CALL_TARGET"),
                )
            # No invented names in output
            blob = json.dumps(payload)
            self.assertNotIn("FUN_NEW_", blob)


if __name__ == "__main__":
    unittest.main()
