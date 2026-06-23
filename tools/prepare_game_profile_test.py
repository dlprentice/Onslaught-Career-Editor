#!/usr/bin/env python3
"""Focused tests for the copied-profile preparation helper."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "prepare_game_profile.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell") or "powershell"


class PrepareGameProfileTests(unittest.TestCase):
    def run_helper(
        self,
        source_root: Path,
        output_root: Path,
        *,
        profile_name: str = "test-profile",
        executable_override: Path | None = None,
        print_only: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-SourceGameRoot",
            str(source_root),
            "-OutputRoot",
            str(output_root),
            "-ProfileName",
            profile_name,
        ]
        if executable_override is not None:
            command += ["-ExecutableOverridePath", str(executable_override)]
        if print_only:
            command.append("-PrintOnly")
        command[0] = POWERSHELL
        return subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def make_source_root(self, root: Path, *, include_exe: bool = False) -> None:
        (root / "data").mkdir()
        for name in ("defaultoptions.bea", "binkw32.dll", "ogg.dll", "vorbis.dll", "zlib.dll"):
            (root / name).write_bytes(f"{name}\n".encode("ascii"))
        if include_exe:
            (root / "BEA.exe").write_bytes(b"source-exe")

    def test_printonly_allows_clean_executable_override_without_source_exe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = base / "out"
            source.mkdir()
            self.make_source_root(source)
            clean_exe = source / "BEA.exe.original.backup"
            clean_exe.write_bytes(b"clean-exe")

            result = self.run_helper(source, output, executable_override=clean_exe)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["executableOverride"])
            exe_row = next(row for row in payload["entries"] if row["name"] == "BEA.exe")
            self.assertEqual(Path(exe_row["source"]), clean_exe.resolve())
            self.assertEqual(Path(exe_row["target"]).name, "BEA.exe")

    def test_copy_uses_executable_override_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = base / "out"
            source.mkdir()
            self.make_source_root(source, include_exe=True)
            clean_exe = source / "BEA.exe.original.backup"
            clean_exe.write_bytes(b"clean-exe")

            result = self.run_helper(source, output, executable_override=clean_exe, print_only=False)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            target_root = Path(payload["targetGameRoot"])
            self.assertEqual((target_root / "BEA.exe").read_bytes(), b"clean-exe")
            self.assertEqual((target_root / "defaultoptions.bea").read_bytes(), b"defaultoptions.bea\n")

    def test_rejects_output_root_inside_source_game_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = source / "profiles"
            source.mkdir()
            self.make_source_root(source, include_exe=True)

            result = self.run_helper(source, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("OutputRoot must not be inside the source game root", result.stderr)
            self.assertFalse(output.exists(), "Unsafe non-existent output directories must not be created.")

    def test_rejects_non_printonly_output_root_inside_source_before_creation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = source / "profiles"
            source.mkdir()
            self.make_source_root(source, include_exe=True)

            result = self.run_helper(source, output, print_only=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("OutputRoot must not be inside the source game root", result.stderr)
            self.assertFalse(output.exists(), "Rejected non-PrintOnly outputs must not be created before safety checks.")

    def test_rejects_source_game_root_inside_output_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            output = base / "profiles"
            source = output / "source"
            source.mkdir(parents=True)
            self.make_source_root(source, include_exe=True)

            result = self.run_helper(source, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SourceGameRoot must not be inside OutputRoot", result.stderr)

    def test_rejects_output_root_with_steam_bea_install_shape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = base / "steamapps" / "common" / "Battle Engine Aquila" / "profiles"
            source.mkdir()
            self.make_source_root(source, include_exe=True)

            result = self.run_helper(source, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("OutputRoot must not be under a steamapps/common/Battle Engine Aquila", result.stderr)
            self.assertIn("install root.", result.stderr)

    def test_rejects_executable_override_outside_source_game_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = base / "out"
            source.mkdir()
            self.make_source_root(source)
            clean_exe = base / "BEA.exe.original.backup"
            clean_exe.write_bytes(b"clean-exe")

            result = self.run_helper(source, output, executable_override=clean_exe)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ExecutableOverridePath must be inside SourceGameRoot", result.stderr)

    def test_rejects_unsupported_executable_override_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-profile-test-") as temp:
            base = Path(temp)
            source = base / "source"
            output = base / "out"
            source.mkdir()
            self.make_source_root(source)
            clean_exe = source / "patched-copy.exe"
            clean_exe.write_bytes(b"clean-exe")

            result = self.run_helper(source, output, executable_override=clean_exe)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ExecutableOverridePath must point to BEA.exe or BEA.exe.original.backup", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
