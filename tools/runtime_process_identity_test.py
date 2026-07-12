#!/usr/bin/env python3
"""Focused tests for runtime-process-receipt.v1 validation."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "runtime_process_identity.psm1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
CMD_EXE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"
WOW64_CMD_EXE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "SysWOW64" / "cmd.exe"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def ps_quote(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def run_powershell(command: str, *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
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
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_receipt(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return sha256_file(path)


class CopiedCmdFixture:
    """One bounded copied cmd.exe process and its synthetic private receipt."""

    def __init__(
        self,
        root: Path,
        *,
        source_executable: Path = CMD_EXE,
        profile_name: str = "safe-profile",
    ) -> None:
        self.root = root
        self.profile_root = root / "profiles" / profile_name
        self.profile_root.mkdir(parents=True)
        self.executable = self.profile_root / "BEA.exe"
        shutil.copy2(source_executable, self.executable)
        self.manifest = self.profile_root / "onslaught-profile-manifest.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "schemaVersion": "winui-copied-game-profile.v1",
                    "mutation": True,
                    "targetGameRoot": ".",
                    "executablePath": "BEA.exe",
                },
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )
        self.launch_arguments = ["/c", "ping -n 30 127.0.0.1 > nul"]
        self.processes: list[subprocess.Popen[bytes]] = []
        self.process = self.start_process()

    def start_process(self, *, cwd: Path | None = None) -> subprocess.Popen[bytes]:
        process = subprocess.Popen(
            [str(self.executable), *self.launch_arguments],
            cwd=cwd or self.profile_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
        )
        self.processes.append(process)
        time.sleep(0.25)
        if process.poll() is not None:
            raise RuntimeError(f"copied cmd.exe fixture exited with {process.returncode}")
        return process

    def stop_process(self, process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

    def stop(self) -> None:
        for process in reversed(self.processes):
            self.stop_process(process)

    def current_identity(self) -> dict[str, Any]:
        command = (
            f"$p = Get-Process -Id {self.process.pid} -ErrorAction Stop; "
            "$p.Refresh(); "
            "[PSCustomObject]@{ "
            "startedAtUtc = $p.StartTime.ToUniversalTime().ToString('o'); "
            "modulePath = [System.IO.Path]::GetFullPath($p.MainModule.FileName); "
            "moduleBaseAddressHex = ('0x{0:X}' -f $p.MainModule.BaseAddress.ToInt64()); "
            "moduleSize = [int64]$p.MainModule.ModuleMemorySize "
            "} | ConvertTo-Json -Compress"
        )
        result = run_powershell(command)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        return json.loads(result.stdout)

    def receipt_payload(self) -> dict[str, Any]:
        identity = self.current_identity()
        executable_sha256 = sha256_file(self.executable)
        return {
            "schemaVersion": "runtime-process-receipt.v1",
            "runId": "synthetic-runtime-process-test",
            "process": {
                "id": self.process.pid,
                "startedAtUtc": identity["startedAtUtc"],
                "executable": {
                    "path": str(self.executable.resolve()),
                    "sha256": executable_sha256,
                    "size": self.executable.stat().st_size,
                },
                "workingDirectory": str(self.profile_root.resolve()),
                "launchArguments": self.launch_arguments,
            },
            "profileManifest": {
                "path": str(self.manifest.resolve()),
                "sha256": sha256_file(self.manifest),
                "size": self.manifest.stat().st_size,
            },
            "window": {"hwndHex": "0x0"},
            "module": {
                "path": identity["modulePath"],
                "baseAddressHex": identity["moduleBaseAddressHex"],
                "size": identity["moduleSize"],
            },
            "sourceExecutableSha256": executable_sha256,
            "copiedExecutableSha256": executable_sha256,
            "commandTemplateSha256": "a" * 64,
            "generatedCommandSha256": "b" * 64,
        }


class RuntimeProcessIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="runtime-receipt-test-")
        self.root = Path(self.temp_dir.name)
        self.fixture = CopiedCmdFixture(self.root)

    def tearDown(self) -> None:
        self.fixture.stop()
        self.temp_dir.cleanup()

    def assert_receipt(
        self,
        payload: dict[str, Any],
        *,
        expected_sha256: str | None = None,
        receipt_path: Path | None = None,
        require_window: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        receipt_path = receipt_path or (self.root / "runtime-process-receipt.v1.json")
        actual_sha256 = write_receipt(receipt_path, payload)
        expected_sha256 = expected_sha256 or actual_sha256
        command = (
            f"Import-Module {ps_quote(MODULE)} -Force; "
            f"$validated = Assert-RuntimeProcessReceipt -ReceiptPath {ps_quote(receipt_path)} "
            f"-ExpectedReceiptSha256 {ps_quote(expected_sha256)}"
        )
        if require_window:
            command += " -RequireWindow"
        command += (
            "; [PSCustomObject]@{ "
            "schemaVersion = $validated.Receipt.schemaVersion; "
            "processId = $validated.Process.Id; "
            "propertyCount = @($validated.PSObject.Properties).Count "
            "} | ConvertTo-Json -Compress"
        )
        return run_powershell(command)

    def assert_rejected(self, payload: dict[str, Any], message: str, **kwargs: Any) -> None:
        result = self.assert_receipt(payload, **kwargs)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message.lower(), result.stderr.lower())

    def test_accepts_exact_matching_receipt_and_returns_only_receipt_and_process(self) -> None:
        result = self.assert_receipt(self.fixture.receipt_payload())

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["schemaVersion"], "runtime-process-receipt.v1")
        self.assertEqual(output["processId"], self.fixture.process.pid)
        self.assertEqual(output["propertyCount"], 2)

    @unittest.skipUnless(WOW64_CMD_EXE.exists(), "32-bit cmd.exe fixture is unavailable")
    def test_accepts_wow64_process_working_directory_identity(self) -> None:
        self.fixture.stop()
        self.fixture = CopiedCmdFixture(
            self.root,
            source_executable=WOW64_CMD_EXE,
            profile_name="wow64-profile",
        )

        result = self.assert_receipt(self.fixture.receipt_payload())

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_schema_name_and_exact_key_drift(self) -> None:
        wrong_schema = self.fixture.receipt_payload()
        wrong_schema["schemaVersion"] = "runtime-process-receipt.v2"
        self.assert_rejected(wrong_schema, "schema")

        extra_key = self.fixture.receipt_payload()
        extra_key["unexpected"] = True
        self.assert_rejected(extra_key, "exact keys")

        missing_key = self.fixture.receipt_payload()
        del missing_key["runId"]
        self.assert_rejected(missing_key, "exact keys")

        wrong_key_case = self.fixture.receipt_payload()
        wrong_key_case["SchemaVersion"] = wrong_key_case.pop("schemaVersion")
        self.assert_rejected(wrong_key_case, "exact keys")

        nested_extra_key = self.fixture.receipt_payload()
        nested_extra_key["process"]["executable"]["unexpected"] = True
        self.assert_rejected(nested_extra_key, "exact keys")

    def test_rejects_receipt_hash_mismatch(self) -> None:
        self.assert_rejected(
            self.fixture.receipt_payload(),
            "receipt sha-256",
            expected_sha256="0" * 64,
        )

    def test_rejects_pid_reuse_start_time_mismatch(self) -> None:
        payload = self.fixture.receipt_payload()
        payload["process"]["startedAtUtc"] = "2000-01-01T00:00:00.0000000Z"
        self.assert_rejected(payload, "start time")

    def test_rejects_executable_path_hash_and_size_drift(self) -> None:
        cases = {
            "path": str(CMD_EXE.resolve()),
            "sha256": "0" * 64,
            "size": self.fixture.executable.stat().st_size + 1,
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                payload = self.fixture.receipt_payload()
                payload["process"]["executable"][field] = value
                self.assert_rejected(payload, f"executable {field}")

    def test_rejects_manifest_path_hash_and_size_drift(self) -> None:
        cases = {
            "path": str(self.fixture.executable.resolve()),
            "sha256": "0" * 64,
            "size": self.fixture.manifest.stat().st_size + 1,
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                payload = self.fixture.receipt_payload()
                payload["profileManifest"][field] = value
                if field == "path":
                    payload["profileManifest"]["sha256"] = sha256_file(self.fixture.executable)
                    payload["profileManifest"]["size"] = self.fixture.executable.stat().st_size
                self.assert_rejected(payload, f"manifest {field}")

    def test_rejects_working_directory_and_launch_argument_drift(self) -> None:
        payload = self.fixture.receipt_payload()
        payload["process"]["workingDirectory"] = str(self.root.resolve())
        self.assert_rejected(payload, "working directory")

        payload = self.fixture.receipt_payload()
        payload["process"]["launchArguments"] = ["/c", "exit 0"]
        self.assert_rejected(payload, "launch arguments")

    def test_rejects_live_process_working_directory_drift(self) -> None:
        self.fixture.stop_process(self.fixture.process)
        self.fixture.process = self.fixture.start_process(cwd=self.root)
        payload = self.fixture.receipt_payload()

        self.assert_rejected(payload, "live process working directory")

    def test_rejects_module_path_base_and_size_drift(self) -> None:
        cases = {
            "path": str(CMD_EXE.resolve()),
            "baseAddressHex": "0x1",
            "size": self.fixture.receipt_payload()["module"]["size"] + 1,
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                payload = self.fixture.receipt_payload()
                payload["module"][field] = value
                self.assert_rejected(payload, f"module {field}")

    def test_rejects_source_copy_and_command_digest_drift(self) -> None:
        cases = {
            "sourceExecutableSha256": "0" * 64,
            "copiedExecutableSha256": "0" * 64,
            "commandTemplateSha256": "not-a-sha256",
            "generatedCommandSha256": "not-a-sha256",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                payload = self.fixture.receipt_payload()
                payload[field] = value
                self.assert_rejected(payload, field)

    def test_rejects_second_process_using_the_same_executable_path(self) -> None:
        payload = self.fixture.receipt_payload()
        self.fixture.start_process()
        self.assert_rejected(payload, "multiple running processes")

    def test_require_window_rejects_hwnd_ownership_mismatch(self) -> None:
        payload = self.fixture.receipt_payload()
        payload["window"]["hwndHex"] = "0x1"
        self.assert_rejected(payload, "window", require_window=True)

    @unittest.skipUnless(os.name == "nt", "junction test requires Windows")
    def test_rejects_receipt_path_through_reparse_directory(self) -> None:
        real_directory = self.root / "real-receipt"
        alias_directory = self.root / "receipt-alias"
        receipt_path = real_directory / "runtime-process-receipt.v1.json"
        payload = self.fixture.receipt_payload()
        digest = write_receipt(receipt_path, payload)
        junction = subprocess.run(
            [str(CMD_EXE), "/c", "mklink", "/J", str(alias_directory), str(real_directory)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(junction.returncode, 0, junction.stderr)

        result = self.assert_receipt(
            payload,
            expected_sha256=digest,
            receipt_path=alias_directory / receipt_path.name,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("reparse", result.stderr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
