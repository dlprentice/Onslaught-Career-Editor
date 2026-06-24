#!/usr/bin/env python3
"""Tests for the DirectInput deadzone byte-export checker."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "winui_directinput_deadzone_byte_export_check.py"


class DirectInputDeadzoneByteExportCheckTests(unittest.TestCase):
    def test_checker_self_test_passes(self) -> None:
        self.assertTrue(CHECKER.is_file(), "checker is missing")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
