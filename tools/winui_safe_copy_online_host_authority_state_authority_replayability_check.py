#!/usr/bin/env python3
"""Validate replayability for host-authority state-authority observer proofs."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_state_authority_observer_check as observer


EXPECTED_SCHEMA = "winui-original-binary-host-authority-state-authority-replayability.v1"
EXPECTED_PROTOCOL = "host-authority-state-authority-replayability.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-state-authority-replayability"
EXPECTED_HELPER_VERSION = "host-authority-state-authority-replayability.v1"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_state_authority_replayability_check.py --self-test"
EXPECTED_SCOPE = "single-copied-host-exact-pid-state-graph"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_REJECTED_SLOTS = ["P3", "P4"]
EXPECTED_SEQUENCES = ["wait:300", "down:Q,wait:500,up:Q", "wait:300", "down:E,wait:500,up:E"]


class HostAuthorityStateAuthorityReplayabilityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityStateAuthorityReplayabilityError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    item = value.get(key)
    require(isinstance(item, dict), f"missing object field: {key}")
    return item


def runtime_process_and_log(runtime_path: Path) -> tuple[Any, str]:
    artifact = observer.read_json(runtime_path)
    launch = artifact.get("launch") if isinstance(artifact.get("launch"), dict) else {}
    cdb = artifact.get("cdbObserver") if isinstance(artifact.get("cdbObserver"), dict) else {}
    result = cdb.get("result") if isinstance(cdb.get("result"), dict) else {}
    process_id = launch.get("processId")
    log_path = str(result.get("logPath") or cdb.get("logPath") or "")
    require(process_id is not None, f"{runtime_path} is missing launch.processId")
    require(log_path, f"{runtime_path} is missing CDB log path")
    return process_id, log_path


def pointer_tuple(summary: dict[str, Any]) -> tuple[Any, ...]:
    host_graph = object_at(summary, "hostGraph")
    q_route = object_at(object_at(summary, "routeAuthority"), "P1/Q")
    e_route = object_at(object_at(summary, "routeAuthority"), "P2/E")
    return (
        host_graph.get("p1Player"),
        host_graph.get("p2Player"),
        q_route.get("controller"),
        e_route.get("controller"),
        host_graph.get("p1BattleEngine"),
        host_graph.get("p2BattleEngine"),
        host_graph.get("p1Walker"),
        host_graph.get("p2Walker"),
    )


def require_route(summary: dict[str, Any], route_name: str, expected_input_device: int) -> dict[str, Any]:
    route = object_at(object_at(summary, "routeAuthority"), route_name)
    require(route.get("route") == route_name, f"{route_name} route label mismatch")
    require(route.get("inputDevice") == expected_input_device, f"{route_name} input-device mismatch")
    require(int(route.get("button31ReceiveRows", 0)) > 0, f"{route_name} missing button-31 receive rows")
    require(int(route.get("forwardStateStoreRows", 0)) > 0, f"{route_name} missing forward state-store rows")
    require(route.get("observedVectorDelta") is True, f"{route_name} missing vector delta")
    require(route.get("targetPositionChanged") is True, f"{route_name} missing position delta")
    require(route.get("targetVelocityChanged") is True, f"{route_name} missing velocity delta")
    require(route.get("targetDiffersFromAdjacentBaseline") is True, f"{route_name} missing adjacent-baseline delta")
    return route


def observer_details(path: Path) -> dict[str, Any]:
    resolved = observer.require_private_proof_path(path)
    summary = observer.validate_state_authority_proof(resolved)
    proof = observer.read_json(resolved)
    source_bridge = observer.require_private_proof_path(Path(str(proof.get("sourceBridgeProof", ""))))
    bridge_summary, _bridge_proof, runtime_path, nslot_path = observer.resolve_bridge_paths(source_bridge)
    process_id, cdb_log_path = runtime_process_and_log(runtime_path)

    require(summary.get("schemaVersion") == observer.EXPECTED_SCHEMA, f"{path} observer schema mismatch")
    require(summary.get("protocolVersion") == observer.EXPECTED_PROTOCOL, f"{path} observer protocol mismatch")
    require(summary.get("hostAuthorityScope") == EXPECTED_SCOPE, f"{path} scope mismatch")
    require(summary.get("slotCapacity") == 4, f"{path} slot capacity must stay four")
    require(summary.get("acceptedSessionParticipantCount") == 4, f"{path} accepted participant count must stay four")
    require(summary.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, f"{path} active slot mismatch")
    require(summary.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, f"{path} metadata slot mismatch")
    require(summary.get("rejectedGameplayRouteSlots") == EXPECTED_REJECTED_SLOTS, f"{path} rejected slot mismatch")
    require(summary.get("derivedInputSequences") == EXPECTED_SEQUENCES, f"{path} derived input sequences mismatch")
    require(summary.get("hostHelperInputSent") is True, f"{path} host helper input must be true")
    require(summary.get("gameInputSentByNSlotScheduler") is False, f"{path} scheduler direct input must stay false")
    require(summary.get("nPlayerOriginalBinaryRuntimeProof") == 0, f"{path} N-player runtime proof must stay zero")
    require(summary.get("activeP3P4OriginalBinaryGameplayProof") is False, f"{path} P3/P4 gameplay proof must stay false")
    require(summary.get("multiHostLanProof") is False, f"{path} multi-host LAN proof must stay false")
    require(summary.get("publicMatchmakingProof") is False, f"{path} public matchmaking proof must stay false")
    require(summary.get("nativeBeaNetcodeProof") is False, f"{path} native netcode proof must stay false")
    require(summary.get("fullSessionSecurityProof") is False, f"{path} full session-security proof must stay false")
    require(summary.get("deterministicSyncProof") is False, f"{path} deterministic sync proof must stay false")
    require(summary.get("rollbackProof") is False, f"{path} rollback proof must stay false")
    require(summary.get("antiCheatProof") is False, f"{path} anti-cheat proof must stay false")
    require(summary.get("physicalGamepadProof") is False, f"{path} physical gamepad proof must stay false")
    require(summary.get("rebuildParityProof") is False, f"{path} rebuild parity proof must stay false")
    require(summary.get("noNoticeableDifferenceProof") is False, f"{path} no-noticeable-difference proof must stay false")
    require(summary.get("waitWindowsClean") is True, f"{path} wait windows must be clean")
    require(summary.get("privateProofReleaseExcludedByPolicy") is True, f"{path} private proof boundary missing")

    host_graph = object_at(summary, "hostGraph")
    require(host_graph.get("players") == 2, f"{path} host graph player count must stay two")
    require(host_graph.get("level") == 850, f"{path} host graph level must stay 850")
    require(host_graph.get("horizSplit") == 1, f"{path} host graph horizontal split mismatch")
    for key in ("distinctPlayers", "distinctBattleEngines", "distinctWalkers", "distinctControllers"):
        require(host_graph.get(key) is True, f"{path} missing host graph invariant: {key}")
    q_route = require_route(summary, "P1/Q", 0)
    e_route = require_route(summary, "P2/E", 1)

    return {
        "artifact": str(resolved),
        "sourceBridgeProof": str(source_bridge),
        "runtimeArtifact": str(runtime_path),
        "nSlotConcurrentProcessProof": str(nslot_path),
        "processId": process_id,
        "cdbLogPath": cdb_log_path,
        "summary": summary,
        "bridgeSummary": bridge_summary,
        "pointerTuple": pointer_tuple(summary),
        "qRows": {
            "button31ReceiveRows": q_route["button31ReceiveRows"],
            "forwardStateStoreRows": q_route["forwardStateStoreRows"],
        },
        "eRows": {
            "button31ReceiveRows": e_route["button31ReceiveRows"],
            "forwardStateStoreRows": e_route["forwardStateStoreRows"],
        },
    }


def validate_replayability(paths: list[Path]) -> dict[str, Any]:
    require(len(paths) >= 2, "at least two state-authority observer proofs are required")
    resolved = [observer.require_private_proof_path(path) for path in paths]
    require(len(set(resolved)) == len(resolved), "state-authority observer proof paths must be distinct")

    details = [observer_details(path) for path in resolved]
    live_hashes = [item["summary"]["liveRuntimeArtifactSha256"] for item in details]
    source_hashes = [item["summary"]["sourceBridgeProofSha256"] for item in details]
    process_ids = [item["processId"] for item in details]
    cdb_logs = [item["cdbLogPath"] for item in details]
    pointer_tuples = [item["pointerTuple"] for item in details]
    runtime_paths = [item["runtimeArtifact"] for item in details]
    bridge_paths = [item["sourceBridgeProof"] for item in details]

    require(len(set(live_hashes)) == len(live_hashes), "live runtime artifact hashes must be distinct")
    require(len(set(source_hashes)) == len(source_hashes), "source bridge proof hashes must be distinct")
    require(len(set(process_ids)) == len(process_ids), "process IDs must be distinct")
    require(len(set(cdb_logs)) == len(cdb_logs), "CDB log paths must be distinct")
    require(len(set(pointer_tuples)) == len(pointer_tuples), "runtime player/controller/BattleEngine/Walker tuples must be distinct")
    require(len(set(runtime_paths)) == len(runtime_paths), "runtime artifact paths must be distinct")
    require(len(set(bridge_paths)) == len(bridge_paths), "source bridge paths must be distinct")

    nslot_hashes = {item["summary"]["nSlotConcurrentProcessProofSha256"] for item in details}
    relay_hashes = {item["bridgeSummary"]["nSlotRelayPlanSha256"] for item in details}
    runtime_relay_hashes = {item["bridgeSummary"]["runtimeCompatibleP1P2RelayHash"] for item in details}
    require(len(nslot_hashes) == 1, "all replayability runs must use the same N-slot concurrent process proof")
    require(len(relay_hashes) == 1, "all replayability runs must use the same N-slot relay plan")
    require(len(runtime_relay_hashes) == 1, "all replayability runs must use the same runtime-compatible P1/P2 relay hash")

    artifacts = []
    for item in details:
        summary = item["summary"]
        artifacts.append(
            {
                "artifact": item["artifact"],
                "sourceBridgeProofSha256": summary["sourceBridgeProofSha256"],
                "liveRuntimeArtifactSha256": summary["liveRuntimeArtifactSha256"],
                "processId": item["processId"],
                "cdbLogPath": item["cdbLogPath"],
                "hostGraph": summary["hostGraph"],
                "qRows": item["qRows"],
                "eRows": item["eRows"],
                "visualCaptureCount": summary["visualCaptureCount"],
            }
        )

    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "protocolVersion": EXPECTED_PROTOCOL,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "claim": "repeated same-workstation single-copied-host exact-PID P1/P2 state-authority graph proof",
        "hostAuthorityScope": EXPECTED_SCOPE,
        "stateAuthorityGraphProven": True,
        "stateAuthorityReplayabilityProven": True,
        "proofCount": len(artifacts),
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
        "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
        "rejectedGameplayRouteSlots": EXPECTED_REJECTED_SLOTS,
        "maxOriginalBinaryActiveSlotsProven": 2,
        "nSlotConcurrentProcessProofSha256": next(iter(nslot_hashes)),
        "nSlotRelayPlanSha256": next(iter(relay_hashes)),
        "runtimeCompatibleP1P2RelayHash": next(iter(runtime_relay_hashes)),
        "derivedInputSequences": EXPECTED_SEQUENCES,
        "roleInvariant": "P1 -> Q -> inputDevice0/top split half; P2 -> E -> inputDevice1/bottom split half",
        "distinctLiveRuntimeArtifactHashes": True,
        "distinctSourceBridgeProofHashes": True,
        "distinctProcessIds": True,
        "distinctCdbLogs": True,
        "distinctRuntimePointerTuples": True,
        "waitWindowsClean": True,
        "hostHelperInputSent": True,
        "gameInputSentByNSlotScheduler": False,
        "visibleMovementDeltaClaim": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "beyondTwoPlayersRequiresNewProofClass": True,
        "absenceOfCurrentProofIsNotProofOfPermanentAbsence": True,
        "permanentImpossibilityClaim": False,
        "multiHostLanProof": False,
        "publicMatchmakingProof": False,
        "nativeBeaNetcodeProof": False,
        "fullSessionSecurityProof": False,
        "deterministicSyncProof": False,
        "rollbackProof": False,
        "antiCheatProof": False,
        "physicalGamepadProof": False,
        "rebuildParityProof": False,
        "noNoticeableDifferenceProof": False,
        "privateProofReleaseExcludedByPolicy": True,
        "rawPrivateProofPathPublished": False,
        "rawPrivateArtifactContentPublished": False,
        "absolutePrivatePathPublished": False,
        "releaseIncludedPrivateArtifact": False,
        "artifacts": artifacts,
        "claimBoundary": (
            "This proves replayability of the single-copied-host exact-PID P1/P2 state-authority graph across "
            "distinct copied BEA level-850/config-1 runtime artifacts. It does not prove active P3/P4 original-binary "
            "gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN "
            "play, public matchmaking, native BEA netcode, full session security, deterministic sync, rollback, "
            "anti-cheat, physical gamepad behavior, visible movement causality, rebuild parity, or no-noticeable-"
            "difference online parity."
        ),
    }


def replace_fixture_pointers(path: Path, replacements: dict[str, str]) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    observer_block = artifact["cdbObserver"]
    result = observer_block["result"]
    log_path = Path(result["logPath"])
    log_text = log_path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        log_text = log_text.replace(old, new)
    log_path.write_text(log_text, encoding="utf-8")


def set_fixture_process_id(path: Path, process_id: int) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["launch"]["processId"] = process_id
    artifact["cdbObserver"]["result"]["targetProcessId"] = process_id
    path.write_text(json.dumps(artifact), encoding="utf-8")


def make_observer_fixture(root: Path, *, distinct: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    nslot_path = observer.nslot_bridge.nslot.make_bundle_fixture(root / "nslot")
    executor_proof_path = observer.nslot_bridge.movement_bridge.make_bridge_fixture(root / "runtime")
    _executor_path, runtime_path, _delivery_path = observer.nslot_bridge.movement_bridge.resolve_executor_paths(executor_proof_path)
    if distinct:
        replace_fixture_pointers(
            runtime_path,
            {
                "04646090": "04aa0090",
                "0465d890": "04bb8890",
                "046460f0": "04aa00f0",
                "0465d8f0": "04bb88f0",
                "03867570": "07aa7570",
                "0386d570": "07bbd570",
                "04700010": "04cc0010",
                "04710010": "04dd0010",
            },
        )
        set_fixture_process_id(runtime_path, 5678)
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
            "liveRuntimeArtifact": observer.nslot_bridge.movement_bridge.executor.created_file_receipt(runtime_path),
        },
    }
    bridge_path = root / "host-authority-n-slot-runtime-bridge-proof.json"
    observer.nslot_bridge.make_live_bridge_proof(nslot_path, runtime_path, bridge_path, execution_receipt=receipt)
    output_path = root / "host-authority-state-authority-observer-proof.json"
    observer.make_state_authority_proof(bridge_path, output_path)
    return output_path


def run_self_test() -> None:
    observer.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=observer.PRIVATE_PROOF_ROOT) as tmp:
        root = Path(tmp)
        summary = validate_replayability(
            [
                make_observer_fixture(root / "first"),
                make_observer_fixture(root / "second", distinct=True),
            ]
        )
        require(summary["proofCount"] == 2, "self-test expected two replayability proofs")
        require(summary["stateAuthorityReplayabilityProven"] is True, "self-test replayability flag missing")
        require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "self-test must keep N-player proof at zero")

    with tempfile.TemporaryDirectory(dir=observer.PRIVATE_PROOF_ROOT) as tmp:
        path = make_observer_fixture(Path(tmp) / "duplicate-path")
        try:
            validate_replayability([path, path])
        except HostAuthorityStateAuthorityReplayabilityError:
            pass
        else:
            raise HostAuthorityStateAuthorityReplayabilityError("duplicate observer path should fail replayability")

    with tempfile.TemporaryDirectory(dir=observer.PRIVATE_PROOF_ROOT) as tmp:
        root = Path(tmp)
        try:
            validate_replayability([make_observer_fixture(root / "first"), make_observer_fixture(root / "second")])
        except HostAuthorityStateAuthorityReplayabilityError:
            pass
        else:
            raise HostAuthorityStateAuthorityReplayabilityError("duplicate runtime pointer tuple should fail replayability")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proofs", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority state-authority replayability checker self-test: PASS")
        return 0
    print(json.dumps(validate_replayability(args.proofs), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityStateAuthorityReplayabilityError,
        observer.HostAuthorityStateAuthorityObserverError,
        observer.nslot_bridge.HostAuthorityNSlotRuntimeBridgeError,
        observer.nslot_bridge.nslot.HostAuthorityNSlotProcessSmokeProofError,
        observer.nslot_bridge.movement_bridge.HostAuthorityRuntimeMovementBridgeError,
        observer.nslot_bridge.movement_bridge.executor.HostAuthorityRuntimeExecutorError,
        observer.state_delta.ArtifactError,
        observer.movement.MovementStateDeltaError,
    ) as exc:
        print(f"WinUI original-binary host-authority state-authority replayability check: FAIL: {exc}")
        raise SystemExit(2)
