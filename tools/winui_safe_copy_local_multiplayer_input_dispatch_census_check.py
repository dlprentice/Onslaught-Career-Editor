#!/usr/bin/env python3
"""Summarize a CDB-backed local-multiplayer input-dispatch census artifact."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
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


def sequence_windows_from_artifact(artifact: dict[str, Any], log_path: Path) -> dict[int, tuple[str, int, str]]:
    rows = list_at(artifact, "inputCdbWindows")
    data = log_path.read_bytes()
    windows: dict[int, tuple[str, int, str]] = {}
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
        window_bytes = data[start:end]
        windows[index] = (sequence, len(window_bytes), window_bytes.decode("utf-8", errors="replace"))
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
                "inputDevice": int(match.group(5), 16),
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


def count_by(values: list[str | int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def summarize_window(index: int, sequence: str, byte_length: int, text: str, expected_controller_configuration: int) -> dict[str, Any]:
    sends = send_rows(text)
    receives = receive_rows(text)
    sends31 = [row for row in sends if int(row["button"]) == 31]
    receives31 = [row for row in receives if int(row["button"]) == 31]
    send_configs = sorted({int(row["controllerConfig"]) for row in sends})
    require(
        not send_configs or send_configs == [expected_controller_configuration],
        f"input window {index} controller config rows were {send_configs}, expected {expected_controller_configuration}",
    )
    return {
        "index": index,
        "sequence": sequence,
        "cdbByteLength": byte_length,
        "cdbAdvanced": byte_length > 0,
        "sendRows": len(sends),
        "receiveRows": len(receives),
        "sendButtons": sorted({int(row["button"]) for row in sends}),
        "receiveButtons": sorted({int(row["button"]) for row in receives}),
        "sendControllerConfigurations": send_configs,
        "sendInputDevices": sorted({int(row["inputDevice"]) for row in sends}),
        "sendControllers": sorted({str(row["controller"]) for row in sends if nonzero_hex(str(row["controller"]))}),
        "sendTargets": sorted({str(row["target"]) for row in sends if nonzero_hex(str(row["target"]))}),
        "receivePlayers": sorted({str(row["player"]) for row in receives if nonzero_hex(str(row["player"]))}),
        "receiveFromControllers": sorted({str(row["fromController"]) for row in receives if nonzero_hex(str(row["fromController"]))}),
        "receiveGameP0s": sorted({str(row["gameP0"]) for row in receives if nonzero_hex(str(row["gameP0"]))}),
        "receiveGameP1s": sorted({str(row["gameP1"]) for row in receives if nonzero_hex(str(row["gameP1"]))}),
        "sendButtonCounts": count_by([int(row["button"]) for row in sends]),
        "receiveButtonCounts": count_by([int(row["button"]) for row in receives]),
        "sendButton31InputDeviceCounts": count_by([int(row["inputDevice"]) for row in sends31]),
        "sendButton31ControllerCounts": count_by([str(row["controller"]) for row in sends31 if nonzero_hex(str(row["controller"]))]),
        "sendButton31TargetCounts": count_by([str(row["target"]) for row in sends31 if nonzero_hex(str(row["target"]))]),
        "receiveButton31PlayerCounts": count_by([str(row["player"]) for row in receives31 if nonzero_hex(str(row["player"]))]),
        "receiveButton31FromControllerCounts": count_by([str(row["fromController"]) for row in receives31 if nonzero_hex(str(row["fromController"]))]),
        "sendControllerCounts": count_by([str(row["controller"]) for row in sends if nonzero_hex(str(row["controller"]))]),
        "sendInputDeviceCounts": count_by([int(row["inputDevice"]) for row in sends]),
        "sendTargetCounts": count_by([str(row["target"]) for row in sends if nonzero_hex(str(row["target"]))]),
        "receivePlayerCounts": count_by([str(row["player"]) for row in receives if nonzero_hex(str(row["player"]))]),
        "receiveFromControllerCounts": count_by([str(row["fromController"]) for row in receives if nonzero_hex(str(row["fromController"]))]),
    }


def require_config2_forward_qe_button31_isolation(
    *,
    control_options: dict[str, Any],
    summaries: list[dict[str, Any]],
    p0: str,
    p1: str,
    expected_controller_configuration: int,
) -> dict[str, Any]:
    require(expected_controller_configuration == 2, "config-2 forward Q/E isolation proof requires controller configuration 2")
    require(
        control_options.get("requestedConfig2CensusRowQe") == "movement-forward",
        "expected copied-options config-2 movement-forward Q/E census row",
    )
    require(
        control_options.get("proofLever") == "copied-defaultoptions-config2-census-movement-forward-qe",
        "expected movement-forward Q/E copied-options proof lever",
    )
    require(len(summaries) >= 2, "config-2 forward Q/E isolation proof expects at least two input windows")

    def target_windows(key: str) -> list[dict[str, Any]]:
        pattern = re.compile(rf"(?:^|[,;\s])(?:down|tap):{re.escape(key)}(?:$|[,;\s])", re.IGNORECASE)
        return [summary for summary in summaries if pattern.search(str(summary["sequence"]))]

    q_windows = target_windows("Q")
    e_windows = target_windows("E")
    require(len(q_windows) == 1, "config-2 forward Q/E isolation proof expects exactly one Q input window")
    require(len(e_windows) == 1, "config-2 forward Q/E isolation proof expects exactly one E input window")
    require(q_windows[0]["index"] != e_windows[0]["index"], "config-2 forward Q/E isolation proof expects distinct Q and E input windows")

    checks = [
        (q_windows[0], "Q", 0, p0),
        (e_windows[0], "E", 1, p1),
    ]
    proof_windows: list[dict[str, Any]] = []
    for summary, key, expected_input_device, expected_player in checks:
        sequence = str(summary["sequence"])
        require(key in sequence, f"input window {summary['index']} does not contain expected {key} sequence")
        require(
            summary["sendButtonCounts"].get("31", 0) > 0,
            f"input window {summary['index']} did not send button 31",
        )
        require(
            summary["receiveButtonCounts"].get("31", 0) > 0,
            f"input window {summary['index']} did not receive button 31",
        )
        require(
            summary["sendButton31InputDeviceCounts"] == {str(expected_input_device): summary["sendButtonCounts"]["31"]},
            f"input window {summary['index']} button 31 was not isolated to input device {expected_input_device}",
        )
        receive_players = summary["receiveButton31PlayerCounts"]
        require(
            receive_players == {expected_player: summary["receiveButtonCounts"]["31"]},
            f"input window {summary['index']} button 31 did not route only to expected player {expected_player}",
        )
        require(
            len(summary["sendButton31ControllerCounts"]) == 1 and len(summary["receiveButton31FromControllerCounts"]) == 1,
            f"input window {summary['index']} button 31 did not isolate to one send/receive controller",
        )
        send_controller = next(iter(summary["sendButton31ControllerCounts"]))
        receive_controller = next(iter(summary["receiveButton31FromControllerCounts"]))
        require(
            send_controller == receive_controller,
            f"input window {summary['index']} button 31 send/receive controller mismatch",
        )
        proof_windows.append(
            {
                "index": summary["index"],
                "sequence": sequence,
                "button31SendRows": summary["sendButtonCounts"]["31"],
                "button31ReceiveRows": summary["receiveButtonCounts"]["31"],
                "inputDevice": expected_input_device,
                "player": expected_player,
                "controller": send_controller,
            }
        )

    target_indices = {int(row["index"]) for row in proof_windows}
    for summary in summaries:
        if int(summary["index"]) in target_indices:
            continue
        require(
            summary["sendButtonCounts"].get("31", 0) == 0 and summary["receiveButtonCounts"].get("31", 0) == 0,
            f"non-target input window {summary['index']} contained button-31 rows",
        )

    require(
        proof_windows[0]["controller"] != proof_windows[1]["controller"],
        "config-2 forward Q/E isolation proof expects distinct Q and E controllers",
    )

    return {
        "claim": "config-2 movement-forward Q/E button-31 dispatch isolation",
        "proofLever": control_options.get("proofLever"),
        "windows": proof_windows,
        "claimBoundary": "This proves scoped copied-profile keyboard input dispatch for button 31 reaches distinct local-multiplayer player/controller routes under controller configuration 2. It does not prove improved control feel, movement distance, online networking, or rebuild parity.",
    }


def validate_artifact(
    path: Path,
    min_capture_count: int,
    expected_controller_configuration: int,
    require_config2_forward_qe_isolation: bool = False,
) -> dict[str, Any]:
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
    require(len(windows) == sequence_count, "inputCdbWindows count does not match inputSequencesSent")
    summaries = [
        summarize_window(index, sequence, byte_length, text, expected_controller_configuration)
        for index, (sequence, byte_length, text) in sorted(windows.items())
    ]
    strict_isolation = (
        require_config2_forward_qe_button31_isolation(
            control_options=control_options,
            summaries=summaries,
            p0=p0,
            p1=p1,
            expected_controller_configuration=expected_controller_configuration,
        )
        if require_config2_forward_qe_isolation
        else None
    )

    summary = {
        "artifact": str(path),
        "claim": "diagnostic copied-profile level-850 input-dispatch census only",
        "controllerConfiguration": expected_controller_configuration,
        "launchArguments": expected_args(expected_controller_configuration),
        "captureCount": len(captures),
        "visualCaptureCount": visual_count,
        "p0": p0,
        "p1": p1,
        "windows": summaries,
        "windowsWithSendRows": sum(1 for window in summaries if window["sendRows"] > 0),
        "windowsWithoutSendRows": sum(1 for window in summaries if window["sendRows"] == 0),
        "claimBoundary": "This summarizes CDB dispatch rows around scoped keyboard inputs. Empty windows are recorded as candidates with no observed dispatch, not as proof failures. This is not P1/P2 isolation proof or movement-causality proof.",
    }
    if strict_isolation is not None:
        summary["strictConfig2ForwardQeIsolation"] = strict_isolation
    return summary


def make_artifact(
    root: Path,
    *,
    controller_configuration: int = 2,
    wrong_config_row: bool = False,
    malformed_offset: bool = False,
    background_message: bool = False,
    config2_forward_qe_isolation: bool = False,
    wrong_isolation_player: bool = False,
    extra_wait_windows: bool = False,
    wait_window_button31: bool = False,
) -> Path:
    log_path = root / "windbg.log"
    prelude = (
        "CGame__Render this=008a9a98 numRenders=0 players=2 level=850 fullscreenMP=0 horizSplit=1 "
        "p0=04646090 p1=0465d890 cam0=046d97f0 cam1=046d98a0 world=038c0840 "
    )
    if config2_forward_qe_isolation:
        first_window = (
            f"CController__SendButtonAction controller=11110000 button=31 rawButton=0000001f analogRaw=00000000 inputDevice=00000000 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=04646090 "
            "CPlayer__ReceiveButtonAction player=04646090 fromController=11110000 button=31 rawButton=0000001f analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
        )
    else:
        first_window = ""
    row_config = 3 if wrong_config_row else controller_configuration
    if config2_forward_qe_isolation:
        second_player = "04646090" if wrong_isolation_player else "0465d890"
        second_window = (
            f"CController__SendButtonAction controller=22220000 button=31 rawButton=0000001f analogRaw=00000000 inputDevice=00000001 controllerConfig={row_config:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=0465d890 "
            f"CPlayer__ReceiveButtonAction player={second_player} fromController=22220000 button=31 rawButton=0000001f analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
        )
    else:
        second_window = (
            f"CController__SendButtonAction controller=22220000 button=38 rawButton=00000026 analogRaw=00000000 inputDevice=00000001 controllerConfig={row_config:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=0465d890 "
            "CPlayer__ReceiveButtonAction player=0465d890 fromController=22220000 button=38 rawButton=00000026 analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
        )
    wait_button = 31 if wait_window_button31 else 25
    wait_raw_button = "0000001f" if wait_window_button31 else "00000019"
    wait_window = (
        f"CController__SendButtonAction controller=11110000 button={wait_button} rawButton={wait_raw_button} analogRaw=00000000 inputDevice=00000000 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=04646090 "
        f"CPlayer__ReceiveButtonAction player=04646090 fromController=11110000 button={wait_button} rawButton={wait_raw_button} analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
    )
    window_specs = (
        [
            ("wait:300", wait_window),
            ("down:Q,wait:500,up:Q", first_window),
            ("wait:300", wait_window),
            ("down:E,wait:500,up:E", second_window),
        ]
        if extra_wait_windows
        else [
            ("down:Q,wait:250,up:Q", first_window),
            ("down:E,wait:250,up:E", second_window),
        ]
    )
    cursor = len(prelude.encode("utf-8"))
    input_windows = []
    log_chunks = [prelude]
    for index, (sequence, chunk) in enumerate(window_specs, start=1):
        start = cursor
        cursor += len(chunk.encode("utf-8"))
        end = cursor
        input_windows.append({"index": index, "sequence": sequence, "logStartByte": start, "logEndByte": end})
        log_chunks.append(chunk)
    if malformed_offset:
        input_windows[0]["logEndByte"] = cursor + 100
    log_path.write_text("".join(log_chunks), encoding="utf-8")
    artifact = {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {
            "controlOptions": {
                "requestedPersistedControllerConfig": True,
                "requestedControllerConfig": controller_configuration,
                "requestedConfig2CensusRowQe": "movement-forward" if config2_forward_qe_isolation else None,
                "proofLever": "copied-defaultoptions-config2-census-movement-forward-qe" if config2_forward_qe_isolation else None,
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
            "inputSequencesSent": len(window_specs),
            "focusedInputSequences": len(window_specs),
            "inputWindowMessageEventsSent": 1 if background_message else 0,
        },
        "inputCdbWindows": input_windows,
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
        summary = validate_artifact(make_artifact(Path(tmp)), min_capture_count=1, expected_controller_configuration=2)
        require(summary["windows"][0]["sendRows"] == 0, "empty census window should be accepted and summarized")
        require(summary["windows"][1]["sendRows"] == 1, "populated census window should be summarized")
        require(summary["windows"][1]["sendButtonCounts"] == {"38": 1}, "populated census window should include grouped send button counts")
        require(summary["windows"][1]["receivePlayerCounts"] == {"0465d890": 1}, "populated census window should include grouped receive player counts")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(make_artifact(Path(tmp), wrong_config_row=True), min_capture_count=1, expected_controller_configuration=2)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("wrong controller-config rows should fail")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(make_artifact(Path(tmp), controller_configuration=3), min_capture_count=1, expected_controller_configuration=2)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("wrong launch/options config should fail")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(make_artifact(Path(tmp), malformed_offset=True), min_capture_count=1, expected_controller_configuration=2)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("malformed CDB byte offset fixture should fail")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(make_artifact(Path(tmp), background_message=True), min_capture_count=1, expected_controller_configuration=2)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("background window-message fixture should fail")

    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_artifact(
            make_artifact(Path(tmp), config2_forward_qe_isolation=True),
            min_capture_count=1,
            expected_controller_configuration=2,
            require_config2_forward_qe_isolation=True,
        )
        strict = summary.get("strictConfig2ForwardQeIsolation")
        require(isinstance(strict, dict), "strict isolation summary missing")
        require(strict["windows"][0]["player"] == "04646090", "Q window should route button 31 to P0")
        require(strict["windows"][1]["player"] == "0465d890", "E window should route button 31 to P1")

    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_artifact(
            make_artifact(Path(tmp), config2_forward_qe_isolation=True, extra_wait_windows=True),
            min_capture_count=1,
            expected_controller_configuration=2,
            require_config2_forward_qe_isolation=True,
        )
        strict = summary.get("strictConfig2ForwardQeIsolation")
        require(isinstance(strict, dict), "strict isolation summary missing for wait/input fixture")
        require(strict["windows"][0]["sequence"].startswith("down:Q"), "wait/input fixture should choose Q target window")
        require(strict["windows"][1]["sequence"].startswith("down:E"), "wait/input fixture should choose E target window")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(
                make_artifact(Path(tmp), config2_forward_qe_isolation=True, wrong_isolation_player=True),
                min_capture_count=1,
                expected_controller_configuration=2,
                require_config2_forward_qe_isolation=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("wrong button-31 player route should fail strict isolation")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(
                make_artifact(
                    Path(tmp),
                    config2_forward_qe_isolation=True,
                    extra_wait_windows=True,
                    wait_window_button31=True,
                ),
                min_capture_count=1,
                expected_controller_configuration=2,
                require_config2_forward_qe_isolation=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("non-target wait-window button-31 rows should fail strict isolation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--require-config2-forward-qe-isolation", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer input-dispatch census checker self-test: PASS")
        return 0
    if args.artifact is None:
        raise SystemExit("artifact is required unless --self-test is used")
    summary = validate_artifact(
        args.artifact,
        args.min_capture_count,
        args.expected_controller_configuration,
        require_config2_forward_qe_isolation=args.require_config2_forward_qe_isolation,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ArtifactError as exc:
        print(f"WinUI safe-copy local multiplayer input-dispatch census check: FAIL: {exc}")
        raise SystemExit(2)
