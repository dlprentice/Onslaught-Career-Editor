#!/usr/bin/env python3
"""Validate host-authority executor proof with movement-state CDB deltas."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_movement_state_delta_check as movement
import winui_safe_copy_online_host_authority_runtime_executor_check as executor


EXPECTED_SCHEMA = "winui-original-binary-host-authority-runtime-movement-bridge.v1"
EXPECTED_PROTOCOL = "host-authority-runtime-movement-bridge.v1"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_runtime_movement_bridge_check.py --self-test"
EXPECTED_SEQUENCES = [
    "wait:300",
    "down:Q,wait:500,up:Q",
    "wait:300",
    "down:E,wait:500,up:E",
]


class HostAuthorityRuntimeMovementBridgeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityRuntimeMovementBridgeError(message)


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def resolve_executor_paths(path: Path) -> tuple[dict[str, Any], Path, Path]:
    bundle = executor.read_json(path)
    runtime_path = executor.resolve_path(path, str(bundle.get("liveRuntimeArtifact", "")))
    delivery_path = executor.resolve_path(path, str(bundle.get("runtimeDeliveryProofBundle", "")))
    return bundle, runtime_path, delivery_path


def require_movement_role(summary: dict[str, Any], key: str, role: str, input_device: int) -> dict[str, Any]:
    row = object_at(summary, key.lower())
    require(row.get("key") == key, f"{key}/{role} key mismatch")
    require(row.get("role") == role, f"{key}/{role} role mismatch")
    require(row.get("inputDevice") == input_device, f"{key}/{role} input device mismatch")
    require(row.get("routeType") == "walker-forward", f"{key}/{role} route mismatch")
    require(row.get("button31ReceiveRows", 0) > 0, f"{key}/{role} missing button-31 receive rows")
    require(row.get("forwardStateStoreRows", 0) > 0, f"{key}/{role} missing forward state-store rows")
    require(row.get("stateWindowPositionTupleCount", 0) > 0, f"{key}/{role} missing state-window position rows")
    require(row.get("stateWindowVelocityTupleCount", 0) > 0, f"{key}/{role} missing state-window velocity rows")
    require(row.get("targetPositionChanged") is True, f"{key}/{role} target position did not change")
    require(row.get("targetVelocityChanged") is True, f"{key}/{role} target velocity did not change")
    require(row.get("targetDiffersFromAdjacentBaseline") is True, f"{key}/{role} did not differ from adjacent baseline")
    require(row.get("nonzeroStoredLastMoveYValues"), f"{key}/{role} missing nonzero stored last-move values")
    return row


def validate_bridge(path: Path) -> dict[str, Any]:
    executor_summary = executor.validate_executor_proof(path)
    bundle, runtime_path, delivery_path = resolve_executor_paths(path)
    delivery_summary = executor.delivery.validate_bundle(delivery_path)
    movement_summary = movement.validate_artifact(
        runtime_path,
        min_capture_count=5,
        min_render_samples=2,
        expected_controller_configuration=1,
        expected_qe_proof_lever="input-isolation-forward-qe",
    )
    execution = object_at(bundle, "execution")
    require(execution.get("derivedInputSequences") == EXPECTED_SEQUENCES, "executor derived input sequence mismatch")
    require(execution.get("runtimeInputWindowSequences") == EXPECTED_SEQUENCES, "executor runtime input sequence mismatch")
    require(execution.get("hostHelperInputSent") is True, "host-helper input must be true")
    require(execution.get("gameInputSentByScheduler") is False, "scheduler direct game input must be false")
    require(execution.get("deliveredOriginalBinaryCommandCount") == 2, "expected two delivered original-binary commands")
    require(execution.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")

    runtime_players = object_at(delivery_summary, "runtimePlayers")
    require(runtime_players.get("P1") == movement_summary["p0"], "P1 runtime player mismatch")
    require(runtime_players.get("P2") == movement_summary["p1"], "P2 runtime player mismatch")
    require(movement_summary["visualCaptureCount"] == executor_summary["visualCaptureCount"], "visual capture count mismatch")

    q = require_movement_role(movement_summary, "Q", "P0", 0)
    e = require_movement_role(movement_summary, "E", "P1", 1)

    for key in (
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "nativeBeaNetcodeClaim",
        "deterministicSyncClaim",
        "rollbackClaim",
        "antiCheatClaim",
        "physicalGamepadClaim",
        "rebuildParityClaim",
        "noNoticeableDifferenceClaim",
    ):
        require(execution.get(key) is False, f"executor overclaim must be false: {key}")

    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "protocolVersion": EXPECTED_PROTOCOL,
        "artifact": str(path),
        "liveRuntimeArtifact": str(runtime_path),
        "runtimeDeliveryProofBundle": str(delivery_path),
        "claim": "relay-plan-driven host-authority runtime executor with exact-PID movement-state deltas",
        "derivedInputSequences": executor_summary["derivedInputSequences"],
        "hostAuthorityRelayPlanSha256": executor_summary["hostAuthorityRelayPlanSha256"],
        "visualCaptureCount": executor_summary["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": executor_summary["deliveredOriginalBinaryCommandCount"],
        "nPlayerOriginalBinaryRuntimeProof": executor_summary["nPlayerOriginalBinaryRuntimeProof"],
        "runtimePlayers": {
            "P1": runtime_players["P1"],
            "P2": runtime_players["P2"],
        },
        "movementState": {
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
        },
        "visibleMovementDeltaClaim": False,
        "claimBoundary": (
            "This proves the accepted same-workstation host-authority P1/P2 relay plan drove one copied "
            "level-850/config-1 BEA host through the hardened executor and that exact-PID CDB render windows "
            "show matching P0/P1 movement-state deltas against adjacent no-input baselines. It does not prove "
            "visible movement causality, improved control feel, physical gamepad behavior, multi-host LAN play, "
            "public matchmaking, native BEA netcode, active P3/P4 gameplay, deterministic sync, rollback, "
            "anti-cheat, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_bridge_fixture(root: Path, *, collapse_q: bool = False) -> Path:
    proof_path = executor.make_executor_fixture(root)
    bundle, runtime_path, delivery_path = resolve_executor_paths(proof_path)
    host_path = executor.resolve_path(proof_path, str(bundle.get("hostAuthorityTwoClientProofBundle", "")))
    movement.inject_render_rows(runtime_path, collapse_q=collapse_q)
    runtime = executor.delivery.state_delta.read_json(runtime_path)
    captures = runtime.get("captures")
    require(isinstance(captures, list) and captures, "fixture runtime artifact must contain captures")
    while len(captures) < 5:
        captures.append(dict(captures[0]))
    runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
    executor.delivery.build_bundle(host_path, runtime_path, delivery_path)
    executor.make_executor_proof(host_path, runtime_path, delivery_path, proof_path)
    return proof_path


def self_test() -> None:
    executor.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=executor.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_bridge(make_bridge_fixture(Path(tmp)))
        require(summary["deliveredOriginalBinaryCommandCount"] == 2, "fixture must deliver two commands")
        require(summary["movementState"]["Q"]["targetPositionChanged"] is True, "fixture Q movement-state proof missing")
        require(summary["movementState"]["E"]["targetPositionChanged"] is True, "fixture E movement-state proof missing")

    with tempfile.TemporaryDirectory(dir=executor.PRIVATE_PROOF_ROOT) as tmp:
        try:
            validate_bridge(make_bridge_fixture(Path(tmp), collapse_q=True))
        except (HostAuthorityRuntimeMovementBridgeError, movement.MovementStateDeltaError):
            pass
        else:
            raise HostAuthorityRuntimeMovementBridgeError("collapsed Q movement-state bridge should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary host-authority runtime movement bridge checker self-test: PASS")
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test is used")
    print(json.dumps(validate_bridge(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityRuntimeMovementBridgeError,
        executor.HostAuthorityRuntimeExecutorError,
        executor.delivery.HostAuthorityRuntimeDeliveryError,
        executor.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor.delivery.host.remote.PrivateRemoteClientSmokeProofError,
        executor.delivery.host.remote.lan.PrivateTransportSmokeProofError,
        executor.delivery.host.remote.lan.delivery.PrivateRelayDeliveryProofError,
        executor.delivery.host.remote.lan.delivery.relay.RelayProofError,
        executor.delivery.host.remote.lan.delivery.loopback.LoopbackProofError,
        executor.delivery.state_delta.ArtifactError,
        executor.delivery.nslot.NSlotSessionSchemaError,
        movement.MovementStateDeltaError,
        movement.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary host-authority runtime movement bridge check: FAIL: {exc}")
        raise SystemExit(2)
