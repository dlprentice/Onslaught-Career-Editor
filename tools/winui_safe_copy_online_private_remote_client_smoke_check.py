#!/usr/bin/env python3
"""Validate a process-separated private remote-client smoke proof."""

from __future__ import annotations

import argparse
import ipaddress
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_private_lan_transport_smoke_check as lan


EXPECTED_SCHEMA = "winui-original-binary-private-remote-client-smoke.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-private-remote-client-session.v1"
EXPECTED_TRANSPORT = "private-remote-client-tcp-jsonl-auth-smoke"
EXPECTED_PROTOCOL = "private-remote-client-input.v1"
EXPECTED_HELPER = "winui-original-binary-private-remote-client-smoke-helper"
EXPECTED_HELPER_VERSION = "private-remote-client-smoke-helper.v1"
EXPECTED_COMMAND_ID = "private-remote-client-p2-forward-0001"
EXPECTED_PRIVATE_LAN_COMMAND_ID = lan.EXPECTED_COMMAND_ID
EXPECTED_REMOTE_SLOT = "P2"
EXPECTED_REMOTE_COMMAND = lan.delivery.relay.EXPECTED_REMOTE_COMMAND
EXPECTED_MAPPED_SEQUENCE = lan.delivery.loopback.EXPECTED_MAPPED_SEQUENCE
PRIVATE_NON_LOOPBACK_FIXTURE_HOST = "192.0.2.114"  # TEST-NET-1 fixture, not an operator LAN address.


class PrivateRemoteClientSmokeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateRemoteClientSmokeProofError(message)


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
    require(candidate.is_file(), f"referenced private LAN transport proof is missing: {candidate}")
    return candidate


def sha256_file(path: Path) -> str:
    return lan.sha256_file(path)


