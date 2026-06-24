#!/usr/bin/env python3
"""Build a joined-session runtime-causality proof with one fresh copied BEA run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle as security_builder
import build_winui_original_binary_joined_session_same_host_runtime_authority_bundle as joined_builder
import winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check as executor_check
import winui_safe_copy_online_joined_session_same_host_runtime_authority_check as joined_check


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = executor_check.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = (
    PRIVATE_ROOT
    / "joined-session-runtime-causality-20260619"
)
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "joined-session-runtime-causality-proof.json"
DEFAULT_SESSION_SECURITY_PROOF = (
    DEFAULT_ARTIFACT_ROOT / "host-authority-n-slot-session-security-smoke-proof.json"
)

SCHEMA = "winui-original-binary-joined-session-runtime-causality.v1"
PROTOCOL = "joined-session-runtime-causality.v1"
HELPER = "winui-original-binary-joined-session-runtime-causality"
HELPER_VERSION = "joined-session-runtime-causality.v1"
CAUSALITY_SCOPE = "joined-session-fresh-runtime-causality-same-host-not-online-play"
HOST_AUTHORITY_MODEL = joined_builder.HOST_AUTHORITY_MODEL
HOST_AUTHORITY_SCOPE = joined_builder.HOST_AUTHORITY_SCOPE
RUNTIME_PROFILE = joined_builder.RUNTIME_PROFILE
ACTIVE_SLOTS = joined_builder.ACTIVE_SLOTS
METADATA_SLOTS = joined_builder.METADATA_SLOTS


class JoinedSessionRuntimeCausalityBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise JoinedSessionRuntimeCausalityBuildError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def relative_path(base: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), base.resolve()).replace("\\", "/")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def resolve_executor_runtime_path(executor_path: Path, executor_payload: dict[str, Any]) -> Path:
    return executor_check.resolve_path(executor_path, str(executor_payload.get("liveRuntimeArtifact", "")))


def cdb_log_sha256(runtime_path: Path) -> str:
    runtime = executor_check.read_json(runtime_path)
    cdb = runtime.get("cdbObserver") if isinstance(runtime.get("cdbObserver"), dict) else {}
    result = cdb.get("result") if isinstance(cdb.get("result"), dict) else {}
    raw_log = str(result.get("logPath") or cdb.get("logPath") or "")
    require(raw_log, "runtime artifact is missing a CDB log path")
    log_path = Path(raw_log)
    require(log_path.is_file(), f"CDB log path is missing: {log_path}")
    return sha256_file(log_path)


def require_private_output(path: Path) -> Path:
    return executor_check.runtime_bridge.movement_bridge.executor.require_private_proof_path(path)


def build_bundle_from_artifacts(
    joined_session_proof: Path,
    secure_runtime_executor_proof: Path,
    output_path: Path,
    *,
    allow_fixture_executor: bool = False,
) -> dict[str, Any]:
    output_path = require_private_output(output_path)
    joined_session_proof = joined_session_proof.resolve()
    secure_runtime_executor_proof = executor_check.require_private_path(secure_runtime_executor_proof, must_exist=True)

    joined_summary = joined_check.validate_bundle(joined_session_proof)
    executor_summary = executor_check.validate_secure_runtime_executor_proof(
        secure_runtime_executor_proof,
        allow_fixture=allow_fixture_executor,
    )
    joined_payload = read_json(joined_session_proof)
    executor_payload = executor_check.read_json(secure_runtime_executor_proof)
    executor_runtime = resolve_executor_runtime_path(secure_runtime_executor_proof, executor_payload)
    joined_source = object_at(joined_payload, "sourceProofs")
    joined_session = object_at(joined_payload, "joinedSession")
    joined_runtime = object_at(joined_payload, "runtimeAuthority")
    execution = object_at(executor_payload, "execution")

    require(joined_summary["acceptedJoinTicketSlot"] == "P2", "joined proof must carry accepted P2 ticket")
    require(isinstance(joined_session.get("acceptedJoinTicketFingerprint"), str) and len(joined_session["acceptedJoinTicketFingerprint"]) == 64, "joined proof must carry accepted ticket fingerprint")
    require(joined_summary["joinTicketRuntimeRelayHashMatched"] is True, "joined proof relay hash link missing")
    require(joined_summary["joinedSessionVisibleMovementCausalityProof"] is False, "prior wrapper must not claim visible causality")
    require(joined_source.get("runtimeCompatibleP1P2RelayHash") == executor_summary["runtimeCompatibleP1P2RelayHash"], "joined/runtime relay hash mismatch")
    require(joined_runtime.get("derivedInputSequences") == executor_summary["derivedInputSequences"], "joined/runtime derived sequence mismatch")
    require(joined_runtime.get("acceptedOriginalBinaryGameplaySlots") == executor_summary["acceptedOriginalBinaryGameplaySlots"] == ACTIVE_SLOTS, "active slots mismatch")
    require(joined_runtime.get("metadataOnlySlots") == executor_summary["metadataOnlySlots"] == METADATA_SLOTS, "metadata slots mismatch")
    require(joined_runtime.get("rejectedGameplayRouteSlots") == executor_summary["rejectedGameplayRouteSlots"] == METADATA_SLOTS, "rejected slots mismatch")
    require(executor_summary["receiptMode"] == "live-secure-nslot-runtime-executor-subprocess" or allow_fixture_executor, "runtime executor must be a live proof")
    require(executor_summary["newBeaLaunchCount"] == 1, "fresh runtime proof must launch one copied BEA")
    require(executor_summary["cdbAttachCount"] == 1, "fresh runtime proof must attach CDB once")
    require(executor_summary["hostHelperInputSent"] is True, "host helper input must be sent")
    require(executor_summary["gameInputSentByNSlotScheduler"] is False, "scheduler direct game input must stay false")
    require(executor_summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "N-player runtime proof must stay zero")
    require(executor_summary["activeP3P4OriginalBinaryGameplayProof"] is False, "P3/P4 proof must stay false")
    require(executor_summary["visibleMovementDeltaClaim"] is False, "visible movement causality must remain unclaimed")

    state_digest = sha256_payload(
        {
            "runtimePlayers": executor_summary["runtimePlayers"],
            "movementState": executor_summary["movementState"],
        }
    )
    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "causalityScope": CAUSALITY_SCOPE,
        "hostAuthorityModel": HOST_AUTHORITY_MODEL,
        "runtimeProfile": RUNTIME_PROFILE,
        "sourceArtifacts": {
            "joinedSessionAuthorityProof": relative_path(output_path.parent, joined_session_proof),
            "joinedSessionAuthorityProofSha256": sha256_file(joined_session_proof),
            "secureRuntimeExecutorProof": relative_path(output_path.parent, secure_runtime_executor_proof),
            "secureRuntimeExecutorProofSha256": sha256_file(secure_runtime_executor_proof),
            "sessionSecurityProofSha256": executor_payload["sessionSecurityProofSha256"],
            "liveRuntimeArtifactSha256": executor_payload["liveRuntimeArtifactSha256"],
            "cdbLogSha256": cdb_log_sha256(executor_runtime),
            "runtimeStateSummarySha256": state_digest,
        },
        "joinedSessionCausality": {
            "joinedSessionRuntimeCausalityProven": True,
            "joinedSessionAuthorityProofValidated": True,
            "freshRuntimeExecutorProofValidated": True,
            "joinTicketRuntimeRelayPathMatchCount": 1,
            "acceptedJoinTicketSlot": "P2",
            "acceptedJoinTicketFingerprint": joined_session["acceptedJoinTicketFingerprint"],
            "joinTicketRuntimeRelayHashMatched": True,
            "samePhysicalMachineWslPredecessor": True,
            "sameHostOnly": True,
            "secondPhysicalHostProof": False,
            "runtimeCompatibleP1P2RelayHash": executor_summary["runtimeCompatibleP1P2RelayHash"],
            "derivedInputSequences": executor_summary["derivedInputSequences"],
        },
        "runtimeEvidence": {
            "hostAuthorityScope": HOST_AUTHORITY_SCOPE,
            "receiptMode": executor_summary["receiptMode"],
            "securityProofScope": executor_summary["securityProofScope"],
            "sessionSecurityRelayPlanSha256": executor_summary["sessionSecurityRelayPlanSha256"],
            "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
            "metadataOnlySlots": METADATA_SLOTS,
            "rejectedGameplayRouteSlots": METADATA_SLOTS,
            "safeCopyLaunchLevel": execution["safeCopyLaunchLevel"],
            "controllerConfiguration": execution["controllerConfiguration"],
            "newBeaLaunchCount": executor_summary["newBeaLaunchCount"],
            "cdbAttachCount": executor_summary["cdbAttachCount"],
            "visualCaptureCount": executor_summary["visualCaptureCount"],
            "deliveredOriginalBinaryCommandCount": executor_summary["deliveredOriginalBinaryCommandCount"],
            "hostHelperInputSent": executor_summary["hostHelperInputSent"],
            "gameInputSentByJoinedSessionClient": False,
            "gameInputSentByDirectory": False,
            "gameInputSentByWslClient": False,
            "gameInputSentByNSlotScheduler": executor_summary["gameInputSentByNSlotScheduler"],
            "stateAuthorityGraphProven": True,
            "exactPidCdbStateRowsProven": True,
            "waitWindowsClean": True,
            "visibleMovementDeltaClaim": False,
            "joinedSessionVisibleMovementCausalityProof": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "slotBoundary": {
            "slotCapacity": 4,
            "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
            "metadataOnlySlots": METADATA_SLOTS,
            "rejectedGameplayRouteSlots": METADATA_SLOTS,
            "maxOriginalBinaryActiveSlotsProven": 2,
            "beyondTwoPlayersRequiresNewProofClass": True,
            "permanentImpossibilityClaim": False,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "secondPhysicalHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "teamVersusRuntimeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "physicalGamepadProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "rawPrivateProofPathPublished": False,
            "rawPrivateArtifactContentPublished": False,
            "absolutePrivatePathPublished": False,
            "rawRuntimePointerPublished": False,
            "rawRuntimePidPublished": False,
            "rawCdbLogPathPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This proves same-host joined-session runtime causality: a validated joined-session P2 ticket/relay chain "
            "selects the same P1/P2 runtime-compatible relay hash and derived input sequence that drove one fresh "
            "copied BEA level-850/config-1 secure N-slot runtime executor run with exact-PID CDB state evidence. "
            "It does not prove base online multiplayer readiness, a second physical host, multi-host LAN play, "
            "public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more-than-two "
            "original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, "
            "anti-cheat, physical gamepad behavior, joined-session visible movement causality, rebuild parity, "
            "or no-noticeable-difference online parity."
        ),
    }
    write_json(output_path, bundle)
    return bundle


def build_live_bundle(
    joined_session_proof: Path,
    artifact_root: Path,
    output_path: Path,
    *,
    exe_override: Path,
) -> dict[str, Any]:
    artifact_root = require_private_output(artifact_root)
    output_path = require_private_output(output_path)
    output_parent = output_path.parent.resolve()
    if artifact_root.resolve() == output_parent:
        run_stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        artifact_root = artifact_root / "runs" / run_stamp
    artifact_root.mkdir(parents=True, exist_ok=True)
    session_security_path = artifact_root / DEFAULT_SESSION_SECURITY_PROOF.name
    security_builder.build_bundle(session_security_path)
    executor_summary = executor_check.build_live_secure_runtime_executor(
        session_security_path,
        artifact_root,
        exe_override=exe_override,
    )
    executor_path = Path(str(executor_summary["artifact"]))
    return build_bundle_from_artifacts(joined_session_proof, executor_path, output_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--joined-session-proof", type=Path, default=joined_builder.DEFAULT_OUTPUT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--exe-override", type=Path, default=executor_check.runtime_bridge.movement_bridge.executor.DEFAULT_EXE_OVERRIDE)
    args = parser.parse_args()
    bundle = build_live_bundle(
        args.joined_session_proof,
        args.artifact_root,
        args.output,
        exe_override=args.exe_override,
    )
    print(
        json.dumps(
            {
                "artifact": str(args.output),
                "schemaVersion": bundle["schemaVersion"],
                "joinedSessionRuntimeCausalityProven": bundle["joinedSessionCausality"][
                    "joinedSessionRuntimeCausalityProven"
                ],
                "newBeaLaunchCount": bundle["runtimeEvidence"]["newBeaLaunchCount"],
                "cdbAttachCount": bundle["runtimeEvidence"]["cdbAttachCount"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
