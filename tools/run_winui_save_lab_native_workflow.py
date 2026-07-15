#!/usr/bin/env python3
"""Run fail-closed native WinUI Save Lab workflow acceptance.

The runner builds only the repository Debug/win-x64 WinUI app, executes one
explicit deterministic Save Lab test, reconciles all receipt-bound artifacts,
and requires zero relevant processes before and after. It never launches BEA,
uses an external executable, or opens Explorer/a browser.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import winui_native_acceptance_support as native_support


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = REPO_ROOT / "local-lab" / "winui-save-lab-native-workflow"
RUNNER_ROOT = REPO_ROOT / "local-lab" / "winui-save-lab-native-workflow-runner"
TEST_METHOD_NAME = "SaveLab_FirstUseAndOptions_PublishDeterministicNativeEvidence"
TEST_FQN = f"OnslaughtCareerEditor.UiTests.WinUiSaveLabNativeWorkflowTests.{TEST_METHOD_NAME}"
BUILT_APP_ROOT = (
    REPO_ROOT
    / "OnslaughtCareerEditor.WinUI"
    / "bin"
    / "Debug"
    / "net10.0-windows10.0.19041.0"
    / "win-x64"
)
WINUI_BUILD_COMMAND = [
    "dotnet",
    "build",
    r".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj",
    "--nologo",
    "--configuration",
    "Debug",
    "--runtime",
    "win-x64",
]
ARTIFACT_LENGTH = 10_004
SYNTHETIC_VERSION_WORD = 0x4BD1
TRACKED_FIXTURE_SHA256 = "0C17E47DB9D666E9B26EF88D43D0A25E7CBFBF4F88C8005CC748965050E506FB"
SYNTHETIC_OPTIONS_SHA256 = "A922C6BCA412DB45AED3FCCBE926B6383C039CCF3778C4558D299D1D3C466D99"
INTERACTION_MODE = "UIA Value/Toggle/ExpandCollapse/Scroll/Focus/Invoke; no keyboard or pointer synthesis"

NativeAcceptanceError = native_support.NativeAcceptanceError
HarnessError = NativeAcceptanceError
require = native_support.require
sha256 = native_support.sha256
normalized = native_support.normalized
png_dimensions = native_support.png_dimensions


EXPECTED_CAPTURES: dict[str, tuple[str, str, str, int, int, frozenset[str]]] = {
    "save-ready-normal.png": (
        "save-editor", "ready", "SaveEditorInputFile", 1100, 900,
        frozenset(("SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox")),
    ),
    "save-ready-760.png": (
        "save-editor", "ready", "SaveEditorInputFile", 760, 820,
        frozenset(("SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox")),
    ),
    "save-complete-normal.png": (
        "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 1100, 900,
        frozenset(("SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton")),
    ),
    "save-complete-760.png": (
        "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 760, 820,
        frozenset(("SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton")),
    ),
    "options-guidance-normal.png": (
        "game-options", "guidance", "OpenZigguratControllerGuideButton", 1100, 900,
        frozenset(("ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton")),
    ),
    "options-guidance-760.png": (
        "game-options", "guidance", "OpenZigguratControllerGuideButton", 760, 820,
        frozenset(("ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton")),
    ),
    "options-complete-normal.png": (
        "game-options", "complete", "ConfigurationPatchButton", 1100, 900,
        frozenset(("ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog")),
    ),
    "options-complete-760.png": (
        "game-options", "complete", "ConfigurationPatchButton", 760, 820,
        frozenset(("ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog")),
    ),
}


def validate_trx(path: Path) -> dict[str, int]:
    return native_support.validate_exact_trx(path, TEST_METHOD_NAME, "native Save Lab")


def validate_manifest(
    path: Path,
    repo_root: Path = REPO_ROOT,
    expected_harness_run_id: str | None = None,
) -> dict[str, Any]:
    require(path.is_file(), f"fresh native Save Lab manifest is missing: {path}")
    require(".partial" not in path.parent.name, "accepted native Save Lab manifest remains in a partial directory")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NativeAcceptanceError(f"native Save Lab manifest is unreadable: {exc}") from exc

    require(isinstance(manifest, dict) and manifest.get("SchemaVersion") == 1, "native Save Lab manifest schema must be 1")
    harness_run_id = manifest.get("HarnessRunId")
    require(
        isinstance(harness_run_id, str) and re.fullmatch(r"[0-9a-f]{32}", harness_run_id) is not None,
        "native Save Lab manifest harness run ID is invalid",
    )
    if expected_harness_run_id is not None:
        require(harness_run_id == expected_harness_run_id, "native Save Lab manifest belongs to another runner invocation")
    require(manifest.get("InteractionMode") == INTERACTION_MODE, "native Save Lab interaction mode changed")
    require(
        manifest.get("TrackedSaveFixtureSha256") == TRACKED_FIXTURE_SHA256,
        "native Save Lab tracked fixture identity changed",
    )
    recipe = manifest.get("SyntheticOptions")
    require(
        isinstance(recipe, dict)
        and recipe.get("Length") == ARTIFACT_LENGTH
        and recipe.get("VersionWord") == SYNTHETIC_VERSION_WORD
        and recipe.get("Sha256") == SYNTHETIC_OPTIONS_SHA256,
        "native Save Lab synthetic options recipe changed",
    )
    captures = manifest.get("Captures")
    workflows = manifest.get("Workflows")
    require(isinstance(captures, list) and len(captures) == 8, "native Save Lab manifest must contain exactly eight captures")
    require(isinstance(workflows, list) and len(workflows) == 2, "native Save Lab manifest must contain exactly two workflows")

    expected_app_root = (
        repo_root
        / "OnslaughtCareerEditor.WinUI"
        / "bin"
        / "Debug"
        / "net10.0-windows10.0.19041.0"
        / "win-x64"
    )
    expected_exe = expected_app_root / "OnslaughtCareerEditor.WinUI.exe"
    expected_dll = expected_app_root / "OnslaughtCareerEditor.WinUI.dll"
    require(expected_exe.is_file() and expected_dll.is_file(), "repository WinUI build outputs are missing during Save Lab validation")

    def validate_identity(identity: Any) -> dict[str, Any]:
        require(isinstance(identity, dict), "native Save Lab launch identity is missing")
        process_id = identity.get("ProcessId")
        require(isinstance(process_id, int) and process_id > 0, "native Save Lab process ID is invalid")
        require(identity.get("WindowOwnerProcessId") == process_id, "native Save Lab HWND owner does not match its process")
        main_hwnd = identity.get("MainWindowHandle")
        require(
            isinstance(main_hwnd, int) and main_hwnd != 0 and identity.get("UiaNativeWindowHandle") == main_hwnd,
            "native Save Lab main/UIA HWND identity is invalid",
        )
        require(
            normalized(identity.get("ExecutablePath", "")) == normalized(expected_exe),
            "native Save Lab executable path is not the repo build",
        )
        require(
            normalized(identity.get("ProductAssemblyPath", "")) == normalized(expected_dll),
            "native Save Lab product DLL path is not the repo build",
        )
        executable_hash = identity.get("ExecutableSha256")
        product_hash = identity.get("ProductAssemblySha256")
        require(
            isinstance(executable_hash, str) and re.fullmatch(r"[0-9A-F]{64}", executable_hash) is not None,
            "native Save Lab executable hash is invalid",
        )
        require(
            isinstance(product_hash, str) and re.fullmatch(r"[0-9A-F]{64}", product_hash) is not None,
            "native Save Lab product DLL hash is invalid",
        )
        require(executable_hash == sha256(expected_exe), "native Save Lab executable hash no longer matches the repo build")
        require(product_hash == sha256(expected_dll), "native Save Lab product DLL hash no longer matches the repo build")
        require(
            isinstance(identity.get("ProcessStartTimeUtc"), str) and identity["ProcessStartTimeUtc"],
            "native Save Lab process start time is missing",
        )
        return identity

    workflow_by_name: dict[str, dict[str, Any]] = {}
    evidence_directory = path.parent.resolve()
    for workflow in workflows:
        require(isinstance(workflow, dict), "native Save Lab workflow receipt must be an object")
        name = workflow.get("Workflow")
        require(name in {"save-editor", "game-options"} and name not in workflow_by_name, "native Save Lab workflow set is not exact")
        identity = validate_identity(workflow.get("Identity"))
        input_path = resolve_confined(evidence_directory, workflow.get("InputRelativePath"), f"{name} input")
        output_path = resolve_confined(evidence_directory, workflow.get("OutputRelativePath"), f"{name} output")
        require(input_path.is_file() and output_path.is_file(), f"native Save Lab {name} artifacts are missing")
        require(input_path != output_path, f"native Save Lab {name} output is not separate")
        input_hash = sha256(input_path)
        output_hash = sha256(output_path)
        expected_input_hash = TRACKED_FIXTURE_SHA256 if name == "save-editor" else SYNTHETIC_OPTIONS_SHA256
        require(
            input_hash == expected_input_hash
            and workflow.get("InputSha256Before") == input_hash
            and workflow.get("InputSha256After") == input_hash
            and workflow.get("InputPreserved") is True,
            f"native Save Lab {name} input preservation or identity changed",
        )
        require(input_path.stat().st_size == ARTIFACT_LENGTH, f"native Save Lab {name} input length changed")
        require(
            output_path.stat().st_size == ARTIFACT_LENGTH
            and workflow.get("OutputLength") == ARTIFACT_LENGTH
            and workflow.get("OutputSha256") == output_hash
            and workflow.get("OutputValidated") is True
            and output_hash != input_hash,
            f"native Save Lab {name} output validation changed",
        )
        expected_readback = "goodies-old-output-valid" if name == "save-editor" else "controller-config-p1=1"
        require(workflow.get("Readback") == expected_readback, f"native Save Lab {name} readback changed")
        if name == "game-options":
            require(
                input_path.read_bytes()[:2] == SYNTHETIC_VERSION_WORD.to_bytes(2, "little"),
                "native Save Lab synthetic options header changed",
            )
        workflow_by_name[name] = workflow

    require(set(workflow_by_name) == {"save-editor", "game-options"}, "native Save Lab workflow set is not exact")
    launch_keys = {
        (
            row["Identity"].get("ProcessId"),
            row["Identity"].get("ProcessStartTimeUtc"),
            row["Identity"].get("MainWindowHandle"),
        )
        for row in workflow_by_name.values()
    }
    require(len(launch_keys) == 2, "native Save Lab workflows must bind distinct launch identities")

    capture_by_name: dict[str, dict[str, Any]] = {}
    for capture in captures:
        require(isinstance(capture, dict), "native Save Lab capture receipt must be an object")
        name = capture.get("RelativeFileName")
        require(name in EXPECTED_CAPTURES and name not in capture_by_name, "native Save Lab capture file set is not exact")
        workflow, phase, focus_id, width, height, marker_ids = EXPECTED_CAPTURES[name]
        require(
            capture.get("Workflow") == workflow
            and capture.get("Phase") == phase
            and capture.get("FocusAutomationId") == focus_id,
            f"native Save Lab capture phase mapping changed: {name}",
        )
        identity = validate_identity(capture.get("Identity"))
        require(identity == workflow_by_name[workflow]["Identity"], f"native Save Lab capture workflow identity changed: {name}")
        require(capture.get("Width") == width and capture.get("Height") == height, f"native Save Lab capture dimensions changed: {name}")
        markers = capture.get("Markers")
        require(isinstance(markers, list), f"native Save Lab capture markers are missing: {name}")
        require(
            {marker.get("Name") for marker in markers if isinstance(marker, dict)} == marker_ids
            and len(markers) == len(marker_ids),
            f"native Save Lab marker set changed: {name}",
        )
        for marker in markers:
            validate_bounds(marker.get("Bounds"), width, height, f"native Save Lab marker {marker.get('Name')} in {name}")
        image = resolve_confined(evidence_directory, name, f"capture {name}")
        require(image.is_file(), f"native Save Lab capture is missing: {name}")
        require(capture.get("Sha256") == sha256(image), f"native Save Lab capture hash changed: {name}")
        require(png_dimensions(image) == (width, height), f"native Save Lab PNG dimensions changed: {name}")
        validate_focus(capture.get("FocusBeforeCapture"), identity, focus_id, width, height, name)
        validate_focus(capture.get("FocusAfterCapture"), identity, focus_id, width, height, name)
        capture_by_name[name] = capture

    require(set(capture_by_name) == set(EXPECTED_CAPTURES), "native Save Lab capture file set is not exact")
    return {
        "captureCount": len(captures),
        "workflowCount": len(workflows),
        "workflows": sorted(workflow_by_name),
        "manifest": str(path),
        "harnessRunId": harness_run_id,
    }


def resolve_confined(root: Path, relative_value: Any, label: str) -> Path:
    require(isinstance(relative_value, str) and relative_value, f"{label} relative path is missing")
    candidate_value = relative_value.replace("/", os.sep).replace("\\", os.sep)
    candidate = Path(candidate_value)
    require(not candidate.is_absolute(), f"{label} path must be relative and confined")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    require(resolved != resolved_root and resolved_root in resolved.parents, f"{label} path must remain confined")
    return resolved


def validate_bounds(bounds: Any, width: int, height: int, label: str) -> None:
    require(isinstance(bounds, dict), f"{label} bounds are missing")
    x = bounds.get("X")
    y = bounds.get("Y")
    item_width = bounds.get("Width")
    item_height = bounds.get("Height")
    require(
        all(isinstance(value, int) for value in (x, y, item_width, item_height))
        and item_width > 0
        and item_height > 0
        and x >= 0
        and y >= 0
        and x + item_width <= width
        and y + item_height <= height,
        f"{label} bounds are outside the bound HWND image",
    )


def validate_focus(
    focus: Any,
    identity: dict[str, Any],
    expected_automation_id: str,
    width: int,
    height: int,
    capture_name: str,
) -> None:
    require(isinstance(focus, dict), f"native Save Lab focus receipt is missing: {capture_name}")
    require(focus.get("AutomationId") == expected_automation_id, f"native Save Lab focus target changed: {capture_name}")
    require(focus.get("ProcessId") == identity["ProcessId"], f"native Save Lab focus owner changed: {capture_name}")
    require(focus.get("MainWindowHandle") == identity["MainWindowHandle"], f"native Save Lab focus HWND changed: {capture_name}")
    require(focus.get("HasKeyboardFocus") is True, f"native Save Lab focus is not keyboard focus: {capture_name}")
    validate_bounds(focus, width, height, f"native Save Lab focus in {capture_name}")


def process_census() -> dict[int, dict[str, Any]]:
    return native_support.process_census(REPO_ROOT)


def describe_processes(census: dict[int, dict[str, Any]]) -> str:
    return native_support.describe_processes(census)


def run_command(
    command: list[str],
    *,
    timeout: int,
    env_overrides: dict[str, str] | None = None,
) -> None:
    native_support.run_command(command, repo_root=REPO_ROOT, timeout=timeout, env_overrides=env_overrides)


def validate_invocation_id(invocation_id: str) -> None:
    native_support.validate_invocation_id(invocation_id)


def native_test_command(run_root: Path, trx: Path) -> list[str]:
    return [
        "dotnet",
        "test",
        r".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj",
        "--nologo",
        "--configuration",
        "Debug",
        "--runtime",
        "win-x64",
        "--filter",
        f"FullyQualifiedName={TEST_FQN}",
        "--logger",
        f"trx;LogFileName={trx.name}",
        "--results-directory",
        str(run_root),
    ]


def invocation_manifests(invocation_id: str, evidence_root: Path = EVIDENCE_ROOT) -> set[Path]:
    validate_invocation_id(invocation_id)
    if not evidence_root.exists():
        return set()
    return {
        path.resolve()
        for path in evidence_root.glob(f"save-lab-*-{invocation_id}/save-lab-acceptance-manifest.json")
        if path.is_file()
    }


def invocation_evidence_directories(invocation_id: str, evidence_root: Path = EVIDENCE_ROOT) -> set[Path]:
    validate_invocation_id(invocation_id)
    if not evidence_root.exists():
        return set()
    matches = set(evidence_root.glob(f"save-lab-*-{invocation_id}"))
    matches.update(evidence_root.glob(f".save-lab-*-{invocation_id}.partial"))
    return {path.resolve() for path in matches if path.is_dir()}


def partial_evidence_directories(evidence_root: Path = EVIDENCE_ROOT) -> list[Path]:
    if not evidence_root.exists():
        return []
    return sorted(path for path in evidence_root.iterdir() if path.is_dir() and path.name.endswith(".partial"))


def verify_runner_path(path: Path) -> None:
    resolved = path.resolve()
    root = RUNNER_ROOT.resolve()
    require(resolved != root and root in resolved.parents, f"runner cleanup path escaped its ignored root: {resolved}")


def remove_failed_invocation_evidence(invocation_id: str, evidence_root: Path = EVIDENCE_ROOT) -> None:
    validate_invocation_id(invocation_id)
    root = evidence_root.resolve()
    for run_directory in invocation_evidence_directories(invocation_id, evidence_root):
        expected_accepted = run_directory.name.startswith("save-lab-") and run_directory.name.endswith(invocation_id)
        expected_partial = (
            run_directory.name.startswith(".save-lab-")
            and run_directory.name.endswith(f"-{invocation_id}.partial")
        )
        require(
            run_directory.parent == root and (expected_accepted or expected_partial),
            f"refusing to remove unowned failed Save Lab evidence path: {run_directory}",
        )
        if run_directory.exists():
            shutil.rmtree(run_directory)


def shutdown_build_servers() -> None:
    native_support.shutdown_build_servers(REPO_ROOT)


def append_cleanup_error(error: Exception | None, phase: str, cleanup_error: Exception) -> NativeAcceptanceError:
    return native_support.append_cleanup_error(error, phase, cleanup_error)


def run_acceptance() -> dict[str, Any]:
    baseline = process_census()
    require(not baseline, f"pre-run relevant-process census must be zero, found: {describe_processes(baseline)}")
    partials = partial_evidence_directories()
    require(not partials, f"pre-run Save Lab evidence contains partial directories: {[path.name for path in partials]}")
    invocation_id = uuid.uuid4().hex
    validate_invocation_id(invocation_id)
    require(not invocation_evidence_directories(invocation_id), "fresh Save Lab invocation unexpectedly already owns evidence")
    run_root = RUNNER_ROOT / f".{invocation_id}.partial"
    verify_runner_path(run_root)
    run_root.mkdir(parents=True, exist_ok=False)
    trx = run_root / "save-lab-native-workflow.trx"
    error: Exception | None = None
    result: dict[str, Any] | None = None
    try:
        run_command(WINUI_BUILD_COMMAND, timeout=180)
        executable = BUILT_APP_ROOT / "OnslaughtCareerEditor.WinUI.exe"
        product_dll = BUILT_APP_ROOT / "OnslaughtCareerEditor.WinUI.dll"
        require(executable.is_file() and product_dll.is_file(), "pinned Debug/win-x64 WinUI build outputs are missing")
        expected_executable_hash = sha256(executable)
        expected_product_hash = sha256(product_dll)
        run_command(
            native_test_command(run_root, trx),
            timeout=300,
            env_overrides={
                "ONSLAUGHT_SAVE_LAB_NATIVE_ACCEPTANCE_RUN_ID": invocation_id,
                "ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_EXE_SHA256": expected_executable_hash,
                "ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_DLL_SHA256": expected_product_hash,
            },
        )
        trx_summary = validate_trx(trx)
        manifests = invocation_manifests(invocation_id)
        require(len(manifests) == 1, f"native Save Lab invocation must publish exactly one owned manifest, found {len(manifests)}")
        partials = partial_evidence_directories()
        require(not partials, f"native Save Lab run left partial evidence directories: {[path.name for path in partials]}")
        manifest_summary = validate_manifest(
            next(iter(manifests)),
            REPO_ROOT,
            expected_harness_run_id=invocation_id,
        )
        time.sleep(0.5)
        post = process_census()
        require(not post, f"post-run relevant-process census must be zero, found: {describe_processes(post)}")
        result = {"trx": trx_summary, **manifest_summary, "processCensus": "zero"}
    except Exception as exc:
        error = exc
    finally:
        try:
            shutdown_build_servers()
        except Exception as cleanup_error:
            error = append_cleanup_error(error, "build-server shutdown", cleanup_error)
        try:
            final_census = process_census()
            if final_census:
                raise NativeAcceptanceError(
                    f"final relevant-process census must be zero, found: {describe_processes(final_census)}"
                )
        except Exception as cleanup_error:
            error = append_cleanup_error(error, "final relevant-process census", cleanup_error)
        try:
            if run_root.exists():
                verify_runner_path(run_root)
                shutil.rmtree(run_root)
        except Exception as cleanup_error:
            error = append_cleanup_error(error, "runner-root cleanup", cleanup_error)
        if error is not None:
            try:
                remove_failed_invocation_evidence(invocation_id)
            except Exception as cleanup_error:
                error = append_cleanup_error(error, "owned evidence rollback", cleanup_error)

    if error is not None:
        if isinstance(error, NativeAcceptanceError):
            raise error
        raise NativeAcceptanceError(str(error)) from error
    require(result is not None, "native Save Lab acceptance produced no result")
    return result


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print("usage: run_winui_save_lab_native_workflow.py", file=sys.stderr)
        return 2
    try:
        result = run_acceptance()
        print("\nWinUI Save Lab native workflow acceptance: PASS", flush=True)
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        return 0
    except (NativeAcceptanceError, subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as exc:
        print(f"WinUI Save Lab native workflow acceptance: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
