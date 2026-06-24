#!/usr/bin/env python3
"""Validate replayability for secure N-slot runtime executor proofs."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check as executor


EXPECTED_SCHEMA = "winui-original-binary-host-authority-secure-n-slot-runtime-executor-replayability.v1"
EXPECTED_PROTOCOL = "host-authority-secure-n-slot-runtime-executor-replayability.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-secure-n-slot-runtime-executor-replayability"
EXPECTED_HELPER_VERSION = "host-authority-secure-n-slot-runtime-executor-replayability.v1"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check.py --self-test"


class SecureNSlotRuntimeExecutorReplayabilityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecureNSlotRuntimeExecutorReplayabilityError(message)


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


def runtime_process_and_log(runtime_path: Path) -> tuple[Any, str]:
    artifact = executor.read_json(runtime_path)
    launch = artifact.get("launch") if isinstance(artifact.get("launch"), dict) else {}
    cdb = artifact.get("cdbObserver") if isinstance(artifact.get("cdbObserver"), dict) else {}
    result = cdb.get("result") if isinstance(cdb.get("result"), dict) else {}
    process_id = launch.get("processId")
    log_path = str(result.get("logPath") or cdb.get("logPath") or "")
    require(isinstance(process_id, int) and process_id > 0, f"{runtime_path} is missing launch.processId")
    require(log_path, f"{runtime_path} is missing CDB log path")
    return process_id, log_path


def execution_receipt(path: Path, proof: dict[str, Any], *, allow_fixture: bool) -> dict[str, Any]:
    execution = object_at(proof, "execution")
    receipt = object_at(execution, "executionReceipt")
    mode = receipt.get("mode")
    if allow_fixture and mode == "self-test-fixture":
        return {
            "mode": mode,
            "artifactRoot": str(receipt.get("artifactRoot") or ""),
            "startedAtUtc": "",
            "endedAtUtc": "",
            "createdLiveRuntimeArtifactPath": "",
            "createdLiveRuntimeArtifactSha256": "",
            "createdLiveRuntimeArtifactMtimeUtc": "",
        }

    require(mode == "live-secure-nslot-runtime-executor-subprocess", f"{path} must use a live executor receipt")
    require(receipt.get("liveSmokeReturnCode") == 0, f"{path} live smoke return code must be zero")
    require(receipt.get("childEnvSensitiveKeyCount") == 0, f"{path} child environment must have no sensitive keys")
    require(receipt.get("executorRecordsFreshSameRootArtifacts") is True, f"{path} must record fresh same-root artifacts")
    artifact_root = str(receipt.get("artifactRoot") or "")
    started = str(receipt.get("startedAtUtc") or "")
    ended = str(receipt.get("endedAtUtc") or "")
    require(artifact_root, f"{path} missing execution receipt artifact root")
    require(started and ended, f"{path} missing execution receipt timestamps")
    created = object_at(object_at(receipt, "createdFiles"), "liveRuntimeArtifact")
    created_path = str(created.get("path") or "")
    created_hash = str(created.get("sha256") or "")
    created_mtime = str(created.get("mtimeUtc") or "")
    require(created_path, f"{path} missing created live runtime artifact path")
    require(created_hash == str(proof.get("liveRuntimeArtifactSha256") or ""), f"{path} created runtime hash mismatch")
    require(created_mtime, f"{path} missing created runtime mtime")
    return {
        "mode": mode,
        "artifactRoot": artifact_root,
        "startedAtUtc": started,
        "endedAtUtc": ended,
        "createdLiveRuntimeArtifactPath": created_path,
        "createdLiveRuntimeArtifactSha256": created_hash,
        "createdLiveRuntimeArtifactMtimeUtc": created_mtime,
    }


def runtime_pointer_tuple(summary: dict[str, Any]) -> tuple[Any, ...]:
    runtime_players = object_at(summary, "runtimePlayers")
    movement_state = object_at(summary, "movementState")
    q = object_at(movement_state, "Q")
    e = object_at(movement_state, "E")
    return (
        runtime_players.get("P1"),
        runtime_players.get("P2"),
        q.get("player"),
        e.get("player"),
    )


def require_executor_summary(summary: dict[str, Any], path: Path) -> None:
    require(summary.get("schemaVersion") == executor.EXPECTED_SCHEMA, f"{path} executor schema mismatch")
    require(summary.get("protocolVersion") == executor.EXPECTED_PROTOCOL, f"{path} executor protocol mismatch")
    require(summary.get("receiptMode") in {"live-secure-nslot-runtime-executor-subprocess", "self-test-fixture"}, f"{path} receipt mode mismatch")
    require(summary.get("securityProofScope") == executor.security.EXPECTED_SECURITY_SCOPE, f"{path} security scope mismatch")
    require(summary.get("derivedInputSequences") == executor.EXPECTED_SEQUENCES, f"{path} derived input sequence mismatch")
    require(summary.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, f"{path} active slots mismatch")
    require(summary.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, f"{path} metadata-only slots mismatch")
    require(summary.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, f"{path} rejected route slots mismatch")
    require(summary.get("secureSessionAcceptedCommandCount") == 2, f"{path} accepted secure command count mismatch")
    require(summary.get("secureSessionMetadataRejectionCount") == 2, f"{path} secure metadata rejection count mismatch")
    require(
        summary.get("secureSessionSecurityRejectionCount") == len(executor.security.EXPECTED_SECURITY_REJECTION_CASES),
        f"{path} secure rejection count mismatch",
    )
    require(summary.get("deliveredOriginalBinaryCommandCount") == 2, f"{path} delivered command count mismatch")
    require(summary.get("hostHelperInputSent") is True, f"{path} host helper input must be true")
    require(summary.get("gameInputSentByNSlotScheduler") is False, f"{path} scheduler direct game input must stay false")
    require(summary.get("newBeaLaunchCount") == 1, f"{path} must account for one copied BEA launch")
    require(summary.get("cdbAttachCount") == 1, f"{path} must account for one CDB attach")
    require(summary.get("nPlayerOriginalBinaryRuntimeProof") == 0, f"{path} N-player runtime proof must stay zero")
    require(summary.get("activeP3P4OriginalBinaryGameplayProof") is False, f"{path} P3/P4 proof must stay false")
    require(summary.get("visibleMovementDeltaClaim") is False, f"{path} visible movement claim must stay false")


def executor_details(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    proof_path = executor.require_private_path(path, must_exist=True)
    summary = executor.validate_secure_runtime_executor_proof(proof_path, allow_fixture=allow_fixture)
    require_executor_summary(summary, proof_path)
    proof = executor.read_json(proof_path)
    session_path = executor.resolve_path(proof_path, str(proof.get("sessionSecurityProof", "")))
    runtime_path = executor.resolve_path(proof_path, str(proof.get("liveRuntimeArtifact", "")))
    process_id, cdb_log_path = runtime_process_and_log(runtime_path)
    receipt = execution_receipt(proof_path, proof, allow_fixture=allow_fixture)
    cdb_log = Path(cdb_log_path)
    require(cdb_log.is_file(), f"{proof_path} CDB log does not exist")
    return {
        "artifact": str(proof_path),
        "artifactSha256": executor.sha256_file(proof_path),
        "sessionSecurityProof": str(session_path),
        "sessionSecurityProofSha256": str(proof.get("sessionSecurityProofSha256") or ""),
        "liveRuntimeArtifact": str(runtime_path),
        "liveRuntimeArtifactSha256": str(proof.get("liveRuntimeArtifactSha256") or ""),
        "summary": summary,
        "processId": process_id,
        "cdbLogPath": cdb_log_path,
        "cdbLogSha256": executor.sha256_file(cdb_log),
        "runtimePointerTuple": runtime_pointer_tuple(summary),
        "receipt": receipt,
    }


def validate_replayability(paths: list[Path], *, allow_fixture: bool = False) -> dict[str, Any]:
    require(len(paths) >= 2, "at least two secure N-slot runtime executor proofs are required")
    resolved = [executor.require_private_path(path, must_exist=True) for path in paths]
    require(len(set(resolved)) == len(resolved), "executor proof paths must be distinct")
    details = [executor_details(path, allow_fixture=allow_fixture) for path in resolved]

    proof_hashes = [item["artifactSha256"] for item in details]
    session_hashes = [item["sessionSecurityProofSha256"] for item in details]
    live_hashes = [item["liveRuntimeArtifactSha256"] for item in details]
    runtime_paths = [item["liveRuntimeArtifact"] for item in details]
    process_ids = [item["processId"] for item in details]
    cdb_logs = [item["cdbLogPath"] for item in details]
    cdb_log_hashes = [item["cdbLogSha256"] for item in details]
    pointer_tuples = [item["runtimePointerTuple"] for item in details]
    receipt_modes = [item["receipt"]["mode"] for item in details]
    live_replayability = all(mode == "live-secure-nslot-runtime-executor-subprocess" for mode in receipt_modes) and not allow_fixture

    require(len(set(proof_hashes)) == len(proof_hashes), "executor proof hashes must be distinct")
    require(len(set(session_hashes)) == 1, "all executor proofs must use the same session-security proof hash")
    require(len(set(live_hashes)) == len(live_hashes), "live runtime artifact hashes must be distinct")
    require(len(set(runtime_paths)) == len(runtime_paths), "live runtime artifact paths must be distinct")
    require(len(set(process_ids)) == len(process_ids), "launch process IDs must be distinct")
    require(len(set(cdb_logs)) == len(cdb_logs), "CDB log paths must be distinct")
    require(len(set(cdb_log_hashes)) == len(cdb_log_hashes), "CDB log hashes must be distinct")
    require(len(set(pointer_tuples)) == len(pointer_tuples), "runtime player tuples must be distinct")
    if live_replayability:
        receipts = [item["receipt"] for item in details]
        require(len({receipt["artifactRoot"] for receipt in receipts}) == len(receipts), "live artifact roots must be distinct")
        require(len({receipt["startedAtUtc"] for receipt in receipts}) == len(receipts), "live receipt start timestamps must be distinct")
        require(len({receipt["endedAtUtc"] for receipt in receipts}) == len(receipts), "live receipt end timestamps must be distinct")
        require(len({receipt["createdLiveRuntimeArtifactPath"] for receipt in receipts}) == len(receipts), "created runtime paths must be distinct")
        require(
            len({receipt["createdLiveRuntimeArtifactMtimeUtc"] for receipt in receipts}) == len(receipts),
            "created runtime mtimes must be distinct",
        )

    relay_hashes = {item["summary"]["sessionSecurityRelayPlanSha256"] for item in details}
    runtime_relay_hashes = {item["summary"]["runtimeCompatibleP1P2RelayHash"] for item in details}
    scopes = {item["summary"]["securityProofScope"] for item in details}
    require(len(relay_hashes) == 1, "all executor proofs must use the same secure session relay plan hash")
    require(len(runtime_relay_hashes) == 1, "all executor proofs must use the same runtime-compatible P1/P2 relay hash")
    require(scopes == {executor.security.EXPECTED_SECURITY_SCOPE}, "all executor proofs must keep the same security scope")

    artifacts = []
    for item in details:
        summary = item["summary"]
        artifacts.append(
            {
                "proofOrdinal": len(artifacts) + 1,
                "artifactSha256": item["artifactSha256"],
                "sessionSecurityProofSha256": item["sessionSecurityProofSha256"],
                "liveRuntimeArtifactSha256": item["liveRuntimeArtifactSha256"],
                "receiptMode": summary["receiptMode"],
                "cdbLogSha256": item["cdbLogSha256"],
                "visualCaptureCount": summary["visualCaptureCount"],
            }
        )

    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "protocolVersion": EXPECTED_PROTOCOL,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "claim": "repeated same-workstation secure-session-derived P1/P2 copied-runtime executor proof",
        "proofCount": len(artifacts),
        "secureNSlotRuntimeExecutorReplayabilityProven": live_replayability,
        "liveReplayabilityProof": live_replayability,
        "selfTestFixtureOnly": allow_fixture,
        "securityProofScope": executor.security.EXPECTED_SECURITY_SCOPE,
        "sessionSecurityProofSha256": next(iter(session_hashes)),
        "sessionSecurityRelayPlanSha256": next(iter(relay_hashes)),
        "runtimeCompatibleP1P2RelayHash": next(iter(runtime_relay_hashes)),
        "derivedInputSequences": executor.EXPECTED_SEQUENCES,
        "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
        "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
        "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
        "secureSessionAcceptedCommandCount": 2,
        "secureSessionMetadataRejectionCount": 2,
        "secureSessionSecurityRejectionCount": len(executor.security.EXPECTED_SECURITY_REJECTION_CASES),
        "deliveredOriginalBinaryCommandCountPerProof": 2,
        "hostHelperInputSent": True,
        "gameInputSentByNSlotScheduler": False,
        "newBeaLaunchCountPerProof": 1,
        "cdbAttachCountPerProof": 1,
        "distinctLiveRuntimeArtifactHashes": True,
        "distinctRuntimeArtifactPaths": True,
        "distinctProcessIds": True,
        "distinctCdbLogs": True,
        "distinctCdbLogHashes": True,
        "distinctRuntimePointerTuples": True,
        "visibleMovementDeltaClaim": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
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
        "privateProofReleaseExcludedByPolicy": True,
        "rawPrivateProofPathPublished": False,
        "rawPrivateArtifactContentPublished": False,
        "absolutePrivatePathPublished": False,
        "releaseIncludedPrivateArtifact": False,
        "artifacts": artifacts,
        "claimBoundary": (
            "This proves repeated same-workstation secure-session-derived P1/P2 copied-runtime executor artifacts "
            "with distinct live runtime hashes, process IDs, CDB logs, runtime paths, and runtime player tuples. "
            "It does not prove visible movement causality, active P3/P4 original-binary gameplay, more-than-two "
            "original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, "
            "native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, "
            "or no-noticeable-difference online parity."
        ),
    }


def replace_fixture_pointers(path: Path, replacements: dict[str, str]) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    observer = artifact["cdbObserver"]
    result = observer["result"]
    log_path = Path(result["logPath"])
    log_text = log_path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        log_text = log_text.replace(old, new)
    log_path.write_text(log_text, encoding="utf-8")


def set_fixture_process_id(path: Path, process_id: int) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["launch"]["processId"] = process_id
    artifact["cdbObserver"]["result"]["targetProcessId"] = process_id
    path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


def make_executor_fixture(root: Path, *, distinct: bool = False, session_path: Path | None = None) -> Path:
    if session_path is None:
        session_path = root / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
        executor.security_builder.build_bundle(session_path)
    else:
        session_path = executor.require_private_path(session_path, must_exist=True)
    runtime_bridge_proof = executor.runtime_bridge.movement_bridge.make_bridge_fixture(root / "runtime")
    _, runtime_path, _ = executor.runtime_bridge.movement_bridge.resolve_executor_paths(runtime_bridge_proof)
    if distinct:
        replace_fixture_pointers(
            runtime_path,
            {
                "04646090": "04aa0090",
                "0465d890": "04bb8890",
            },
        )
        set_fixture_process_id(runtime_path, 5678)
    output_path = root / "secure-n-slot-runtime-executor-proof.json"
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
            "liveRuntimeArtifact": executor.runtime_bridge.movement_bridge.executor.created_file_receipt(runtime_path),
        },
    }
    return Path(
        executor.make_secure_runtime_executor_proof(
            session_path,
            runtime_path,
            output_path,
            execution_receipt=receipt,
            allow_fixture_receipt=True,
        )["artifact"]
    )


def run_self_test() -> None:
    executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        root = Path(tmp)
        session_path = root / "shared-session" / "host-authority-n-slot-session-security-smoke-proof.json"
        executor.security_builder.build_bundle(session_path)
        summary = validate_replayability(
            [
                make_executor_fixture(root / "first", session_path=session_path),
                make_executor_fixture(root / "second", distinct=True, session_path=session_path),
            ],
            allow_fixture=True,
        )
        require(summary["proofCount"] == 2, "self-test expected two executor proofs")
        require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "self-test must keep N-player proof at zero")
        require(summary["visibleMovementDeltaClaim"] is False, "self-test must keep visible movement unclaimed")

    with tempfile.TemporaryDirectory(dir=executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        path = make_executor_fixture(Path(tmp) / "duplicate-path")
        try:
            validate_replayability([path, path], allow_fixture=True)
        except SecureNSlotRuntimeExecutorReplayabilityError:
            pass
        else:
            raise SecureNSlotRuntimeExecutorReplayabilityError("duplicate proof path should fail replayability")

    with tempfile.TemporaryDirectory(dir=executor.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        root = Path(tmp)
        session_path = root / "shared-session" / "host-authority-n-slot-session-security-smoke-proof.json"
        executor.security_builder.build_bundle(session_path)
        try:
            validate_replayability(
                [
                    make_executor_fixture(root / "first", session_path=session_path),
                    make_executor_fixture(root / "second", session_path=session_path),
                ],
                allow_fixture=True,
            )
        except SecureNSlotRuntimeExecutorReplayabilityError:
            pass
        else:
            raise SecureNSlotRuntimeExecutorReplayabilityError("duplicate runtime player tuple should fail replayability")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proofs", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary secure N-slot runtime executor replayability checker self-test: PASS")
        return 0
    print(json.dumps(validate_replayability(args.proofs), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecureNSlotRuntimeExecutorReplayabilityError,
        executor.SecureNSlotRuntimeExecutorProofError,
        executor.security.HostAuthorityNSlotSessionSecuritySmokeProofError,
        executor.runtime_bridge.HostAuthorityNSlotRuntimeBridgeError,
        executor.runtime_bridge.nslot.HostAuthorityNSlotProcessSmokeProofError,
        executor.runtime_bridge.movement_bridge.HostAuthorityRuntimeMovementBridgeError,
        executor.runtime_bridge.movement_bridge.executor.HostAuthorityRuntimeExecutorError,
        executor.runtime_bridge.movement_bridge.executor.delivery.HostAuthorityRuntimeDeliveryError,
        executor.runtime_bridge.movement_bridge.movement.MovementStateDeltaError,
        executor.runtime_bridge.movement_bridge.movement.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary secure N-slot runtime executor replayability check: FAIL: {exc}")
        raise SystemExit(2)
