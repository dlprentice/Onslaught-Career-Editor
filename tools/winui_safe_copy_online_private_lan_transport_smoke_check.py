#!/usr/bin/env python3
"""Validate a private LAN transport/auth smoke chained to private relay-delivery evidence."""

from __future__ import annotations

import argparse
import ipaddress
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_private_relay_delivery_check as delivery


EXPECTED_SCHEMA = "winui-original-binary-private-lan-transport-smoke.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-private-lan-transport-session.v1"
EXPECTED_TRANSPORT = "private-lan-tcp-jsonl-auth-smoke"
EXPECTED_PROTOCOL = "private-lan-transport-input.v1"
EXPECTED_HELPER = "winui-original-binary-private-lan-transport-smoke-helper"
EXPECTED_HELPER_VERSION = "private-lan-transport-smoke-helper.v1"
EXPECTED_COMMAND_ID = "private-lan-p2-forward-0001"
EXPECTED_PRIVATE_RELAY_COMMAND_ID = delivery.EXPECTED_PRIVATE_COMMAND_ID
PRIVATE_NON_LOOPBACK_FIXTURE_HOST = "192.0.2.114"  # TEST-NET-1 fixture, not an operator LAN address.


class PrivateTransportSmokeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateTransportSmokeProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = bundle_path.parent / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"referenced private relay proof bundle is missing: {candidate}")
    return candidate


def sha256_file(path: Path) -> str:
    return delivery.relay.sha256_file(path)


def is_private_non_loopback_host(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return address.is_private and not address.is_loopback and not address.is_link_local and not address.is_multicast and not address.is_unspecified


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected private transport smoke schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected private transport smoke helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected private transport smoke helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected private transport smoke protocol")


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            require(lowered not in {"secret", "sharedsecret", "rawsecret", "authkey", "credential", "password", "token"}, f"serialized credential-like field is not allowed at {path}.{key}")
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_private_relay_reference(bundle: dict[str, Any], path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    private_relay_path = resolve_artifact_path(path, str(bundle.get("privateRelayDeliveryProofBundle", "")))
    require(str(bundle.get("privateRelayDeliveryProofSha256", "")).lower() == sha256_file(private_relay_path), "private relay-delivery proof hash mismatch")
    summary = delivery.validate_bundle(private_relay_path, expected_controller_configuration=1)
    private_bundle = read_json(private_relay_path)
    return private_relay_path, summary, private_bundle


def require_session_descriptor(
    bundle: dict[str, Any],
    *,
    private_relay_path: Path,
    private_relay_summary: dict[str, Any],
    private_relay_bundle: dict[str, Any],
) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    adapter = object_at(private_relay_bundle, "hostHelperAdapter")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "unexpected private transport session schema")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "private transport session protocol mismatch")
    require(descriptor.get("upstreamPrivateRelayProtocolVersion") == delivery.EXPECTED_PROTOCOL, "upstream private relay protocol mismatch")
    require(descriptor.get("upstreamPrivateRelayProofSha256") == sha256_file(private_relay_path), "upstream private relay hash mismatch")
    require(descriptor.get("sessionCompatibilityKey") == adapter.get("sessionCompatibilityKey"), "session compatibility key mismatch")
    require(descriptor.get("cleanSpecimenSha256") == adapter.get("cleanSpecimenSha256"), "clean specimen hash mismatch")
    require(descriptor.get("remotePlayerSlot") == delivery.relay.EXPECTED_REMOTE_SLOT, "private transport must target P2")
    require(descriptor.get("allowedCommand") == delivery.relay.EXPECTED_REMOTE_COMMAND, "private transport command mismatch")
    require(descriptor.get("mappedInputSequence") == delivery.loopback.EXPECTED_MAPPED_SEQUENCE, "mapped input sequence mismatch")
    require(descriptor.get("upstreamPrivateRelayCommandId") == EXPECTED_PRIVATE_RELAY_COMMAND_ID, "wrong upstream private relay command id")
    require(descriptor.get("upstreamLocalRelayCommandId") == private_relay_summary["relayCommandId"], "wrong upstream local relay command id")
    require(descriptor.get("upstreamLoopbackCommandId") == private_relay_summary["upstreamLoopbackCommandId"], "wrong upstream loopback command id")
    require(descriptor.get("deliveryEvidence") == private_relay_summary["gameInputDeliveryEvidence"], "private relay evidence mismatch")
    require(descriptor.get("levelId") == 850, "session level must remain 850")
    require(descriptor.get("controllerConfiguration") == 1, "session controller configuration must remain 1")
    return descriptor


