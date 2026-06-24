#!/usr/bin/env python3
"""Focused tests for bounded BEA window capture helper guards."""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "capture_game_window.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell") or "powershell"


class CaptureGameWindowTests(unittest.TestCase):
    def ps_quote(self, value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def script_text(self) -> str:
        return SCRIPT.read_text(encoding="utf-8")

    def test_capture_artifact_records_z_order_occlusion_metadata(self) -> None:
        text = self.script_text()

        self.assertIn("Get-ZOrderOcclusionPayload", text)
        self.assertIn("occlusion = $occlusionPayload", text)
        self.assertIn("visualProof = $visualProof", text)
        self.assertIn("visualProofReason = $visualProofReason", text)
        self.assertIn("z-order-occlusion-free", text)
        self.assertIn("minimumOccluderOverlapArea", text)
        self.assertIn("tinyOverlappingWindows", text)

    def run_helper(self, extra_args: str = "", output_name: str = "capture.png") -> subprocess.CompletedProcess[str]:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_path = Path(temp_dir.name) / output_name
        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            "-ProcessId 1 "
            "-HwndHex 0x1 "
            f"-OutputPath {self.ps_quote(str(output_path))}"
        )
        if extra_args:
            command += f" {extra_args}"

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

    def test_real_capture_requires_allowed_output_root(self) -> None:
        result = self.run_helper()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AllowedOutputRoot", result.stderr)

    def test_output_path_must_be_png(self) -> None:
        result = self.run_helper(output_name="capture.jpg")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OutputPath must end in .png", result.stderr)

    def test_real_capture_requires_expected_copied_game_identity_after_allowed_root(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_path = Path(temp_dir.name) / "capture.png"
        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            "-ProcessId 1 "
            "-HwndHex 0x1 "
            f"-OutputPath {self.ps_quote(str(output_path))} "
            f"-AllowedOutputRoot {self.ps_quote(temp_dir.name)}"
        )
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        result = subprocess.run(
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

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ExpectedExecutablePath and ExpectedWorkingDirectory", result.stderr)

    def test_real_capture_requires_source_game_root_after_identity(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        copied_root = root / "CopiedGame"
        output_root = root / "Evidence"
        copied_root.mkdir()
        output_root.mkdir()
        copied_exe = copied_root / "BEA.exe"
        copied_exe.write_bytes(b"MZ")
        output_path = output_root / "capture.png"
        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            "-ProcessId 1 "
            "-HwndHex 0x1 "
            f"-OutputPath {self.ps_quote(str(output_path))} "
            f"-AllowedOutputRoot {self.ps_quote(str(output_root))} "
            f"-ExpectedExecutablePath {self.ps_quote(str(copied_exe))} "
            f"-ExpectedWorkingDirectory {self.ps_quote(str(copied_root))}"
        )
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        result = subprocess.run(
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

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SourceGameRoot", result.stderr)

    def test_real_capture_rejects_output_root_overlapping_source_game_root(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        source_root = root / "SourceGame"
        copied_root = root / "CopiedGame"
        source_root.mkdir()
        copied_root.mkdir()
        copied_exe = copied_root / "BEA.exe"
        copied_exe.write_bytes(b"MZ")
        output_path = source_root / "capture.png"
        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            "-ProcessId 1 "
            "-HwndHex 0x1 "
            f"-OutputPath {self.ps_quote(str(output_path))} "
            f"-AllowedOutputRoot {self.ps_quote(str(source_root))} "
            f"-ExpectedExecutablePath {self.ps_quote(str(copied_exe))} "
            f"-ExpectedWorkingDirectory {self.ps_quote(str(copied_root))} "
            f"-SourceGameRoot {self.ps_quote(str(source_root))}"
        )
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        result = subprocess.run(
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

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("read-only source game root", result.stderr)

    @unittest.skipUnless(os.name == "nt", "hardlink guard is Windows-specific")
    def test_allow_overwrite_rejects_existing_hardlinked_output_before_capture(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        output_root = root / "Evidence"
        output_root.mkdir()
        outside_file = root / "outside.bin"
        outside_file.write_bytes(b"outside bytes")
        output_path = output_root / "capture.png"
        os.link(outside_file, output_path)

        command = (
            f"& {self.ps_quote(str(SCRIPT))} "
            "-ProcessId 1 "
            "-HwndHex 0x1 "
            f"-OutputPath {self.ps_quote(str(output_path))} "
            f"-AllowedOutputRoot {self.ps_quote(str(output_root))} "
            f"-ExpectedExecutablePath {self.ps_quote(str(root / 'CopiedGame' / 'BEA.exe'))} "
            f"-ExpectedWorkingDirectory {self.ps_quote(str(root / 'CopiedGame'))} "
            f"-SourceGameRoot {self.ps_quote(str(root / 'SourceGame'))} "
            "-AllowOverwrite"
        )
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        result = subprocess.run(
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

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardlinked", result.stderr.lower())
        self.assertEqual(outside_file.read_bytes(), b"outside bytes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
