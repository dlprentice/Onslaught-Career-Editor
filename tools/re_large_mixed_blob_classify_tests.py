#!/usr/bin/env python3
"""Tests for re_large_mixed_blob_classify.py."""

from __future__ import annotations

import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_large_mixed_blob_classify.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
DEEPER = ROOT / "local-lab" / "residual-open-mixed-deeper-20260804-v1" / "full.json"

sys.path.insert(0, str(ROOT / "tools"))
import re_large_mixed_blob_classify as lmb  # noqa: E402


class SyntheticSegmentTests(unittest.TestCase):
    def test_code_ptr_table_then_junk(self) -> None:
        ptrs = b"".join(struct.pack("<I", 0x005BE628 + i * 4) for i in range(8))
        blob = ptrs + b"\xff" * 40
        segs = lmb.segment_blob(0x005B4EB0, blob, None)
        self.assertEqual(segs[0]["kind"], "CODE_ADDRESS_TABLE")
        self.assertTrue(segs[0]["terminal"])
        self.assertGreaterEqual(segs[0]["bytes"], 32)

    def test_float_lut(self) -> None:
        floats = b"".join(struct.pack("<f", 0.05 * (i + 1)) for i in range(16))
        segs = lmb.segment_blob(0x500000, floats, None)
        self.assertEqual(segs[0]["kind"], "FLOAT32_LUT")
        self.assertTrue(segs[0]["terminal"])

    def test_int16_quant_like(self) -> None:
        # 80 int16 values in 1..200
        blob = b"".join(struct.pack("<h", (i % 50) + 1) for i in range(80))
        segs = lmb.segment_blob(0x500000, blob, None)
        kinds = [s["kind"] for s in segs]
        self.assertIn("INT16_QUANT_LIKE", kinds)

    def test_open_code_not_terminal(self) -> None:
        cs = lmb.try_capstone()
        if cs is None:
            self.skipTest("capstone missing")
        # ret-ending body so fragment is accepted without inventing a name
        code = bytes.fromhex("55 8B EC") + (b"\x90" * 40) + bytes.fromhex("33 C0 5D C3")
        segs = lmb.segment_blob(0x401000, code, cs)
        code_segs = [s for s in segs if s["kind"] == "OPEN_CODE_FRAGMENT"]
        self.assertTrue(code_segs)
        self.assertFalse(code_segs[0]["terminal"])

    def test_data_table_not_long_code_without_ct(self) -> None:
        # Dense non-prologue fill (no 0x55/0x8B/… starts) must not become long code.
        # Note: bytes(range(256)) intentionally contains every prologue byte and is
        # *not* a fair pure-data probe for this detector.
        blob = b"\xfe\xfd" * 512  # 1024B
        segs = lmb.segment_blob(0x005C9E59, blob, lmb.try_capstone())
        long_code = [
            s
            for s in segs
            if s["kind"] == "OPEN_CODE_FRAGMENT" and s["bytes"] > 128
        ]
        self.assertEqual(long_code, [])


@unittest.skipUnless(SPECIMEN.is_file() and DEEPER.is_file(), "local evidence missing")
class LiveLargeMixedTests(unittest.TestCase):
    def test_live_classify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "out.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--specimen",
                    str(SPECIMEN),
                    "--deeper-full-json",
                    str(DEEPER),
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
            self.assertIn("LARGE_MIXED_BLOB_CLASSIFY_OK", completed.stdout)
            payload = json.loads(
                completed.stdout.split("LARGE_MIXED_BLOB_CLASSIFY_OK")[0].strip()
            )
            self.assertEqual(
                "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                payload["specimen_sha256"],
            )
            self.assertGreaterEqual(payload["n_spans"], 10)
            self.assertTrue(payload["capstone"])
            # Must account some structure without claiming all open bytes closed
            self.assertGreater(payload["terminal_bytes_accounted"] + payload["open_bytes_remaining"], 0)
            # Code fragments must appear on this JPEG/math frontier (non-terminal)
            kinds = payload.get("segment_kind_counts") or {}
            self.assertGreater(kinds.get("OPEN_CODE_FRAGMENT", 0), 0)
            # Pure invented-name free: no kind implies a function name
            for k in kinds:
                self.assertNotIn("FUN_", k)
                self.assertNotIn("CFast", k)


if __name__ == "__main__":
    unittest.main()
