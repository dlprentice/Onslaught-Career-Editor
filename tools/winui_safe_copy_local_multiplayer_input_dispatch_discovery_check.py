#!/usr/bin/env python3
"""Validate a diagnostic CDB artifact for local-multiplayer input dispatch discovery."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "local-multiplayer-level850-input-dispatch-discovery-observer.cdb.txt"
EXPECTED_BASE_ARGS = ["-skipfmv", "-level", "850", "-configuration"]


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def expected_args(controller_configuration: int) -> list[str]:
    return EXPECTED_BASE_ARGS + [str(controller_configuration)]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "artifact must be a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def int_at(value: dict[str, Any], key: str, default: int | None = None) -> int:
    child = value.get(key)
    if isinstance(child, int):
        return child
    require(default is not None, f"missing integer: {key}")
    return default


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def all_regex(pattern: str, text: str) -> list[re.Match[str]]:
    return list(re.finditer(pattern, text, flags=re.IGNORECASE))


def nonzero_hex(value: str | None) -> bool:
    if not value:
        return False
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


def sequence_windows_from_artifact(artifact: dict[str, Any], log_path: Path) -> dict[int, tuple[str, str]]:
    rows = list_at(artifact, "inputCdbWindows")
    data = log_path.read_bytes()
    windows: dict[int, tuple[str, str]] = {}
    for row in rows:
        require(isinstance(row, dict), "inputCdbWindows row is not an object")
        index = row.get("index")
        sequence = row.get("sequence")
        start = row.get("logStartByte")
        end = row.get("logEndByte")
        require(isinstance(index, int) and index > 0, "inputCdbWindows row has invalid index")
        require(isinstance(sequence, str) and sequence, f"inputCdbWindows row {index} has invalid sequence")
        require(isinstance(start, int) and isinstance(end, int), f"inputCdbWindows row {index} is missing byte offsets")
        require(0 <= start <= end <= len(data), f"inputCdbWindows row {index} byte offsets are out of range")
        require(end > start, f"inputCdbWindows row {index} did not advance the CDB log")
        windows[index] = (sequence, data[start:end].decode("utf-8", errors="replace"))
    return windows


def send_rows(window_text: str) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    pattern = (
        r"CController__SendButtonAction controller=([0-9a-fA-F]+) button=(\d+) rawButton=([0-9a-fA-F]+) "
        r"analogRaw=([0-9a-fA-F]+) inputDevice=([0-9a-fA-F]+) controllerConfig=([0-9a-fA-F]+) "
        r"buttons0=([0-9a-fA-F]+) buttons1=([0-9a-fA-F]+) buttons2=([0-9a-fA-F]+) target=([0-9a-fA-F]+)"
    )
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "controller": match.group(1).lower(),
                "button": int(match.group(2)),
                "rawButton": match.group(3).lower(),
                "analogRaw": match.group(4).lower(),
                "inputDevice": match.group(5).lower(),
                "controllerConfig": int(match.group(6), 16),
                "target": match.group(10).lower(),
            }
        )
    return rows


def receive_rows(window_text: str) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    pattern = (
        r"CPlayer__ReceiveButtonAction player=([0-9a-fA-F]+) fromController=([0-9a-fA-F]+) "
        r"button=(\d+) rawButton=([0-9a-fA-F]+) analogRaw=([0-9a-fA-F]+) "
        r"gameP0=([0-9a-fA-F]+) gameP1=([0-9a-fA-F]+)"
    )
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "player": match.group(1).lower(),
                "fromController": match.group(2).lower(),
                "button": int(match.group(3)),
                "rawButton": match.group(4).lower(),
                "analogRaw": match.group(5).lower(),
                "gameP0": match.group(6).lower(),
                "gameP1": match.group(7).lower(),
            }
        )
    return rows


def summarize_window(index: int, sequence: str, text: str, expected_controller_configuration: int) -> dict[str, Any]:
    sends = send_rows(text)
    receives = receive_rows(text)
    require(sends, f"input window {index} has no CController__SendButtonAction rows")
    send_configs = sorted({int(row["controllerConfig"]) for row in sends})
    require(send_configs == [expected_controller_configuration], f"input window {index} controller config rows were {send_configs}, expected {expected_controller_configuration}")
    buttons = sorted({int(row["button"]) for row in sends})
    receive_buttons = sorted({int(row["button"]) for row in receives})
    receive_players = sorted({str(row["player"]) for row in receives if nonzero_hex(str(row["player"]))})
    send_controllers = sorted({str(row["controller"]) for row in sends if nonzero_hex(str(row["controller"]))})
    return {
        "index": index,
        "sequence": sequence,
        "sendRows": len(sends),
        "receiveRows": len(receives),
        "sendButtons": buttons,
        "receiveButtons": receive_buttons,
        "sendControllerConfigurations": send_configs,
        "sendControllers": send_controllers,
        "receivePlayers": receive_players,
    }


def validate_artifact(path: Path, min_capture_count: int, expected_controller_configuration: int) -> dict[str, Any]:
    artifact = read_json(path)
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")
    require(1 <= expected_controller_configuration <= 4, "expected controller configuration must be 1..4")

    source = object_at(artifact, "source")
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe changed")
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe changed")
    require(object_at(source, "saveAndOptions").get("unchanged") is True, "source save/options changed")

    launch = object_at(artifact, "launch")
    require(launch.get("arguments") == expected_args(expected_controller_configuration), f"launch args are not -skipfmv -level 850 -configuration {expected_controller_configuration}")
    launch_pid = int_at(launch, "processId")

    process_baseline = object_at(artifact, "processBaseline")
    require(process_baseline.get("noPreexistingBea") is True, "preexisting BEA process was present")
    require(process_baseline.get("noBeaAfterStop") is True, "BEA process remained after stop")
    require(object_at(artifact, "stop").get("Success") is True, "managed stop did not succeed")

    captures = list_at(artifact, "captures")
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}")
    visual_count = visual_capture_count(captures)
    require(visual_count > 0, "no foreground/occlusion-free visual capture")

    control_options = object_at(object_at(artifact, "safeCopy"), "controlOptions")
    require(control_options.get("requestedInputIsolationForwardQe") is True, "input-isolation Q/E keybind materialization was not requested")
    require(control_options.get("requestedPersistedControllerConfig") is True, "persisted copied-options controller configuration was not requested")
    require(control_options.get("requestedControllerConfig") == expected_controller_configuration, "requested copied-options controller config mismatch")
    require(control_options.get("observedControllerConfigP1") == expected_controller_configuration, "observed P1 copied-options controller config mismatch")
    require(control_options.get("observedControllerConfigP2") == expected_controller_configuration, "observed P2 copied-options controller config mismatch")

    input_plan = object_at(artifact, "inputPlan")
    require(input_plan.get("allowBackgroundWindowMessages") is False, "background window messages were allowed")
    input_summary = object_at(artifact, "inputSummary")
    sequence_count = int_at(input_summary, "inputSequencesSent")
    require(sequence_count >= 2, "expected at least two input sequences")
    require(int_at(input_summary, "focusedInputSequences") == sequence_count, "not all input sequences were focused")
    require(int_at(input_summary, "inputWindowMessageEventsSent") == 0, "PostMessage/background input was used")

    observer = object_at(artifact, "cdbObserver")
    require(observer.get("enabled") is True, "CDB observer not enabled")
    require(str(observer.get("commandFile") or "").replace("\\", "/").endswith(EXPECTED_COMMAND_FILE), "wrong CDB command file")
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(result.get("logExists") is True, "CDB log was not created")
    require(result.get("targetProcessId") == launch_pid, "CDB target PID does not match launched process")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish")

    log_path = Path(str(result.get("logPath") or observer.get("logPath") or ""))
    require(log_path.is_file(), f"CDB log path is missing: {log_path}")
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    render = re.search(
        r"CGame__Render this=([0-9a-fA-F]+) numRenders=(\d+) players=(\d+) level=(\d+) "
        r"fullscreenMP=(\d+) horizSplit=(\d+) p0=([0-9a-fA-F]+) p1=([0-9a-fA-F]+)",
        log_text,
        flags=re.IGNORECASE,
    )
    require(render is not None, "missing CGame__Render observation")
    p0 = render.group(7).lower()
    p1 = render.group(8).lower()
    require(int(render.group(3)) == 2, "CGame__Render players was not 2")
    require(int(render.group(4)) == 850, "CGame__Render level was not 850")
    require(int(render.group(6)) == 1, "CGame__Render horizontal split flag was not 1")
    require(nonzero_hex(p0) and nonzero_hex(p1) and p0 != p1, "P0/P1 pointers were missing or not distinct")

    windows = sequence_windows_from_artifact(artifact, log_path)
    summaries = [
        summarize_window(index, sequence, text, expected_controller_configuration)
        for index, (sequence, text) in sorted(windows.items())
    ]

    return {
        "artifact": str(path),
        "claim": "diagnostic copied-profile level-850 input dispatch discovery only",
        "controllerConfiguration": expected_controller_configuration,
        "launchArguments": expected_args(expected_controller_configuration),
        "captureCount": len(captures),
        "visualCaptureCount": visual_count,
        "p0": p0,
        "p1": p1,
        "windows": summaries,
        "claimBoundary": "This identifies button/controller/player dispatch rows around scoped keyboard input. It is not P1/P2 forward-isolation proof unless a stricter checker verifies the expected action and no cross-dispatch.",
    }


def make_artifact(root: Path, *, controller_configuration: int = 2, empty_first_window: bool = False) -> Path:
    log_path = root / "windbg.log"
    prelude = (
        "CGame__Render this=008a9a98 numRenders=0 players=2 level=850 fullscreenMP=0 horizSplit=1 "
        "p0=04646090 p1=0465d890 cam0=046d97f0 cam1=046d98a0 world=038c0840 "
    )
    first_window = "" if empty_first_window else (
        f"CController__SendButtonAction controller=11110000 button=37 rawButton=00000025 analogRaw=00000000 inputDevice=00000000 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=04646090 "
        "CPlayer__ReceiveButtonAction player=04646090 fromController=11110000 button=37 rawButton=00000025 analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
    )
    second_window = (
        f"CController__SendButtonAction controller=22220000 button=38 rawButton=00000026 analogRaw=00000000 inputDevice=00000001 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=0465d890 "
        "CPlayer__ReceiveButtonAction player=0465d890 fromController=22220000 button=38 rawButton=00000026 analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
    )
    prelude_end = len(prelude.encode("utf-8"))
    first_end = prelude_end + len(first_window.encode("utf-8"))
    second_end = first_end + len(second_window.encode("utf-8"))
    log_path.write_text(prelude + first_window + second_window, encoding="utf-8")
    artifact = {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {
            "controlOptions": {
                "requestedInputIsolationForwardQe": True,
                "requestedPersistedControllerConfig": True,
                "requestedControllerConfig": controller_configuration,
                "observedControllerConfigP1": controller_configuration,
                "observedControllerConfigP2": controller_configuration,
            }
        },
        "launch": {"processId": 1234, "arguments": expected_args(controller_configuration)},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "captures": [{"visualProof": True}],
        "inputPlan": {"allowBackgroundWindowMessages": False},
        "inputSummary": {
            "inputSequencesSent": 2,
            "focusedInputSequences": 2,
            "inputWindowMessageEventsSent": 0,
        },
        "inputCdbWindows": [
            {"index": 1, "sequence": "tap:Q", "logStartByte": prelude_end, "logEndByte": first_end},
            {"index": 2, "sequence": "tap:E", "logStartByte": first_end, "logEndByte": second_end},
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
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        validate_artifact(make_artifact(root), min_capture_count=1, expected_controller_configuration=2)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            validate_artifact(make_artifact(root, empty_first_window=True), min_capture_count=1, expected_controller_configuration=2)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("empty first window should fail")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            validate_artifact(make_artifact(root, controller_configuration=3), min_capture_count=1, expected_controller_configuration=2)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("wrong config should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer input-dispatch discovery checker self-test: PASS")
        return 0
    if args.artifact is None:
        raise SystemExit("artifact is required unless --self-test is used")
    summary = validate_artifact(args.artifact, args.min_capture_count, args.expected_controller_configuration)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ArtifactError as exc:
        print(f"WinUI safe-copy local multiplayer input-dispatch discovery check: FAIL: {exc}")
        raise SystemExit(2)
