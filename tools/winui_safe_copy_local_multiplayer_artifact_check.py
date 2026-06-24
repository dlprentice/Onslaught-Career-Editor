#!/usr/bin/env python3
"""Validate a safe-copy local multiplayer probe runtime artifact."""

from __future__ import annotations

import argparse
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


def string_list_at(value: Any, key: str) -> list[str]:
    child = list_at(value, key)
    require(all(isinstance(item, str) for item in child), f"{key} must contain only strings.")
    return [str(item) for item in child]


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def capture_has_visual_proof(item: dict[str, Any]) -> bool:
    if item.get("foregroundMatchesTarget") is True:
        return True
    occlusion = item.get("occlusion")
    return (
        isinstance(occlusion, dict)
        and occlusion.get("checked") is True
        and occlusion.get("targetFound") is True
        and occlusion.get("occlusionFree") is True
        and occlusion.get("occludingWindowCount") == 0
    )


def capture_visual_count(captures: list[Any]) -> int:
    count = 0
    for item in captures:
        if isinstance(item, dict) and capture_has_visual_proof(item):
            count += 1
    return count


def foreground_process_ids(captures: list[Any]) -> list[int]:
    ids: list[int] = []
    for item in captures:
        if not isinstance(item, dict):
            continue
        value = item.get("foregroundProcessId")
        if isinstance(value, int) and value not in ids:
            ids.append(value)
    return ids


