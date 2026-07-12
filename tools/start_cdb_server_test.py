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
TEST_CDB_ARM = "ALLOW TEST-ONLY CDB EXECUTABLE"

FAKE_CDB_SOURCE = r'''
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading;

public static class FakeCdb {
    private static string ArgumentValue(string[] args, string name) {
        for (int index = 0; index + 1 < args.Length; index++) {
            if (String.Equals(args[index], name, StringComparison.OrdinalIgnoreCase)) {
                return args[index + 1];
            }
        }
        return null;
    }

    public static int Main(string[] args) {
        string logPath = ArgumentValue(args, "-logo");
        string commandPath = ArgumentValue(args, "-cf");
        if (String.IsNullOrEmpty(logPath) || String.IsNullOrEmpty(commandPath)) {
            return 21;
        }

        var directives = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (string line in File.ReadAllLines(commandPath)) {
            int separator = line.IndexOf('=');
            if (separator > 0) {
                directives[line.Substring(0, separator)] = line.Substring(separator + 1);
            }
        }
        string mode = directives.ContainsKey("MODE") ? directives["MODE"] : "EXACT";
        string marker = directives.ContainsKey("MARKER") ? directives["MARKER"] : "MORPH_CANARY_READY";
        if (directives.ContainsKey("PIDFILE")) {
            File.WriteAllText(directives["PIDFILE"], Process.GetCurrentProcess().Id.ToString());
        }

        if (String.Equals(mode, "MUTATE", StringComparison.OrdinalIgnoreCase)) {
            File.AppendAllText(directives["MUTATE_PATH"], "drift");
        }

        if (String.Equals(mode, "OVERSIZE", StringComparison.OrdinalIgnoreCase)) {
            using (var stream = new FileStream(logPath, FileMode.CreateNew, FileAccess.Write, FileShare.ReadWrite)) {
                stream.SetLength((16L * 1024L * 1024L) + 1L);
                stream.Flush(true);
            }
        } else if (String.Equals(mode, "ECHO_ONLY", StringComparison.OrdinalIgnoreCase)) {
            File.WriteAllText(logPath, ".echo " + marker + Environment.NewLine);
        } else if (String.Equals(mode, "LOCK", StringComparison.OrdinalIgnoreCase)) {
            bool writeDenied = false;
            bool deleteDenied = false;
            try {
                using (var stream = new FileStream(commandPath, FileMode.Open, FileAccess.Write, FileShare.ReadWrite)) { }
            } catch (IOException) {
                writeDenied = true;
            } catch (UnauthorizedAccessException) {
                writeDenied = true;
            }
            try {
                File.Delete(commandPath);
                deleteDenied = File.Exists(commandPath);
            } catch (IOException) {
                deleteDenied = true;
            } catch (UnauthorizedAccessException) {
                deleteDenied = true;
            }
            File.WriteAllLines(logPath, new [] {
                writeDenied ? "WRITE_DENIED" : "WRITE_ALLOWED",
                deleteDenied ? "DELETE_DENIED" : "DELETE_ALLOWED",
                writeDenied && deleteDenied ? "  " + marker + "  " : "LOCK_FAILED"
            });
        } else {
            File.WriteAllText(logPath, "  " + marker + "  " + Environment.NewLine);
        }

        Thread.Sleep(30000);
        return 0;
    }
}
'''


