#!/usr/bin/env python3
"""Validate a same-workstation two-client host-authority scheduler smoke proof."""

from __future__ import annotations

import argparse
import ipaddress
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_private_remote_client_smoke_check as remote


EXPECTED_SCHEMA = "winui-original-binary-host-authority-two-client-smoke.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-host-authority-two-client-session.v1"
EXPECTED_TRANSPORT = "host-authority-two-client-tcp-jsonl-smoke"
EXPECTED_PROTOCOL = "host-authority-two-client-input.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-two-client-smoke-helper"
EXPECTED_HELPER_VERSION = "host-authority-two-client-smoke-helper.v1"
EXPECTED_P1_COMMAND_ID = "host-authority-p1-forward-0001"
EXPECTED_P2_COMMAND_ID = "host-authority-p2-forward-0001"
EXPECTED_COMMAND = remote.EXPECTED_REMOTE_COMMAND
EXPECTED_P1_SEQUENCE = "down:Q,wait:500,up:Q"
EXPECTED_P2_SEQUENCE = remote.EXPECTED_MAPPED_SEQUENCE
PRIVATE_NON_LOOPBACK_FIXTURE_HOST = "192.0.2.114"  # TEST-NET-1 fixture, not an operator LAN address.


class HostAuthorityTwoClientSmokeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityTwoClientSmokeProofError(message)


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


def sha256_payload(value: Any) -> str:
    import hashlib

    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = bundle_path.parent / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"referenced private remote-client proof is missing: {candidate}")
    return candidate


