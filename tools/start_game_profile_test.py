#!/usr/bin/env python3
"""Focused tests for the copied-profile launch helper argument allowlist."""

from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "start_game_profile.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell") or "powershell"


class StartGameProfileTests(unittest.TestCase):
    def ps_quote(self, value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def run_helper(self, game_root: Path, arguments: str) -> subprocess.CompletedProcess[str]:
        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            f"-GameRoot {self.ps_quote(str(game_root))} "
            f"-Arguments {self.ps_quote(arguments)} "
            "-PrintOnly"
        )
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        return subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-EncodedCommand",
                encoded_command,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_real_helper(self, game_root: Path, arguments: str) -> subprocess.CompletedProcess[str]:
        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            f"-GameRoot {self.ps_quote(str(game_root))} "
            f"-Arguments {self.ps_quote(arguments)}"
        )
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        return subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-EncodedCommand",
                encoded_command,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def with_fake_game_root(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        game_root = Path(temp_dir.name)
        (game_root / "BEA.exe").write_bytes(b"")
        return game_root

    def test_allows_numeric_level_for_copied_profile_probe(self) -> None:
        result = self.run_helper(self.with_fake_game_root(), "-skipfmv -level 710")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-skipfmv -level 710", result.stdout)

    def test_allows_bounded_controller_configuration_for_copied_profile_probe(self) -> None:
        result = self.run_helper(self.with_fake_game_root(), "-skipfmv -configuration 2")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-skipfmv -configuration 2", result.stdout)

    def test_rejects_out_of_range_controller_configuration(self) -> None:
        result = self.run_helper(self.with_fake_game_root(), "-configuration 5")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("-configuration requires a controller configuration between 1 and 4", result.stderr)

    def test_rejects_non_numeric_level(self) -> None:
        result = self.run_helper(self.with_fake_game_root(), "-level cloak")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("-level requires a numeric mission", result.stderr)

    def test_rejects_missing_level_value(self) -> None:
        result = self.run_helper(self.with_fake_game_root(), "-skipfmv -level")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("-level requires a numeric mission", result.stderr)

    def test_rejects_unallowlisted_retail_debug_flags(self) -> None:
        result = self.run_helper(self.with_fake_game_root(), "-devmode")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported launch argument", result.stderr)
        self.assertIn("-devmode", result.stderr)

    def test_real_start_is_retired(self) -> None:
        result = self.run_real_helper(self.with_fake_game_root(), "-skipfmv")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Direct launch through tools/start_game_profile.ps1 is retired", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
