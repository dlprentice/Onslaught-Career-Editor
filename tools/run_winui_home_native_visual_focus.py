#!/usr/bin/env python3
"""Run fail-closed native WinUI Home visual/focus acceptance.

The runner builds the repository WinUI app, executes exactly one explicit
native test, verifies the TRX result and one fresh receipt-bound manifest, and
requires a zero relevant-process census. It never launches Battle Engine
Aquila and never consumes an external WinUI executable override.
"""

from __future__ import annotations

import json
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
EVIDENCE_ROOT = REPO_ROOT / "local-lab" / "winui-home-native-visual-focus"
RUNNER_ROOT = REPO_ROOT / "local-lab" / "winui-home-native-visual-focus-runner"
TEST_METHOD_NAME = "Home_NewcomerHierarchy_CapturesFirstRunReadyAndCompactWithoutNavigation"
TEST_FQN = f"OnslaughtCareerEditor.UiTests.WinUiHomeNavigationSmokeTests.{TEST_METHOD_NAME}"
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
HarnessError = native_support.NativeAcceptanceError
require = native_support.require
sha256 = native_support.sha256
normalized = native_support.normalized
png_dimensions = native_support.png_dimensions


def validate_trx(path: Path) -> dict[str, int]:
    return native_support.validate_exact_trx(path, TEST_METHOD_NAME, "native Home")


