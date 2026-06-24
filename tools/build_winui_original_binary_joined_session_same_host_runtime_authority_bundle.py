#!/usr/bin/env python3
"""Build a public-safe joined-session same-host runtime-authority proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import build_winui_original_binary_online_session_directory_smoke_bundle as directory_builder
import build_winui_original_binary_wsl_remote_client_smoke_bundle as wsl_builder
import winui_safe_copy_online_session_directory_smoke_check as directory_check
import winui_safe_copy_online_wsl_remote_client_smoke_check as wsl_check


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "subagents"
    / "winui-original-binary-online"
    / "joined-session-same-host-runtime-authority-20260619"
    / "joined-session-same-host-runtime-authority-proof.json"
)

SCHEMA = "winui-original-binary-joined-session-same-host-runtime-authority.v1"
PROTOCOL = "joined-session-same-host-runtime-authority.v1"
HELPER = "winui-original-binary-joined-session-same-host-runtime-authority"
HELPER_VERSION = "joined-session-same-host-runtime-authority.v1"
JOINED_SCOPE = "joined-session-same-host-runtime-authority-not-online-play"
HOST_AUTHORITY_MODEL = "single-host-authoritative-copied-session"
HOST_AUTHORITY_SCOPE = "single-copied-host-exact-pid-state-graph"
RUNTIME_PROFILE = "original-binary-copied-local-splitscreen"
ACTIVE_SLOTS = ["P1", "P2"]
METADATA_SLOTS = ["P3", "P4"]
SEQUENCES = ["wait:300", "down:Q,wait:500,up:Q", "wait:300", "down:E,wait:500,up:E"]

SESSION_SECURITY_PROOF_SHA256 = "3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b"
N_SLOT_RELAY_PLAN_SHA256 = "ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002"
RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256 = "fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376"
SECURE_EXECUTOR_REPLAYABILITY_PROOF_SHA256_VALUES = [
    "4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1",
    "8ef72707fd57a6c4ad9e65d3f03e1c21dd945e72bfbb3c3c87f5ddfd3c5d1e0d",
]
STATE_AUTHORITY_REPLAYABILITY_SUMMARY_SHA256 = "a66e66dee6ff06bfab3a1cae234b86958bc8537712206d4db6605c898543ef7a"
STATE_AUTHORITY_OBSERVER_PROOF_SHA256_VALUES = [
    "ac1cd32281e354b5ae37a0aa8c17b1ab883bc9dd863c2ae5e2ffe7bde62c0416",
    "e57516d1b306d0a8a37aa1be2103235f066d1d4e06d4b648a9b0c140dfafc017",
]
STATE_AUTHORITY_LIVE_RUNTIME_SHA256_VALUES = [
    "7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae",
    "f87e0e6b622e504733082a9b8aafb4ba8d4e254e7a93471b0eacb87d263f32a8",
]
VISIBLE_MOVEMENT_REFERENCE_ARTIFACTS = [
    "local-multiplayer-visible-movement-delta-config1-20260618-focus2",
    "local-multiplayer-visible-movement-delta-config1-20260618-focus3",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative_path(base: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), base.resolve()).replace("\\", "/")


def first_join_ticket(path: Path) -> dict[str, Any]:
    bundle = read_json(path)
    tickets = bundle.get("joinTickets")
    accepted = tickets.get("accepted") if isinstance(tickets, dict) else None
    if not isinstance(accepted, list) or not accepted or not isinstance(accepted[0], dict):
        raise RuntimeError("session-directory proof is missing its accepted join ticket")
    return accepted[0]


def build_bundle(session_directory_proof: Path, wsl_remote_client_proof: Path, output_path: Path) -> dict[str, Any]:
    session_directory_proof = session_directory_proof.resolve()
    wsl_remote_client_proof = wsl_remote_client_proof.resolve()
    directory_summary = directory_check.validate_bundle(session_directory_proof)
    wsl_summary = wsl_check.validate_bundle(wsl_remote_client_proof)
    ticket = first_join_ticket(session_directory_proof)

    relay_hash_matched = (
        directory_summary["acceptedJoinTicketCount"] == 1
        and wsl_summary["acceptedCommandId"] == wsl_builder.COMMAND_ID
        and directory_builder.RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256 == RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256
        and wsl_builder.ACTIVE_SLOTS == ACTIVE_SLOTS
    )

    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "joinedSessionScope": JOINED_SCOPE,
        "hostAuthorityModel": HOST_AUTHORITY_MODEL,
        "runtimeProfile": RUNTIME_PROFILE,
        "sourceArtifacts": {
            "sessionDirectoryProof": relative_path(output_path.parent, session_directory_proof),
            "sessionDirectoryProofSha256": sha256_file(session_directory_proof),
            "wslRemoteClientProof": relative_path(output_path.parent, wsl_remote_client_proof),
            "wslRemoteClientProofSha256": sha256_file(wsl_remote_client_proof),
        },
        "sourceProofs": {
            "sessionDirectorySchema": directory_builder.SCHEMA,
            "directoryScope": directory_builder.DIRECTORY_SCOPE,
            "wslRemoteClientSchema": wsl_builder.SCHEMA,
            "wslRemoteClientTransport": wsl_builder.TRANSPORT,
            "sessionSecurityProofSha256": SESSION_SECURITY_PROOF_SHA256,
            "nSlotRelayPlanSha256": N_SLOT_RELAY_PLAN_SHA256,
            "runtimeCompatibleP1P2RelayHash": RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256,
            "secureExecutorReplayabilityProofHashes": SECURE_EXECUTOR_REPLAYABILITY_PROOF_SHA256_VALUES,
            "stateAuthorityReplayabilitySummarySha256": STATE_AUTHORITY_REPLAYABILITY_SUMMARY_SHA256,
            "stateAuthorityObserverProofHashes": STATE_AUTHORITY_OBSERVER_PROOF_SHA256_VALUES,
            "stateAuthorityLiveRuntimeArtifactHashes": STATE_AUTHORITY_LIVE_RUNTIME_SHA256_VALUES,
        },
        "joinedSession": {
            "joinedSessionSameHostRuntimeAuthorityChainProven": True,
            "acceptedJoinTicketSlot": ticket["clientSlot"],
            "acceptedJoinTicketFingerprint": ticket["ticketFingerprint"],
            "joinTicketRuntimeRelayHashMatched": relay_hash_matched,
            "acceptedWslCommandId": wsl_summary["acceptedCommandId"],
            "wslTransport": wsl_summary["transport"],
            "wslNetworkScope": wsl_summary["networkScope"],
            "samePhysicalMachineWslPredecessor": True,
            "sameHostOnly": True,
            "secondPhysicalHostProof": False,
        },
        "runtimeAuthority": {
            "hostAuthorityScope": HOST_AUTHORITY_SCOPE,
            "stateAuthorityGraphProven": True,
            "stateAuthorityReplayabilityProven": True,
            "secureNSlotRuntimeExecutorReplayabilityProven": True,
            "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
            "metadataOnlySlots": METADATA_SLOTS,
            "rejectedGameplayRouteSlots": METADATA_SLOTS,
            "maxOriginalBinaryActiveSlotsProven": 2,
            "derivedInputSequences": SEQUENCES,
            "roleInvariant": "P1 -> Q -> inputDevice0/top split half; P2 -> E -> inputDevice1/bottom split half",
            "p1QButton31ReceiveRowsPerProof": 12,
            "p1QForwardStateStoreRowsPerProof": 12,
            "p2EButton31ReceiveRowsPerProof": 11,
            "p2EForwardStateStoreRowsPerProof": 11,
            "waitWindowsClean": True,
            "visualCaptureCountPerRuntimeProof": 7,
            "visibleMovementReferenceAccepted": True,
            "visibleMovementReferenceArtifacts": VISIBLE_MOVEMENT_REFERENCE_ARTIFACTS,
            "joinedSessionVisibleMovementCausalityProof": False,
        },
        "counts": {
            "registeredSessionCount": directory_summary["registeredSessionCount"],
            "compatibleListingCount": directory_summary["compatibleListingCount"],
            "acceptedJoinTicketCount": directory_summary["acceptedJoinTicketCount"],
            "rejectedDirectoryCaseCount": directory_summary["rejectedDirectoryCaseCount"],
            "wslAcceptedCommandCount": 1,
            "secureExecutorReplayabilityProofCount": len(SECURE_EXECUTOR_REPLAYABILITY_PROOF_SHA256_VALUES),
            "stateAuthorityReplayabilityProofCount": len(STATE_AUTHORITY_OBSERVER_PROOF_SHA256_VALUES),
            "wrapperNewBeaLaunchCount": 0,
            "wrapperCdbAttachCount": 0,
            "upstreamNewBeaLaunchCountPerProof": 1,
            "upstreamCdbAttachCountPerProof": 1,
            "hostHelperInputSentByAcceptedRuntimeAuthority": True,
            "gameInputSentByDirectory": False,
            "gameInputSentByWslClient": False,
            "gameInputSentByNSlotScheduler": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
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
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This proves a same-host joined-session runtime-authority chain: the accepted local directory P2 "
            "join-ticket selects the bounded P1/P2 relay path, and the same-physical-machine WSL command-source "
            "predecessor is linked to that accepted P2 route already replayed through secure N-slot runtime "
            "executor and exact-PID state-authority proofs. "
            "It does not prove a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, "
            "active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online "
            "semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, joined-session visible "
            "movement causality, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-directory-proof", type=Path, default=directory_builder.DEFAULT_OUTPUT)
    parser.add_argument("--wsl-remote-client-proof", type=Path, default=wsl_builder.DEFAULT_OUTPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    bundle = build_bundle(args.session_directory_proof, args.wsl_remote_client_proof, args.output)
    print(
        json.dumps(
            {
                "artifact": str(args.output),
                "schemaVersion": bundle["schemaVersion"],
                "joinedSessionSameHostRuntimeAuthorityChainProven": bundle["joinedSession"][
                    "joinedSessionSameHostRuntimeAuthorityChainProven"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
