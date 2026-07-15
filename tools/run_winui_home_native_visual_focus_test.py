#!/usr/bin/env python3
"""Tests for the fail-closed native Home visual/focus acceptance runner."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

import run_winui_home_native_visual_focus as harness


PNG_SIGNATURE = bytes((137, 80, 78, 71, 13, 10, 26, 10))


def write_png(path: Path, width: int, height: int) -> None:
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + (b"\x20\x34\x9a\xff" * width) for _ in range(height))
    payload = (
        PNG_SIGNATURE
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def write_trx(path: Path, *, total: int = 1, passed: int = 1, not_executed: int = 0, outcome: str = "Passed") -> None:
    root = ET.Element("TestRun")
    results = ET.SubElement(root, "Results")
    ET.SubElement(
        results,
        "UnitTestResult",
        {
            "testName": harness.TEST_METHOD_NAME,
            "outcome": outcome,
        },
    )
    summary = ET.SubElement(root, "ResultSummary", {"outcome": "Completed"})
    ET.SubElement(
        summary,
        "Counters",
        {
            "total": str(total),
            "executed": str(total - not_executed),
            "passed": str(passed),
            "failed": "0",
            "error": "0",
            "timeout": "0",
            "aborted": "0",
            "inconclusive": "0",
            "notExecuted": str(not_executed),
        },
    )
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


class HomeNativeVisualFocusRunnerTests(unittest.TestCase):
    HARNESS_RUN_ID = "a" * 32

    def test_commands_pin_debug_win_x64(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            test_command = harness.native_test_command(root, root / "result.trx")

        for command in (harness.WINUI_BUILD_COMMAND, test_command):
            self.assertIn("--configuration", command)
            self.assertEqual("Debug", command[command.index("--configuration") + 1])
            self.assertIn("--runtime", command)
            self.assertEqual("win-x64", command[command.index("--runtime") + 1])

    def test_trx_requires_exactly_one_executed_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trx = Path(temp_dir) / "result.trx"
            write_trx(trx)

            summary = harness.validate_trx(trx)

        self.assertEqual(1, summary["total"])
        self.assertEqual(1, summary["passed"])

    def test_trx_rejects_skip_even_when_no_failure_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trx = Path(temp_dir) / "result.trx"
            write_trx(trx, total=1, passed=0, not_executed=1, outcome="NotExecuted")

            with self.assertRaisesRegex(harness.HarnessError, "exactly one executed passing test"):
                harness.validate_trx(trx)

    def test_manifest_requires_full_identity_mapping_and_capture_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)

            summary = harness.validate_manifest(manifest, root, self.HARNESS_RUN_ID)

        self.assertEqual(4, summary["captureCount"])
        self.assertEqual(["first-run", "ready"], summary["states"])

    def test_manifest_rejects_pid_only_focus_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["FocusReceipts"][0]["Identity"]["ProcessStartTimeUtc"] = "2026-07-15T04:20:00Z"
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(harness.HarnessError, "full launch identity"):
                harness.validate_manifest(manifest, root)

    def test_manifest_rejects_stale_or_tampered_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            (manifest.parent / "ready-760.png").write_bytes(b"tampered")

            with self.assertRaisesRegex(harness.HarnessError, "capture hash"):
                harness.validate_manifest(manifest, root)

    def test_failed_invocation_cleanup_removes_only_owned_accepted_and_partial_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            evidence_root = repo / "local-lab" / "winui-home-native-visual-focus"
            other_id = "b" * 32
            other_run = evidence_root / f"home-newcomer-20260715T000000000Z-{other_id}"
            owned_run = evidence_root / f"home-newcomer-20260715T000000001Z-{self.HARNESS_RUN_ID}"
            owned_partial = evidence_root / f".home-newcomer-20260715T000000002Z-{self.HARNESS_RUN_ID}.partial"
            other_run.mkdir(parents=True)
            owned_run.mkdir()
            owned_partial.mkdir()

            harness.remove_failed_invocation_evidence(
                self.HARNESS_RUN_ID,
                evidence_root,
                repo_root=repo,
            )

            self.assertTrue(other_run.is_dir())
            self.assertFalse(owned_run.exists())
            self.assertFalse(owned_partial.exists())

    def test_failed_invocation_cleanup_rejects_untrusted_token(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_root = Path(temp_dir) / "evidence"
            evidence_root.mkdir()

            with self.assertRaisesRegex(harness.HarnessError, "invocation ID is invalid"):
                harness.remove_failed_invocation_evidence("*", evidence_root)

    def test_runner_and_evidence_roots_reject_junctions_before_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            local_lab = repo / "local-lab"
            local_lab.mkdir(parents=True)
            outside_runner = root / "outside-runner"
            outside_evidence = root / "outside-evidence"
            outside_runner.mkdir()
            outside_evidence.mkdir()
            runner_root = local_lab / "winui-home-native-visual-focus-runner"
            evidence_root = local_lab / "winui-home-native-visual-focus"
            self._create_junction(runner_root, outside_runner)
            self._create_junction(evidence_root, outside_evidence)
            try:
                with self.assertRaisesRegex(harness.HarnessError, "reparse point"):
                    harness.verify_runner_path(
                        runner_root / f".{self.HARNESS_RUN_ID}.partial",
                        runner_root=runner_root,
                        repo_root=repo,
                    )
                with self.assertRaisesRegex(harness.HarnessError, "reparse point"):
                    harness.verify_evidence_root(evidence_root, repo_root=repo)
            finally:
                evidence_root.rmdir()
                runner_root.rmdir()

    def test_failed_invocation_cleanup_rejects_nested_junction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            evidence_root = repo / "local-lab" / "winui-home-native-visual-focus"
            owned = evidence_root / f"home-newcomer-test-{self.HARNESS_RUN_ID}"
            outside = root / "outside"
            owned.mkdir(parents=True)
            outside.mkdir()
            canary = outside / "canary.txt"
            canary.write_text("preserve", encoding="utf-8")
            junction = owned / "nested"
            self._create_junction(junction, outside)
            try:
                with self.assertRaisesRegex(harness.HarnessError, "reparse point"):
                    harness.remove_failed_invocation_evidence(
                        self.HARNESS_RUN_ID,
                        evidence_root,
                        repo_root=repo,
                    )
                self.assertEqual(canary.read_text(encoding="utf-8"), "preserve")
            finally:
                junction.rmdir()


    def _write_valid_manifest(self, root: Path) -> Path:
        build = root / "OnslaughtCareerEditor.WinUI" / "bin" / "Debug" / "net10.0-windows10.0.19041.0" / "win-x64"
        build.mkdir(parents=True)
        exe = build / "OnslaughtCareerEditor.WinUI.exe"
        dll = build / "OnslaughtCareerEditor.WinUI.dll"
        exe.write_bytes(b"repo-exe")
        dll.write_bytes(b"repo-dll")
        run = root / "local-lab" / "winui-home-native-visual-focus" / f"home-newcomer-test-{self.HARNESS_RUN_ID}"
        run.mkdir(parents=True)

        identities: dict[str, dict[str, object]] = {}
        for index, state in enumerate(("first-run", "ready"), start=1):
            identities[state] = {
                "ProcessId": 4200 + index,
                "ProcessStartTimeUtc": f"2026-07-15T04:1{index}:00Z",
                "ExecutablePath": str(exe),
                "ExecutableSha256": hashlib.sha256(exe.read_bytes()).hexdigest().upper(),
                "ProductAssemblyPath": str(dll),
                "ProductAssemblySha256": hashlib.sha256(dll.read_bytes()).hexdigest().upper(),
                "MainWindowHandle": 9000 + index,
                "UiaNativeWindowHandle": 9000 + index,
                "WindowOwnerProcessId": 4200 + index,
            }

        captures: list[dict[str, object]] = []
        focus_receipts: list[dict[str, object]] = []
        for state, expected, outcome, run_id in (
            ("first-run", "HomeSetupActionButton", "ContentFocused", "first-run-id"),
            ("ready", "HomeOpenPatchBenchButton", "UserFocusPreserved", "ready-id"),
        ):
            identity = identities[state]
            for suffix, width, height in (("normal", 1100, 900), ("760", 760, 820)):
                name = f"{state}-{suffix}.png"
                image = run / name
                write_png(image, width, height)
                endpoint = self._endpoint(expected, int(identity["ProcessId"]), sequence=5 if suffix == "normal" else 8)
                captures.append(
                    {
                        "State": state,
                        "ExpectedAutomationId": expected,
                        "RunId": run_id,
                        "DiagnosticOutcome": outcome,
                        "RelativeFileName": name,
                        "Sha256": hashlib.sha256(image.read_bytes()).hexdigest().upper(),
                        "X": 16,
                        "Y": 16,
                        "Width": width,
                        "Height": height,
                        "Identity": identity,
                        "Markers": [{"Name": expected, "Bounds": {"X": 20, "Y": 180, "Width": 200, "Height": 40}}],
                        "FocusBeforeCapture": endpoint,
                        "FocusAfterCapture": endpoint,
                    }
                )
            focus_receipts.append(
                {
                    "State": state,
                    "ExpectedAutomationId": expected,
                    "ObservedAutomationId": expected,
                    "RunId": run_id,
                    "ProcessId": identity["ProcessId"],
                    "DiagnosticStage": "terminal",
                    "DiagnosticTarget": "Setup" if state == "first-run" else None,
                    "DiagnosticOutcome": outcome,
                    "FocusVerified": True if state == "first-run" else None,
                    "FocusedAutomationIdAtSample": expected if state == "first-run" else "HomeNavigationItem",
                    "FinalXamlFocusedAutomationId": expected,
                    "InputEpochAtSample": 0,
                    "Identity": identity,
                    "FinalEndpoint": self._endpoint(expected, int(identity["ProcessId"]), sequence=10),
                }
            )

        manifest = run / "home-acceptance-manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "SchemaVersion": 3,
                    "HarnessRunId": self.HARNESS_RUN_ID,
                    "Captures": captures,
                    "FocusReceipts": focus_receipts,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return manifest

    @staticmethod
    def _endpoint(expected: str, process_id: int, *, sequence: int) -> dict[str, object]:
        return {
            "AutomationId": expected,
            "ProcessId": process_id,
            "NativeWindowHandle": 0,
            "X": 100,
            "Y": 200,
            "Width": 220,
            "Height": 44,
            "HasKeyboardFocus": True,
            "EndpointSequence": sequence,
            "EndpointInputEpoch": 0,
            "EndpointFocusedAutomationId": expected,
        }

    @staticmethod
    def _create_junction(link: Path, target: Path) -> None:
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)


if __name__ == "__main__":
    unittest.main()
