#!/usr/bin/env python3
"""Build a public-safe local session-directory smoke bundle for the original-binary online ladder."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "subagents"
    / "winui-original-binary-online"
    / "session-directory-smoke-20260619"
    / "online-session-directory-smoke-proof.json"
)

SCHEMA = "winui-original-binary-online-session-directory-smoke.v1"
PROTOCOL = "online-session-directory.v1"
HELPER = "winui-original-binary-online-session-directory-smoke-helper"
HELPER_VERSION = "online-session-directory-smoke-helper.v1"
DIRECTORY_SCOPE = "same-workstation-local-directory-smoke-not-public-matchmaking"
CLEAN_SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SESSION_SECURITY_PROOF_SHA256 = "3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b"
SESSION_RELAY_PLAN_SHA256 = "ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002"
RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256 = "fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376"
SECURE_EXECUTOR_PROOF_SHA256_VALUES = [
    "4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1",
    "8ef72707fd57a6c4ad9e65d3f03e1c21dd945e72bfbb3c3c87f5ddfd3c5d1e0d",
]
ACTIVE_SLOTS = ["P1", "P2"]
METADATA_SLOTS = ["P3", "P4"]
ALL_SLOTS = ["P1", "P2", "P3", "P4"]


def sha256_payload(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fingerprint(label: str, payload: Any) -> str:
    return sha256_payload({"label": label, "payload": payload})


def build_bundle(output: Path) -> dict[str, Any]:
    session_id = "local-directory-session-0001"
    server_identity = fingerprint("directory-server-identity", {"scope": DIRECTORY_SCOPE, "sessionId": session_id})
    host_identity = fingerprint("host-session-identity", {"sessionId": session_id, "relay": RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256})
    compatibility_key = fingerprint(
        "session-compatibility-key",
        {
            "cleanSpecimenSha256": CLEAN_SPECIMEN_SHA256,
            "protocolVersion": PROTOCOL,
            "runtimeRelayHash": RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256,
            "levelId": 850,
            "controllerConfiguration": 1,
        },
    )
    listing = {
        "listingId": "bea-copied-host-level850-config1",
        "sessionId": session_id,
        "sessionType": "host-authority-original-binary-local-splitscreen",
        "modeFamily": "unclassified-local-multiplayer-behavior",
        "modeRuntimeProof": False,
        "levelId": 850,
        "controllerConfiguration": 1,
        "cleanSpecimenSha256": CLEAN_SPECIMEN_SHA256,
        "compatibilityKey": compatibility_key,
        "hostIdentityFingerprint": host_identity,
        "slotCapacity": 4,
        "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "rejectedGameplayRouteSlots": METADATA_SLOTS,
        "maxOriginalBinaryActiveSlotsProven": 2,
        "runtimeCompatibleP1P2RelayHash": RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256,
        "sessionSecurityProofSha256": SESSION_SECURITY_PROOF_SHA256,
        "secureExecutorReplayabilityProofHashes": SECURE_EXECUTOR_PROOF_SHA256_VALUES,
        "publicAddressPublished": False,
        "rawPrivateRuntimePathPublished": False,
        "operatorSecretPublished": False,
        "directConnectionAddressPublished": False,
    }
    redacted_listing = {
        key: listing[key]
        for key in (
            "listingId",
            "sessionId",
            "sessionType",
            "modeFamily",
            "levelId",
            "controllerConfiguration",
            "cleanSpecimenSha256",
            "compatibilityKey",
            "hostIdentityFingerprint",
            "slotCapacity",
            "acceptedOriginalBinaryGameplaySlots",
            "metadataOnlySlots",
            "rejectedGameplayRouteSlots",
            "maxOriginalBinaryActiveSlotsProven",
            "runtimeCompatibleP1P2RelayHash",
        )
    }
    join_ticket = {
        "ticketId": "local-directory-p2-join-ticket-0001",
        "sessionId": session_id,
        "clientSlot": "P2",
        "ticketFingerprint": fingerprint("join-ticket", {"sessionId": session_id, "clientSlot": "P2"}),
        "expiresInSeconds": 30,
        "credentialStorage": "ephemeral-not-serialized",
        "rawCredentialSerialized": False,
        "publicServerClaim": False,
        "publicMatchmakingClaim": False,
        "multiHostLanClaim": False,
    }
    rejected_cases = [
        ("public-matchmaking-request", "public-matchmaking-not-allowed"),
        ("public-bind-request", "public-bind-not-allowed"),
        ("native-bea-netcode-claim", "native-bea-netcode-not-proven"),
        ("multi-host-lan-claim", "multi-host-lan-not-proven"),
        ("p3-gameplay-route-request", "required-for-unproven-original-binary-slots"),
        ("p4-gameplay-route-request", "required-for-unproven-original-binary-slots"),
        ("mode-proof-claim", "co-op-versus-mode-runtime-not-proven"),
        ("incompatible-specimen", "clean-specimen-mismatch"),
        ("protocol-version-mismatch", "protocol-version-mismatch"),
        ("unknown-field", "unknown-field"),
        ("oversized-query", "max-json-line-bytes-exceeded"),
        ("secret-bearing-listing", "secret-bearing-listing-rejected"),
        ("raw-private-path-listing", "raw-private-path-listing-rejected"),
        ("duplicate-session-id", "duplicate-session-id"),
    ]
    rejected = [
        {
            "caseId": case_id,
            "reason": reason,
            "directoryAccepted": False,
            "listingReturned": False,
            "joinTicketIssued": False,
            "publicMatchmakingClaim": False,
            "multiHostLanClaim": False,
        }
        for case_id, reason in rejected_cases
    ]
    bundle = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "directoryScope": DIRECTORY_SCOPE,
        "sourceProofs": {
            "sessionSecurityProofSha256": SESSION_SECURITY_PROOF_SHA256,
            "sessionRelayPlanSha256": SESSION_RELAY_PLAN_SHA256,
            "runtimeCompatibleP1P2RelayHash": RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256,
            "secureExecutorReplayabilityProofHashes": SECURE_EXECUTOR_PROOF_SHA256_VALUES,
        },
        "directory": {
            "transport": "same-workstation-in-memory-session-directory",
            "networkScope": DIRECTORY_SCOPE,
            "serverIdentityMode": "pinned-fingerprint",
            "serverIdentityFingerprint": server_identity,
            "publicNetworkSocketsOpened": False,
            "publicBind": False,
            "publicMatchmakingClaim": False,
            "matchmakingServerContacted": False,
            "operatorSecretsRequired": False,
            "credentialStorage": "ephemeral-not-serialized",
            "serializedCredentialPresent": False,
            "maxJsonLineBytes": 4096,
            "unknownFieldRejectionProof": True,
            "strictMessageSchemaProof": True,
        },
        "registeredSessions": [listing],
        "queries": {
            "accepted": [
                {
                    "caseId": "compatible-session-query",
                    "directoryAccepted": True,
                    "listingReturned": True,
                    "returnedListingCount": 1,
                    "returnedListings": [redacted_listing],
                    "publicAddressPublished": False,
                    "rawPrivateRuntimePathPublished": False,
                    "operatorSecretPublished": False,
                }
            ],
            "rejected": rejected,
        },
        "joinTickets": {
            "accepted": [join_ticket],
            "rejected": [
                {
                    "caseId": "p3-gameplay-join-ticket-rejected",
                    "clientSlot": "P3",
                    "reason": "required-for-unproven-original-binary-slots",
                    "joinTicketIssued": False,
                },
                {
                    "caseId": "p4-gameplay-join-ticket-rejected",
                    "clientSlot": "P4",
                    "reason": "required-for-unproven-original-binary-slots",
                    "joinTicketIssued": False,
                },
            ],
        },
        "counts": {
            "registeredSessionCount": 1,
            "compatibleListingCount": 1,
            "acceptedJoinTicketCount": 1,
            "rejectedDirectoryCaseCount": len(rejected),
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
            "hostHelperInputSent": False,
            "gameInputSentByDirectory": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
            "publicMatchmakingProof": False,
            "multiHostLanProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "physicalGamepadProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "claimBoundary": (
            "This proves only a same-workstation local session-directory smoke over public-safe metadata. It can "
            "register and list one compatible copied-host session and issue one redacted P2 join-ticket fingerprint. "
            "It does not contact a public matchmaking server, open public sockets, launch BEA, attach CDB, send game "
            "input, does not prove multi-host LAN play, does not prove native BEA netcode, does not prove active P3/P4 gameplay, or prove "
            "co-op/versus/runtime parity."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    bundle = build_bundle(args.output)
    print(json.dumps({"artifact": str(args.output), "schemaVersion": bundle["schemaVersion"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