def validate_manifest(
    path: Path,
    repo_root: Path = REPO_ROOT,
    expected_harness_run_id: str | None = None,
) -> dict[str, Any]:
    require(path.is_file(), f"fresh native Home manifest is missing: {path}")
    require(".partial" not in path.parent.name, "accepted native Home manifest remains in a partial directory")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"native Home manifest is unreadable: {exc}") from exc
    require(isinstance(manifest, dict) and manifest.get("SchemaVersion") == 3, "native Home manifest schema must be 3")
    harness_run_id = manifest.get("HarnessRunId")
    require(
        isinstance(harness_run_id, str) and re.fullmatch(r"[0-9a-f]{32}", harness_run_id) is not None,
        "native Home manifest harness run ID is invalid",
    )
    if expected_harness_run_id is not None:
        require(harness_run_id == expected_harness_run_id, "native Home manifest belongs to another runner invocation")
    captures = manifest.get("Captures")
    receipts = manifest.get("FocusReceipts")
    require(isinstance(captures, list) and len(captures) == 4, "native Home manifest must contain four captures")
    require(isinstance(receipts, list) and len(receipts) == 2, "native Home manifest must contain two focus receipts")

    expected_files = {
        "first-run-normal.png": ("first-run", "HomeSetupActionButton", 1100, 900),
        "first-run-760.png": ("first-run", "HomeSetupActionButton", 760, 820),
        "ready-normal.png": ("ready", "HomeOpenPatchBenchButton", 1100, 900),
        "ready-760.png": ("ready", "HomeOpenPatchBenchButton", 760, 820),
    }
    require(
        {capture.get("RelativeFileName") for capture in captures if isinstance(capture, dict)} == set(expected_files),
        "native Home capture file set is not exact",
    )
    receipt_by_state = {
        receipt.get("State"): receipt
        for receipt in receipts
        if isinstance(receipt, dict) and isinstance(receipt.get("State"), str)
    }
    require(set(receipt_by_state) == {"first-run", "ready"}, "native Home focus states must be first-run and ready")
    run_ids = {receipt.get("RunId") for receipt in receipts if isinstance(receipt, dict)}
    require(len(run_ids) == 2 and all(isinstance(run_id, str) and run_id for run_id in run_ids), "native Home focus run IDs must be distinct")

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
    require(expected_exe.is_file() and expected_dll.is_file(), "repository WinUI build outputs are missing during manifest validation")

    def validate_identity(identity: Any) -> dict[str, Any]:
        require(isinstance(identity, dict), "native Home receipt identity is missing")
        process_id = identity.get("ProcessId")
        require(isinstance(process_id, int) and process_id > 0, "native Home identity process ID is invalid")
        require(identity.get("WindowOwnerProcessId") == process_id, "native Home HWND owner does not match process identity")
        require(
            isinstance(identity.get("MainWindowHandle"), int)
            and identity.get("MainWindowHandle") != 0
            and identity.get("UiaNativeWindowHandle") == identity.get("MainWindowHandle"),
            "native Home main/UIA HWND identity is invalid",
        )
        require(normalized(identity.get("ExecutablePath", "")) == normalized(expected_exe), "native Home executable path is not the repo build")
        require(normalized(identity.get("ProductAssemblyPath", "")) == normalized(expected_dll), "native Home product DLL path is not the repo build")
        executable_hash = identity.get("ExecutableSha256")
        product_hash = identity.get("ProductAssemblySha256")
        require(isinstance(executable_hash, str) and re.fullmatch(r"[0-9A-F]{64}", executable_hash) is not None, "native Home executable hash is invalid")
        require(isinstance(product_hash, str) and re.fullmatch(r"[0-9A-F]{64}", product_hash) is not None, "native Home product DLL hash is invalid")
        require(executable_hash == sha256(expected_exe), "native Home executable hash no longer matches the repo build")
        require(product_hash == sha256(expected_dll), "native Home product DLL hash no longer matches the repo build")
        require(isinstance(identity.get("ProcessStartTimeUtc"), str) and identity["ProcessStartTimeUtc"], "native Home process start time is missing")
        return identity

    def validate_endpoint(endpoint: Any, expected: str, process_id: int) -> None:
        require(isinstance(endpoint, dict), "native Home focus endpoint is missing")
        require(endpoint.get("AutomationId") == expected, "native Home focus endpoint target changed")
        require(endpoint.get("EndpointFocusedAutomationId") == expected, "native Home app endpoint focus changed")
        require(endpoint.get("ProcessId") == process_id, "native Home focus endpoint owner process changed")
        require(endpoint.get("HasKeyboardFocus") is True, "native Home focus endpoint lacks keyboard focus")
        require(endpoint.get("EndpointInputEpoch") == 0, "native Home input epoch changed")
        require(isinstance(endpoint.get("EndpointSequence"), int) and endpoint["EndpointSequence"] > 0, "native Home endpoint sequence is invalid")
        require(endpoint.get("Width", 0) > 0 and endpoint.get("Height", 0) > 0, "native Home focused bounds are empty")

    validated_identities: dict[str, dict[str, Any]] = {}
    for state, receipt in receipt_by_state.items():
        expected = "HomeSetupActionButton" if state == "first-run" else "HomeOpenPatchBenchButton"
        identity = validate_identity(receipt.get("Identity"))
        validated_identities[state] = identity
        require(receipt.get("ProcessId") == identity["ProcessId"], "native Home focus receipt process ID disagrees with identity")
        require(receipt.get("ExpectedAutomationId") == expected and receipt.get("ObservedAutomationId") == expected, "native Home final focus receipt target changed")
        require(receipt.get("FinalXamlFocusedAutomationId") == expected, "native Home final XAML focus target changed")
        require(receipt.get("InputEpochAtSample") == 0, "native Home diagnostic input epoch changed")
        outcome = receipt.get("DiagnosticOutcome")
        if state == "first-run":
            require(outcome == "ContentFocused", "first-run native Home diagnostic must actively focus Setup")
            require(receipt.get("DiagnosticTarget") == "Setup", "first-run native Home diagnostic target changed")
            require(receipt.get("FocusVerified") is True, "first-run native Home focus was not verified")
            require(receipt.get("FocusedAutomationIdAtSample") == expected, "first-run native Home sampled focus changed")
        else:
            require(outcome in {"ContentFocused", "UserFocusPreserved"}, "ready native Home diagnostic outcome is not accepted")
        validate_endpoint(receipt.get("FinalEndpoint"), expected, identity["ProcessId"])

    for capture in captures:
        require(isinstance(capture, dict), "native Home capture receipt must be an object")
        name = capture.get("RelativeFileName")
        state, expected, width, height = expected_files[name]
        require(capture.get("State") == state and capture.get("ExpectedAutomationId") == expected, f"native Home capture state mapping changed: {name}")
        require(capture.get("RunId") == receipt_by_state[state].get("RunId"), f"native Home capture run mapping changed: {name}")
        require(capture.get("DiagnosticOutcome") == receipt_by_state[state].get("DiagnosticOutcome"), f"native Home capture outcome mapping changed: {name}")
        identity = validate_identity(capture.get("Identity"))
        require(identity == validated_identities[state], f"native Home capture lacks full launch identity mapping: {name}")
        require(capture.get("Width") == width and capture.get("Height") == height, f"native Home capture dimensions changed: {name}")
        markers = capture.get("Markers")
        require(isinstance(markers, list) and markers, f"native Home capture has no visual markers: {name}")
        image = path.parent / name
        require(image.is_file(), f"native Home capture is missing: {name}")
        require(capture.get("Sha256") == sha256(image), f"native Home capture hash changed: {name}")
        require(png_dimensions(image) == (width, height), f"native Home PNG dimensions changed: {name}")
        validate_endpoint(capture.get("FocusBeforeCapture"), expected, identity["ProcessId"])
        validate_endpoint(capture.get("FocusAfterCapture"), expected, identity["ProcessId"])

    return {
        "captureCount": len(captures),
        "focusReceiptCount": len(receipts),
        "states": sorted(receipt_by_state),
        "manifest": str(path),
        "harnessRunId": harness_run_id,
    }


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
    native_support.run_command(
        command,
        repo_root=REPO_ROOT,
        timeout=timeout,
        env_overrides=env_overrides,
    )