def is_private_non_loopback_host(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return address.is_private and not address.is_loopback and not address.is_link_local and not address.is_multicast and not address.is_unspecified


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected private remote-client smoke schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected private remote-client smoke helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected private remote-client smoke helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected private remote-client smoke protocol")


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            require(lowered not in {"secret", "sharedsecret", "rawsecret", "authkey", "credential", "password", "token"}, f"serialized credential-like field is not allowed at {path}.{key}")
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_private_lan_reference(bundle: dict[str, Any], path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    private_lan_path = resolve_artifact_path(path, str(bundle.get("privateLanTransportProofBundle", "")))
    require(str(bundle.get("privateLanTransportProofSha256", "")).lower() == sha256_file(private_lan_path), "private LAN transport proof hash mismatch")
    summary = lan.validate_bundle(private_lan_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_path)
    return private_lan_path, summary, private_lan_bundle


def require_session_descriptor(
    bundle: dict[str, Any],
    *,
    private_lan_path: Path,
    private_lan_summary: dict[str, Any],
    private_lan_bundle: dict[str, Any],
) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "unexpected private remote-client session schema")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "private remote-client session protocol mismatch")
    require(descriptor.get("upstreamPrivateLanProtocolVersion") == lan.EXPECTED_PROTOCOL, "upstream private LAN protocol mismatch")
    require(descriptor.get("upstreamPrivateLanProofSha256") == sha256_file(private_lan_path), "upstream private LAN hash mismatch")
    require(descriptor.get("upstreamPrivateLanTransport") == private_lan_summary["transport"], "upstream private LAN transport mismatch")
    require(descriptor.get("sessionCompatibilityKey") == upstream_descriptor["sessionCompatibilityKey"], "session compatibility key mismatch")
    require(descriptor.get("cleanSpecimenSha256") == upstream_descriptor["cleanSpecimenSha256"], "clean specimen hash mismatch")
    require(descriptor.get("remotePlayerSlot") == EXPECTED_REMOTE_SLOT, "private remote-client smoke must target P2")
    require(descriptor.get("allowedCommand") == EXPECTED_REMOTE_COMMAND, "private remote-client command mismatch")
    require(descriptor.get("mappedInputSequence") == EXPECTED_MAPPED_SEQUENCE, "mapped input sequence mismatch")
    require(descriptor.get("upstreamPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "wrong upstream private LAN command id")
    require(descriptor.get("upstreamPrivateRelayCommandId") == private_lan_summary["wouldForwardToPrivateRelayCommandId"], "wrong upstream private relay command id")
    require(descriptor.get("upstreamPrivateRelayDeliveryEvidence") == private_lan_summary["upstreamPrivateRelay"]["gameInputDeliveryEvidence"], "private relay delivery evidence mismatch")
    require(descriptor.get("levelId") == 850, "session level must remain 850")
    require(descriptor.get("controllerConfiguration") == 1, "session controller configuration must remain 1")
    return descriptor


def require_transport_contract(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == EXPECTED_TRANSPORT, "unexpected private remote-client transport")
    require(is_private_non_loopback_host(str(transport.get("bindHost") or "")), "private remote-client smoke must bind a private non-loopback host")
    port = transport.get("actualBindPort")
    require(isinstance(port, int) and 0 < port < 65536, "actualBindPort must be a TCP port")
    require(transport.get("networkScope") == "private-interface-process-separated-smoke", "unexpected private remote-client network scope")
    require(transport.get("loopbackInterfaceOnly") is False, "private remote-client smoke must not be loopback-only")
    require(transport.get("privateLanInterfaceBound") is True, "private remote-client smoke must bind a private interface")
    require(transport.get("privateLanSocketOpened") is True, "private remote-client smoke must open a private-interface TCP socket")
    require(transport.get("processSeparatedClient") is True, "private remote-client smoke must use a separate client process")
    require(transport.get("sameWorkstationOnly") is True, "private remote-client smoke must record same-workstation boundary")
    require(transport.get("publicNetworkSocketsOpened") is False, "private remote-client smoke must not open public sockets")
    require(transport.get("multiHostLanClaim") is False, "private remote-client smoke must not claim multi-host LAN play")
    require(transport.get("publicMatchmakingClaim") is False, "private remote-client smoke must not claim public matchmaking")
    require(transport.get("matchmakingServerContacted") is False, "private remote-client smoke must not contact matchmaking")
    require(transport.get("publicServerClaim") is False, "private remote-client smoke must not claim public server behavior")
    require(transport.get("nativeBeaNetcodeClaim") is False, "private remote-client smoke must not claim native BEA netcode")
    require(transport.get("natTraversalClaim") is False, "private remote-client smoke must not claim NAT traversal")
    require(transport.get("deterministicSyncClaim") is False, "private remote-client smoke must not claim deterministic sync")
    require(transport.get("rollbackClaim") is False, "private remote-client smoke must not claim rollback")
    require(transport.get("antiCheatClaim") is False, "private remote-client smoke must not claim anti-cheat")
    require(transport.get("dualClientParityClaim") is False, "private remote-client smoke must not claim dual-client parity")
    require(transport.get("physicalGamepadClaim") is False, "private remote-client smoke must not claim physical gamepad behavior")
    require(transport.get("rebuildParityClaim") is False, "private remote-client smoke must not claim rebuild parity")
    require(transport.get("gameInputSentByRemoteClient") is False, "private remote-client smoke must not claim direct game input")
    require(transport.get("hostHelperInputSent") is False, "private remote-client smoke must not claim new host-helper input")
    return transport


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "authorization credential storage must be ephemeral")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must not be present")
    require(isinstance(authorization.get("authKeyFingerprint"), str) and len(authorization["authKeyFingerprint"]) == 64, "auth key fingerprint must be a SHA-256 hex string")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(isinstance(authorization.get("serverIdentityFingerprint"), str) and len(authorization["serverIdentityFingerprint"]) == 64, "server identity fingerprint must be a SHA-256 hex string")
    require(authorization.get("clientIdentityMode") == "pinned-fingerprint", "client identity mode mismatch")
    require(isinstance(authorization.get("clientIdentityFingerprint"), str) and len(authorization["clientIdentityFingerprint"]) == 64, "client identity fingerprint must be a SHA-256 hex string")
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window must be 30 seconds")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement must be enabled")
    rate_limit = object_at(authorization, "rateLimit")
    require(rate_limit.get("maxAcceptedCommandsPerSession") == 1, "accepted-command session limit mismatch")
    require(rate_limit.get("maxCommandsPerSecond") == 1, "per-second command limit mismatch")
    require(authorization.get("clockMode") == "deterministic-smoke-clock", "clock mode mismatch")
    return authorization