class StartCdbServerTests(unittest.TestCase):
    ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

    @staticmethod
    def run_powershell(command: str) -> subprocess.CompletedProcess[str]:
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

    @classmethod
    def setUpClass(cls) -> None:
        cls.fake_temp = tempfile.TemporaryDirectory(prefix="fake-cdb-executable-")
        fake_root = Path(cls.fake_temp.name)
        source_path = fake_root / "FakeCdb.cs"
        cls.fake_cdb = fake_root / "FakeCdb.exe"
        source_path.write_text(FAKE_CDB_SOURCE, encoding="utf-8")
        framework_root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Microsoft.NET"
        compiler_candidates = [
            framework_root / "Framework64" / "v4.0.30319" / "csc.exe",
            framework_root / "Framework" / "v4.0.30319" / "csc.exe",
        ]
        compiler = next((path for path in compiler_candidates if path.is_file()), None)
        if compiler is None:
            raise RuntimeError("Could not find the .NET Framework C# compiler for fake CDB tests")
        compile_result = subprocess.run(
            [str(compiler), "/nologo", f"/out:{cls.fake_cdb}", str(source_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(f"Could not compile fake CDB: {compile_result.stderr}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fake_temp.cleanup()

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

    def stop_pid(self, process_id: int) -> None:
        subprocess.run(
            ["taskkill", "/PID", str(process_id), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    def process_is_running(self, process_id: int) -> bool:
        result = self.run_powershell(
            f"if (Get-Process -Id {process_id} -ErrorAction SilentlyContinue) {{ exit 0 }} else {{ exit 1 }}"
        )
        return result.returncode == 0

    def parse_result_json(self, result: subprocess.CompletedProcess[str]) -> dict[str, object]:
        json_lines = [line for line in result.stdout.splitlines() if line.strip().startswith("{")]
        self.assertTrue(json_lines, result.stdout)
        return json.loads(json_lines[-1])

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
        log_path: Path | None = None,
        fake_cdb_path: Path | None = None,
        print_only: bool = True,
        timeout_milliseconds: int = 5000,
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
            f"-LogReadyTimeoutMilliseconds {timeout_milliseconds} "
        )
        if log_path is not None:
            command += f"-LogPath {self.ps_quote(log_path)} "
        if fake_cdb_path is not None:
            command += (
                f"-TestOnlyCdbExecutablePath {self.ps_quote(fake_cdb_path)} "
                f"-TestOnlyCdbExecutableArm {self.ps_quote(TEST_CDB_ARM)} "
            )
        if extra_args:
            command += f"{extra_args} "
        if print_only:
            command += "-PrintOnly"
        return command

    def run_fake_canary(
        self,
        root: Path,
        mode: str,
        *,
        stale_log: bool = False,
        mutate_path: Path | None = None,
        timeout_milliseconds: int = 1200,
    ) -> tuple[subprocess.CompletedProcess[str], subprocess.Popen[bytes], Path, Path, Path]:
        profile = root / "profiles" / "safe-profile"
        command_file = root / "commands" / "canary.cdb.txt"
        command_file.parent.mkdir(parents=True)
        log_path = root / "logs" / "canary.log"
        log_path.parent.mkdir(parents=True)
        pid_file = root / "fake-cdb.pid"
        directives = [
            f"MODE={mode}",
            "MARKER=MORPH_CANARY_READY",
            f"PIDFILE={pid_file}",
        ]
        if mutate_path is not None:
            directives.append(f"MUTATE_PATH={mutate_path}")
        command_file.write_text("\n".join(directives) + "\n", encoding="utf-8")
        if stale_log:
            log_path.write_text("MORPH_CANARY_READY\n", encoding="utf-8")
        target = self.start_fake_copied_bea(profile)
        receipt, receipt_hash, command_hash = self.write_runtime_receipt(
            profile, target, command_file
        )
        result = self.run_powershell(
            self.build_canary_command(
                receipt=receipt,
                receipt_sha256=receipt_hash,
                command_file=command_file,
                command_sha256=command_hash,
                allowed_command_root=command_file.parent,
                log_path=log_path,
                fake_cdb_path=self.fake_cdb,
                print_only=False,
                timeout_milliseconds=timeout_milliseconds,
            )
        )
        return result, target, command_file, log_path, pid_file

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

    def test_test_only_cdb_path_requires_exact_arm_and_canary_mode(self) -> None:
        missing_arm = self.run_powershell(
            f"& {self.ps_quote(SCRIPT)} -TestOnlyCdbExecutablePath {self.ps_quote(self.fake_cdb)} -PrintOnly"
        )
        wrong_arm = self.run_powershell(
            f"& {self.ps_quote(SCRIPT)} -TestOnlyCdbExecutablePath {self.ps_quote(self.fake_cdb)} "
            "-TestOnlyCdbExecutableArm 'WRONG' -PrintOnly"
        )

        self.assertNotEqual(missing_arm.returncode, 0)
        self.assertIn("test-only", missing_arm.stderr.lower())
        self.assertNotEqual(wrong_arm.returncode, 0)
        self.assertIn("test-only", wrong_arm.stderr.lower())

    def test_canary_rejects_stale_log_before_starting_fake_cdb(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-fake-stale-") as temp:
            result, target, _, _, pid_file = self.run_fake_canary(
                Path(temp), "EXACT", stale_log=True
            )
            try:
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("already exists", result.stderr.lower())
                self.assertFalse(pid_file.exists(), "fake CDB must not start for a stale log")
            finally:
                self.stop_process(target)

    def test_canary_requires_exact_trimmed_marker_line_not_command_echo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-fake-marker-") as temp:
            root = Path(temp)
            echo_result, echo_target, _, echo_log, echo_pid_file = self.run_fake_canary(
                root / "echo", "ECHO_ONLY", timeout_milliseconds=700
            )
            echo_pid: int | None = None
            try:
                echo_pid = int(echo_pid_file.read_text(encoding="utf-8"))
                self.assertNotEqual(echo_result.returncode, 0)
                self.assertIn("required log marker", echo_result.stderr.lower())
                self.assertIn(".echo MORPH_CANARY_READY", echo_log.read_text(encoding="utf-8"))
                self.assertFalse(self.process_is_running(echo_pid), "failed fake CDB must be cleaned up")
            finally:
                self.stop_process(echo_target)
                if echo_pid is not None and self.process_is_running(echo_pid):
                    self.stop_pid(echo_pid)

            exact_result, exact_target, _, exact_log, exact_pid_file = self.run_fake_canary(
                root / "exact", "EXACT"
            )
            exact_pid: int | None = None
            try:
                exact_pid = int(exact_pid_file.read_text(encoding="utf-8"))
                self.assertEqual(exact_result.returncode, 0, exact_result.stderr)
                payload = self.parse_result_json(exact_result)
                self.assertEqual(payload["status"], "marker-ready")
                self.assertTrue(payload["requiredLogMarkerFound"])
                self.assertEqual(Path(str(payload["cdbExecutablePath"])), self.fake_cdb.resolve())
                self.assertTrue(str(payload["cdbStartedAtUtc"]).endswith("Z"))
                self.assertEqual(
                    [line.strip() for line in exact_log.read_text(encoding="utf-8").splitlines()],
                    ["MORPH_CANARY_READY"],
                )
            finally:
                self.stop_process(exact_target)
                if exact_pid is not None and self.process_is_running(exact_pid):
                    self.stop_pid(exact_pid)

    def test_canary_holds_verified_command_read_lock_through_marker(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-fake-lock-") as temp:
            result, target, command_file, log_path, pid_file = self.run_fake_canary(
                Path(temp), "LOCK"
            )
            fake_pid: int | None = None
            try:
                fake_pid = int(pid_file.read_text(encoding="utf-8"))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(command_file.exists())
                lines = {line.strip() for line in log_path.read_text(encoding="utf-8").splitlines()}
                self.assertIn("WRITE_DENIED", lines)
                self.assertIn("DELETE_DENIED", lines)
                self.assertIn("MORPH_CANARY_READY", lines)
            finally:
                self.stop_process(target)
                if fake_pid is not None and self.process_is_running(fake_pid):
                    self.stop_pid(fake_pid)

    def test_canary_bounded_log_read_rejects_16_mib_plus_sentinel_and_cleans_up(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-fake-bound-") as temp:
            result, target, _, log_path, pid_file = self.run_fake_canary(
                Path(temp), "OVERSIZE"
            )
            fake_pid: int | None = None
            try:
                fake_pid = int(pid_file.read_text(encoding="utf-8"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("16 mib", result.stderr.lower())
                self.assertGreater(log_path.stat().st_size, 16 * 1024 * 1024)
                self.assertFalse(self.process_is_running(fake_pid), "oversize-log fake CDB must be cleaned up")
            finally:
                self.stop_process(target)
                if fake_pid is not None and self.process_is_running(fake_pid):
                    self.stop_pid(fake_pid)

    def test_canary_post_marker_receipt_rejection_cleans_exact_fake_cdb(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bea-cdb-fake-post-marker-") as temp:
            root = Path(temp)
            manifest = root / "profiles" / "safe-profile" / "onslaught-profile-manifest.json"
            result, target, _, _, pid_file = self.run_fake_canary(
                root, "MUTATE", mutate_path=manifest
            )
            fake_pid: int | None = None
            try:
                fake_pid = int(pid_file.read_text(encoding="utf-8"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("identity changed", result.stderr.lower())
                self.assertFalse(self.process_is_running(fake_pid), "post-marker failure must clean exact fake CDB")
            finally:
                self.stop_process(target)
                if fake_pid is not None and self.process_is_running(fake_pid):
                    self.stop_pid(fake_pid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
