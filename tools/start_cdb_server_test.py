#!/usr/bin/env python3
"""Focused tests for the CDB attach helper safety gates."""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "start_cdb_server.ps1"
COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "defaultoptions-wave1.cdb.txt"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
CMD_EXE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class StartCdbServerTests(unittest.TestCase):
    def run_powershell(self, command: str) -> subprocess.CompletedProcess[str]:
        wrapped_command = (
            "$ErrorActionPreference = 'Stop'; "
            f"try {{ {command} }} catch {{ "
            "[Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
        )
        encoded_command = base64.b64encode(wrapped_command.encode("utf-16le")).decode("ascii")
        return subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-OutputFormat",
                "Text",
                "-EncodedCommand",
                encoded_command,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def ps_quote(self, value: str | Path) -> str:
        text = str(value)
        return "'" + text.replace("'", "''") + "'"

    def write_profile_manifest(self, profile_root: Path) -> None:
        (profile_root / "onslaught-profile-manifest.json").write_text(
            json.dumps(
                {
                    "schemaVersion": "winui-copied-game-profile.v1",
                    "mutation": True,
                    "targetGameRoot": ".",
                    "executablePath": "BEA.exe",
                }
            ),
            encoding="utf-8",
        )

    def write_malformed_profile_manifest(self, profile_root: Path) -> None:
        (profile_root / "onslaught-profile-manifest.json").write_text("{not-json", encoding="utf-8")

    def start_fake_copied_bea(self, profile_root: Path, *, manifest: bool = True) -> subprocess.Popen[bytes]:
        profile_root.mkdir(parents=True)
        shutil.copy2(CMD_EXE, profile_root / "BEA.exe")
        if manifest:
            self.write_profile_manifest(profile_root)

        process = subprocess.Popen(
            [str(profile_root / "BEA.exe"), "/c", "ping -n 30 127.0.0.1 > nul"],
            cwd=profile_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
        )
        time.sleep(0.25)
        return process

    def stop_process(self, process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return

        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            return

        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def build_safe_attach_command(
        self,
        *,
        process_id: int,
        app_root: Path,
        profile_root: Path,
        expected_executable: Path | None = None,
        log_path: Path | None = None,
        command_file: Path = COMMAND_FILE,
    ) -> str:
        expected_executable = expected_executable or (profile_root / "BEA.exe")
        command = (
            f"& {self.ps_quote(SCRIPT)} "
            "-ProcessName BEA.exe "
            f"-ProcessId {process_id} "
            f"-AppOwnedProfilesRoot {self.ps_quote(app_root)} "
            f"-ExpectedExecutablePath {self.ps_quote(expected_executable)} "
            f"-ExpectedWorkingDirectory {self.ps_quote(profile_root)} "
            f"-CommandFile {self.ps_quote(command_file)} "
        )
        if log_path is not None:
            command += f"-LogPath {self.ps_quote(log_path)} "
        return command + "-PrintOnly"

    def test_printonly_exact_pid_accepts_generated_copied_profile_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            profile = app_root / "safe-profile"
            process = self.start_fake_copied_bea(profile)
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("-p", result.stdout)
            self.assertIn(str(COMMAND_FILE), result.stdout)

    def test_rejects_exact_pid_without_app_owned_profile_proof(self) -> None:
        command = (
            "$proc = Get-Process -Id $PID; "
            f"& {self.ps_quote(SCRIPT)} "
            "-ProcessName ($proc.ProcessName + '.exe') "
            "-ProcessId $PID "
            f"-CommandFile {self.ps_quote(COMMAND_FILE)} "
            "-PrintOnly"
        )

        result = self.run_powershell(command)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires -AppOwnedProfilesRoot", result.stderr)

    def test_rejects_process_name_attach_without_explicit_legacy_switch(self) -> None:
        command = (
            f"& {self.ps_quote(SCRIPT)} "
            "-ProcessName BEA.exe "
            f"-CommandFile {self.ps_quote(COMMAND_FILE)} "
            "-PrintOnly"
        )

        result = self.run_powershell(command)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires -ProcessId", result.stderr)
        self.assertIn("AllowProcessNameAttach", result.stderr)

    def test_rejects_generated_profile_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            profile = app_root / "safe-profile"
            process = self.start_fake_copied_bea(profile, manifest=False)
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing generated copied-profile manifest", result.stderr)

    def test_rejects_generated_profile_malformed_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            profile = app_root / "safe-profile"
            process = self.start_fake_copied_bea(profile, manifest=False)
            self.write_malformed_profile_manifest(profile)
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("is not valid JSON", result.stderr)

    def test_rejects_generated_profile_under_steam_install_shape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            profile = app_root / "steamapps" / "common" / "Battle Engine Aquila" / "safe-profile"
            process = self.start_fake_copied_bea(profile)
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("installed/protected game root", result.stderr)

    def test_rejects_working_directory_outside_app_owned_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            app_root.mkdir()
            profile = Path(temp) / "outside-profile"
            process = self.start_fake_copied_bea(profile)
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be inside app-owned profiles root", result.stderr)

    def test_rejects_command_file_outside_default_probe_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            command_file = Path(temp) / "observer.cdb.txt"
            command_file.write_text(".echo test\n", encoding="utf-8")
            command = (
                f"& {self.ps_quote(SCRIPT)} "
                "-ProcessName BEA.exe "
                f"-CommandFile {self.ps_quote(command_file)} "
                "-PrintOnly"
            )

            result = self.run_powershell(command)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay under allowed command root", result.stderr)

    def test_printonly_does_not_create_log_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            profile = app_root / "safe-profile"
            missing_log_dir = Path(temp) / "missing-log-dir"
            log_path = missing_log_dir / "windbg.log"
            process = self.start_fake_copied_bea(profile)
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                        log_path=log_path,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(missing_log_dir.exists(), "PrintOnly should not create log directories.")

    def test_rejects_expected_executable_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-test-") as temp:
            app_root = Path(temp) / "profiles"
            profile = app_root / "safe-profile"
            process = self.start_fake_copied_bea(profile)
            wrong_exe = profile / "Wrong.exe"
            wrong_exe.write_bytes(b"not bea")
            try:
                result = self.run_powershell(
                    self.build_safe_attach_command(
                        process_id=process.pid,
                        app_root=app_root,
                        profile_root=profile,
                        expected_executable=wrong_exe,
                    )
                )
            finally:
                self.stop_process(process)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be the copied BEA.exe", result.stderr)

    def test_remote_server_requires_arm_phrase_and_non_default_password(self) -> None:
        missing_arm = (
            f"& {self.ps_quote(SCRIPT)} "
            "-ProcessName BEA.exe "
            f"-CommandFile {self.ps_quote(COMMAND_FILE)} "
            "-EnableRemoteServer "
            "-Password safer_token "
            "-PrintOnly"
        )
        missing_arm_result = self.run_powershell(missing_arm)
        self.assertNotEqual(missing_arm_result.returncode, 0)
        self.assertIn("Remote CDB server mode requires", missing_arm_result.stderr)

        default_password = (
            f"& {self.ps_quote(SCRIPT)} "
            "-ProcessName BEA.exe "
            f"-CommandFile {self.ps_quote(COMMAND_FILE)} "
            "-EnableRemoteServer "
            "-RemoteServerArmPhrase 'ALLOW CDB REMOTE SERVER' "
            "-Password secret "
            "-PrintOnly"
        )
        default_password_result = self.run_powershell(default_password)
        self.assertNotEqual(default_password_result.returncode, 0)
        self.assertIn("non-default", default_password_result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