def is_private_non_loopback_host(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return address.is_private and not address.is_loopback and not address.is_link_local and not address.is_multicast and not address.is_unspecified


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            require(lowered not in {"secret", "sharedsecret", "rawsecret", "authkey", "credential", "password", "token"}, f"serialized credential-like field is not allowed at {path}.{key}")
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected host-authority schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected host-authority helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected host-authority helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected host-authority protocol")


def require_remote_client_reference(bundle: dict[str, Any], path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    remote_path = resolve_artifact_path(path, str(bundle.get("privateRemoteClientProofBundle", "")))
    require(str(bundle.get("privateRemoteClientProofSha256", "")).lower() == remote.sha256_file(remote_path), "private remote-client proof hash mismatch")
    summary = remote.validate_bundle(remote_path, expected_controller_configuration=1)
    remote_bundle = read_json(remote_path)
    return remote_path, summary, remote_bundle


def require_session_descriptor(
    bundle: dict[str, Any],
    *,
    remote_path: Path,
    remote_summary: dict[str, Any],
    remote_bundle: dict[str, Any],
) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    upstream_descriptor = object_at(remote_bundle, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "unexpected host-authority session schema")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "host-authority session protocol mismatch")
    require(descriptor.get("upstreamPrivateRemoteClientProtocolVersion") == remote.EXPECTED_PROTOCOL, "upstream remote-client protocol mismatch")
    require(descriptor.get("upstreamPrivateRemoteClientProofSha256") == remote.sha256_file(remote_path), "upstream remote-client hash mismatch")
    require(descriptor.get("upstreamPrivateRemoteClientTransport") == remote_summary["transport"], "upstream remote-client transport mismatch")
    require(descriptor.get("sessionCompatibilityKey") == upstream_descriptor["sessionCompatibilityKey"], "session compatibility key mismatch")
    require(descriptor.get("cleanSpecimenSha256") == upstream_descriptor["cleanSpecimenSha256"], "clean specimen hash mismatch")
    require(descriptor.get("levelId") == 850, "session level must remain 850")
    require(descriptor.get("controllerConfiguration") == 1, "session controller configuration must remain 1")
    require(descriptor.get("hostAuthorityModel") == "single-host-authoritative-copied-session", "host authority model mismatch")
    require(descriptor.get("clientSlots") == ["P1", "P2"], "client slots must be P1/P2")
    commands = object_at(descriptor, "allowedCommands")
    p1 = object_at(commands, "P1")
    p2 = object_at(commands, "P2")
    require(p1.get("commandId") == EXPECTED_P1_COMMAND_ID, "P1 command id mismatch")
    require(p1.get("command") == EXPECTED_COMMAND, "P1 command mismatch")
    require(p1.get("mappedInputSequence") == EXPECTED_P1_SEQUENCE, "P1 mapped sequence mismatch")
    require(p2.get("commandId") == EXPECTED_P2_COMMAND_ID, "P2 command id mismatch")
    require(p2.get("command") == EXPECTED_COMMAND, "P2 command mismatch")
    require(p2.get("mappedInputSequence") == EXPECTED_P2_SEQUENCE, "P2 mapped sequence mismatch")
    require(descriptor.get("upstreamPrivateRemoteClientCommandId") == remote.EXPECTED_COMMAND_ID, "upstream remote-client command id mismatch")
    require(descriptor.get("upstreamPrivateLanCommandId") == remote_summary["wouldForwardToPrivateLanCommandId"], "upstream private LAN command id mismatch")
    return descriptor


def require_transport(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == EXPECTED_TRANSPORT, "unexpected host-authority transport")
    require(is_private_non_loopback_host(str(transport.get("bindHost") or "")), "host-authority smoke must bind private non-loopback host")
    port = transport.get("actualBindPort")
    require(isinstance(port, int) and 0 < port < 65536, "actualBindPort must be a TCP port")
    require(transport.get("networkScope") == "private-interface-two-client-host-authority-smoke", "network scope mismatch")
    require(transport.get("privateLanInterfaceBound") is True, "private LAN interface must be bound")
    require(transport.get("loopbackInterfaceOnly") is False, "host-authority smoke must not be loopback-only")
    require(transport.get("sameWorkstationOnly") is True, "host-authority smoke must record same-workstation boundary")
    require(transport.get("processSeparatedClients") is True, "host-authority smoke must use process-separated clients")
    require(transport.get("twoDistinctClientProcesses") is True, "host-authority smoke must record distinct client processes")
    for key in (
        "publicNetworkSocketsOpened",
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "publicServerClaim",
        "nativeBeaNetcodeClaim",
        "natTraversalClaim",
        "deterministicSyncClaim",
        "rollbackClaim",
        "antiCheatClaim",
        "physicalGamepadClaim",
        "rebuildParityClaim",
        "gameInputSentByScheduler",
        "hostHelperInputSent",
    ):
        require(transport.get(key) is False, f"transport overclaim must be false: {key}")
    return transport


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must not be present")
    fingerprints = object_at(authorization, "slotCredentialFingerprints")
    require(sorted(fingerprints) == ["P1", "P2"], "slot credential fingerprints must cover P1/P2")
    for slot, value in fingerprints.items():
        require(isinstance(value, str) and len(value) == 64, f"{slot} credential fingerprint must be SHA-256")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(isinstance(authorization.get("serverIdentityFingerprint"), str) and len(authorization["serverIdentityFingerprint"]) == 64, "server identity fingerprint must be SHA-256")
    require(authorization.get("clientIdentityMode") == "pinned-slot-fingerprint", "client identity mode mismatch")
    client_ids = object_at(authorization, "clientIdentityFingerprints")
    require(sorted(client_ids) == ["P1", "P2"], "client identity fingerprints must cover P1/P2")
    for slot, value in client_ids.items():
        require(isinstance(value, str) and len(value) == 64, f"{slot} client identity fingerprint must be SHA-256")
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window mismatch")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement must be enabled")
    rate = object_at(authorization, "rateLimit")
    require(rate.get("maxAcceptedCommandsPerSlot") == 1, "per-slot rate limit mismatch")
    require(rate.get("maxAcceptedCommandsPerTick") == 2, "per-tick rate limit mismatch")
    require(authorization.get("clockMode") == "deterministic-smoke-clock", "clock mode mismatch")
    return authorization


