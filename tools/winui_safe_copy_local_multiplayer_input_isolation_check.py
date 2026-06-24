#!/usr/bin/env python3
"""Validate a CDB-backed copied-profile P1/P2 input-isolation artifact."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_BASE_ARGS = ["-skipfmv", "-level", "850", "-configuration"]
EXPECTED_COMMAND_FILE = "local-multiplayer-level850-input-isolation-observer.cdb.txt"
BUTTON_MECH_FORWARD = 31


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


def nonzero_hex(value: str | None) -> bool:
    if not value:
        return False
    try:
        return int(value, 16) != 0
    except ValueError:
        return False


def expected_args(controller_configuration: int) -> list[str]:
    return EXPECTED_BASE_ARGS + [str(controller_configuration)]


def hex_to_int(value: str) -> int:
    return int(value, 16)


def capture_has_visual_proof(item: dict[str, Any]) -> bool:
    if item.get("visualProof") is True:
        return True
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


def visual_capture_count(captures: list[Any]) -> int:
    return sum(1 for item in captures if isinstance(item, dict) and capture_has_visual_proof(item))


def all_regex(pattern: str, text: str) -> list[re.Match[str]]:
    return list(re.finditer(pattern, text, flags=re.IGNORECASE))


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
                "controllerConfig": match.group(6).lower(),
                "target": match.group(10).lower(),
            }
        )
    return rows


def validate_window(
    *,
    label: str,
    sequence: str,
    text: str,
    expected_key: str,
    expected_player: str,
    forbidden_player: str,
    expected_controller_configuration: int,
) -> dict[str, Any]:
    normalized_sequence = sequence.upper()
    require(expected_key.upper() in normalized_sequence, f"{label} marker sequence does not contain {expected_key}")

    sends = [row for row in send_rows(text) if row["button"] == BUTTON_MECH_FORWARD]
    receives = [row for row in receive_rows(text) if row["button"] == BUTTON_MECH_FORWARD]
    require(bool(sends), f"{label} window has no CController__SendButtonAction button 31 rows")
    require(bool(receives), f"{label} window has no CPlayer__ReceiveButtonAction button 31 rows")

    expected_hits = [row for row in receives if row["player"] == expected_player.lower()]
    forbidden_hits = [row for row in receives if row["player"] == forbidden_player.lower()]
    require(bool(expected_hits), f"{label} window did not dispatch button 31 to expected player")
    require(not forbidden_hits, f"{label} window cross-dispatched button 31 to the other player")

    controllers = sorted({str(row["fromController"]) for row in expected_hits if nonzero_hex(str(row["fromController"]))})
    require(bool(controllers), f"{label} window did not record a nonzero source controller")
    send_configs = sorted({hex_to_int(str(row["controllerConfig"])) for row in sends})
    require(send_configs == [expected_controller_configuration], f"{label} window controller config rows were {send_configs}, expected {expected_controller_configuration}")
    return {
        "sequence": sequence,
        "sendButton31Rows": len(sends),
        "receiveButton31Rows": len(receives),
        "expectedPlayerHits": len(expected_hits),
        "sourceControllers": controllers,
        "observedControllerConfigurations": send_configs,
    }


def validate_artifact(path: Path, min_capture_count: int, expected_controller_configuration: int = 1) -> dict[str, Any]:
    artifact = read_json(path)
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")
    require(1 <= expected_controller_configuration <= 4, "expected controller configuration must be 1..4")

    source = object_at(artifact, "source")
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe changed")
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe changed")
    require(object_at(source, "saveAndOptions").get("unchanged") is True, "source save/options changed")

    launch = object_at(artifact, "launch")
    require(
        launch.get("arguments") == expected_args(expected_controller_configuration),
        f"launch args are not -skipfmv -level 850 -configuration {expected_controller_configuration}",
    )
    launch_pid = int_at(launch, "processId")

    process_baseline = object_at(artifact, "processBaseline")
    require(process_baseline.get("noPreexistingBea") is True, "preexisting BEA process was present")
    require(process_baseline.get("noBeaAfterStop") is True, "BEA process remained after stop")
    require(object_at(artifact, "stop").get("Success") is True, "managed stop did not succeed")

    captures = list_at(artifact, "captures")
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}")
    visual_count = visual_capture_count(captures)
    require(visual_count > 0, "no foreground/occlusion-free visual capture")

    safe_copy = object_at(artifact, "safeCopy")
    control_options = object_at(safe_copy, "controlOptions")
    require(control_options.get("requestedInputIsolationForwardQe") is True, "input-isolation Q/E keybind materialization was not requested")
    require(control_options.get("proofLever") == "copied-defaultoptions-input-isolation-forward-qe", "unexpected control-options proof lever")
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
    require(int_at(input_summary, "inputKeyEventsSent") >= 4, "too few keyboard events sent")
    require(
        int_at(input_summary, "inputSendInputEventsSent", 0) + int_at(input_summary, "inputScanKeybdEventsSent", 0) >= 4,
        "focused SendInput/scan-code keyboard path was not used",
    )

    for index, item in enumerate(artifact.get("input") or [], start=1):
        require(isinstance(item, dict), f"input row {index} is not an object")
        require(item.get("status") == "sent", f"input row {index} was not sent")
        require(item.get("focused") is True, f"input row {index} was not focused")
        require(item.get("backgroundWindowMessagesAllowed") is False, f"input row {index} allowed background messages")
        require(item.get("windowMessageEventsSent") == 0, f"input row {index} used window messages")

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
        r"fullscreenMP=(\d+) horizSplit=(\d+) p0=([0-9a-fA-F]+) p1=([0-9a-fA-F]+) "
        r"cam0=([0-9a-fA-F]+) cam1=([0-9a-fA-F]+) world=([0-9a-fA-F]+)",
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

    set_num_viewpoints = re.search(r"CEngine__SetNumViewpoints engine=([0-9a-fA-F]+) requested=(\d+)", log_text, flags=re.IGNORECASE)
    require(set_num_viewpoints is not None and int(set_num_viewpoints.group(2)) == 2, "CEngine__SetNumViewpoints did not request 2")

    windows = sequence_windows_from_artifact(artifact, log_path)
    require(1 in windows and 2 in windows, "missing input sequence windows 1 and 2")
    q_summary = validate_window(
        label="P1/Q",
        sequence=windows[1][0],
        text=windows[1][1],
        expected_key="Q",
        expected_player=p0,
        forbidden_player=p1,
        expected_controller_configuration=expected_controller_configuration,
    )
    e_summary = validate_window(
        label="P2/E",
        sequence=windows[2][0],
        text=windows[2][1],
        expected_key="E",
        expected_player=p1,
        forbidden_player=p0,
        expected_controller_configuration=expected_controller_configuration,
    )
    require(set(q_summary["sourceControllers"]).isdisjoint(set(e_summary["sourceControllers"])), "P1/P2 source controller sets were not distinct")

    return {
        "artifact": str(path),
        "launchArguments": expected_args(expected_controller_configuration),
        "controllerConfiguration": expected_controller_configuration,
        "captureCount": len(captures),
        "visualCaptureCount": visual_count,
        "p0": p0,
        "p1": p1,
        "qWindow": q_summary,
        "eWindow": e_summary,
        "claim": "one copied-profile level-850 P1/P2 input-isolation observer proof",
    }


def make_artifact(root: Path, _log_text: str, *, controller_configuration: int = 1, cross_dispatch: bool = False, one_player_only: bool = False) -> Path:
    log_path = root / "windbg.log"
    prelude = (
        "noise CGame__Render this=008a9a98 numRenders=0 players=2 level=850 fullscreenMP=0 horizSplit=1 "
        "p0=04646090 p1=0465d890 cam0=046d97f0 cam1=046d98a0 world=038c0840 "
        "CEngine__SetNumViewpoints engine=0089c9a0 requested=2 esp8=008a9a98 "
    )
    q_window = (
        f"CController__SendButtonAction controller=11110000 button=31 rawButton=0000001f analogRaw=00000000 inputDevice=00000000 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=04646090 "
        "CPlayer__ReceiveButtonAction player=04646090 fromController=11110000 button=31 rawButton=0000001f analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
    )
    if cross_dispatch:
        q_window += "CPlayer__ReceiveButtonAction player=0465d890 fromController=11110000 button=31 rawButton=0000001f analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
    e_window = "" if one_player_only else (
        f"CController__SendButtonAction controller=22220000 button=31 rawButton=0000001f analogRaw=00000000 inputDevice=00000001 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target=0465d890 "
        "CPlayer__ReceiveButtonAction player=0465d890 fromController=22220000 button=31 rawButton=0000001f analogRaw=00000000 gameP0=04646090 gameP1=0465d890 "
    )
    log_text = prelude + q_window + e_window
    prelude_end = len(prelude.encode("utf-8"))
    q_end = prelude_end + len(q_window.encode("utf-8"))
    e_end = q_end + len(e_window.encode("utf-8"))
    log_path.write_text(log_text, encoding="utf-8")
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
                "proofLever": "copied-defaultoptions-input-isolation-forward-qe",
            }
        },
        "launch": {
            "processId": 1234,
            "arguments": expected_args(controller_configuration),
        },
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "captures": [{"visualProof": True}],
        "inputPlan": {"allowBackgroundWindowMessages": False},
        "inputSummary": {
            "inputSequencesSent": 2,
            "focusedInputSequences": 2,
            "inputActionCount": 2,
            "inputKeyEventsSent": 4,
            "inputSendInputEventsSent": 4,
            "inputScanKeybdEventsSent": 0,
            "inputWindowMessageEventsSent": 0,
            "inputMouseEventsSent": 0,
        },
        "input": [
            {"status": "sent", "focused": True, "backgroundWindowMessagesAllowed": False, "windowMessageEventsSent": 0},
            {"status": "sent", "focused": True, "backgroundWindowMessagesAllowed": False, "windowMessageEventsSent": 0},
        ],
        "inputCdbWindows": [
            {"index": 1, "sequence": "tap:Q", "logPath": str(log_path), "logStartByte": prelude_end, "logEndByte": q_end},
            {"index": 2, "sequence": "tap:E", "logPath": str(log_path), "logStartByte": q_end, "logEndByte": e_end},
        ],
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path), "targetProcessId": 1234},
            "cleanup": {"status": "stopped"},
        },
    }
    artifact_path = root / "artifact.json"
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
    return artifact_path


def good_log() -> str:
    return "legacy fixture placeholder; make_artifact builds byte-window fixtures directly"


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        validate_artifact(make_artifact(root, good_log()), min_capture_count=1)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        validate_artifact(make_artifact(root, good_log(), controller_configuration=4), min_capture_count=1, expected_controller_configuration=4)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            validate_artifact(make_artifact(root, good_log(), controller_configuration=4), min_capture_count=1, expected_controller_configuration=1)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("wrong-controller-config fixture should fail")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            validate_artifact(make_artifact(root, good_log(), cross_dispatch=True), min_capture_count=1)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("cross-dispatch fixture should fail")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            validate_artifact(make_artifact(root, good_log(), one_player_only=True), min_capture_count=1)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("one-player-only fixture should fail")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        artifact_path = make_artifact(root, good_log())
        artifact = read_json(artifact_path)
        artifact["inputSummary"]["inputWindowMessageEventsSent"] = 2
        artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
        try:
            validate_artifact(artifact_path, min_capture_count=1)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("window-message fixture should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer input-isolation checker self-test: PASS")
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
        print(f"WinUI safe-copy local multiplayer input-isolation check: FAIL: {exc}")
        raise SystemExit(2)
