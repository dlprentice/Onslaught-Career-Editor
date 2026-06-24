#!/usr/bin/env python3
"""Validate a safe-copy Enhanced Profile Preview runtime artifact."""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_PROFILE_ID = "enhanced-edition-preview"
EXPECTED_PROFILE_NAME = "Enhanced Profile Preview"
EXPECTED_REQUESTED_KEYS = {
    "resolution_gate",
    "force_windowed",
    "extra_graphics_default_on",
    "ignore_cardid_tweak_overrides",
    "version_overlay_use_patched_format_pointer",
    "frontend_clear_screen_dark_red",
    "goodies_gallery_display_unlock",
}
EXPECTED_EXPANDED_KEYS = EXPECTED_REQUESTED_KEYS | {
    "version_overlay_patched_format_cave_string",
}
EXCLUDED_KEYS = {
    "skip_auto_toggle",
    "free_camera_aurore_gate_bypass",
    "frontend_clear_screen_dark_green",
    "frontend_clear_screen_black",
}
EXPECTED_MOUSE_SENSITIVITY = 2.25
MOUSE_SENSITIVITY_OFFSET = 0x26C2
CONTROLLER_CONFIG_P1_OFFSET = 0x24B6
CONTROLLER_CONFIG_P2_OFFSET = 0x24BA


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


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def number_at(value: Any, key: str) -> float:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, (int, float)), f"Missing number: {key}")
    return float(child)


def string_set_at(value: Any, key: str) -> set[str]:
    raw = list_at(value, key)
    require(all(isinstance(item, str) for item in raw), f"{key} must contain only strings.")
    return {str(item) for item in raw}


def arg_list(value: Any, key: str) -> list[str]:
    raw = list_at(value, key)
    require(all(isinstance(item, str) for item in raw), f"{key} must contain only strings.")
    return [str(item) for item in raw]


def range_intersects_offset(diff_range: Any, offset_to_check: int) -> bool:
    if not isinstance(diff_range, dict):
        return False
    offset = diff_range.get("offset")
    length = diff_range.get("length")
    if not isinstance(offset, int) or not isinstance(length, int):
        return False
    return offset <= offset_to_check + 3 and offset + length > offset_to_check


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
    return sum(1 for item in captures if isinstance(item, dict) and capture_has_visual_proof(item))