def require_process_boundary(bundle: dict[str, Any]) -> dict[str, Any]:
    boundary = object_at(bundle, "clientProcessBoundary")
    require(boundary.get("processModel") == "two-separate-python-client-processes", "process model mismatch")
    builder_pid = boundary.get("builderProcessId")
    require(isinstance(builder_pid, int) and builder_pid > 0, "builder process id must be positive")
    processes = list_at(boundary, "clientProcesses")
    require(len(processes) == 2, "expected two client processes")
    slots = [row.get("clientSlot") for row in processes if isinstance(row, dict)]
    require(sorted(slots) == ["P1", "P2"], "client process slots mismatch")
    client_pids: list[int] = []
    for row in processes:
        require(isinstance(row, dict), "client process row must be an object")
        pid = row.get("clientProcessId")
        require(isinstance(pid, int) and pid > 0, "client process id must be positive")
        client_pids.append(pid)
        require(row.get("clientVerifiedServerIdentity") is True, "client must verify server identity")
        require(row.get("clientExitCode") == 0, "client process must exit cleanly")
    require(boundary.get("clientProcessIdsDistinctFromBuilder") is True, "clients must be distinct from builder")
    require(builder_pid not in client_pids, "client process id matched builder")
    require(boundary.get("clientProcessIdsDistinctFromEachOther") is True, "client processes must be distinct from each other")
    require(len(set(client_pids)) == 2, "client process ids must be unique")
    require(boundary.get("credentialTransportToClientProcesses") == "stdin-ephemeral-not-serialized-to-artifact", "credential transport mismatch")
    for key in ("clientCommandLineContainsCredential", "clientEnvironmentContainsCredential", "clientStdoutContainsCredential", "clientStderrContainsCredential", "multiHostLanClaim"):
        require(boundary.get(key) is False, f"process boundary overclaim must be false: {key}")
    require(boundary.get("sameWorkstationOnly") is True, "process boundary must record same workstation")
    responses = object_at(boundary, "clientResponses")
    require({*responses.keys()} == {"P1", "P2"}, "client responses must cover P1/P2")
    p1_rows = list_at(responses, "P1")
    p2_rows = list_at(responses, "P2")
    p1_summary = [(row.get("label"), row.get("type"), row.get("reason"), row.get("commandId")) for row in p1_rows if isinstance(row, dict)]
    p2_summary = [(row.get("label"), row.get("type"), row.get("reason"), row.get("commandId")) for row in p2_rows if isinstance(row, dict)]
    require(
        p1_summary
        == [
            ("session", "session_accepted", None, None),
            ("missing-auth", "command_rejected", "missing-authentication", EXPECTED_P1_COMMAND_ID),
            ("public-matchmaking-claim", "command_rejected", "public-matchmaking-not-allowed", EXPECTED_P1_COMMAND_ID),
            ("accepted", "command_accepted", None, EXPECTED_P1_COMMAND_ID),
            ("direct-input-claim", "command_rejected", "direct-input-not-allowed", EXPECTED_P1_COMMAND_ID),
        ],
        "P1 response sequence mismatch",
    )
    require(
        p2_summary
        == [
            ("session", "session_accepted", None, None),
            ("wrong-command-id", "command_rejected", "command-id-not-allowed", "host-authority-reject-wrong-command-id-0001"),
            ("accepted", "command_accepted", None, EXPECTED_P2_COMMAND_ID),
            ("replay", "command_rejected", "replay-nonce", EXPECTED_P2_COMMAND_ID),
            ("rate-limit", "command_rejected", "slot-rate-limit-exceeded", EXPECTED_P2_COMMAND_ID),
        ],
        "P2 response sequence mismatch",
    )
    return boundary