def validate_artifact(
    payload: dict[str, Any],
    *,
    expected_level_id: int,
    expected_controller_configuration: int | None,
    min_capture_count: int,
    require_visual: bool,
) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    source_save_options = object_at(source, "saveAndOptions")
    require(bool_at(source_save_options, "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "Safe copy did not apply required windowed compatibility patch keys.")

    launch = object_at(payload, "launch")
    requested = string_list_at(launch, "requestedArguments")
    arguments = string_list_at(launch, "arguments")
    expected_arguments = ["-skipfmv", "-level", str(expected_level_id)]
    if expected_controller_configuration is not None:
        require(1 <= expected_controller_configuration <= 4, "Expected controller configuration must be 1..4.")
        expected_arguments += ["-configuration", str(expected_controller_configuration)]
    require(requested == arguments, "Launch requestedArguments and arguments differ.")
    require(arguments == expected_arguments, f"Launch arguments must be exactly: {' '.join(expected_arguments)}")
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")

    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")

    captures = list_at(payload, "captures")
    require(len(captures) >= min_capture_count, f"Expected at least {min_capture_count} capture(s).")
    process_id = int_at(launch, "processId")
    hwnd = string_at(launch, "mainWindowHandle").lower()
    for item in captures:
        require(isinstance(item, dict), "Each capture must be an object.")
        require(item.get("status") == "captured", "Each capture must have captured status.")
        require(item.get("processId") == process_id, "Capture process id does not match launched process.")
        require(str(item.get("hwndHex", "")).lower() == hwnd, "Capture hwnd does not match launched main window.")
        require(int_at(item, "fileSize") > 0, "Capture file size must be positive.")

    visual_capture_count = capture_visual_count(captures)
    visual_proof = visual_capture_count > 0
    if require_visual:
        require(visual_proof, "No capture was foreground-matched or z-order occlusion-free; visual proof is absent.")

    boundary = string_at(payload, "claimBoundary")
    require("unoccluded pixels" in boundary, "Claim boundary must explicitly separate unoccluded-pixel proof.")

    return {
        "schema": EXPECTED_SCHEMA,
        "expectedLevelId": expected_level_id,
        "expectedControllerConfiguration": expected_controller_configuration,
        "launchArguments": arguments,
        "captureCount": len(captures),
        "foregroundCaptureCount": visual_capture_count,
        "foregroundProcessIds": foreground_process_ids(captures),
        "visualProof": visual_proof,
        "sourceSaveOptionsUnchanged": True,
        "installedExeUnchanged": True,
        "overrideExeUnchanged": True,
        "noBeaAfterStop": True,
        "claim": (
            "safe-copy launch/source-safety/managed-stop plus unoccluded visual proof"
            if visual_proof
            else "safe-copy launch/source-safety/managed-stop only"
        ),
    }


def fixture(*, visual: bool = False, occlusion_free: bool = False, controller_configuration: int | None = None) -> dict[str, Any]:
    arguments = ["-skipfmv", "-level", "850"]
    if controller_configuration is not None:
        arguments += ["-configuration", str(controller_configuration)]
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
            "processId": 42464,
            "observedAlive": True,
            "mainWindowHandle": "0x1600d2a",
            "requestedArguments": arguments,
            "arguments": arguments,
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "captures": [
            {
                "status": "captured",
                "processId": 42464,
                "hwndHex": "0x1600d2a",
                "foregroundProcessId": 35596,
                "foregroundMatchesTarget": visual,
                "occlusion": {
                    "checked": True,
                    "targetFound": True,
                    "occlusionFree": occlusion_free,
                    "occludingWindowCount": 0 if occlusion_free else 1,
                },
                "fileSize": 503209,
            }
        ],
        "stop": {
            "Success": True,
        },
        "claimBoundary": "This does not prove gameplay, rendering correctness, visual parity, unoccluded pixels, or rebuild parity.",
    }


def run_self_test() -> None:
    occluded = fixture(visual=False)
    summary = validate_artifact(occluded, expected_level_id=850, expected_controller_configuration=None, min_capture_count=1, require_visual=False)
    require(summary["visualProof"] is False, "Occluded fixture should not report visual proof.")

    try:
        validate_artifact(occluded, expected_level_id=850, expected_controller_configuration=None, min_capture_count=1, require_visual=True)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected require_visual=True to fail for an occluded artifact.")

    visible = fixture(visual=True)
    visible_summary = validate_artifact(visible, expected_level_id=850, expected_controller_configuration=None, min_capture_count=1, require_visual=True)
    require(visible_summary["visualProof"] is True, "Visible fixture should report visual proof.")

    occlusion_free = fixture(occlusion_free=True)
    occlusion_free_summary = validate_artifact(occlusion_free, expected_level_id=850, expected_controller_configuration=None, min_capture_count=1, require_visual=True)
    require(occlusion_free_summary["visualProof"] is True, "Occlusion-free fixture should report visual proof.")

    config_two = fixture(visual=True, controller_configuration=2)
    config_two_summary = validate_artifact(config_two, expected_level_id=850, expected_controller_configuration=2, min_capture_count=1, require_visual=True)
    require(config_two_summary["expectedControllerConfiguration"] == 2, "Config-two fixture should report expected controller configuration.")

    bad = fixture(visual=True)
    bad["launch"]["arguments"] = ["-skipfmv", "-level", "849"]
    try:
        validate_artifact(bad, expected_level_id=850, expected_controller_configuration=None, min_capture_count=1, require_visual=False)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected wrong level id to fail.")

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "artifact.json"
        path.write_text(json.dumps(visible), encoding="utf-8")
        validate_artifact(read_json(path), expected_level_id=850, expected_controller_configuration=None, min_capture_count=1, require_visual=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Path to live-safe-copy-runtime-smoke.json")
    parser.add_argument("--expected-level-id", type=int, default=850)
    parser.add_argument("--expected-controller-configuration", type=int, choices=(1, 2, 3, 4))
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--require-visual", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.expected_level_id > 0, "--expected-level-id must be positive.")
        require(args.min_capture_count > 0, "--min-capture-count must be positive.")
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy local multiplayer artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(
            read_json(Path(args.artifact)),
            expected_level_id=args.expected_level_id,
            expected_controller_configuration=args.expected_controller_configuration,
            min_capture_count=args.min_capture_count,
            require_visual=args.require_visual,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy local multiplayer artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
