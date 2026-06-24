#!/usr/bin/env python3
"""Classify CDB-backed safe-copy pause O-scan initializer runtime artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "pause-o-scan-initializer-observer.cdb.txt"
PATCH_KEY = "pause_o_scan_initializer_experiment"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
REQUIRED_PATCH_KEYS = BASE_PATCH_KEYS | {PATCH_KEY}
ENTRY_ID_VIEW_BASE = 0x008892DC
ROW_STRIDE_DWORDS = 8
TABLE_DUMP_WORDS = 0x220
BUTTON_PAUSE = 56
KEY_ONCE = 8
KEY_ON = 9
O_KEY_ARGS = {0x18, 0x4F}


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


def signed32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


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


DD_LINE_RE = re.compile(r"^(?P<address>[0-9a-f`]{8,17})\s+(?P<values>(?:[0-9a-f]{8}\s*){1,8})$", re.IGNORECASE)


def parse_dd_words(text: str) -> dict[int, int]:
    words_by_address: dict[int, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = DD_LINE_RE.match(line)
        if not match:
            continue
        address = int(match.group("address").replace("`", ""), 16)
        values = [int(value, 16) for value in match.group("values").split()]
        for offset, value in enumerate(values):
            words_by_address[address + offset * 4] = value
    return words_by_address


def byte_from_unaligned_dd(words_by_address: dict[int, int], address: int) -> int | None:
    word = words_by_address.get(address)
    if word is None:
        return None
    return word & 0xFF


def parse_table_rows(words_by_address: dict[int, int], base: int = ENTRY_ID_VIEW_BASE) -> tuple[list[dict[str, Any]], bool]:
    words: list[int] = []
    for index in range(TABLE_DUMP_WORDS):
        address = base + index * 4
        if address not in words_by_address:
            break
        words.append(words_by_address[address])
    require(len(words) >= ROW_STRIDE_DWORDS, "mapping-table dd output was not found")

    rows: list[dict[str, Any]] = []
    sentinel_found = False
    for index in range(0, len(words) - ROW_STRIDE_DWORDS + 1, ROW_STRIDE_DWORDS):
        row_words = words[index : index + ROW_STRIDE_DWORDS]
        entry_id = signed32(row_words[0])
        if entry_id == -1:
            sentinel_found = True
            break
        rows.append(
            {
                "index": index // ROW_STRIDE_DWORDS,
                "entryId": entry_id,
                "raw": [f"{value & 0xFFFFFFFF:08x}" for value in row_words],
                "slot0": decode_slot(row_words[1], row_words[2], row_words[3]),
                "slot1": decode_slot(row_words[4], row_words[5], row_words[6]),
            }
        )
    return rows, sentinel_found


def decode_slot(input_code: int, push_type: int, key_arg: int) -> dict[str, int]:
    return {
        "inputCode": signed32(input_code),
        "pushType": signed32(push_type),
        "keyArg": signed32(key_arg),
    }


def pause_o_slots(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for row in rows:
        if row["entryId"] != BUTTON_PAUSE:
            continue
        for slot_name in ("slot0", "slot1"):
            slot = row[slot_name]
            if slot["pushType"] in {KEY_ONCE, KEY_ON} and slot["keyArg"] in O_KEY_ARGS:
                hits.append(
                    {
                        "row": row["index"],
                        "slot": slot_name,
                        "pushType": slot["pushType"],
                        "keyArg": slot["keyArg"],
                    }
                )
    return hits


def classify_table(rows: list[dict[str, Any]], hits: list[dict[str, Any]]) -> str:
    if hits:
        return "runtime-table-o-pause-slot-present"
    if any(row["entryId"] == BUTTON_PAUSE for row in rows):
        return "runtime-table-pause-row-present-without-o-slot"
    return "runtime-table-no-pause-row"


def regex_rows(pattern: str, text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in re.finditer(pattern, text, flags=re.IGNORECASE)]


def event_rows(kind: str, pattern: str, text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        row: dict[str, Any] = dict(match.groupdict())
        row["_kind"] = kind
        row["_start"] = match.start()
        row["_end"] = match.end()
        rows.append(row)
    return rows


GET_KEY_ONCE_RE = (
    r"PauseOScan__GetKeyOnce controller=(?P<controller>[0-9a-f]+) "
    r"arg4=(?P<arg4>[0-9a-f]+) arg8=(?P<arg8>[0-9a-f]+) "
    r"onceVkO=(?P<once_vk_o>[0-9a-f]+) onceScanO=(?P<once_scan_o>[0-9a-f]+) "
    r"onVkO=(?P<on_vk_o>[0-9a-f]+) onScanO=(?P<on_scan_o>[0-9a-f]+) "
    r"state3VkO=(?P<state3_vk_o>[0-9a-f]+) state3ScanO=(?P<state3_scan_o>[0-9a-f]+) "
    r"gamePause=(?P<pause>\d+)"
)
GET_KEY_ONCE_CORE_RE = (
    r"PauseOScan__GetKeyOnceCore input=(?P<input>[0-9a-f]+) "
    r"key=(?P<key>[0-9a-f]+) onceByteBefore=(?P<once>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
CONSUME_RE = (
    r"PauseOScan__ConsumeKeyOnce key=(?P<key>[0-9a-f]+) "
    r"globalOnceBefore=(?P<once>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
SEND_RE = (
    r"PauseOScan__SendButtonAction controller=(?P<controller>[0-9a-f]+) "
    r"button=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
CAMERA_RE = (
    r"PauseOScan__CameraReceive targetIController=(?P<target>[0-9a-f]+) "
    r"camera=(?P<camera>[0-9a-f]+) button=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) "
    r"analogRaw=(?P<analog>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
PAUSE_RE = (
    r"PauseOScan__Pause game=(?P<game>[0-9a-f]+) pauseBefore=(?P<pause_before>\d+)"
    r" togglePauseMenu=(?P<toggle_pause_menu>\d+) fromController=(?P<from_controller>[0-9a-f]+) "
    r"free0=(?P<free0>\d+) free1=(?P<free1>\d+) pauseMenu=(?P<pause_menu>[0-9a-f]+)"
)
UNPAUSE_RE = (
    r"PauseOScan__UnPause game=(?P<game>[0-9a-f]+) pauseBefore=(?P<pause_before>\d+)"
    r" free0=(?P<free0>\d+) free1=(?P<free1>\d+) pauseMenu=(?P<pause_menu>[0-9a-f]+)"
)
RESUME_PERSIST_RE = (
    r"PauseOScan__PauseMenuResumePersist pauseMenu=(?P<pause_menu>[0-9a-f]+) "
    r"gamePause=(?P<pause>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+)"
)
MENU_RE = (
    r"PauseOScan__PauseMenuInit pauseMenu=(?P<pause_menu>[0-9a-f]+)"
    r" activateControl=(?P<activate_control>\d+) gamePause=(?P<pause>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+)"
)
GAMEINTERFACE_RE = r"PauseOScan__GameInterfaceMenuInput gameInterface=(?P<game_interface>[0-9a-f]+)"


def hex_values(rows: list[dict[str, str]], *keys: str) -> list[str]:
    values: set[str] = set()
    for row in rows:
        for key in keys:
            value = row.get(key)
            if value:
                values.add(value.lower().rjust(8, "0"))
    return sorted(values)


def any_nonzero_byte(row: dict[str, str], keys: tuple[str, ...]) -> bool:
    return any(row.get(key) and int(row[key], 16) != 0 for key in keys)


def normalize_path_text(value: str) -> str:
    return value.replace("/", "\\").lower()


def row_int(row: dict[str, Any], key: str, base: int = 10, default: int | None = None) -> int | None:
    value = row.get(key)
    if value is None:
        return default
    try:
        return int(str(value), base)
    except ValueError:
        return default


def zero_free_flags(rows: list[dict[str, str]]) -> bool:
    for row in rows:
        free0 = row_int(row, "free0")
        free1 = row_int(row, "free1")
        if free0 == 0 and free1 == 0:
            return True
    return False


def row_has_zero_free_flags(row: dict[str, Any]) -> bool:
    return row_int(row, "free0") == 0 and row_int(row, "free1") == 0


def same_optional_pointer(left: dict[str, Any], right: dict[str, Any], key: str) -> bool:
    left_value = str(left.get(key, "")).lower()
    right_value = str(right.get(key, "")).lower()
    return not left_value or not right_value or left_value == right_value


def sequence_has_input(sequence: str, key: str) -> bool:
    return re.search(rf"(?:^|[,;])\s*(?:tap|down):{re.escape(key)}(?:[,;]|$)", sequence, flags=re.IGNORECASE) is not None


def exact_level_100_launch(arguments: list[str]) -> bool:
    return arguments == ["-skipfmv", "-level", "100"]


def is_o_query_event(row: dict[str, Any]) -> bool:
    kind = row.get("_kind")
    if kind == "get":
        return row_int(row, "arg4", 16) in O_KEY_ARGS or row_int(row, "arg8", 16) in O_KEY_ARGS
    if kind in {"core", "consume"}:
        return row_int(row, "key", 16) in O_KEY_ARGS
    return False


def is_button_pause_send_event(row: dict[str, Any]) -> bool:
    return row.get("_kind") == "send" and row_int(row, "button") == BUTTON_PAUSE


def has_ordered_o_pause_path(events: list[dict[str, Any]], *, transition_kind: str, required_pause_state: int) -> bool:
    for o_event in events:
        if not is_o_query_event(o_event) or row_int(o_event, "pause") != required_pause_state:
            continue
        o_controller = str(o_event.get("controller", "")).lower()
        for send_event in events:
            if send_event["_start"] <= o_event["_end"] or not is_button_pause_send_event(send_event):
                continue
            if row_int(send_event, "pause") != required_pause_state:
                continue
            send_controller = str(send_event.get("controller", "")).lower()
            if o_controller and send_controller and o_controller != send_controller:
                continue
            for transition_event in events:
                if transition_event["_start"] <= send_event["_end"] or transition_event.get("_kind") != transition_kind:
                    continue
                if row_int(transition_event, "pause_before") == required_pause_state:
                    return True
    return False


def has_ordered_normal_o_pause_path(events: list[dict[str, Any]]) -> bool:
    for o_event in events:
        if not is_o_query_event(o_event) or row_int(o_event, "pause") != 0:
            continue
        o_controller = str(o_event.get("controller", "")).lower()
        for send_event in events:
            if send_event["_start"] <= o_event["_end"] or not is_button_pause_send_event(send_event):
                continue
            if row_int(send_event, "pause") != 0:
                continue
            send_controller = str(send_event.get("controller", "")).lower()
            if o_controller and send_controller and o_controller != send_controller:
                continue
            for pause_event in events:
                if pause_event["_start"] <= send_event["_end"] or pause_event.get("_kind") != "pause":
                    continue
                if row_int(pause_event, "pause_before") != 0 or not row_has_zero_free_flags(pause_event):
                    continue
                for menu_event in events:
                    if menu_event["_start"] <= pause_event["_end"] or menu_event.get("_kind") != "menu":
                        continue
                    if (
                        row_has_zero_free_flags(menu_event)
                        and row_int(menu_event, "pause") == 1
                        and same_optional_pointer(pause_event, menu_event, "pause_menu")
                    ):
                        return True
    return False


def has_ordered_normal_resume_path(events: list[dict[str, Any]]) -> bool:
    for resume_event in events:
        if resume_event.get("_kind") != "resume_persist":
            continue
        if row_int(resume_event, "pause") != 1 or not row_has_zero_free_flags(resume_event):
            continue
        for unpause_event in events:
            if unpause_event["_start"] <= resume_event["_end"] or unpause_event.get("_kind") != "unpause":
                continue
            if (
                row_int(unpause_event, "pause_before") == 1
                and row_has_zero_free_flags(unpause_event)
                and same_optional_pointer(resume_event, unpause_event, "pause_menu")
            ):
                return True
    return False


def window_summary(sequence: str, text: str, byte_count: int) -> dict[str, Any]:
    get_key_once = regex_rows(GET_KEY_ONCE_RE, text)
    get_key_once_core = regex_rows(GET_KEY_ONCE_CORE_RE, text)
    consume = regex_rows(CONSUME_RE, text)
    send = regex_rows(SEND_RE, text)
    camera = regex_rows(CAMERA_RE, text)
    pause = regex_rows(PAUSE_RE, text)
    unpause = regex_rows(UNPAUSE_RE, text)
    resume_persist = regex_rows(RESUME_PERSIST_RE, text)
    menu = regex_rows(MENU_RE, text)
    game_interface = regex_rows(GAMEINTERFACE_RE, text)
    events = (
        event_rows("get", GET_KEY_ONCE_RE, text)
        + event_rows("core", GET_KEY_ONCE_CORE_RE, text)
        + event_rows("consume", CONSUME_RE, text)
        + event_rows("send", SEND_RE, text)
        + event_rows("camera", CAMERA_RE, text)
        + event_rows("pause", PAUSE_RE, text)
        + event_rows("unpause", UNPAUSE_RE, text)
        + event_rows("resume_persist", RESUME_PERSIST_RE, text)
        + event_rows("menu", MENU_RE, text)
        + event_rows("game_interface", GAMEINTERFACE_RE, text)
    )
    events.sort(key=lambda row: int(row["_start"]))
    key_values = set(hex_values(get_key_once, "arg4", "arg8")) | set(hex_values(get_key_once_core, "key")) | set(hex_values(consume, "key"))
    o_key_query = bool({"00000018", "0000004f"} & key_values)
    o_state_latched = any(
        any_nonzero_byte(row, ("once_vk_o", "once_scan_o", "on_vk_o", "on_scan_o", "state3_vk_o", "state3_scan_o"))
        for row in get_key_once
    )
    button_pause_dispatched = any(row["button"] == "56" for row in send) or any(row["button"] == "56" for row in camera)
    ordered_pause = has_ordered_o_pause_path(events, transition_kind="pause", required_pause_state=0)
    ordered_unpause = has_ordered_o_pause_path(events, transition_kind="unpause", required_pause_state=1)
    normal_pause_path = has_ordered_normal_o_pause_path(events)
    normal_resume_path = has_ordered_normal_resume_path(events)
    return {
        "sequence": sequence,
        "cdbByteCount": byte_count,
        "getKeyOnceCount": len(get_key_once),
        "getKeyOnceCoreCount": len(get_key_once_core),
        "consumeKeyOnceCount": len(consume),
        "sendButtonActionCount": len(send),
        "cameraReceiveCount": len(camera),
        "pauseCount": len(pause),
        "unpauseCount": len(unpause),
        "pauseMenuResumePersistCount": len(resume_persist),
        "pauseMenuInitCount": len(menu),
        "gameInterfaceMenuInputCount": len(game_interface),
        "keyValues": sorted(key_values),
        "sendButtons": sorted({row["button"] for row in send}),
        "cameraButtons": sorted({row["button"] for row in camera}),
        "oKeyQueryObserved": o_key_query,
        "oKeyStateLatched": o_state_latched,
        "buttonPauseDispatched": button_pause_dispatched,
        "orderedOToButtonPauseThenPause": ordered_pause,
        "orderedOToButtonPauseThenUnPause": ordered_unpause,
        "normalGameplayOrderedPausePath": normal_pause_path,
        "normalGameplayOrderedResumePath": normal_resume_path,
        "normalGameplayPauseFreeFlags": normal_pause_path,
        "normalGameplayUnPauseFreeFlags": normal_resume_path,
        "normalGameplayResumePersistFreeFlags": normal_resume_path,
        "normalGameplayPauseMenuFreeFlags": normal_pause_path,
        "enterInputObserved": sequence_has_input(sequence, "ENTER"),
    }


def is_strict_pause_window(row: dict[str, Any]) -> bool:
    return bool(row["orderedOToButtonPauseThenPause"])


def is_strict_unpause_window(row: dict[str, Any]) -> bool:
    return bool(row["orderedOToButtonPauseThenUnPause"])


def is_normal_gameplay_o_pause_window(row: dict[str, Any]) -> bool:
    return (
        bool(row["normalGameplayOrderedPausePath"])
        and int(row["pauseMenuInitCount"]) > 0
        and int(row["cameraReceiveCount"]) == 0
    )


def is_normal_gameplay_resume_window(row: dict[str, Any]) -> bool:
    return (
        bool(row["enterInputObserved"])
        and bool(row["normalGameplayOrderedResumePath"])
        and int(row["unpauseCount"]) > 0
        and int(row["pauseMenuResumePersistCount"]) > 0
        and int(row["cameraReceiveCount"]) == 0
    )


def classify_input(o_windows: list[dict[str, Any]]) -> str:
    strict_pause = any(is_strict_pause_window(row) for row in o_windows)
    strict_unpause = any(is_strict_unpause_window(row) for row in o_windows)
    pause = any(row["pauseCount"] > 0 for row in o_windows)
    unpause = any(row["unpauseCount"] > 0 for row in o_windows)
    dispatch = any(row["buttonPauseDispatched"] for row in o_windows)
    query = any(row["oKeyQueryObserved"] for row in o_windows)
    latched = any(row["oKeyStateLatched"] for row in o_windows)
    if strict_pause and strict_unpause:
        return "ordered-o-window-pause-and-unpause-observed"
    if pause and unpause:
        return "pause-and-unpause-observed-without-ordered-o-dispatch-pair"
    if pause:
        return "o-pause-observed-without-unpause"
    if unpause:
        return "o-unpause-observed-without-pause"
    if dispatch:
        return "o-button-pause-dispatched-without-pause-call"
    if query:
        return "o-key-query-observed-without-button-pause"
    if latched:
        return "o-key-state-latched-without-o-query"
    return "o-window-without-o-query-or-dispatch"


def observer_log_path_and_target_pid(artifact: dict[str, Any]) -> tuple[Path, int]:
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
    return path, int_at(result, "targetProcessId")


def input_windows(artifact: dict[str, Any], log_path: Path) -> dict[int, tuple[str, str, int]]:
    rows = list_at(artifact, "inputCdbWindows")
    data = log_path.read_bytes()
    windows: dict[int, tuple[str, str, int]] = {}
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
        windows[index] = (sequence, data[start:end].decode("utf-8", errors="replace"), end - start)
    return windows


def validate_artifact(
    path: Path,
    min_capture_count: int = 1,
    require_positive: bool = False,
    require_normal_gameplay_positive: bool = False,
) -> dict[str, Any]:
    artifact = read_json(path)
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")
    source = object_at(artifact, "source")
    require(bool_at(source, "installedHashUnchanged"), "installed BEA.exe hash changed")
    require(bool_at(source, "overrideHashUnchanged"), "clean override BEA.exe hash changed")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "source save/options changed")

    safe_copy = object_at(artifact, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(REQUIRED_PATCH_KEYS.issubset(patch_keys), "safe copy did not apply the pause O-scan initializer patch set")
    safe_copy_exe = string_at(safe_copy, "ExecutablePath")
    exact_normal_patch_set = patch_keys == REQUIRED_PATCH_KEYS
    normal_profile_clean = (
        safe_copy.get("ProfilePresetId") in {None, ""}
        and safe_copy.get("ProfilePresetDisplayName") in {None, ""}
        and safe_copy.get("controlOptions") is None
    )

    baseline = object_at(artifact, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "preexisting BEA process was present")
    require(bool_at(baseline, "noBeaAfterStop"), "BEA process remained after stop")
    launch = object_at(artifact, "launch")
    require(bool_at(launch, "observedAlive"), "copied BEA process was not observed alive")
    launch_pid = int_at(launch, "processId")
    launch_arguments = string_list_at(launch, "arguments")
    level_100_launch = exact_level_100_launch(launch_arguments)
    require(bool_at(object_at(artifact, "stop"), "Success"), "managed copied-game stop failed")

    input_summary = object_at(artifact, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 1, "expected at least one input sequence")
    require(int_at(input_summary, "focusedInputSequences") == int_at(input_summary, "inputSequencesSent"), "not all input sequences were focused")
    require(int_at(input_summary, "inputWindowMessageEventsSent") == 0, "background/PostMessage input was used")

    captures = list_at(artifact, "captures")
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}")
    require(visual_capture_count(captures) >= min_capture_count, "not enough visual-proof captures")

    log_path, cdb_target_pid = observer_log_path_and_target_pid(artifact)
    require(cdb_target_pid == launch_pid, f"CDB target PID {cdb_target_pid} did not match launched PID {launch_pid}")
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    require("safe-copy pause O-scan initializer observer" in log_text, "pause O-scan observer marker missing")
    require(normalize_path_text(safe_copy_exe) in normalize_path_text(log_text), "CDB log does not reference the safe-copy BEA executable path")
    words_by_address = parse_dd_words(log_text)
    patch_byte = byte_from_unaligned_dd(words_by_address, 0x005144CD)
    require(patch_byte is not None, "patch-site dd output was not found")
    rows, sentinel_found = parse_table_rows(words_by_address)
    require(sentinel_found, "mapping-table sentinel was not found in dumped row range")
    o_slots = pause_o_slots(rows)
    table_classification = classify_table(rows, o_slots)

    windows = input_windows(artifact, log_path)
    require(windows, "expected CDB input windows")
    summaries: list[dict[str, Any]] = []
    for index in sorted(windows):
        sequence, text, byte_count = windows[index]
        summary = window_summary(sequence, text, byte_count)
        summary["windowIndex"] = index
        summaries.append(summary)
    o_windows = [summary for summary in summaries if re.search(r"(?:^|[,;])\s*(?:tap|down):O(?:[,;]|$)", summary["sequence"], flags=re.IGNORECASE)]
    require(o_windows, "expected at least one O input window")
    input_classification = classify_input(o_windows)
    strict_pause_windows = [summary for summary in o_windows if is_strict_pause_window(summary)]
    strict_unpause_windows = [summary for summary in o_windows if is_strict_unpause_window(summary)]
    normal_pause_windows = [summary for summary in o_windows if is_normal_gameplay_o_pause_window(summary)]
    first_normal_pause_index = min((int(summary["windowIndex"]) for summary in normal_pause_windows), default=0)
    normal_resume_windows = [
        summary
        for summary in summaries
        if first_normal_pause_index > 0
        and int(summary["windowIndex"]) > first_normal_pause_index
        and is_normal_gameplay_resume_window(summary)
    ]
    positive = (
        patch_byte == 0x18
        and table_classification == "runtime-table-o-pause-slot-present"
        and input_classification == "ordered-o-window-pause-and-unpause-observed"
        and bool(strict_pause_windows)
        and bool(strict_unpause_windows)
    )
    normal_gameplay_positive = (
        patch_byte == 0x18
        and table_classification == "runtime-table-o-pause-slot-present"
        and exact_normal_patch_set
        and normal_profile_clean
        and level_100_launch
        and bool(normal_pause_windows)
        and bool(normal_resume_windows)
    )
    if require_positive:
        require(positive, f"positive pause proof was not established: {table_classification}; {input_classification}; patch byte 0x{patch_byte:02x}")
    if require_normal_gameplay_positive:
        require(
            normal_gameplay_positive,
            "normal gameplay pause proof was not established: "
            f"exactPatchSet={exact_normal_patch_set}; profileClean={normal_profile_clean}; level100={level_100_launch}; "
            f"normalPauseWindows={len(normal_pause_windows)}; normalResumeWindows={len(normal_resume_windows)}; "
            f"{table_classification}; patch byte 0x{patch_byte:02x}",
        )

    return {
        "schema": "winui-pause-o-scan-initializer-runtime-diagnostic.v1",
        "artifact": str(path),
        "cdbLog": str(log_path),
        "patchByteAt005144cd": f"0x{patch_byte:02x}",
        "patchBytePatched": patch_byte == 0x18,
        "patchKeys": sorted(patch_keys),
        "exactNormalGameplayPatchSet": exact_normal_patch_set,
        "normalGameplayProfileClean": normal_profile_clean,
        "launchArguments": launch_arguments,
        "level100Launch": level_100_launch,
        "launchProcessId": launch_pid,
        "cdbTargetProcessId": cdb_target_pid,
        "exactPidMatched": cdb_target_pid == launch_pid,
        "visualCaptureCount": visual_capture_count(captures),
        "mappingTable": {
            "entryIdViewBase": f"0x{ENTRY_ID_VIEW_BASE:08x}",
            "rowStrideDwords": ROW_STRIDE_DWORDS,
            "rowCount": len(rows),
            "sentinelFound": sentinel_found,
            "pauseRows": [row for row in rows if row["entryId"] == BUTTON_PAUSE],
            "oPauseSlots": o_slots,
            "classification": table_classification,
        },
        "inputWindows": summaries,
        "oWindowClassification": input_classification,
        "strictOPauseWindowCount": len(strict_pause_windows),
        "strictOUnpauseWindowCount": len(strict_unpause_windows),
        "normalGameplayOPauseWindowCount": len(normal_pause_windows),
        "normalGameplayResumeWindowCount": len(normal_resume_windows),
        "positiveRuntimeProof": positive,
        "normalGameplayPositiveRuntimeProof": normal_gameplay_positive,
        "claim": "safe-copy exact-PID CDB observer classified ordered O-window pause initializer evidence",
        "claimBoundary": (
            "Diagnostic classification only unless positiveRuntimeProof is true. A positive result requires ordered same-window CDB "
            "evidence, not a full debugger call-chain proof. This does not prove control feel, all gameplay pause paths, "
            "menu UX safety, online networking, rebuild parity, or no-noticeable-difference parity."
        ),
    }


def make_artifact(root: Path, *, positive: bool, dispatch: bool | None = None, ordered: bool = True, normal: bool = False) -> Path:
    if dispatch is None:
        dispatch = positive
    log_path = root / "windbg.log"
    exe_path = root / "GameProfiles" / "safe" / "BEA.exe"
    patch_word = "086a3818" if positive else "086a3801"
    table_key = "00000018" if positive else "00000001"
    table = (
        "008892dc  00000038 00000000 00000008 " + table_key + " ffffffff 00000000 00000000 00000000\n"
        "008892fc  ffffffff ffffffff 00000000 ffffffff ffffffff 00000000 ffffffff 00000000\n"
    )
    prefix = f"ModLoad: 00400000 009d8000   {exe_path}\n=== safe-copy pause O-scan initializer observer ===\n005144cd  {patch_word}\n" + table
    o1 = (
        "PauseOScan__GetKeyOnce controller=03d4c6b0 arg4=00000018 arg8=00000000 onceVkO=00 onceScanO=01 onVkO=00 onScanO=01 state3VkO=00 state3ScanO=00 gamePause=0\n"
        "PauseOScan__GetKeyOnceCore input=00855bb0 key=00000018 onceByteBefore=01 gamePause=0\n"
    )
    if positive:
        if dispatch:
            o1 += (
                "PauseOScan__SendButtonAction controller=03d4c6b0 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=0\n"
            )
            if not normal:
                o1 += (
                    "PauseOScan__CameraReceive targetIController=03d8d914 camera=03d8d910 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=0\n"
                )
        free0 = 0 if normal else 1
        o1 += (
            f"PauseOScan__Pause game=008a9a98 pauseBefore=0 togglePauseMenu={1 if normal else 0} fromController=03d4c6b0 free0={free0} free1=0 pauseMenu=03ab1010\n"
        )
        if normal:
            o1 += (
                "PauseOScan__PauseMenuInit pauseMenu=03ab1010 activateControl=1 gamePause=1 free0=0 free1=0\n"
            )
    o2 = "" if normal else (
        "PauseOScan__GetKeyOnce controller=03d4c6b0 arg4=00000018 arg8=00000000 onceVkO=00 onceScanO=01 onVkO=00 onScanO=01 state3VkO=00 state3ScanO=00 gamePause=1\n"
    )
    if positive:
        if dispatch:
            if normal:
                o2 += "PauseOScan__GameInterfaceMenuInput gameInterface=03d90000 controlContext=03ab1010 buttonId=51 buttonContext=0 gamePause=1 free0=0 free1=0\n"
            else:
                o2 += (
                    "PauseOScan__SendButtonAction controller=03d4c6b0 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=1\n"
                    "PauseOScan__CameraReceive targetIController=03d8d914 camera=03d8d910 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=1\n"
                )
        free0 = 0 if normal else 1
        o2 += (
            f"PauseOScan__PauseMenuResumePersist pauseMenu=03ab1010 gamePause=1 free0={free0} free1=0\n"
            f"PauseOScan__UnPause game=008a9a98 pauseBefore=1 free0={free0} free1=0 pauseMenu=03ab1010\n"
        )
    if not ordered:
        o1 = (
            "PauseOScan__Pause game=008a9a98 pauseBefore=0 togglePauseMenu=0 fromController=00000000 free0=1 free1=0 pauseMenu=03ab1010\n"
            "PauseOScan__GetKeyOnce controller=03d4c6b0 arg4=00000018 arg8=00000000 onceVkO=00 onceScanO=01 onVkO=00 onScanO=01 state3VkO=00 state3ScanO=00 gamePause=0\n"
            "PauseOScan__SendButtonAction controller=03d4c6b0 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=0\n"
        )
        o2 = (
            "PauseOScan__UnPause game=008a9a98 pauseBefore=1 free0=1 free1=0 pauseMenu=03ab1010\n"
            "PauseOScan__GetKeyOnce controller=03d4c6b0 arg4=00000018 arg8=00000000 onceVkO=00 onceScanO=01 onVkO=00 onScanO=01 state3VkO=00 state3ScanO=00 gamePause=1\n"
            "PauseOScan__SendButtonAction controller=03d4c6b0 button=56 rawButton=00000038 analogRaw=3f800000 gamePause=1\n"
        )
    chunks = [prefix, o1, o2]
    offsets: list[tuple[int, int]] = []
    cursor = 0
    for chunk in chunks:
        start = cursor
        cursor += len(chunk.encode("utf-8"))
        offsets.append((start, cursor))
    log_path.write_text("".join(chunks), encoding="utf-8", newline="\n")
    artifact = {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {"patchKeys": sorted(REQUIRED_PATCH_KEYS), "ExecutablePath": str(exe_path)},
        "launch": {"observedAlive": True, "processId": 1234, "arguments": ["-skipfmv", "-level", "100"]},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "inputSummary": {
            "inputSequencesSent": 2,
            "focusedInputSequences": 2,
            "inputWindowMessageEventsSent": 0,
        },
        "captures": [{"status": "captured", "fileSize": 1024, "visualProof": True}],
        "inputCdbWindows": [
            {"index": 1, "sequence": "tap:O,wait:500", "logStartByte": offsets[1][0], "logEndByte": offsets[1][1]},
            {"index": 2, "sequence": f"tap:{'ENTER' if normal else 'O'},wait:500", "logStartByte": offsets[2][0], "logEndByte": offsets[2][1]},
        ],
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path), "targetProcessId": 1234},
            "cleanup": {"status": "stopped"},
        },
    }
    path = root / "artifact.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(make_artifact(Path(temp_dir), positive=True), require_positive=True)
        require(summary["positiveRuntimeProof"] is True, "positive self-test did not classify positive")
        require(summary["normalGameplayPositiveRuntimeProof"] is False, "free-camera-style positive should not classify as normal gameplay")
        try:
            validate_artifact(make_artifact(Path(temp_dir), positive=True), require_normal_gameplay_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("free-camera-style positive unexpectedly passed --require-normal-gameplay-positive")
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(
            make_artifact(Path(temp_dir), positive=True, normal=True),
            require_normal_gameplay_positive=True,
        )
        require(summary["normalGameplayPositiveRuntimeProof"] is True, "normal gameplay positive self-test did not classify positive")
        require(summary["positiveRuntimeProof"] is False, "normal gameplay resume-key proof should not classify as O/O free-camera-style positive")
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_artifact(Path(temp_dir), positive=True, normal=True)
        artifact = read_json(path)
        artifact["inputCdbWindows"][1]["sequence"] = "tap:SPACE,wait:500"
        path.write_text(json.dumps(artifact), encoding="utf-8")
        try:
            validate_artifact(path, require_normal_gameplay_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("normal gameplay fixture unexpectedly passed without ENTER input")
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_artifact(Path(temp_dir), positive=True, normal=True)
        artifact = read_json(path)
        object_at(artifact, "launch")["arguments"] = ["-skipfmv", "-level", "850", "-configuration", "100"]
        path.write_text(json.dumps(artifact), encoding="utf-8")
        try:
            validate_artifact(path, require_normal_gameplay_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("normal gameplay fixture unexpectedly passed with non-adjacent level 100 token")
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_artifact(Path(temp_dir), positive=True, normal=True)
        log_path = path.parent / "windbg.log"
        log_text = log_path.read_text(encoding="utf-8")
        log_text = log_text.replace(
            "PauseOScan__Pause game=008a9a98 pauseBefore=0 togglePauseMenu=1 fromController=03d4c6b0 free0=0 free1=0 pauseMenu=03ab1010",
            "PauseOScan__Pause game=008a9a98 pauseBefore=0 togglePauseMenu=1 fromController=03d4c6b0 free0=1 free1=0 pauseMenu=03ab1010",
            1,
        )
        log_path.write_text(log_text, encoding="utf-8", newline="\n")
        try:
            validate_artifact(path, require_normal_gameplay_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("normal gameplay fixture unexpectedly passed with free-camera pause flags")
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_artifact(Path(temp_dir), positive=True, dispatch=False)
        summary = validate_artifact(path)
        require(summary["positiveRuntimeProof"] is False, "dispatchless pause/unpause self-test should stay diagnostic-only")
        try:
            validate_artifact(path, require_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("dispatchless pause/unpause self-test unexpectedly passed --require-positive")
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_artifact(Path(temp_dir), positive=True, ordered=False)
        summary = validate_artifact(path)
        require(summary["positiveRuntimeProof"] is False, "out-of-order co-window self-test should stay diagnostic-only")
        try:
            validate_artifact(path, require_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("out-of-order co-window self-test unexpectedly passed --require-positive")
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_artifact(Path(temp_dir), positive=True)
        artifact = read_json(path)
        object_at(object_at(artifact, "cdbObserver"), "result")["targetProcessId"] = 4321
        path.write_text(json.dumps(artifact), encoding="utf-8")
        try:
            validate_artifact(path, require_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("PID mismatch self-test unexpectedly passed --require-positive")
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(make_artifact(Path(temp_dir), positive=False))
        require(summary["positiveRuntimeProof"] is False, "negative self-test should stay diagnostic-only")
        try:
            validate_artifact(make_artifact(Path(temp_dir), positive=False), require_positive=True)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("negative self-test unexpectedly passed --require-positive")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--require-positive", action="store_true")
    parser.add_argument("--require-normal-gameplay-positive", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive")
        if args.self_test:
            self_test()
            print("WinUI pause O-scan initializer runtime artifact checker self-test: PASS")
            return 0
        require(args.artifact is not None, "artifact is required unless --self-test is used")
        print(
            json.dumps(
                validate_artifact(
                    args.artifact,
                    args.min_capture_count,
                    args.require_positive,
                    args.require_normal_gameplay_positive,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except ArtifactError as exc:
        print(f"WinUI pause O-scan initializer runtime artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
