#!/usr/bin/env python3
"""Focused tests for the CDB attach helper safety gates."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
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
    ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

    def run_powershell(self, command: str) -> subprocess.CompletedProcess[str]:
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
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

    def normalized_stderr(self, result: subprocess.CompletedProcess[str]) -> str:
        tokens = self.ANSI_ESCAPE.sub("", result.stderr).split()
        return " ".join(token for token in tokens if token != "|")

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

    def write_runtime_receipt(
        self,
        profile_root: Path,
        process: subprocess.Popen[bytes],
        command_file: Path,
        *,
        started_at: str | None = None,
    ) -> tuple[Path, str, str]:
        identity_result = self.run_powershell(
            f"$p = Get-Process -Id {process.pid} -ErrorAction Stop; $p.Refresh(); "
            "[PSCustomObject]@{ "
            "startedAtUtc = $p.StartTime.ToUniversalTime().ToString('o'); "
            "modulePath = [System.IO.Path]::GetFullPath($p.MainModule.FileName); "
            "moduleBaseAddressHex = ('0x{0:X}' -f $p.MainModule.BaseAddress.ToInt64()); "
            "moduleSize = [int64]$p.MainModule.ModuleMemorySize "
            "} | ConvertTo-Json -Compress"
        )
        self.assertEqual(identity_result.returncode, 0, identity_result.stderr)
        identity = json.loads(identity_result.stdout)
        executable = profile_root / "BEA.exe"
        manifest = profile_root / "onslaught-profile-manifest.json"
        executable_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
        command_hash = hashlib.sha256(command_file.read_bytes()).hexdigest()
        payload = {
            "schemaVersion": "runtime-process-receipt.v1",
            "runId": "synthetic-cdb-test",
            "process": {
                "id": process.pid,
                "startedAtUtc": started_at or identity["startedAtUtc"],
                "executable": {
                    "path": str(executable.resolve()),
                    "sha256": executable_hash,
                    "size": executable.stat().st_size,
                },
                "workingDirectory": str(profile_root.resolve()),
                "launchArguments": ["/c", "ping -n 30 127.0.0.1 > nul"],
            },
            "profileManifest": {
                "path": str(manifest.resolve()),
                "sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                "size": manifest.stat().st_size,
            },
            "window": {"hwndHex": "0x0"},
            "module": {
                "path": identity["modulePath"],
                "baseAddressHex": identity["moduleBaseAddressHex"],
                "size": identity["moduleSize"],
            },
            "sourceExecutableSha256": executable_hash,
            "copiedExecutableSha256": executable_hash,
            "commandTemplateSha256": "a" * 64,
            "generatedCommandSha256": command_hash,
        }
        receipt = profile_root / "runtime-process-receipt.v1.json"
        receipt.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        return receipt, hashlib.sha256(receipt.read_bytes()).hexdigest(), command_hash

    def build_canary_command(
        self,
        *,
        receipt: Path,
        receipt_sha256: str,
        command_file: Path,
        command_sha256: str,
        allowed_command_root: Path,
        extra_args: str = "",
    ) -> str:
        command = (
            f"& {self.ps_quote(SCRIPT)} "
            f"-RuntimeReceiptPath {self.ps_quote(receipt)} "
            f"-ExpectedReceiptSha256 {receipt_sha256} "
            f"-CommandFile {self.ps_quote(command_file)} "
            f"-ExpectedCommandSha256 {command_sha256} "
            "-RequiredLogMarker MORPH_CANARY_READY "
            f"-AllowedCommandRoot {self.ps_quote(allowed_command_root)} "
        )
        if extra_args:
            command += f"{extra_args} "
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
            self.assertIn("must be inside app-owned profiles root", self.normalized_stderr(result))

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
            self.assertIn("must stay under allowed command root", self.normalized_stderr(result))

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
            self.assertIn("must be the copied BEA.exe", self.normalized_stderr(result))

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

    def test_canary_printonly_validates_receipt_and_adds_local_safety_flags(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-canary-test-") as temp:
            root = Path(temp)
            profile = root / "profiles" / "safe-profile"
            command_file = root / "commands" / "canary.cdb.txt"
            command_file.parent.mkdir()
            command_file.write_text(".echo MORPH_CANARY_READY\n", encoding="utf-8")
            process = self.start_fake_copied_bea(profile)
            try:
                receipt, receipt_hash, command_hash = self.write_runtime_receipt(
                    profile, process, command_file
                )
                result = self.run_powershell(
                    self.build_canary_command(
                        receipt=receipt,
                        receipt_sha256=receipt_hash,
                        command_file=command_file,
                        command_sha256=command_hash,
                        allowed_command_root=command_file.parent,
                    )
                )
            finally:
                self.stop_process(process)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-pd", result.stdout)
        self.assertIn("-noshell", result.stdout)
        self.assertNotIn("-server", result.stdout)

    def test_canary_printonly_rejects_stale_receipt_start_time(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-canary-test-") as temp:
            root = Path(temp)
            profile = root / "profiles" / "safe-profile"
            command_file = root / "commands" / "canary.cdb.txt"
            command_file.parent.mkdir()
            command_file.write_text(".echo MORPH_CANARY_READY\n", encoding="utf-8")
            process = self.start_fake_copied_bea(profile)
            try:
                receipt, receipt_hash, command_hash = self.write_runtime_receipt(
                    profile,
                    process,
                    command_file,
                    started_at="2000-01-01T00:00:00.0000000Z",
                )
                result = self.run_powershell(
                    self.build_canary_command(
                        receipt=receipt,
                        receipt_sha256=receipt_hash,
                        command_file=command_file,
                        command_sha256=command_hash,
                        allowed_command_root=command_file.parent,
                    )
                )
            finally:
                self.stop_process(process)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("start time", result.stderr.lower())

    def test_canary_requires_all_receipt_command_and_marker_inputs(self) -> None:
        parameter_names = (
            "RuntimeReceiptPath",
            "ExpectedReceiptSha256",
            "ExpectedCommandSha256",
            "RequiredLogMarker",
        )
        for missing in parameter_names:
            with self.subTest(missing=missing):
                arguments = {
                    "RuntimeReceiptPath": "missing-receipt.json",
                    "ExpectedReceiptSha256": "a" * 64,
                    "ExpectedCommandSha256": "b" * 64,
                    "RequiredLogMarker": "MORPH_CANARY_READY",
                }
                del arguments[missing]
                rendered = " ".join(
                    f"-{name} {self.ps_quote(value)}" for name, value in arguments.items()
                )
                result = self.run_powershell(
                    f"& {self.ps_quote(SCRIPT)} {rendered} -PrintOnly"
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("requires", result.stderr.lower())

    def test_canary_rejects_command_digest_drift_and_remote_server(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-canary-test-") as temp:
            root = Path(temp)
            profile = root / "profiles" / "safe-profile"
            command_file = root / "commands" / "canary.cdb.txt"
            command_file.parent.mkdir()
            command_file.write_text(".echo MORPH_CANARY_READY\n", encoding="utf-8")
            process = self.start_fake_copied_bea(profile)
            try:
                receipt, receipt_hash, command_hash = self.write_runtime_receipt(
                    profile, process, command_file
                )
                digest_result = self.run_powershell(
                    self.build_canary_command(
                        receipt=receipt,
                        receipt_sha256=receipt_hash,
                        command_file=command_file,
                        command_sha256="0" * 64,
                        allowed_command_root=command_file.parent,
                    )
                )
                remote_result = self.run_powershell(
                    self.build_canary_command(
                        receipt=receipt,
                        receipt_sha256=receipt_hash,
                        command_file=command_file,
                        command_sha256=command_hash,
                        allowed_command_root=command_file.parent,
                        extra_args=(
                            "-EnableRemoteServer "
                            "-RemoteServerArmPhrase 'ALLOW CDB REMOTE SERVER' "
                            "-Password safer_token"
                        ),
                    )
                )
            finally:
                self.stop_process(process)

        self.assertNotEqual(digest_result.returncode, 0)
        self.assertIn("command sha-256", digest_result.stderr.lower())
        self.assertNotEqual(remote_result.returncode, 0)
        self.assertIn("remote", remote_result.stderr.lower())

    @unittest.skipUnless(os.name == "nt", "junction test requires Windows")
    def test_canary_rejects_command_path_through_reparse_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-canary-test-") as temp:
            root = Path(temp)
            profile = root / "profiles" / "safe-profile"
            real_commands = root / "commands" / "real"
            alias_commands = root / "commands" / "alias"
            real_commands.mkdir(parents=True)
            command_file = real_commands / "canary.cdb.txt"
            command_file.write_text(".echo MORPH_CANARY_READY\n", encoding="utf-8")
            junction = subprocess.run(
                [str(CMD_EXE), "/c", "mklink", "/J", str(alias_commands), str(real_commands)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(junction.returncode, 0, junction.stderr)
            aliased_command = alias_commands / command_file.name
            process = self.start_fake_copied_bea(profile)
            try:
                receipt, receipt_hash, command_hash = self.write_runtime_receipt(
                    profile, process, command_file
                )
                result = self.run_powershell(
                    self.build_canary_command(
                        receipt=receipt,
                        receipt_sha256=receipt_hash,
                        command_file=aliased_command,
                        command_sha256=command_hash,
                        allowed_command_root=root / "commands",
                    )
                )
            finally:
                self.stop_process(process)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reparse", result.stderr.lower())

    def test_canary_marker_readiness_and_result_identity_are_explicit(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        for token in (
            "$RequiredLogMarker",
            "requiredLogMarkerFound",
            "cdbStartedAtUtc",
            "cdbExecutablePath",
            "targetReceiptSha256",
            "commandSha256",
        ):
            self.assertIn(token, script)
        self.assertIn("-SimpleMatch", script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
