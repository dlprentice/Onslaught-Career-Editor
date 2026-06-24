#!/usr/bin/env python3
"""Validate second-host/private-LAN command-source proof bundles."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_private_lan_transport_smoke_check as lan


ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "roadmap" / "original-binary-online-second-host-command-source.v1.json"
EXPECTED_GATE_SCHEMA = "winui-original-binary-second-host-command-source-gate.v1"
EXPECTED_GATE_SCOPE = "second-host-command-source-proof-gate-not-live-runtime-proof"
EXPECTED_SCHEMA = "winui-original-binary-second-host-command-source.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-second-host-command-source-session.v1"
EXPECTED_TRANSPORT = "second-host-private-lan-command-source-tcp-jsonl-auth"
EXPECTED_PROTOCOL = "second-host-private-lan-command-source.v1"
EXPECTED_HELPER = "winui-original-binary-second-host-command-source-proof-helper"
EXPECTED_HELPER_VERSION = "second-host-command-source-proof-helper.v1"
EXPECTED_COMMAND_ID = "second-host-p2-forward-0001"
EXPECTED_PRIVATE_LAN_COMMAND_ID = lan.EXPECTED_COMMAND_ID
EXPECTED_NEXT_RUNTIME_PROOF_ID = "host-runtime-delivery-from-source-bound-distinct-command-source"
EXPECTED_REMOTE_SLOT = "P2"
EXPECTED_REMOTE_COMMAND = lan.delivery.relay.EXPECTED_REMOTE_COMMAND
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
ALLOWED_COMMAND_SOURCE_KINDS = {
    "distinct-physical-host-private-lan",
    "distinct-vm-private-lan-labeled-vm-only",
}
ALLOWED_RUNTIME_HOST_KINDS = {
    "windows-host",
    "linux-host",
    "macos-host",
    "vm-guest",
}
FORBIDDEN_RUNTIME_HOST_KINDS = {
    "wsl-on-host",
    "container-on-host",
    "unknown-host",
}
FORBIDDEN_COMMAND_SOURCE_KINDS = {
    "loopback",
    "same-workstation-process",
    "wsl-on-host",
    "public-internet-host",
    "unknown-peer",
}
EXPECTED_REJECTION_REASONS = {
    "metadata-slot-gameplay-not-allowed",
    "loopback-not-allowed",
    "same-workstation-process-not-allowed",
    "wsl-on-host-not-allowed",
    "public-internet-host-not-allowed",
    "unknown-peer-not-allowed",
    "bad-hmac",
    "session-not-established",
    "replay-nonce",
    "timestamp-window",
    "sequence-order",
    "pinned-identity-mismatch",
    "compatibility-key-mismatch",
    "rate-limit-exceeded",
    "direct-input-not-allowed",
    "message-schema-mismatch",
}
EXPECTED_TRANSCRIPT_EVENTS = [
    "server_bound",
    "client_session_hello_bad_hmac",
    "server_session_rejected_bad_hmac",
    "client_session_hello_wrong_server",
    "server_session_rejected_server_pin",
    "client_session_hello_wrong_identity",
    "server_session_rejected_pinned_identity",
    "client_command_pre_session",
    "server_command_rejected_pre_session",
    "client_session_hello",
    "server_session_accepted",
    "client_command_p3_forward",
    "server_command_rejected_metadata_slot",
    "client_command_bad_hmac",
    "server_command_rejected_bad_hmac",
    "client_command_stale_timestamp",
    "server_command_rejected_timestamp_window",
    "client_command_future_timestamp",
    "server_command_rejected_future_timestamp",
    "client_command_sequence_regression",
    "server_command_rejected_sequence_order",
    "client_command_bad_compatibility",
    "server_command_rejected_compatibility_key",
    "client_command_p2_forward",
    "server_command_accepted",
    "client_command_replay_nonce",
    "server_command_rejected_replay_nonce",
    "client_command_rate_limited",
    "server_command_rejected_rate_limit",
    "client_command_unknown_field",
    "server_command_rejected_unknown_field",
    "client_command_direct_input",
    "server_command_rejected_direct_input",
    "client_source_safety_postflight",
    "server_source_safety_postflight_accepted",
    "client_close",
    "server_stopped",
]
REQUIRED_SESSION_SECURITY_HARDENING_FLAGS = (
    "badHmacLiveRejected",
    "replayNonceLiveRejected",
    "timestampWindowLiveEnforced",
    "sequenceOrderLiveEnforced",
    "pinnedIdentityLiveEnforced",
    "compatibilityKeyLiveEnforced",
    "metadataSlotGameplayLiveRejected",
    "preSessionCommandLiveRejected",
    "directInputBypassLiveRejected",
    "unknownFieldLiveRejected",
)
SESSION_SECURITY_HARDENING_CASES = {
    "badHmacLiveRejected": {
        "caseId": "bad-hmac-session-and-command",
        "reason": "bad-hmac",
        "requestEvents": ["client_session_hello_bad_hmac", "client_command_bad_hmac"],
        "responseEvents": ["server_session_rejected_bad_hmac", "server_command_rejected_bad_hmac"],
    },
    "replayNonceLiveRejected": {
        "caseId": "replay-nonce-command",
        "reason": "replay-nonce",
        "requestEvents": ["client_command_replay_nonce"],
        "responseEvents": ["server_command_rejected_replay_nonce"],
    },
    "timestampWindowLiveEnforced": {
        "caseId": "stale-and-future-timestamp-command",
        "reason": "timestamp-window",
        "requestEvents": ["client_command_stale_timestamp", "client_command_future_timestamp"],
        "responseEvents": ["server_command_rejected_timestamp_window", "server_command_rejected_future_timestamp"],
    },
    "sequenceOrderLiveEnforced": {
        "caseId": "sequence-regression-command",
        "reason": "sequence-order",
        "requestEvents": ["client_command_sequence_regression"],
        "responseEvents": ["server_command_rejected_sequence_order"],
    },
    "pinnedIdentityLiveEnforced": {
        "caseId": "wrong-pinned-server-or-client-identity",
        "reason": "pinned-identity-mismatch",
        "requestEvents": ["client_session_hello_wrong_server", "client_session_hello_wrong_identity"],
        "responseEvents": ["server_session_rejected_server_pin", "server_session_rejected_pinned_identity"],
    },
    "compatibilityKeyLiveEnforced": {
        "caseId": "bad-compatibility-key-command",
        "reason": "compatibility-key-mismatch",
        "requestEvents": ["client_command_bad_compatibility"],
        "responseEvents": ["server_command_rejected_compatibility_key"],
    },
    "metadataSlotGameplayLiveRejected": {
        "caseId": "metadata-slot-gameplay-command",
        "reason": "metadata-slot-gameplay-not-allowed",
        "requestEvents": ["client_command_p3_forward"],
        "responseEvents": ["server_command_rejected_metadata_slot"],
    },
    "preSessionCommandLiveRejected": {
        "caseId": "pre-session-command",
        "reason": "session-not-established",
        "requestEvents": ["client_command_pre_session"],
        "responseEvents": ["server_command_rejected_pre_session"],
    },
    "directInputBypassLiveRejected": {
        "caseId": "direct-input-bypass-command",
        "reason": "direct-input-not-allowed",
        "requestEvents": ["client_command_direct_input"],
        "responseEvents": ["server_command_rejected_direct_input"],
    },
    "unknownFieldLiveRejected": {
        "caseId": "unknown-field-command",
        "reason": "message-schema-mismatch",
        "requestEvents": ["client_command_unknown_field"],
        "responseEvents": ["server_command_rejected_unknown_field"],
    },
}
EXPECTED_NONCLAIM_FALSE_KEYS = (
    "baseOnlineMultiplayerReady",
    "multiHostLanPlayProof",
    "publicMatchmakingProof",
    "publicServerProof",
    "nativeBeaNetcodeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "moreThanTwoOriginalBinaryRuntimePlayersProof",
    "coOpVersusRuntimeProof",
    "physicalGamepadProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
    "gameInputSentBySecondHostClient",
    "hostHelperInputSent",
)
EXPECTED_RELEASE_FALSE_KEYS = (
    "secretsSerialized",
    "rawPrivateAddressPublishedToPublicDocs",
    "rawPrivateProofPathPublished",
    "privateArtifactContentPublished",
    "publicHostOrMatchmakingEndpointPublished",
    "releaseIncludedPrivateArtifact",
)
ALLOWED_TRUTHY_CLAIM_FLAGS = {
    "privateProofReleaseExcludedByPolicy",
    "requiresPrivateLanTransportProofHash",
    "replayCacheEnabled",
    "secondHostCommandSourceProof",
    "secondPhysicalHostProof",
}
PRIVATE_IPV4_NETWORKS = tuple(
    ipaddress.ip_network((value, prefix))
    for value, prefix in (
        (0x0A000000, 8),
        (0xAC100000, 12),
        (0xC0A80000, 16),
    )
)
PRIVATE_IPV6_NETWORKS = (ipaddress.ip_network("fc00::/7"),)
DOCUMENTATION_OR_RESERVED_TEST_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
FIXTURE_HOST_ADDRESS = ".".join(str(part) for part in (10, 77, 20, 114))
FIXTURE_CLIENT_ADDRESS = ".".join(str(part) for part in (10, 77, 20, 115))
FIXTURE_HEX64_SENTINELS = {char * 64 for char in "0123456789abcdef"}
MIN_REALISTIC_LIVE_UNIX_TIMESTAMP = 1_600_000_000


class SecondHostCommandSourceProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostCommandSourceProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def sha256_file(path: Path) -> str:
    return lan.sha256_file(path)


def is_hex64(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    require(not candidate.is_absolute(), "private LAN proof reference must be proof-root relative")
    require(".." not in candidate.parts, "private LAN proof reference must not escape the proof root")
    if not candidate.is_absolute():
        candidate = bundle_path.parent / candidate
    proof_root = bundle_path.parent.resolve()
    candidate = candidate.resolve()
    require(candidate == proof_root or proof_root in candidate.parents, "private LAN proof reference escaped the proof root")
    require(candidate.is_file(), f"referenced private LAN proof is missing: {candidate}")
    return candidate


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    allowed = {
        "authkeyfingerprint",
        "credentialstorage",
        "serializedcredentialpresent",
        "credentialtransport",
        "credentialtransporttoclient",
        "credentialtransporttoserver",
        "requirestransientinvitationcredentialnotartifactserialized",
        "secretsserialized",
    }
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if lowered not in allowed:
                forbidden = ("secret", "password", "token", "credential", "authkey", "apikey", "api_key", "rawcredential")
                require(not any(fragment in lowered for fragment in forbidden), f"serialized credential-like field is not allowed at {path}.{key}")
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_no_sensitive_string_values(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require_no_sensitive_string_values(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_sensitive_string_values(child, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        forbidden_fragments = (
            "c:\\",
            "c:/",
            "users\\",
            "users/",
            "program files",
            "\\\\",
            "/mnt/",
            "/home/",
            "file://",
            "bearer ",
            "password=",
            "token=",
            "secret=",
            "sk-",
        )
        require(not any(fragment in lowered for fragment in forbidden_fragments), f"sensitive path or secret-like string is not allowed at {path}")
        require(re.search(r"(?i)\b[a-z]:[\\/]", value) is None, f"drive-letter path is not allowed at {path}")


def require_no_hidden_truthy_overclaim_flags(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            looks_like_claim = lowered.endswith(("proof", "ready", "enabled", "claim", "implemented")) or "proof" in lowered
            if looks_like_claim and key not in ALLOWED_TRUTHY_CLAIM_FLAGS and not key.startswith("requires"):
                if is_truthy_overclaim_value(child):
                    raise SecondHostCommandSourceProofError(f"truthy overclaim-like field is not allowed at {path}.{key}")
            require_no_hidden_truthy_overclaim_flags(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_hidden_truthy_overclaim_flags(child, f"{path}[{index}]")


def is_truthy_overclaim_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "enabled", "ready", "implemented", "proof", "proved"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def require_false_claims(value: dict[str, Any], keys: tuple[str, ...], label: str) -> None:
    for key in keys:
        require(value.get(key) is False, f"{label} must remain false: {key}")


def ip_is_private_lan_non_loopback(raw: str) -> bool:
    try:
        address = ipaddress.ip_address(raw)
    except ValueError:
        return False
    if address.is_loopback or address.is_link_local or address.is_multicast or address.is_unspecified:
        return False
    if any(address in network for network in DOCUMENTATION_OR_RESERVED_TEST_NETWORKS):
        return False
    if address.version == 4:
        return any(address in network for network in PRIVATE_IPV4_NETWORKS)
    return any(address in network for network in PRIVATE_IPV6_NETWORKS)


def make_gate_fixture() -> dict[str, Any]:
    return {
        "schemaVersion": EXPECTED_GATE_SCHEMA,
        "gateScope": EXPECTED_GATE_SCOPE,
        "status": "validator-ready-no-accepted-live-second-host-proof",
        "validator": {
            "script": "tools/winui_safe_copy_online_second_host_command_source_check.py",
            "packageScript": "test:winui-original-binary-second-host-command-source",
            "validatesPrivateProofSchema": EXPECTED_SCHEMA,
        },
        "acceptedProofContract": {
            "proofSchemaVersion": EXPECTED_SCHEMA,
            "sessionSchemaVersion": EXPECTED_SESSION_SCHEMA,
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "helper": EXPECTED_HELPER,
            "helperVersion": EXPECTED_HELPER_VERSION,
            "networkScope": "distinct-private-host-command-source-not-online-play",
            "allowedCommandSourceKinds": sorted(ALLOWED_COMMAND_SOURCE_KINDS),
            "forbiddenCommandSourceKinds": sorted(FORBIDDEN_COMMAND_SOURCE_KINDS),
            "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
            "acceptedRemoteSlot": EXPECTED_REMOTE_SLOT,
            "acceptedCommandId": EXPECTED_COMMAND_ID,
            "forwardsToPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
            "requiresPrivateLanTransportProofHash": True,
            "requiresPrivateNonLoopbackAssignedAddresses": True,
            "rejectsDocumentationAndReservedAddressRanges": True,
            "requiresStructuredHostClientIdentityEvidence": True,
            "requiresComputedMachineFingerprintPreflight": True,
            "requiresRuntimeHostKindEvidence": True,
            "rejectsWslOrContainerRuntimeHostKind": True,
            "requiresVmGuestRuntimeKindForVmLabeledProof": True,
            "requiresNonVmRuntimeKindForPhysicalProof": True,
            "requiresRedactedMachineIdentityInputs": True,
            "requiresClientSourceNotHostAssignedLocalAddress": True,
            "requiresSanitizedInterfaceEvidence": True,
            "requiresHmacSha256SessionAuth": True,
            "requiresPinnedServerAndClientIdentities": True,
            "requiresReplayAndSequenceProtection": True,
            "requiresAcceptedCommandTranscriptBinding": True,
            "requiresSecondHostSessionSecurityHardening": True,
            "requiresLiveNegativeCaseTranscript": True,
            "supportsExplicitLiveValidationMode": True,
            "requiresLiveValidationModeBeforeRuntimePromotion": True,
            "requiresPerEventServerObservedAtUnixForLiveProof": True,
            "requiresMonotonicServerObservedTimestampsInsideInvitationWindowForLiveProof": True,
            "requiresNonFixtureMachineFingerprintSourcesForLiveProof": True,
            "requiresAutoPlatformRuntimeHostKindSourcesForLiveProof": True,
            "rejectsSyntheticLiveLabeledFixtures": True,
            "requiresInvitationExclusiveCreate": True,
            "requiresInvitationExpiryValidation": True,
            "requiresInvitationDeletionAfterServerCompletion": True,
            "requiresInvitationLifecycleReceipt": True,
            "requiresListenerLifecycleReceipt": True,
            "requiresListenerTeardownEvidence": True,
            "requiresListenerPostCloseConnectRejection": True,
            "requiresServerObservedTimestampWindow": True,
            "requiresTransientInvitationCredentialNotArtifactSerialized": True,
            "requiresVmLabeledProofSamePhysicalMachineOnly": True,
            "requiresPhysicalSecondHostProofNotSamePhysicalMachineOnly": True,
            "requiredSecondHostSecurityHardeningFlags": list(REQUIRED_SESSION_SECURITY_HARDENING_FLAGS),
            "requiresCopiedProfileHashesOnBothSides": True,
            "requiresInstalledGamePrePostHashesOnBothSides": True,
            "requiresLocalSourceSafetyPreflightForLiveProof": True,
            "requiresTwoPhasePrePostSourceSafetyForLiveProof": True,
            "requiresOperatorSuppliedHashOnlyLiveProofRejection": True,
            "requiresFixtureSentinelLiveProofRejection": True,
            "requiresStringNumericTruthyOverclaimRejection": True,
            "requiresNoRawPathsInPreflightEvidence": True,
            "requiresProgramFilesMutationRejection": True,
            "requiredRejectedCases": sorted(EXPECTED_REJECTION_REASONS),
        },
        "currentEvidence": {
            "acceptedLiveSecondHostCommandSourceProof": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
            "hostJoinControlsMayBeEnabled": False,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "coOpVersusRuntimeProof": False,
            "physicalGamepadProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
            "gameInputSentBySecondHostClient": False,
            "hostHelperInputSent": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "secretsSerialized": False,
            "rawPrivateAddressPublishedToPublicDocs": False,
            "rawPrivateProofPathPublished": False,
            "privateArtifactContentPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "nextRequiredProof": {
            "id": EXPECTED_NEXT_RUNTIME_PROOF_ID,
            "description": "A later live proof must deliver the accepted distinct-host command through the copied BEA host-helper path with mapped P2 sequence and exact-PID CDB evidence.",
            "requiredBeforeHostJoinEnablement": True,
        },
    }


def validate_gate(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    require_no_sensitive_string_values(payload)
    require_no_hidden_truthy_overclaim_flags(payload)
    require(payload.get("schemaVersion") == EXPECTED_GATE_SCHEMA, "gate schema mismatch")
    require(payload.get("gateScope") == EXPECTED_GATE_SCOPE, "gate scope mismatch")
    require_no_serialized_credentials(payload)

    validator = object_at(payload, "validator")
    require(validator.get("script") == "tools/winui_safe_copy_online_second_host_command_source_check.py", "validator script mismatch")
    require(validator.get("packageScript") == "test:winui-original-binary-second-host-command-source", "validator package script mismatch")
    require(validator.get("validatesPrivateProofSchema") == EXPECTED_SCHEMA, "private proof schema guard mismatch")

    contract = object_at(payload, "acceptedProofContract")
    require(contract.get("proofSchemaVersion") == EXPECTED_SCHEMA, "accepted proof schema mismatch")
    require(contract.get("sessionSchemaVersion") == EXPECTED_SESSION_SCHEMA, "session schema mismatch")
    require(contract.get("transport") == EXPECTED_TRANSPORT, "transport mismatch")
    require(contract.get("protocolVersion") == EXPECTED_PROTOCOL, "protocol mismatch")
    require(contract.get("helper") == EXPECTED_HELPER, "helper mismatch")
    require(contract.get("helperVersion") == EXPECTED_HELPER_VERSION, "helper version mismatch")
    require(contract.get("networkScope") == "distinct-private-host-command-source-not-online-play", "network scope mismatch")
    require(contract.get("allowedCommandSourceKinds") == sorted(ALLOWED_COMMAND_SOURCE_KINDS), "allowed source kinds mismatch")
    require(contract.get("forbiddenCommandSourceKinds") == sorted(FORBIDDEN_COMMAND_SOURCE_KINDS), "forbidden source kinds mismatch")
    require(contract.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "accepted slots mismatch")
    require(contract.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata slots mismatch")
    require(contract.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "rejected route slots mismatch")
    require(contract.get("acceptedRemoteSlot") == EXPECTED_REMOTE_SLOT, "accepted remote slot mismatch")
    require(contract.get("acceptedCommandId") == EXPECTED_COMMAND_ID, "accepted command id mismatch")
    require(contract.get("forwardsToPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "private LAN forward target mismatch")
    for key in (
        "requiresPrivateLanTransportProofHash",
        "requiresPrivateNonLoopbackAssignedAddresses",
        "rejectsDocumentationAndReservedAddressRanges",
        "requiresStructuredHostClientIdentityEvidence",
        "requiresComputedMachineFingerprintPreflight",
        "requiresRuntimeHostKindEvidence",
        "rejectsWslOrContainerRuntimeHostKind",
        "requiresVmGuestRuntimeKindForVmLabeledProof",
        "requiresNonVmRuntimeKindForPhysicalProof",
        "requiresRedactedMachineIdentityInputs",
        "requiresClientSourceNotHostAssignedLocalAddress",
        "requiresSanitizedInterfaceEvidence",
        "requiresHmacSha256SessionAuth",
        "requiresPinnedServerAndClientIdentities",
        "requiresReplayAndSequenceProtection",
        "requiresAcceptedCommandTranscriptBinding",
        "requiresSecondHostSessionSecurityHardening",
        "requiresLiveNegativeCaseTranscript",
        "supportsExplicitLiveValidationMode",
        "requiresLiveValidationModeBeforeRuntimePromotion",
        "requiresPerEventServerObservedAtUnixForLiveProof",
        "requiresMonotonicServerObservedTimestampsInsideInvitationWindowForLiveProof",
        "requiresNonFixtureMachineFingerprintSourcesForLiveProof",
        "requiresAutoPlatformRuntimeHostKindSourcesForLiveProof",
        "rejectsSyntheticLiveLabeledFixtures",
        "requiresInvitationExclusiveCreate",
        "requiresInvitationExpiryValidation",
        "requiresInvitationDeletionAfterServerCompletion",
        "requiresInvitationLifecycleReceipt",
        "requiresListenerLifecycleReceipt",
        "requiresListenerTeardownEvidence",
        "requiresListenerPostCloseConnectRejection",
        "requiresServerObservedTimestampWindow",
        "requiresTransientInvitationCredentialNotArtifactSerialized",
        "requiresVmLabeledProofSamePhysicalMachineOnly",
        "requiresPhysicalSecondHostProofNotSamePhysicalMachineOnly",
        "requiresCopiedProfileHashesOnBothSides",
        "requiresInstalledGamePrePostHashesOnBothSides",
        "requiresLocalSourceSafetyPreflightForLiveProof",
        "requiresTwoPhasePrePostSourceSafetyForLiveProof",
        "requiresOperatorSuppliedHashOnlyLiveProofRejection",
        "requiresFixtureSentinelLiveProofRejection",
        "requiresStringNumericTruthyOverclaimRejection",
        "requiresNoRawPathsInPreflightEvidence",
        "requiresProgramFilesMutationRejection",
    ):
        require(contract.get(key) is True, f"proof contract requirement missing: {key}")
    require(
        contract.get("requiredSecondHostSecurityHardeningFlags") == list(REQUIRED_SESSION_SECURITY_HARDENING_FLAGS),
        "second-host security hardening flags mismatch",
    )
    require(set(contract.get("requiredRejectedCases") or []) == EXPECTED_REJECTION_REASONS, "required rejected cases mismatch")

    evidence = object_at(payload, "currentEvidence")
    require_false_claims(
        evidence,
        (
            "acceptedLiveSecondHostCommandSourceProof",
            "acceptedLiveSecondHostRuntimeDeliveryProof",
            "hostJoinControlsMayBeEnabled",
        ),
        "current evidence",
    )
    require(evidence.get("newBeaLaunchCount") == 0, "gate must not add BEA launches")
    require(evidence.get("cdbAttachCount") == 0, "gate must not add CDB attaches")

    nonclaims = object_at(payload, "nonClaims")
    require_false_claims(nonclaims, tuple(nonclaims.keys()), "non-claim")

    release = object_at(payload, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    require_false_claims(
        release,
        (
            "secretsSerialized",
            "rawPrivateAddressPublishedToPublicDocs",
            "rawPrivateProofPathPublished",
            "privateArtifactContentPublished",
            "publicHostOrMatchmakingEndpointPublished",
            "releaseIncludedPrivateArtifact",
        ),
        "release boundary",
    )

    next_required = object_at(payload, "nextRequiredProof")
    require(next_required.get("id") == EXPECTED_NEXT_RUNTIME_PROOF_ID, "next proof id mismatch")
    require(next_required.get("requiredBeforeHostJoinEnablement") is True, "Host/Join must require later runtime proof")

    return {
        "schemaVersion": payload["schemaVersion"],
        "gateScope": payload["gateScope"],
        "acceptedLiveSecondHostCommandSourceProof": evidence["acceptedLiveSecondHostCommandSourceProof"],
        "acceptedLiveSecondHostRuntimeDeliveryProof": evidence["acceptedLiveSecondHostRuntimeDeliveryProof"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "multiHostLanPlayProof": nonclaims["multiHostLanPlayProof"],
        "publicMatchmakingProof": nonclaims["publicMatchmakingProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "activeP3P4OriginalBinaryGameplayProof": nonclaims["activeP3P4OriginalBinaryGameplayProof"],
        "newBeaLaunchCount": evidence["newBeaLaunchCount"],
        "cdbAttachCount": evidence["cdbAttachCount"],
        "requiredRejectedCaseCount": len(contract["requiredRejectedCases"]),
        "nextRequiredProof": next_required["id"],
    }


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected second-host command-source schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected second-host command-source helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected second-host command-source helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected second-host command-source protocol")


def require_private_lan_reference(bundle: dict[str, Any], path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    private_lan_path = resolve_artifact_path(path, str(bundle.get("privateLanTransportProofBundle") or ""))
    require(bundle.get("privateLanTransportProofSha256") == sha256_file(private_lan_path), "private LAN transport proof hash mismatch")
    private_lan_summary = lan.validate_bundle(private_lan_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_path)
    return private_lan_path, private_lan_summary, private_lan_bundle


def require_session_descriptor(
    bundle: dict[str, Any],
    *,
    private_lan_path: Path,
    private_lan_summary: dict[str, Any],
    private_lan_bundle: dict[str, Any],
) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "unexpected second-host session schema")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "second-host session protocol mismatch")
    require(descriptor.get("upstreamPrivateLanProtocolVersion") == lan.EXPECTED_PROTOCOL, "upstream private LAN protocol mismatch")
    require(descriptor.get("upstreamPrivateLanProofSha256") == sha256_file(private_lan_path), "upstream private LAN hash mismatch")
    require(descriptor.get("upstreamPrivateLanTransport") == private_lan_summary["transport"], "upstream private LAN transport mismatch")
    require(descriptor.get("sessionCompatibilityKey") == upstream_descriptor["sessionCompatibilityKey"], "session compatibility key mismatch")
    require(descriptor.get("cleanSpecimenSha256") == upstream_descriptor["cleanSpecimenSha256"], "clean specimen hash mismatch")
    require(descriptor.get("allowedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "accepted gameplay slots must stay P1/P2")
    require(descriptor.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata-only slots must stay P3/P4")
    require(descriptor.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "P3/P4 gameplay routes must be rejected")
    require(descriptor.get("remotePlayerSlot") == EXPECTED_REMOTE_SLOT, "second-host command-source proof must target P2")
    require(descriptor.get("allowedCommand") == EXPECTED_REMOTE_COMMAND, "second-host command mismatch")
    require(descriptor.get("upstreamPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "private LAN forward target mismatch")
    require(descriptor.get("levelId") == 850, "session level must remain 850")
    require(descriptor.get("controllerConfiguration") == 1, "session controller configuration must remain 1")
    require(descriptor.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 gameplay proof must remain false")
    require(descriptor.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must remain zero")
    return descriptor


def require_transport(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == EXPECTED_TRANSPORT, "unexpected second-host transport")
    require(transport.get("networkScope") == "distinct-private-host-command-source-not-online-play", "unexpected network scope")
    source_kind = str(transport.get("commandSourceKind") or "")
    require(source_kind in ALLOWED_COMMAND_SOURCE_KINDS, f"forbidden command source kind: {source_kind}")
    require(source_kind not in FORBIDDEN_COMMAND_SOURCE_KINDS, f"forbidden command source kind accepted: {source_kind}")
    host_address = str(transport.get("hostBindAddress") or "")
    client_address = str(transport.get("clientSourceAddress") or "")
    require(ip_is_private_lan_non_loopback(host_address), "host bind address must be RFC1918/ULA private LAN and non-loopback")
    require(ip_is_private_lan_non_loopback(client_address), "client source address must be RFC1918/ULA private LAN and non-loopback")
    require(client_address != host_address, "client source address must differ from host bind address")
    require(transport.get("hostPrivateInterfaceBound") is True, "host private interface was not bound")
    require(transport.get("hostAddressAssignedToLocalInterface") is True, "host address must be assigned to a local interface")
    require(transport.get("clientSourceAddressNotHostAssignedLocalAddress") is True, "client source must not be a host-local address")
    require(transport.get("sanitizedHostAndClientInterfaceEvidence") is True, "sanitized interface evidence missing")
    require(transport.get("secondHostCommandSourceProof") is True, "second-host command-source proof flag missing")
    if source_kind == "distinct-physical-host-private-lan":
        require(transport.get("secondPhysicalHostProof") is True, "physical second-host proof flag missing")
        require(transport.get("vmLabeledOnly") is False, "physical second-host proof cannot be VM-labeled only")
        require(transport.get("samePhysicalMachineOnly") is False, "physical second-host proof cannot be same-physical-machine only")
    else:
        require(transport.get("secondPhysicalHostProof") is False, "VM-labeled proof must not claim physical second host")
        require(transport.get("vmLabeledOnly") is True, "VM proof must be labeled VM-only")
        require(transport.get("samePhysicalMachineOnly") is True, "VM-labeled proof must remain same-physical-machine only")
    for key in (
        "sameWorkstationOnly",
        "wslOnHost",
        "loopbackInterfaceOnly",
        "publicNetworkSocketsOpened",
        "multiHostLanPlayProof",
        "publicMatchmakingProof",
        "publicServerProof",
        "nativeBeaNetcodeProof",
        "natTraversalProof",
        "deterministicSyncProof",
        "rollbackProof",
        "antiCheatProof",
        "gameInputSentBySecondHostClient",
        "hostHelperInputSent",
    ):
        require(transport.get(key) is False, f"transport overclaim must remain false: {key}")
    return transport


def require_network_identity_evidence(bundle: dict[str, Any], transport: dict[str, Any]) -> dict[str, Any]:
    evidence = object_at(bundle, "networkIdentityEvidence")
    host = object_at(evidence, "host")
    client = object_at(evidence, "client")
    runtime_markers = object_at(evidence, "runtimeMarkers")

    host_fingerprint = host.get("machineFingerprint")
    client_fingerprint = client.get("machineFingerprint")
    require(is_hex64(host_fingerprint), "host machine fingerprint must be lowercase sha256 hex")
    require(is_hex64(client_fingerprint), "client machine fingerprint must be lowercase sha256 hex")
    require(host_fingerprint != client_fingerprint, "host and client machine fingerprints must differ")
    require(host.get("hostIdentityObserved") is True, "host identity observation missing")
    require(client.get("clientIdentityObserved") is True, "client identity observation missing")
    for label, row in (("host", host), ("client", client)):
        require(row.get("machineFingerprintComputedByPreflight") is True, f"{label} machine fingerprint was not computed by preflight")
        require(
            row.get("machineFingerprintSource") in {"local-hostname-platform-preflight", "self-test-fixture"},
            f"{label} machine fingerprint source mismatch",
        )
        require(row.get("machineFingerprintInputsRedacted") is True, f"{label} machine fingerprint inputs were not redacted")
        require(is_hex64(row.get("hostnameFingerprint")), f"{label} hostname fingerprint missing")
        require(is_hex64(row.get("platformFingerprint")), f"{label} platform fingerprint missing")
        runtime_kind = str(row.get("runtimeHostKind") or "")
        require(runtime_kind in ALLOWED_RUNTIME_HOST_KINDS, f"{label} runtime host kind is not accepted: {runtime_kind}")
        require(runtime_kind not in FORBIDDEN_RUNTIME_HOST_KINDS, f"{label} runtime host kind is forbidden: {runtime_kind}")
        require(
            row.get("runtimeHostKindSource") in {"auto-platform-preflight", "operator-supplied-runtime-host-kind", "self-test-fixture"},
            f"{label} runtime host kind source mismatch",
        )
        require(row.get("runtimeHostKindInputsRedacted") is True, f"{label} runtime host kind inputs were not redacted")
        require(row.get("wslDetectedByPreflight") is False, f"{label} WSL runtime must not be accepted")
        require(row.get("containerDetectedByPreflight") is False, f"{label} container runtime must not be accepted")

    client_runtime_kind = str(client.get("runtimeHostKind") or "")
    if transport["commandSourceKind"] == "distinct-vm-private-lan-labeled-vm-only":
        require(client_runtime_kind == "vm-guest", "VM-labeled proof requires vm-guest client runtime kind")
    else:
        require(client_runtime_kind != "vm-guest", "physical proof cannot use vm-guest client runtime kind")

    host_addresses = list_at(host, "assignedPrivateAddresses")
    require(all(isinstance(row, str) and ip_is_private_lan_non_loopback(row) for row in host_addresses), "host assigned addresses must be RFC1918/ULA private LAN addresses")
    host_address = str(transport.get("hostBindAddress") or "")
    client_address = str(transport.get("clientSourceAddress") or "")
    require(host_address in host_addresses, "host bind address must appear in sanitized host interface evidence")
    require(client_address not in host_addresses, "client source address must not appear in sanitized host interface evidence")
    require(client.get("observedSourceAddress") == client_address, "observed client source address mismatch")
    require(client.get("sourceAddressAssignedToClientInterface") is True, "client source address must be assigned to client interface")
    require(client.get("sourceAddressAssignedToHostInterface") is False, "client source address must not be assigned to host interface")
    require(client.get("vmLabeledOnly") is (transport["commandSourceKind"] == "distinct-vm-private-lan-labeled-vm-only"), "VM label must match command-source kind")

    for key in (
        "sameMachineSid",
        "sameBootId",
        "sameWindowsComputerName",
        "wslDetectedOnHost",
        "wslDetectedOnClient",
        "containerDetectedOnHost",
        "containerDetectedOnClient",
        "loopbackObserved",
        "publicRoutablePeerObserved",
    ):
        require(runtime_markers.get(key) is False, f"runtime marker overclaim must remain false: {key}")
    return evidence


def require_invitation_lifecycle(bundle: dict[str, Any]) -> dict[str, Any]:
    lifecycle = object_at(bundle, "invitationLifecycle")
    require(
        lifecycle.get("schemaVersion") == "winui-original-binary-second-host-invitation-lifecycle.v1",
        "invitation lifecycle schema mismatch",
    )
    require(lifecycle.get("rootClass") == "os-temp-outside-repo", "invitation root class mismatch")
    require(lifecycle.get("exclusiveCreateSucceeded") is True, "invitation exclusive create receipt missing")
    require(lifecycle.get("deletionAttempted") is True, "invitation deletion attempt receipt missing")
    require(lifecycle.get("deletionSucceeded") is True, "invitation deletion success receipt missing")
    require(lifecycle.get("postDeleteExists") is False, "invitation must not exist after deletion")
    require(lifecycle.get("rawInvitationPathSerialized") is False, "raw invitation path must not be serialized")
    require(lifecycle.get("rawServerAddressSerializedInReceipt") is False, "raw server address must not be serialized in receipt")
    require(lifecycle.get("privateMaterialSerialized") is False, "private invitation material must not be serialized")
    require(is_hex64(lifecycle.get("sanitizedInvitationDescriptorSha256")), "sanitized invitation descriptor hash missing")
    try:
        issued = int(lifecycle["issuedAtUnix"])
        expires = int(lifecycle["expiresAtUnix"])
        nonce = int(lifecycle["nonceWindowSeconds"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondHostCommandSourceProofError("invitation lifecycle timestamps are invalid") from exc
    require(expires > issued, "invitation lifecycle expiry must be after issue time")
    require(nonce == 30, "invitation nonce window mismatch")
    return lifecycle


def require_listener_lifecycle(bundle: dict[str, Any]) -> dict[str, Any]:
    lifecycle = object_at(bundle, "listenerLifecycle")
    require(
        lifecycle.get("schemaVersion") == "winui-original-binary-second-host-listener-lifecycle.v1",
        "listener lifecycle schema mismatch",
    )
    require(
        lifecycle.get("evidenceMode") in {"live-server-socket-receipt", "self-test-fixture"},
        "listener lifecycle evidence mode mismatch",
    )
    require(lifecycle.get("bindAddress") == object_at(bundle, "transport").get("hostBindAddress"), "listener bind address mismatch")
    require(lifecycle.get("bindAddressClass") == "private-lan-non-loopback", "listener bind address class mismatch")
    require(is_hex64(lifecycle.get("sanitizedEndpointSha256")), "listener sanitized endpoint hash missing")
    require(lifecycle.get("socketFamily") == "AF_INET", "listener socket family mismatch")
    require(lifecycle.get("bindAttempted") is True, "listener bind attempt receipt missing")
    require(lifecycle.get("bindSucceeded") is True, "listener bind success receipt missing")
    require(lifecycle.get("boundHostMatchesTransport") is True, "listener bound host/transport mismatch")
    require(lifecycle.get("hostPrivateInterfaceBound") is True, "listener private interface bind missing")
    require(lifecycle.get("wildcardBind") is False, "listener wildcard bind must be false")
    require(lifecycle.get("loopbackBind") is False, "listener loopback bind must be false")
    require(lifecycle.get("publicRoutableBind") is False, "listener public bind must be false")
    require(lifecycle.get("publicEndpointPublished") is False, "listener public endpoint publication must be false")
    require(lifecycle.get("listenSucceeded") is True, "listener listen success receipt missing")
    require(lifecycle.get("listenerStarted") is True, "listener start receipt missing")
    require(lifecycle.get("listenerAcceptLimit") == 1, "listener accept limit mismatch")
    require(lifecycle.get("closeAttempted") is True, "listener close attempt receipt missing")
    require(lifecycle.get("closeSucceeded") is True, "listener close success receipt missing")
    require(lifecycle.get("listenerClosedBeforeBundleWrite") is True, "listener close receipt missing")
    require(lifecycle.get("teardownObserved") is True, "listener teardown receipt missing")
    require(lifecycle.get("postCloseConnectRejected") is True, "listener post-close connect rejection receipt missing")
    require(lifecycle.get("portValueSerializedInPublicDocs") is False, "listener port must not be serialized in public docs")
    return lifecycle


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "transient-os-temp-invitation-not-artifact-serialized", "credential storage boundary mismatch")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must be absent")
    require(
        authorization.get("credentialTransportToClient") == "os-temp-invitation-json-exclusive-create-deleted-after-server-completion",
        "client credential transport boundary mismatch",
    )
    require(
        authorization.get("credentialTransportToServer") == "generated-in-memory-and-never-written-to-proof-artifact",
        "server credential transport boundary mismatch",
    )
    require(is_hex64(authorization.get("authKeyFingerprint")), "auth key fingerprint must be lowercase sha256 hex")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(authorization.get("clientIdentityMode") == "pinned-fingerprint", "client identity mode mismatch")
    require(is_hex64(authorization.get("serverIdentityFingerprint")), "server identity fingerprint must be lowercase sha256 hex")
    require(is_hex64(authorization.get("clientIdentityFingerprint")), "client identity fingerprint must be lowercase sha256 hex")
    require(authorization["serverIdentityFingerprint"] != authorization["clientIdentityFingerprint"], "server and client identities must differ")
    require(authorization.get("sessionScopedAuthentication") is True, "session-scoped auth missing")
    require(authorization.get("replayCacheEnabled") is True, "replay cache missing")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement missing")
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window mismatch")
    rate_limit = object_at(authorization, "rateLimit")
    require(rate_limit.get("maxAcceptedCommandsPerSession") == 1, "accepted command rate limit mismatch")
    require(rate_limit.get("maxCommandsPerSecond") == 1, "per-second rate limit mismatch")
    return authorization


def require_source_safety(bundle: dict[str, Any]) -> dict[str, Any]:
    safety = object_at(bundle, "sourceSafety")
    mode = safety.get("evidenceMode")
    require(mode in {"local-preflight-computed", "self-test-fixture"}, "source safety evidence mode mismatch")
    require(safety.get("computedByPreflight") is True, "source safety must be computed by preflight")
    require(safety.get("pathValuesPublished") is False, "source safety must not publish raw path values")
    require(safety.get("absolutePathsSerialized") is False, "source safety must not serialize absolute paths")
    for key in (
        "copiedProfileHashesOnBothSides",
        "installedGamePrePostHashesOnBothSides",
        "prePostHashSamplesOnBothSides",
        "installedGameHashesUnchangedOnHost",
        "installedGameHashesUnchangedOnClient",
        "copiedProfileRootUsedOnHost",
        "copiedProfileRootUsedOnClient",
        "programFilesMutationRejected",
        "originalExeMutationRejected",
    ):
        require(safety.get(key) is True, f"source safety requirement missing: {key}")
    for key in (
        "installedGameMutationAllowed",
        "originalExeMutationAllowed",
        "programFilesMutationTargetUsed",
        "sourceInstallPatchedInPlace",
    ):
        require(safety.get(key) is False, f"source safety overclaim must remain false: {key}")
    for side in ("host", "client"):
        side_evidence = object_at(safety, side)
        side_mode = side_evidence.get("sourceEvidenceMode")
        require(side_mode in {"local-preflight-computed", "self-test-fixture"}, f"{side} source evidence mode mismatch")
        require(side_evidence.get("computedByPreflight") is True, f"{side} source evidence was not computed by preflight")
        require(side_evidence.get("pathValuesPublished") is False, f"{side} source evidence published raw paths")
        require(side_evidence.get("absolutePathsSerialized") is False, f"{side} source evidence serialized absolute paths")
        require(side_evidence.get("copiedProfileRootClass") == "app-owned-or-private-proof-root", f"{side} copied profile root class mismatch")
        require(side_evidence.get("installedGameRootClass") == "source-install-read-only", f"{side} installed game root class mismatch")
        copied_mode = side_evidence.get("copiedProfileHashMode")
        installed_mode = side_evidence.get("installedGameHashMode")
        allowed_modes = {"file-sha256", "directory-manifest-sha256"}
        if side_mode == "self-test-fixture":
            allowed_modes = allowed_modes | {"operator-supplied-sha256"}
        require(copied_mode in allowed_modes, f"{side} copied profile hash mode mismatch")
        require(installed_mode in allowed_modes, f"{side} installed game hash mode mismatch")
        require(isinstance(side_evidence.get("copiedProfileFileCount"), int), f"{side} copied profile file count missing")
        require(isinstance(side_evidence.get("installedGameFileCount"), int), f"{side} installed game file count missing")
        sampling_mode = side_evidence.get("prePostHashSamplingMode")
        require(
            sampling_mode in {"single-sample-preflight", "live-pre-post", "self-test-fixture"},
            f"{side} source safety sampling mode mismatch",
        )
        require(isinstance(side_evidence.get("prePostHashSampleCount"), int), f"{side} source safety sample count missing")
        require(isinstance(side_evidence.get("prePostHashSamplesDistinct"), bool), f"{side} source safety sample distinction missing")
        if side_mode == "local-preflight-computed":
            require(side_evidence["copiedProfileFileCount"] > 0, f"{side} copied profile preflight did not hash files")
            require(side_evidence["installedGameFileCount"] > 0, f"{side} installed game preflight did not hash files")
        require(is_hex64(side_evidence.get("copiedProfileSha256Before")), f"{side} copied profile pre-hash missing")
        require(side_evidence.get("copiedProfileSha256Before") == side_evidence.get("copiedProfileSha256After"), f"{side} copied profile hash drifted")
        require(is_hex64(side_evidence.get("installedGameSha256Before")), f"{side} installed game pre-hash missing")
        require(side_evidence.get("installedGameSha256Before") == side_evidence.get("installedGameSha256After"), f"{side} installed game hash drifted")
        require(side_evidence.get("programFilesMutationAttempted") is False, f"{side} Program Files mutation attempted")
    return safety


def require_commands(bundle: dict[str, Any], transcript: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    rejected = list_at(commands, "rejected")
    require(len(accepted) == 1 and isinstance(accepted[0], dict), "expected exactly one accepted command")
    accepted_command = accepted[0]
    require(
        set(accepted_command.keys())
        == {
            "commandId",
            "remoteSlot",
            "command",
            "requestEvent",
            "requestPayloadSha256",
            "responseEvent",
            "responsePayloadSha256",
            "authorizationStatus",
            "secondHostClientAccepted",
            "wouldForwardToPrivateLanCommandId",
            "gameInputSentBySecondHostClient",
            "hostHelperInputSent",
        },
        "accepted command key set mismatch",
    )
    transcript_hashes = {
        str(row.get("kind") or ""): str(row.get("payloadSha256") or "")
        for row in list_at(transcript, "events")
        if isinstance(row, dict)
    }
    require(accepted_command.get("commandId") == EXPECTED_COMMAND_ID, "accepted command id mismatch")
    require(accepted_command.get("remoteSlot") == EXPECTED_REMOTE_SLOT, "accepted command must target P2")
    require(accepted_command.get("command") == EXPECTED_REMOTE_COMMAND, "accepted command mismatch")
    require(accepted_command.get("requestEvent") == "client_command_p2_forward", "accepted command request event mismatch")
    require(accepted_command.get("responseEvent") == "server_command_accepted", "accepted command response event mismatch")
    require(is_hex64(accepted_command.get("requestPayloadSha256")), "accepted command request payload hash missing")
    require(is_hex64(accepted_command.get("responsePayloadSha256")), "accepted command response payload hash missing")
    require(
        accepted_command["requestPayloadSha256"] == transcript_hashes.get(str(accepted_command["requestEvent"])),
        "accepted command request payload hash does not match transcript",
    )
    require(
        accepted_command["responsePayloadSha256"] == transcript_hashes.get(str(accepted_command["responseEvent"])),
        "accepted command response payload hash does not match transcript",
    )
    require(accepted_command.get("authorizationStatus") == "accepted-hmac-sha256", "authorization status mismatch")
    require(accepted_command.get("secondHostClientAccepted") is True, "accepted command flag missing")
    require(accepted_command.get("wouldForwardToPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "private LAN forward target mismatch")
    require(accepted_command.get("gameInputSentBySecondHostClient") is False, "second-host client must not send direct game input")
    require(accepted_command.get("hostHelperInputSent") is False, "second-host client must not send host-helper input")
    reasons = {str(row.get("reason") or "") for row in rejected if isinstance(row, dict)}
    require(EXPECTED_REJECTION_REASONS.issubset(reasons), "missing required second-host rejection rows")
    for row in rejected:
        require(isinstance(row, dict), "rejected row must be an object")
        require(set(row.keys()) == {"commandId", "reason", "secondHostClientAccepted"}, "rejected command key set mismatch")
        require(row.get("secondHostClientAccepted") is False, "rejected command was accepted")
    return accepted_command


def require_transcript(bundle: dict[str, Any], authorization: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "transportTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "transcript protocol mismatch")
    require(transcript.get("serverIdentityFingerprint") == authorization["serverIdentityFingerprint"], "server fingerprint mismatch")
    require(transcript.get("clientIdentityFingerprint") == authorization["clientIdentityFingerprint"], "client fingerprint mismatch")
    require(transcript.get("messageCount") == len(EXPECTED_TRANSCRIPT_EVENTS), "transcript message count mismatch")
    events = list_at(transcript, "events")
    require(len(events) == len(EXPECTED_TRANSCRIPT_EVENTS), "transcript event count mismatch")
    kinds = []
    for row in events:
        require(isinstance(row, dict), "transcript event must be an object")
        require(set(row.keys()).issubset({"kind", "payloadSha256", "serverObservedAtUnix"}), "transcript event key set mismatch")
        kinds.append(row.get("kind"))
        require(is_hex64(row.get("payloadSha256")), f"transcript event payload hash missing: {row.get('kind')}")
    require(kinds == EXPECTED_TRANSCRIPT_EVENTS, "transcript event sequence mismatch")
    return transcript


def require_session_security_hardening(bundle: dict[str, Any], transcript: dict[str, Any]) -> dict[str, Any] | None:
    hardening = bundle.get("sessionSecurityHardening")
    if hardening is None:
        return None
    require(isinstance(hardening, dict), "sessionSecurityHardening must be an object")
    evidence_mode = hardening.get("evidenceMode")
    require(
        evidence_mode in {"live-server-client-transcript", "self-test-fixture"},
        "sessionSecurityHardening evidence mode mismatch",
    )
    require(hardening.get("requiredBeforeAcceptedLiveRuntimeDelivery") is True, "hardening must gate live runtime delivery")
    require(hardening.get("caseCount") == len(SESSION_SECURITY_HARDENING_CASES), "hardening case count mismatch")
    require(
        hardening.get("liveNegativeCaseTranscript") is (evidence_mode == "live-server-client-transcript"),
        "live negative-case transcript flag mismatch",
    )
    transcript_hashes = {
        str(row.get("kind") or ""): str(row.get("payloadSha256") or "")
        for row in list_at(transcript, "events")
        if isinstance(row, dict)
    }
    cases = list_at(hardening, "cases")
    require(len(cases) == len(SESSION_SECURITY_HARDENING_CASES), "hardening cases length mismatch")
    cases_by_flag = {str(row.get("flag") or ""): row for row in cases if isinstance(row, dict)}
    require(set(cases_by_flag) == set(REQUIRED_SESSION_SECURITY_HARDENING_FLAGS), "hardening flags mismatch")
    for flag in REQUIRED_SESSION_SECURITY_HARDENING_FLAGS:
        expected = SESSION_SECURITY_HARDENING_CASES[flag]
        row = cases_by_flag[flag]
        require(hardening.get(flag) is True, f"hardening flag must be true: {flag}")
        require(row.get("caseId") == expected["caseId"], f"hardening case id mismatch: {flag}")
        require(row.get("rejectionReason") == expected["reason"], f"hardening rejection reason mismatch: {flag}")
        require(row.get("accepted") is False, f"hardening negative case was accepted: {flag}")
        require(row.get("liveTranscriptObserved") is (evidence_mode == "live-server-client-transcript"), f"hardening transcript flag mismatch: {flag}")
        request_events = row.get("requestEvents")
        response_events = row.get("responseEvents")
        require(request_events == expected["requestEvents"], f"hardening request events mismatch: {flag}")
        require(response_events == expected["responseEvents"], f"hardening response events mismatch: {flag}")
        for event in [*expected["requestEvents"], *expected["responseEvents"]]:
            require(event in transcript_hashes, f"hardening transcript missing event {event}")
        if evidence_mode == "live-server-client-transcript":
            request_hashes = row.get("requestPayloadSha256ByEvent")
            response_hashes = row.get("responsePayloadSha256ByEvent")
            require(isinstance(request_hashes, dict), f"hardening request payload hashes missing: {flag}")
            require(isinstance(response_hashes, dict), f"hardening response payload hashes missing: {flag}")
            require(set(request_hashes) == set(expected["requestEvents"]), f"hardening request payload hash keys mismatch: {flag}")
            require(set(response_hashes) == set(expected["responseEvents"]), f"hardening response payload hash keys mismatch: {flag}")
            for event in expected["requestEvents"]:
                require(request_hashes[event] == transcript_hashes[event], f"hardening request payload hash mismatch: {flag}:{event}")
            for event in expected["responseEvents"]:
                require(response_hashes[event] == transcript_hashes[event], f"hardening response payload hash mismatch: {flag}:{event}")
        else:
            require("requestPayloadSha256ByEvent" not in row, f"self-test hardening must not carry live request hashes: {flag}")
            require("responsePayloadSha256ByEvent" not in row, f"self-test hardening must not carry live response hashes: {flag}")
    return hardening


def require_nonclaims_and_release(bundle: dict[str, Any]) -> dict[str, Any]:
    nonclaims = object_at(bundle, "nonClaims")
    require(set(nonclaims.keys()) == set(EXPECTED_NONCLAIM_FALSE_KEYS) | {"newBeaLaunchCount", "cdbAttachCount", "nPlayerOriginalBinaryRuntimeProof"}, "non-claim key set mismatch")
    for key in EXPECTED_NONCLAIM_FALSE_KEYS:
        require(nonclaims.get(key) is False, f"non-claim must remain false: {key}")
    require(nonclaims.get("newBeaLaunchCount") == 0, "command-source proof must not launch BEA")
    require(nonclaims.get("cdbAttachCount") == 0, "command-source proof must not attach CDB")
    require(nonclaims.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must remain zero")
    release = object_at(bundle, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    require(set(release.keys()) == set(EXPECTED_RELEASE_FALSE_KEYS) | {"privateProofReleaseExcludedByPolicy"}, "release boundary key set mismatch")
    for key in EXPECTED_RELEASE_FALSE_KEYS:
        require(release.get(key) is False, f"release boundary must remain false: {key}")
    return nonclaims


def require_live_promotion_evidence(
    safety: dict[str, Any],
    hardening: dict[str, Any] | None,
    authorization: dict[str, Any],
    invitation: dict[str, Any],
    listener: dict[str, Any],
    transcript: dict[str, Any],
    network_identity: dict[str, Any],
    transport: dict[str, Any],
) -> None:
    require(hardening is not None, "live command-source validation requires sessionSecurityHardening")
    require(hardening.get("evidenceMode") == "live-server-client-transcript", "live validation requires live hardening transcript evidence")
    require(safety.get("evidenceMode") == "local-preflight-computed", "live validation requires local-preflight-computed source safety")
    require(listener.get("evidenceMode") == "live-server-socket-receipt", "live validation requires live listener lifecycle evidence")
    try:
        issued = int(invitation["issuedAtUnix"])
        expires = int(invitation["expiresAtUnix"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondHostCommandSourceProofError("live validation requires invitation issue/expiry timestamps") from exc
    require(issued >= MIN_REALISTIC_LIVE_UNIX_TIMESTAMP, "live validation rejects fixture invitation timestamps")
    require(expires > issued, "live validation requires invitation expiry after issue time")
    observed_timestamps: list[int] = []
    for row in list_at(transcript, "events"):
        try:
            observed_timestamps.append(int(row["serverObservedAtUnix"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise SecondHostCommandSourceProofError("live validation requires per-event serverObservedAtUnix timestamps") from exc
    require(observed_timestamps == sorted(observed_timestamps), "live validation requires monotonic server-observed transcript timestamps")
    require(observed_timestamps[0] >= issued, "live transcript starts before invitation issue time")
    require(observed_timestamps[-1] <= expires, "live transcript ends after invitation expiry time")
    require(transport.get("hostBindAddress") != FIXTURE_HOST_ADDRESS, "live validation rejects fixture host address")
    require(transport.get("clientSourceAddress") != FIXTURE_CLIENT_ADDRESS, "live validation rejects fixture client address")
    for key in ("authKeyFingerprint", "serverIdentityFingerprint", "clientIdentityFingerprint"):
        require_not_fixture_hex64(authorization.get(key), f"authorization.{key}")
    if transport.get("commandSourceKind") == "distinct-physical-host-private-lan":
        for side in ("host", "client"):
            side_identity = object_at(network_identity, side)
            require(
                side_identity.get("runtimeHostKindSource") != "operator-supplied-runtime-host-kind",
                f"live physical validation rejects operator-supplied runtime host kind for {side}",
            )
    for side in ("host", "client"):
        side_identity = object_at(network_identity, side)
        for key in ("machineFingerprint", "hostnameFingerprint", "platformFingerprint"):
            require_not_fixture_hex64(side_identity.get(key), f"networkIdentityEvidence.{side}.{key}")
        require(
            side_identity.get("machineFingerprintSource") == "local-hostname-platform-preflight",
            f"live validation requires non-fixture machine fingerprint evidence for {side}",
        )
        require(
            side_identity.get("runtimeHostKindSource") == "auto-platform-preflight",
            f"live validation requires auto-detected runtime host kind for {side}",
        )
        side_evidence = object_at(safety, side)
        require(side_evidence.get("sourceEvidenceMode") == "local-preflight-computed", f"live validation requires local source evidence for {side}")
        require(side_evidence.get("copiedProfileHashMode") in {"file-sha256", "directory-manifest-sha256"}, f"live validation rejects operator-supplied copied-profile hash for {side}")
        require(side_evidence.get("installedGameHashMode") in {"file-sha256", "directory-manifest-sha256"}, f"live validation rejects operator-supplied installed-game hash for {side}")
        require(side_evidence.get("copiedProfileFileCount", 0) > 0, f"live validation requires copied-profile file count for {side}")
        require(side_evidence.get("installedGameFileCount", 0) > 0, f"live validation requires installed-game file count for {side}")
        require(side_evidence.get("prePostHashSamplingMode") == "live-pre-post", f"live validation requires live pre/post hash sampling for {side}")
        require(side_evidence.get("prePostHashSampleCount") == 2, f"live validation requires two source-safety samples for {side}")
        require(side_evidence.get("prePostHashSamplesDistinct") is True, f"live validation requires distinct pre/post source-safety samples for {side}")
        for key in (
            "copiedProfileSha256Before",
            "copiedProfileSha256After",
            "installedGameSha256Before",
            "installedGameSha256After",
        ):
            require_not_fixture_hex64(side_evidence.get(key), f"sourceSafety.{side}.{key}")


def require_not_fixture_hex64(value: Any, label: str) -> None:
    require(value not in FIXTURE_HEX64_SENTINELS, f"live validation rejects fixture sentinel value at {label}")


def validate_bundle(path: Path, *, require_live: bool = False) -> dict[str, Any]:
    path = path.resolve()
    bundle = read_json(path)
    require_no_sensitive_string_values(bundle)
    require_no_hidden_truthy_overclaim_flags(bundle)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    private_lan_path, private_lan_summary, private_lan_bundle = require_private_lan_reference(bundle, path)
    descriptor = require_session_descriptor(
        bundle,
        private_lan_path=private_lan_path,
        private_lan_summary=private_lan_summary,
        private_lan_bundle=private_lan_bundle,
    )
    transport = require_transport(bundle)
    network_identity = require_network_identity_evidence(bundle, transport)
    authorization = require_authorization(bundle)
    invitation = require_invitation_lifecycle(bundle)
    listener = require_listener_lifecycle(bundle)
    transcript = require_transcript(bundle, authorization)
    source_safety = require_source_safety(bundle)
    accepted_command = require_commands(bundle, transcript)
    hardening = require_session_security_hardening(bundle, transcript)
    if require_live:
        require_live_promotion_evidence(source_safety, hardening, authorization, invitation, listener, transcript, network_identity, transport)
    nonclaims = require_nonclaims_and_release(bundle)
    claim = str(bundle.get("claimBoundary") or "")
    for token in (
        "second-host/private-LAN command-source proof only",
        "does not prove player-ready online multiplayer",
        "does not prove multi-host LAN play",
        "does not prove native BEA netcode",
        "does not prove active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": path.name,
        "schemaVersion": bundle["schemaVersion"],
        "transport": transport["transport"],
        "networkScope": transport["networkScope"],
        "commandSourceKind": transport["commandSourceKind"],
        "secondHostCommandSourceProof": transport["secondHostCommandSourceProof"],
        "acceptedLiveSecondHostCommandSourceProof": require_live,
        "secondPhysicalHostProof": transport["secondPhysicalHostProof"],
        "acceptedOriginalBinaryGameplaySlots": descriptor["allowedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": descriptor["metadataOnlySlots"],
        "acceptedCommandId": accepted_command["commandId"],
        "wouldForwardToPrivateLanCommandId": accepted_command["wouldForwardToPrivateLanCommandId"],
        "gameInputSentBySecondHostClient": accepted_command["gameInputSentBySecondHostClient"],
        "hostHelperInputSent": accepted_command["hostHelperInputSent"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "multiHostLanPlayProof": nonclaims["multiHostLanPlayProof"],
        "publicMatchmakingProof": nonclaims["publicMatchmakingProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "nPlayerOriginalBinaryRuntimeProof": nonclaims["nPlayerOriginalBinaryRuntimeProof"],
        "sessionSecurityHardeningPresent": hardening is not None,
        "sessionSecurityHardeningEvidenceMode": None if hardening is None else hardening["evidenceMode"],
        "listenerLifecycleEvidenceMode": listener["evidenceMode"],
        "liveValidationMode": require_live,
        "privateLanTransportProofBundle": private_lan_path.relative_to(path.parent).as_posix(),
        "upstreamPrivateLanAcceptedCommandId": private_lan_summary["acceptedCommandId"],
    }


def make_session_security_hardening_fixture(evidence_mode: str = "self-test-fixture") -> dict[str, Any]:
    require(
        evidence_mode in {"live-server-client-transcript", "self-test-fixture"},
        "security hardening fixture evidence mode mismatch",
    )
    live_observed = evidence_mode == "live-server-client-transcript"
    hardening: dict[str, Any] = {
        "evidenceMode": evidence_mode,
        "requiredBeforeAcceptedLiveRuntimeDelivery": True,
        "liveNegativeCaseTranscript": live_observed,
        "caseCount": len(SESSION_SECURITY_HARDENING_CASES),
        "cases": [],
    }
    for flag in REQUIRED_SESSION_SECURITY_HARDENING_FLAGS:
        expected = SESSION_SECURITY_HARDENING_CASES[flag]
        hardening[flag] = True
        hardening["cases"].append(
            {
                "flag": flag,
                "caseId": expected["caseId"],
                "rejectionReason": expected["reason"],
                "requestEvents": expected["requestEvents"],
                "responseEvents": expected["responseEvents"],
                "accepted": False,
                "liveTranscriptObserved": live_observed,
            }
        )
    return hardening


def make_bundle_fixture(
    root: Path,
    *,
    command_source_kind: str = "distinct-vm-private-lan-labeled-vm-only",
    host_address: str = FIXTURE_HOST_ADDRESS,
    client_source_address: str = FIXTURE_CLIENT_ADDRESS,
    p3_gameplay_claim: bool = False,
    multi_host_play_claim: bool = False,
    native_netcode_claim: bool = False,
    copied_hashes: bool = True,
    installed_hashes: bool = True,
    include_security_hardening: bool = False,
    security_hardening_evidence_mode: str = "self-test-fixture",
    source_safety_evidence_mode: str = "self-test-fixture",
    listener_evidence_mode: str | None = None,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    private_lan_path = lan.make_bundle_fixture(root / "private-lan")
    private_lan_bundle = read_json(private_lan_path)
    private_lan_summary = lan.validate_bundle(private_lan_path, expected_controller_configuration=1)
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    second_physical = command_source_kind == "distinct-physical-host-private-lan"
    transcript_events = [
        {"kind": kind, "payloadSha256": f"{index % 16:x}" * 64}
        for index, kind in enumerate(EXPECTED_TRANSCRIPT_EVENTS, start=1)
    ]
    transcript_hashes = {row["kind"]: row["payloadSha256"] for row in transcript_events}
    auth = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "transient-os-temp-invitation-not-artifact-serialized",
        "serializedCredentialPresent": False,
        "credentialTransportToClient": "os-temp-invitation-json-exclusive-create-deleted-after-server-completion",
        "credentialTransportToServer": "generated-in-memory-and-never-written-to-proof-artifact",
        "authKeyFingerprint": "a" * 64,
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": "b" * 64,
        "clientIdentityMode": "pinned-fingerprint",
        "clientIdentityFingerprint": "c" * 64,
        "sessionScopedAuthentication": True,
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
    }
    source_hash_mode = "operator-supplied-sha256"
    source_file_count = 0
    if source_safety_evidence_mode == "local-preflight-computed":
        source_hash_mode = "directory-manifest-sha256"
        source_file_count = 12
        source_sampling_mode = "live-pre-post"
        source_sample_count = 2
        source_samples_distinct = True
    else:
        source_sampling_mode = "self-test-fixture"
        source_sample_count = 2
        source_samples_distinct = True
    listener_evidence_mode = listener_evidence_mode or (
        "live-server-socket-receipt"
        if source_safety_evidence_mode == "local-preflight-computed"
        else "self-test-fixture"
    )
    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "privateLanTransportProofBundle": private_lan_path.resolve().relative_to(root.resolve()).as_posix(),
        "privateLanTransportProofSha256": sha256_file(private_lan_path),
        "sessionDescriptor": {
            "schemaVersion": EXPECTED_SESSION_SCHEMA,
            "protocolVersion": EXPECTED_PROTOCOL,
            "upstreamPrivateLanProtocolVersion": lan.EXPECTED_PROTOCOL,
            "upstreamPrivateLanProofSha256": sha256_file(private_lan_path),
            "upstreamPrivateLanTransport": private_lan_summary["transport"],
            "sessionCompatibilityKey": upstream_descriptor["sessionCompatibilityKey"],
            "cleanSpecimenSha256": upstream_descriptor["cleanSpecimenSha256"],
            "allowedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
            "remotePlayerSlot": EXPECTED_REMOTE_SLOT,
            "allowedCommand": EXPECTED_REMOTE_COMMAND,
            "upstreamPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
            "levelId": 850,
            "controllerConfiguration": 1,
            "activeP3P4OriginalBinaryGameplayProof": p3_gameplay_claim,
            "nPlayerOriginalBinaryRuntimeProof": 0,
        },
        "transport": {
            "transport": EXPECTED_TRANSPORT,
            "networkScope": "distinct-private-host-command-source-not-online-play",
            "commandSourceKind": command_source_kind,
            "hostBindAddress": host_address,
            "clientSourceAddress": client_source_address,
            "hostPrivateInterfaceBound": True,
            "hostAddressAssignedToLocalInterface": True,
            "clientSourceAddressNotHostAssignedLocalAddress": client_source_address != host_address,
            "sanitizedHostAndClientInterfaceEvidence": True,
            "secondHostCommandSourceProof": True,
            "secondPhysicalHostProof": second_physical,
            "vmLabeledOnly": not second_physical,
            "sameWorkstationOnly": False,
            "samePhysicalMachineOnly": not second_physical,
            "wslOnHost": False,
            "loopbackInterfaceOnly": False,
            "publicNetworkSocketsOpened": False,
            "multiHostLanPlayProof": multi_host_play_claim,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": native_netcode_claim,
            "natTraversalProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "gameInputSentBySecondHostClient": False,
            "hostHelperInputSent": False,
        },
        "networkIdentityEvidence": {
            "host": {
                "machineFingerprint": "1" * 64,
                "machineFingerprintComputedByPreflight": True,
                "machineFingerprintSource": "self-test-fixture",
                "machineFingerprintInputsRedacted": True,
                "hostnameFingerprint": "7" * 64,
                "platformFingerprint": "8" * 64,
                "runtimeHostKind": "windows-host",
                "runtimeHostKindSource": "self-test-fixture",
                "runtimeHostKindInputsRedacted": True,
                "wslDetectedByPreflight": False,
                "containerDetectedByPreflight": False,
                "hostIdentityObserved": True,
                "assignedPrivateAddresses": [
                    host_address,
                ],
            },
            "client": {
                "machineFingerprint": "2" * 64,
                "machineFingerprintComputedByPreflight": True,
                "machineFingerprintSource": "self-test-fixture",
                "machineFingerprintInputsRedacted": True,
                "hostnameFingerprint": "9" * 64,
                "platformFingerprint": "0" * 64,
                "runtimeHostKind": "windows-host" if second_physical else "vm-guest",
                "runtimeHostKindSource": "self-test-fixture",
                "runtimeHostKindInputsRedacted": True,
                "wslDetectedByPreflight": False,
                "containerDetectedByPreflight": False,
                "clientIdentityObserved": True,
                "observedSourceAddress": client_source_address,
                "sourceAddressAssignedToClientInterface": True,
                "sourceAddressAssignedToHostInterface": False,
                "vmLabeledOnly": not second_physical,
            },
            "runtimeMarkers": {
                "sameMachineSid": False,
                "sameBootId": False,
                "sameWindowsComputerName": False,
                "wslDetectedOnHost": False,
                "wslDetectedOnClient": False,
                "containerDetectedOnHost": False,
                "containerDetectedOnClient": False,
                "loopbackObserved": False,
                "publicRoutablePeerObserved": False,
            },
        },
        "authorization": auth,
        "invitationLifecycle": {
            "schemaVersion": "winui-original-binary-second-host-invitation-lifecycle.v1",
            "rootClass": "os-temp-outside-repo",
            "exclusiveCreateSucceeded": True,
            "issuedAtUnix": 1000,
            "expiresAtUnix": 1120,
            "nonceWindowSeconds": 30,
            "sanitizedInvitationDescriptorSha256": "e" * 64,
            "rawInvitationPathSerialized": False,
            "rawServerAddressSerializedInReceipt": False,
            "privateMaterialSerialized": False,
            "deletionAttempted": True,
            "deletionSucceeded": True,
            "postDeleteExists": False,
        },
        "listenerLifecycle": {
            "schemaVersion": "winui-original-binary-second-host-listener-lifecycle.v1",
            "evidenceMode": listener_evidence_mode,
            "bindAddress": host_address,
            "bindAddressClass": "private-lan-non-loopback",
            "sanitizedEndpointSha256": "8" * 64,
            "socketFamily": "AF_INET",
            "bindAttempted": True,
            "bindSucceeded": True,
            "boundHostMatchesTransport": True,
            "hostPrivateInterfaceBound": True,
            "wildcardBind": False,
            "loopbackBind": False,
            "publicRoutableBind": False,
            "publicEndpointPublished": False,
            "listenSucceeded": True,
            "listenerStarted": True,
            "listenerAcceptLimit": 1,
            "closeAttempted": True,
            "closeSucceeded": True,
            "listenerClosedBeforeBundleWrite": True,
            "teardownObserved": True,
            "postCloseConnectRejected": True,
            "portValueSerializedInPublicDocs": False,
        },
        "sourceSafety": {
            "evidenceMode": source_safety_evidence_mode,
            "computedByPreflight": True,
            "pathValuesPublished": False,
            "absolutePathsSerialized": False,
            "copiedProfileHashesOnBothSides": copied_hashes,
            "installedGamePrePostHashesOnBothSides": installed_hashes,
            "prePostHashSamplesOnBothSides": True,
            "installedGameHashesUnchangedOnHost": True,
            "installedGameHashesUnchangedOnClient": True,
            "copiedProfileRootUsedOnHost": True,
            "copiedProfileRootUsedOnClient": True,
            "programFilesMutationRejected": True,
            "originalExeMutationRejected": True,
            "installedGameMutationAllowed": False,
            "originalExeMutationAllowed": False,
            "programFilesMutationTargetUsed": False,
            "sourceInstallPatchedInPlace": False,
            "host": {
                "sourceEvidenceMode": source_safety_evidence_mode,
                "computedByPreflight": True,
                "pathValuesPublished": False,
                "absolutePathsSerialized": False,
                "copiedProfileRootClass": "app-owned-or-private-proof-root",
                "copiedProfileHashMode": source_hash_mode,
                "copiedProfileFileCount": source_file_count,
                "copiedProfileSha256Before": "3" * 64,
                "copiedProfileSha256After": "3" * 64,
                "prePostHashSamplingMode": source_sampling_mode,
                "prePostHashSampleCount": source_sample_count,
                "prePostHashSamplesDistinct": source_samples_distinct,
                "installedGameRootClass": "source-install-read-only",
                "installedGameHashMode": source_hash_mode,
                "installedGameFileCount": source_file_count,
                "installedGameSha256Before": "4" * 64,
                "installedGameSha256After": "4" * 64,
                "programFilesMutationAttempted": False,
            },
            "client": {
                "sourceEvidenceMode": source_safety_evidence_mode,
                "computedByPreflight": True,
                "pathValuesPublished": False,
                "absolutePathsSerialized": False,
                "copiedProfileRootClass": "app-owned-or-private-proof-root",
                "copiedProfileHashMode": source_hash_mode,
                "copiedProfileFileCount": source_file_count,
                "copiedProfileSha256Before": "5" * 64,
                "copiedProfileSha256After": "5" * 64,
                "prePostHashSamplingMode": source_sampling_mode,
                "prePostHashSampleCount": source_sample_count,
                "prePostHashSamplesDistinct": source_samples_distinct,
                "installedGameRootClass": "source-install-read-only",
                "installedGameHashMode": source_hash_mode,
                "installedGameFileCount": source_file_count,
                "installedGameSha256Before": "6" * 64,
                "installedGameSha256After": "6" * 64,
                "programFilesMutationAttempted": False,
            },
        },
        "commands": {
            "accepted": [
                {
                    "commandId": EXPECTED_COMMAND_ID,
                    "remoteSlot": EXPECTED_REMOTE_SLOT,
                    "command": EXPECTED_REMOTE_COMMAND,
                    "requestEvent": "client_command_p2_forward",
                    "requestPayloadSha256": transcript_hashes["client_command_p2_forward"],
                    "responseEvent": "server_command_accepted",
                    "responsePayloadSha256": transcript_hashes["server_command_accepted"],
                    "authorizationStatus": "accepted-hmac-sha256",
                    "secondHostClientAccepted": True,
                    "wouldForwardToPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
                    "gameInputSentBySecondHostClient": False,
                    "hostHelperInputSent": False,
                }
            ],
            "rejected": [
                {"commandId": "second-host-reject-p3-forward-0001", "reason": "metadata-slot-gameplay-not-allowed", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-loopback-0001", "reason": "loopback-not-allowed", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-same-workstation-0001", "reason": "same-workstation-process-not-allowed", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-wsl-0001", "reason": "wsl-on-host-not-allowed", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-public-host-0001", "reason": "public-internet-host-not-allowed", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-unknown-peer-0001", "reason": "unknown-peer-not-allowed", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-bad-hmac-0001", "reason": "bad-hmac", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-pre-session-0001", "reason": "session-not-established", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-replay-0001", "reason": "replay-nonce", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-timestamp-0001", "reason": "timestamp-window", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-sequence-0001", "reason": "sequence-order", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-pinned-identity-0001", "reason": "pinned-identity-mismatch", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-compatibility-key-0001", "reason": "compatibility-key-mismatch", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-rate-limit-0001", "reason": "rate-limit-exceeded", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-unknown-field-0001", "reason": "message-schema-mismatch", "secondHostClientAccepted": False},
                {"commandId": "second-host-reject-direct-input-0001", "reason": "direct-input-not-allowed", "secondHostClientAccepted": False},
            ],
        },
        "transportTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": auth["serverIdentityFingerprint"],
            "clientIdentityFingerprint": auth["clientIdentityFingerprint"],
            "messageCount": len(EXPECTED_TRANSCRIPT_EVENTS),
            "events": transcript_events,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "multiHostLanPlayProof": multi_host_play_claim,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": native_netcode_claim,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "activeP3P4OriginalBinaryGameplayProof": p3_gameplay_claim,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "coOpVersusRuntimeProof": False,
            "physicalGamepadProof": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
            "gameInputSentBySecondHostClient": False,
            "hostHelperInputSent": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "secretsSerialized": False,
            "rawPrivateAddressPublishedToPublicDocs": False,
            "rawPrivateProofPathPublished": False,
            "privateArtifactContentPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This is a second-host/private-LAN command-source proof only. It proves one distinct private-host or "
            "VM-labeled client command source can authenticate and produce a P2 command envelope that would forward "
            "to the existing private LAN command path. It does not prove player-ready online multiplayer, does not "
            "prove multi-host LAN play, does not prove native BEA netcode, and does not prove active P3/P4 gameplay."
        ),
    }
    if include_security_hardening:
        hardening = make_session_security_hardening_fixture(security_hardening_evidence_mode)
        if security_hardening_evidence_mode == "live-server-client-transcript":
            for row in hardening["cases"]:
                row["requestPayloadSha256ByEvent"] = {event: transcript_hashes[event] for event in row["requestEvents"]}
                row["responsePayloadSha256ByEvent"] = {event: transcript_hashes[event] for event in row["responseEvents"]}
        bundle["sessionSecurityHardening"] = hardening
    output = root / "second-host-command-source-proof.json"
    write_json(output, bundle)
    return output


def run_self_test() -> None:
    validate_gate_dict = make_gate_fixture()
    with tempfile.TemporaryDirectory() as tmp:
        gate_path = Path(tmp) / "gate.json"
        write_json(gate_path, validate_gate_dict)
        validate_gate(gate_path)
    overclaim = make_gate_fixture()
    overclaim["currentEvidence"]["hostJoinControlsMayBeEnabled"] = True
    with tempfile.TemporaryDirectory() as tmp:
        gate_path = Path(tmp) / "overclaim.json"
        write_json(gate_path, overclaim)
        try:
            validate_gate(gate_path)
        except SecondHostCommandSourceProofError:
            pass
        else:
            raise AssertionError("Host/Join overclaim should fail")
    with tempfile.TemporaryDirectory() as tmp:
        validate_bundle(make_bundle_fixture(Path(tmp)))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_bundle(make_bundle_fixture(Path(tmp), command_source_kind="wsl-on-host"))
        except SecondHostCommandSourceProofError:
            pass
        else:
            raise AssertionError("wsl-on-host proof should fail")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_bundle(make_bundle_fixture(Path(tmp), client_source_address="127.0.0.1"))
        except SecondHostCommandSourceProofError:
            pass
        else:
            raise AssertionError("loopback source proof should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--live", action="store_true", help="Require live transcript hardening and local-preflight source safety for a candidate bundle.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host command-source checker self-test: PASS")
        return 0
    if args.check:
        require(not args.live, "--live validates a private bundle path, not the public gate contract")
        print("WinUI original-binary second-host command-source gate check: PASS")
        print(json.dumps(validate_gate(args.bundle or GATE_PATH), indent=2, sort_keys=True))
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.bundle, require_live=args.live), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecondHostCommandSourceProofError,
        lan.PrivateTransportSmokeProofError,
        lan.delivery.PrivateRelayDeliveryProofError,
        lan.delivery.relay.RelayProofError,
        lan.delivery.loopback.LoopbackProofError,
        lan.delivery.loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary second-host command-source check: FAIL: {exc}")
        raise SystemExit(2)
