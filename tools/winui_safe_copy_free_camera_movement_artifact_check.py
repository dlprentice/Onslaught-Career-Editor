#!/usr/bin/env python3
"""Validate CDB-backed safe-copy free-camera Q movement artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "free-camera-movement-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
HOOK_BYTES = "e9 90 90 18 00"
PROOF_MODES = {
    "forward": {
        "direction": "forward",
        "delta_kind": "position",
        "source_button": "31",
        "source_raw": "0000001f",
        "source_analog": "bf800000",
        "target_button": "38",
        "target_raw": "00000026",
        "census_row": "movement-forward",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_forward_q_hook",
            "free_camera_keyboard_forward_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 1f 75 09 b8 26 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-forward-proof.v1",
    },
    "backward": {
        "direction": "backward",
        "delta_kind": "position",
        "source_button": "32",
        "source_raw": "00000020",
        "source_analog": "3f800000",
        "target_button": "39",
        "target_raw": "00000027",
        "census_row": "movement-backward",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_backward_q_hook",
            "free_camera_keyboard_backward_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 20 75 09 b8 27 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-backward-proof.v1",
    },
    "strafe-left": {
        "direction": "strafe-left",
        "delta_kind": "position",
        "source_button": "29",
        "source_raw": "0000001d",
        "source_analog": "bf800000",
        "target_button": "40",
        "target_raw": "00000028",
        "census_row": "movement-left",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_strafe_left_q_hook",
            "free_camera_keyboard_strafe_left_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 1d 75 09 b8 28 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-strafe-left-proof.v1",
    },
    "strafe-right": {
        "direction": "strafe-right",
        "delta_kind": "position",
        "source_button": "30",
        "source_raw": "0000001e",
        "source_analog": "3f800000",
        "target_button": "41",
        "target_raw": "00000029",
        "census_row": "movement-right",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_strafe_right_q_hook",
            "free_camera_keyboard_strafe_right_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 1e 75 09 b8 29 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-strafe-right-proof.v1",
    },
    "yaw-right": {
        "direction": "yaw-right",
        "delta_kind": "orientation",
        "source_button": "27",
        "source_raw": "0000001b",
        "source_analog": "3f800000",
        "target_button": "37",
        "target_raw": "00000025",
        "census_row": "look-right",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_yaw_right_q_hook",
            "free_camera_keyboard_yaw_right_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 1b 75 09 b8 25 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-yaw-right-proof.v1",
    },
    "yaw-left": {
        "direction": "yaw-left",
        "delta_kind": "orientation",
        "source_button": "25",
        "source_raw": "00000019",
        "source_analog": "bf800000",
        "target_button": "36",
        "target_raw": "00000024",
        "census_row": "look-left",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_yaw_left_q_hook",
            "free_camera_keyboard_yaw_left_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 19 75 09 b8 24 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-yaw-left-proof.v1",
    },
    "pitch-up": {
        "direction": "pitch-up",
        "delta_kind": "orientation",
        "source_button": "26",
        "source_raw": "0000001a",
        "source_analog": "bf800000",
        "target_button": "34",
        "target_raw": "00000022",
        "census_row": "look-up",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_pitch_up_q_hook",
            "free_camera_keyboard_pitch_up_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 1a 75 09 b8 22 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-pitch-up-proof.v1",
    },
    "pitch-down": {
        "direction": "pitch-down",
        "delta_kind": "orientation",
        "source_button": "28",
        "source_raw": "0000001c",
        "source_analog": "3f800000",
        "target_button": "35",
        "target_raw": "00000023",
        "census_row": "look-down",
        "required_patch_keys": {
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_pitch_down_q_hook",
            "free_camera_keyboard_pitch_down_q_cave",
        },
        "cave_bytes": "8b 44 24 08 83 f8 1c 75 09 b8 23 00 00 00 89 44 24 08 81 ec c0 00 00 00 e9 58 6f e7 ff",
        "schema": "winui-safe-copy-free-camera-q-pitch-down-proof.v1",
    },
}


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "artifact must be a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def bool_at(value: dict[str, Any], key: str) -> bool:
    child = value.get(key)
    require(isinstance(child, bool), f"missing boolean: {key}")
    return bool(child)


def int_at(value: dict[str, Any], key: str) -> int:
    child = value.get(key)
    require(isinstance(child, int), f"missing integer: {key}")
    return int(child)


def string_at(value: dict[str, Any], key: str) -> str:
    child = value.get(key)
    require(isinstance(child, str), f"missing string: {key}")
    return child


def string_list_at(value: dict[str, Any], key: str) -> list[str]:
    values = list_at(value, key)
    require(all(isinstance(item, str) for item in values), f"{key} must contain only strings")
    return [str(item) for item in values]


def norm_hex(value: str) -> str:
    return " ".join(value.lower().split())


def nonzero_hex(value: str) -> bool:
    try:
        return int(value, 16) != 0
    except ValueError:
        return False


def capture_has_visual_proof(item: dict[str, Any]) -> bool:
    if item.get("visualProof") is True or item.get("foregroundMatchesTarget") is True:
        return True
    occlusion = item.get("occlusion")
    return (
        isinstance(occlusion, dict)
        and occlusion.get("checked") is True
        and occlusion.get("targetFound") is True
        and occlusion.get("occlusionFree") is True
        and occlusion.get("occludingWindowCount") == 0
    )


def visual_capture_count(captures: list[Any]) -> int:
    return sum(1 for item in captures if isinstance(item, dict) and capture_has_visual_proof(item))


def regex_rows(pattern: str, text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in re.finditer(pattern, text, flags=re.IGNORECASE)]


def observer_log_path(artifact: dict[str, Any]) -> Path:
    observer = object_at(artifact, "cdbObserver")
    require(bool_at(observer, "enabled"), "CDB observer was not enabled")
    command_file = string_at(observer, "commandFile").replace("/", "\\").lower()
    require(command_file.endswith(EXPECTED_COMMAND_FILE), "unexpected CDB observer command file")
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(bool_at(result, "logExists"), "CDB log was not created")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish")
    candidate = result.get("logPath") or observer.get("logPath")
    require(isinstance(candidate, str) and candidate, "CDB log path is missing")
    path = Path(candidate)
    require(path.is_file(), f"CDB log path is missing: {path}")
    return path


def input_windows(artifact: dict[str, Any], log_path: Path) -> dict[int, tuple[str, str]]:
    rows = list_at(artifact, "inputCdbWindows")
    data = log_path.read_bytes()
    windows: dict[int, tuple[str, str]] = {}
    for row in rows:
        require(isinstance(row, dict), "inputCdbWindows row must be an object")
        index = row.get("index")
        sequence = row.get("sequence")
        start = row.get("logStartByte")
        end = row.get("logEndByte")
        require(isinstance(index, int) and index > 0, "inputCdbWindows row has invalid index")
        require(isinstance(sequence, str) and sequence, f"inputCdbWindows row {index} has invalid sequence")
        require(isinstance(start, int) and isinstance(end, int), f"inputCdbWindows row {index} is missing byte offsets")
        require(0 <= start <= end <= len(data), f"inputCdbWindows row {index} byte offsets are out of range")
        windows[index] = (sequence, data[start:end].decode("utf-8", errors="replace"))
    return windows


def input_window_text(artifact: dict[str, Any], log_path: Path, target_index: int, pre_slop: int = 0, post_slop: int = 0) -> str:
    rows = list_at(artifact, "inputCdbWindows")
    data = log_path.read_bytes()
    for row in rows:
        require(isinstance(row, dict), "inputCdbWindows row must be an object")
        if row.get("index") != target_index:
            continue
        start = row.get("logStartByte")
        end = row.get("logEndByte")
        require(isinstance(start, int) and isinstance(end, int), f"inputCdbWindows row {target_index} is missing byte offsets")
        start = max(0, start - pre_slop)
        end = min(len(data), end + post_slop)
        require(start <= end, f"inputCdbWindows row {target_index} byte offsets are invalid")
        return data[start:end].decode("utf-8", errors="replace")
    raise ArtifactError(f"inputCdbWindows row {target_index} is missing")


CAVE_RE = (
    r"FreeCameraKeyboard(?:ForwardQ|BackwardQ|QRemap)_Cave targetIController=(?P<target>[0-9a-f]+) "
    r"originalButton=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+) "
    r"hookBytes=(?P<hook>[0-9a-f ]+?) caveBytes=(?P<cave>[0-9a-f ]+?)(?=\s+[A-Za-z0-9_]+__|\s+FreeCamera|\s*$)"
)

ENTRY_RE = (
    r"CControllableCamera__ReceiveButtonAction_Entry targetIController=(?P<target>[0-9a-f]+) "
    r"camera=(?P<camera>[0-9a-f]+) button=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) "
    r"analogRaw=(?P<analog>[0-9a-f]+) curPos=(?P<cur_pos>[0-9a-f/]+) tempPos=(?P<temp_pos>[0-9a-f/]+) "
    r"curOri00_01_02=(?P<cur_ori>[0-9a-f/]+) tempOri00_01_02=(?P<temp_ori>[0-9a-f/]+)"
)

PREP_RE = (
    r"CControllableCamera__PrepareForInterpolation_Delta camera=(?P<camera>[0-9a-f]+) "
    r"frameCount=(?P<frame>[0-9a-f]+) lastFrame=(?P<last>[0-9a-f]+) "
    r"curPos=(?P<cur_pos>[0-9a-f/]+) tempPos=(?P<temp_pos>[0-9a-f/]+) "
    r"curOri00_01_02=(?P<cur_ori>[0-9a-f/]+) tempOri00_01_02=(?P<temp_ori>[0-9a-f/]+)"
)

POST_CAVE_RE = (
    r"CControllableCamera__ReceiveButtonAction_PostCave targetIController=(?P<target>[0-9a-f]+) "
    r"camera=(?P<camera>[0-9a-f]+) eaxButton=(?P<eax_button>\d+) stackButton=(?P<stack_button>\d+) "
    r"stackButtonRaw=(?P<stack_raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+)"
)

RECEIVE_RE = (
    r"CGame__ReceiveButtonAction game=(?P<game>[0-9a-f]+) fromController=(?P<controller>[0-9a-f]+) "
    r"button=(?P<button>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+)"
)

SET_CAMERA_RE = (
    r"CGame__SetCurrentCamera game=(?P<game>[0-9a-f]+) player=(?P<player>\d+) camera=(?P<camera>[0-9a-f]+) "
    r"releaseOld=(?P<release_old>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+) "
    r"cam0=(?P<cam0>[0-9a-f]+) cam1=(?P<cam1>[0-9a-f]+) "
    r"oldCam0=(?P<old_cam0>[0-9a-f]+) oldCam1=(?P<old_cam1>[0-9a-f]+)"
)


def mode_rows(rows: list[dict[str, str]], mode: dict[str, Any]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row["button"] == mode["source_button"]
        and row["raw"].lower() == mode["source_raw"]
        and row["analog"].lower() == mode["source_analog"]
    ]


def validate_common(artifact: dict[str, Any], min_capture_count: int, mode: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")

    source = object_at(artifact, "source")
    require(bool_at(source, "installedHashUnchanged"), "installed BEA.exe hash changed")
    require(bool_at(source, "overrideHashUnchanged"), "clean override BEA.exe hash changed")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "source save/options changed")

    safe_copy = object_at(artifact, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "safe copy did not apply windowed compatibility patch keys")
    require(mode["required_patch_keys"].issubset(patch_keys), f"safe copy did not apply all free-camera Q-{mode['direction']} patch keys")
    control_options = object_at(safe_copy, "controlOptions")
    require(control_options.get("requestedControllerConfig") == 2, f"Q-{mode['direction']} proof must use controller configuration 2")
    require(
        control_options.get("requestedConfig2CensusRowQe") == mode["census_row"],
        f"Q-{mode['direction']} proof must bind config-2 {mode['census_row']} to Q/E in the copied options file",
    )

    launch = object_at(artifact, "launch")
    require(bool_at(launch, "observedAlive"), "copied BEA process was not observed alive")
    baseline = object_at(artifact, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "preexisting BEA process was present")
    require(bool_at(baseline, "noBeaAfterStop"), "BEA process remained after stop")
    require(bool_at(object_at(artifact, "stop"), "Success"), "managed copied-game stop failed")

    input_summary = object_at(artifact, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 5, "expected toggle/wait/Q/wait/toggle input sequence set")
    require(int_at(input_summary, "focusedInputSequences") == int_at(input_summary, "inputSequencesSent"), "not all input sequences were focused")
    require(int_at(input_summary, "inputWindowMessageEventsSent") == 0, "background/PostMessage input was used")

    captures = list_at(artifact, "captures")
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}")
    require(visual_capture_count(captures) >= min_capture_count, "not enough visual-proof captures")

    log_path = observer_log_path(artifact)
    return log_path, {
        "patchKeys": sorted(patch_keys),
        "captureCount": len(captures),
        "visualCaptureCount": visual_capture_count(captures),
        "inputSequencesSent": int_at(input_summary, "inputSequencesSent"),
    }


def validate_artifact(
    path: Path,
    min_capture_count: int = 1,
    proof_mode: str = "forward",
    expect_q_count: int | None = None,
) -> dict[str, Any]:
    mode = PROOF_MODES[proof_mode]
    artifact = read_json(path)
    log_path, summary = validate_common(artifact, min_capture_count, mode)
    log_text = log_path.read_text(encoding="utf-8", errors="replace")

    windows = input_windows(artifact, log_path)
    require(sorted(windows) == [1, 2, 3, 4, 5], "expected exactly five ordered CDB input windows")
    expected_sequences = [
        r"tap:F",
        r"wait:\d+",
        r"down:Q,wait:\d+,up:Q",
        r"wait:\d+",
        r"tap:F",
    ]
    for index, pattern in enumerate(expected_sequences, start=1):
        sequence = windows[index][0]
        require(re.fullmatch(pattern, sequence, flags=re.IGNORECASE), f"input window {index} had unexpected sequence: {sequence}")

    first_f_text = input_window_text(artifact, log_path, 1, pre_slop=4096, post_slop=4096)
    second_f_text = input_window_text(artifact, log_path, 5, pre_slop=4096, post_slop=4096)
    first_f_receive_rows = regex_rows(RECEIVE_RE, first_f_text)
    second_f_receive_rows = regex_rows(RECEIVE_RE, second_f_text)
    require(any(row["button"] == "1" and row["free0"] == "0" for row in first_f_receive_rows), "first F window did not receive free-camera toggle while off")
    require(any(row["button"] == "1" and row["free0"] == "1" for row in second_f_receive_rows), "second F window did not receive free-camera toggle while on")
    first_f_set_rows = regex_rows(SET_CAMERA_RE, first_f_text)
    second_f_set_rows = regex_rows(SET_CAMERA_RE, second_f_text)
    require("CGame__ToggleFreeCameraOn" in first_f_text, "first F window did not hit CGame__ToggleFreeCameraOn")
    require(any(row["release_old"] == "0" for row in first_f_set_rows), "first F window did not install the free-camera pointer")
    require(any(row["release_old"] == "1" for row in second_f_set_rows), "second F window did not restore the original camera pointer")

    q_windows = [
        (index, sequence, text)
        for index, (sequence, text) in windows.items()
        if re.fullmatch(r"down:Q,wait:\d+,up:Q", sequence, flags=re.IGNORECASE)
    ]
    require(len(q_windows) == 1, "expected exactly one down:Q,wait:<ms>,up:Q CDB input window")
    q_index, q_sequence, q_text = q_windows[0]

    cave_rows = mode_rows(regex_rows(CAVE_RE, q_text), mode)
    entry_rows = mode_rows(regex_rows(ENTRY_RE, q_text), mode)
    all_post_cave_rows = regex_rows(POST_CAVE_RE, q_text)
    post_cave_rows = [
        row
        for row in all_post_cave_rows
        if row["eax_button"] == mode["target_button"]
        and row["stack_button"] == mode["target_button"]
        and row["stack_raw"].lower() == mode["target_raw"]
        and row["analog"].lower() == mode["source_analog"]
    ]
    all_prep_rows = regex_rows(PREP_RE, q_text)
    require(cave_rows, f"Q input window did not hit the free-camera Q-{mode['direction']} cave")
    require(entry_rows, f"Q input window did not reach CControllableCamera::ReceiveButtonAction with button {mode['source_button']}")
    require(post_cave_rows, f"Q input window did not record post-cave button-{mode['target_button']} readback")
    require(all_prep_rows, "Q input window did not record camera interpolation deltas")
    require(all(norm_hex(row["hook"]) == HOOK_BYTES for row in cave_rows), f"Q-{mode['direction']} cave rows did not show expected hook bytes")
    require(all(norm_hex(row["cave"]) == mode["cave_bytes"] for row in cave_rows), f"Q-{mode['direction']} cave rows did not show the full expected cave bytes")

    q_targets = {row["target"].lower() for row in cave_rows}
    entry_targets = {row["target"].lower() for row in entry_rows}
    require(q_targets == entry_targets, "Q cave target did not match camera handler target")
    post_targets = {row["target"].lower() for row in post_cave_rows}
    require(q_targets == post_targets, "Q cave target did not match post-cave target")
    require(all(nonzero_hex(target) for target in q_targets), "Q cave target pointer was zero")
    entry_cameras = {row["camera"].lower() for row in entry_rows}
    require(len(entry_cameras) == 1 and all(nonzero_hex(camera) for camera in entry_cameras), "Q camera pointer was missing or inconsistent")
    prep_rows = [row for row in all_prep_rows if row["camera"].lower() in entry_cameras]
    require(len(prep_rows) == len(all_prep_rows), "Q interpolation delta rows did not match the handled camera pointer")
    if expect_q_count is not None:
        require(len(cave_rows) == expect_q_count, f"expected {expect_q_count} Q cave rows, saw {len(cave_rows)}")
        require(len(entry_rows) == expect_q_count, f"expected {expect_q_count} Q camera-handler rows, saw {len(entry_rows)}")
        require(len(post_cave_rows) == expect_q_count, f"expected {expect_q_count} post-cave button rows, saw {len(post_cave_rows)}")
        require(len(prep_rows) == expect_q_count, f"expected {expect_q_count} camera interpolation delta rows, saw {len(prep_rows)}")
    require(
        all(
            row["eax_button"] == mode["target_button"]
            and row["stack_button"] == mode["target_button"]
            and row["stack_raw"].lower() == mode["target_raw"]
            and row["analog"].lower() == mode["source_analog"]
            for row in post_cave_rows
        ),
        f"post-cave rows did not show rewritten button {mode['target_button']} with Q analogue value",
    )

    if mode["delta_kind"] == "orientation":
        q_cur_orientations = {row["cur_ori"].lower() for row in entry_rows}
        prep_temp_orientations = {row["temp_ori"].lower() for row in prep_rows}
        require(len(q_cur_orientations) > 1, "Q camera entry orientations did not change")
        require(len(prep_temp_orientations) > 1, "Q camera interpolation temp orientations did not change")
        require(prep_rows[0]["cur_ori"].lower() != prep_rows[-1]["temp_ori"].lower(), "camera orientation did not move across Q window")
    else:
        q_cur_positions = {row["cur_pos"].lower() for row in entry_rows}
        prep_temp_positions = {row["temp_pos"].lower() for row in prep_rows}
        require(len(q_cur_positions) > 1, "Q camera entry positions did not change")
        require(len(prep_temp_positions) > 1, "Q camera interpolation temp positions did not change")
        require(prep_rows[0]["cur_pos"].lower() != prep_rows[-1]["temp_pos"].lower(), "camera position did not move across Q window")

    for index, (sequence, text) in windows.items():
        if re.fullmatch(r"wait:\d+", sequence, flags=re.IGNORECASE):
            require(not mode_rows(regex_rows(CAVE_RE, text), mode), f"wait window {sequence} had Q/button-{mode['source_button']} cave rows")
            require(not regex_rows(PREP_RE, text), f"wait window {sequence} had camera interpolation delta rows")

    summary.update(
        {
            "schema": mode["schema"],
            "mode": proof_mode,
            "artifact": str(path),
            "cdbLog": str(log_path),
            "qWindowIndex": q_index,
            "qWindowSequence": q_sequence,
            "qCaveCount": len(cave_rows),
            "qEntryCount": len(entry_rows),
            "postCaveButtonReadbackCount": len(post_cave_rows),
            f"postCaveButton{mode['target_button']}Count": len(post_cave_rows),
            "prepareDeltaCount": len(prep_rows),
            "setCurrentCameraCount": len(regex_rows(SET_CAMERA_RE, log_text)),
            "camera": entry_rows[0]["camera"],
            "targetIController": entry_rows[0]["target"],
            "firstQCurPos": entry_rows[0]["cur_pos"],
            "lastQCurPos": entry_rows[-1]["cur_pos"],
            "firstPrepareTempPos": prep_rows[0]["temp_pos"],
            "lastPrepareTempPos": prep_rows[-1]["temp_pos"],
            "firstQCurOri": entry_rows[0]["cur_ori"],
            "lastQCurOri": entry_rows[-1]["cur_ori"],
            "firstPrepareTempOri": prep_rows[0]["temp_ori"],
            "lastPrepareTempOri": prep_rows[-1]["temp_ori"],
            "claim": (
                f"safe-copy experimental free-camera Q-{mode['direction']} hook maps Q/button-{mode['source_button']} through the copied-exe cave "
                f"and produces CDB-observed free-camera {mode['delta_kind']} deltas"
            ),
            "claimBoundary": (
                "Does not prove full free-camera controls, control feel, joystick/analog coverage, "
                "pause/menu safety, gameplay safety, rendering correctness, visual parity, online networking, "
                "rebuild parity, or no-noticeable-difference parity."
            ),
        }
    )
    return summary


def make_artifact(
    root: Path,
    *,
    proof_mode: str = "forward",
    missing_q: bool = False,
    static_position: bool = False,
    static_orientation: bool = False,
) -> Path:
    mode = PROOF_MODES[proof_mode]
    log_path = root / "windbg.log"
    prelude = (
        "CGame__ReceiveButtonAction game=008a9a98 fromController=03d4c6b0 button=1 free0=0 free1=0 "
        "player0=0456b340 player1=00000000 cam0=03a57e40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
        "CGame__ToggleFreeCameraOn game=008a9a98 player=0 freeBefore0=0 freeBefore1=0 "
        "player0=0456b340 player1=00000000 cam0=03a57e40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
        "CGame__SetCurrentCamera game=008a9a98 player=0 camera=03d8d910 releaseOld=0 free0=0 free1=0 "
        "cam0=03a57e40 cam1=00000000 oldCam0=03a57e40 oldCam1=00000000 "
    )
    wait1 = ""
    q_window = "" if missing_q else (
        "FreeCameraKeyboardQRemap_Cave targetIController=03d8d914 "
        f"originalButton={mode['source_button']} rawButton={mode['source_raw']} "
        f"analogRaw={mode['source_analog']} hookBytes=e9 90 90 18 00 caveBytes={mode['cave_bytes']} "
        "CControllableCamera__ReceiveButtonAction_PostCave targetIController=03d8d914 camera=03d8d910 "
        f"eaxButton={mode['target_button']} stackButton={mode['target_button']} "
        f"stackButtonRaw={mode['target_raw']} analogRaw={mode['source_analog']} "
        "CControllableCamera__ReceiveButtonAction_Entry targetIController=03d8d914 camera=03d8d910 "
        f"button={mode['source_button']} rawButton={mode['source_raw']} analogRaw={mode['source_analog']} "
        "curPos=43905800/43734000/c141c8b3/00000002 "
        "tempPos=43905800/43734000/c141c8b3/00000002 curOri00_01_02=3f5f719f/bef9deec/00000000 "
        "tempOri00_01_02=3f5f719f/bef9deec/00000000 "
        "CControllableCamera__PrepareForInterpolation_Delta camera=03d8d910 frameCount=000001c1 lastFrame=000001c0 "
        "curPos=43905800/43734000/c141c8b3/00000002 tempPos=43901988/43741f72/c141c8b3/00000002 "
        "curOri00_01_02=3f5f719f/bef9deec/00000000 tempOri00_01_02=3f5f719f/bef9deec/00000000 "
        "FreeCameraKeyboardQRemap_Cave targetIController=03d8d914 "
        f"originalButton={mode['source_button']} rawButton={mode['source_raw']} "
        f"analogRaw={mode['source_analog']} hookBytes=e9 90 90 18 00 caveBytes={mode['cave_bytes']} "
        "CControllableCamera__ReceiveButtonAction_PostCave targetIController=03d8d914 camera=03d8d910 "
        f"eaxButton={mode['target_button']} stackButton={mode['target_button']} "
        f"stackButtonRaw={mode['target_raw']} analogRaw={mode['source_analog']} "
        "CControllableCamera__ReceiveButtonAction_Entry targetIController=03d8d914 camera=03d8d910 "
        f"button={mode['source_button']} rawButton={mode['source_raw']} analogRaw={mode['source_analog']} curPos="
        + ("43905800/43734000/c141c8b3/00000002" if static_position else "43901988/43741f72/c141c8b3/00000002")
        + " tempPos=43901988/43741f72/c141c8b3/00000002 curOri00_01_02="
        + ("3f5f719f/bef9deec/00000000" if static_orientation else "3f5f7200/bef9de00/00000000")
        + " tempOri00_01_02=3f5f7200/bef9de00/00000000 "
        "CControllableCamera__PrepareForInterpolation_Delta camera=03d8d910 frameCount=000001c2 lastFrame=000001c1 "
        "curPos=43901988/43741f72/c141c8b3/00000002 tempPos=438fdb10/4374fee4/c141c8b3/00000002 "
        "curOri00_01_02=3f5f7200/bef9de00/00000000 tempOri00_01_02="
        + ("3f5f719f/bef9deec/00000000" if static_orientation else "3f5f7300/bef9dd00/00000000")
        + " "
    )
    wait2 = ""
    off = (
        "CGame__ReceiveButtonAction game=008a9a98 fromController=03d4c6b0 button=1 free0=1 free1=0 "
        "player0=0456b340 player1=00000000 cam0=03d8d910 cam1=00000000 oldCam0=03a57e40 oldCam1=00000000 "
        "CGame__SetCurrentCamera game=008a9a98 player=0 camera=03a57e40 releaseOld=1 free0=0 free1=0 "
        "cam0=03d8d910 cam1=00000000 oldCam0=03a57e40 oldCam1=00000000"
    )
    chunks = [prelude, wait1, q_window, wait2, off]
    offsets: list[tuple[int, int]] = []
    cursor = len(prelude.encode("utf-8"))
    for chunk in chunks[1:]:
        start = cursor
        cursor += len(chunk.encode("utf-8"))
        offsets.append((start, cursor))
    log_path.write_text("".join(chunks), encoding="utf-8")
    artifact = {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {
            "patchKeys": sorted(BASE_PATCH_KEYS | mode["required_patch_keys"]),
            "controlOptions": {
                "requestedControllerConfig": 2,
                "requestedConfig2CensusRowQe": mode["census_row"],
            },
        },
        "launch": {"observedAlive": True},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "inputSummary": {
            "inputSequencesSent": 5,
            "focusedInputSequences": 5,
            "inputWindowMessageEventsSent": 0,
        },
        "captures": [{"status": "captured", "fileSize": 1024, "visualProof": True}],
        "inputCdbWindows": [
            {"index": 1, "sequence": "tap:F", "logStartByte": 0, "logEndByte": len(prelude.encode("utf-8"))},
            {"index": 2, "sequence": "wait:500", "logStartByte": offsets[0][0], "logEndByte": offsets[0][1]},
            {"index": 3, "sequence": "down:Q,wait:1000,up:Q", "logStartByte": offsets[1][0], "logEndByte": offsets[1][1]},
            {"index": 4, "sequence": "wait:500", "logStartByte": offsets[2][0], "logEndByte": offsets[2][1]},
            {"index": 5, "sequence": "tap:F", "logStartByte": offsets[3][0], "logEndByte": offsets[3][1]},
        ],
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
            "cleanup": {"status": "stopped"},
        },
    }
    path = root / "artifact.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def self_test() -> None:
    for proof_mode in PROOF_MODES:
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = validate_artifact(make_artifact(Path(temp_dir), proof_mode=proof_mode), proof_mode=proof_mode, expect_q_count=2)
            require(summary["qCaveCount"] == 2, f"self-test expected two Q cave rows for {proof_mode}")

        expected_failures = [("missing Q cave rows should fail", {"missing_q": True})]
        if PROOF_MODES[proof_mode]["delta_kind"] == "orientation":
            expected_failures.append(("static camera orientation should fail", {"static_orientation": True}))
        else:
            expected_failures.append(("static camera position should fail", {"static_position": True}))
        for label, kwargs in expected_failures:
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    validate_artifact(make_artifact(Path(temp_dir), proof_mode=proof_mode, **kwargs), proof_mode=proof_mode)
                except ArtifactError:
                    pass
                else:
                    raise ArtifactError(f"{label} for {proof_mode}")
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                validate_artifact(make_artifact(Path(temp_dir), proof_mode=proof_mode), proof_mode=proof_mode, expect_q_count=3)
            except ArtifactError:
                pass
            else:
                raise ArtifactError(f"wrong expected Q row count should fail for {proof_mode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--mode", choices=sorted(PROOF_MODES), default="forward")
    parser.add_argument("--expect-q-count", type=int)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive")
        require(args.expect_q_count is None or args.expect_q_count > 0, "--expect-q-count must be positive")
        if args.self_test:
            self_test()
            print("WinUI safe-copy free-camera movement artifact checker self-test: PASS")
            return 0
        require(args.artifact is not None, "artifact is required unless --self-test is used")
        print(json.dumps(validate_artifact(args.artifact, args.min_capture_count, args.mode, args.expect_q_count), indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy free-camera movement artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