def terminate_owned_process_tree(root_process_id: int) -> None:
    native_support.terminate_owned_process_tree(root_process_id, repo_root=REPO_ROOT)


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
        for path in evidence_root.glob(f"home-newcomer-*-{invocation_id}/home-acceptance-manifest.json")
        if path.is_file()
    }


def invocation_evidence_directories(invocation_id: str, evidence_root: Path = EVIDENCE_ROOT) -> set[Path]:
    validate_invocation_id(invocation_id)
    if not evidence_root.exists():
        return set()
    matches = set(evidence_root.glob(f"home-newcomer-*-{invocation_id}"))
    matches.update(evidence_root.glob(f".home-newcomer-*-{invocation_id}.partial"))
    return {path.resolve() for path in matches if path.is_dir()}


def partial_evidence_directories() -> list[Path]:
    if not EVIDENCE_ROOT.exists():
        return []
    return sorted(path for path in EVIDENCE_ROOT.iterdir() if path.is_dir() and path.name.endswith(".partial"))


def verify_runner_path(path: Path) -> None:
    resolved = path.resolve()
    root = RUNNER_ROOT.resolve()
    require(resolved != root and root in resolved.parents, f"runner cleanup path escaped its ignored root: {resolved}")


def remove_failed_invocation_evidence(invocation_id: str, evidence_root: Path = EVIDENCE_ROOT) -> None:
    validate_invocation_id(invocation_id)
    root = evidence_root.resolve()
    for run_directory in invocation_evidence_directories(invocation_id, evidence_root):
        expected_accepted = run_directory.name.startswith("home-newcomer-") and run_directory.name.endswith(invocation_id)
        expected_partial = (
            run_directory.name.startswith(".home-newcomer-")
            and run_directory.name.endswith(f"-{invocation_id}.partial")
        )
        require(
            run_directory.parent == root and (expected_accepted or expected_partial),
            f"refusing to remove unowned failed evidence path: {run_directory}",
        )
        if run_directory.exists():
            shutil.rmtree(run_directory)


def shutdown_build_servers() -> None:
    native_support.shutdown_build_servers(REPO_ROOT)


def append_cleanup_error(error: Exception | None, phase: str, cleanup_error: Exception) -> HarnessError:
    return native_support.append_cleanup_error(error, phase, cleanup_error)


def run_acceptance() -> dict[str, Any]:
    baseline = process_census()
    require(not baseline, f"pre-run relevant-process census must be zero, found: {describe_processes(baseline)}")
    partials = partial_evidence_directories()
    require(not partials, f"pre-run native Home evidence contains partial directories: {[path.name for path in partials]}")
    invocation_id = uuid.uuid4().hex
    validate_invocation_id(invocation_id)
    require(
        not invocation_evidence_directories(invocation_id, EVIDENCE_ROOT),
        "fresh runner invocation ID unexpectedly already owns evidence",
    )
    run_root = RUNNER_ROOT / f".{invocation_id}.partial"
    verify_runner_path(run_root)
    run_root.mkdir(parents=True, exist_ok=False)
    trx = run_root / "home-native-visual-focus.trx"
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
            timeout=240,
            env_overrides={
                "ONSLAUGHT_HOME_NATIVE_ACCEPTANCE_RUN_ID": invocation_id,
                "ONSLAUGHT_HOME_NATIVE_EXPECTED_EXE_SHA256": expected_executable_hash,
                "ONSLAUGHT_HOME_NATIVE_EXPECTED_DLL_SHA256": expected_product_hash,
            },
        )
        trx_summary = validate_trx(trx)
        owned_manifests = invocation_manifests(invocation_id, EVIDENCE_ROOT)
        require(len(owned_manifests) == 1, f"native Home invocation must publish exactly one owned manifest, found {len(owned_manifests)}")
        partials = partial_evidence_directories()
        require(not partials, f"native Home run left partial evidence directories: {[path.name for path in partials]}")
        manifest_summary = validate_manifest(
            next(iter(owned_manifests)),
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
                raise HarnessError(f"final relevant-process census must be zero, found: {describe_processes(final_census)}")
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
                remove_failed_invocation_evidence(invocation_id, EVIDENCE_ROOT)
            except Exception as cleanup_error:
                error = append_cleanup_error(error, "owned evidence rollback", cleanup_error)

    if error is not None:
        if isinstance(error, HarnessError):
            raise error
        raise HarnessError(str(error)) from error
    require(result is not None, "native Home acceptance produced no result")
    return result


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print("usage: run_winui_home_native_visual_focus.py", file=sys.stderr)
        return 2
    try:
        result = run_acceptance()
        print("\nWinUI Home native visual/focus acceptance: PASS", flush=True)
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        return 0
    except (HarnessError, subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as exc:
        print(f"WinUI Home native visual/focus acceptance: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
