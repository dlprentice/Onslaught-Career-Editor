#!/usr/bin/env python3
"""Validate the public-safe control causality contract over accepted artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_movement_state_delta_check as movement_state
import winui_safe_copy_local_multiplayer_visible_movement_delta_check as visible_movement


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCHEMA = "winui-control-causality-contract.v1"
LIVE_RUNTIME_ARTIFACT_NAME = "live-safe-copy-runtime-" + "smoke.json"


class ControlCausalityContractError(RuntimeError):
    pass


SEND_PATTERN = (
    r"CController__SendButtonAction controller=([0-9a-fA-F]+) button=(\d+) rawButton=([0-9a-fA-F]+) "
    r"analogRaw=([0-9a-fA-F]+) inputDevice=([0-9a-fA-F]+) controllerConfig=([0-9a-fA-F]+) "
    r"buttons0=([0-9a-fA-F]+) buttons1=([0-9a-fA-F]+) buttons2=([0-9a-fA-F]+) target=([0-9a-fA-F]+)"
)
RECEIVE_PATTERN = (
    r"CPlayer__ReceiveButtonActionState player=([0-9a-fA-F]+) fromController=([0-9a-fA-F]+) "
    r"button=(\d+) rawButton=([0-9a-fA-F]+) analogRaw=([0-9a-fA-F]+) "
    r"gameP0=([0-9a-fA-F]+) gameP1=([0-9a-fA-F]+) be=([0-9a-fA-F]+) "
    r"state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) walker=([0-9a-fA-F]+) jet=([0-9a-fA-F]+) "
    r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
    r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
    r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+)"
)
FORWARD_STORE_PATTERN = (
    r"CBattleEngineWalkerPart__ForwardStateStore walker=([0-9a-fA-F]+) vyRaw=([0-9a-fA-F]+) "
    r"mainPart=([0-9a-fA-F]+) state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) "
    r"storedLastMoveYRaw=([0-9a-fA-F]+) dashCount=([0-9a-fA-F]+) "
    r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
    r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
    r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+)"
)
JET_STORE_PATTERN = (
    r"CBattleEngineJetPart__ThrustStateStore jet=([0-9a-fA-F]+) vyRaw=([0-9a-fA-F]+) "
    r"mainPart=([0-9a-fA-F]+) state098=([0-9a-fA-F]+) state260=([0-9a-fA-F]+) "
    r"thrusterRaw=([0-9a-fA-F]+) storedLastMoveYRaw=([0-9a-fA-F]+) loopFlag=([0-9a-fA-F]+) barrelCount=([0-9a-fA-F]+) "
    r"pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
    r"oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
    r"vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) pitchVel=([0-9a-fA-F]+)"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ControlCausalityContractError(message)


def artifact(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


MOVEMENT_CASES = (
    {
        "caseId": "config1-visible-focus2",
        "controllerConfiguration": 1,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config1-20260618-focus2", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config1-visible-focus3",
        "controllerConfiguration": 1,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config1-20260618-focus3", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config2-movement-focus1",
        "controllerConfiguration": 2,
        "proofLever": "config2-census-movement-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-movement-state-delta-config2-20260618-focus1", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config2-movement-focus2",
        "controllerConfiguration": 2,
        "proofLever": "config2-census-movement-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-movement-state-delta-config2-20260618-focus2", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config3-movement-focus1",
        "controllerConfiguration": 3,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config3-20260618-focus1", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config4-movement-focus1",
        "controllerConfiguration": 4,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-input-state-delta-config4-20260618-focus1", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config4-movement-focus2",
        "controllerConfiguration": 4,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-input-state-delta-config4-20260618-focus2", LIVE_RUNTIME_ARTIFACT_NAME),
    },
)


VISIBLE_CASES = (
    {
        "caseId": "config1-visible-focus2",
        "controllerConfiguration": 1,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config1-20260618-focus2", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config1-visible-focus3",
        "controllerConfiguration": 1,
        "proofLever": "input-isolation-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config1-20260618-focus3", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config2-visible-focus1",
        "controllerConfiguration": 2,
        "proofLever": "config2-census-movement-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config2-20260618-focus1", LIVE_RUNTIME_ARTIFACT_NAME),
    },
    {
        "caseId": "config2-visible-focus2",
        "controllerConfiguration": 2,
        "proofLever": "config2-census-movement-forward-qe",
        "path": artifact("subagents", "winui-safe-copy-live-runtime", "local-multiplayer-visible-movement-delta-config2-20260618-focus2", LIVE_RUNTIME_ARTIFACT_NAME),
    },
)


def public_state_window(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": row["role"],
        "inputDevice": row["inputDevice"],
        "routeType": row["routeType"],
        "button31ReceiveRows": row["button31ReceiveRows"],
        "forwardStateStoreRows": row["forwardStateStoreRows"],
        "nonzeroStoredLastMoveYValues": row["nonzeroStoredLastMoveYValues"],
        "targetPositionChanged": row["targetPositionChanged"],
        "targetVelocityChanged": row["targetVelocityChanged"],
        "targetDiffersFromAdjacentBaseline": row["targetDiffersFromAdjacentBaseline"],
        "baselineRenderSamples": row["baselineRenderSamples"],
        "targetRenderSamples": row["targetRenderSamples"],
    }


def normalize_hex(value: str) -> str:
    return value.lower()


def first_event_offset(pattern: str, text: str, predicate: Any, label: str) -> int:
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        if predicate(match):
            return match.start()
    raise ControlCausalityContractError(f"missing ordered CDB event: {label}")


def ordered_causality_window(
    *,
    case_id: str,
    window_text: str,
    state: dict[str, Any],
    input_device: int,
    controller_configuration: int,
) -> dict[str, Any]:
    player = normalize_hex(str(state["player"]))
    controller = normalize_hex(str(state["controller"]))
    battle_engine = normalize_hex(str(state["battleEngine"]))
    route_type = str(state["routeType"])
    send_offset = first_event_offset(
        SEND_PATTERN,
        window_text,
        lambda match: (
            int(match.group(2)) == 31
            and normalize_hex(match.group(1)) == controller
            and int(match.group(5), 16) == input_device
            and int(match.group(6), 16) == controller_configuration
        ),
        f"{case_id} controller send",
    )
    receive_offset = first_event_offset(
        RECEIVE_PATTERN,
        window_text,
        lambda match: (
            normalize_hex(match.group(1)) == player
            and normalize_hex(match.group(2)) == controller
            and int(match.group(3)) == 31
            and normalize_hex(match.group(8)) == battle_engine
        ),
        f"{case_id} player receive",
    )
    if route_type == "walker-forward":
        walker = normalize_hex(str(state["walker"]))
        store_offset = first_event_offset(
            FORWARD_STORE_PATTERN,
            window_text,
            lambda match: (
                normalize_hex(match.group(1)) == walker
                and normalize_hex(match.group(3)) == battle_engine
                and normalize_hex(match.group(6)) == normalize_hex(match.group(2))
                and int(match.group(6), 16) != 0
            ),
            f"{case_id} walker forward state store",
        )
        store_kind = "walker-forward-state-store"
    else:
        require(route_type == "jet-thrust", f"{case_id} unknown route type {route_type}")
        jet = normalize_hex(str(state["jet"]))
        store_offset = first_event_offset(
            JET_STORE_PATTERN,
            window_text,
            lambda match: (
                normalize_hex(match.group(1)) == jet
                and normalize_hex(match.group(3)) == battle_engine
                and normalize_hex(match.group(7)) == normalize_hex(match.group(2))
                and int(match.group(7), 16) != 0
            ),
            f"{case_id} jet thrust state store",
        )
        store_kind = "jet-thrust-state-store"
    require(
        send_offset < receive_offset < store_offset,
        f"{case_id} CDB event order was not send -> receive -> state-store",
    )
    return {
        "sendBeforeReceive": True,
        "receiveBeforeStateStore": True,
        "routeType": route_type,
        "storeKind": store_kind,
        "sendRelativeByte": send_offset,
        "receiveRelativeByte": receive_offset,
        "stateStoreRelativeByte": store_offset,
    }


def ordered_causality_for_case(case: dict[str, Any], movement_summary: dict[str, Any]) -> dict[str, Any]:
    artifact_data = movement_state.state_delta.read_json(Path(case["path"]))
    observer = movement_state.state_delta.object_at(artifact_data, "cdbObserver")
    result = movement_state.state_delta.object_at(observer, "result")
    log_path = Path(str(result.get("logPath") or observer.get("logPath") or ""))
    require(log_path.is_file(), f"{case['caseId']} CDB log is missing")
    windows = movement_state.state_delta.sequence_windows_from_artifact(artifact_data, log_path)
    require(set(windows) == {1, 2, 3, 4}, f"{case['caseId']} does not have the required wait/Q/wait/E CDB windows")
    return {
        "clockModel": "cdb-byte-window-ordered-correlation",
        "wallClockLatencyProven": False,
        "q": ordered_causality_window(
            case_id=f"{case['caseId']} Q/P0",
            window_text=windows[2][2],
            state=movement_summary["q"],
            input_device=0,
            controller_configuration=int(case["controllerConfiguration"]),
        ),
        "e": ordered_causality_window(
            case_id=f"{case['caseId']} E/P1",
            window_text=windows[4][2],
            state=movement_summary["e"],
            input_device=1,
            controller_configuration=int(case["controllerConfiguration"]),
        ),
    }


def validate_movement_case(case: dict[str, Any]) -> dict[str, Any]:
    summary = movement_state.validate_artifact(
        Path(case["path"]),
        min_capture_count=5,
        min_render_samples=2,
        expected_controller_configuration=int(case["controllerConfiguration"]),
        expected_qe_proof_lever=str(case["proofLever"]),
    )
    q = public_state_window(summary["q"])
    e = public_state_window(summary["e"])
    require(q["inputDevice"] == 0, f"{case['caseId']} Q did not route to inputDevice0")
    require(e["inputDevice"] == 1, f"{case['caseId']} E did not route to inputDevice1")
    require(q["button31ReceiveRows"] > 0 and e["button31ReceiveRows"] > 0, f"{case['caseId']} has no button-31 receive rows")
    require(q["forwardStateStoreRows"] > 0 and e["forwardStateStoreRows"] > 0, f"{case['caseId']} has no Forward state-store rows")
    require(q["targetDiffersFromAdjacentBaseline"] is True, f"{case['caseId']} Q target did not differ from baseline")
    require(e["targetDiffersFromAdjacentBaseline"] is True, f"{case['caseId']} E target did not differ from baseline")
    ordered = ordered_causality_for_case(case, summary)
    return {
        "caseId": case["caseId"],
        "controllerConfiguration": summary["controllerConfiguration"],
        "proofLever": summary["proofLever"],
        "captureCount": summary["captureCount"],
        "visualCaptureCount": summary["visualCaptureCount"],
        "orderedCausality": ordered,
        "q": q,
        "e": e,
    }


def public_visible_window(row: dict[str, Any]) -> dict[str, Any]:
    state = public_state_window(row["state"])
    return {
        "state": state,
        "baselineVisualChangedRatio": row["baselineVisualDelta"]["changedRatio"],
        "targetVisualChangedRatio": row["targetVisualDelta"]["changedRatio"],
        "nonTargetVisualChangedRatio": row["nonTargetVisualDelta"]["changedRatio"],
    }


def validate_visible_case(case: dict[str, Any]) -> dict[str, Any]:
    summary = visible_movement.validate_artifact(
        Path(case["path"]),
        min_capture_count=5,
        min_render_samples=2,
        pixel_threshold=16,
        min_target_changed_ratio=0.002,
        min_target_to_baseline_ratio=1.25,
        min_target_to_nontarget_ratio=1.05,
        expected_controller_configuration=int(case["controllerConfiguration"]),
        expected_qe_proof_lever=str(case["proofLever"]),
    )
    return {
        "caseId": case["caseId"],
        "controllerConfiguration": summary["controllerConfiguration"],
        "proofLever": summary["proofLever"],
        "q": public_visible_window(summary["q"]),
        "e": public_visible_window(summary["e"]),
    }


def validate_contract(
    movement_cases: tuple[dict[str, Any], ...] = MOVEMENT_CASES,
    visible_cases: tuple[dict[str, Any], ...] = VISIBLE_CASES,
) -> dict[str, Any]:
    movement = [validate_movement_case(case) for case in movement_cases]
    visible = [validate_visible_case(case) for case in visible_cases]
    movement_configs = sorted({row["controllerConfiguration"] for row in movement})
    visible_configs = sorted({row["controllerConfiguration"] for row in visible})
    require(movement_configs == [1, 2, 3, 4], f"movement-state configs were {movement_configs}, expected [1, 2, 3, 4]")
    require(visible_configs == [1, 2], f"visible configs were {visible_configs}, expected [1, 2]")
    require(len(movement) == 7, "expected seven accepted movement-state causality artifacts")
    require(len(visible) == 4, "expected four accepted visible movement artifacts")
    return {
        "schema": EXPECTED_SCHEMA,
        "movementStateCausalityArtifactCount": len(movement),
        "movementStateControllerConfigurations": movement_configs,
        "visibleMovementCausalityArtifactCount": len(visible),
        "visibleMovementControllerConfigurations": visible_configs,
        "waitWindowsClean": True,
        "inputWindowButton31ReceiveRowsPositive": True,
        "inputWindowForwardStateStoreRowsPositive": True,
        "inputWindowOrderedSendReceiveStateStore": True,
        "clockModel": "cdb-byte-window-ordered-correlation",
        "wallClockLatencyProven": False,
        "movementStateTargetDiffersFromAdjacentBaseline": True,
        "visibleSubsetOnly": True,
        "newBeaLaunchCount": 0,
        "cdbAttachCount": 0,
        "gameInputSentByNSlotScheduler": False,
        "hostHelperInputSent": False,
        "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
        "metadataOnlySlots": ["P3", "P4"],
        "rejectedGameplayRouteSlots": ["P3", "P4"],
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "controlFeelImprovementProof": False,
        "physicalGamepadProof": False,
        "claimBoundary": (
            "This contract revalidates existing ignored exact-PID level-850 copied-runtime artifacts and proves a "
            "bounded keyboard-input-to-CDB-state/render-window causality chain for Movement/Forward across controller "
            "configs 1-4, with a stricter visible movement subset for configs 1-2. It does not launch BEA, mutate "
            "Ghidra, mutate the installed game, prove improved control feel, prove physical gamepad behavior, prove "
            "true online multiplayer, prove active P3/P4 original-binary gameplay, or prove rebuild/no-noticeable-difference parity."
        ),
        "movementStateCases": movement,
        "visibleMovementCases": visible,
    }


def pad_fixture_captures(path: Path, minimum: int = 5) -> None:
    artifact_data = json.loads(path.read_text(encoding="utf-8"))
    captures = artifact_data.get("captures")
    if not isinstance(captures, list) or not captures:
        return
    while len(captures) < minimum:
        captures.append(dict(captures[-1]))
    path.write_text(json.dumps(artifact_data), encoding="utf-8")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        movement_cases: list[dict[str, Any]] = []
        visible_cases: list[dict[str, Any]] = []
        for config in (1, 2, 3, 4):
            proof = "input-isolation-forward-qe" if config != 2 else "config2-census-movement-forward-qe"
            (root / f"movement-{config}").mkdir(parents=True, exist_ok=True)
            path = movement_state.state_delta.make_artifact(root / f"movement-{config}", controller_configuration=config, qe_proof_lever=proof)
            movement_state.inject_render_rows(path)
            pad_fixture_captures(path)
            movement_cases.append({"caseId": f"movement-{config}", "controllerConfiguration": config, "proofLever": proof, "path": path})
        for config in (1, 2):
            proof = "input-isolation-forward-qe" if config == 1 else "config2-census-movement-forward-qe"
            (root / f"visible-{config}").mkdir(parents=True, exist_ok=True)
            path = visible_movement.make_visible_fixture(root / f"visible-{config}", controller_configuration=config, qe_proof_lever=proof)
            visible_cases.append({"caseId": f"visible-{config}", "controllerConfiguration": config, "proofLever": proof, "path": path})
        movement_cases.extend(movement_cases[:3])
        visible_cases.extend(visible_cases[:2])
        summary = validate_contract(tuple(movement_cases), tuple(visible_cases))
        require(summary["movementStateControllerConfigurations"] == [1, 2, 3, 4], "self-test movement configs missing")
        require(summary["visibleMovementControllerConfigurations"] == [1, 2], "self-test visible configs missing")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "movement-1").mkdir(parents=True, exist_ok=True)
        path = movement_state.state_delta.make_artifact(root / "movement-1", controller_configuration=1, qe_proof_lever="input-isolation-forward-qe")
        movement_state.inject_render_rows(path, collapse_q=True)
        pad_fixture_captures(path)
        try:
            validate_contract(
                ({"caseId": "bad", "controllerConfiguration": 1, "proofLever": "input-isolation-forward-qe", "path": path},) * 7,
                tuple(),
            )
        except (ControlCausalityContractError, movement_state.MovementStateDeltaError):
            pass
        else:
            raise ControlCausalityContractError("self-test expected collapsed Q movement-state artifact to fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate the default accepted artifact set.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI control causality contract checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("--check or --self-test is required")
    print(json.dumps(validate_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        ControlCausalityContractError,
        movement_state.MovementStateDeltaError,
        movement_state.state_delta.ArtifactError,
        visible_movement.VisibleMovementDeltaError,
    ) as exc:
        print(f"WinUI control causality contract check: FAIL: {exc}")
        raise SystemExit(2)
