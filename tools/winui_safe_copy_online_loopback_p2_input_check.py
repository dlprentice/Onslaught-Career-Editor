#!/usr/bin/env python3
"""Validate a loopback remote-intent-to-P2 copied-BEA input proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_input_state_delta_check as state_delta


EXPECTED_SCHEMA = "winui-original-binary-loopback-p2-input.v1"
EXPECTED_TRANSPORT = "local-loopback-mock"
EXPECTED_PROTOCOL = "loopback-input.v1"
EXPECTED_HELPER = "winui-original-binary-loopback-helper"
EXPECTED_HELPER_VERSION = "loopback-helper.v1"
EXPECTED_REMOTE_SLOT = "P2"
EXPECTED_REMOTE_COMMAND = "movement-forward"
EXPECTED_MAPPED_SEQUENCE = "down:E,wait:500,up:E"
EXPECTED_WAIT_SEQUENCE_PREFIX = "wait:"
EXPECTED_CLEAN_SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"


class LoopbackProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LoopbackProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def int_at(value: dict[str, Any], key: str, default: int | None = None) -> int:
    child = value.get(key)
    if isinstance(child, int):
        return child
    require(default is not None, f"missing integer: {key}")
    return default


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = bundle_path.parent / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"live runtime artifact is missing: {candidate}")
    return candidate


def capture_has_visual_proof(item: dict[str, Any]) -> bool:
    return state_delta.capture_has_visual_proof(item)


def visual_capture_count(captures: list[Any]) -> int:
    return sum(1 for item in captures if isinstance(item, dict) and capture_has_visual_proof(item))


def require_live_source_safety(live: dict[str, Any]) -> None:
    source = object_at(live, "source")
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe changed")
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe changed")
    require(object_at(source, "saveAndOptions").get("unchanged") is True, "source save/options changed")

    process_baseline = object_at(live, "processBaseline")
    require(process_baseline.get("noPreexistingBea") is True, "preexisting BEA process was present")
    require(process_baseline.get("noBeaAfterStop") is True, "BEA process remained after stop")
    require(object_at(live, "stop").get("Success") is True, "managed stop did not succeed")


def require_loopback_contract(bundle: dict[str, Any]) -> dict[str, Any]:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected loopback proof schema")
    loopback = object_at(bundle, "loopback")
    require(loopback.get("transport") == EXPECTED_TRANSPORT, "loopback transport must be local-loopback-mock")
    require(loopback.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected loopback protocol version")
    require(loopback.get("remoteSlot") == EXPECTED_REMOTE_SLOT, "loopback proof must target remoteSlot=P2")
    require(loopback.get("command") == EXPECTED_REMOTE_COMMAND, "unexpected loopback command")
    require(loopback.get("mappedInputSequence") == EXPECTED_MAPPED_SEQUENCE, "unexpected mapped input sequence")
    require(loopback.get("networkSocketsOpened") is False, "loopback proof must not open network sockets")
    require(loopback.get("matchmakingServerContacted") is False, "loopback proof must not contact matchmaking")
    require(loopback.get("publicServerClaim") is False, "loopback proof must not claim public server behavior")
    require(loopback.get("nativeBeaNetcodeClaim") is False, "loopback proof must not claim native BEA netcode")
    return loopback


def require_session_metadata(bundle: dict[str, Any], *, expected_controller_configuration: int) -> dict[str, Any]:
    session = object_at(bundle, "session")
    require(session.get("helperName") == EXPECTED_HELPER, "unexpected helperName")
    require(session.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected helperVersion")
    require(session.get("protocolVersion") == EXPECTED_PROTOCOL, "session protocolVersion mismatch")
    require(str(session.get("cleanSpecimenSha256", "")).lower() == EXPECTED_CLEAN_SPECIMEN_SHA256, "clean specimen hash mismatch")
    require(session.get("levelId") == 850, "loopback session must target level 850")
    require(session.get("controllerConfiguration") == expected_controller_configuration, "session controller configuration mismatch")
    require(session.get("inputCdbWindowIndex") == 2, "session must correlate to CDB input window 2")
    require(session.get("remotePlayerSlot") == EXPECTED_REMOTE_SLOT, "session remote player slot mismatch")
    require(session.get("mappedInputSequence") == EXPECTED_MAPPED_SEQUENCE, "session mapped input sequence mismatch")
    launch_arguments = session.get("launchArguments")
    require(
        launch_arguments == state_delta.expected_args(expected_controller_configuration),
        "session launch arguments mismatch",
    )
    patch_keys = session.get("patchKeys")
    require(isinstance(patch_keys, list) and {"force_windowed", "resolution_gate"}.issubset(set(patch_keys)), "session patch keys must include the windowed pair")
    profile_root = Path(str(session.get("safeCopyProfileRoot") or ""))
    manifest_path = Path(str(session.get("profileManifestPath") or ""))
    manifest_sha256 = str(session.get("profileManifestSha256") or "").lower()
    require(profile_root.is_dir(), "session safe-copy profile root is missing")
    require(manifest_path.is_file(), "session profile manifest is missing")
    require(len(manifest_sha256) == 64 and sha256_file(manifest_path) == manifest_sha256, "session profile manifest hash mismatch")
    return session


def require_command_envelope(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    rejected = list_at(commands, "rejected")
    require(len(accepted) == 1, "loopback proof expects exactly one accepted remote command")
    accepted_command = accepted[0]
    require(isinstance(accepted_command, dict), "accepted command row is not an object")
    require(accepted_command.get("commandId") == "loopback-p2-forward-0001", "unexpected accepted command id")
    require(accepted_command.get("order") == 1, "accepted command order mismatch")
    require(accepted_command.get("remoteSlot") == EXPECTED_REMOTE_SLOT, "accepted command slot mismatch")
    require(accepted_command.get("command") == EXPECTED_REMOTE_COMMAND, "accepted command mismatch")
    require(accepted_command.get("mappedInputSequence") == EXPECTED_MAPPED_SEQUENCE, "accepted command mapped sequence mismatch")
    require(accepted_command.get("cdbInputWindowIndex") == 2, "accepted command must correlate to CDB input window 2")
    require(accepted_command.get("inputSent") is True, "accepted command did not send input")

    require(len(rejected) >= 2, "loopback proof expects rejected malformed/P1 command evidence")
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require("malformed-command" in reasons, "missing malformed-command rejection")
    require("remote-slot-not-allowed" in reasons, "missing remote-slot-not-allowed rejection")
    for index, row in enumerate(rejected, start=1):
        require(isinstance(row, dict), f"rejected command row {index} is not an object")
        require(row.get("inputSent") is False, f"rejected command row {index} sent input")
    return accepted_command


def require_input_delivery(live: dict[str, Any], *, expected_controller_configuration: int) -> dict[str, Any]:
    require(live.get("schemaVersion") == state_delta.EXPECTED_SCHEMA, "unexpected live runtime artifact schema")

    launch = object_at(live, "launch")
    require(
        launch.get("arguments") == state_delta.expected_args(expected_controller_configuration),
        f"launch args are not -skipfmv -level 850 -configuration {expected_controller_configuration}",
    )
    launch_pid = int_at(launch, "processId")

    captures = list_at(live, "captures")
    require(bool(captures), "live artifact has no captures")
    visual_count = visual_capture_count(captures)
    require(visual_count > 0, "live artifact has no foreground/occlusion-free visual capture")

    safe_copy = object_at(live, "safeCopy")
    control_options = object_at(safe_copy, "controlOptions")
    require(control_options.get("requestedPersistedControllerConfig") is True, "copied options controller config was not requested")
    require(control_options.get("requestedControllerConfig") == expected_controller_configuration, "requested controller config mismatch")
    require(control_options.get("observedControllerConfigP1") == expected_controller_configuration, "observed P1 controller config mismatch")
    require(control_options.get("observedControllerConfigP2") == expected_controller_configuration, "observed P2 controller config mismatch")
    state_delta.require_expected_qe_proof_lever(
        control_options,
        "input-isolation-forward-qe",
        expected_controller_configuration,
    )

    input_plan = object_at(live, "inputPlan")
    require(input_plan.get("allowBackgroundWindowMessages") is False, "background window messages were allowed")
    if "inputSequenceCount" in input_plan:
        require(input_plan.get("inputSequenceCount") == 2, "loopback proof expects exactly two input sequences")
    input_summary = object_at(live, "inputSummary")
    require(int_at(input_summary, "inputSequencesSent") == 2, "loopback proof expects exactly two sent input sequences")
    require(int_at(input_summary, "focusedInputSequences") == 2, "both loopback input sequences must be focused")
    require(int_at(input_summary, "inputWindowMessageEventsSent") == 0, "PostMessage/background input was used")
    require(
        int_at(input_summary, "inputSendInputEventsSent", 0) + int_at(input_summary, "inputScanKeybdEventsSent", 0) >= 2,
        "focused scan-code keyboard path was not used",
    )

    input_rows = live.get("input") or []
    require(isinstance(input_rows, list), "input must be a list when present")
    require(len(input_rows) == 2, "loopback proof expects exactly two input result rows")
    for index, row in enumerate(input_rows, start=1):
        require(isinstance(row, dict), f"input row {index} is not an object")
        require(row.get("status") == "sent", f"input row {index} was not sent")
        require(row.get("focused") is True, f"input row {index} was not focused")
        require(row.get("backgroundWindowMessagesAllowed") is False, f"input row {index} allowed background messages")
        require(row.get("windowMessageEventsSent") == 0, f"input row {index} used window messages")

    observer = object_at(live, "cdbObserver")
    require(observer.get("enabled") is True, "CDB observer not enabled")
    require(
        str(observer.get("commandFile") or "").replace("\\", "/").endswith(state_delta.EXPECTED_COMMAND_FILE),
        "wrong CDB command file",
    )
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(result.get("logExists") is True, "CDB log was not created")
    require(result.get("targetProcessId") == launch_pid, "CDB target PID does not match launched process")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish")

    log_path = Path(str(result.get("logPath") or observer.get("logPath") or ""))
    require(log_path.is_file(), f"CDB log path is missing: {log_path}")
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    render = state_delta.render_row(log_text)
    require(render["players"] == 2, "CGame__Render players was not 2")
    require(render["level"] == 850, "CGame__Render level was not 850")
    require(render["horizSplit"] == 1, "CGame__Render horizontal split flag was not 1")
    p0 = str(render["p0"])
    p1 = str(render["p1"])
    require(state_delta.nonzero_hex(p0) and state_delta.nonzero_hex(p1) and p0 != p1, "P0/P1 pointers were missing or not distinct")

    windows = state_delta.sequence_windows_from_artifact(live, log_path)
    require(set(windows) == {1, 2}, "loopback proof expects exactly two CDB input windows")
    wait_sequence, _, wait_text = windows[1]
    require(wait_sequence.lower().startswith(EXPECTED_WAIT_SEQUENCE_PREFIX), "first loopback window must be a wait baseline")
    state_delta.require_wait_window_clean(1, wait_sequence, wait_text)

    command_sequence, byte_length, command_text = windows[2]
    require(command_sequence == EXPECTED_MAPPED_SEQUENCE, "second loopback window must be the mapped P2 E sequence")
    summary = state_delta.summarize_window(2, command_sequence, byte_length, command_text)
    p2_window = state_delta.require_target_window(
        summary=summary,
        text=command_text,
        key="E",
        input_device=1,
        player=p1,
        other_player=p0,
    )
    require(p2_window["player"] == p1, "loopback command did not route to P2")

    return {
        "launchArguments": state_delta.expected_args(expected_controller_configuration),
        "visualCaptureCount": visual_count,
        "p0": p0,
        "p1": p1,
        "p2Window": p2_window,
    }


def validate_bundle(path: Path, *, expected_controller_configuration: int) -> dict[str, Any]:
    bundle = read_json(path)
    loopback = require_loopback_contract(bundle)
    session = require_session_metadata(bundle, expected_controller_configuration=expected_controller_configuration)
    accepted_command = require_command_envelope(bundle)
    live_path = resolve_artifact_path(path, str(bundle.get("liveRuntimeArtifact", "")))
    live = read_json(live_path)
    require_live_source_safety(live)
    delivery = require_input_delivery(live, expected_controller_configuration=expected_controller_configuration)
    return {
        "artifact": str(path),
        "liveRuntimeArtifact": str(live_path),
        "claim": "local loopback remote P2 Movement/Forward command reached the copied original-binary P2 route",
        "remoteSlot": loopback["remoteSlot"],
        "command": loopback["command"],
        "transport": loopback["transport"],
        "helperVersion": session["helperVersion"],
        "acceptedCommandId": accepted_command["commandId"],
        "controllerConfiguration": expected_controller_configuration,
        "delivery": delivery,
        "claimBoundary": (
            "This proves only a local mock remote-intent bridge into one safe copied original BEA level-850 split-screen "
            "session, with exact-PID CDB evidence that the mapped P2 E input reached the P2 movement/state path. It does "
            "not prove real networking, matchmaking, public relay/server behavior, native BEA netcode, deterministic sync, "
            "anti-cheat, physical gamepad behavior, dual-binary parity, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_bundle_fixture(root: Path, *, wrong_slot: bool = False, wrong_transport: bool = False, wrong_player: bool = False, window_messages: bool = False) -> Path:
    live_path = state_delta.make_artifact(
        root,
        controller_configuration=1,
        qe_proof_lever="input-isolation-forward-qe",
        wrong_player=wrong_player,
    )
    live = read_json(live_path)
    old_windows = live["inputCdbWindows"]
    live["inputCdbWindows"] = [
        {
            "index": 1,
            "sequence": "wait:300",
            "logStartByte": old_windows[2]["logStartByte"],
            "logEndByte": old_windows[2]["logEndByte"],
        },
        {
            "index": 2,
            "sequence": EXPECTED_MAPPED_SEQUENCE,
            "logStartByte": old_windows[3]["logStartByte"],
            "logEndByte": old_windows[3]["logEndByte"],
        },
    ]
    live["inputPlan"]["inputSequenceCount"] = 2
    live["inputSummary"]["inputSequencesSent"] = 2
    live["inputSummary"]["focusedInputSequences"] = 2
    live["inputSummary"]["inputKeyEventsSent"] = 2
    live["inputSummary"]["inputSendInputEventsSent"] = 2
    live["inputSummary"]["inputWindowMessageEventsSent"] = 2 if window_messages else 0
    live["input"] = [
        {
            "status": "sent",
            "focused": True,
            "backgroundWindowMessagesAllowed": False,
            "windowMessageEventsSent": 0,
        },
        {
            "status": "sent",
            "focused": True,
            "backgroundWindowMessagesAllowed": False,
            "windowMessageEventsSent": 2 if window_messages else 0,
        },
    ]
    live_path.write_text(json.dumps(live), encoding="utf-8")

    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "liveRuntimeArtifact": live_path.name,
        "session": {
            "helperName": EXPECTED_HELPER,
            "helperVersion": EXPECTED_HELPER_VERSION,
            "protocolVersion": EXPECTED_PROTOCOL,
            "cleanSpecimenSha256": EXPECTED_CLEAN_SPECIMEN_SHA256,
            "patchKeys": ["force_windowed", "resolution_gate"],
            "safeCopyProfileRoot": str(root),
            "profileManifestPath": str(root / "onslaught-profile-manifest.json"),
            "profileManifestSha256": "",
            "launchArguments": state_delta.expected_args(1),
            "levelId": 850,
            "controllerConfiguration": 1,
            "remotePlayerSlot": EXPECTED_REMOTE_SLOT,
            "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
            "inputCdbWindowIndex": 2,
        },
        "commands": {
            "accepted": [
                {
                    "commandId": "loopback-p2-forward-0001",
                    "order": 1,
                    "remoteSlot": EXPECTED_REMOTE_SLOT,
                    "command": EXPECTED_REMOTE_COMMAND,
                    "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
                    "cdbInputWindowIndex": 2,
                    "inputSent": True,
                }
            ],
            "rejected": [
                {
                    "commandId": "loopback-reject-malformed-0001",
                    "reason": "malformed-command",
                    "inputSent": False,
                },
                {
                    "commandId": "loopback-reject-p1-0001",
                    "remoteSlot": "P1",
                    "reason": "remote-slot-not-allowed",
                    "inputSent": False,
                },
            ],
        },
        "loopback": {
            "transport": "bad-transport" if wrong_transport else EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "remoteSlot": "P1" if wrong_slot else EXPECTED_REMOTE_SLOT,
            "command": EXPECTED_REMOTE_COMMAND,
            "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
            "networkSocketsOpened": False,
            "matchmakingServerContacted": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
        },
    }
    manifest_path = root / "onslaught-profile-manifest.json"
    manifest_path.write_text(json.dumps({"fixture": True}), encoding="utf-8")
    bundle["session"]["profileManifestSha256"] = sha256_file(manifest_path)
    bundle_path = root / "loopback-p2-input-proof.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_bundle(make_bundle_fixture(Path(tmp)), expected_controller_configuration=1)
        require(summary["remoteSlot"] == EXPECTED_REMOTE_SLOT, "fixture should target P2")
        require(summary["delivery"]["p2Window"]["inputDevice"] == 1, "fixture should use P2 input device")

    for label, kwargs in (
        ("wrong slot should fail", {"wrong_slot": True}),
        ("wrong transport should fail", {"wrong_transport": True}),
        ("wrong player route should fail", {"wrong_player": True}),
        ("window-message input should fail", {"window_messages": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs), expected_controller_configuration=1)
            except (LoopbackProofError, state_delta.ArtifactError):
                pass
            else:
                raise LoopbackProofError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary loopback P2 input checker self-test: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    summary = validate_bundle(args.bundle, expected_controller_configuration=args.expected_controller_configuration)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LoopbackProofError, state_delta.ArtifactError) as exc:
        print(f"WinUI original-binary loopback P2 input check: FAIL: {exc}")
        raise SystemExit(2)