def require_transport_contract(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == EXPECTED_TRANSPORT, "unexpected private transport")
    require(is_private_non_loopback_host(str(transport.get("bindHost") or "")), "private LAN transport smoke must bind a private non-loopback host")
    port = transport.get("actualBindPort")
    require(isinstance(port, int) and 0 < port < 65536, "actualBindPort must be a TCP port")
    require(transport.get("networkScope") == "private-lan-interface-smoke", "unexpected private LAN transport network scope")
    require(transport.get("loopbackInterfaceOnly") is False, "private LAN transport smoke must not be loopback-only")
    require(transport.get("privateLanInterfaceBound") is True, "private LAN transport smoke must bind a private interface")
    require(transport.get("privateLanSocketOpened") is True, "private LAN transport smoke must open a private-interface TCP socket")
    require(transport.get("publicNetworkSocketsOpened") is False, "private LAN transport smoke must not open public sockets")
    require(transport.get("multiHostLanClaim") is False, "private LAN transport smoke must not claim multi-host LAN play")
    require(transport.get("publicMatchmakingClaim") is False, "private LAN transport smoke must not claim public matchmaking")
    require(transport.get("matchmakingServerContacted") is False, "private LAN transport smoke must not contact matchmaking")
    require(transport.get("publicServerClaim") is False, "private LAN transport smoke must not claim public server behavior")
    require(transport.get("nativeBeaNetcodeClaim") is False, "private LAN transport smoke must not claim native BEA netcode")
    require(transport.get("natTraversalClaim") is False, "private LAN transport smoke must not claim NAT traversal")
    require(transport.get("antiCheatClaim") is False, "private LAN transport smoke must not claim anti-cheat")
    require(transport.get("deterministicSyncClaim") is False, "private LAN transport smoke must not claim deterministic sync")
    require(transport.get("rollbackClaim") is False, "private LAN transport smoke must not claim rollback")
    require(transport.get("twoClientParityClaim") is False, "private LAN transport smoke must not claim two-client parity")
    require(transport.get("physicalGamepadClaim") is False, "private LAN transport smoke must not claim physical gamepad behavior")
    require(transport.get("rebuildParityClaim") is False, "private LAN transport smoke must not claim rebuild parity")
    require(transport.get("gameInputSentByTransport") is False, "private LAN transport smoke must not claim direct game input")
    require(transport.get("hostHelperInputSent") is False, "private LAN transport smoke must not claim new host-helper input")
    require(transport.get("wouldForwardToPrivateRelayCommandId") == EXPECTED_PRIVATE_RELAY_COMMAND_ID, "private transport forward target mismatch")
    return transport


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "authorization credential storage must be ephemeral")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must not be present")
    require(isinstance(authorization.get("authKeyFingerprint"), str) and len(authorization["authKeyFingerprint"]) == 64, "auth key fingerprint must be a SHA-256 hex string")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(isinstance(authorization.get("serverIdentityFingerprint"), str) and len(authorization["serverIdentityFingerprint"]) == 64, "server identity fingerprint must be a SHA-256 hex string")
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window must be 30 seconds")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement must be enabled")
    rate_limit = object_at(authorization, "rateLimit")
    require(rate_limit.get("maxAcceptedCommandsPerSession") == 1, "accepted-command session limit mismatch")
    require(rate_limit.get("maxCommandsPerSecond") == 1, "per-second command limit mismatch")
    require(authorization.get("clockMode") == "deterministic-smoke-clock", "clock mode mismatch")
    return authorization


