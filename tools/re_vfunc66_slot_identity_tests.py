#!/usr/bin/env python3
"""Unit tests for re_vfunc66_slot_identity.py (uses real pristine specimen)."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_vfunc66_slot_identity.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"


class Vfunc66SlotIdentityTests(unittest.TestCase):
    @unittest.skipUnless(SPECIMEN.is_file(), "pristine specimen not present")
    def test_pristine_specimen_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--specimen", str(SPECIMEN)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("VFUNC66_SLOT_IDENTITY_PASS", completed.stdout)
        payload = json.loads(
            completed.stdout.split("VFUNC66_SLOT_IDENTITY_PASS")[0].strip()
        )
        self.assertEqual("PASS", payload["status"])
        self.assertEqual("0x4d8e40", payload["cround_slot66_target"])
        self.assertEqual("0x4081c0", payload["cbattleengine_slot66_target"])
        self.assertEqual("OPEN", payload["source_spelling"]["status"])

    @unittest.skipUnless(SPECIMEN.is_file(), "pristine specimen not present")
    def test_json_out_and_poisoned_byte_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            json_out = tmp_path / "out.json"
            good = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--specimen",
                    str(SPECIMEN),
                    "--json-out",
                    str(json_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, good.returncode, good.stdout + good.stderr)
            self.assertTrue(json_out.is_file())

            # Poison: flip one byte of the callsite so the mechanical check fails.
            poisoned = tmp_path / "poisoned.exe"
            data = bytearray(SPECIMEN.read_bytes())
            # File offset of VA 0x401AEA under identity-mapped .text for this PE:
            # section raw = rva for this build (measured: body off == rva).
            # Safer: locate the unique callsite bytes and flip the last byte.
            needle = bytes.fromhex("ff9208010000")
            idx = data.find(needle)
            self.assertNotEqual(-1, idx)
            data[idx + 5] ^= 0x01
            poisoned.write_bytes(data)
            bad = subprocess.run(
                [sys.executable, str(SCRIPT), "--specimen", str(poisoned)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, bad.returncode, bad.stdout + bad.stderr)
            self.assertIn("FAIL", bad.stderr)


if __name__ == "__main__":
    unittest.main()
