#!/usr/bin/env python3
"""Tests for the fail-closed native WinUI Save Lab workflow runner."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from unittest import mock

import run_winui_save_lab_native_workflow as harness


PNG_SIGNATURE = bytes((137, 80, 78, 71, 13, 10, 26, 10))
GOODIE_BASE_OFFSET = 0x1F46
DISPLAYABLE_GOODIE_COUNT = 233
CONTROLLER_CONFIG_P1_OFFSET = 0x24B6


def write_png(path: Path, width: int, height: int) -> None:
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + (b"\x20\x34\x9a\xff" * width) for _ in range(height))
    path.write_bytes(
        PNG_SIGNATURE
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def write_trx(path: Path, *, passed: int = 1, not_executed: int = 0, outcome: str = "Passed") -> None:
    root = ET.Element("TestRun")
    results = ET.SubElement(root, "Results")
    ET.SubElement(results, "UnitTestResult", {"testName": harness.TEST_METHOD_NAME, "outcome": outcome})
    summary = ET.SubElement(root, "ResultSummary", {"outcome": "Completed"})
    ET.SubElement(
        summary,
        "Counters",
        {
            "total": "1",
            "executed": str(1 - not_executed),
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


class SaveLabNativeWorkflowRunnerTests(unittest.TestCase):
    RUN_ID = "a" * 32
    OTHER_ID = "b" * 32

    def test_commands_pin_debug_win_x64_and_exact_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            test_command = harness.native_test_command(root, root / "result.trx")
        for command in (harness.WINUI_BUILD_COMMAND, test_command):
            self.assertEqual("Debug", command[command.index("--configuration") + 1])
            self.assertEqual("win-x64", command[command.index("--runtime") + 1])
        self.assertIn(f"FullyQualifiedName={harness.TEST_FQN}", test_command)

    def test_validate_manifest_accepts_exact_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            summary = harness.validate_manifest(manifest, root, self.RUN_ID)
        self.assertEqual(8, summary["captureCount"])
        self.assertEqual(2, summary["workflowCount"])

    def test_interaction_contract_names_scroll_item_and_excludes_os_input(self) -> None:
        self.assertEqual(
            "UIA Value/Toggle/ExpandCollapse/Scroll/ScrollItem/Selection/Focus/Invoke; no keyboard or pointer synthesis",
            harness.INTERACTION_MODE,
        )

    def test_validate_manifest_rejects_another_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "another runner invocation"):
                harness.validate_manifest(manifest, root, self.OTHER_ID)

    def test_validate_manifest_rejects_missing_or_extra_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Captures"].append(copy.deepcopy(payload["Captures"][0]))
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "exactly eight captures"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_png_dimension_or_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            image = manifest.parent / "save-ready-760.png"
            write_png(image, 761, 820)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            for capture in payload["Captures"]:
                if capture["RelativeFileName"] == image.name:
                    capture["Sha256"] = harness.sha256(image)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "PNG dimensions"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Workflows"][0]["OutputRelativePath"] = "../escape.bes"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "confined"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_fixture_or_synthetic_recipe_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["SyntheticOptions"]["VersionWord"] = 0
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "synthetic options recipe"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_capture_workflow_identity_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Captures"][0]["Identity"] = copy.deepcopy(payload["Workflows"][1]["Identity"])
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "workflow identity"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_input_preservation_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["Workflows"][0]["InputSha256After"] = "F" * 64
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "input preservation"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_forged_save_readback_with_wrong_goodie_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            workflow = next(row for row in payload["Workflows"] if row["Workflow"] == "save-editor")
            output = manifest.parent / Path(workflow["OutputRelativePath"])
            changed = bytearray(output.read_bytes())
            struct.pack_into("<I", changed, GOODIE_BASE_OFFSET, 0)
            output.write_bytes(changed)
            workflow["OutputSha256"] = harness.sha256(output)
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(harness.NativeAcceptanceError, "displayable Goodies"):
                harness.validate_manifest(manifest, root)

    def test_validate_manifest_rejects_forged_options_readback_with_wrong_controller_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = self._write_valid_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            workflow = next(row for row in payload["Workflows"] if row["Workflow"] == "game-options")
            output = manifest.parent / Path(workflow["OutputRelativePath"])
            changed = bytearray(output.read_bytes())
            struct.pack_into("<I", changed, CONTROLLER_CONFIG_P1_OFFSET, 2)
            output.write_bytes(changed)
            workflow["OutputSha256"] = harness.sha256(output)
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(harness.NativeAcceptanceError, "ControllerConfigP1"):
                harness.validate_manifest(manifest, root)

    def test_validate_trx_rejects_skipped_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trx = Path(temp_dir) / "result.trx"
            write_trx(trx, passed=0, not_executed=1, outcome="NotExecuted")
            with self.assertRaisesRegex(harness.NativeAcceptanceError, "exactly one executed passing test"):
                harness.validate_trx(trx)

    def test_partial_evidence_scan_rejects_stale_partial(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir)
            (evidence / ".save-lab-stale.partial").mkdir()
            self.assertEqual([".save-lab-stale.partial"], [path.name for path in harness.partial_evidence_directories(evidence)])

    def test_failed_invocation_cleanup_removes_only_owned_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            evidence = repo / "local-lab" / "winui-save-lab-native-workflow"
            evidence.mkdir(parents=True)
            owned = evidence / f"save-lab-date-{self.RUN_ID}"
            owned_partial = evidence / f".save-lab-date-{self.RUN_ID}.partial"
            other = evidence / f"save-lab-date-{self.OTHER_ID}"
            owned.mkdir()
            owned_partial.mkdir()
            other.mkdir()
            harness.remove_failed_invocation_evidence(self.RUN_ID, evidence, repo_root=repo)
            self.assertFalse(owned.exists())
            self.assertFalse(owned_partial.exists())
            self.assertTrue(other.is_dir())

    def test_runner_and_evidence_roots_reject_junction_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            local_lab = repo / "local-lab"
            local_lab.mkdir(parents=True)
            outside_runner = root / "outside-runner"
            outside_evidence = root / "outside-evidence"
            outside_runner.mkdir()
            outside_evidence.mkdir()
            runner_root = local_lab / "winui-save-lab-native-workflow-runner"
            evidence_root = local_lab / "winui-save-lab-native-workflow"
            self._create_junction(runner_root, outside_runner)
            self._create_junction(evidence_root, outside_evidence)
            try:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.verify_runner_path(
                        runner_root / f".{self.RUN_ID}.partial",
                        runner_root=runner_root,
                        repo_root=repo,
                    )
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.verify_evidence_root(evidence_root, repo_root=repo)
            finally:
                evidence_root.rmdir()
                runner_root.rmdir()

    def test_owned_roots_reject_junction_targeting_another_local_lab_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            local_lab = repo / "local-lab"
            local_lab.mkdir(parents=True)
            other_owned_root = local_lab / "other-owned-root"
            other_owned_root.mkdir()
            evidence_root = local_lab / "winui-save-lab-native-workflow"
            self._create_junction(evidence_root, other_owned_root)
            try:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.verify_evidence_root(evidence_root, repo_root=repo)
            finally:
                evidence_root.rmdir()

    def test_cleanup_identity_recovery_rejects_manifest_through_child_junction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            manifest = self._write_valid_manifest(repo)
            run_directory = manifest.parent
            outside = root / "outside-receipt"
            run_directory.rename(outside)
            self._create_junction(run_directory, outside)
            try:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.recover_validated_owned_process_identities(
                        self.RUN_ID,
                        evidence_root=repo / "local-lab" / "winui-save-lab-native-workflow",
                        repo_root=repo,
                    )
            finally:
                run_directory.rmdir()

    def test_owned_manifest_receipt_rechecks_after_validation_junction_swap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            manifest = self._write_valid_manifest(repo)
            evidence_root = repo / "local-lab" / "winui-save-lab-native-workflow"
            run_directory = manifest.parent
            outside = root / "outside-receipt"
            original_validate = harness.validate_manifest

            def validate_then_swap(*args: object, **kwargs: object) -> dict[str, object]:
                summary = original_validate(*args, **kwargs)
                run_directory.rename(outside)
                self._create_junction(run_directory, outside)
                return summary

            try:
                with mock.patch.object(harness, "validate_manifest", side_effect=validate_then_swap):
                    with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                        harness.validate_owned_manifest_receipt(
                            manifest,
                            evidence_root=evidence_root,
                            repo_root=repo,
                            expected_harness_run_id=self.RUN_ID,
                        )
            finally:
                if run_directory.exists():
                    run_directory.rmdir()

    def test_failed_invocation_cleanup_rejects_nested_junction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            evidence_root = repo / "local-lab" / "winui-save-lab-native-workflow"
            owned = evidence_root / f"save-lab-test-{self.RUN_ID}"
            outside = root / "outside"
            owned.mkdir(parents=True)
            outside.mkdir()
            canary = outside / "canary.txt"
            canary.write_text("preserve", encoding="utf-8")
            junction = owned / "nested"
            self._create_junction(junction, outside)
            try:
                with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                    harness.remove_failed_invocation_evidence(
                        self.RUN_ID,
                        evidence_root,
                        repo_root=repo,
                    )
                self.assertEqual(canary.read_text(encoding="utf-8"), "preserve")
            finally:
                junction.rmdir()

    def test_owned_repo_winui_survivors_require_exact_path_and_start_identity(self) -> None:
        expected = Path(r"C:\repo\OnslaughtCareerEditor.WinUI.exe")
        row = {
            "Id": 4101,
            "ProcessName": "OnslaughtCareerEditor.WinUI",
            "Path": str(expected),
            "StartTimeUtcTicks": 638881920000000000,
        }
        owned = {(4101, row["StartTimeUtcTicks"], harness.normalized(expected))}
        selected = harness.select_owned_repo_winui_survivors({4101: row}, expected, owned)
        self.assertEqual([(4101, row)], selected)

        forged = dict(row, Path=r"C:\other\OnslaughtCareerEditor.WinUI.exe")
        with self.assertRaisesRegex(harness.NativeAcceptanceError, "not the exact repo build"):
            harness.select_owned_repo_winui_survivors({4101: forged}, expected, owned)

        missing_start = dict(row)
        del missing_start["StartTimeUtcTicks"]
        with self.assertRaisesRegex(harness.NativeAcceptanceError, "start identity"):
            harness.select_owned_repo_winui_survivors({4101: missing_start}, expected, owned)

        wrong_start = dict(row, StartTimeUtcTicks=row["StartTimeUtcTicks"] + 1)
        with self.assertRaisesRegex(harness.NativeAcceptanceError, "validated launch receipt"):
            harness.select_owned_repo_winui_survivors({4101: wrong_start}, expected, owned)

    def test_dotnet_utc_timestamp_ticks_preserves_100ns_precision_and_offsets(self) -> None:
        earlier = harness.dotnet_utc_timestamp_ticks("2026-07-14T04:10:00.1234566Z")
        later = harness.dotnet_utc_timestamp_ticks("2026-07-14T04:10:00.1234567Z")
        equivalent_offset = harness.dotnet_utc_timestamp_ticks("2026-07-14T00:10:00.1234567-04:00")

        self.assertEqual(later - earlier, 1)
        self.assertEqual(equivalent_offset, later)
        with self.assertRaisesRegex(harness.NativeAcceptanceError, "UTC timestamp"):
            harness.dotnet_utc_timestamp_ticks("2026-07-14")

    def test_exact_owned_winui_termination_uses_identity_gated_tree_kill(self) -> None:
        expected = Path(r"C:\repo path\OnslaughtCareerEditor.WinUI.exe")
        row = {"StartTimeUtcTicks": 638881920000000000}

        with mock.patch.object(harness.native_support, "terminate_owned_process_tree") as terminate:
            harness.terminate_exact_owned_winui_process(4101, row, expected)

        identity = terminate.call_args.args[0]
        self.assertEqual(identity.process_id, 4101)
        self.assertEqual(identity.start_time_utc_ticks, row["StartTimeUtcTicks"])
        self.assertEqual(identity.executable_path, expected)
        self.assertEqual(terminate.call_args.kwargs["repo_root"], harness.REPO_ROOT)

    def test_survivor_remediation_rechecks_receipt_before_termination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            manifest = self._write_valid_manifest(repo)
            summary = harness.validate_manifest(manifest, repo, self.RUN_ID)
            owned_identities = harness.owned_process_identity_set(summary)
            identity = summary["ownedProcessIdentities"][0]
            census = {
                identity["processId"]: {
                    "Id": identity["processId"],
                    "ProcessName": "OnslaughtCareerEditor.WinUI",
                    "Path": identity["executablePath"],
                    "StartTimeUtcTicks": identity["startTimeUtcTicks"],
                }
            }
            run_directory = manifest.parent
            outside = root / "outside-receipt"
            run_directory.rename(outside)
            self._create_junction(run_directory, outside)
            try:
                with mock.patch.object(harness, "terminate_exact_owned_winui_process") as terminate:
                    with self.assertRaisesRegex(harness.NativeAcceptanceError, "reparse point"):
                        harness.remediate_final_process_census(
                            census,
                            owned_identities,
                            receipt_path=manifest,
                            evidence_root=repo / "local-lab" / "winui-save-lab-native-workflow",
                            repo_root=repo,
                        )
                terminate.assert_not_called()
            finally:
                run_directory.rmdir()

    def _write_valid_manifest(self, root: Path) -> Path:
        build = root / "OnslaughtCareerEditor.WinUI" / "bin" / "Debug" / "net10.0-windows10.0.19041.0" / "win-x64"
        build.mkdir(parents=True)
        exe = build / "OnslaughtCareerEditor.WinUI.exe"
        dll = build / "OnslaughtCareerEditor.WinUI.dll"
        exe.write_bytes(b"repo-exe")
        dll.write_bytes(b"repo-dll")

        run = root / "local-lab" / "winui-save-lab-native-workflow" / f"save-lab-test-{self.RUN_ID}"
        fixture_dir = run / "fixtures"
        fixture_dir.mkdir(parents=True)
        tracked_fixture = harness.REPO_ROOT / "tests_shared" / "fixtures" / "gold_career_save.bin"
        save_input = fixture_dir / "first-save-input.bes"
        save_input.write_bytes(tracked_fixture.read_bytes())
        options_data = bytearray(harness.ARTIFACT_LENGTH)
        options_data[0:2] = harness.SYNTHETIC_VERSION_WORD.to_bytes(2, "little")
        options_input = fixture_dir / "synthetic-options.bea"
        options_input.write_bytes(options_data)

        save_output = run / "save-session" / "appdata" / "OnslaughtCareerEditor" / "patched-output" / "first-save-input_patched.bes"
        options_output = run / "options-session" / "appdata" / "OnslaughtCareerEditor" / "patched-output" / "synthetic-options_patched.bea"
        save_output.parent.mkdir(parents=True)
        options_output.parent.mkdir(parents=True)
        changed_save = bytearray(save_input.read_bytes())
        for index in range(DISPLAYABLE_GOODIE_COUNT):
            struct.pack_into("<I", changed_save, GOODIE_BASE_OFFSET + index * 4, 3)
        save_output.write_bytes(changed_save)
        changed_options = bytearray(options_input.read_bytes())
        struct.pack_into("<I", changed_options, CONTROLLER_CONFIG_P1_OFFSET, 1)
        options_output.write_bytes(changed_options)

        identities = {
            "save-editor": self._identity(exe, dll, 4101, 9101, "2026-07-14T04:10:00Z"),
            "game-options": self._identity(exe, dll, 4102, 9102, "2026-07-14T04:11:00Z"),
        }
        workflows = [
            self._workflow("save-editor", identities["save-editor"], run, save_input, save_output, "goodies-old-output-valid"),
            self._workflow("game-options", identities["game-options"], run, options_input, options_output, "controller-config-p1=1"),
        ]

        capture_specs = (
            ("save-ready-normal.png", "save-editor", "ready", "SaveEditorInputFile", 1100, 900,
             ("SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox")),
            ("save-ready-760.png", "save-editor", "ready", "SaveEditorInputFile", 760, 820,
             ("SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox")),
            ("save-complete-normal.png", "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 1100, 900,
             ("SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton")),
            ("save-complete-760.png", "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 760, 820,
             ("SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton")),
            ("options-guidance-normal.png", "game-options", "guidance", "OpenZigguratControllerGuideButton", 1100, 900,
             ("ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton")),
            ("options-guidance-760.png", "game-options", "guidance", "OpenZigguratControllerGuideButton", 760, 820,
             ("ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton")),
            ("options-complete-normal.png", "game-options", "complete", "ConfigurationPatchButton", 1100, 900,
             ("ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog")),
            ("options-complete-760.png", "game-options", "complete", "ConfigurationPatchButton", 760, 820,
             ("ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog")),
        )
        captures = []
        for name, workflow, phase, focus, width, height, marker_ids in capture_specs:
            image = run / name
            write_png(image, width, height)
            focus_row = {
                "AutomationId": focus,
                "ProcessId": identities[workflow]["ProcessId"],
                "MainWindowHandle": identities[workflow]["MainWindowHandle"],
                "X": 20,
                "Y": 180,
                "Width": 220,
                "Height": 42,
                "HasKeyboardFocus": True,
            }
            captures.append(
                {
                    "Workflow": workflow,
                    "Phase": phase,
                    "FocusAutomationId": focus,
                    "RelativeFileName": name,
                    "Sha256": harness.sha256(image),
                    "Width": width,
                    "Height": height,
                    "Identity": identities[workflow],
                    "Markers": [
                        {"Name": marker, "Bounds": {"X": 20, "Y": 180 + index * 50, "Width": 220, "Height": 42}}
                        for index, marker in enumerate(marker_ids)
                    ],
                    "FocusBeforeCapture": focus_row,
                    "FocusAfterCapture": focus_row,
                }
            )

        manifest = run / "save-lab-acceptance-manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "SchemaVersion": 1,
                    "HarnessRunId": self.RUN_ID,
                    "InteractionMode": harness.INTERACTION_MODE,
                    "TrackedSaveFixtureSha256": harness.TRACKED_FIXTURE_SHA256,
                    "SyntheticOptions": {
                        "Length": harness.ARTIFACT_LENGTH,
                        "VersionWord": harness.SYNTHETIC_VERSION_WORD,
                        "Sha256": harness.SYNTHETIC_OPTIONS_SHA256,
                    },
                    "Captures": captures,
                    "Workflows": workflows,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return manifest

    @staticmethod
    def _identity(exe: Path, dll: Path, pid: int, hwnd: int, start: str) -> dict[str, object]:
        return {
            "ProcessId": pid,
            "ProcessStartTimeUtc": start,
            "ExecutablePath": str(exe),
            "ExecutableSha256": hashlib.sha256(exe.read_bytes()).hexdigest().upper(),
            "ProductAssemblyPath": str(dll),
            "ProductAssemblySha256": hashlib.sha256(dll.read_bytes()).hexdigest().upper(),
            "MainWindowHandle": hwnd,
            "UiaNativeWindowHandle": hwnd,
            "WindowOwnerProcessId": pid,
        }

    @staticmethod
    def _workflow(
        name: str,
        identity: dict[str, object],
        run: Path,
        input_path: Path,
        output_path: Path,
        readback: str,
    ) -> dict[str, object]:
        input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest().upper()
        output_hash = hashlib.sha256(output_path.read_bytes()).hexdigest().upper()
        return {
            "Workflow": name,
            "Identity": identity,
            "InputRelativePath": input_path.relative_to(run).as_posix(),
            "InputSha256Before": input_hash,
            "InputSha256After": input_hash,
            "OutputRelativePath": output_path.relative_to(run).as_posix(),
            "OutputSha256": output_hash,
            "OutputLength": len(output_path.read_bytes()),
            "InputPreserved": True,
            "OutputValidated": True,
            "Readback": readback,
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
