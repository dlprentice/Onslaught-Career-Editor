#!/usr/bin/env python3
"""Validate N-slot host-authority concurrency bridged to copied-runtime P1/P2 state."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_n_slot_concurrent_process_smoke_check as nslot
import winui_safe_copy_online_host_authority_runtime_movement_bridge_check as movement_bridge


EXPECTED_SCHEMA = "winui-original-binary-host-authority-n-slot-runtime-bridge.v1"
EXPECTED_PROTOCOL = "host-authority-n-slot-runtime-bridge.v1"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check.py --self-test"
EXPECTED_HELPER = "winui-original-binary-host-authority-n-slot-runtime-bridge"
EXPECTED_HELPER_VERSION = "host-authority-n-slot-runtime-bridge.v1"
EXPECTED_EXECUTION_MODE = "n-slot-concurrent-relay-derived-safe-copy-runtime-state-observer"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_SEQUENCES = [
    "wait:300",
    "down:Q,wait:500,up:Q",
    "wait:300",
    "down:E,wait:500,up:E",
]


class HostAuthorityNSlotRuntimeBridgeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityNSlotRuntimeBridgeError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def resolve_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = bundle_path.parent / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"referenced file is missing: {candidate}")
    return candidate


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def require_common_nslot_summary(nslot_summary: dict[str, Any]) -> None:
    require(nslot_summary["slotCapacity"] == 4, "N-slot bridge must retain slotCapacity=4")
    require(nslot_summary["acceptedSessionParticipantCount"] == 4, "N-slot bridge must retain four participants")
    require(nslot_summary["acceptedOriginalBinaryGameplaySlots"] == EXPECTED_ACTIVE_SLOTS, "runtime-active slots must stay P1/P2")
    require(nslot_summary["metadataOnlySlots"] == EXPECTED_METADATA_SLOTS, "P3/P4 must stay metadata-only")
    require(nslot_summary["rejectedGameplayRouteSlots"] == EXPECTED_METADATA_SLOTS, "P3/P4 gameplay routes must stay rejected")
    require(nslot_summary["deterministicOriginalBinaryRelayOrder"] == EXPECTED_ACTIVE_SLOTS, "runtime relay order must stay P1/P2")
    require(nslot_summary["acceptedOriginalBinaryGameplayCommandCount"] == 2, "expected two original-binary-compatible commands")
    require(nslot_summary["rejectedOriginalBinaryGameplayCommandCount"] == 2, "expected two rejected P3/P4 gameplay commands")
    require(nslot_summary["processConcurrencyModel"] == "barrier-concurrent-client-processes", "N-slot process proof must be concurrent/barrier")
    require(nslot_summary["simultaneousClientProcessesProven"] == 4, "N-slot process proof must show four client processes")
    require(nslot_summary["maxSimultaneousSocketConnectionsProven"] == 4, "N-slot process proof must show four socket connections")
    require(nslot_summary["privateLanReachableDuringRun"] is True, "private LAN reachability boundary must be retained")
    require(nslot_summary["foreignPeersRejectedAfterAccept"] is True, "foreign peer rejection boundary must be retained")
    require(nslot_summary["sameWorkstationClientProcessesOnly"] is True, "same-workstation client-process boundary must be retained")
    require(nslot_summary["sameWorkstationNetworkOnly"] is False, "bridge must not claim same-workstation-only networking")
    require(nslot_summary["securityProofScope"] == "minimal-smoke-hmac-envelope-not-full-session-security-proof", "security scope must stay bounded")
    require(nslot_summary["gameInputSentByNSlotScheduler"] is False, "N-slot scheduler must not claim direct game input")
    require(nslot_summary["hostHelperInputSent"] is False, "N-slot process smoke must not claim host-helper input")
    require(nslot_summary["newBeaLaunchCount"] == 0, "N-slot process smoke must not add a BEA launch")
    require(nslot_summary["cdbAttachCount"] == 0, "N-slot process smoke must not add a CDB attach")
    require(nslot_summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "N-player runtime proof must remain zero")
    require(nslot_summary["activeP3P4OriginalBinaryGameplayProof"] is False, "P3/P4 gameplay proof must stay false")
    require(nslot_summary["permanentImpossibilityClaim"] is False, "bridge must not claim permanent impossibility")


def relay_sequences_from_nslot(bundle: dict[str, Any]) -> list[str]:
    scheduler = object_at(bundle, "hostAuthorityNSlotScheduler")
    require(scheduler.get("deterministicOriginalBinaryRelayOrder") == EXPECTED_ACTIVE_SLOTS, "N-slot relay order must be P1/P2")
    relay_plan = scheduler.get("relayPlan")
    require(isinstance(relay_plan, list), "N-slot relay plan must be a list")
    sequences = [str(row.get("mappedInputSequence") or "") for row in relay_plan if isinstance(row, dict)]
    require(sequences == EXPECTED_SEQUENCES[1::2], "N-slot P1/P2 mapped input sequences mismatch")
    return EXPECTED_SEQUENCES


def runtime_input_window_sequences(runtime_path: Path) -> list[str]:
    return movement_bridge.executor.runtime_input_window_sequences(runtime_path)


def validate_movement_runtime(runtime_path: Path) -> dict[str, Any]:
    return movement_bridge.movement.validate_artifact(
        runtime_path,
        min_capture_count=5,
        min_render_samples=2,
        expected_controller_configuration=1,
        expected_qe_proof_lever="input-isolation-forward-qe",
    )


def require_movement_summary(movement_summary: dict[str, Any], visual_capture_count: int | None = None) -> dict[str, Any]:
    if visual_capture_count is not None:
        require(movement_summary["visualCaptureCount"] == visual_capture_count, "visual capture count mismatch")
    require(movement_summary["p0"], "movement summary missing P1/P0 pointer")
    require(movement_summary["p1"], "movement summary missing P2/P1 pointer")
    q = object_at(movement_summary, "q")
    e = object_at(movement_summary, "e")
    require(q["inputDevice"] == 0, "Q route must stay inputDevice0/P1")
    require(e["inputDevice"] == 1, "E route must stay inputDevice1/P2")
    for key, row in (("Q", q), ("E", e)):
        require(row["button31ReceiveRows"] > 0, f"{key} route missing button-31 receive rows")
        require(row["forwardStateStoreRows"] > 0, f"{key} route missing forward state-store rows")
        require(row["targetPositionChanged"] is True, f"{key} target position must change")
        require(row["targetVelocityChanged"] is True, f"{key} target velocity must change")
        require(row["targetDiffersFromAdjacentBaseline"] is True, f"{key} target must differ from baseline")
    return {
        "Q": {
            "player": q["player"],
            "inputDevice": q["inputDevice"],
            "button31ReceiveRows": q["button31ReceiveRows"],
            "forwardStateStoreRows": q["forwardStateStoreRows"],
            "baselineRenderSamples": q["baselineRenderSamples"],
            "targetRenderSamples": q["targetRenderSamples"],
            "targetPositionChanged": q["targetPositionChanged"],
            "targetVelocityChanged": q["targetVelocityChanged"],
            "targetDiffersFromAdjacentBaseline": q["targetDiffersFromAdjacentBaseline"],
        },
        "E": {
            "player": e["player"],
            "inputDevice": e["inputDevice"],
            "button31ReceiveRows": e["button31ReceiveRows"],
            "forwardStateStoreRows": e["forwardStateStoreRows"],
            "baselineRenderSamples": e["baselineRenderSamples"],
            "targetRenderSamples": e["targetRenderSamples"],
            "targetPositionChanged": e["targetPositionChanged"],
            "targetVelocityChanged": e["targetVelocityChanged"],
            "targetDiffersFromAdjacentBaseline": e["targetDiffersFromAdjacentBaseline"],
        },
    }


def validate_bridge(nslot_path: Path, runtime_movement_path: Path) -> dict[str, Any]:
    nslot_summary = nslot.validate_bundle(nslot_path)
    runtime_summary = movement_bridge.validate_bridge(runtime_movement_path)

    require_common_nslot_summary(nslot_summary)
    require(
        nslot_summary["runtimeCompatibleP1P2RelayHash"] == runtime_summary["hostAuthorityRelayPlanSha256"],
        "N-slot runtime-compatible P1/P2 relay hash must match runtime movement bridge relay hash",
    )
    require(runtime_summary["deliveredOriginalBinaryCommandCount"] == 2, "runtime bridge must deliver two P1/P2 commands")
    require(runtime_summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "runtime bridge must not become N-player proof")
    require(runtime_summary["visibleMovementDeltaClaim"] is False, "visible movement causality must remain unclaimed")
    require(sorted(runtime_summary["runtimePlayers"]) == EXPECTED_ACTIVE_SLOTS, "runtime bridge must expose P1/P2 players only")
    movement_state = object_at(runtime_summary, "movementState")
    require(sorted(movement_state) == ["E", "Q"], "runtime movement bridge must cover Q/E only")
    require(movement_state["Q"]["inputDevice"] == 0, "Q route must stay inputDevice0/P1")
    require(movement_state["E"]["inputDevice"] == 1, "E route must stay inputDevice1/P2")
    for key in ("Q", "E"):
        require(movement_state[key]["targetPositionChanged"] is True, f"{key} target position must change")
        require(movement_state[key]["targetVelocityChanged"] is True, f"{key} target velocity must change")
        require(movement_state[key]["targetDiffersFromAdjacentBaseline"] is True, f"{key} target must differ from baseline")

    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "protocolVersion": EXPECTED_PROTOCOL,
        "nSlotConcurrentProcessProof": str(nslot_path),
        "runtimeMovementBridgeProof": str(runtime_movement_path),
        "claim": "concurrent four-client N-slot process proof bridged to copied-runtime P1/P2 movement-state proof",
        "slotCapacity": nslot_summary["slotCapacity"],
        "acceptedSessionParticipantCount": nslot_summary["acceptedSessionParticipantCount"],
        "processConcurrencyModel": nslot_summary["processConcurrencyModel"],
        "simultaneousClientProcessesProven": nslot_summary["simultaneousClientProcessesProven"],
        "maxSimultaneousSocketConnectionsProven": nslot_summary["maxSimultaneousSocketConnectionsProven"],
        "privateLanReachableDuringRun": nslot_summary["privateLanReachableDuringRun"],
        "foreignPeersRejectedAfterAccept": nslot_summary["foreignPeersRejectedAfterAccept"],
        "sameWorkstationClientProcessesOnly": nslot_summary["sameWorkstationClientProcessesOnly"],
        "sameWorkstationNetworkOnly": nslot_summary["sameWorkstationNetworkOnly"],
        "securityProofScope": nslot_summary["securityProofScope"],
        "acceptedOriginalBinaryGameplaySlots": nslot_summary["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": nslot_summary["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": nslot_summary["rejectedGameplayRouteSlots"],
        "relayHashMatched": True,
        "nSlotRelayPlanSha256": nslot_summary["relayPlanSha256"],
        "runtimeCompatibleP1P2RelayHash": nslot_summary["runtimeCompatibleP1P2RelayHash"],
        "runtimeMovementBridgeRelayHash": runtime_summary["hostAuthorityRelayPlanSha256"],
        "runtimePlayers": runtime_summary["runtimePlayers"],
        "movementState": runtime_summary["movementState"],
        "deliveredOriginalBinaryCommandCount": runtime_summary["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": True,
        "gameInputSentByNSlotScheduler": False,
        "newBeaLaunchCount": 0,
        "cdbAttachCountFromNSlotProof": 0,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "visibleMovementDeltaClaim": False,
        "multiHostLanProof": False,
        "publicMatchmakingProof": False,
        "nativeBeaNetcodeProof": False,
        "deterministicSyncProof": False,
        "rollbackProof": False,
        "antiCheatProof": False,
        "rebuildParityProof": False,
        "claimBoundary": (
            "This bridges the accepted same-workstation-client/private-interface four-client N-slot concurrent process "
            "proof to the accepted copied-runtime P1/P2 movement-state bridge by matching the runtime-compatible P1/P2 "
            "relay hash. It proves process-layer concurrency plus P1/P2 host-helper state delivery are compatible in the "
            "current proof chain. It does not prove multi-host LAN, public matchmaking, native BEA netcode, active P3/P4 "
            "original-binary gameplay, more than two original-binary runtime players, full session-security coverage, "
            "deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def live_smoke_command(sequences: list[str], *, artifact_root: Path, exe_override: Path) -> list[str]:
    command = [
        sys.executable,
        str(movement_bridge.executor.LIVE_SMOKE),
        "--exe-override",
        str(exe_override),
        "--artifact-root",
        str(artifact_root),
        "--timeout-seconds",
        "25",
        "--pre-input-capture-count",
        "1",
        "--focus-before-pre-input-capture",
        "--capture-count",
        "2",
        "--capture-after-each-input-sequence",
        "--after-input-capture-delay-ms",
        "500",
        "--capture-interval-seconds",
        "1",
        "--post-window-delay-seconds",
        "2",
    ]
    for sequence in sequences:
        command.extend(["--input-sequence", sequence])
    command.extend(
        [
            "--level-id",
            "850",
            "--controller-configuration",
            "1",
            "--persist-controller-config-in-options",
            "--bind-forward-qe-for-input-isolation",
            "--enable-cdb-observer",
            "--arm-cdb-observer",
            movement_bridge.executor.delivery.state_delta.CDB_OBSERVER_ARM_PHRASE
            if hasattr(movement_bridge.executor.delivery.state_delta, "CDB_OBSERVER_ARM_PHRASE")
            else "ATTACH CDB TO SAFE COPY BEA",
            "--cdb-command-file",
            r"tools\runtime-probes\local-multiplayer-level850-input-state-delta-observer.cdb.txt",
            "--cdb-log-ready-timeout-ms",
            "30000",
            "--cdb-post-attach-wait-seconds",
            "2",
            "--arm-live-bea",
            "LAUNCH SAFE COPY BEA",
        ]
    )
    return command


def make_live_bridge_proof(
    nslot_path: Path,
    runtime_path: Path,
    output_path: Path,
    *,
    execution_receipt: dict[str, Any],
) -> dict[str, Any]:
    nslot_path = nslot_path.resolve()
    runtime_path = runtime_path.resolve()
    output_path = output_path.resolve()
    movement_bridge.executor.require_private_proof_path(output_path)
    nslot_summary = nslot.validate_bundle(nslot_path)
    require_common_nslot_summary(nslot_summary)
    nslot_bundle = nslot.read_json(nslot_path)
    expected_sequences = relay_sequences_from_nslot(nslot_bundle)
    require(runtime_input_window_sequences(runtime_path) == expected_sequences, "runtime input windows were not derived from N-slot relay plan")
    movement_summary = validate_movement_runtime(runtime_path)
    movement_state = require_movement_summary(movement_summary)
    proof = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "nSlotConcurrentProcessProof": relative_path(output_path.parent, nslot_path),
        "nSlotConcurrentProcessProofSha256": movement_bridge.executor.sha256_file(nslot_path),
        "liveRuntimeArtifact": relative_path(output_path.parent, runtime_path),
        "liveRuntimeArtifactSha256": movement_bridge.executor.sha256_file(runtime_path),
        "execution": {
            "executionMode": EXPECTED_EXECUTION_MODE,
            "nSlotRelayPlanSha256": nslot_summary["relayPlanSha256"],
            "runtimeCompatibleP1P2RelayHash": nslot_summary["runtimeCompatibleP1P2RelayHash"],
            "derivedInputSequences": expected_sequences,
            "runtimeInputWindowSequences": runtime_input_window_sequences(runtime_path),
            "executionReceipt": execution_receipt,
            "generatedByLiveSmokeHarness": True,
            "safeCopyLaunchLevel": 850,
            "controllerConfiguration": 1,
            "visualCaptureCount": movement_summary["visualCaptureCount"],
            "runtimePlayers": {"P1": movement_summary["p0"], "P2": movement_summary["p1"]},
            "movementState": movement_state,
            "deliveredOriginalBinaryCommandCount": 2,
            "hostHelperInputSent": True,
            "gameInputSentByNSlotScheduler": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "visibleMovementDeltaClaim": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "noNoticeableDifferenceClaim": False,
        },
        "claimBoundary": (
            "N-slot concurrent host-authority runtime bridge for P1/P2 only. This records that the accepted four-client "
            "concurrent N-slot process proof supplied the runtime-compatible P1/P2 relay input sequence for one safe-copy "
            "level-850/config-1 BEA host-helper run, and exact-PID CDB movement-state windows showed Q/P1 and E/P2 state "
            "deltas. P3/P4 remain metadata-only and gameplay-rejected. This does not prove active P3/P4 original-binary "
            "gameplay, more than two original-binary runtime players, multi-host LAN, public matchmaking, native BEA "
            "netcode, full session-security coverage, deterministic sync, rollback, anti-cheat, physical gamepad behavior, "
            "rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    return validate_live_bridge_proof(output_path)


def validate_live_bridge_proof(path: Path) -> dict[str, Any]:
    proof = read_json(path)
    require(proof.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected bridge schema")
    require(proof.get("generatedBy") == EXPECTED_HELPER, "unexpected bridge helper")
    require(proof.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected bridge helper version")
    require(proof.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected bridge protocol")
    nslot_path = resolve_path(path, str(proof.get("nSlotConcurrentProcessProof", "")))
    runtime_path = resolve_path(path, str(proof.get("liveRuntimeArtifact", "")))
    require(proof.get("nSlotConcurrentProcessProofSha256") == movement_bridge.executor.sha256_file(nslot_path), "N-slot proof hash mismatch")
    require(proof.get("liveRuntimeArtifactSha256") == movement_bridge.executor.sha256_file(runtime_path), "runtime artifact hash mismatch")
    nslot_summary = nslot.validate_bundle(nslot_path)
    require_common_nslot_summary(nslot_summary)
    expected_sequences = relay_sequences_from_nslot(nslot.read_json(nslot_path))
    movement_summary = validate_movement_runtime(runtime_path)
    movement_state = require_movement_summary(movement_summary)
    execution = object_at(proof, "execution")
    require(execution.get("executionMode") == EXPECTED_EXECUTION_MODE, "execution mode mismatch")
    require(execution.get("nSlotRelayPlanSha256") == nslot_summary["relayPlanSha256"], "N-slot relay hash mismatch")
    require(execution.get("runtimeCompatibleP1P2RelayHash") == nslot_summary["runtimeCompatibleP1P2RelayHash"], "runtime-compatible relay hash mismatch")
    require(execution.get("derivedInputSequences") == expected_sequences, "derived input sequences mismatch")
    require(execution.get("runtimeInputWindowSequences") == runtime_input_window_sequences(runtime_path), "runtime input sequences mismatch")
    require(execution.get("runtimeInputWindowSequences") == expected_sequences, "runtime input windows were not derived from N-slot proof")
    receipt = object_at(execution, "executionReceipt")
    require(receipt.get("mode") in {"live-nslot-runtime-bridge-subprocess", "self-test-fixture"}, "receipt mode mismatch")
    require(receipt.get("liveSmokeReturnCode") == 0, "live smoke return code must be zero")
    require(receipt.get("childEnvSensitiveKeyCount") == 0, "child env retained sensitive-looking keys")
    require(receipt.get("executorRecordsFreshSameRootArtifacts") is True, "fresh same-root runtime artifact receipt missing")
    require(execution.get("generatedByLiveSmokeHarness") is True, "live smoke harness generation must be recorded")
    require(execution.get("safeCopyLaunchLevel") == 850, "bridge must stay on level 850")
    require(execution.get("controllerConfiguration") == 1, "bridge must stay on controller config 1")
    require(execution.get("visualCaptureCount") == movement_summary["visualCaptureCount"], "visual capture count mismatch")
    require(execution.get("runtimePlayers") == {"P1": movement_summary["p0"], "P2": movement_summary["p1"]}, "runtime player pointers mismatch")
    require(execution.get("movementState") == movement_state, "movement-state summary mismatch")
    require(execution.get("deliveredOriginalBinaryCommandCount") == 2, "expected two delivered P1/P2 commands")
    require(execution.get("hostHelperInputSent") is True, "host helper input must be true")
    require(execution.get("gameInputSentByNSlotScheduler") is False, "N-slot scheduler direct game input must be false")
    require(execution.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(execution.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 runtime gameplay proof must stay false")
    require(execution.get("visibleMovementDeltaClaim") is False, "visible movement causality must remain unclaimed")
    for key in (
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "publicServerClaim",
        "nativeBeaNetcodeClaim",
        "deterministicSyncClaim",
        "rollbackClaim",
        "antiCheatClaim",
        "physicalGamepadClaim",
        "rebuildParityClaim",
        "noNoticeableDifferenceClaim",
    ):
        require(execution.get(key) is False, f"execution overclaim must be false: {key}")

    return {
        "schemaVersion": proof["schemaVersion"],
        "protocolVersion": proof["protocolVersion"],
        "artifact": str(path),
        "nSlotConcurrentProcessProof": str(nslot_path),
        "liveRuntimeArtifact": str(runtime_path),
        "claim": "fresh N-slot concurrent relay-derived copied-runtime P1/P2 movement-state proof",
        "slotCapacity": nslot_summary["slotCapacity"],
        "acceptedSessionParticipantCount": nslot_summary["acceptedSessionParticipantCount"],
        "processConcurrencyModel": nslot_summary["processConcurrencyModel"],
        "simultaneousClientProcessesProven": nslot_summary["simultaneousClientProcessesProven"],
        "maxSimultaneousSocketConnectionsProven": nslot_summary["maxSimultaneousSocketConnectionsProven"],
        "acceptedOriginalBinaryGameplaySlots": nslot_summary["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": nslot_summary["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": nslot_summary["rejectedGameplayRouteSlots"],
        "nSlotRelayPlanSha256": nslot_summary["relayPlanSha256"],
        "runtimeCompatibleP1P2RelayHash": nslot_summary["runtimeCompatibleP1P2RelayHash"],
        "derivedInputSequences": expected_sequences,
        "visualCaptureCount": movement_summary["visualCaptureCount"],
        "runtimePlayers": execution["runtimePlayers"],
        "movementState": movement_state,
        "deliveredOriginalBinaryCommandCount": execution["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": execution["hostHelperInputSent"],
        "gameInputSentByNSlotScheduler": execution["gameInputSentByNSlotScheduler"],
        "nPlayerOriginalBinaryRuntimeProof": execution["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": execution["activeP3P4OriginalBinaryGameplayProof"],
        "visibleMovementDeltaClaim": execution["visibleMovementDeltaClaim"],
        "claimBoundary": proof["claimBoundary"],
    }


def build_live_bridge(nslot_path: Path, artifact_root: Path, *, exe_override: Path) -> dict[str, Any]:
    artifact_root = movement_bridge.executor.require_private_proof_path(artifact_root)
    nslot_path = nslot_path.resolve()
    exe_override = exe_override.resolve()
    require(exe_override.is_file(), f"executable override not found: {exe_override}")
    movement_bridge.executor.require_no_bea_or_cdb_processes("before N-slot runtime bridge")
    nslot_bundle = nslot.read_json(nslot_path)
    nslot_summary = nslot.validate_bundle(nslot_path)
    require_common_nslot_summary(nslot_summary)
    sequences = relay_sequences_from_nslot(nslot_bundle)
    command = live_smoke_command(sequences, artifact_root=artifact_root, exe_override=exe_override)
    child_env = movement_bridge.executor.minimal_child_env()
    started_at = dt.datetime.now(dt.timezone.utc)
    completed = movement_bridge.executor.run_live_smoke_process(command)
    ended_at = dt.datetime.now(dt.timezone.utc)
    require(completed.returncode == 0, f"live smoke failed with {completed.returncode}: {completed.stdout}\n{completed.stderr}")
    runtime_path = artifact_root / ("live-safe-copy-runtime-" + "smoke.json")
    require(runtime_path.is_file(), f"live runtime artifact was not created: {runtime_path}")
    output_path = artifact_root / "host-authority-n-slot-runtime-bridge-proof.json"
    movement_bridge.executor.require_no_bea_or_cdb_processes("after N-slot runtime bridge")
    receipt = {
        "mode": "live-nslot-runtime-bridge-subprocess",
        "artifactRoot": str(artifact_root.resolve()),
        "startedAtUtc": started_at.isoformat(),
        "endedAtUtc": ended_at.isoformat(),
        "liveSmokeCommandSha256": movement_bridge.executor.command_hash(command),
        "liveSmokeReturnCode": completed.returncode,
        "childEnvKeyCount": len(child_env),
        "childEnvSensitiveKeyCount": len(movement_bridge.executor.sensitive_env_keys(child_env)),
        "childEnvSensitiveKeys": movement_bridge.executor.sensitive_env_keys(child_env),
        "executorRecordsFreshSameRootArtifacts": runtime_path.parent.resolve() == artifact_root.resolve(),
        "createdFiles": {
            "liveRuntimeArtifact": movement_bridge.executor.created_file_receipt(runtime_path),
        },
        "stdoutSha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderrSha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
    }
    return make_live_bridge_proof(nslot_path, runtime_path, output_path, execution_receipt=receipt)


def make_fixture(root: Path, *, hash_mismatch: bool = False) -> tuple[Path, Path]:
    nslot_path = nslot.make_bundle_fixture(root / "nslot")
    runtime_path = movement_bridge.make_bridge_fixture(root / "runtime")
    if hash_mismatch:
        bundle = read_json(nslot_path)
        bundle["hostAuthorityNSlotScheduler"]["runtimeCompatibleP1P2RelayHash"] = "0" * 64
        write_json(nslot_path, bundle)
    return nslot_path, runtime_path


def make_live_bridge_fixture(root: Path) -> Path:
    nslot_path = nslot.make_bundle_fixture(root / "nslot")
    executor_proof_path = movement_bridge.make_bridge_fixture(root / "runtime")
    _, runtime_path, _ = movement_bridge.resolve_executor_paths(executor_proof_path)
    output_path = root / "host-authority-n-slot-runtime-bridge-proof.json"
    receipt = {
        "mode": "self-test-fixture",
        "artifactRoot": str(root.resolve()),
        "liveSmokeCommandSha256": "0" * 64,
        "liveSmokeReturnCode": 0,
        "childEnvKeyCount": 0,
        "childEnvSensitiveKeyCount": 0,
        "childEnvSensitiveKeys": [],
        "executorRecordsFreshSameRootArtifacts": True,
        "createdFiles": {
            "liveRuntimeArtifact": movement_bridge.executor.created_file_receipt(runtime_path),
        },
    }
    return Path(make_live_bridge_proof(nslot_path, runtime_path, output_path, execution_receipt=receipt)["artifact"])


def self_test() -> None:
    movement_bridge.executor.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        nslot_path, runtime_path = make_fixture(Path(tmp))
        summary = validate_bridge(nslot_path, runtime_path)
        require(summary["relayHashMatched"] is True, "fixture relay hash must match")
        require(summary["simultaneousClientProcessesProven"] == 4, "fixture must prove four processes")
        live_summary = validate_live_bridge_proof(make_live_bridge_fixture(Path(tmp) / "live-bridge"))
        require(live_summary["hostHelperInputSent"] is True, "live bridge fixture must record host-helper input")

    with tempfile.TemporaryDirectory(dir=movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        nslot_path, runtime_path = make_fixture(Path(tmp), hash_mismatch=True)
        try:
            validate_bridge(nslot_path, runtime_path)
        except (HostAuthorityNSlotRuntimeBridgeError, nslot.HostAuthorityNSlotProcessSmokeProofError):
            pass
        else:
            raise HostAuthorityNSlotRuntimeBridgeError("relay hash mismatch should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("nslot_concurrent_proof", nargs="?", type=Path)
    parser.add_argument("runtime_movement_bridge_proof", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--build-live-from-nslot", type=Path, default=None)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--exe-override", type=Path, default=movement_bridge.executor.DEFAULT_EXE_OVERRIDE)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary host-authority N-slot runtime bridge checker self-test: PASS")
        return 0
    if args.build_live_from_nslot is not None:
        if args.artifact_root is None:
            raise SystemExit("--artifact-root is required with --build-live-from-nslot")
        print(json.dumps(build_live_bridge(args.build_live_from_nslot, args.artifact_root, exe_override=args.exe_override), indent=2, sort_keys=True))
        return 0
    if args.nslot_concurrent_proof is not None and args.runtime_movement_bridge_proof is None:
        print(json.dumps(validate_live_bridge_proof(args.nslot_concurrent_proof), indent=2, sort_keys=True))
        return 0
    if args.nslot_concurrent_proof is None or args.runtime_movement_bridge_proof is None:
        raise SystemExit("proof, or nslot_concurrent_proof plus runtime_movement_bridge_proof, is required unless --self-test is used")
    print(json.dumps(validate_bridge(args.nslot_concurrent_proof, args.runtime_movement_bridge_proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityNSlotRuntimeBridgeError,
        nslot.HostAuthorityNSlotProcessSmokeProofError,
        movement_bridge.HostAuthorityRuntimeMovementBridgeError,
        movement_bridge.executor.HostAuthorityRuntimeExecutorError,
        movement_bridge.executor.delivery.HostAuthorityRuntimeDeliveryError,
        movement_bridge.movement.MovementStateDeltaError,
    ) as exc:
        print(f"WinUI original-binary host-authority N-slot runtime bridge check: FAIL: {exc}")
        raise SystemExit(2)
