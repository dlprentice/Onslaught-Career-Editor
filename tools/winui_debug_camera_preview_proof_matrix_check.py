#!/usr/bin/env python3
"""Validate the WinUI Debug Camera Preview proof-boundary consistency matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import winui_safe_copy_free_camera_key_census_artifact_check as key_census_checker
import winui_safe_copy_free_camera_movement_artifact_check as movement_checker
import winui_safe_copy_free_camera_pause_context_artifact_check as pause_context_checker

BASE_KEYS = ["resolution_gate", "force_windowed"]
GATE_KEY = "free_camera_aurore_gate_bypass"
PROFILE_ID = "debug-camera-preview"
PROFILE_HOOK = "free_camera_keyboard_forward_q_hook"
PROFILE_CAVE = "free_camera_keyboard_forward_q_cave"

HOOK_ROWS = {
    "forward": ("free_camera_keyboard_forward_q_hook", "free_camera_keyboard_forward_q_cave", "winui_free_camera_q_forward_runtime_2026-06-18.md"),
    "backward": ("free_camera_keyboard_backward_q_hook", "free_camera_keyboard_backward_q_cave", "winui_free_camera_q_backward_runtime_2026-06-18.md"),
    "strafe-left": ("free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_left_q_cave", "winui_free_camera_q_strafe_left_runtime_2026-06-18.md"),
    "strafe-right": ("free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_strafe_right_q_cave", "winui_free_camera_q_strafe_right_runtime_2026-06-18.md"),
    "yaw-left": ("free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_left_q_cave", "winui_free_camera_q_yaw_left_runtime_2026-06-18.md"),
    "yaw-right": ("free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_yaw_right_q_cave", "winui_free_camera_q_yaw_right_runtime_2026-06-18.md"),
    "pitch-up": ("free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_up_q_cave", "winui_free_camera_q_pitch_up_runtime_2026-06-18.md"),
    "pitch-down": ("free_camera_keyboard_pitch_down_q_hook", "free_camera_keyboard_pitch_down_q_cave", "winui_free_camera_q_pitch_down_runtime_2026-06-18.md"),
}

DOC_TOKENS = {
    "roadmap/debug-camera-preview-proof-matrix.v1.json": [
        '"schemaVersion": "debug-camera-preview-proof-matrix.v1"',
        '"checkerScope": "public-proof-boundary-consistency-not-runtime-artifact-revalidation"',
        '"movementProofRows": 8',
        '"pauseContextProofRows": 2',
        '"keyCensusProofRows": 1',
    ],
    "CURRENT_CAPABILITIES.md": [
        "Debug camera proof-boundary matrix: the public consistency guard records eight individual Q-key remap rows with accepted copied-runtime CDB movement/orientation proof.",
        "It does not revalidate private runtime artifacts.",
        "Pause-context proof currently covers Q-forward and Q-backward only; key-census proof currently covers Q-forward only.",
    ],
    "roadmap/mod-patch-runtime-rebuild-register.md": [
        "2026-06-22 Debug Camera Preview proof-matrix addendum",
        "movementProofRows=8",
        "pauseContextProofRows=2",
        "keyCensusProofRows=1",
    ],
    "release/readiness/winui_debug_camera_preview_proof_matrix_2026-06-22.md": [
        "movementProofRows=8",
        "pauseContextProofRows=2",
        "keyCensusProofRows=1",
        "Preset-selected rows",
        "Manual-only rows",
        "not a full free-camera control scheme",
        "not private runtime artifact revalidation",
    ],
    "OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml": [
        "PatchBenchDebugCameraProofMatrixStatus",
        "Debug Camera Preview selects the camera toggle plus one Q-forward movement test.",
        "Debug Camera Preview keeps the other camera-key experiments manual so you can opt into them one at a time.",
        "Use this preview as a small camera-control trial, not a full camera overhaul.",
        "Some camera-key combinations still need broader menu and pause testing before they become presets.",
    ],
    "OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs": [
        "PatchBenchDebugCameraProofMatrixStatus",
        "Debug Camera Preview selects the camera toggle plus one Q-forward movement test.",
        "Debug Camera Preview keeps the other camera-key experiments manual so you can opt into them one at a time.",
    ],
    "package.json": [
        '"test:winui-debug-camera-preview-proof-matrix"',
    ],
}


class MatrixError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def read_json(path: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must be a JSON object")
    return value


def assert_text_tokens() -> None:
    for path, tokens in DOC_TOKENS.items():
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(token in text, f"{path} missing token: {token}")


def assert_profile_catalog() -> dict[str, Any]:
    catalog = read_json("patches/catalog/safe-copy-profiles.v1.json")
    profiles = catalog.get("profiles")
    require(isinstance(profiles, list), "safe-copy profile catalog missing profiles list")
    profile = next((item for item in profiles if isinstance(item, dict) and item.get("id") == PROFILE_ID), None)
    require(isinstance(profile, dict), "missing debug-camera-preview profile")
    require(profile.get("patch_keys") == [*BASE_KEYS, GATE_KEY, PROFILE_HOOK], "debug profile selected key set changed")
    modules = profile.get("modules")
    require(isinstance(modules, list), "debug profile missing modules")
    module_ids = [item.get("id") for item in modules if isinstance(item, dict)]
    require(module_ids == ["windowed-compatibility", "debug-camera-q-forward"], "debug profile module set changed")
    module = next(item for item in modules if isinstance(item, dict) and item.get("id") == "debug-camera-q-forward")
    require("Q-forward" in str(module.get("claim_boundary", "")), "debug module claim boundary must stay Q-forward scoped")
    require("No full free-camera control scheme proof." in module.get("non_claims", []), "debug module missing full-control non-claim")
    return profile


def assert_patch_catalog() -> None:
    catalog = read_json("patches/catalog/patches.v2.json")
    patches = catalog.get("patches")
    require(isinstance(patches, list), "patch catalog missing patches list")
    by_id = {item.get("id"): item for item in patches if isinstance(item, dict)}
    hook_keys = {hook for hook, _, _ in HOOK_ROWS.values()}
    cave_keys = {cave for _, cave, _ in HOOK_ROWS.values()}

    require(GATE_KEY in by_id, "missing free-camera gate bypass row")
    require(set(by_id) >= hook_keys | cave_keys, "missing one or more free-camera hook/cave rows")

    for mode, (hook, cave, _readiness) in HOOK_ROWS.items():
        hook_spec = by_id[hook]
        cave_spec = by_id[cave]
        require(hook_spec.get("selectability") == "experimental_visible", f"{hook} must stay visible experimental")
        require(cave_spec.get("selectability") == "hidden_companion", f"{cave} must stay hidden companion")
        require(hook_spec.get("exclusive_group") == "free_camera_keyboard_q_remap", f"{hook} exclusive group changed")
        require(hook_spec.get("requires_windowed_pair") is True, f"{hook} must require windowed pair")
        require(cave_spec.get("requires_windowed_pair") is True, f"{cave} must require windowed pair")
        require(set(hook_spec.get("dependencies", [])) == {GATE_KEY, cave}, f"{hook} dependency set changed")
        require(set(hook_spec.get("conflicts", [])) == hook_keys - {hook}, f"{hook} conflict set changed")
        eligible = set(hook_spec.get("preset_eligibility", []))
        if mode == "forward":
            require(PROFILE_ID in eligible, "Q-forward hook must remain eligible for Debug Camera Preview")
        else:
            require(PROFILE_ID not in eligible, f"{hook} must stay manual-only for Debug Camera Preview")


def assert_matrix_contract() -> None:
    matrix = read_json("roadmap/debug-camera-preview-proof-matrix.v1.json")
    require(matrix.get("schemaVersion") == "debug-camera-preview-proof-matrix.v1", "matrix schema changed")
    require(matrix.get("checkerScope") == "public-proof-boundary-consistency-not-runtime-artifact-revalidation", "matrix checker scope changed")
    require(matrix.get("profileId") == PROFILE_ID, "matrix profile id changed")
    require(matrix.get("profileSelectedPatchKeys") == [*BASE_KEYS, GATE_KEY, PROFILE_HOOK], "matrix selected profile keys changed")
    require(matrix.get("expandedProfilePatchKeys") == [*BASE_KEYS, GATE_KEY, PROFILE_CAVE, PROFILE_HOOK], "matrix expanded profile keys changed")
    require(matrix.get("movementProofRows") == 8, "matrix movementProofRows changed")
    require(matrix.get("pauseContextProofRows") == 2, "matrix pauseContextProofRows changed")
    require(matrix.get("keyCensusProofRows") == 1, "matrix keyCensusProofRows changed")
    rows = matrix.get("rows")
    require(isinstance(rows, list) and len(rows) == 8, "matrix must contain eight row entries")
    rows_by_mode = {row.get("mode"): row for row in rows if isinstance(row, dict)}
    require(set(rows_by_mode) == set(HOOK_ROWS), "matrix row modes changed")
    for mode, (hook, cave, readiness) in HOOK_ROWS.items():
        row = rows_by_mode[mode]
        require(row.get("visiblePatchKey") == hook, f"matrix {mode} visible key changed")
        require(row.get("hiddenCompanionKey") == cave, f"matrix {mode} cave key changed")
        require(str(row.get("readinessNote", "")).endswith(readiness), f"matrix {mode} readiness note changed")
        require(row.get("profileSelected") is (mode == "forward"), f"matrix {mode} profile-selected truth changed")
        require(row.get("pauseContextProof") is (mode in {"forward", "backward"}), f"matrix {mode} pause-context truth changed")
        require(row.get("keyCensusProof") is (mode == "forward"), f"matrix {mode} key-census truth changed")
    non_claims = set(str(item) for item in matrix.get("nonClaims", []))
    for token in {
        "not a full free-camera control scheme",
        "not private runtime artifact revalidation",
        "not joystick or analog camera proof",
        "not pause/menu safety proof",
        "not gameplay safety proof",
        "not render parity",
        "not online proof",
        "not rebuild parity",
        "not no-noticeable-difference parity",
    }:
        require(token in non_claims, f"matrix missing non-claim: {token}")


def assert_checker_modes() -> dict[str, Any]:
    movement_modes = set(movement_checker.PROOF_MODES)
    pause_modes = set(pause_context_checker.PROOF_MODES)
    require(movement_modes == set(HOOK_ROWS), "movement checker must cover exactly the eight Q remap modes")
    require(pause_modes == {"forward", "backward"}, "pause-context checker must cover only forward/backward")
    require(key_census_checker.REQUIRED_PATCH_KEYS == {GATE_KEY, PROFILE_HOOK, PROFILE_CAVE}, "key-census checker must stay Q-forward scoped")

    return {
        "movementProofRows": len(movement_modes),
        "pauseContextProofRows": len(pause_modes),
        "keyCensusProofRows": 1,
        "profileSelectedHook": PROFILE_HOOK,
        "manualOnlyHookRows": sorted(hook for mode, (hook, _, _) in HOOK_ROWS.items() if mode != "forward"),
    }


def assert_readiness_notes() -> None:
    require((ROOT / "release/readiness/winui_safe_copy_free_camera_toggle_2026-06-18.md").is_file(), "missing toggle readiness note")
    for _, _, readiness in HOOK_ROWS.values():
        require((ROOT / "release/readiness" / readiness).is_file(), f"missing readiness note: {readiness}")


def check() -> dict[str, Any]:
    profile = assert_profile_catalog()
    assert_patch_catalog()
    assert_matrix_contract()
    summary = assert_checker_modes()
    assert_readiness_notes()
    assert_text_tokens()
    summary.update(
        {
            "schema": "winui-debug-camera-preview-proof-matrix.v1",
            "profileId": profile["id"],
            "profilePatchKeys": profile["patch_keys"],
            "claimBoundary": "This is a public proof-boundary consistency guard over accepted evidence; it does not revalidate private runtime artifacts and is not a full free-camera control scheme, gameplay-safety proof, online proof, rebuild parity, or no-noticeable-difference parity.",
        }
    )
    return summary


def self_test() -> None:
    require(len(HOOK_ROWS) == 8, "self-test expected eight hook rows")
    require(PROFILE_HOOK in {hook for hook, _, _ in HOOK_ROWS.values()}, "profile hook missing from row map")
    require(PROFILE_CAVE in {cave for _, cave, _ in HOOK_ROWS.values()}, "profile cave missing from row map")
    manual_only = [hook for mode, (hook, _, _) in HOOK_ROWS.items() if mode != "forward"]
    require(len(manual_only) == 7, "self-test expected seven manual-only hook rows")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI Debug Camera Preview proof matrix checker self-test: PASS")
            return 0
        require(args.check, "use --check or --self-test")
        print(json.dumps(check(), indent=2, sort_keys=True))
        return 0
    except MatrixError as exc:
        print(f"WinUI Debug Camera Preview proof matrix check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
