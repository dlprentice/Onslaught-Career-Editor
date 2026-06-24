#!/usr/bin/env python3
"""Classify CDB-backed safe-copy free-camera F/O/Q key-census artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "free-camera-key-census-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
REQUIRED_PATCH_KEYS = {
    "free_camera_aurore_gate_bypass",
    "free_camera_keyboard_forward_q_hook",
    "free_camera_keyboard_forward_q_cave",
}
EXPECTED_SEQUENCE_PATTERNS = [
    r"tap:F,wait:\d+",
    r"(?:tap:O,wait:\d+|down:O,wait:\d+,up:O)",
    r"down:Q,wait:\d+,up:Q",
    r"tap:F,wait:\d+",
]
O_KEY_VALUES = {"0000004f", "00000018"}
O_KEY_BYTE_FIELDS = {
    "once_vk_o",
    "once_scan_o",
    "on_vk_o",
    "on_scan_o",
    "state3_vk_o",
    "state3_scan_o",
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


def hex_values(rows: list[dict[str, str]], *keys: str) -> list[str]:
    values: set[str] = set()
    for row in rows:
        for key in keys:
            value = row.get(key)
            if value:
                values.add(value.lower().rjust(8, "0"))
    return sorted(values)


def any_nonzero_byte(row: dict[str, str], keys: set[str]) -> bool:
    for key in keys:
        value = row.get(key)
        if value and int(value, 16) != 0:
            return True
    return False


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


GET_KEY_ONCE_RE = (
    r"FreeCameraKeyCensus__GetKeyOnce controller=(?P<controller>[0-9a-f]+) "
    r"arg4=(?P<arg4>[0-9a-f]+) arg8=(?P<arg8>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
KEY_BYTES_RE = (
    r"FreeCameraKeyCensus__KeyBytes onceVkO=(?P<once_vk_o>[0-9a-f]+) onceScanO=(?P<once_scan_o>[0-9a-f]+) "
    r"onceVkF=(?P<once_vk_f>[0-9a-f]+) onceScanF=(?P<once_scan_f>[0-9a-f]+) "
    r"onceVkQ=(?P<once_vk_q>[0-9a-f]+) onceScanQ=(?P<once_scan_q>[0-9a-f]+) "
    r"onVkO=(?P<on_vk_o>[0-9a-f]+) onScanO=(?P<on_scan_o>[0-9a-f]+) "
    r"onVkF=(?P<on_vk_f>[0-9a-f]+) onScanF=(?P<on_scan_f>[0-9a-f]+) "
    r"onVkQ=(?P<on_vk_q>[0-9a-f]+) onScanQ=(?P<on_scan_q>[0-9a-f]+) "
    r"state3VkO=(?P<state3_vk_o>[0-9a-f]+) state3ScanO=(?P<state3_scan_o>[0-9a-f]+) "
    r"state3VkF=(?P<state3_vk_f>[0-9a-f]+) state3ScanF=(?P<state3_scan_f>[0-9a-f]+) "
    r"state3VkQ=(?P<state3_vk_q>[0-9a-f]+) state3ScanQ=(?P<state3_scan_q>[0-9a-f]+)"
)
GET_KEY_ONCE_CORE_RE = (
    r"FreeCameraKeyCensus__GetKeyOnceCore input=(?P<input>[0-9a-f]+) "
    r"key=(?P<key>[0-9a-f]+) onceByteBefore=(?P<once>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
CONSUME_RE = (
    r"FreeCameraKeyCensus__ConsumeKeyOnce key=(?P<key>[0-9a-f]+) "
    r"globalOnceBefore=(?P<once>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
SEND_RE = (
    r"FreeCameraKeyCensus__SendButtonAction controller=(?P<controller>[0-9a-f]+) "
    r"button=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+) analogRaw=(?P<analog>[0-9a-f]+) gamePause=(?P<pause>\d+)"
)
CAMERA_RE = (
    r"FreeCameraKeyCensus__CameraReceive targetIController=(?P<target>[0-9a-f]+) "
    r"camera=(?P<camera>[0-9a-f]+) button=(?P<button>\d+) rawButton=(?P<raw>[0-9a-f]+)"
)
PAUSE_RE = r"FreeCameraKeyCensus__Pause game=(?P<game>[0-9a-f]+) pauseBefore=(?P<pause_before>\d+)"
UNPAUSE_RE = r"FreeCameraKeyCensus__UnPause game=(?P<game>[0-9a-f]+) pauseBefore=(?P<pause_before>\d+)"


def window_summary(sequence: str, text: str, byte_count: int) -> dict[str, Any]:
    get_key_once = regex_rows(GET_KEY_ONCE_RE, text)
    key_bytes = regex_rows(KEY_BYTES_RE, text)
    get_key_once_core = regex_rows(GET_KEY_ONCE_CORE_RE, text)
    consume = regex_rows(CONSUME_RE, text)
    send = regex_rows(SEND_RE, text)
    camera = regex_rows(CAMERA_RE, text)
    pause = regex_rows(PAUSE_RE, text)
    unpause = regex_rows(UNPAUSE_RE, text)
    get_key_once_args = hex_values(get_key_once, "arg4", "arg8")
    core_keys = hex_values(get_key_once_core, "key")
    consume_keys = hex_values(consume, "key")
    send_buttons = sorted({row["button"] for row in send})
    o_key_query_count = sum(1 for value in get_key_once_args + core_keys + consume_keys if value in O_KEY_VALUES)
    o_key_state_latched = any(any_nonzero_byte(row, O_KEY_BYTE_FIELDS) for row in key_bytes)
    pause_button_dispatched = "56" in send_buttons or any(row.get("button") == "56" for row in camera)
    return {
        "sequence": sequence,
        "cdbByteCount": byte_count,
        "getKeyOnceCount": len(get_key_once),
        "keyBytesCount": len(key_bytes),
        "getKeyOnceCoreCount": len(get_key_once_core),
        "consumeKeyOnceCount": len(consume),
        "sendButtonActionCount": len(send),
        "cameraReceiveCount": len(camera),
        "pauseCount": len(pause),
        "unpauseCount": len(unpause),
        "getKeyOnceArgs": get_key_once_args,
        "coreKeys": core_keys,
        "consumeKeys": consume_keys,
        "sendButtons": send_buttons,
        "cameraButtons": sorted({row["button"] for row in camera}),
        "oKeyQueryCount": o_key_query_count,
        "oKeyStateLatched": o_key_state_latched,
        "pauseButtonDispatched": pause_button_dispatched,
        "lastKeyBytes": key_bytes[-1] if key_bytes else None,
    }


def validate_common(artifact: dict[str, Any], min_capture_count: int) -> tuple[Path, dict[str, Any]]:
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")

    source = object_at(artifact, "source")
    require(bool_at(source, "installedHashUnchanged"), "installed BEA.exe hash changed")
    require(bool_at(source, "overrideHashUnchanged"), "clean override BEA.exe hash changed")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "source save/options changed")

    safe_copy = object_at(artifact, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "safe copy did not apply windowed compatibility patch keys")
    require(REQUIRED_PATCH_KEYS.issubset(patch_keys), "safe copy did not apply the free-camera key-census patch set")
    control_options = object_at(safe_copy, "controlOptions")
    require(control_options.get("requestedControllerConfig") == 2, "key census must use controller configuration 2")
    require(
        control_options.get("requestedConfig2CensusRowQe") == "movement-forward",
        "key census must bind config-2 movement-forward to Q/E in the copied options file",
    )

    launch = object_at(artifact, "launch")
    require(bool_at(launch, "observedAlive"), "copied BEA process was not observed alive")
    baseline = object_at(artifact, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "preexisting BEA process was present")
    require(bool_at(baseline, "noBeaAfterStop"), "BEA process remained after stop")
    require(bool_at(object_at(artifact, "stop"), "Success"), "managed copied-game stop failed")

    input_summary = object_at(artifact, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 4, "expected F/O/Q/F key-census input sequence set")
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


def classify_o_window(o_summary: dict[str, Any]) -> str:
    if o_summary["pauseButtonDispatched"] or o_summary["pauseCount"] or o_summary["unpauseCount"]:
        return "o-dispatch-or-pause-observed"
    if o_summary["oKeyQueryCount"]:
        return "o-specific-key-query-observed"
    if o_summary["oKeyStateLatched"]:
        return "o-key-state-latched-without-o-query"
    if o_summary["cdbByteCount"] > 0:
        return "o-window-polling-without-o-key-query"
    return "no-o-cdb-window-activity"


def validate_artifact(path: Path, min_capture_count: int = 1) -> dict[str, Any]:
    artifact = read_json(path)
    log_path, summary = validate_common(artifact, min_capture_count)
    windows = input_windows(artifact, log_path)
    require(sorted(windows) == [1, 2, 3, 4], "expected exactly four ordered CDB input windows")
    for index, pattern in enumerate(EXPECTED_SEQUENCE_PATTERNS, start=1):
        sequence = windows[index][0]
        require(re.fullmatch(pattern, sequence, flags=re.IGNORECASE), f"input window {index} had unexpected sequence: {sequence}")

    f1 = window_summary(*windows[1])
    o = window_summary(*windows[2])
    q = window_summary(*windows[3])
    f2 = window_summary(*windows[4])

    f_key_values = set(f1["getKeyOnceArgs"]) | set(f1["coreKeys"]) | set(f1["consumeKeys"])
    q_key_values = set(q["getKeyOnceArgs"]) | set(q["coreKeys"]) | set(q["consumeKeys"])
    require({"00000046", "00000021"} & f_key_values or f1["sendButtonActionCount"] > 0, "first F window did not show live key/dispatch observer activity")
    require({"00000051", "00000010"} & q_key_values or q["sendButtonActionCount"] > 0, "Q window did not show live key/dispatch observer activity")
    require(f2["sendButtonActionCount"] > 0 or f2["getKeyOnceCount"] > 0, "second F window did not show live observer activity")

    summary.update(
        {
            "schema": "winui-safe-copy-free-camera-key-census-diagnostic.v1",
            "artifact": str(path),
            "cdbLog": str(log_path),
            "firstFWindow": f1,
            "oWindow": o,
            "qWindow": q,
            "secondFWindow": f2,
            "oWindowClassification": classify_o_window(o),
            "claim": "safe-copy CDB key census captured bounded F/O/Q input-window evidence with adjacent live observer controls",
            "claimBoundary": (
                "Diagnostic only. This does not prove O pauses, free-camera pause safety, control feel, "
                "gameplay safety, online networking, rebuild parity, or no-noticeable-difference parity."
            ),
        }
    )
    return summary


def make_artifact(
    root: Path,
    *,
    missing_f: bool = False,
    missing_o_window: bool = False,
    o_polling_without_o_query: bool = False,
) -> Path:
    log_path = root / "windbg.log"
    f1 = "" if missing_f else (
        "FreeCameraKeyCensus__GetKeyOnce controller=03d4c6b0 arg4=00000046 arg8=00000000 gamePause=0\n"
        "FreeCameraKeyCensus__KeyBytes onceVkO=00 onceScanO=00 onceVkF=01 onceScanF=00 onceVkQ=00 onceScanQ=00 onVkO=00 onScanO=00 onVkF=01 onScanF=00 onVkQ=00 onScanQ=00 state3VkO=00 state3ScanO=00 state3VkF=00 state3ScanF=00 state3VkQ=00 state3ScanQ=00\n"
        "FreeCameraKeyCensus__GetKeyOnceCore input=00855bb0 key=00000046 onceByteBefore=01 gamePause=0\n"
        "FreeCameraKeyCensus__SendButtonAction controller=03d4c6b0 button=1 rawButton=00000001 analogRaw=3f800000 gamePause=0\n"
    )
    o = (
        "FreeCameraKeyCensus__GetKeyOnce controller=03d4c6b0 arg4=00000021 arg8=00000000 gamePause=0\n"
        "FreeCameraKeyCensus__KeyBytes onceVkO=00 onceScanO=01 onceVkF=00 onceScanF=00 onceVkQ=00 onceScanQ=00 onVkO=00 onScanO=00 onVkF=00 onScanF=00 onVkQ=00 onScanQ=00 state3VkO=00 state3ScanO=00 state3VkF=00 state3ScanF=00 state3VkQ=00 state3ScanQ=00\n"
        "FreeCameraKeyCensus__GetKeyOnceCore input=00855bb0 key=00000021 onceByteBefore=01 gamePause=0\n"
        "FreeCameraKeyCensus__SendButtonAction controller=03d4c6b0 button=25 rawButton=00000019 analogRaw=bf800000 gamePause=0\n"
    ) if o_polling_without_o_query else ""
    q = (
        "FreeCameraKeyCensus__GetKeyOnce controller=03d4c6b0 arg4=00000051 arg8=00000000 gamePause=0\n"
        "FreeCameraKeyCensus__KeyBytes onceVkO=00 onceScanO=00 onceVkF=00 onceScanF=00 onceVkQ=01 onceScanQ=00 onVkO=00 onScanO=00 onVkF=00 onScanF=00 onVkQ=01 onScanQ=00 state3VkO=00 state3ScanO=00 state3VkF=00 state3ScanF=00 state3VkQ=00 state3ScanQ=00\n"
        "FreeCameraKeyCensus__GetKeyOnceCore input=00855bb0 key=00000051 onceByteBefore=01 gamePause=0\n"
        "FreeCameraKeyCensus__SendButtonAction controller=03d4c6b0 button=31 rawButton=0000001f analogRaw=bf800000 gamePause=0\n"
        "FreeCameraKeyCensus__CameraReceive targetIController=03d8d914 camera=03d8d910 button=31 rawButton=0000001f analogRaw=bf800000 gamePause=0\n"
    )
    f2 = (
        "FreeCameraKeyCensus__GetKeyOnce controller=03d4c6b0 arg4=00000046 arg8=00000000 gamePause=0\n"
        "FreeCameraKeyCensus__SendButtonAction controller=03d4c6b0 button=1 rawButton=00000001 analogRaw=3f800000 gamePause=0\n"
    )
    chunks = [f1, o, q, f2]
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
            "patchKeys": sorted(BASE_PATCH_KEYS | REQUIRED_PATCH_KEYS),
            "controlOptions": {
                "requestedControllerConfig": 2,
                "requestedConfig2CensusRowQe": "movement-forward",
            },
        },
        "launch": {"observedAlive": True},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "inputSummary": {
            "inputSequencesSent": 4 if not missing_o_window else 3,
            "focusedInputSequences": 4 if not missing_o_window else 3,
            "inputWindowMessageEventsSent": 0,
        },
        "captures": [{"status": "captured", "fileSize": 1024, "visualProof": True}],
        "inputCdbWindows": [
            {"index": 1, "sequence": "tap:F,wait:1000", "logStartByte": offsets[0][0], "logEndByte": offsets[0][1]},
            *([] if missing_o_window else [{"index": 2, "sequence": "down:O,wait:1000,up:O", "logStartByte": offsets[1][0], "logEndByte": offsets[1][1]}]),
            {"index": 3 if not missing_o_window else 2, "sequence": "down:Q,wait:1000,up:Q", "logStartByte": offsets[2][0], "logEndByte": offsets[2][1]},
            {"index": 4 if not missing_o_window else 3, "sequence": "tap:F,wait:1000", "logStartByte": offsets[3][0], "logEndByte": offsets[3][1]},
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
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(make_artifact(Path(temp_dir)))
        require(summary["oWindowClassification"] == "no-o-cdb-window-activity", "self-test expected silent O-window classification")

    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(make_artifact(Path(temp_dir), o_polling_without_o_query=True))
        require(
            summary["oWindowClassification"] == "o-key-state-latched-without-o-query",
            "self-test expected O scancode latch without O-key query classification",
        )

    for label, kwargs in (
        ("missing F observer evidence should fail", {"missing_f": True}),
        ("missing O window should fail", {"missing_o_window": True}),
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                validate_artifact(make_artifact(Path(temp_dir), **kwargs))
            except ArtifactError:
                pass
            else:
                raise ArtifactError(label)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive")
        if args.self_test:
            self_test()
            print("WinUI safe-copy free-camera key-census artifact checker self-test: PASS")
            return 0
        require(args.artifact is not None, "artifact is required unless --self-test is used")
        print(json.dumps(validate_artifact(args.artifact, args.min_capture_count), indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy free-camera key-census artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