def require_process_boundary(bundle: dict[str, Any]) -> dict[str, Any]:
    boundary = object_at(bundle, "clientProcessBoundary")
    require(boundary.get("processModel") == "separate-python-process", "unexpected client process model")
    builder_pid = boundary.get("builderProcessId")
    client_pid = boundary.get("clientProcessId")
    require(isinstance(builder_pid, int) and builder_pid > 0, "builder process id must be positive")
    require(isinstance(client_pid, int) and client_pid > 0, "client process id must be positive")
    require(boundary.get("clientProcessDifferentFromBuilder") is True, "client process must differ from builder process")
    require(builder_pid != client_pid, "builder and client process ids must differ")
    require(boundary.get("clientExitCode") == 0, "client process must exit cleanly")
    require(boundary.get("clientVerifiedServerIdentity") is True, "client must verify pinned server identity")
    require(boundary.get("clientCommandLineContainsCredential") is False, "credential must not be placed on command line")
    require(boundary.get("clientEnvironmentContainsCredential") is False, "credential must not be placed in client environment")
    require(boundary.get("clientStdoutContainsCredential") is False, "credential must not leak through stdout")
    require(boundary.get("clientStderrContainsCredential") is False, "credential must not leak through stderr")
    require(boundary.get("credentialTransportToClientProcess") == "stdin-ephemeral-not-serialized-to-artifact", "unexpected credential transport boundary")
    require(boundary.get("sameWorkstationOnly") is True, "process boundary must record same-workstation proof")
    require(boundary.get("multiHostLanClaim") is False, "process boundary must not claim multi-host LAN")
    responses = list_at(boundary, "clientResponses")
    labels = [row.get("label") for row in responses if isinstance(row, dict)]
    require(labels == ["session", "missing-auth", "wrong-slot", "accepted", "rate-limit"], "client response sequence mismatch")
    return boundary


