#!/usr/bin/env python3
"""Validate a safe-copy control input pre/post frame-delta artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "Artifact root must be a JSON object.")
    return value


def object_at(value: Any, key: str) -> dict[str, Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: Any, key: str) -> list[Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def bool_at(value: Any, key: str) -> bool:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return child


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def string_list_at(value: Any, key: str) -> list[str]:
    values = list_at(value, key)
    require(all(isinstance(item, str) for item in values), f"{key} must contain only strings.")
    return [str(item) for item in values]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capture_has_visual_proof(capture: dict[str, Any]) -> bool:
    if capture.get("foregroundMatchesTarget") is True:
        return True
    occlusion = capture.get("occlusion")
    return (
        isinstance(occlusion, dict)
        and occlusion.get("checked") is True
        and occlusion.get("targetFound") is True
        and occlusion.get("occlusionFree") is True
        and occlusion.get("occludingWindowCount") == 0
    )


def capture_name(capture: dict[str, Any]) -> str:
    output_path = string_at(capture, "outputPath")
    return Path(output_path).name.lower()


def is_pre_input_capture(capture: dict[str, Any]) -> bool:
    return capture_name(capture).startswith("safe-copy-pre-input-frame")


def is_post_input_capture(capture: dict[str, Any]) -> bool:
    name = capture_name(capture)
    return name.startswith("safe-copy-after-input-") or (
        name.startswith("safe-copy-frame") and not name.startswith("safe-copy-pre-input-frame")
    )


def verify_capture_file(capture: dict[str, Any], *, require_files: bool) -> None:
    output_path = Path(string_at(capture, "outputPath"))
    if not output_path.exists():
        require(not require_files, f"Capture file is missing: {output_path}")
        return
    expected_size = int_at(capture, "fileSize")
    expected_hash = string_at(capture, "sha256").lower()
    require(output_path.stat().st_size == expected_size, f"Capture file size mismatch: {output_path}")
    require(sha256_file(output_path) == expected_hash, f"Capture file hash mismatch: {output_path}")


def configuration_value(arguments: list[str]) -> int:
    lowered = [arg.lower() for arg in arguments]
    require("-configuration" in lowered, "Launch arguments must include -configuration for this control proof.")
    index = lowered.index("-configuration")
    require(index + 1 < len(arguments), "-configuration must have a following value.")
    try:
        value = int(arguments[index + 1])
    except ValueError as exc:
        raise ArtifactError("-configuration value must be numeric.") from exc
    require(1 <= value <= 4, "-configuration value must be between 1 and 4.")
    return value


def require_level_850_arguments(arguments: list[str]) -> None:
    lowered = [arg.lower() for arg in arguments]
    require("-skipfmv" in lowered, "Launch arguments must include -skipfmv for this level-850 control proof.")
    require("-level" in lowered, "Launch arguments must include -level for this level-850 control proof.")
    index = lowered.index("-level")
    require(index + 1 < len(arguments), "-level must have a following value.")
    try:
        value = int(arguments[index + 1])
    except ValueError as exc:
        raise ArtifactError("-level value must be numeric.") from exc
    require(value == 850, f"Expected -level 850, got {value}.")


def validate_artifact(
    payload: dict[str, Any],
    *,
    expected_controller_configuration: int,
    min_pre_captures: int,
    min_post_captures: int,
    require_visual: bool,
    require_files: bool,
) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    source_options = object_at(source, "saveAndOptions")
    require(bool_at(source_options, "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "Safe copy did not apply required windowed compatibility patch keys.")

    launch = object_at(payload, "launch")
    requested_arguments = string_list_at(launch, "requestedArguments")
    arguments = string_list_at(launch, "arguments")
    require(requested_arguments == arguments, "Launch requestedArguments and arguments differ.")
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")
    require_level_850_arguments(arguments)
    config = configuration_value(arguments)
    require(
        config == expected_controller_configuration,
        f"Expected -configuration {expected_controller_configuration}, got {config}.",
    )

    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")

    input_plan = object_at(payload, "inputPlan")
    require(int_at(input_plan, "inputSequenceCount") >= 1, "Artifact did not plan any scoped input sequence.")
    input_summary = object_at(payload, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 1, "No scoped input sequence was reported sent.")
    require(int_at(input_summary, "inputActionCount") >= 1, "No scoped input actions were reported.")
    require(
        int_at(input_summary, "inputKeyEventsSent") + int_at(input_summary, "inputMouseEventsSent") + int_at(input_summary, "inputWindowMessageEventsSent") >= 1,
        "No scoped input event was reported.",
    )

    inputs = list_at(payload, "input")
    process_id = int_at(launch, "processId")
    hwnd = string_at(launch, "mainWindowHandle").lower()
    sent_inputs = 0
    for item in inputs:
        require(isinstance(item, dict), "Each input result must be an object.")
        if item.get("status") == "sent":
            sent_inputs += 1
            require(item.get("processId") == process_id, "Input process id does not match launched process.")
            require(str(item.get("hwndHex", "")).lower() == hwnd, "Input hwnd does not match launched main window.")
    require(sent_inputs >= 1, "No sent input result matched the launched process/window.")

    capture_plan = object_at(payload, "capturePlan")
    require(int_at(capture_plan, "preInputCaptureCount") >= min_pre_captures, "Capture plan did not request enough pre-input captures.")
    require(int_at(capture_plan, "captureCount") >= min_post_captures, "Capture plan did not request enough post-input captures.")

    captures = list_at(payload, "captures")
    pre_captures: list[dict[str, Any]] = []
    post_captures: list[dict[str, Any]] = []
    visual_count = 0
    for capture in captures:
        require(isinstance(capture, dict), "Each capture must be an object.")
        require(capture.get("status") == "captured", "Each capture must have captured status.")
        require(capture.get("processId") == process_id, "Capture process id does not match launched process.")
        require(str(capture.get("hwndHex", "")).lower() == hwnd, "Capture hwnd does not match launched main window.")
        require(int_at(capture, "fileSize") > 0, "Capture file size must be positive.")
        require(len(string_at(capture, "sha256")) == 64, "Capture sha256 must be present.")
        verify_capture_file(capture, require_files=require_files)
        if capture_has_visual_proof(capture):
            visual_count += 1
        if is_pre_input_capture(capture):
            pre_captures.append(capture)
        elif is_post_input_capture(capture):
            post_captures.append(capture)

    require(len(pre_captures) >= min_pre_captures, f"Expected at least {min_pre_captures} pre-input capture(s).")
    require(len(post_captures) >= min_post_captures, f"Expected at least {min_post_captures} post-input capture(s).")
    if require_visual:
        require(visual_count >= min_pre_captures + min_post_captures, "Not all required pre/post captures have visual proof.")

    pre_hashes = {string_at(capture, "sha256").lower() for capture in pre_captures}
    post_hashes = {string_at(capture, "sha256").lower() for capture in post_captures}
    require(pre_hashes.isdisjoint(post_hashes), "Pre-input and post-input capture hashes did not change.")

    boundary = string_at(payload, "claimBoundary")
    require(
        "do not prove improved runtime control feel" in boundary,
        "Claim boundary must reject improved runtime control-feel proof.",
    )

    return {
        "schema": "winui-control-input-delta-proof.v1",
        "controllerConfiguration": config,
        "preInputCaptureCount": len(pre_captures),
        "postInputCaptureCount": len(post_captures),
        "visualCaptureCount": visual_count,
        "inputSequencesSent": int_at(input_summary, "inputSequencesSent"),
        "inputActionCount": int_at(input_summary, "inputActionCount"),
        "inputKeyEventsSent": int_at(input_summary, "inputKeyEventsSent"),
        "inputMouseEventsSent": int_at(input_summary, "inputMouseEventsSent"),
        "inputWindowMessageEventsSent": int_at(input_summary, "inputWindowMessageEventsSent"),
        "frameHashDelta": True,
        "sourceSaveOptionsUnchanged": True,
        "installedExeUnchanged": True,
        "overrideExeUnchanged": True,
        "noBeaAfterStop": True,
        "claimBoundary": (
            "safe-copy launch/source-safety/managed-stop plus scoped input delivery "
            "and pre/post frame-hash delta only; not improved control-feel proof"
        ),
    }


def capture_fixture(path: Path, *, name: str, data: bytes, process_id: int = 1234, hwnd: str = "0x123") -> dict[str, Any]:
    output = path / name
    output.write_bytes(data)
    return {
        "status": "captured",
        "processId": process_id,
        "hwndHex": hwnd,
        "foregroundMatchesTarget": True,
        "outputPath": str(output),
        "fileSize": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def fixture(root: Path, *, same_frames: bool = False, after_input_only: bool = False) -> dict[str, Any]:
    pre = capture_fixture(root, name="safe-copy-pre-input-frame.png", data=b"before-frame")
    post_data = b"before-frame" if same_frames else b"after-frame"
    post_name = "safe-copy-after-input-01-frame.png" if after_input_only else "safe-copy-frame.png"
    post = capture_fixture(root, name=post_name, data=post_data)
    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {
                "unchanged": True,
            },
        },
        "safeCopy": {
            "patchKeys": ["resolution_gate", "force_windowed"],
        },
        "launch": {
            "processId": 1234,
            "observedAlive": True,
            "mainWindowHandle": "0x123",
            "requestedArguments": ["-skipfmv", "-level", "850", "-configuration", "1"],
            "arguments": ["-skipfmv", "-level", "850", "-configuration", "1"],
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "input": [
            {
                "status": "sent",
                "processId": 1234,
                "hwndHex": "0x123",
            }
        ],
        "inputPlan": {
            "inputSequenceCount": 1,
            "inputStepDelayMs": 60,
            "allowBackgroundWindowMessages": False,
        },
        "inputSummary": {
            "inputSequencesSent": 1,
            "focusedInputSequences": 1,
            "inputActionCount": 3,
            "inputKeyEventsSent": 4,
            "inputSendInputEventsSent": 0,
            "inputScanKeybdEventsSent": 4,
            "inputWindowMessageEventsSent": 0,
            "inputMouseEventsSent": 0,
        },
        "capture": pre,
        "captures": [pre, post],
        "capturePlan": {
            "captureCount": 1,
            "preInputCaptureCount": 1,
            "captureIntervalSeconds": 0,
            "postWindowDelaySeconds": 1,
        },
        "stop": {
            "Success": True,
        },
        "claimBoundary": "Optional control options do not prove improved runtime control feel.",
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        summary = validate_artifact(
            fixture(root),
            expected_controller_configuration=1,
            min_pre_captures=1,
            min_post_captures=1,
            require_visual=True,
            require_files=True,
        )
        require(summary["frameHashDelta"] is True, "Self-test did not report frame hash delta.")

        after_input_summary = validate_artifact(
            fixture(root, after_input_only=True),
            expected_controller_configuration=1,
            min_pre_captures=1,
            min_post_captures=1,
            require_visual=True,
            require_files=True,
        )
        require(after_input_summary["postInputCaptureCount"] == 1, "Self-test did not count after-input capture as post-input.")

        wrong_level = fixture(root)
        wrong_level["launch"]["requestedArguments"] = ["-skipfmv", "-level", "849", "-configuration", "1"]
        wrong_level["launch"]["arguments"] = ["-skipfmv", "-level", "849", "-configuration", "1"]
        try:
            validate_artifact(
                wrong_level,
                expected_controller_configuration=1,
                min_pre_captures=1,
                min_post_captures=1,
                require_visual=True,
                require_files=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected wrong level argument to fail.")

        same = fixture(root, same_frames=True)
        try:
            validate_artifact(
                same,
                expected_controller_configuration=1,
                min_pre_captures=1,
                min_post_captures=1,
                require_visual=True,
                require_files=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected identical pre/post frame hashes to fail.")

        missing_visual = fixture(root)
        for capture in missing_visual["captures"]:
            capture["foregroundMatchesTarget"] = False
            capture["occlusion"] = {
                "checked": True,
                "targetFound": True,
                "occlusionFree": False,
                "occludingWindowCount": 1,
            }
        try:
            validate_artifact(
                missing_visual,
                expected_controller_configuration=1,
                min_pre_captures=1,
                min_post_captures=1,
                require_visual=True,
                require_files=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected missing visual proof to fail.")

        path = root / "artifact.json"
        path.write_text(json.dumps(fixture(root)), encoding="utf-8")
        validate_artifact(
            read_json(path),
            expected_controller_configuration=1,
            min_pre_captures=1,
            min_post_captures=1,
            require_visual=True,
            require_files=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Path to live-safe-copy-runtime-smoke.json")
    parser.add_argument("--expected-controller-configuration", type=int, default=1)
    parser.add_argument("--min-pre-captures", type=int, default=1)
    parser.add_argument("--min-post-captures", type=int, default=1)
    parser.add_argument("--require-visual", action="store_true")
    parser.add_argument("--require-files", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(1 <= args.expected_controller_configuration <= 4, "--expected-controller-configuration must be 1..4.")
        require(args.min_pre_captures >= 1, "--min-pre-captures must be positive.")
        require(args.min_post_captures >= 1, "--min-post-captures must be positive.")
        if args.self_test:
            run_self_test()
            print("WinUI control input-delta artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(
            read_json(Path(args.artifact)),
            expected_controller_configuration=args.expected_controller_configuration,
            min_pre_captures=args.min_pre_captures,
            min_post_captures=args.min_post_captures,
            require_visual=args.require_visual,
            require_files=args.require_files,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI control input-delta artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
