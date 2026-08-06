#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_hresult_tostring_static.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"


class HResultToStringStaticTests(unittest.TestCase):
    @unittest.skipUnless(SPECIMEN.is_file(), "pristine specimen missing")
    def test_static_mapper_extracts_required_pairs_and_21_callers(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--specimen", str(SPECIMEN)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("HRESULT_TOSTRING_STATIC_PASS", completed.stdout)
        payload = json.loads(
            completed.stdout.split("HRESULT_TOSTRING_STATIC_PASS")[0].strip()
        )
        self.assertEqual(21, payload["n_call_sites"])
        self.assertGreaterEqual(payload["n_string_pairs"], 400)
        self.assertEqual(46657, payload["body_bytes"])
        self.assertEqual("c20400", payload["ret4_bytes"])
        self.assertEqual(
            "CODE_ADDRESS_TABLE_PREFIX", payload["post_body_table"]["kind"]
        )
        self.assertGreaterEqual(
            payload["post_body_table"]["pure_code_ptr_prefix_dwords"], 100
        )
        # Required semantic pins
        by = {c["hresult"]: c for c in payload["required_pair_checks"]}
        self.assertTrue(by["0x88760868"]["ok"])
        self.assertTrue(by["0x88760869"]["ok"])
        self.assertTrue(by["0x80004004"]["ok"])


if __name__ == "__main__":
    unittest.main()