def require_commands(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    rejected = list_at(commands, "rejected")
    require(len(accepted) == 1, "private transport smoke expects exactly one accepted command")
    accepted_command = accepted[0]
    require(isinstance(accepted_command, dict), "accepted command row is not an object")
    require(accepted_command.get("commandId") == EXPECTED_COMMAND_ID, "unexpected private transport command id")
    require(accepted_command.get("remoteSlot") == delivery.relay.EXPECTED_REMOTE_SLOT, "accepted command must target P2")
    require(accepted_command.get("command") == delivery.relay.EXPECTED_REMOTE_COMMAND, "accepted command mismatch")
    require(accepted_command.get("sequence") == 1, "accepted command sequence mismatch")
    require(accepted_command.get("authorizationStatus") == "accepted-hmac-sha256", "accepted command authorization status mismatch")
    require(accepted_command.get("privateTransportAccepted") is True, "accepted command was not accepted by private transport")
    require(accepted_command.get("wouldForwardToPrivateRelayCommandId") == EXPECTED_PRIVATE_RELAY_COMMAND_ID, "accepted command forward target mismatch")
    require(accepted_command.get("gameInputSentByTransport") is False, "accepted private transport command must not send direct game input")
    require(accepted_command.get("hostHelperInputSent") is False, "accepted private transport command must not send new host-helper input")
    require(accepted_command.get("upstreamHostHelperEvidence") == "private-relay-delivery-proof-already-proven", "accepted command must cite prior host-helper evidence")

    expected_reasons = {
        "missing-authentication",
        "bad-hmac",
        "replay-nonce",
        "expired-timestamp",
        "sequence-not-next",
        "command-id-not-allowed",
        "server-identity-mismatch",
        "rate-limit-exceeded",
        "session-compatibility-mismatch",
        "remote-slot-not-allowed",
        "loopback-positive-claim",
        "public-bind-not-allowed",
        "direct-input-not-allowed",
    }
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require(expected_reasons.issubset(reasons), "missing private transport rejection rows")
    for index, row in enumerate(rejected, start=1):
        require(isinstance(row, dict), f"rejected command row {index} is not an object")
        require(row.get("privateTransportAccepted") is False, f"rejected command row {index} was accepted")
        require(row.get("gameInputSentByTransport") is False, f"rejected command row {index} sent direct game input")
        require(row.get("hostHelperInputSent") is False, f"rejected command row {index} sent host-helper input")
    return accepted_command


def require_transcript(bundle: dict[str, Any], *, authorization: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "transportTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "transport transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "transport transcript protocol mismatch")
    require(transcript.get("serverIdentityFingerprint") == authorization.get("serverIdentityFingerprint"), "server identity fingerprint mismatch")
    require(transcript.get("messageCount") == 25, "private transport transcript should have twenty-five wire messages")
    events = list_at(transcript, "events")
    expected_kinds = [
        "server_bound",
        "client_session_hello",
        "server_session_accepted",
        "client_command_missing_auth",
        "server_command_rejected",
        "client_command_bad_hmac",
        "server_command_rejected",
        "client_command_replay_nonce",
        "server_command_rejected",
        "client_command_expired",
        "server_command_rejected",
        "client_command_out_of_order",
        "server_command_rejected",
        "client_command_wrong_command_id",
        "server_command_rejected",
        "client_session_wrong_server_identity",
        "server_session_rejected",
        "client_command_p2_forward",
        "server_command_accepted",
        "client_command_rate_limited",
        "server_command_rejected",
        "client_command_wrong_slot",
        "server_command_rejected",
        "client_command_wrong_compatibility",
        "server_command_rejected",
        "client_close",
        "server_stopped",
    ]
    actual_kinds = [row.get("kind") if isinstance(row, dict) else None for row in events]
    require(actual_kinds == expected_kinds, "private transport transcript event sequence mismatch")
    for index, row in enumerate(events, start=1):
        require(isinstance(row, dict), f"transport transcript event {index} is not an object")
        if row["kind"].startswith("client_") or row["kind"].startswith("server_"):
            if row["kind"] not in {"server_bound", "server_stopped"}:
                payload_sha = str(row.get("payloadSha256") or "")
                payload_bytes = row.get("payloadBytes")
                require(len(payload_sha) == 64, f"event {index} missing payload sha")
                require(isinstance(payload_bytes, int) and payload_bytes > 0, f"event {index} missing payload byte count")
    accepted = events[18]
    require(accepted.get("commandId") == EXPECTED_COMMAND_ID, "accepted transcript command mismatch")
    require(accepted.get("wouldForwardToPrivateRelayCommandId") == EXPECTED_PRIVATE_RELAY_COMMAND_ID, "accepted transcript forward target mismatch")
    require(accepted.get("gameInputSentByTransport") is False, "accepted transcript must not claim direct game input")
    require(accepted.get("hostHelperInputSent") is False, "accepted transcript must not claim new host-helper input")
    return {"eventCount": len(events), "messageCount": transcript["messageCount"]}


def validate_bundle(path: Path, *, expected_controller_configuration: int) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    private_relay_path, private_relay_summary, private_relay_bundle = require_private_relay_reference(bundle, path)
    require_session_descriptor(
        bundle,
        private_relay_path=private_relay_path,
        private_relay_summary=private_relay_summary,
        private_relay_bundle=private_relay_bundle,
    )
    transport = require_transport_contract(bundle)
    authorization = require_authorization(bundle)
    accepted_command = require_commands(bundle)
    transcript = require_transcript(bundle, authorization=authorization)
    require(expected_controller_configuration == 1, "private transport smoke is currently bounded to controller configuration 1")

    return {
        "artifact": str(path),
        "privateRelayDeliveryProofBundle": str(private_relay_path),
        "claim": "private LAN-interface transport/auth smoke accepted one signed P2 command envelope that would forward to the already-proven private relay-delivery command",
        "transport": transport["transport"],
        "bindHost": transport["bindHost"],
        "actualBindPort": transport["actualBindPort"],
        "helperVersion": bundle["helperVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "authorization": {
            "scheme": authorization["scheme"],
            "credentialStorage": authorization["credentialStorage"],
            "serverIdentityMode": authorization["serverIdentityMode"],
            "nonceWindowSeconds": authorization["nonceWindowSeconds"],
            "replayCacheEnabled": authorization["replayCacheEnabled"],
            "sequenceEnforced": authorization["sequenceEnforced"],
            "rateLimit": authorization["rateLimit"],
        },
        "acceptedCommandId": accepted_command["commandId"],
        "wouldForwardToPrivateRelayCommandId": accepted_command["wouldForwardToPrivateRelayCommandId"],
        "privateTransportAccepted": accepted_command["privateTransportAccepted"],
        "gameInputSentByTransport": accepted_command["gameInputSentByTransport"],
        "hostHelperInputSent": accepted_command["hostHelperInputSent"],
        "upstreamPrivateRelay": {
            "acceptedCommandId": private_relay_summary["acceptedCommandId"],
            "relayCommandId": private_relay_summary["relayCommandId"],
            "upstreamLoopbackCommandId": private_relay_summary["upstreamLoopbackCommandId"],
            "hostHelperInputSent": private_relay_summary["hostHelperInputSent"],
            "gameInputDeliveryEvidence": private_relay_summary["gameInputDeliveryEvidence"],
        },
        "transcript": transcript,
        "claimBoundary": (
            "This proves only a single-host private LAN-interface transport/auth envelope smoke chained to an existing "
            "private relay-delivery proof. It does not prove multi-host LAN play, public matchmaking, public relay/server "
            "behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, dual-client parity, "
            "physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = delivery.relay.sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def make_bundle_fixture(
    root: Path,
    *,
    missing_auth: bool = False,
    loopback_positive_claim: bool = False,
    public_bind_claim: bool = False,
    direct_input_claim: bool = False,
    serialized_credential: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    private_relay_path = delivery.make_bundle_fixture(root / "private-relay")
    private_relay_bundle = read_json(private_relay_path)
    adapter = object_at(private_relay_bundle, "hostHelperAdapter")
    auth: dict[str, Any] = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": serialized_credential,
        "authKeyFingerprint": "a" * 64,
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": "b" * 64,
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
        "clockMode": "deterministic-smoke-clock",
    }
    if serialized_credential:
        auth["credential"] = "bad"
    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "privateRelayDeliveryProofBundle": str(private_relay_path),
        "privateRelayDeliveryProofSha256": sha256_file(private_relay_path),
        "sessionDescriptor": {
            "schemaVersion": EXPECTED_SESSION_SCHEMA,
            "protocolVersion": EXPECTED_PROTOCOL,
            "upstreamPrivateRelayProtocolVersion": delivery.EXPECTED_PROTOCOL,
            "upstreamPrivateRelayProofSha256": sha256_file(private_relay_path),
            "sessionCompatibilityKey": adapter["sessionCompatibilityKey"],
            "cleanSpecimenSha256": adapter["cleanSpecimenSha256"],
            "remotePlayerSlot": delivery.relay.EXPECTED_REMOTE_SLOT,
            "allowedCommand": delivery.relay.EXPECTED_REMOTE_COMMAND,
            "mappedInputSequence": delivery.loopback.EXPECTED_MAPPED_SEQUENCE,
            "upstreamPrivateRelayCommandId": EXPECTED_PRIVATE_RELAY_COMMAND_ID,
            "upstreamLocalRelayCommandId": delivery.EXPECTED_RELAY_COMMAND_ID,
            "upstreamLoopbackCommandId": delivery.EXPECTED_LOOPBACK_COMMAND_ID,
            "deliveryEvidence": "fresh-host-helper-cdb-proof",
            "levelId": 850,
            "controllerConfiguration": 1,
        },
        "transport": {
            "transport": EXPECTED_TRANSPORT,
            "bindHost": "8.8.8.8" if public_bind_claim else PRIVATE_NON_LOOPBACK_FIXTURE_HOST,
            "actualBindPort": 49153,
            "networkScope": "private-lan-interface-smoke",
            "loopbackInterfaceOnly": loopback_positive_claim,
            "privateLanInterfaceBound": not public_bind_claim,
            "privateLanSocketOpened": True,
            "publicNetworkSocketsOpened": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": False,
            "matchmakingServerContacted": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "natTraversalClaim": False,
            "antiCheatClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "twoClientParityClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "gameInputSentByTransport": direct_input_claim,
            "hostHelperInputSent": False,
            "wouldForwardToPrivateRelayCommandId": EXPECTED_PRIVATE_RELAY_COMMAND_ID,
        },
        "authorization": auth,
        "commands": {
            "accepted": [
                {
                    "commandId": EXPECTED_COMMAND_ID,
                    "remoteSlot": delivery.relay.EXPECTED_REMOTE_SLOT,
                    "command": delivery.relay.EXPECTED_REMOTE_COMMAND,
                    "sequence": 1,
                    "authorizationStatus": "missing-authentication" if missing_auth else "accepted-hmac-sha256",
                    "privateTransportAccepted": not missing_auth,
                    "wouldForwardToPrivateRelayCommandId": EXPECTED_PRIVATE_RELAY_COMMAND_ID,
                    "gameInputSentByTransport": direct_input_claim,
                    "hostHelperInputSent": False,
                    "upstreamHostHelperEvidence": "private-relay-delivery-proof-already-proven",
                }
            ],
            "rejected": [
                {"commandId": "private-lan-reject-missing-auth-0001", "reason": "missing-authentication", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-bad-signature-0001", "reason": "bad-hmac", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-replay-0001", "reason": "replay-nonce", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-expired-nonce-0001", "reason": "expired-timestamp", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-sequence-gap-0001", "reason": "sequence-not-next", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-wrong-command-id-0001", "reason": "command-id-not-allowed", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-wrong-server-identity-0001", "reason": "server-identity-mismatch", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-rate-limit-0001", "reason": "rate-limit-exceeded", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-compatibility-0001", "reason": "session-compatibility-mismatch", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-p1-0001", "reason": "remote-slot-not-allowed", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-loopback-positive-claim-0001", "reason": "loopback-positive-claim", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-public-bind-0001", "reason": "public-bind-not-allowed", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
                {"commandId": "private-lan-reject-direct-input-0001", "reason": "direct-input-not-allowed", "privateTransportAccepted": False, "gameInputSentByTransport": False, "hostHelperInputSent": False},
            ],
        },
        "transportTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": auth["serverIdentityFingerprint"],
            "messageCount": 25,
            "events": [
                make_event("server_bound", bindHost=PRIVATE_NON_LOOPBACK_FIXTURE_HOST, actualBindPort=49153),
                make_event("client_session_hello", {"type": "session_hello"}),
                make_event("server_session_accepted", {"type": "session_accepted"}),
                make_event("client_command_missing_auth", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "missing-authentication"}),
                make_event("client_command_bad_hmac", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "bad-hmac"}),
                make_event("client_command_replay_nonce", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "replay-nonce"}),
                make_event("client_command_expired", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "expired-timestamp"}),
                make_event("client_command_out_of_order", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "sequence-not-next"}),
                make_event("client_command_wrong_command_id", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "command-id-not-allowed"}),
                make_event("client_session_wrong_server_identity", {"type": "session_hello"}),
                make_event("server_session_rejected", {"type": "session_rejected", "reason": "server-identity-mismatch"}),
                make_event("client_command_p2_forward", {"type": "command"}),
                make_event("server_command_accepted", {"type": "command_accepted"}, commandId=EXPECTED_COMMAND_ID, wouldForwardToPrivateRelayCommandId=EXPECTED_PRIVATE_RELAY_COMMAND_ID, gameInputSentByTransport=direct_input_claim, hostHelperInputSent=False),
                make_event("client_command_rate_limited", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "rate-limit-exceeded"}),
                make_event("client_command_wrong_slot", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "remote-slot-not-allowed"}),
                make_event("client_command_wrong_compatibility", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "session-compatibility-mismatch"}),
                make_event("client_close", {"type": "close"}),
                make_event("server_stopped"),
            ],
        },
    }
    bundle_path = root / "private-transport-smoke-proof.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_bundle(make_bundle_fixture(Path(tmp)), expected_controller_configuration=1)
        require(summary["acceptedCommandId"] == EXPECTED_COMMAND_ID, "fixture command mismatch")
        require(summary["gameInputSentByTransport"] is False, "fixture should not claim transport game input")

    for label, kwargs in (
        ("missing auth accepted row should fail", {"missing_auth": True}),
        ("loopback positive claim should fail", {"loopback_positive_claim": True}),
        ("public bind claim should fail", {"public_bind_claim": True}),
        ("direct transport input claim should fail", {"direct_input_claim": True}),
        ("serialized credential should fail", {"serialized_credential": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs), expected_controller_configuration=1)
            except (PrivateTransportSmokeProofError, delivery.PrivateRelayDeliveryProofError, delivery.relay.RelayProofError, delivery.loopback.LoopbackProofError, delivery.loopback.state_delta.ArtifactError):
                pass
            else:
                raise PrivateTransportSmokeProofError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary private LAN transport smoke checker self-test: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    summary = validate_bundle(args.bundle, expected_controller_configuration=args.expected_controller_configuration)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        PrivateTransportSmokeProofError,
        delivery.PrivateRelayDeliveryProofError,
        delivery.relay.RelayProofError,
        delivery.loopback.LoopbackProofError,
        delivery.loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary private transport smoke check: FAIL: {exc}")
        raise SystemExit(2)
