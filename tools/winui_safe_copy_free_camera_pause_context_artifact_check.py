#!/usr/bin/env python3
"""Validate CDB-backed safe-copy free-camera pause/context artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "free-camera-pause-context-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
HOOK_BYTES = "e9 90 90 18 00"
PROOF_MODES = {
    "forward": {
        "direction": "forward",
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
        "schema": "winui-safe-copy-free-camera-q-forward-pause-context-proof.v1",
    },
    "backward": {
        "direction": "backward",
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
        "schema": "winui-safe-copy-free-camera-q-backward-pause-context-proof.v1",
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


CAVE_RE = (
    r"FreeCameraKeyboard(?:ForwardQ|BackwardQ|QRemap)_Cave targetIController=(?P<target>[0-9a-f]+) "
    r"originalButton=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+) "
    r"gamePause=(?P<pause>\d+) hookBytes=(?P<hook>[0-9a-f ]+?) caveBytes=(?P<cave>[0-9a-f ]+?)(?=\s+[A-Za-z0-9_]+__|\s+FreeCamera|\s*$)"
)
ENTRY_RE = (
    r"CControllableCamera__ReceiveButtonAction_Entry targetIController=(?P<target>[0-9a-f]+) "
    r"camera=(?P<camera>[0-9a-f]+) button=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) "
    r"analogRaw=(?P<analog>[0-9a-f]+) gamePause=(?P<pause>\d+) "
    r"curPos=(?P<cur_pos>[0-9a-f/]+) tempPos=(?P<temp_pos>[0-9a-f/]+) "
    r"curOri00_01_02=(?P<cur_ori>[0-9a-f/]+) tempOri00_01_02=(?P<temp_ori>[0-9a-f/]+)"
)
POST_CAVE_RE = (
    r"CControllableCamera__ReceiveButtonAction_PostCave targetIController=(?P<target>[0-9a-f]+) "
    r"camera=(?P<camera>[0-9a-f]+) eaxButton=(?P<eax_button>\d+) stackButton=(?P<stack_button>\d+) "
    r"stackButtonRaw=(?P<stack_raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
PREP_RE = (
    r"CControllableCamera__PrepareForInterpolation_Delta camera=(?P<camera>[0-9a-f]+) "
    r"gamePause=(?P<pause>\d+) frameCount=(?P<frame>[0-9a-f]+) lastFrame=(?P<last>[0-9a-f]+) "
    r"curPos=(?P<cur_pos>[0-9a-f/]+) tempPos=(?P<temp_pos>[0-9a-f/]+) "
    r"curOri00_01_02=(?P<cur_ori>[0-9a-f/]+) tempOri00_01_02=(?P<temp_ori>[0-9a-f/]+)"
)
RECEIVE_RE = (
    r"CGame__ReceiveButtonAction game=(?P<game>[0-9a-f]+) fromController=(?P<controller>[0-9a-f]+) "
    r"button=(?P<button>\d+) pause=(?P<pause>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+)"
)
SET_CAMERA_RE = (
    r"CGame__SetCurrentCamera game=(?P<game>[0-9a-f]+) player=(?P<player>\d+) camera=(?P<camera>[0-9a-f]+) "
    r"releaseOld=(?P<release_old>\d+) pause=(?P<pause>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+)"
)
PAUSE_RE = (
    r"CGame__Pause game=(?P<game>[0-9a-f]+) pauseBefore=(?P<pause_before>\d+) "
    r"togglePauseMenu=(?P<toggle_menu>\d+) fromController=(?P<from_controller>[0-9a-f]+) "
    r"free0=(?P<free0>\d+) free1=(?P<free1>\d+) pauseMenu=(?P<pause_menu>[0-9a-f]+)"
)
UNPAUSE_RE = (
    r"CGame__UnPause game=(?P<game>[0-9a-f]+) pauseBefore=(?P<pause_before>\d+) "
    r"free0=(?P<free0>\d+) free1=(?P<free1>\d+) pauseMenu=(?P<pause_menu>[0-9a-f]+)"
)
SEND_RE = (
    r"CController__SendButtonAction controller=(?P<controller>[0-9a-f]+) button=(?P<button>\d+) "
    r"rawButton=(?P<raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
CONTROLLER_KEY_ONCE_RE = (
    r"CPCController__GetKeyOnce controller=(?P<controller>[0-9a-f]+) key=79 arg4=(?P<arg4>[0-9a-f]+) "
    r"arg8=(?P<arg8>[0-9a-f]+) globalOnceO=(?P<once>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
PLATFORM_KEY_ONCE_RE = (
    r"PlatformInput__GetKeyOnceCore input=(?P<input>[0-9a-f]+) key=79 rawKey=(?P<raw>[0-9a-f]+) "
    r"onceByteBefore=(?P<once>[0-9a-f]+) globalOnceO=(?P<global_once>[0-9a-f]+) "
    r"consumedQueue=(?P<queue>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
CONSUME_KEY_ONCE_RE = (
    r"PlatformInput__ConsumeKeyOnce key=79 rawKey=(?P<raw>[0-9a-f]+) "
    r"globalOnceBefore=(?P<once>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
PAUSEMENU_INIT_RE = r"CPauseMenu__InitPauseSession pauseMenu=(?P<pause_menu>[0-9a-f]+)"
PAUSEMENU_DEACTIVATE_RE = r"CPauseMenu__DeactivatePauseSession pauseMenu=(?P<pause_menu>[0-9a-f]+)"
GAMEINTERFACE_RE = r"CGameInterface__VFunc_03_HandleMenuControlInput gameInterface=(?P<game_interface>[0-9a-f]+)"


def mode_rows(rows: list[dict[str, str]], mode: dict[str, Any]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row["button"] == mode["source_button"]
        and row["raw"].lower() == mode["source_raw"]
        and row["analog"].lower() == mode["source_analog"]
    ]


def post_cave_rows(rows: list[dict[str, str]], mode: dict[str, Any], pause: str) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row["eax_button"] == mode["target_button"]
        and row["stack_button"] == mode["target_button"]
        and row["stack_raw"].lower() == mode["target_raw"]
        and row["analog"].lower() == mode["source_analog"]
        and row["pause"] == pause
    ]


def q_window_has_no_camera_path(text: str, label: str) -> None:
    require(not regex_rows(CAVE_RE, text), f"{label} unexpectedly hit free-camera Q cave")
    require(not regex_rows(POST_CAVE_RE, text), f"{label} unexpectedly hit post-cave rows")
    require(not regex_rows(PREP_RE, text), f"{label} unexpectedly moved free camera")
    require(not mode_rows(regex_rows(ENTRY_RE, text), {"source_button": "31", "source_raw": "0000001f", "source_analog": "bf800000"}), f"{label} unexpectedly entered forward camera path")
    require(not mode_rows(regex_rows(ENTRY_RE, text), {"source_button": "32", "source_raw": "00000020", "source_analog": "3f800000"}), f"{label} unexpectedly entered backward camera path")


def validate_common(artifact: dict[str, Any], min_capture_count: int, mode: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")
    source = object_at(artifact, "source")
    require(bool_at(source, "installedHashUnchanged"), "installed BEA.exe hash changed")
    require(bool_at(source, "overrideHashUnchanged"), "clean override BEA.exe hash changed")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "source save/options changed")

    safe_copy = object_at(artifact, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "safe copy did not apply windowed compatibility patch keys")
    require(mode["required_patch_keys"].issubset(patch_keys), "safe copy did not apply all required free-camera patch keys")
    control_options = object_at(safe_copy, "controlOptions")
    require(control_options.get("requestedControllerConfig") == 2, "pause-context proof must use controller configuration 2")
    require(control_options.get("requestedConfig2CensusRowQe") == mode["census_row"], "pause-context proof must bind the expected Q/E row")

    launch = object_at(artifact, "launch")
    require(bool_at(launch, "observedAlive"), "copied BEA process was not observed alive")
    baseline = object_at(artifact, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "preexisting BEA process was present")
    require(bool_at(baseline, "noBeaAfterStop"), "BEA process remained after stop")
    require(bool_at(object_at(artifact, "stop"), "Success"), "managed copied-game stop failed")

    input_summary = object_at(artifact, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 8, "expected pre/on/Q/pause/Q/unpause/off/post input windows")
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


def validate_movement_window(text: str, mode: dict[str, Any], pause: str, label: str) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    cave_rows = [row for row in mode_rows(regex_rows(CAVE_RE, text), mode) if row["pause"] == pause]
    entry_rows = [row for row in mode_rows(regex_rows(ENTRY_RE, text), mode) if row["pause"] == pause]
    post_rows = post_cave_rows(regex_rows(POST_CAVE_RE, text), mode, pause)
    prep_rows = [row for row in regex_rows(PREP_RE, text) if row["pause"] == pause]

    require(cave_rows, f"{label} did not hit the expected Q cave")
    require(entry_rows, f"{label} did not reach CControllableCamera::ReceiveButtonAction")
    require(post_rows, f"{label} did not record post-cave button-{mode['target_button']} readback")
    require(prep_rows, f"{label} did not record camera interpolation deltas")
    require(all(norm_hex(row["hook"]) == HOOK_BYTES for row in cave_rows), f"{label} cave rows did not show expected hook bytes")
    require(all(norm_hex(row["cave"]) == mode["cave_bytes"] for row in cave_rows), f"{label} cave rows did not show full expected cave bytes")

    q_targets = {row["target"].lower() for row in cave_rows}
    entry_targets = {row["target"].lower() for row in entry_rows}
    post_targets = {row["target"].lower() for row in post_rows}
    require(q_targets == entry_targets == post_targets, f"{label} cave/entry/post-cave targets did not match")
    require(all(nonzero_hex(target) for target in q_targets), f"{label} target pointer was zero")
    require(len({row["cur_pos"].lower() for row in entry_rows}) > 1, f"{label} camera entry positions did not change")
    require(len({row["temp_pos"].lower() for row in prep_rows}) > 1, f"{label} interpolation temp positions did not change")
    require(prep_rows[0]["cur_pos"].lower() != prep_rows[-1]["temp_pos"].lower(), f"{label} camera position did not move across input window")
    return cave_rows, entry_rows, prep_rows


def validate_artifact(path: Path, min_capture_count: int = 1, proof_mode: str = "forward") -> dict[str, Any]:
    mode = PROOF_MODES[proof_mode]
    artifact = read_json(path)
    log_path, summary = validate_common(artifact, min_capture_count, mode)
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    windows = input_windows(artifact, log_path)
    require(sorted(windows) == list(range(1, 9)), "expected exactly eight ordered CDB input windows")

    expected_patterns = [
        r"down:Q,wait:\d+,up:Q",
        r"tap:F,wait:\d+",
        r"down:Q,wait:\d+,up:Q",
        r"(?:tap:O,wait:\d+|down:O,wait:\d+,up:O)",
        r"down:Q,wait:\d+,up:Q",
        r"(?:tap:O,wait:\d+|down:O,wait:\d+,up:O)",
        r"tap:F,wait:\d+",
        r"down:Q,wait:\d+,up:Q",
    ]
    for index, pattern in enumerate(expected_patterns, start=1):
        sequence = windows[index][0]
        require(re.fullmatch(pattern, sequence, flags=re.IGNORECASE), f"input window {index} had unexpected sequence: {sequence}")

    pre_q_text = windows[1][1]
    toggle_on_text = windows[2][1]
    active_q_text = windows[3][1]
    pause_text = windows[4][1]
    paused_q_text = windows[5][1]
    unpause_text = windows[6][1]
    toggle_off_text = windows[7][1]
    post_q_text = windows[8][1]

    q_window_has_no_camera_path(pre_q_text, "pre-free-camera Q window")
    q_window_has_no_camera_path(post_q_text, "post-free-camera Q window")

    first_receive_rows = regex_rows(RECEIVE_RE, toggle_on_text)
    require(any(row["button"] == "1" and row["free0"] == "0" for row in first_receive_rows), "toggle-on window did not receive free-camera button while off")
    require("CGame__ToggleFreeCameraOn" in toggle_on_text, "toggle-on window did not hit CGame__ToggleFreeCameraOn")
    require(any(row["release_old"] == "0" for row in regex_rows(SET_CAMERA_RE, toggle_on_text)), "toggle-on window did not install free-camera pointer")

    active_cave, active_entry, active_prep = validate_movement_window(active_q_text, mode, "0", "active Q window")

    pause_send_rows = regex_rows(SEND_RE, pause_text)
    pause_controller_key_rows = regex_rows(CONTROLLER_KEY_ONCE_RE, pause_text)
    pause_platform_key_rows = regex_rows(PLATFORM_KEY_ONCE_RE, pause_text)
    pause_consume_key_rows = regex_rows(CONSUME_KEY_ONCE_RE, pause_text)
    pause_entry_rows = [row for row in regex_rows(ENTRY_RE, pause_text) if row["button"] == "56" and row["raw"].lower() == "00000038"]
    pause_rows = regex_rows(PAUSE_RE, pause_text)
    require(pause_controller_key_rows, "pause window did not query CPCController::GetKeyOnce for O")
    require(pause_platform_key_rows, "pause window did not query PlatformInput::GetKeyOnceCore for O")
    require(
        all(row["arg4"].lower() == "0000004f" or row["arg8"].lower() == "0000004f" for row in pause_controller_key_rows),
        "pause window CPCController key-once rows were not for O",
    )
    require(all(row["raw"].lower() == "0000004f" for row in pause_platform_key_rows), "pause window PlatformInput key-once rows were not for O")
    require(any(row["button"] == "56" for row in pause_send_rows), "pause window did not send BUTTON_PAUSE")
    require(pause_entry_rows, "pause window did not enter CControllableCamera with BUTTON_PAUSE")
    require(any(row["pause_before"] == "0" and row["toggle_menu"] == "0" and int(row["from_controller"], 16) == 0 for row in pause_rows), "pause window did not call CGame__Pause with menu toggle disabled")
    require(not regex_rows(PAUSEMENU_INIT_RE, pause_text), "free-camera pause unexpectedly initialized pause menu")
    require(not regex_rows(GAMEINTERFACE_RE, pause_text), "free-camera pause unexpectedly dispatched GameInterface menu input")
    require(not regex_rows(CAVE_RE, pause_text), "pause window unexpectedly hit Q remap cave")

    paused_cave, paused_entry, paused_prep = validate_movement_window(paused_q_text, mode, "1", "paused Q window")
    require(not regex_rows(PAUSEMENU_INIT_RE, paused_q_text), "paused Q unexpectedly initialized pause menu")
    require(not regex_rows(PAUSEMENU_DEACTIVATE_RE, paused_q_text), "paused Q unexpectedly deactivated pause menu")
    require(not regex_rows(GAMEINTERFACE_RE, paused_q_text), "paused Q unexpectedly dispatched GameInterface menu input")

    unpause_send_rows = regex_rows(SEND_RE, unpause_text)
    unpause_controller_key_rows = regex_rows(CONTROLLER_KEY_ONCE_RE, unpause_text)
    unpause_platform_key_rows = regex_rows(PLATFORM_KEY_ONCE_RE, unpause_text)
    unpause_consume_key_rows = regex_rows(CONSUME_KEY_ONCE_RE, unpause_text)
    unpause_entry_rows = [row for row in regex_rows(ENTRY_RE, unpause_text) if row["button"] == "56" and row["raw"].lower() == "00000038"]
    unpause_rows = regex_rows(UNPAUSE_RE, unpause_text)
    require(unpause_controller_key_rows, "unpause window did not query CPCController::GetKeyOnce for O")
    require(unpause_platform_key_rows, "unpause window did not query PlatformInput::GetKeyOnceCore for O")
    require(
        all(row["arg4"].lower() == "0000004f" or row["arg8"].lower() == "0000004f" for row in unpause_controller_key_rows),
        "unpause window CPCController key-once rows were not for O",
    )
    require(all(row["raw"].lower() == "0000004f" for row in unpause_platform_key_rows), "unpause window PlatformInput key-once rows were not for O")
    require(any(row["button"] == "56" for row in unpause_send_rows), "unpause window did not send BUTTON_PAUSE")
    require(unpause_entry_rows, "unpause window did not enter CControllableCamera with BUTTON_PAUSE")
    require(any(row["pause_before"] == "1" and row["free0"] == "1" for row in unpause_rows), "unpause window did not call CGame__UnPause while free camera remained on")
    require(not regex_rows(PAUSEMENU_DEACTIVATE_RE, unpause_text), "free-camera unpause unexpectedly deactivated pause menu")
    require(not regex_rows(GAMEINTERFACE_RE, unpause_text), "free-camera unpause unexpectedly dispatched GameInterface menu input")

    second_receive_rows = regex_rows(RECEIVE_RE, toggle_off_text)
    require(any(row["button"] == "1" and row["free0"] == "1" for row in second_receive_rows), "toggle-off window did not receive free-camera button while on")
    require(any(row["release_old"] == "1" for row in regex_rows(SET_CAMERA_RE, toggle_off_text)), "toggle-off window did not restore original camera pointer")

    require(not regex_rows(PAUSEMENU_INIT_RE, log_text), "artifact unexpectedly initialized pause menu during free-camera pause-context proof")
    require(not regex_rows(PAUSEMENU_DEACTIVATE_RE, log_text), "artifact unexpectedly deactivated pause menu during free-camera pause-context proof")
    require(not regex_rows(GAMEINTERFACE_RE, log_text), "artifact unexpectedly dispatched GameInterface menu input during free-camera pause-context proof")

    summary.update(
        {
            "schema": mode["schema"],
            "mode": proof_mode,
            "artifact": str(path),
            "cdbLog": str(log_path),
            "activeQCaveCount": len(active_cave),
            "activeQEntryCount": len(active_entry),
            "activePrepareDeltaCount": len(active_prep),
            "pausedQCaveCount": len(paused_cave),
            "pausedQEntryCount": len(paused_entry),
            "pausedPrepareDeltaCount": len(paused_prep),
            "pauseButtonEntryCount": len(pause_entry_rows),
            "unpauseButtonEntryCount": len(unpause_entry_rows),
            "pauseControllerKeyOnceCount": len(pause_controller_key_rows),
            "pausePlatformKeyOnceCount": len(pause_platform_key_rows),
            "pauseConsumeKeyOnceCount": len(pause_consume_key_rows),
            "unpauseControllerKeyOnceCount": len(unpause_controller_key_rows),
            "unpausePlatformKeyOnceCount": len(unpause_platform_key_rows),
            "unpauseConsumeKeyOnceCount": len(unpause_consume_key_rows),
            "pauseCallCount": len(pause_rows),
            "unpauseCallCount": len(unpause_rows),
            "setCurrentCameraCount": len(regex_rows(SET_CAMERA_RE, log_text)),
            "claim": (
                f"safe-copy experimental free-camera Q-{mode['direction']} hook remains bounded across the free-camera pause toggle path: "
                "Q is inert before free camera and after free-camera exit, pause/unpause uses CControllableCamera BUTTON_PAUSE, "
                "and Q movement while paused stays in the camera hook path without pause-menu/GameInterface dispatch"
            ),
            "claimBoundary": (
                "Does not prove all pause-menu behavior, normal gameplay pause-menu UX, control feel, all camera axes, "
                "joystick/analog coverage, rendering parity, online networking, or rebuild parity."
            ),
        }
    )
    return summary


def make_artifact(
    root: Path,
    *,
    proof_mode: str = "forward",
    missing_pause: bool = False,
    missing_key_once: bool = False,
    pre_q_hits_cave: bool = False,
) -> Path:
    mode = PROOF_MODES[proof_mode]
    log_path = root / "windbg.log"

    def q_chunk(pause: str, cur_a: str, cur_b: str, temp_b: str) -> str:
        return (
            "FreeCameraKeyboardQRemap_Cave targetIController=03d8d914 "
            f"originalButton={mode['source_button']} rawButton={mode['source_raw']} "
            f"analogRaw={mode['source_analog']} gamePause={pause} hookBytes=e9 90 90 18 00 caveBytes={mode['cave_bytes']} "
            "CControllableCamera__ReceiveButtonAction_PostCave targetIController=03d8d914 camera=03d8d910 "
            f"eaxButton={mode['target_button']} stackButton={mode['target_button']} stackButtonRaw={mode['target_raw']} "
            f"analogRaw={mode['source_analog']} gamePause={pause} "
            "CControllableCamera__ReceiveButtonAction_Entry targetIController=03d8d914 camera=03d8d910 "
            f"button={mode['source_button']} rawButton={mode['source_raw']} analogRaw={mode['source_analog']} gamePause={pause} "
            f"curPos={cur_a} tempPos={cur_a} curOri00_01_02=3f5f719f/bef9deec/00000000 "
            "tempOri00_01_02=3f5f719f/bef9deec/00000000 "
            "CControllableCamera__PrepareForInterpolation_Delta camera=03d8d910 "
            f"gamePause={pause} frameCount=000001c1 lastFrame=000001c0 curPos={cur_a} tempPos={cur_b} "
            "curOri00_01_02=3f5f719f/bef9deec/00000000 tempOri00_01_02=3f5f719f/bef9deec/00000000 "
            "FreeCameraKeyboardQRemap_Cave targetIController=03d8d914 "
            f"originalButton={mode['source_button']} rawButton={mode['source_raw']} "
            f"analogRaw={mode['source_analog']} gamePause={pause} hookBytes=e9 90 90 18 00 caveBytes={mode['cave_bytes']} "
            "CControllableCamera__ReceiveButtonAction_PostCave targetIController=03d8d914 camera=03d8d910 "
            f"eaxButton={mode['target_button']} stackButton={mode['target_button']} stackButtonRaw={mode['target_raw']} "
            f"analogRaw={mode['source_analog']} gamePause={pause} "
            "CControllableCamera__ReceiveButtonAction_Entry targetIController=03d8d914 camera=03d8d910 "
            f"button={mode['source_button']} rawButton={mode['source_raw']} analogRaw={mode['source_analog']} gamePause={pause} "
            f"curPos={cur_b} tempPos={cur_b} curOri00_01_02=3f5f719f/bef9deec/00000000 "
            "tempOri00_01_02=3f5f719f/bef9deec/00000000 "
            "CControllableCamera__PrepareForInterpolation_Delta camera=03d8d910 "
            f"gamePause={pause} frameCount=000001c2 lastFrame=000001c1 curPos={cur_b} tempPos={temp_b} "
            "curOri00_01_02=3f5f719f/bef9deec/00000000 tempOri00_01_02=3f5f719f/bef9deec/00000000 "
        )

    pre_q = q_chunk("0", "43900000/43730000/c141c8b3/00000002", "43901000/43731000/c141c8b3/00000002", "43902000/43732000/c141c8b3/00000002") if pre_q_hits_cave else ""
    on = (
        "CGame__ReceiveButtonAction game=008a9a98 fromController=03d4c6b0 button=1 pause=0 free0=0 free1=0 "
        "player0=0456b340 player1=00000000 cam0=03a57e40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
        "CGame__ToggleFreeCameraOn game=008a9a98 player=0 pauseBefore=0 freeBefore0=0 freeBefore1=0 "
        "player0=0456b340 player1=00000000 cam0=03a57e40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
        "CGame__SetCurrentCamera game=008a9a98 player=0 camera=03d8d910 releaseOld=0 pause=0 free0=0 free1=0 "
        "cam0=03a57e40 cam1=00000000 oldCam0=03a57e40 oldCam1=00000000 "
    )
    active_q = q_chunk("0", "43905800/43734000/c141c8b3/00000002", "43901988/43741f72/c141c8b3/00000002", "438fdb10/4374fee4/c141c8b3/00000002")
    def key_once(pause: str) -> str:
        if missing_key_once:
            return ""
        return (
            f"PlatformInput__ConsumeKeyOnce key=79 rawKey=0000004f globalOnceBefore=01 gamePause={pause} "
            f"CPCController__GetKeyOnce controller=03d4c6b0 key=79 arg4=0000004f arg8=00000000 globalOnceO=01 gamePause={pause} "
            f"PlatformInput__GetKeyOnceCore input=00855bb0 key=79 rawKey=0000004f onceByteBefore=01 globalOnceO=01 consumedQueue=00855424 gamePause={pause} "
        )
    pause = "" if missing_pause else (
        key_once("0") +
        "CController__SendButtonAction controller=03d4c6b0 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=0 "
        "inputDevice=00000009 controllerConfig=00000002 buttons0=00000000 buttons1=00000000 buttons2=00000000 target=03d8d914 targetVtable=005d9340 "
        "CControllableCamera__ReceiveButtonAction_Entry targetIController=03d8d914 camera=03d8d910 button=56 rawButton=00000038 "
        "analogRaw=3f800000 gamePause=0 curPos=43901988/43741f72/c141c8b3/00000002 tempPos=438fdb10/4374fee4/c141c8b3/00000002 "
        "curOri00_01_02=3f5f719f/bef9deec/00000000 tempOri00_01_02=3f5f719f/bef9deec/00000000 "
        "CGame__Pause game=008a9a98 pauseBefore=0 togglePauseMenu=0 fromController=00000000 free0=1 free1=0 pauseMenu=03ab1010 "
    )
    paused_q = q_chunk("1", "438fdb10/4374fee4/c141c8b3/00000002", "438f9c98/4375de56/c141c8b3/00000002", "438f5e20/4376bdc8/c141c8b3/00000002")
    unpause = (
        key_once("1") +
        "CController__SendButtonAction controller=03d4c6b0 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=1 "
        "inputDevice=00000009 controllerConfig=00000002 buttons0=00000000 buttons1=00000000 buttons2=00000000 target=03d8d914 targetVtable=005d9340 "
        "CControllableCamera__ReceiveButtonAction_Entry targetIController=03d8d914 camera=03d8d910 button=56 rawButton=00000038 "
        "analogRaw=3f800000 gamePause=1 curPos=438f9c98/4375de56/c141c8b3/00000002 tempPos=438f5e20/4376bdc8/c141c8b3/00000002 "
        "curOri00_01_02=3f5f719f/bef9deec/00000000 tempOri00_01_02=3f5f719f/bef9deec/00000000 "
        "CGame__UnPause game=008a9a98 pauseBefore=1 free0=1 free1=0 pauseMenu=03ab1010 "
    )
    off = (
        "CGame__ReceiveButtonAction game=008a9a98 fromController=03d4c6b0 button=1 pause=0 free0=1 free1=0 "
        "player0=0456b340 player1=00000000 cam0=03d8d910 cam1=00000000 oldCam0=03a57e40 oldCam1=00000000 "
        "CGame__SetCurrentCamera game=008a9a98 player=0 camera=03a57e40 releaseOld=1 pause=0 free0=0 free1=0 "
        "cam0=03d8d910 cam1=00000000 oldCam0=03a57e40 oldCam1=00000000 "
    )
    post_q = ""
    chunks = [pre_q, on, active_q, pause, paused_q, unpause, off, post_q]
    offsets: list[tuple[int, int]] = []
    cursor = 0
    for chunk in chunks:
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
            "inputSequencesSent": 8,
            "focusedInputSequences": 8,
            "inputWindowMessageEventsSent": 0,
        },
        "captures": [{"status": "captured", "fileSize": 1024, "visualProof": True}],
        "inputCdbWindows": [
            {"index": 1, "sequence": "down:Q,wait:500,up:Q", "logStartByte": offsets[0][0], "logEndByte": offsets[0][1]},
            {"index": 2, "sequence": "tap:F,wait:500", "logStartByte": offsets[1][0], "logEndByte": offsets[1][1]},
            {"index": 3, "sequence": "down:Q,wait:1000,up:Q", "logStartByte": offsets[2][0], "logEndByte": offsets[2][1]},
            {"index": 4, "sequence": "tap:O,wait:500", "logStartByte": offsets[3][0], "logEndByte": offsets[3][1]},
            {"index": 5, "sequence": "down:Q,wait:1000,up:Q", "logStartByte": offsets[4][0], "logEndByte": offsets[4][1]},
            {"index": 6, "sequence": "tap:O,wait:500", "logStartByte": offsets[5][0], "logEndByte": offsets[5][1]},
            {"index": 7, "sequence": "tap:F,wait:500", "logStartByte": offsets[6][0], "logEndByte": offsets[6][1]},
            {"index": 8, "sequence": "down:Q,wait:500,up:Q", "logStartByte": offsets[7][0], "logEndByte": offsets[7][1]},
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
            summary = validate_artifact(make_artifact(Path(temp_dir), proof_mode=proof_mode), proof_mode=proof_mode)
            require(summary["activeQCaveCount"] == 2, f"self-test expected two active Q cave rows for {proof_mode}")
            require(summary["pausedQCaveCount"] == 2, f"self-test expected two paused Q cave rows for {proof_mode}")
        for label, kwargs in (
            ("missing pause rows should fail", {"missing_pause": True}),
            ("missing upstream O key-once rows should fail", {"missing_key_once": True}),
            ("pre-free-camera Q cave should fail", {"pre_q_hits_cave": True}),
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    validate_artifact(make_artifact(Path(temp_dir), proof_mode=proof_mode, **kwargs), proof_mode=proof_mode)
                except ArtifactError:
                    pass
                else:
                    raise ArtifactError(f"{label} for {proof_mode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Path to winui-safe-copy-live-runtime-smoke.v1 artifact JSON.")
    parser.add_argument("--mode", choices=sorted(PROOF_MODES), default="forward")
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print(json.dumps({"status": "PASS", "selfTest": True, "modes": sorted(PROOF_MODES)}, indent=2))
            return 0
        if not args.artifact:
            raise ArtifactError("artifact path is required unless --self-test is used")
        summary = validate_artifact(Path(args.artifact), min_capture_count=args.min_capture_count, proof_mode=args.mode)
        print(json.dumps(summary, indent=2))
        return 0
    except ArtifactError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