def require_commands(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    rejected = list_at(commands, "rejected")
    require(len(accepted) == 2, "expected two accepted commands")
    by_slot = {row.get("clientSlot"): row for row in accepted if isinstance(row, dict)}
    require(set(by_slot) == {"P1", "P2"}, "accepted commands must cover P1/P2")
    require(by_slot["P1"].get("commandId") == EXPECTED_P1_COMMAND_ID, "P1 accepted command mismatch")
    require(by_slot["P1"].get("mappedInputSequence") == EXPECTED_P1_SEQUENCE, "P1 accepted sequence mismatch")
    require(by_slot["P2"].get("commandId") == EXPECTED_P2_COMMAND_ID, "P2 accepted command mismatch")
    require(by_slot["P2"].get("mappedInputSequence") == EXPECTED_P2_SEQUENCE, "P2 accepted sequence mismatch")
    for row in accepted:
        require(row.get("command") == EXPECTED_COMMAND, "accepted command name mismatch")
        require(row.get("scheduledTick") == 1, "accepted commands must be scheduled on tick 1")
        require(row.get("hostAccepted") is True, "accepted command must be host accepted")
        require(row.get("gameInputSentByScheduler") is False, "accepted command must not send scheduler game input")
        require(row.get("hostHelperInputSent") is False, "accepted command must not send host-helper input")
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    for reason in (
        "missing-authentication",
        "public-matchmaking-not-allowed",
        "direct-input-not-allowed",
        "command-id-not-allowed",
        "replay-nonce",
        "slot-rate-limit-exceeded",
    ):
        require(reason in reasons, f"missing rejection reason: {reason}")
    for row in rejected:
        require(isinstance(row, dict), "rejected command row must be an object")
        require(row.get("hostAccepted") is False, "rejected command must not be host accepted")
        require(row.get("gameInputSentByScheduler") is False, "rejected command must not send scheduler game input")
        require(row.get("hostHelperInputSent") is False, "rejected command must not send host-helper input")
    return {"accepted": accepted, "rejected": rejected}


def require_scheduler(bundle: dict[str, Any], *, accepted: list[Any]) -> dict[str, Any]:
    scheduler = object_at(bundle, "hostAuthorityScheduler")
    require(scheduler.get("authorityModel") == "single-host-authoritative-copied-session", "authority model mismatch")
    require(scheduler.get("arrivalOrder") == ["P2", "P1"], "arrival order should prove schedule is not arrival-order dependent")
    require(scheduler.get("deterministicScheduleOrder") == ["P1", "P2"], "deterministic schedule order mismatch")
    require(scheduler.get("scheduledTickCount") == 1, "scheduled tick count mismatch")
    require(scheduler.get("acceptedCommandCount") == 2, "accepted count mismatch")
    require(scheduler.get("rejectedCommandCount") >= 6, "rejected count too low")
    for key in ("gameInputSentByScheduler", "hostHelperInputSent", "multiHostLanClaim", "publicMatchmakingClaim", "nativeBeaNetcodeClaim", "deterministicSyncClaim", "dualClientParityClaim"):
        require(scheduler.get(key) is False, f"scheduler overclaim must be false: {key}")
    require(scheduler.get("sameWorkstationOnly") is True, "scheduler must record same-workstation boundary")
    plan = list_at(scheduler, "relayPlan")
    require(len(plan) == 2, "relay plan must contain P1/P2 rows")
    require(scheduler.get("relayPlanSha256") == sha256_payload(plan), "relay plan hash mismatch")
    require([row.get("clientSlot") for row in plan if isinstance(row, dict)] == ["P1", "P2"], "relay plan order mismatch")
    require(plan[0].get("mappedInputSequence") == EXPECTED_P1_SEQUENCE, "P1 relay plan sequence mismatch")
    require(plan[0].get("route") == "P1/inputDevice0/top-split-half", "P1 route mismatch")
    require(plan[1].get("mappedInputSequence") == EXPECTED_P2_SEQUENCE, "P2 relay plan sequence mismatch")
    require(plan[1].get("route") == "P2/inputDevice1/bottom-split-half", "P2 route mismatch")
    for row in plan:
        require(row.get("hostHelperInputSent") is False, "relay plan must not claim host-helper input")
    require(sorted(row.get("clientSlot") for row in accepted if isinstance(row, dict)) == ["P1", "P2"], "accepted rows mismatch")
    return scheduler


def require_transcript(bundle: dict[str, Any], *, authorization: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "transportTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "transcript protocol mismatch")
    require(transcript.get("serverIdentityFingerprint") == authorization["serverIdentityFingerprint"], "transcript server identity mismatch")
    require(transcript.get("messageCount") == 22, "transcript message count mismatch")
    events = list_at(transcript, "events")
    require(len(events) == 26, "transcript should contain the observed bounded request/response event summary")
    kinds = [row.get("kind") if isinstance(row, dict) else None for row in events]
    require(kinds.count("server_bound") == 1, "transcript must contain one server_bound event")
    require(kinds.count("client_message") == 10, "transcript must contain ten observed client request events")
    require(kinds.count("server_response") == 10, "transcript must contain ten observed server response events")
    require(kinds.count("client_close") == 2, "transcript must contain two client close events")
    require(kinds.count("client_process_exited") == 2, "transcript must contain two client process exits")
    require(kinds.count("server_stopped") == 1, "transcript must contain one server stopped event")
    accepted_responses = [row for row in events if isinstance(row, dict) and row.get("kind") == "server_response" and row.get("responseType") == "command_accepted"]
    require([row.get("commandId") for row in accepted_responses] == [EXPECTED_P2_COMMAND_ID, EXPECTED_P1_COMMAND_ID], "accepted response arrival order mismatch")
    for index, row in enumerate(events, start=1):
        require(isinstance(row, dict), f"transcript event {index} must be an object")
        if row.get("kind") in {"client_message", "server_response", "client_close"}:
            payload_sha = str(row.get("payloadSha256") or "")
            payload_bytes = row.get("payloadBytes")
            require(len(payload_sha) == 64, f"event {index} missing payload sha")
            require(isinstance(payload_bytes, int) and payload_bytes > 0, f"event {index} missing payload byte count")
    return {"eventCount": len(events), "messageCount": transcript["messageCount"]}


def validate_bundle(path: Path, *, expected_controller_configuration: int) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    remote_path, remote_summary, remote_bundle = require_remote_client_reference(bundle, path)
    require_session_descriptor(bundle, remote_path=remote_path, remote_summary=remote_summary, remote_bundle=remote_bundle)
    transport = require_transport(bundle)
    authorization = require_authorization(bundle)
    process_boundary = require_process_boundary(bundle)
    commands = require_commands(bundle)
    scheduler = require_scheduler(bundle, accepted=commands["accepted"])
    transcript = require_transcript(bundle, authorization=authorization)
    require(expected_controller_configuration == 1, "host-authority smoke is currently bounded to controller configuration 1")
    return {
        "artifact": str(path),
        "privateRemoteClientProofBundle": str(remote_path),
        "claim": "same-workstation two-client host-authority scheduler accepted one P1 and one P2 command from distinct client processes and emitted a deterministic host relay plan",
        "transport": transport["transport"],
        "bindHost": transport["bindHost"],
        "actualBindPort": transport["actualBindPort"],
        "helperVersion": bundle["helperVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "processBoundary": {
            "processModel": process_boundary["processModel"],
            "clientProcessIdsDistinctFromBuilder": process_boundary["clientProcessIdsDistinctFromBuilder"],
            "clientProcessIdsDistinctFromEachOther": process_boundary["clientProcessIdsDistinctFromEachOther"],
            "credentialTransportToClientProcesses": process_boundary["credentialTransportToClientProcesses"],
            "sameWorkstationOnly": process_boundary["sameWorkstationOnly"],
        },
        "authorization": {
            "scheme": authorization["scheme"],
            "credentialStorage": authorization["credentialStorage"],
            "serverIdentityMode": authorization["serverIdentityMode"],
            "clientIdentityMode": authorization["clientIdentityMode"],
            "replayCacheEnabled": authorization["replayCacheEnabled"],
            "sequenceEnforced": authorization["sequenceEnforced"],
            "rateLimit": authorization["rateLimit"],
        },
        "acceptedCommandIds": [row["commandId"] for row in commands["accepted"]],
        "deterministicScheduleOrder": scheduler["deterministicScheduleOrder"],
        "relayPlanSha256": scheduler["relayPlanSha256"],
        "gameInputSentByScheduler": scheduler["gameInputSentByScheduler"],
        "hostHelperInputSent": scheduler["hostHelperInputSent"],
        "upstreamPrivateRemoteClient": {
            "acceptedCommandId": remote_summary["acceptedCommandId"],
            "wouldForwardToPrivateLanCommandId": remote_summary["wouldForwardToPrivateLanCommandId"],
            "remoteClientAccepted": remote_summary["remoteClientAccepted"],
            "gameInputSentByRemoteClient": remote_summary["gameInputSentByRemoteClient"],
            "hostHelperInputSent": remote_summary["hostHelperInputSent"],
        },
        "transcript": transcript,
        "claimBoundary": (
            "This proves only a same-workstation two-client host-authority scheduler smoke chained to existing private "
            "remote-client evidence. It does not prove multi-host LAN play, public matchmaking, public relay/server "
            "behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical "
            "gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def make_transcript_fixture_events() -> list[dict[str, Any]]:
    events = [make_event("server_bound", bindHost=PRIVATE_NON_LOOPBACK_FIXTURE_HOST, actualBindPort=49155)]
    observed = [
        ("P2", "session_hello", None, "session_accepted", None, None),
        ("P2", "command", "host-authority-reject-wrong-command-id-0001", "command_rejected", "command-id-not-allowed", "host-authority-reject-wrong-command-id-0001"),
        ("P2", "command", EXPECTED_P2_COMMAND_ID, "command_accepted", None, EXPECTED_P2_COMMAND_ID),
        ("P2", "command", EXPECTED_P2_COMMAND_ID, "command_rejected", "replay-nonce", EXPECTED_P2_COMMAND_ID),
        ("P2", "command", EXPECTED_P2_COMMAND_ID, "command_rejected", "slot-rate-limit-exceeded", EXPECTED_P2_COMMAND_ID),
        ("P1", "session_hello", None, "session_accepted", None, None),
        ("P1", "command", EXPECTED_P1_COMMAND_ID, "command_rejected", "missing-authentication", EXPECTED_P1_COMMAND_ID),
        ("P1", "command", EXPECTED_P1_COMMAND_ID, "command_rejected", "public-matchmaking-not-allowed", EXPECTED_P1_COMMAND_ID),
        ("P1", "command", EXPECTED_P1_COMMAND_ID, "command_accepted", None, EXPECTED_P1_COMMAND_ID),
        ("P1", "command", EXPECTED_P1_COMMAND_ID, "command_rejected", "direct-input-not-allowed", EXPECTED_P1_COMMAND_ID),
    ]
    for slot, message_type, command_id, response_type, reason, response_command_id in observed:
        request = {"type": message_type, "clientSlot": slot}
        if command_id is not None:
            request["commandId"] = command_id
        events.append(make_event("client_message", request, clientSlot=slot, messageType=message_type, commandId=command_id))
        response = {"type": response_type, "clientSlot": slot}
        if reason is not None:
            response["reason"] = reason
        if response_command_id is not None:
            response["commandId"] = response_command_id
        events.append(make_event("server_response", response, clientSlot=slot, responseType=response_type, reason=reason, commandId=response_command_id, scheduledTick=1 if response_type == "command_accepted" else None))
    events.append(make_event("client_close", {"type": "close"}))
    events.append(make_event("client_close", {"type": "close"}))
    events.append(make_event("client_process_exited", processId=101, clientSlot="P2", exitCode=0))
    events.append(make_event("client_process_exited", processId=102, clientSlot="P1", exitCode=0))
    events.append(make_event("server_stopped"))
    return events


def make_bundle_fixture(
    root: Path,
    *,
    scheduler_input_claim: bool = False,
    public_matchmaking_claim: bool = False,
    same_process_claim: bool = False,
    wrong_schedule_order: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    remote_path = remote.make_bundle_fixture(root / "private-remote")
    remote_summary = remote.validate_bundle(remote_path, expected_controller_configuration=1)
    remote_bundle = read_json(remote_path)
    upstream_descriptor = object_at(remote_bundle, "sessionDescriptor")
    auth = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "slotCredentialFingerprints": {"P1": "1" * 64, "P2": "2" * 64},
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": "3" * 64,
        "clientIdentityMode": "pinned-slot-fingerprint",
        "clientIdentityFingerprints": {"P1": "4" * 64, "P2": "5" * 64},
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {"maxAcceptedCommandsPerSlot": 1, "maxAcceptedCommandsPerTick": 2},
        "clockMode": "deterministic-smoke-clock",
    }
    accepted = [
        {"commandId": EXPECTED_P2_COMMAND_ID, "clientSlot": "P2", "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P2_SEQUENCE, "scheduledTick": 1, "arrivalOrder": 1, "hostAccepted": True, "gameInputSentByScheduler": scheduler_input_claim, "hostHelperInputSent": False},
        {"commandId": EXPECTED_P1_COMMAND_ID, "clientSlot": "P1", "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P1_SEQUENCE, "scheduledTick": 1, "arrivalOrder": 2, "hostAccepted": True, "gameInputSentByScheduler": scheduler_input_claim, "hostHelperInputSent": False},
    ]
    relay_plan = [
        {"scheduledTick": 1, "clientSlot": "P1", "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P1_SEQUENCE, "route": "P1/inputDevice0/top-split-half", "hostHelperInputSent": False},
        {"scheduledTick": 1, "clientSlot": "P2", "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P2_SEQUENCE, "route": "P2/inputDevice1/bottom-split-half", "hostHelperInputSent": False},
    ]
    if wrong_schedule_order:
        relay_plan = list(reversed(relay_plan))
    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "privateRemoteClientProofBundle": remote_path.resolve().relative_to(root.resolve()).as_posix(),
        "privateRemoteClientProofSha256": remote.sha256_file(remote_path),
        "sessionDescriptor": {
            "schemaVersion": EXPECTED_SESSION_SCHEMA,
            "protocolVersion": EXPECTED_PROTOCOL,
            "upstreamPrivateRemoteClientProtocolVersion": remote.EXPECTED_PROTOCOL,
            "upstreamPrivateRemoteClientProofSha256": remote.sha256_file(remote_path),
            "upstreamPrivateRemoteClientTransport": remote_summary["transport"],
            "sessionCompatibilityKey": upstream_descriptor["sessionCompatibilityKey"],
            "cleanSpecimenSha256": upstream_descriptor["cleanSpecimenSha256"],
            "levelId": 850,
            "controllerConfiguration": 1,
            "hostAuthorityModel": "single-host-authoritative-copied-session",
            "clientSlots": ["P1", "P2"],
            "allowedCommands": {
                "P1": {"commandId": EXPECTED_P1_COMMAND_ID, "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P1_SEQUENCE},
                "P2": {"commandId": EXPECTED_P2_COMMAND_ID, "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P2_SEQUENCE},
            },
            "upstreamPrivateRemoteClientCommandId": remote.EXPECTED_COMMAND_ID,
            "upstreamPrivateLanCommandId": remote_summary["wouldForwardToPrivateLanCommandId"],
        },
        "transport": {
            "transport": EXPECTED_TRANSPORT,
            "bindHost": PRIVATE_NON_LOOPBACK_FIXTURE_HOST,
            "actualBindPort": 49155,
            "networkScope": "private-interface-two-client-host-authority-smoke",
            "privateLanInterfaceBound": True,
            "loopbackInterfaceOnly": False,
            "sameWorkstationOnly": True,
            "processSeparatedClients": not same_process_claim,
            "twoDistinctClientProcesses": not same_process_claim,
            "publicNetworkSocketsOpened": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": public_matchmaking_claim,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "natTraversalClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "gameInputSentByScheduler": scheduler_input_claim,
            "hostHelperInputSent": False,
        },
        "authorization": auth,
        "clientProcessBoundary": {
            "processModel": "two-separate-python-client-processes",
            "builderProcessId": 100,
            "clientProcesses": [
                {"clientSlot": "P2", "clientProcessId": 101, "clientVerifiedServerIdentity": True, "clientExitCode": 0},
                {"clientSlot": "P1", "clientProcessId": 102 if not same_process_claim else 101, "clientVerifiedServerIdentity": True, "clientExitCode": 0},
            ],
            "clientProcessIdsDistinctFromBuilder": True,
            "clientProcessIdsDistinctFromEachOther": not same_process_claim,
            "credentialTransportToClientProcesses": "stdin-ephemeral-not-serialized-to-artifact",
            "clientCommandLineContainsCredential": False,
            "clientEnvironmentContainsCredential": False,
            "clientStdoutContainsCredential": False,
            "clientStderrContainsCredential": False,
            "sameWorkstationOnly": True,
            "multiHostLanClaim": False,
            "clientResponses": {
                "P1": [
                    {"label": "session", "type": "session_accepted", "commandId": None, "reason": None},
                    {"label": "missing-auth", "type": "command_rejected", "reason": "missing-authentication", "commandId": EXPECTED_P1_COMMAND_ID},
                    {"label": "public-matchmaking-claim", "type": "command_rejected", "reason": "public-matchmaking-not-allowed", "commandId": EXPECTED_P1_COMMAND_ID},
                    {"label": "accepted", "type": "command_accepted", "reason": None, "commandId": EXPECTED_P1_COMMAND_ID},
                    {"label": "direct-input-claim", "type": "command_rejected", "reason": "direct-input-not-allowed", "commandId": EXPECTED_P1_COMMAND_ID},
                ],
                "P2": [
                    {"label": "session", "type": "session_accepted", "commandId": None, "reason": None},
                    {"label": "wrong-command-id", "type": "command_rejected", "reason": "command-id-not-allowed", "commandId": "host-authority-reject-wrong-command-id-0001"},
                    {"label": "accepted", "type": "command_accepted", "reason": None, "commandId": EXPECTED_P2_COMMAND_ID},
                    {"label": "replay", "type": "command_rejected", "reason": "replay-nonce", "commandId": EXPECTED_P2_COMMAND_ID},
                    {"label": "rate-limit", "type": "command_rejected", "reason": "slot-rate-limit-exceeded", "commandId": EXPECTED_P2_COMMAND_ID},
                ],
            },
        },
        "commands": {
            "accepted": accepted,
            "rejected": [
                {"commandId": EXPECTED_P1_COMMAND_ID, "clientSlot": "P1", "reason": "missing-authentication", "hostAccepted": False, "gameInputSentByScheduler": False, "hostHelperInputSent": False},
                {"commandId": EXPECTED_P1_COMMAND_ID, "clientSlot": "P1", "reason": "public-matchmaking-not-allowed", "hostAccepted": False, "gameInputSentByScheduler": False, "hostHelperInputSent": False},
                {"commandId": EXPECTED_P1_COMMAND_ID, "clientSlot": "P1", "reason": "direct-input-not-allowed", "hostAccepted": False, "gameInputSentByScheduler": False, "hostHelperInputSent": False},
                {"commandId": "host-authority-reject-wrong-command-id-0001", "clientSlot": "P2", "reason": "command-id-not-allowed", "hostAccepted": False, "gameInputSentByScheduler": False, "hostHelperInputSent": False},
                {"commandId": EXPECTED_P2_COMMAND_ID, "clientSlot": "P2", "reason": "replay-nonce", "hostAccepted": False, "gameInputSentByScheduler": False, "hostHelperInputSent": False},
                {"commandId": EXPECTED_P2_COMMAND_ID, "clientSlot": "P2", "reason": "slot-rate-limit-exceeded", "hostAccepted": False, "gameInputSentByScheduler": False, "hostHelperInputSent": False},
            ],
        },
        "hostAuthorityScheduler": {
            "authorityModel": "single-host-authoritative-copied-session",
            "arrivalOrder": ["P2", "P1"],
            "deterministicScheduleOrder": ["P2", "P1"] if wrong_schedule_order else ["P1", "P2"],
            "scheduledTickCount": 1,
            "acceptedCommandCount": 2,
            "rejectedCommandCount": 6,
            "relayPlan": relay_plan,
            "relayPlanSha256": sha256_payload(relay_plan),
            "gameInputSentByScheduler": scheduler_input_claim,
            "hostHelperInputSent": False,
            "sameWorkstationOnly": True,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": public_matchmaking_claim,
            "nativeBeaNetcodeClaim": False,
            "deterministicSyncClaim": False,
            "dualClientParityClaim": False,
        },
        "transportTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": auth["serverIdentityFingerprint"],
            "messageCount": 22,
            "events": make_transcript_fixture_events(),
        },
    }
    output = root / "host-authority-two-client-smoke-proof.json"
    output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return output


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        validate_bundle(make_bundle_fixture(Path(tmp)), expected_controller_configuration=1)
    for label, kwargs in (
        ("scheduler direct-input claim should fail", {"scheduler_input_claim": True}),
        ("public matchmaking claim should fail", {"public_matchmaking_claim": True}),
        ("same-process client claim should fail", {"same_process_claim": True}),
        ("wrong schedule order should fail", {"wrong_schedule_order": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs), expected_controller_configuration=1)
            except HostAuthorityTwoClientSmokeProofError:
                continue
            raise AssertionError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority two-client smoke checker self-test: PASS")
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
        HostAuthorityTwoClientSmokeProofError,
        remote.PrivateRemoteClientSmokeProofError,
        remote.lan.PrivateTransportSmokeProofError,
        remote.lan.delivery.PrivateRelayDeliveryProofError,
        remote.lan.delivery.relay.RelayProofError,
        remote.lan.delivery.loopback.LoopbackProofError,
        remote.lan.delivery.loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary host-authority two-client smoke check: FAIL: {exc}")
        raise SystemExit(2)
