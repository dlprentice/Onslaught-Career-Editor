#!/usr/bin/env python3
"""Validate CDB-backed safe-copy free-camera toggle runtime artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "free-camera-toggle-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
FREE_CAMERA_PATCH_KEY = "free_camera_aurore_gate_bypass"
CLEAN_GATE_BYTES = "0f 84 58 02 00 00"
PATCHED_GATE_BYTES = "90 90 90 90 90 90"


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
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


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def string_list_at(value: Any, key: str) -> list[str]:
    values = list_at(value, key)
    require(all(isinstance(item, str) for item in values), f"{key} must contain only strings.")
    return [str(item) for item in values]


def normalize_gate_bytes(value: str) -> str:
    return " ".join(value.lower().split())


def visual_capture_count(captures: list[Any]) -> int:
    total = 0
    for item in captures:
        if not isinstance(item, dict):
            continue
        occlusion = item.get("occlusion")
        if item.get("visualProof") is True or item.get("foregroundMatchesTarget") is True:
            total += 1
        elif (
            isinstance(occlusion, dict)
            and occlusion.get("checked") is True
            and occlusion.get("targetFound") is True
            and occlusion.get("occlusionFree") is True
            and occlusion.get("occludingWindowCount") == 0
        ):
            total += 1
    return total


def extract_log_path(observer: dict[str, Any]) -> Path:
    result = object_at(observer, "result")
    candidate = result.get("logPath") or observer.get("logPath")
    require(isinstance(candidate, str) and candidate, "CDB log path is missing.")
    path = Path(candidate)
    require(path.is_file(), f"CDB log path is missing: {path}")
    return path


def runtime_log_text(payload: dict[str, Any]) -> str:
    observer = object_at(payload, "cdbObserver")
    require(bool_at(observer, "enabled"), "CDB observer not enabled.")
    command_file = string_at(observer, "commandFile").replace("/", "\\").lower()
    require(command_file.endswith(EXPECTED_COMMAND_FILE), "Unexpected CDB observer command file.")
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(result.get("status") == "attached", "CDB observer did not attach.")
    require(bool_at(result, "logExists"), "CDB log was not created.")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish.")
    return extract_log_path(observer).read_text(encoding="utf-8", errors="replace")


def regex_rows(pattern: str, text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in re.finditer(pattern, text, flags=re.IGNORECASE)]


RECEIVE_RE = (
    r"CGame__ReceiveButtonAction game=(?P<game>[0-9a-f]+) fromController=(?P<controller>[0-9a-f]+) "
    r"button=(?P<button>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+) "
    r"player0=(?P<player0>[0-9a-f]+) player1=(?P<player1>[0-9a-f]+) "
    r"cam0=(?P<cam0>[0-9a-f]+) cam1=(?P<cam1>[0-9a-f]+) "
    r"oldCam0=(?P<old_cam0>[0-9a-f]+) oldCam1=(?P<old_cam1>[0-9a-f]+)"
)

CASE_RE = (
    r"CGame__FreeCameraCase game=(?P<game>[0-9a-f]+) free0=(?P<free0>\d+) free1=(?P<free1>\d+) "
    r"gateBytes=(?P<gate_bytes>[0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2})"
)

GATE_RE = (
    r"CGame__FreeCameraGateSite game=(?P<game>[0-9a-f]+) eax=(?P<eax>[0-9a-f]+) al=(?P<al>[0-9a-f]+) "
    r"free0=(?P<free0>\d+) free1=(?P<free1>\d+) "
    r"gateBytes=(?P<gate_bytes>[0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2} [0-9a-f]{2})"
)

TOGGLE_RE = (
    r"CGame__ToggleFreeCameraOn game=(?P<game>[0-9a-f]+) player=(?P<player>\d+) "
    r"freeBefore0=(?P<free_before0>\d+) freeBefore1=(?P<free_before1>\d+) "
    r"player0=(?P<player0>[0-9a-f]+) player1=(?P<player1>[0-9a-f]+) "
    r"cam0=(?P<cam0>[0-9a-f]+) cam1=(?P<cam1>[0-9a-f]+) "
    r"oldCam0=(?P<old_cam0>[0-9a-f]+) oldCam1=(?P<old_cam1>[0-9a-f]+)"
)

SET_CAMERA_RE = (
    r"CGame__SetCurrentCamera game=(?P<game>[0-9a-f]+) player=(?P<player>\d+) camera=(?P<camera>[0-9a-f]+) "
    r"releaseOld=(?P<release_old>\d+) free0=(?P<free0>\d+) free1=(?P<free1>\d+) "
    r"cam0=(?P<cam0>[0-9a-f]+) cam1=(?P<cam1>[0-9a-f]+) "
    r"oldCam0=(?P<old_cam0>[0-9a-f]+) oldCam1=(?P<old_cam1>[0-9a-f]+)"
)


def common_validate(
    payload: dict[str, Any],
    *,
    expected_patch_present: bool,
    min_capture_count: int,
    min_input_actions: int,
) -> tuple[dict[str, Any], str]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "Safe copy did not apply required windowed compatibility patch keys.")
    if expected_patch_present:
        require(FREE_CAMERA_PATCH_KEY in patch_keys, f"Missing expected patch key: {FREE_CAMERA_PATCH_KEY}")
    else:
        require(FREE_CAMERA_PATCH_KEY not in patch_keys, "Baseline artifact unexpectedly includes the free-camera patch.")

    launch = object_at(payload, "launch")
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")
    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    require(bool_at(object_at(payload, "stop"), "Success"), "Managed copied-game stop did not succeed.")

    input_summary = object_at(payload, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") >= 1, "No scoped input sequence was reported sent.")
    require(int_at(input_summary, "inputActionCount") >= min_input_actions, "Scoped input action count is too low.")
    require(int_at(input_summary, "inputKeyEventsSent") >= 2, "Scoped key events were not reported.")
    for item in list_at(payload, "input"):
        require(isinstance(item, dict), "Each input result must be an object.")
        if item.get("status") == "sent":
            require(item.get("focused") is True, "Scoped input was not foreground focused.")

    captures = list_at(payload, "captures")
    require(len(captures) >= min_capture_count, f"Expected at least {min_capture_count} capture(s).")
    require(visual_capture_count(captures) >= min_capture_count, "Not enough visual captures.")
    for item in captures:
        require(isinstance(item, dict), "Each capture must be an object.")
        require(item.get("status") == "captured", "Each capture must have captured status.")
        require(int_at(item, "fileSize") > 0, "Capture file size must be positive.")

    boundary = string_at(payload, "claimBoundary")
    require("camera movement" in boundary and "rebuild parity" in boundary, "Claim boundary must keep movement/parity separate.")

    return {
        "patchKeys": sorted(patch_keys),
        "captureCount": len(captures),
        "visualCaptureCount": visual_capture_count(captures),
        "inputActionCount": int_at(input_summary, "inputActionCount"),
        "inputKeyEventsSent": int_at(input_summary, "inputKeyEventsSent"),
    }, runtime_log_text(payload)


def parse_rows(log_text: str) -> dict[str, list[dict[str, str]]]:
    return {
        "receive": [row for row in regex_rows(RECEIVE_RE, log_text) if row["button"] == "1"],
        "case": regex_rows(CASE_RE, log_text),
        "gate": regex_rows(GATE_RE, log_text),
        "toggle": regex_rows(TOGGLE_RE, log_text),
        "set_camera": regex_rows(SET_CAMERA_RE, log_text),
    }


def validate_positive(payload: dict[str, Any], *, min_capture_count: int) -> dict[str, Any]:
    summary, log_text = common_validate(
        payload,
        expected_patch_present=True,
        min_capture_count=min_capture_count,
        min_input_actions=3,
    )
    rows = parse_rows(log_text)
    receive = rows["receive"]
    cases = rows["case"]
    gates = rows["gate"]
    toggles = rows["toggle"]
    set_rows = rows["set_camera"]

    require(len(receive) >= 2, "Positive proof needs two BUTTON_TOGGLE_FREE_CAMERA receive rows.")
    require(receive[0]["free0"] == "0", "First free-camera receive row should start with free0=0.")
    require(any(row["free0"] == "1" for row in receive[1:]), "Second free-camera receive row did not observe free0=1.")
    require(len(cases) >= 2, "Positive proof needs two free-camera case rows.")
    require(all(normalize_gate_bytes(row["gate_bytes"]) == PATCHED_GATE_BYTES for row in cases), "Positive free-camera case did not show patched NOP bytes.")
    require(len(gates) >= 2, "Positive proof needs two gate-site rows.")
    require(all(normalize_gate_bytes(row["gate_bytes"]) == PATCHED_GATE_BYTES for row in gates), "Positive gate site did not show patched NOP bytes.")
    require(len(toggles) >= 1, "Positive proof did not hit CGame__ToggleFreeCameraOn.")
    require(any(row["player"] == "0" and row["free_before0"] == "0" for row in toggles), "Toggle-on row did not target player 0 from free0=0.")
    require(len(set_rows) >= 2, "Positive proof did not call CGame__SetCurrentCamera for on/off transitions.")

    first_receive = receive[0]
    second_receive = next(row for row in receive[1:] if row["free0"] == "1")
    on_set = next((row for row in set_rows if row["release_old"] == "0"), None)
    off_set = next((row for row in set_rows if row["release_old"] == "1"), None)
    require(on_set is not None, "Positive proof did not observe free-camera-on SetCurrentCamera releaseOld=0.")
    require(off_set is not None, "Positive proof did not observe free-camera-off SetCurrentCamera releaseOld=1.")
    require(on_set["old_cam0"].lower() == first_receive["cam0"].lower(), "Free-camera-on row did not preserve original cam0 into oldCam0.")
    require(on_set["camera"].lower() != first_receive["cam0"].lower(), "Free-camera-on camera pointer did not differ from the original camera.")
    require(second_receive["cam0"].lower() == on_set["camera"].lower(), "Second receive row did not observe the new free-camera pointer as cam0.")
    require(second_receive["old_cam0"].lower() == first_receive["cam0"].lower(), "Second receive row did not preserve oldCam0 as the original camera.")
    require(off_set["camera"].lower() == first_receive["cam0"].lower(), "Free-camera-off row did not restore the original camera pointer.")

    summary.update(
        {
            "schema": "winui-safe-copy-free-camera-toggle-proof.v1",
            "mode": "positive",
            "receiveButton1Count": len(receive),
            "freeCameraCaseCount": len(cases),
            "gateSiteCount": len(gates),
            "toggleOnCount": len(toggles),
            "setCurrentCameraCount": len(set_rows),
            "firstReceiveFree0": int(first_receive["free0"]),
            "secondReceiveFree0": int(second_receive["free0"]),
            "patchedGateBytes": PATCHED_GATE_BYTES,
            "originalCamera": first_receive["cam0"],
            "freeCamera": on_set["camera"],
            "claim": "safe-copy experimental free-camera gate bypass reaches button=1, toggles on, and restores the old camera on a second tap",
        }
    )
    return summary


def validate_baseline(payload: dict[str, Any], *, min_capture_count: int) -> dict[str, Any]:
    summary, log_text = common_validate(
        payload,
        expected_patch_present=False,
        min_capture_count=min_capture_count,
        min_input_actions=1,
    )
    rows = parse_rows(log_text)
    receive = rows["receive"]
    cases = rows["case"]
    gates = rows["gate"]
    require(len(receive) >= 1, "Baseline proof needs a BUTTON_TOGGLE_FREE_CAMERA receive row.")
    require(receive[0]["free0"] == "0", "Baseline receive row should start with free0=0.")
    require(cases, "Baseline proof needs a free-camera case row.")
    require(all(normalize_gate_bytes(row["gate_bytes"]) == CLEAN_GATE_BYTES for row in cases), "Baseline free-camera case did not show clean branch bytes.")
    require(gates, "Baseline proof needs a gate-site row.")
    require(all(normalize_gate_bytes(row["gate_bytes"]) == CLEAN_GATE_BYTES for row in gates), "Baseline gate site did not show clean branch bytes.")
    require(not rows["toggle"], "Baseline unexpectedly hit CGame__ToggleFreeCameraOn.")
    require(not rows["set_camera"], "Baseline unexpectedly hit CGame__SetCurrentCamera.")
    summary.update(
        {
            "schema": "winui-safe-copy-free-camera-toggle-proof.v1",
            "mode": "baseline",
            "receiveButton1Count": len(receive),
            "freeCameraCaseCount": len(cases),
            "gateSiteCount": len(gates),
            "toggleOnCount": 0,
            "setCurrentCameraCount": 0,
            "cleanGateBytes": CLEAN_GATE_BYTES,
            "claim": "safe-copy clean branch receives button=1 but does not reach the free-camera toggle path",
        }
    )
    return summary


def fixture(log_path: Path, *, patched: bool) -> dict[str, Any]:
    gate = PATCHED_GATE_BYTES if patched else CLEAN_GATE_BYTES
    if patched:
        log = (
            "CGame__ReceiveButtonAction game=008a9a98 fromController=03c8f6b0 button=1 free0=0 free1=0 "
            "player0=044ae340 player1=00000000 cam0=0399ae40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
            f"CGame__FreeCameraCase game=008a9a98 free0=0 free1=0 gateBytes={gate} "
            f"CGame__FreeCameraGateSite game=001af3a8 eax=00000000 al=00 free0=1769192 free1=5316980 gateBytes={gate} "
            "CGame__ToggleFreeCameraOn game=008a9a98 player=0 freeBefore0=0 freeBefore1=0 "
            "player0=044ae340 player1=00000000 cam0=0399ae40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
            "CGame__SetCurrentCamera game=008a9a98 player=0 camera=03cd0910 releaseOld=0 free0=0 free1=0 "
            "cam0=0399ae40 cam1=00000000 oldCam0=0399ae40 oldCam1=00000000 "
            "CGame__ReceiveButtonAction game=008a9a98 fromController=03c8f6b0 button=1 free0=1 free1=0 "
            "player0=044ae340 player1=00000000 cam0=03cd0910 cam1=00000000 oldCam0=0399ae40 oldCam1=00000000 "
            f"CGame__FreeCameraCase game=008a9a98 free0=1 free1=0 gateBytes={gate} "
            f"CGame__FreeCameraGateSite game=001af3a8 eax=00000000 al=00 free0=1769192 free1=5316980 gateBytes={gate} "
            "CGame__SetCurrentCamera game=008a9a98 player=0 camera=0399ae40 releaseOld=1 free0=0 free1=0 "
            "cam0=03cd0910 cam1=00000000 oldCam0=0399ae40 oldCam1=00000000"
        )
        patch_keys = ["resolution_gate", "force_windowed", FREE_CAMERA_PATCH_KEY]
        input_actions = 3
        key_events = 4
    else:
        log = (
            "CGame__ReceiveButtonAction game=008a9a98 fromController=03c5b6b0 button=1 free0=0 free1=0 "
            "player0=0447a340 player1=00000000 cam0=03966e40 cam1=00000000 oldCam0=00000000 oldCam1=00000000 "
            f"CGame__FreeCameraCase game=008a9a98 free0=0 free1=0 gateBytes={gate} "
            f"CGame__FreeCameraGateSite game=001af3a8 eax=00000000 al=00 free0=1769192 free1=5316980 gateBytes={gate}"
        )
        patch_keys = ["resolution_gate", "force_windowed"]
        input_actions = 1
        key_events = 2
    log_path.write_text(log, encoding="utf-8")
    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {"patchKeys": patch_keys},
        "launch": {"processId": 1234, "observedAlive": True, "mainWindowHandle": "0x123"},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "input": [{"status": "sent", "processId": 1234, "hwndHex": "0x123", "focused": True}],
        "inputSummary": {
            "inputSequencesSent": 1,
            "inputActionCount": input_actions,
            "inputKeyEventsSent": key_events,
        },
        "captures": [
            {
                "status": "captured",
                "processId": 1234,
                "hwndHex": "0x123",
                "fileSize": 503209,
                "visualProof": True,
            }
        ],
        "stop": {"Success": True},
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
            "logPath": str(log_path),
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
            "cleanup": {"status": "stopped"},
        },
        "claimBoundary": (
            "This does not prove camera movement, gameplay, rendering correctness, visual parity, "
            "unoccluded pixels, or rebuild parity."
        ),
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        patched_path = root / "patched.json"
        baseline_path = root / "baseline.json"
        patched_log = root / "patched.log"
        baseline_log = root / "baseline.log"
        patched_path.write_text(json.dumps(fixture(patched_log, patched=True)), encoding="utf-8")
        baseline_path.write_text(json.dumps(fixture(baseline_log, patched=False)), encoding="utf-8")
        positive = validate_positive(read_json(patched_path), min_capture_count=1)
        baseline = validate_baseline(read_json(baseline_path), min_capture_count=1)
        require(positive["secondReceiveFree0"] == 1, "Self-test expected second receive free0=1.")
        require(baseline["toggleOnCount"] == 0, "Self-test expected clean baseline to block toggle.")

        bad = fixture(patched_log, patched=True)
        patched_log.write_text(patched_log.read_text(encoding="utf-8").replace(PATCHED_GATE_BYTES, CLEAN_GATE_BYTES), encoding="utf-8")
        patched_path.write_text(json.dumps(bad), encoding="utf-8")
        try:
            validate_positive(read_json(patched_path), min_capture_count=1)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected clean bytes in patched proof to fail.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Positive patched runtime smoke JSON artifact")
    parser.add_argument("--baseline-artifact", default="", help="Optional clean-branch baseline runtime smoke JSON artifact")
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive.")
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy free-camera toggle artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary: dict[str, Any] = {
            "positive": validate_positive(read_json(Path(args.artifact)), min_capture_count=args.min_capture_count),
        }
        if args.baseline_artifact:
            summary["baseline"] = validate_baseline(read_json(Path(args.baseline_artifact)), min_capture_count=args.min_capture_count)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy free-camera toggle artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