def require_commands(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    rejected = list_at(commands, "rejected")
    require(len(accepted) == 1, "exactly one remote-client command should be accepted")
    accepted_command = accepted[0]
    require(isinstance(accepted_command, dict), "accepted command must be an object")
    require(accepted_command.get("commandId") == EXPECTED_COMMAND_ID, "accepted command id mismatch")
    require(accepted_command.get("remoteSlot") == EXPECTED_REMOTE_SLOT, "accepted command must target P2")
    require(accepted_command.get("command") == EXPECTED_REMOTE_COMMAND, "accepted command name mismatch")
    require(accepted_command.get("authorizationStatus") == "accepted-hmac-sha256", "accepted command authorization status mismatch")
    require(accepted_command.get("remoteClientAccepted") is True, "accepted command was not accepted by remote-client smoke")
    require(accepted_command.get("wouldForwardToPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "accepted command forward target mismatch")
    require(accepted_command.get("gameInputSentByRemoteClient") is False, "accepted remote-client command must not send direct game input")
    require(accepted_command.get("hostHelperInputSent") is False, "accepted remote-client command must not send new host-helper input")
    expected_reasons = {
        "missing-authentication",
        "remote-slot-not-allowed",
        "rate-limit-exceeded",
        "same-process-positive-claim-not-allowed",
        "multi-host-positive-claim-not-allowed",
        "public-matchmaking-not-allowed",
        "direct-input-not-allowed",
    }
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require(expected_reasons.issubset(reasons), "missing private remote-client rejection rows")
    for row in rejected:
        require(isinstance(row, dict), "rejected command row must be an object")
        require(row.get("remoteClientAccepted") is False, "rejected row must not be accepted")
    return accepted_command


def require_transcript(bundle: dict[str, Any], *, authorization: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "transportTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "transport transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "transport transcript protocol mismatch")
    require(transcript.get("serverIdentityFingerprint") == authorization.get("serverIdentityFingerprint"), "server identity fingerprint mismatch")
    require(transcript.get("clientIdentityFingerprint") == authorization.get("clientIdentityFingerprint"), "client identity fingerprint mismatch")
    require(transcript.get("messageCount") == 11, "private remote-client transcript should have eleven wire messages")
    events = list_at(transcript, "events")
    expected_kinds = [
        "server_bound",
        "client_session_hello",
        "server_session_accepted",
        "client_command_missing_auth",
        "server_command_rejected",
        "client_command_wrong_slot",
        "server_command_rejected",
        "client_command_p2_forward",
        "server_command_accepted",
        "client_command_rate_limited",
        "server_command_rejected",
        "client_close",
        "client_process_started",
        "client_process_exited",
        "server_stopped",
    ]
    actual_kinds = [row.get("kind") if isinstance(row, dict) else None for row in events]
    require(actual_kinds == expected_kinds, "private remote-client transcript event sequence mismatch")
    for index, row in enumerate(events, start=1):
        require(isinstance(row, dict), f"transport transcript event {index} is not an object")
        if row["kind"].startswith("client_") or row["kind"].startswith("server_"):
            if row["kind"] not in {"server_bound", "server_stopped", "client_process_started", "client_process_exited"}:
                payload_sha = str(row.get("payloadSha256") or "")
                payload_bytes = row.get("payloadBytes")
                require(len(payload_sha) == 64, f"event {index} missing payload sha")
                require(isinstance(payload_bytes, int) and payload_bytes > 0, f"event {index} missing payload byte count")
    accepted = object_at(events[8], "extra") if "extra" in events[8] else events[8]
    require(accepted.get("commandId") == EXPECTED_COMMAND_ID, "accepted transcript command mismatch")
    require(accepted.get("wouldForwardToPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "accepted transcript forward target mismatch")
    require(accepted.get("gameInputSentByRemoteClient") is False, "accepted transcript must not claim direct game input")
    require(accepted.get("hostHelperInputSent") is False, "accepted transcript must not claim new host-helper input")
    return {"eventCount": len(events), "messageCount": transcript["messageCount"]}


def validate_bundle(path: Path, *, expected_controller_configuration: int) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    private_lan_path, private_lan_summary, private_lan_bundle = require_private_lan_reference(bundle, path)
    require_session_descriptor(
        bundle,
        private_lan_path=private_lan_path,
        private_lan_summary=private_lan_summary,
        private_lan_bundle=private_lan_bundle,
    )
    transport = require_transport_contract(bundle)
    authorization = require_authorization(bundle)
    process_boundary = require_process_boundary(bundle)
    accepted_command = require_commands(bundle)
    transcript = require_transcript(bundle, authorization=authorization)
    require(expected_controller_configuration == 1, "private remote-client smoke is currently bounded to controller configuration 1")

    return {
        "artifact": str(path),
        "privateLanTransportProofBundle": str(private_lan_path),
        "claim": "process-separated private remote-client accepted one signed P2 command envelope that would forward to the already-proven private LAN transport command",
        "transport": transport["transport"],
        "bindHost": transport["bindHost"],
        "actualBindPort": transport["actualBindPort"],
        "helperVersion": bundle["helperVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "processBoundary": {
            "processModel": process_boundary["processModel"],
            "clientProcessDifferentFromBuilder": process_boundary["clientProcessDifferentFromBuilder"],
            "clientVerifiedServerIdentity": process_boundary["clientVerifiedServerIdentity"],
            "sameWorkstationOnly": process_boundary["sameWorkstationOnly"],
            "credentialTransportToClientProcess": process_boundary["credentialTransportToClientProcess"],
        },
        "authorization": {
            "scheme": authorization["scheme"],
            "credentialStorage": authorization["credentialStorage"],
            "serverIdentityMode": authorization["serverIdentityMode"],
            "clientIdentityMode": authorization["clientIdentityMode"],
            "nonceWindowSeconds": authorization["nonceWindowSeconds"],
            "replayCacheEnabled": authorization["replayCacheEnabled"],
            "sequenceEnforced": authorization["sequenceEnforced"],
            "rateLimit": authorization["rateLimit"],
        },
        "acceptedCommandId": accepted_command["commandId"],
        "wouldForwardToPrivateLanCommandId": accepted_command["wouldForwardToPrivateLanCommandId"],
        "remoteClientAccepted": accepted_command["remoteClientAccepted"],
        "gameInputSentByRemoteClient": accepted_command["gameInputSentByRemoteClient"],
        "hostHelperInputSent": accepted_command["hostHelperInputSent"],
        "upstreamPrivateLan": {
            "acceptedCommandId": private_lan_summary["acceptedCommandId"],
            "wouldForwardToPrivateRelayCommandId": private_lan_summary["wouldForwardToPrivateRelayCommandId"],
            "privateTransportAccepted": private_lan_summary["privateTransportAccepted"],
            "gameInputSentByTransport": private_lan_summary["gameInputSentByTransport"],
            "hostHelperInputSent": private_lan_summary["hostHelperInputSent"],
        },
        "transcript": transcript,
        "claimBoundary": (
            "This proves only a same-workstation process-separated private remote-client command-source smoke chained to "
            "an existing private LAN transport proof. It does not prove multi-host LAN play, public matchmaking, public "
            "relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, "
            "dual-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = lan.delivery.relay.sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def make_bundle_fixture(
    root: Path,
    *,
    same_process_claim: bool = False,
    multi_host_claim: bool = False,
    direct_input_claim: bool = False,
    serialized_credential: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    private_lan_path = lan.make_bundle_fixture(root / "private-lan")
    private_lan_bundle = read_json(private_lan_path)
    private_lan_summary = lan.validate_bundle(private_lan_path, expected_controller_configuration=1)
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    auth: dict[str, Any] = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": serialized_credential,
        "authKeyFingerprint": "c" * 64,
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": "d" * 64,
        "clientIdentityMode": "pinned-fingerprint",
        "clientIdentityFingerprint": "e" * 64,
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
        "clockMode": "deterministic-smoke-clock",
    }
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
            "remotePlayerSlot": EXPECTED_REMOTE_SLOT,
            "allowedCommand": EXPECTED_REMOTE_COMMAND,
            "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
            "upstreamPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
            "upstreamPrivateRelayCommandId": private_lan_summary["wouldForwardToPrivateRelayCommandId"],
            "upstreamPrivateRelayDeliveryEvidence": private_lan_summary["upstreamPrivateRelay"]["gameInputDeliveryEvidence"],
            "levelId": 850,
            "controllerConfiguration": 1,
        },
        "transport": {
            "transport": EXPECTED_TRANSPORT,
            "bindHost": PRIVATE_NON_LOOPBACK_FIXTURE_HOST,
            "actualBindPort": 49154,
            "networkScope": "private-interface-process-separated-smoke",
            "loopbackInterfaceOnly": False,
            "privateLanInterfaceBound": True,
            "privateLanSocketOpened": True,
            "processSeparatedClient": not same_process_claim,
            "sameWorkstationOnly": True,
            "publicNetworkSocketsOpened": False,
            "multiHostLanClaim": multi_host_claim,
            "publicMatchmakingClaim": False,
            "matchmakingServerContacted": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "natTraversalClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "dualClientParityClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "gameInputSentByRemoteClient": direct_input_claim,
            "hostHelperInputSent": False,
        },
        "authorization": auth,
        "clientProcessBoundary": {
            "processModel": "separate-python-process",
            "builderProcessId": 100,
            "clientProcessId": 101 if not same_process_claim else 100,
            "clientProcessDifferentFromBuilder": not same_process_claim,
            "clientExitCode": 0,
            "clientVerifiedServerIdentity": True,
            "clientCommandLineContainsCredential": False,
            "clientEnvironmentContainsCredential": False,
            "clientStdoutContainsCredential": False,
            "clientStderrContainsCredential": False,
            "credentialTransportToClientProcess": "stdin-ephemeral-not-serialized-to-artifact",
            "sameWorkstationOnly": True,
            "multiHostLanClaim": False,
            "clientResponses": [
                {"label": "session", "type": "session_accepted", "serverIdentityFingerprint": auth["serverIdentityFingerprint"]},
                {"label": "missing-auth", "type": "command_rejected", "reason": "missing-authentication"},
                {"label": "wrong-slot", "type": "command_rejected", "reason": "remote-slot-not-allowed"},
                {"label": "accepted", "type": "command_accepted", "commandId": EXPECTED_COMMAND_ID, "wouldForwardToPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID},
                {"label": "rate-limit", "type": "command_rejected", "reason": "rate-limit-exceeded"},
            ],
        },
        "commands": {
            "accepted": [
                {
                    "commandId": EXPECTED_COMMAND_ID,
                    "remoteSlot": EXPECTED_REMOTE_SLOT,
                    "command": EXPECTED_REMOTE_COMMAND,
                    "authorizationStatus": "accepted-hmac-sha256",
                    "remoteClientAccepted": True,
                    "wouldForwardToPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
                    "gameInputSentByRemoteClient": direct_input_claim,
                    "hostHelperInputSent": False,
                }
            ],
            "rejected": [
                {"commandId": "private-remote-client-reject-missing-auth-0001", "reason": "missing-authentication", "remoteClientAccepted": False},
                {"commandId": "private-remote-client-reject-wrong-slot-0001", "reason": "remote-slot-not-allowed", "remoteClientAccepted": False},
                {"commandId": "private-remote-client-reject-rate-limit-0001", "reason": "rate-limit-exceeded", "remoteClientAccepted": False},
                {"commandId": "private-remote-client-reject-same-process-claim-0001", "reason": "same-process-positive-claim-not-allowed", "remoteClientAccepted": False},
                {"commandId": "private-remote-client-reject-multi-host-claim-0001", "reason": "multi-host-positive-claim-not-allowed", "remoteClientAccepted": False},
                {"commandId": "private-remote-client-reject-public-matchmaking-claim-0001", "reason": "public-matchmaking-not-allowed", "remoteClientAccepted": False},
                {"commandId": "private-remote-client-reject-direct-input-claim-0001", "reason": "direct-input-not-allowed", "remoteClientAccepted": False},
            ],
        },
        "transportTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": auth["serverIdentityFingerprint"],
            "clientIdentityFingerprint": auth["clientIdentityFingerprint"],
            "messageCount": 11,
            "events": [
                make_event("server_bound", bindHost=PRIVATE_NON_LOOPBACK_FIXTURE_HOST, actualBindPort=49154),
                make_event("client_session_hello", {"type": "session_hello"}),
                make_event("server_session_accepted", {"type": "session_accepted"}),
                make_event("client_command_missing_auth", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "missing-authentication"}),
                make_event("client_command_wrong_slot", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "remote-slot-not-allowed"}),
                make_event("client_command_p2_forward", {"type": "command"}),
                make_event("server_command_accepted", {"type": "command_accepted"}, commandId=EXPECTED_COMMAND_ID, wouldForwardToPrivateLanCommandId=EXPECTED_PRIVATE_LAN_COMMAND_ID, gameInputSentByRemoteClient=direct_input_claim, hostHelperInputSent=False),
                make_event("client_command_rate_limited", {"type": "command"}),
                make_event("server_command_rejected", {"type": "command_rejected", "reason": "rate-limit-exceeded"}),
                make_event("client_close", {"type": "close"}),
                make_event("client_process_started", processId=101, processModel="separate-python-process"),
                make_event("client_process_exited", processId=101, exitCode=0),
                make_event("server_stopped"),
            ],
        },
    }
    output = root / "private-remote-client-smoke-proof.json"
    output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return output


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fixture = make_bundle_fixture(Path(tmp))
        validate_bundle(fixture, expected_controller_configuration=1)
    for name, kwargs in (
        ("same process claim should fail", {"same_process_claim": True}),
        ("multi-host claim should fail", {"multi_host_claim": True}),
        ("direct input claim should fail", {"direct_input_claim": True}),
        ("serialized credential should fail", {"serialized_credential": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = make_bundle_fixture(Path(tmp), **kwargs)
            try:
                validate_bundle(fixture, expected_controller_configuration=1)
            except PrivateRemoteClientSmokeProofError:
                continue
            raise AssertionError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    summary = validate_bundle(args.bundle, expected_controller_configuration=args.expected_controller_configuration)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