def validate_artifact(payload: dict[str, Any], *, require_visual: bool) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    source_options = object_at(source, "saveAndOptions")
    require(bool_at(source_options, "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    require(string_at(safe_copy, "ProfilePresetId") == EXPECTED_PROFILE_ID, "Artifact did not record the enhanced profile id.")
    require(string_at(safe_copy, "ProfilePresetDisplayName") == EXPECTED_PROFILE_NAME, "Artifact did not record the enhanced profile display name.")
    proof_status = string_at(safe_copy, "ProfilePresetProofStatus")
    require("Proof-bounded preset" in proof_status, "Profile proof status must be proof-bounded.")
    require("not a full overhaul" in proof_status, "Profile proof status must reject full-overhaul claims.")
    require("online mode" in proof_status, "Profile proof status must reject online-mode claims.")
    require("control-feel fix" in proof_status, "Profile proof status must reject control-feel claims.")
    require("gameplay parity" in proof_status, "Profile proof status must reject gameplay-parity claims.")
    require(int(number_at(safe_copy, "ProfileDefaultControllerConfiguration")) == 1, "Enhanced profile default controller configuration must be 1.")
    require(bool_at(safe_copy, "ProfileDefaultPersistControllerConfigInOptions"), "Enhanced profile must default copied controller-config persistence on.")
    require(bool_at(safe_copy, "ProfileDefaultSharpenMouseLook"), "Enhanced profile must default copied mouse-look sharpening on.")

    requested_patch_keys = string_set_at(safe_copy, "requestedPatchKeys")
    expanded_patch_keys = string_set_at(safe_copy, "patchKeys")
    require(requested_patch_keys == EXPECTED_REQUESTED_KEYS, "Requested patch keys do not match Enhanced Profile Preview.")
    require(expanded_patch_keys == EXPECTED_EXPANDED_KEYS, "Expanded patch keys do not match Enhanced Profile Preview dependencies.")
    require(not (requested_patch_keys | expanded_patch_keys) & EXCLUDED_KEYS, "Enhanced artifact includes excluded experimental/alternate rows.")

    control = object_at(safe_copy, "controlOptions")
    require(bool_at(control, "requestedSharperMouseLook"), "Enhanced artifact must request sharper copied mouse look.")
    require(bool_at(control, "requestedPersistedControllerConfig"), "Enhanced artifact must persist copied controller config.")
    require(int(number_at(control, "requestedControllerConfig")) == 1, "Enhanced artifact must request controller config 1.")
    require(int(number_at(control, "observedControllerConfigP1")) == 1, "Observed P1 config must be 1.")
    require(int(number_at(control, "observedControllerConfigP2")) == 1, "Observed P2 config must be 1.")
    require(math.isclose(number_at(control, "MouseSensitivity"), EXPECTED_MOUSE_SENSITIVITY, rel_tol=0.0, abs_tol=0.0001), "Mouse sensitivity read-back was not 2.25.")
    require(string_at(control, "ProofStatus") == "options_byte_materialized_only", "Control options proof status must stay materialization-only.")
    require(string_at(control, "proofLever") == "copied-defaultoptions-mouse-sensitivity-and-controller-config", "Control proof lever is wrong.")
    require(bool_at(control, "changedAfterPrepare"), "Copied defaultoptions hash did not change after prepare.")
    changed_ranges = list_at(control, "changedRanges")
    require(any(range_intersects_offset(item, MOUSE_SENSITIVITY_OFFSET) for item in changed_ranges), "Changed ranges do not cover mouse sensitivity.")
    if int(number_at(control, "requestedControllerConfig")) != 1:
        require(any(range_intersects_offset(item, CONTROLLER_CONFIG_P1_OFFSET) for item in changed_ranges), "Changed ranges do not cover P1 controller config.")
        require(any(range_intersects_offset(item, CONTROLLER_CONFIG_P2_OFFSET) for item in changed_ranges), "Changed ranges do not cover P2 controller config.")
    require(len(list_at(control, "backups")) >= 1, "Control-options mutation did not record a backup.")

    launch = object_at(payload, "launch")
    requested_arguments = arg_list(launch, "requestedArguments")
    arguments = arg_list(launch, "arguments")
    require(requested_arguments == arguments, "Launch requestedArguments and arguments differ.")
    require(arguments == ["-skipfmv", "-configuration", "1"], "Enhanced runtime proof must launch with config 1 only.")

    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")

    captures = list_at(payload, "captures")
    visual_capture_count = capture_visual_count(captures)
    if require_visual:
        require(visual_capture_count > 0, "No capture was foreground-matched or z-order occlusion-free; visual proof is absent.")

    boundary = string_at(payload, "claimBoundary")
    require("not prove improved runtime control feel" in boundary, "Claim boundary must reject runtime control-feel proof.")
    require("unoccluded pixels" in boundary, "Claim boundary must separate unoccluded-pixel proof.")

    return {
        "schema": EXPECTED_SCHEMA,
        "profilePresetId": EXPECTED_PROFILE_ID,
        "requestedPatchKeys": sorted(requested_patch_keys),
        "expandedPatchKeys": sorted(expanded_patch_keys),
        "controllerConfiguration": 1,
        "mouseSensitivity": EXPECTED_MOUSE_SENSITIVITY,
        "foregroundCaptureCount": visual_capture_count,
        "visualProof": visual_capture_count > 0,
        "sourceSaveOptionsUnchanged": True,
        "installedExeUnchanged": True,
        "overrideExeUnchanged": True,
        "noBeaAfterStop": True,
        "claim": "safe-copy enhanced-preview profile/source-safety/managed-stop only",
    }


def valid_fixture(*, visual: bool = False, occlusion_free: bool = False) -> dict[str, Any]:
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
            "ProfilePresetId": EXPECTED_PROFILE_ID,
            "ProfilePresetDisplayName": EXPECTED_PROFILE_NAME,
            "ProfilePresetProofStatus": "Proof-bounded preset over reversible rows; not a full overhaul, online mode, control-feel fix, or gameplay parity claim.",
            "ProfileDefaultControllerConfiguration": 1,
            "ProfileDefaultPersistControllerConfigInOptions": True,
            "ProfileDefaultSharpenMouseLook": True,
            "requestedPatchKeys": sorted(EXPECTED_REQUESTED_KEYS),
            "patchKeys": sorted(EXPECTED_EXPANDED_KEYS),
            "controlOptions": {
                "requestedSharperMouseLook": True,
                "requestedPersistedControllerConfig": True,
                "requestedControllerConfig": 1,
                "proofLever": "copied-defaultoptions-mouse-sensitivity-and-controller-config",
                "MouseSensitivity": 2.25,
                "observedControllerConfigP1": 1,
                "observedControllerConfigP2": 1,
                "ProofStatus": "options_byte_materialized_only",
                "changedAfterPrepare": True,
                "changedRanges": [
                    {"offset": 0x24B6, "length": 1},
                    {"offset": 0x24BA, "length": 1},
                    {"offset": 0x26C4, "length": 2},
                ],
                "backups": [{"relativePath": "defaultoptions.bea.bak"}],
            },
        },
        "launch": {
            "requestedArguments": ["-skipfmv", "-configuration", "1"],
            "arguments": ["-skipfmv", "-configuration", "1"],
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "captures": [
            {
                "status": "captured",
                "foregroundMatchesTarget": visual,
                "occlusion": {
                    "checked": True,
                    "targetFound": True,
                    "occlusionFree": occlusion_free,
                    "occludingWindowCount": 0 if occlusion_free else 1,
                },
                "fileSize": 1,
            }
        ],
        "stop": {
            "Success": True,
        },
        "claimBoundary": "This does not prove improved runtime control feel, gameplay, rendering correctness, visual parity, unoccluded pixels, or rebuild parity.",
    }


def run_self_test() -> None:
    occluded = valid_fixture(visual=False)
    summary = validate_artifact(occluded, require_visual=False)
    require(summary["visualProof"] is False, "Occluded fixture should not report visual proof.")

    try:
        validate_artifact(occluded, require_visual=True)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected require_visual=True to fail for an occluded artifact.")

    visible = valid_fixture(visual=True)
    visible_summary = validate_artifact(visible, require_visual=True)
    require(visible_summary["visualProof"] is True, "Visible fixture should report visual proof.")

    occlusion_free = valid_fixture(occlusion_free=True)
    occlusion_free_summary = validate_artifact(occlusion_free, require_visual=True)
    require(occlusion_free_summary["visualProof"] is True, "Occlusion-free fixture should report visual proof.")

    no_op_config = valid_fixture(visual=True)
    no_op_config["safeCopy"]["controlOptions"]["changedRanges"] = [
        {"offset": 0x26C4, "length": 2},
    ]
    validate_artifact(no_op_config, require_visual=True)

    bad = valid_fixture(visual=True)
    bad["safeCopy"]["requestedPatchKeys"].append("skip_auto_toggle")
    try:
        validate_artifact(bad, require_visual=False)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected excluded key to fail.")

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "artifact.json"
        path.write_text(json.dumps(visible), encoding="utf-8")
        validate_artifact(read_json(path), require_visual=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Path to live-safe-copy-runtime-smoke.json")
    parser.add_argument("--require-visual", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI Enhanced Preview runtime artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(read_json(Path(args.artifact)), require_visual=args.require_visual)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI Enhanced Preview runtime artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
