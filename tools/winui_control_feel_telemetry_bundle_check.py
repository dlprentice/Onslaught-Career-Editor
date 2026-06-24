#!/usr/bin/env python3
"""Validate a safe-copy control-feel telemetry proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_control_feel_diagnostics_matrix as matrix
import winui_control_input_delta_artifact_check as input_delta


EXPECTED_SCHEMA = "winui-control-feel-telemetry-bundle.v1"
LIVE_RUNTIME_ARTIFACT_NAME = "live-safe-copy-runtime-" + "smoke.json"


class TelemetryBundleError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TelemetryBundleError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    require(isinstance(payload, dict), f"{path} root must be a JSON object.")
    return payload


def object_at(value: Any, key: str) -> dict[str, Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: Any, key: str) -> list[Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str) and child, f"Missing string: {key}")
    return child


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def bool_at(value: Any, key: str) -> bool:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return child


def path_identity(path: Path) -> str:
    return str(path.resolve()).lower()


def artifact_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def launch_process_id(payload: dict[str, Any]) -> int:
    return int_at(object_at(payload, "launch"), "processId")


def capture_hashes(payload: dict[str, Any]) -> set[str]:
    hashes: set[str] = set()
    for capture in list_at(payload, "captures"):
        if isinstance(capture, dict):
            value = capture.get("sha256")
            if isinstance(value, str) and len(value) == 64:
                hashes.add(value.lower())
    return hashes


def validate_no_input_control(
    path: Path,
    *,
    expected_controller_configuration: int,
    require_visual: bool,
    require_files: bool,
) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == input_delta.EXPECTED_SCHEMA, "No-input control has unexpected artifact schema.")

    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "No-input control changed installed BEA.exe hash.")
    require(bool_at(source, "overrideHashUnchanged"), "No-input control changed clean executable override hash.")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "No-input control changed source options/save hashes.")

    safe_copy = object_at(payload, "safeCopy")
    patch_keys = set(input_delta.string_list_at(safe_copy, "patchKeys"))
    require(input_delta.BASE_PATCH_KEYS.issubset(patch_keys), "No-input control lacks required safe-copy patch keys.")

    launch = object_at(payload, "launch")
    arguments = input_delta.string_list_at(launch, "arguments")
    require(
        input_delta.configuration_value(arguments) == expected_controller_configuration,
        f"No-input control must use -configuration {expected_controller_configuration}.",
    )
    require(bool_at(launch, "observedAlive"), "No-input control did not observe copied BEA alive.")

    baseline = object_at(payload, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "No-input control started with a pre-existing BEA process.")
    require(bool_at(baseline, "noBeaAfterStop"), "No-input control left BEA running.")
    require(bool_at(object_at(payload, "stop"), "Success"), "No-input control managed stop failed.")

    input_summary = object_at(payload, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 1, "No-input control must send at least one wait-only sequence.")
    require(int_at(input_summary, "inputKeyEventsSent") == 0, "No-input control sent keyboard events.")
    require(int_at(input_summary, "inputMouseEventsSent") == 0, "No-input control sent mouse events.")
    require(int_at(input_summary, "inputWindowMessageEventsSent") == 0, "No-input control sent window-message input events.")

    wait_actions = 0
    for result in list_at(payload, "input"):
        require(isinstance(result, dict), "No-input result must be an object.")
        require(result.get("status") == "sent", "No-input wait sequence was not reported sent.")
        for action in list_at(result, "actions"):
            require(isinstance(action, dict), "No-input action must be an object.")
            require(action.get("kind") == "wait", "No-input control may contain wait actions only.")
            wait_actions += 1
    require(wait_actions >= 1, "No-input control did not record any wait action.")

    captures = list_at(payload, "captures")
    pre_count = sum(1 for capture in captures if isinstance(capture, dict) and input_delta.is_pre_input_capture(capture))
    post_count = sum(1 for capture in captures if isinstance(capture, dict) and input_delta.is_post_input_capture(capture))
    visual_count = 0
    for capture in captures:
        require(isinstance(capture, dict), "No-input capture must be an object.")
        require(capture.get("status") == "captured", "No-input capture must have captured status.")
        if require_files:
            input_delta.verify_capture_file(capture, require_files=True)
        if input_delta.capture_has_visual_proof(capture):
            visual_count += 1
    require(pre_count >= 1, "No-input control needs at least one pre-input capture.")
    require(post_count >= 1, "No-input control needs at least one post/wait capture.")
    if require_visual:
        require(visual_count >= pre_count + post_count, "No-input control lacks required visual proof for pre/post captures.")

    boundary = string_at(payload, "claimBoundary")
    require("do not prove improved runtime control feel" in boundary, "No-input control boundary must reject improved feel proof.")

    hashes = capture_hashes(payload)
    require(len(hashes) > 1, "No-input control must observe at least two distinct frame hashes.")

    return {
        "artifact": str(path),
        "artifactHash": artifact_hash(path),
        "controllerConfiguration": expected_controller_configuration,
        "waitOnlyInputSequences": int_at(input_summary, "inputSequencesSent"),
        "waitOnlyActionCount": wait_actions,
        "preInputCaptureCount": pre_count,
        "postInputCaptureCount": post_count,
        "visualCaptureCount": visual_count,
        "frameHashDeltaObserved": len(hashes) > 1,
    }


def validate_bundle(
    assignments: dict[str, Path],
    *,
    repeat_baseline: Path,
    no_input_control: Path,
    require_visual: bool,
    require_files: bool,
) -> dict[str, Any]:
    matrix_summary = matrix.validate_matrix(assignments, require_visual=require_visual)

    scenario_summaries: list[dict[str, Any]] = []
    for scenario in matrix.SCENARIOS:
        path = assignments[scenario.scenario_id]
        payload = read_json(path)
        delta = input_delta.validate_artifact(
            payload,
            expected_controller_configuration=scenario.controller_config,
            min_pre_captures=1,
            min_post_captures=1,
            require_visual=require_visual,
            require_files=require_files,
        )
        scenario_summaries.append(
            {
                "scenarioId": scenario.scenario_id,
                "artifact": str(path),
                "artifactHash": artifact_hash(path),
                "controllerConfiguration": scenario.controller_config,
                "controlOptionsProof": next(
                    item["controlOptionsProof"]
                    for item in matrix_summary["scenarios"]
                    if item["scenarioId"] == scenario.scenario_id
                ),
                "preInputCaptureCount": delta["preInputCaptureCount"],
                "postInputCaptureCount": delta["postInputCaptureCount"],
                "visualCaptureCount": delta["visualCaptureCount"],
                "inputActionCount": delta["inputActionCount"],
                "inputKeyEventsSent": delta["inputKeyEventsSent"],
            }
        )

    baseline_path = assignments["baseline_config1"]
    repeat_payload = read_json(repeat_baseline)
    repeat_delta = input_delta.validate_artifact(
        repeat_payload,
        expected_controller_configuration=1,
        min_pre_captures=1,
        min_post_captures=1,
        require_visual=require_visual,
        require_files=require_files,
    )
    baseline_payload = read_json(baseline_path)
    require(path_identity(repeat_baseline) != path_identity(baseline_path), "Repeated baseline must be a distinct artifact path.")
    require(launch_process_id(repeat_payload) != launch_process_id(baseline_payload), "Repeated baseline must use a distinct copied BEA process.")
    require(
        capture_hashes(repeat_payload) != capture_hashes(baseline_payload),
        "Repeated baseline must carry a distinct capture-hash set.",
    )

    no_input = validate_no_input_control(
        no_input_control,
        expected_controller_configuration=1,
        require_visual=require_visual,
        require_files=require_files,
    )

    return {
        "schema": EXPECTED_SCHEMA,
        "runtimeProfile": "original-binary-copied-local-control-telemetry",
        "slotCapacity": 4,
        "minimumArchitectureAcceptanceSlots": 4,
        "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
        "metadataOnlySlots": ["P3", "P4"],
        "rejectedGameplayRouteSlots": ["P3", "P4"],
        "gameInputSentByNSlotScheduler": False,
        "hostHelperInputSent": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "scenarioCount": len(scenario_summaries),
        "inputDeltaScenarioCount": len(scenario_summaries),
        "matrixComplete": matrix_summary["matrixComplete"],
        "visualRequired": require_visual,
        "scenarioIds": [item["scenarioId"] for item in scenario_summaries],
        "controllerConfigurations": [item["controllerConfiguration"] for item in scenario_summaries],
        "scenarios": scenario_summaries,
        "repeatedBaseline": {
            "artifact": str(repeat_baseline),
            "artifactHash": artifact_hash(repeat_baseline),
            "controllerConfiguration": 1,
            "processDistinctFromBaseline": True,
            "captureHashSetDistinctFromBaseline": True,
            "preInputCaptureCount": repeat_delta["preInputCaptureCount"],
            "postInputCaptureCount": repeat_delta["postInputCaptureCount"],
            "visualCaptureCount": repeat_delta["visualCaptureCount"],
        },
        "noInputControl": no_input,
        "claimBoundary": (
            "This bundle proves safe-copy control-options materialization plus scoped keyboard input/capture telemetry "
            "coverage across the five control diagnostic scenarios, one distinct repeated baseline, and one wait-only "
            "no-input control. It does not prove improved control feel, analog deadzone behavior, look curves, camera "
            "response quality, physical gamepad behavior, online multiplayer, active P3/P4 original-binary gameplay, "
            "deterministic sync, gameplay parity, rebuild parity, or no-noticeable-difference parity."
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def make_capture(root: Path, name: str, data: bytes, *, process_id: int) -> dict[str, Any]:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {
        "status": "captured",
        "processId": process_id,
        "hwndHex": "0x123",
        "foregroundMatchesTarget": True,
        "outputPath": str(path),
        "fileSize": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def make_artifact(root: Path, scenario: matrix.Scenario, *, process_id: int, repeat: bool = False) -> Path:
    capture_root = root / "capture"
    before = f"{scenario.scenario_id}-before-{process_id}".encode("ascii")
    after = f"{scenario.scenario_id}-after-{process_id}".encode("ascii")
    pre = make_capture(capture_root, "safe-copy-pre-input-frame.png", before, process_id=process_id)
    post = make_capture(capture_root, "safe-copy-after-input-01-frame.png", after, process_id=process_id)
    payload = input_delta.fixture(root, after_input_only=True)
    payload["source"]["installedHashUnchanged"] = True
    payload["source"]["overrideHashUnchanged"] = True
    payload["safeCopy"]["patchKeys"] = sorted(input_delta.BASE_PATCH_KEYS)
    payload["launch"]["processId"] = process_id
    payload["launch"]["mainWindowHandle"] = "0x123"
    payload["launch"]["requestedArguments"] = ["-skipfmv", "-level", "850", "-configuration", str(scenario.controller_config)]
    payload["launch"]["arguments"] = ["-skipfmv", "-level", "850", "-configuration", str(scenario.controller_config)]
    payload["input"][0]["processId"] = process_id
    payload["input"][0]["hwndHex"] = "0x123"
    payload["capture"] = pre
    payload["captures"] = [pre, post]
    payload["capturePlan"]["captureAfterEachInputSequence"] = True
    payload["safeCopy"]["controlOptions"] = None
    if scenario.requires_persisted_config or scenario.requires_mouse_sensitivity:
        payload["safeCopy"]["controlOptions"] = matrix.control_fixture(
            scenario.controller_config,
            sharpen=scenario.requires_mouse_sensitivity,
        )
    if repeat:
        payload["claimBoundary"] += " Repeated baseline artifact; still does not prove improved runtime control feel."
    path = root / LIVE_RUNTIME_ARTIFACT_NAME
    write_json(path, payload)
    return path


def make_no_input_artifact(root: Path) -> Path:
    process_id = 9001
    capture_root = root / "capture"
    pre = make_capture(capture_root, "safe-copy-pre-input-frame.png", b"wait-before", process_id=process_id)
    post = make_capture(capture_root, "safe-copy-after-input-01-frame.png", b"wait-after", process_id=process_id)
    payload = input_delta.fixture(root, after_input_only=True)
    payload["safeCopy"]["patchKeys"] = sorted(input_delta.BASE_PATCH_KEYS)
    payload["launch"]["processId"] = process_id
    payload["launch"]["mainWindowHandle"] = "0x123"
    payload["launch"]["requestedArguments"] = ["-skipfmv", "-level", "850", "-configuration", "1"]
    payload["launch"]["arguments"] = ["-skipfmv", "-level", "850", "-configuration", "1"]
    payload["input"] = [
        {
            "schemaVersion": "game-window-input.v1",
            "status": "sent",
            "processId": process_id,
            "hwndHex": "0x123",
            "focused": True,
            "actionCount": 1,
            "keyEventsSent": 0,
            "sendInputEventsSent": 0,
            "scanKeybdEventsSent": 0,
            "windowMessageEventsSent": 0,
            "mouseEventsSent": 0,
            "actions": [
                {
                    "kind": "wait",
                    "key": None,
                    "virtualKey": None,
                    "durationMs": 500,
                }
            ],
        }
    ]
    payload["inputPlan"]["inputSequenceCount"] = 1
    payload["inputSummary"] = {
        "inputSequencesSent": 1,
        "focusedInputSequences": 1,
        "inputActionCount": 1,
        "inputKeyEventsSent": 0,
        "inputSendInputEventsSent": 0,
        "inputScanKeybdEventsSent": 0,
        "inputWindowMessageEventsSent": 0,
        "inputMouseEventsSent": 0,
    }
    payload["capture"] = pre
    payload["captures"] = [pre, post]
    payload["capturePlan"]["captureAfterEachInputSequence"] = True
    payload["claimBoundary"] += " Wait-only no-input control; still does not prove improved runtime control feel."
    path = root / LIVE_RUNTIME_ARTIFACT_NAME
    write_json(path, payload)
    return path


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        assignments: dict[str, Path] = {}
        process_id = 1000
        for scenario in matrix.SCENARIOS:
            process_id += 1
            assignments[scenario.scenario_id] = make_artifact(root / scenario.scenario_id, scenario, process_id=process_id)
        repeat = make_artifact(root / "baseline_repeat", matrix.SCENARIOS[0], process_id=2001, repeat=True)
        no_input = make_no_input_artifact(root / "no_input")

        summary = validate_bundle(
            assignments,
            repeat_baseline=repeat,
            no_input_control=no_input,
            require_visual=True,
            require_files=True,
        )
        require(summary["scenarioCount"] == len(matrix.SCENARIOS), "Self-test scenario count mismatch.")
        require(summary["inputDeltaScenarioCount"] == len(matrix.SCENARIOS), "Self-test input-delta count mismatch.")
        require(summary["slotCapacity"] == 4, "Self-test slot-capacity boundary mismatch.")
        require(summary["acceptedOriginalBinaryGameplaySlots"] == ["P1", "P2"], "Self-test accepted slot boundary mismatch.")
        require(summary["metadataOnlySlots"] == ["P3", "P4"], "Self-test metadata-only slot boundary mismatch.")
        require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "Self-test must not claim N-player runtime proof.")
        require(summary["activeP3P4OriginalBinaryGameplayProof"] is False, "Self-test must not claim active P3/P4 gameplay.")
        require(summary["repeatedBaseline"]["processDistinctFromBaseline"] is True, "Self-test repeat baseline not distinct.")
        require(summary["noInputControl"]["waitOnlyActionCount"] == 1, "Self-test no-input wait count mismatch.")

        bad_level_path = make_artifact(root / "bad_level", matrix.SCENARIOS[0], process_id=9100)
        bad_level = read_json(bad_level_path)
        bad_level["launch"]["requestedArguments"] = ["-skipfmv", "-level", "849", "-configuration", "1"]
        bad_level["launch"]["arguments"] = ["-skipfmv", "-level", "849", "-configuration", "1"]
        write_json(bad_level_path, bad_level)
        bad_assignments = dict(assignments)
        bad_assignments["baseline_config1"] = bad_level_path
        try:
            validate_bundle(
                bad_assignments,
                repeat_baseline=repeat,
                no_input_control=no_input,
                require_visual=True,
                require_files=True,
            )
        except (TelemetryBundleError, input_delta.ArtifactError):
            pass
        else:
            raise TelemetryBundleError("Self-test expected wrong level argument to fail.")

        no_delta_path = make_no_input_artifact(root / "no_input_no_delta")
        no_delta = read_json(no_delta_path)
        no_delta["captures"][1]["sha256"] = no_delta["captures"][0]["sha256"]
        no_delta["captures"][1]["fileSize"] = no_delta["captures"][0]["fileSize"]
        no_delta["captures"][1]["outputPath"] = no_delta["captures"][0]["outputPath"]
        write_json(no_delta_path, no_delta)
        try:
            validate_bundle(
                assignments,
                repeat_baseline=repeat,
                no_input_control=no_delta_path,
                require_visual=True,
                require_files=True,
            )
        except TelemetryBundleError:
            pass
        else:
            raise TelemetryBundleError("Self-test expected no-input unchanged frame hashes to fail.")

        bad_no_input = read_json(no_input)
        bad_no_input["inputSummary"]["inputKeyEventsSent"] = 1
        write_json(no_input, bad_no_input)
        try:
            validate_bundle(
                assignments,
                repeat_baseline=repeat,
                no_input_control=no_input,
                require_visual=True,
                require_files=True,
            )
        except TelemetryBundleError:
            pass
        else:
            raise TelemetryBundleError("Self-test expected no-input keyboard event to fail.")


def parse_assignment(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("--artifact must be SCENARIO_ID=PATH.")
    scenario_id, path = raw.split("=", 1)
    scenario_id = scenario_id.strip()
    if not scenario_id:
        raise argparse.ArgumentTypeError("Scenario id may not be empty.")
    return scenario_id, Path(path.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", action="append", default=[], type=parse_assignment, help="Scenario assignment in the form scenario_id=<runtime-artifact-json>")
    parser.add_argument("--repeat-baseline", help="Path to a second baseline_config1 input-delta artifact.")
    parser.add_argument("--no-input-control", help="Path to a wait-only no-input control artifact.")
    parser.add_argument("--require-visual", action="store_true")
    parser.add_argument("--require-files", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI control-feel telemetry bundle checker self-test: PASS")
            return 0

        assignments = dict(args.artifact)
        require(bool(assignments), "Provide --artifact scenario_id=path entries or --self-test.")
        require(bool(args.repeat_baseline), "Provide --repeat-baseline.")
        require(bool(args.no_input_control), "Provide --no-input-control.")
        summary = validate_bundle(
            assignments,
            repeat_baseline=Path(str(args.repeat_baseline)),
            no_input_control=Path(str(args.no_input_control)),
            require_visual=args.require_visual,
            require_files=args.require_files,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (TelemetryBundleError, matrix.MatrixError, input_delta.ArtifactError) as exc:
        print(f"WinUI control-feel telemetry bundle check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
