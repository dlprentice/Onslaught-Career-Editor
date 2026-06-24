#!/usr/bin/env python3
"""Validate a local-multiplayer input-to-BattleEngine-part state handoff artifact."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "local-multiplayer-level850-input-state-delta-observer.cdb.txt"
EXPECTED_ARGS_PREFIX = ["-skipfmv", "-level", "850", "-configuration"]
DEFAULT_QE_PROOF_LEVER = "config2-census-movement-forward-qe"
QE_PROOF_LEVERS = {
    "config2-census-movement-forward-qe": {
        "artifactProofLever": "copied-defaultoptions-config2-census-movement-forward-qe",
        "config2CensusRow": "movement-forward",
        "allowedControllerConfigurations": (2,),
    },
    "input-isolation-forward-qe": {
        "artifactProofLever": "copied-defaultoptions-input-isolation-forward-qe",
        "inputIsolationForwardQe": True,
        "allowedControllerConfigurations": (1, 2, 3, 4),
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


def normalize_hex(value: str) -> str:
    return value.lower()


def expected_args(controller_configuration: int) -> list[str]:
    return EXPECTED_ARGS_PREFIX + [str(controller_configuration)]


def vector_value(row: dict[str, str], key: str) -> tuple[str, str, str]:
    raw = row[key]
    parts = raw.split("/")
    require(len(parts) == 3, f"malformed vector field {key}: {raw}")
    return tuple(part.lower() for part in parts)  # type: ignore[return-value]


def count_by(values: list[str | int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


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
    pattern = (
        r"CController__SendButtonAction controller=([0-9a-fA-F]+) button=(\d+) rawButton=([0-9a-fA-F]+) "
        r"analogRaw=([0-9a-fA-F]+) inputDevice=([0-9a-fA-F]+) controllerConfig=([0-9a-fA-F]+) "
        r"buttons0=([0-9a-fA-F]+) buttons1=([0-9a-fA-F]+) buttons2=([0-9a-fA-F]+) target=([0-9a-fA-F]+)"
    )
    rows: list[dict[str, str | int]] = []
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "controller": normalize_hex(match.group(1)),
                "button": int(match.group(2)),
                "rawButton": normalize_hex(match.group(3)),
                "analogRaw": normalize_hex(match.group(4)),
                "inputDevice": int(match.group(5), 16),
                "controllerConfig": int(match.group(6), 16),
                "target": normalize_hex(match.group(10)),
            }
        )
    return rows


def receive_state_rows(window_text: str) -> list[dict[str, str | int]]:
    pattern = (
        r"CPlayer__ReceiveButtonActionState player=([0-9a-fA-F]+) fromController=([0-9a-fA-F]+) "
        r"button=(\d+) rawButton=([0-9a-fA-F]+) analogRaw=([0-9a-fA-F]+) "
        r"gameP0=([0-9a-fA-F]+) gameP1=([0-9a-fA-F]+) be=([0-9a-fA-F]+) "
        r"state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) walker=([0-9a-fA-F]+) jet=([0-9a-fA-F]+) "
        r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+)"
    )
    rows: list[dict[str, str | int]] = []
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "player": normalize_hex(match.group(1)),
                "fromController": normalize_hex(match.group(2)),
                "button": int(match.group(3)),
                "rawButton": normalize_hex(match.group(4)),
                "analogRaw": normalize_hex(match.group(5)),
                "gameP0": normalize_hex(match.group(6)),
                "gameP1": normalize_hex(match.group(7)),
                "be": normalize_hex(match.group(8)),
                "state098": normalize_hex(match.group(9)),
                "state260": normalize_hex(match.group(10)),
                "walker": normalize_hex(match.group(11)),
                "jet": normalize_hex(match.group(12)),
                "pos": normalize_hex(match.group(13)),
                "oldpos": normalize_hex(match.group(14)),
                "vel": normalize_hex(match.group(15)),
            }
        )
    return rows


def forward_entry_rows(window_text: str) -> list[dict[str, str]]:
    pattern = (
        r"CBattleEngineWalkerPart__ForwardEntry walker=([0-9a-fA-F]+) vyRaw=([0-9a-fA-F]+) "
        r"mainPart=([0-9a-fA-F]+) state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) "
        r"lastMoveYRaw=([0-9a-fA-F]+) dashCount=([0-9a-fA-F]+) "
        r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+)"
    )
    rows: list[dict[str, str]] = []
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "walker": normalize_hex(match.group(1)),
                "vyRaw": normalize_hex(match.group(2)),
                "mainPart": normalize_hex(match.group(3)),
                "state098": normalize_hex(match.group(4)),
                "state260": normalize_hex(match.group(5)),
                "lastMoveYRaw": normalize_hex(match.group(6)),
                "dashCount": normalize_hex(match.group(7)),
                "pos": normalize_hex(match.group(8)),
                "oldpos": normalize_hex(match.group(9)),
                "vel": normalize_hex(match.group(10)),
            }
        )
    return rows


def forward_store_rows(window_text: str) -> list[dict[str, str]]:
    pattern = (
        r"CBattleEngineWalkerPart__ForwardStateStore walker=([0-9a-fA-F]+) vyRaw=([0-9a-fA-F]+) "
        r"mainPart=([0-9a-fA-F]+) state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) "
        r"storedLastMoveYRaw=([0-9a-fA-F]+) dashCount=([0-9a-fA-F]+) "
        r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+)"
    )
    rows: list[dict[str, str]] = []
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "walker": normalize_hex(match.group(1)),
                "vyRaw": normalize_hex(match.group(2)),
                "mainPart": normalize_hex(match.group(3)),
                "state098": normalize_hex(match.group(4)),
                "state260": normalize_hex(match.group(5)),
                "storedLastMoveYRaw": normalize_hex(match.group(6)),
                "dashCount": normalize_hex(match.group(7)),
                "pos": normalize_hex(match.group(8)),
                "oldpos": normalize_hex(match.group(9)),
                "vel": normalize_hex(match.group(10)),
            }
        )
    return rows


def jet_entry_rows(window_text: str) -> list[dict[str, str]]:
    pattern = (
        r"CBattleEngineJetPart__ThrustEntry jet=([0-9a-fA-F]+) vyRaw=([0-9a-fA-F]+) "
        r"mainPart=([0-9a-fA-F]+) state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) "
        r"thrusterRaw=([0-9a-fA-F]+) lastMoveYRaw=([0-9a-fA-F]+) loopFlag=([0-9a-fA-F]+) barrelCount=([0-9a-fA-F]+) "
        r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) pitchVel=([0-9a-fA-F]+)"
    )
    rows: list[dict[str, str]] = []
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "jet": normalize_hex(match.group(1)),
                "vyRaw": normalize_hex(match.group(2)),
                "mainPart": normalize_hex(match.group(3)),
                "state098": normalize_hex(match.group(4)),
                "state260": normalize_hex(match.group(5)),
                "thrusterRaw": normalize_hex(match.group(6)),
                "lastMoveYRaw": normalize_hex(match.group(7)),
                "loopFlag": normalize_hex(match.group(8)),
                "barrelCount": normalize_hex(match.group(9)),
                "pos": normalize_hex(match.group(10)),
                "oldpos": normalize_hex(match.group(11)),
                "vel": normalize_hex(match.group(12)),
                "pitchVel": normalize_hex(match.group(13)),
            }
        )
    return rows


def jet_store_rows(window_text: str) -> list[dict[str, str]]:
    pattern = (
        r"CBattleEngineJetPart__ThrustStateStore jet=([0-9a-fA-F]+) vyRaw=([0-9a-fA-F]+) "
        r"mainPart=([0-9a-fA-F]+) state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) "
        r"thrusterRaw=([0-9a-fA-F]+) storedLastMoveYRaw=([0-9a-fA-F]+) loopFlag=([0-9a-fA-F]+) barrelCount=([0-9a-fA-F]+) "
        r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) pitchVel=([0-9a-fA-F]+)"
    )
    rows: list[dict[str, str]] = []
    for match in all_regex(pattern, window_text):
        rows.append(
            {
                "jet": normalize_hex(match.group(1)),
                "vyRaw": normalize_hex(match.group(2)),
                "mainPart": normalize_hex(match.group(3)),
                "state098": normalize_hex(match.group(4)),
                "state260": normalize_hex(match.group(5)),
                "thrusterRaw": normalize_hex(match.group(6)),
                "storedLastMoveYRaw": normalize_hex(match.group(7)),
                "loopFlag": normalize_hex(match.group(8)),
                "barrelCount": normalize_hex(match.group(9)),
                "pos": normalize_hex(match.group(10)),
                "oldpos": normalize_hex(match.group(11)),
                "vel": normalize_hex(match.group(12)),
                "pitchVel": normalize_hex(match.group(13)),
            }
        )
    return rows


def render_row(log_text: str) -> dict[str, str | int]:
    pattern = (
        r"CGame__Render this=([0-9a-fA-F]+) numRenders=(\d+) players=(\d+) level=(\d+) "
        r"fullscreenMP=(\d+) horizSplit=(\d+) p0=([0-9a-fA-F]+) p1=([0-9a-fA-F]+) "
        r"cam0=([0-9a-fA-F]+) cam1=([0-9a-fA-F]+) world=([0-9a-fA-F]+) "
        r"p0be=([0-9a-fA-F]+) p1be=([0-9a-fA-F]+) p0walker=([0-9a-fA-F]+) p1walker=([0-9a-fA-F]+)"
    )
    match = re.search(pattern, log_text, flags=re.IGNORECASE)
    require(match is not None, "missing extended CGame__Render state observation")
    return {
        "game": normalize_hex(match.group(1)),
        "players": int(match.group(3)),
        "level": int(match.group(4)),
        "horizSplit": int(match.group(6)),
        "p0": normalize_hex(match.group(7)),
        "p1": normalize_hex(match.group(8)),
        "p0be": normalize_hex(match.group(12)),
        "p1be": normalize_hex(match.group(13)),
        "p0walker": normalize_hex(match.group(14)),
        "p1walker": normalize_hex(match.group(15)),
    }


def summarize_window(index: int, sequence: str, byte_length: int, text: str) -> dict[str, Any]:
    sends = send_rows(text)
    receives = receive_state_rows(text)
    entries = forward_entry_rows(text)
    stores = forward_store_rows(text)
    jet_entries = jet_entry_rows(text)
    jet_stores = jet_store_rows(text)
    send31 = [row for row in sends if int(row["button"]) == 31]
    receive31 = [row for row in receives if int(row["button"]) == 31]
    return {
        "index": index,
        "sequence": sequence,
        "cdbByteLength": byte_length,
        "sendRows": len(sends),
        "receiveRows": len(receives),
        "forwardEntryRows": len(entries),
        "forwardStateStoreRows": len(stores),
        "jetThrustEntryRows": len(jet_entries),
        "jetThrustStateStoreRows": len(jet_stores),
        "sendButtons": sorted({int(row["button"]) for row in sends}),
        "receiveButtons": sorted({int(row["button"]) for row in receives}),
        "sendControllerConfigurations": sorted({int(row["controllerConfig"]) for row in sends}),
        "sendButton31InputDeviceCounts": count_by([int(row["inputDevice"]) for row in send31]),
        "sendButton31ControllerCounts": count_by([str(row["controller"]) for row in send31 if nonzero_hex(str(row["controller"]))]),
        "receiveButton31PlayerCounts": count_by([str(row["player"]) for row in receive31 if nonzero_hex(str(row["player"]))]),
        "receiveButton31FromControllerCounts": count_by([str(row["fromController"]) for row in receive31 if nonzero_hex(str(row["fromController"]))]),
        "receiveBattleEngines": sorted({str(row["be"]) for row in receive31 if nonzero_hex(str(row["be"]))}),
        "receiveWalkers": sorted({str(row["walker"]) for row in receive31 if nonzero_hex(str(row["walker"]))}),
        "forwardEntryWalkers": count_by([row["walker"] for row in entries if nonzero_hex(row["walker"])]),
        "forwardStateStoreWalkers": count_by([row["walker"] for row in stores if nonzero_hex(row["walker"])]),
        "forwardStateStoreValues": count_by([row["storedLastMoveYRaw"] for row in stores]),
        "jetThrustEntryJets": count_by([row["jet"] for row in jet_entries if nonzero_hex(row["jet"])]),
        "jetThrustStateStoreJets": count_by([row["jet"] for row in jet_stores if nonzero_hex(row["jet"])]),
        "jetThrustStateStoreValues": count_by([row["storedLastMoveYRaw"] for row in jet_stores]),
    }


def require_wait_window_clean(index: int, sequence: str, text: str) -> None:
    require(sequence.lower().startswith("wait:"), f"window {index} is not a wait baseline window")
    require(not send_rows(text), f"wait window {index} had button-31 send rows")
    require(not receive_state_rows(text), f"wait window {index} had button-31 receive rows")
    require(not forward_store_rows(text), f"wait window {index} had Forward state-store rows")


def require_target_window(
    *,
    summary: dict[str, Any],
    text: str,
    key: str,
    input_device: int,
    player: str,
    other_player: str,
) -> dict[str, Any]:
    sequence = str(summary["sequence"])
    require(
        re.fullmatch(rf"down:{re.escape(key)},wait:\d+,up:{re.escape(key)}", sequence) is not None,
        f"input window {summary['index']} does not contain expected down:{key},wait:<ms>,up:{key} sequence",
    )
    require(summary["sendButton31InputDeviceCounts"], f"input window {summary['index']} did not send button 31")
    require(
        summary["sendButton31InputDeviceCounts"] == {str(input_device): sum(summary["sendButton31InputDeviceCounts"].values())},
        f"input window {summary['index']} button 31 was not isolated to input device {input_device}",
    )
    receive_counts = summary["receiveButton31PlayerCounts"]
    require(receive_counts, f"input window {summary['index']} did not receive button 31")
    require(
        receive_counts == {player: sum(receive_counts.values())},
        f"input window {summary['index']} button 31 did not route only to expected player {player}",
    )
    require(other_player not in receive_counts, f"input window {summary['index']} also received button 31 on non-target player")

    receive_rows = [row for row in receive_state_rows(text) if int(row["button"]) == 31 and str(row["player"]) == player]
    require(receive_rows, f"input window {summary['index']} has no target receive-state rows")
    battle_engines = {str(row["be"]) for row in receive_rows if nonzero_hex(str(row["be"]))}
    walkers = {str(row["walker"]) for row in receive_rows if nonzero_hex(str(row["walker"]))}
    jets = {str(row["jet"]) for row in receive_rows if nonzero_hex(str(row["jet"]))}
    controllers = {str(row["fromController"]) for row in receive_rows if nonzero_hex(str(row["fromController"]))}
    state260s = {str(row["state260"]) for row in receive_rows}
    require(len(battle_engines) == 1, f"input window {summary['index']} did not isolate to one BattleEngine pointer")
    require(len(walkers) == 1, f"input window {summary['index']} did not isolate to one WalkerPart pointer")
    require(len(jets) == 1, f"input window {summary['index']} did not isolate to one JetPart pointer")
    require(len(controllers) == 1, f"input window {summary['index']} did not isolate to one controller pointer")
    require(len(state260s) == 1, f"input window {summary['index']} did not isolate to one BattleEngine state260 value")
    battle_engine = next(iter(battle_engines))
    walker = next(iter(walkers))
    jet = next(iter(jets))
    controller = next(iter(controllers))
    state260 = next(iter(state260s))

    entries = [
        row for row in forward_entry_rows(text)
        if row["walker"] == walker and row["mainPart"] == battle_engine
    ]
    stores = [
        row for row in forward_store_rows(text)
        if row["walker"] == walker and row["mainPart"] == battle_engine
    ]
    forward_nonzero_stores = [
        row for row in stores
        if row["storedLastMoveYRaw"] == row["vyRaw"] and nonzero_hex(row["storedLastMoveYRaw"])
    ]
    jet_entries = [
        row for row in jet_entry_rows(text)
        if row["jet"] == jet and row["mainPart"] == battle_engine
    ]
    jet_stores = [
        row for row in jet_store_rows(text)
        if row["jet"] == jet and row["mainPart"] == battle_engine
    ]
    jet_nonzero_stores = [
        row for row in jet_stores
        if row["storedLastMoveYRaw"] == row["vyRaw"] and nonzero_hex(row["storedLastMoveYRaw"])
    ]
    route_type = ""
    if state260 == "00000002" and forward_nonzero_stores:
        route_type = "walker-forward"
    elif state260 == "00000003" and jet_nonzero_stores:
        route_type = "jet-thrust"
    require(
        route_type != "",
        f"input window {summary['index']} state260={state260} did not reach the matching nonzero WalkerPart Forward or JetPart Thrust state store",
    )

    observed_positions = {vector_value(row, "pos") for row in receive_rows}
    observed_positions.update(vector_value(row, "pos") for row in entries)
    observed_positions.update(vector_value(row, "pos") for row in stores)
    observed_positions.update(vector_value(row, "pos") for row in jet_entries)
    observed_positions.update(vector_value(row, "pos") for row in jet_stores)
    observed_velocities = {vector_value(row, "vel") for row in receive_rows}
    observed_velocities.update(vector_value(row, "vel") for row in entries)
    observed_velocities.update(vector_value(row, "vel") for row in stores)
    observed_velocities.update(vector_value(row, "vel") for row in jet_entries)
    observed_velocities.update(vector_value(row, "vel") for row in jet_stores)

    return {
        "index": summary["index"],
        "sequence": sequence,
        "routeType": route_type,
        "player": player,
        "controller": controller,
        "inputDevice": input_device,
        "battleEngine": battle_engine,
        "state260": state260,
        "walker": walker,
        "jet": jet,
        "button31ReceiveRows": sum(receive_counts.values()),
        "forwardEntryRows": len(entries),
        "forwardStateStoreRows": len(stores),
        "jetThrustEntryRows": len(jet_entries),
        "jetThrustStateStoreRows": len(jet_stores),
        "nonzeroStoredLastMoveYValues": sorted({row["storedLastMoveYRaw"] for row in forward_nonzero_stores + jet_nonzero_stores}),
        "positionTupleCount": len(observed_positions),
        "velocityTupleCount": len(observed_velocities),
        "observedVectorDelta": len(observed_positions) > 1 or len(observed_velocities) > 1,
    }


def require_expected_qe_proof_lever(
    control_options: dict[str, Any],
    expected_qe_proof_lever: str,
    expected_controller_configuration: int,
) -> None:
    proof = QE_PROOF_LEVERS.get(expected_qe_proof_lever)
    require(proof is not None, f"unsupported expected Q/E proof lever: {expected_qe_proof_lever}")
    allowed_configs = tuple(proof.get("allowedControllerConfigurations", ()))
    require(
        expected_controller_configuration in allowed_configs,
        f"proof lever {expected_qe_proof_lever} is not valid for controller config {expected_controller_configuration}",
    )
    require(control_options.get("proofLever") == proof["artifactProofLever"], "expected Movement/Forward Q/E proof lever")
    if "config2CensusRow" in proof:
        require(control_options.get("requestedConfig2CensusRowQe") == proof["config2CensusRow"], "expected copied-options config-2 Movement/Forward Q/E row")
    if proof.get("inputIsolationForwardQe") is True:
        require(control_options.get("requestedInputIsolationForwardQe") is True, "expected copied-options input-isolation Movement/Forward Q/E row")


def validate_artifact(
    path: Path,
    min_capture_count: int,
    *,
    expected_controller_configuration: int = 2,
    expected_qe_proof_lever: str = DEFAULT_QE_PROOF_LEVER,
) -> dict[str, Any]:
    require(1 <= expected_controller_configuration <= 4, "expected controller configuration must be 1..4")
    artifact = read_json(path)
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")

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
    require(object_at(artifact, "stop").get("Success") is True, "managed stop did not succeed")
    process_baseline = object_at(artifact, "processBaseline")
    require(process_baseline.get("noPreexistingBea") is True, "preexisting BEA process was present")
    require(process_baseline.get("noBeaAfterStop") is True, "BEA process remained after stop")

    captures = list_at(artifact, "captures")
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}")
    visual_count = visual_capture_count(captures)
    require(visual_count > 0, "no foreground/occlusion-free visual capture")

    control_options = object_at(object_at(artifact, "safeCopy"), "controlOptions")
    require(control_options.get("requestedPersistedControllerConfig") is True, "persisted copied-options controller configuration was not requested")
    require(control_options.get("requestedControllerConfig") == expected_controller_configuration, "requested copied-options controller config mismatch")
    require(control_options.get("observedControllerConfigP1") == expected_controller_configuration, "observed P1 copied-options controller config mismatch")
    require(control_options.get("observedControllerConfigP2") == expected_controller_configuration, "observed P2 copied-options controller config mismatch")
    require_expected_qe_proof_lever(control_options, expected_qe_proof_lever, expected_controller_configuration)

    input_plan = object_at(artifact, "inputPlan")
    require(input_plan.get("allowBackgroundWindowMessages") is False, "background window messages were allowed")
    input_summary = object_at(artifact, "inputSummary")
    sequence_count = int_at(input_summary, "inputSequencesSent")
    require(sequence_count == 4, "state-delta proof expects exactly four input windows")
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
    render = render_row(log_text)
    require(render["players"] == 2, "CGame__Render players was not 2")
    require(render["level"] == 850, "CGame__Render level was not 850")
    require(render["horizSplit"] == 1, "CGame__Render horizontal split flag was not 1")
    p0 = str(render["p0"])
    p1 = str(render["p1"])
    require(nonzero_hex(p0) and nonzero_hex(p1) and p0 != p1, "P0/P1 pointers were missing or not distinct")

    windows = sequence_windows_from_artifact(artifact, log_path)
    require(len(windows) == sequence_count, "inputCdbWindows count does not match inputSequencesSent")
    for required_index in (1, 2, 3, 4):
        require(required_index in windows, f"missing input window {required_index}")
    require_wait_window_clean(1, windows[1][0], windows[1][2])
    require_wait_window_clean(3, windows[3][0], windows[3][2])

    summaries = {
        index: summarize_window(index, sequence, byte_length, text)
        for index, (sequence, byte_length, text) in sorted(windows.items())
    }
    for summary in summaries.values():
        configs = summary["sendControllerConfigurations"]
        require(
            not configs or configs == [expected_controller_configuration],
            f"input window {summary['index']} controller configs were {configs}, expected {expected_controller_configuration}",
        )

    proof_windows = [
        require_target_window(summary=summaries[2], text=windows[2][2], key="Q", input_device=0, player=p0, other_player=p1),
        require_target_window(summary=summaries[4], text=windows[4][2], key="E", input_device=1, player=p1, other_player=p0),
    ]

    return {
        "artifact": str(path),
        "claim": f"config-{expected_controller_configuration} Movement/Forward input-to-mode-specific BattleEngine part state handoff",
        "controllerConfiguration": expected_controller_configuration,
        "proofLever": expected_qe_proof_lever,
        "launchArguments": expected_args(expected_controller_configuration),
        "captureCount": len(captures),
        "visualCaptureCount": visual_count,
        "p0": p0,
        "p1": p1,
        "render": render,
        "windows": list(summaries.values()),
        "strictStateProof": {
            "claim": "Focused Q/E input reached distinct players and reached the matching nonzero WalkerPart Forward or JetPart Thrust last-move state-store point.",
            "proofLever": control_options.get("proofLever"),
            "windows": proof_windows,
            "allTargetWindowsObservedVectorDelta": all(bool(window["observedVectorDelta"]) for window in proof_windows),
            "claimBoundary": f"This proves a copied-profile level 850 config-{expected_controller_configuration} keyboard Q/E input-to-mode-specific BattleEngine part state handoff for Movement/Forward. It does not prove visible movement causality, improved control feel, gamepad coverage, all controller configurations, online networking, deterministic sync, exact full layout, or rebuild parity.",
        },
    }


def make_artifact(
    root: Path,
    *,
    controller_configuration: int = 2,
    qe_proof_lever: str = DEFAULT_QE_PROOF_LEVER,
    wrong_command: bool = False,
    wrong_player: bool = False,
    missing_store: bool = False,
    zero_store: bool = False,
    wait_contamination: bool = False,
    wrong_state_for_walker: bool = False,
) -> Path:
    proof = QE_PROOF_LEVERS[qe_proof_lever]
    p0 = "04646090"
    p1 = "0465d890"
    p0be = "03867570"
    p1be = "0386d570"
    p0walker = "04700010"
    p1walker = "04710010"
    p0controller = "046460f0"
    p1controller = "0465d8f0"
    log_path = root / "windbg.log"
    prelude = (
        "CGame__Render this=008a9a98 numRenders=0 players=2 level=850 fullscreenMP=0 horizSplit=1 "
        f"p0={p0} p1={p1} cam0=046d97f0 cam1=046d98a0 world=038c0840 p0be={p0be} p1be={p1be} "
        f"p0walker={p0walker} p1walker={p1walker} "
    )
    wait1 = (
        f"CBattleEngineWalkerPart__ForwardStateStore walker={p0walker} vyRaw=bf800000 mainPart={p0be} state098=00000003 state260=00000002 storedLastMoveYRaw=bf800000 dashCount=00000000 pos=00000001/00000002/00000003 oldpos=00000001/00000002/00000003 vel=00000000/00000000/00000000 "
        if wait_contamination
        else ""
    )
    q_store = "" if missing_store else (
        f"CBattleEngineWalkerPart__ForwardStateStore walker={p0walker} vyRaw={'00000000' if zero_store else 'bf800000'} mainPart={p0be} state098=00000003 state260=00000002 storedLastMoveYRaw={'00000000' if zero_store else 'bf800000'} dashCount=00000000 pos=00000002/00000002/00000003 oldpos=00000001/00000002/00000003 vel=00000000/bf000000/00000000 "
    )
    q_window = (
        f"CController__SendButtonAction controller={p0controller} button=31 rawButton=0000001f analogRaw=bf800000 inputDevice=00000000 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target={p0} "
        f"CPlayer__ReceiveButtonActionState player={p0} fromController={p0controller} button=31 rawButton=0000001f analogRaw=bf800000 gameP0={p0} gameP1={p1} be={p0be} state098=00000003 state260={'00000003' if wrong_state_for_walker else '00000002'} walker={p0walker} jet=04700020 pos=00000001/00000002/00000003 oldpos=00000001/00000002/00000003 vel=00000000/00000000/00000000 "
        f"CBattleEngineWalkerPart__ForwardEntry walker={p0walker} vyRaw=bf800000 mainPart={p0be} state098=00000003 state260={'00000003' if wrong_state_for_walker else '00000002'} lastMoveYRaw=00000000 dashCount=00000000 pos=00000001/00000002/00000003 oldpos=00000001/00000002/00000003 vel=00000000/00000000/00000000 "
        + q_store
    )
    e_player = p0 if wrong_player else p1
    e_window = (
        f"CController__SendButtonAction controller={p1controller} button=31 rawButton=0000001f analogRaw=bf800000 inputDevice=00000001 controllerConfig={controller_configuration:08x} buttons0=00000000 buttons1=00000000 buttons2=00000000 target={p1} "
        f"CPlayer__ReceiveButtonActionState player={e_player} fromController={p1controller} button=31 rawButton=0000001f analogRaw=bf800000 gameP0={p0} gameP1={p1} be={p1be} state098=00000003 state260=00000002 walker={p1walker} jet=04710020 pos=00000004/00000005/00000006 oldpos=00000004/00000005/00000006 vel=00000000/00000000/00000000 "
        f"CBattleEngineWalkerPart__ForwardEntry walker={p1walker} vyRaw=bf800000 mainPart={p1be} state098=00000003 state260=00000002 lastMoveYRaw=00000000 dashCount=00000000 pos=00000004/00000005/00000006 oldpos=00000004/00000005/00000006 vel=00000000/00000000/00000000 "
        f"CBattleEngineWalkerPart__ForwardStateStore walker={p1walker} vyRaw=bf800000 mainPart={p1be} state098=00000003 state260=00000002 storedLastMoveYRaw=bf800000 dashCount=00000000 pos=00000005/00000005/00000006 oldpos=00000004/00000005/00000006 vel=00000000/bf000000/00000000 "
    )
    wait3 = ""
    chunks = [prelude, wait1, q_window, wait3, e_window]
    offsets: list[tuple[int, int]] = []
    cursor = len(prelude.encode("utf-8"))
    for chunk in chunks[1:]:
        start = cursor
        cursor += len(chunk.encode("utf-8"))
        offsets.append((start, cursor))
    log_path.write_text("".join(chunks), encoding="utf-8")
    control_options = {
        "requestedPersistedControllerConfig": True,
        "requestedControllerConfig": controller_configuration,
        "proofLever": proof["artifactProofLever"],
        "observedControllerConfigP1": controller_configuration,
        "observedControllerConfigP2": controller_configuration,
    }
    if "config2CensusRow" in proof:
        control_options["requestedConfig2CensusRowQe"] = proof["config2CensusRow"]
    if proof.get("inputIsolationForwardQe") is True:
        control_options["requestedInputIsolationForwardQe"] = True

    artifact = {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {
            "controlOptions": control_options
        },
        "launch": {"processId": 1234, "arguments": expected_args(controller_configuration)},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "captures": [{"visualProof": True}],
        "inputPlan": {"allowBackgroundWindowMessages": False},
        "inputSummary": {
            "inputSequencesSent": 4,
            "focusedInputSequences": 4,
            "inputWindowMessageEventsSent": 0,
        },
        "inputCdbWindows": [
            {"index": 1, "sequence": "wait:300", "logStartByte": offsets[0][0], "logEndByte": offsets[0][1]},
            {"index": 2, "sequence": "down:Q,wait:500,up:Q", "logStartByte": offsets[1][0], "logEndByte": offsets[1][1]},
            {"index": 3, "sequence": "wait:300", "logStartByte": offsets[2][0], "logEndByte": offsets[2][1]},
            {"index": 4, "sequence": "down:E,wait:500,up:E", "logStartByte": offsets[3][0], "logEndByte": offsets[3][1]},
        ],
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{'wrong.cdb.txt' if wrong_command else EXPECTED_COMMAND_FILE}",
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path), "targetProcessId": 1234},
            "cleanup": {"status": "stopped"},
        },
    }
    path = root / "artifact.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_artifact(make_artifact(Path(tmp)), min_capture_count=1)
        strict = summary.get("strictStateProof")
        require(isinstance(strict, dict), "strict state proof summary missing")
        require(strict["windows"][0]["player"] == "04646090", "Q window should target P0")
        require(strict["windows"][1]["player"] == "0465d890", "E window should target P1")

    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_artifact(
            make_artifact(Path(tmp), controller_configuration=1, qe_proof_lever="input-isolation-forward-qe"),
            min_capture_count=1,
            expected_controller_configuration=1,
            expected_qe_proof_lever="input-isolation-forward-qe",
        )
        require(summary["controllerConfiguration"] == 1, "config-1 input-isolation proof should be accepted")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_artifact(
                make_artifact(Path(tmp), controller_configuration=1),
                min_capture_count=1,
                expected_controller_configuration=1,
                expected_qe_proof_lever=DEFAULT_QE_PROOF_LEVER,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("config-1 should not accept config2-census Q/E proof lever")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = make_artifact(root)
        artifact = json.loads(path.read_text(encoding="utf-8"))
        artifact["inputCdbWindows"][1]["sequence"] = "tap:Q"
        path.write_text(json.dumps(artifact), encoding="utf-8")
        try:
            validate_artifact(path, min_capture_count=1)
        except ArtifactError:
            pass
        else:
            raise ArtifactError("non-down/wait/up Q sequence should fail")

    for label, kwargs in (
        ("wrong CDB command should fail", {"wrong_command": True}),
        ("wrong player route should fail", {"wrong_player": True}),
        ("missing state store should fail", {"missing_store": True}),
        ("zero state store should fail", {"zero_store": True}),
        ("wait-window contamination should fail", {"wait_contamination": True}),
        ("wrong state-to-route pairing should fail", {"wrong_state_for_walker": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_artifact(make_artifact(Path(tmp), **kwargs), min_capture_count=1)
            except ArtifactError:
                pass
            else:
                raise ArtifactError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--expected-controller-configuration", type=int, default=2, choices=(1, 2, 3, 4))
    parser.add_argument("--expected-qe-proof-lever", default=DEFAULT_QE_PROOF_LEVER, choices=tuple(QE_PROOF_LEVERS))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer input-state-delta checker self-test: PASS")
        return 0
    if args.artifact is None:
        raise SystemExit("artifact is required unless --self-test is used")
    summary = validate_artifact(
        args.artifact,
        args.min_capture_count,
        expected_controller_configuration=args.expected_controller_configuration,
        expected_qe_proof_lever=args.expected_qe_proof_lever,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ArtifactError as exc:
        print(f"WinUI safe-copy local multiplayer input-state-delta check: FAIL: {exc}")
        raise SystemExit(2)
