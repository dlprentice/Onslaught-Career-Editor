#!/usr/bin/env python3
"""Validate a concurrent four-client N-slot host-authority process smoke proof."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-original-binary-host-authority-n-slot-concurrent-process-smoke.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-host-authority-n-slot-session.v1"
EXPECTED_TRANSPORT = "host-authority-n-slot-tcp-jsonl-concurrent-process-smoke"
EXPECTED_PROTOCOL = "host-authority-n-slot-input.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-n-slot-concurrent-process-smoke-helper"
EXPECTED_HELPER_VERSION = "host-authority-n-slot-concurrent-process-smoke-helper.v1"
EXPECTED_COMMAND = "forward"
EXPECTED_P1_COMMAND_ID = "host-authority-p1-forward-0001"
EXPECTED_P2_COMMAND_ID = "host-authority-p2-forward-0001"
EXPECTED_P3_COMMAND_ID = "host-authority-p3-forward-0001"
EXPECTED_P4_COMMAND_ID = "host-authority-p4-forward-0001"
EXPECTED_P1_SEQUENCE = "down:Q,wait:500,up:Q"
EXPECTED_P2_SEQUENCE = "down:E,wait:500,up:E"
EXPECTED_P3_SEQUENCE = "down:R,wait:500,up:R"
EXPECTED_P4_SEQUENCE = "down:T,wait:500,up:T"
EXPECTED_SLOTS = ["P1", "P2", "P3", "P4"]
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_ARRIVAL_ORDER = ["P4", "P2", "P3", "P1"]
EXPECTED_CANONICAL_N_SLOT_RELAY_HASH = "ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002"
EXPECTED_RUNTIME_P1P2_RELAY_HASH = "fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376"
EXPECTED_CONCURRENCY_MODEL = "barrier-concurrent-client-processes"
PRIVATE_NON_LOOPBACK_FIXTURE_HOST = "192.0.2.114"  # TEST-NET-1 fixture, not an operator LAN address.
SAFE_CREDENTIAL_METADATA_KEYS = {
    "clientcommandlinecontainscredential",
    "clientenvironmentcontainscredential",
    "clientstderrcontainscredential",
    "clientstdoutcontainscredential",
    "credentialstorage",
    "credentialtransporttoclientprocesses",
    "serializedcredentialpresent",
    "slotcredentialfingerprints",
}
DANGEROUS_KEY_FRAGMENTS = ("secret", "password", "token", "authkey", "credential", "hmac", "apikey", "api_key")


class HostAuthorityNSlotProcessSmokeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityNSlotProcessSmokeProofError(message)


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


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


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
            require(
                not any(fragment in lowered for fragment in DANGEROUS_KEY_FRAGMENTS) or lowered in SAFE_CREDENTIAL_METADATA_KEYS,
                f"serialized credential-like field is not allowed at {path}.{key}",
            )
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected N-slot process smoke schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected N-slot helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected N-slot helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected N-slot protocol")


def require_transport(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == EXPECTED_TRANSPORT, "transport mismatch")
    require(is_private_non_loopback_host(str(transport.get("bindHost") or "")), "N-slot smoke must bind private non-loopback host")
    require(isinstance(transport.get("actualBindPort"), int), "actualBindPort must be present")
    require(transport.get("networkScope") == "private-interface-n-slot-concurrent-process-smoke", "network scope mismatch")
    require(transport.get("privateLanInterfaceBound") is True, "private LAN interface must be bound")
    require(transport.get("privateLanReachableDuringRun") is True, "private LAN reachability must be explicit")
    require(transport.get("foreignPeersRejectedAfterAccept") is True, "foreign peer rejection boundary must be explicit")
    require(transport.get("loopbackInterfaceOnly") is False, "N-slot smoke must not be loopback-only")
    require(transport.get("sameWorkstationClientProcessesOnly") is True, "same-workstation client process boundary must be recorded")
    require(transport.get("sameWorkstationNetworkOnly") is False, "private-interface listener must not claim same-workstation-only networking")
    require(transport.get("processSeparatedClients") is True, "process-separated clients must be true")
    require(transport.get("processConcurrencyModel") == EXPECTED_CONCURRENCY_MODEL, "process concurrency model mismatch")
    require(transport.get("simultaneousClientProcessesProven") == 4, "simultaneous client process proof must be four")
    require(transport.get("clientReadyBeforeBarrierReleaseCount") == 4, "all clients must be ready before barrier release")
    require(transport.get("barrierReleaseAfterAllClientsReady") is True, "barrier release must follow all client readiness")
    require(transport.get("maxSimultaneousSocketConnectionsProven") == 4, "socket concurrency proof must be four")
    require(transport.get("clientProcessCount") == 4, "transport must record four client processes")
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
        "gameInputSentByNSlotScheduler",
        "hostHelperInputSent",
    ):
        require(transport.get(key) is False, f"transport overclaim must be false: {key}")
    require(transport.get("newBeaLaunchCount") == 0, "N-slot process smoke must not launch BEA")
    require(transport.get("cdbAttachCount") == 0, "N-slot process smoke must not attach CDB")
    return transport


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must not be present")
    fingerprints = object_at(authorization, "slotCredentialFingerprints")
    require(sorted(fingerprints) == EXPECTED_SLOTS, "slot credential fingerprints must cover P1-P4")
    client_ids = object_at(authorization, "clientIdentityFingerprints")
    require(sorted(client_ids) == EXPECTED_SLOTS, "client identity fingerprints must cover P1-P4")
    for collection_name, collection in (("slot credential", fingerprints), ("client identity", client_ids)):
        for slot, value in collection.items():
            require(isinstance(value, str) and len(value) == 64, f"{collection_name} fingerprint for {slot} must be SHA-256")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(isinstance(authorization.get("serverIdentityFingerprint"), str) and len(authorization["serverIdentityFingerprint"]) == 64, "server identity fingerprint must be SHA-256")
    require(authorization.get("clientIdentityMode") == "pinned-slot-fingerprint", "client identity mode mismatch")
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window mismatch")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("replayCacheScope") == "slot-nonce-smoke", "replay cache scope mismatch")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement must be enabled")
    rate = object_at(authorization, "rateLimit")
    require(rate.get("maxAcceptedCommandsPerSlot") == 1, "per-slot rate limit mismatch")
    require(rate.get("maxAcceptedCommandsPerTick") == 2, "per-tick rate limit mismatch")
    require(authorization.get("clockMode") == "deterministic-smoke-clock", "clock mode mismatch")
    require(authorization.get("securityProofScope") == "minimal-smoke-hmac-envelope-not-full-session-security-proof", "security proof scope must be bounded")
    for key in (
        "sessionScopedMacCoverageProof",
        "maxJsonLineBytesEnforced",
        "unknownFieldRejectionProof",
        "strictMessageSchemaProof",
        "tickBoundMacFieldsProof",
    ):
        require(authorization.get(key) is False, f"unproven security claim must be false: {key}")
    return authorization


def require_session_descriptor(bundle: dict[str, Any]) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "session schema mismatch")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "session protocol mismatch")
    require(descriptor.get("hostAuthorityModel") == "single-host-authoritative-copied-session", "host authority model mismatch")
    require(descriptor.get("slotCapacity") == 4, "slot capacity must be four")
    require(descriptor.get("acceptedSessionParticipantCount") == 4, "accepted participant count must be four")
    require(descriptor.get("originalBinaryActiveSlots") == EXPECTED_ACTIVE_SLOTS, "active original-binary slots mismatch")
    require(descriptor.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata-only slots mismatch")
    participants = list_at(descriptor, "participants")
    require(len(participants) == 4, "expected four participant rows")
    require([row.get("slotId") for row in participants if isinstance(row, dict)] == EXPECTED_SLOTS, "participant order must be P1-P4")
    for row in participants:
        require(isinstance(row, dict), "participant row must be an object")
        slot = row.get("slotId")
        if slot in EXPECTED_ACTIVE_SLOTS:
            require(row.get("sessionAdmission") == "accepted-active-original-binary-slot", f"{slot} active admission mismatch")
            require(row.get("commandPermission") == "original-binary-command-allowed-when-authenticated", f"{slot} command permission mismatch")
            require(str(row.get("runtimeRoute", "")).startswith(str(slot) + "/inputDevice"), f"{slot} runtime route mismatch")
        else:
            require(slot in EXPECTED_METADATA_SLOTS, f"unexpected metadata slot: {slot}")
            require(row.get("sessionAdmission") == "accepted-metadata-only-no-original-binary-gameplay-route", f"{slot} metadata admission mismatch")
            require(row.get("runtimeRoute") == "unsupported-original-binary-active-slot", f"{slot} runtime route must stay unsupported")
            require(row.get("commandPermission") == "reject-gameplay-input-until-new-proof-class", f"{slot} gameplay command permission must stay rejected")
    return descriptor


def require_process_boundary(bundle: dict[str, Any]) -> dict[str, Any]:
    boundary = object_at(bundle, "clientProcessBoundary")
    require(boundary.get("processModel") == "four-separate-python-client-processes", "process model mismatch")
    require(boundary.get("processConcurrencyModel") == EXPECTED_CONCURRENCY_MODEL, "process concurrency model mismatch")
    require(boundary.get("simultaneousClientProcessesProven") == 4, "simultaneous client process proof must be four")
    require(boundary.get("allClientProcessesReadyBeforeBarrierRelease") is True, "all clients must be ready before barrier release")
    require(boundary.get("allClientProcessesAliveAtBarrierRelease") is True, "all clients must be alive at barrier release")
    require(boundary.get("allClientSocketsHeldUntilCloseRelease") is True, "all client sockets must hold until close release")
    require(boundary.get("clientProcessCount") == 4, "expected four client processes")
    builder_pid = boundary.get("builderProcessId")
    require(isinstance(builder_pid, int) and builder_pid > 0, "builder process id must be positive")
    processes = list_at(boundary, "clientProcesses")
    require(len(processes) == 4, "expected four client process rows")
    require([row.get("clientSlot") for row in processes if isinstance(row, dict)] == EXPECTED_ARRIVAL_ORDER, "client process arrival order mismatch")
    client_pids: list[int] = []
    for row in processes:
        require(isinstance(row, dict), "client process row must be an object")
        pid = row.get("clientProcessId")
        require(isinstance(pid, int) and pid > 0, "client process id must be positive")
        parent_pid = row.get("clientProcessIdFromParent")
        require(isinstance(parent_pid, int) and parent_pid > 0, "parent-observed client process id must be positive")
        require(parent_pid == pid, "child-reported client process id must match parent-observed Popen pid")
        client_pids.append(pid)
        require(row.get("clientVerifiedServerIdentity") is True, "client must verify server identity")
        require(row.get("clientExitCode") == 0, "client process must exit cleanly")
    require(boundary.get("clientProcessIdsDistinctFromBuilder") is True, "client PIDs must differ from builder")
    require(builder_pid not in client_pids, "client process id matched builder")
    require(boundary.get("clientProcessIdsDistinctFromEachOther") is True, "client PIDs must differ from each other")
    require(len(set(client_pids)) == 4, "client process ids must be unique")
    require(boundary.get("credentialTransportToClientProcesses") == "stdin-ephemeral-not-serialized-to-artifact", "credential transport mismatch")
    require(boundary.get("clientEnvSensitiveKeyCount") == 0, "client subprocess environment must be sanitized")
    for key in (
        "clientCommandLineContainsCredential",
        "clientEnvironmentContainsCredential",
        "clientStdoutContainsCredential",
        "clientStderrContainsCredential",
        "multiHostLanClaim",
    ):
        require(boundary.get(key) is False, f"process boundary overclaim must be false: {key}")
    require(boundary.get("sameWorkstationClientProcessesOnly") is True, "process boundary must record same-workstation clients")
    require(boundary.get("sameWorkstationNetworkOnly") is False, "process boundary must not claim same-workstation-only networking")
    responses = object_at(boundary, "clientResponses")
    require(sorted(responses) == EXPECTED_SLOTS, "client responses must cover P1-P4")
    expected = {
        "P1": [("session", "session_accepted", None, None), ("accepted", "command_accepted", None, EXPECTED_P1_COMMAND_ID)],
        "P2": [("session", "session_accepted", None, None), ("accepted", "command_accepted", None, EXPECTED_P2_COMMAND_ID)],
        "P3": [("session", "session_accepted", None, None), ("rejected-gameplay-route", "command_rejected", "required-for-unproven-original-binary-slots", EXPECTED_P3_COMMAND_ID)],
        "P4": [("session", "session_accepted", None, None), ("rejected-gameplay-route", "command_rejected", "required-for-unproven-original-binary-slots", EXPECTED_P4_COMMAND_ID)],
    }
    for slot, expected_rows in expected.items():
        rows = list_at(responses, slot)
        summary = [(row.get("label"), row.get("type"), row.get("reason"), row.get("commandId")) for row in rows if isinstance(row, dict)]
        require(summary == expected_rows, f"{slot} response sequence mismatch")
    return boundary


def require_concurrency_proof(bundle: dict[str, Any]) -> dict[str, Any]:
    proof = object_at(bundle, "concurrencyProof")
    require(proof.get("processConcurrencyModel") == EXPECTED_CONCURRENCY_MODEL, "concurrency proof model mismatch")
    require(proof.get("clientReadyBeforeBarrierReleaseCount") == 4, "readiness count mismatch")
    require(proof.get("barrierReleaseAfterAllClientsReady") is True, "barrier must release after readiness")
    require(proof.get("maxSimultaneousClientProcessesProven") == 4, "simultaneous process proof mismatch")
    require(proof.get("maxSimultaneousSocketConnectionsProven") == 4, "simultaneous socket proof mismatch")
    require(proof.get("allClientProcessesAliveAtBarrierRelease") is True, "clients must be alive at barrier release")
    require(proof.get("allClientSocketsHeldUntilCloseRelease") is True, "client sockets must be held until close release")
    timings = list_at(proof, "clientProcessTiming")
    require(len(timings) == 4, "expected four client timing rows")
    require([row.get("clientSlot") for row in timings if isinstance(row, dict)] == EXPECTED_ARRIVAL_ORDER, "client timing order mismatch")
    for row in timings:
        require(isinstance(row, dict), "client timing row must be an object")
        for key in (
            "processStartedBeforeBarrierRelease",
            "readyBeforeBarrierRelease",
            "processExitedAfterBarrierRelease",
            "socketOpenedBeforeCloseRelease",
            "socketClosedAfterCloseRelease",
        ):
            require(row.get(key) is True, f"client timing proof must be true: {key}")
    return proof


def require_commands(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "acceptedOriginalBinaryGameplay")
    rejected = list_at(commands, "rejectedOriginalBinaryGameplay")
    require(len(accepted) == 2, "expected exactly two accepted original-binary gameplay commands")
    require(len(rejected) == 2, "expected exactly two rejected P3/P4 gameplay commands")
    require([row.get("clientSlot") for row in accepted if isinstance(row, dict)] == ["P2", "P1"], "accepted arrival order must be P2,P1")
    accepted_by_slot = {row.get("clientSlot"): row for row in accepted if isinstance(row, dict)}
    require(set(accepted_by_slot) == set(EXPECTED_ACTIVE_SLOTS), "accepted commands must cover P1/P2")
    require(accepted_by_slot["P1"].get("commandId") == EXPECTED_P1_COMMAND_ID, "P1 command id mismatch")
    require(accepted_by_slot["P1"].get("mappedInputSequence") == EXPECTED_P1_SEQUENCE, "P1 mapped sequence mismatch")
    require(accepted_by_slot["P2"].get("commandId") == EXPECTED_P2_COMMAND_ID, "P2 command id mismatch")
    require(accepted_by_slot["P2"].get("mappedInputSequence") == EXPECTED_P2_SEQUENCE, "P2 mapped sequence mismatch")
    for row in accepted:
        require(row.get("command") == EXPECTED_COMMAND, "accepted command mismatch")
        require(row.get("hostAccepted") is True, "accepted command must be host accepted")
        require(row.get("scheduledTick") == 1, "accepted command tick mismatch")
        require(row.get("gameInputSentByNSlotScheduler") is False, "accepted command must not send scheduler game input")
        require(row.get("hostHelperInputSent") is False, "accepted command must not send host-helper input")
    rejected_by_slot = {row.get("clientSlot"): row for row in rejected if isinstance(row, dict)}
    require(set(rejected_by_slot) == set(EXPECTED_METADATA_SLOTS), "rejected commands must cover P3/P4")
    for slot in EXPECTED_METADATA_SLOTS:
        row = rejected_by_slot[slot]
        require(row.get("reason") == "required-for-unproven-original-binary-slots", f"{slot} rejection reason mismatch")
        require(row.get("hostAccepted") is False, f"{slot} must not be host accepted")
        require(row.get("gameInputSentByNSlotScheduler") is False, f"{slot} must not send scheduler game input")
        require(row.get("hostHelperInputSent") is False, f"{slot} must not send host-helper input")
    return commands


def require_scheduler(bundle: dict[str, Any]) -> dict[str, Any]:
    scheduler = object_at(bundle, "hostAuthorityNSlotScheduler")
    require(scheduler.get("schedulerSchema") == "host-authority-n-slot-scheduler.v1", "scheduler schema mismatch")
    require(scheduler.get("declaredSlotCount") == 4, "declared slot count must be four")
    require(scheduler.get("slotCapacity") == 4, "slot capacity must be four")
    require(scheduler.get("acceptedSessionParticipantCount") == 4, "accepted participant count must be four")
    require(scheduler.get("originalBinaryRelaySlotCount") == 2, "original-binary relay count must stay P1/P2")
    require(scheduler.get("acceptedOriginalBinaryGameplayCommandCount") == 2, "accepted gameplay command count mismatch")
    require(scheduler.get("rejectedOriginalBinaryGameplayCommandCount") == 2, "P3/P4 rejection count mismatch")
    require(scheduler.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "accepted gameplay slots mismatch")
    require(scheduler.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata slots mismatch")
    require(scheduler.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "rejected route slots mismatch")
    require(scheduler.get("extraSlotRejectionPolicy") == "required-for-unproven-original-binary-slots", "extra slot rejection policy mismatch")
    require(scheduler.get("arrivalOrder") == EXPECTED_ARRIVAL_ORDER, "arrival order mismatch")
    require(scheduler.get("deterministicParticipantOrder") == EXPECTED_SLOTS, "deterministic participant order mismatch")
    require(scheduler.get("deterministicOriginalBinaryRelayOrder") == EXPECTED_ACTIVE_SLOTS, "deterministic relay order mismatch")
    plan = list_at(scheduler, "relayPlan")
    require(len(plan) == 2, "relay plan must contain only P1/P2")
    require([row.get("clientSlot") for row in plan if isinstance(row, dict)] == EXPECTED_ACTIVE_SLOTS, "relay plan slot order mismatch")
    require(plan[0].get("commandId") == EXPECTED_P1_COMMAND_ID, "P1 relay command mismatch")
    require(plan[0].get("mappedInputSequence") == EXPECTED_P1_SEQUENCE, "P1 relay sequence mismatch")
    require(plan[1].get("commandId") == EXPECTED_P2_COMMAND_ID, "P2 relay command mismatch")
    require(plan[1].get("mappedInputSequence") == EXPECTED_P2_SEQUENCE, "P2 relay sequence mismatch")
    for row in plan:
        require(row.get("clientSlot") in EXPECTED_ACTIVE_SLOTS, "relay plan must not include P3/P4")
        require(row.get("hostHelperInputSent") is False, "relay plan must not claim host-helper input")
    require(scheduler.get("relayPlanSha256") == sha256_payload(plan), "relay plan hash mismatch")
    require(scheduler.get("relayPlanSha256") == EXPECTED_CANONICAL_N_SLOT_RELAY_HASH, "canonical N-slot relay hash drifted")
    require(scheduler.get("runtimeCompatibleP1P2RelayHash") == EXPECTED_RUNTIME_P1P2_RELAY_HASH, "runtime-compatible P1/P2 relay hash drifted")
    for key in (
        "gameInputSentByNSlotScheduler",
        "hostHelperInputSent",
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "nativeBeaNetcodeClaim",
        "deterministicSyncClaim",
        "rollbackClaim",
        "antiCheatClaim",
        "moreThanTwoRuntimePlayerClaim",
    ):
        require(scheduler.get(key) is False, f"scheduler overclaim must be false: {key}")
    require(scheduler.get("newBeaLaunchCount") == 0, "scheduler proof must not launch BEA")
    require(scheduler.get("cdbAttachCount") == 0, "scheduler proof must not attach CDB")
    return scheduler


def require_transcript(bundle: dict[str, Any], *, authorization: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "transportTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "transcript protocol mismatch")
    require(transcript.get("serverIdentityFingerprint") == authorization["serverIdentityFingerprint"], "server identity mismatch")
    require(transcript.get("messageCount") == 20, "transcript message count mismatch")
    events = list_at(transcript, "events")
    kinds = [row.get("kind") if isinstance(row, dict) else None for row in events]
    require(kinds.count("server_bound") == 1, "transcript must contain one server_bound event")
    require(kinds.count("client_barrier_ready") == 4, "transcript must contain four client barrier-ready events")
    require(kinds.count("barrier_released") == 1, "transcript must contain one barrier release event")
    require(kinds.count("server_active_connection_count") >= 1, "transcript must contain active connection count evidence")
    require(any(row.get("kind") == "server_active_connection_count" and row.get("activeConnectionCount") == 4 for row in events if isinstance(row, dict)), "transcript must prove four simultaneous socket connections")
    require(kinds.count("close_barrier_released") == 1, "transcript must contain one close barrier release event")
    require(kinds.count("client_message") == 8, "transcript must contain eight observed client requests")
    require(kinds.count("server_response") == 8, "transcript must contain eight observed server responses")
    require(kinds.count("client_close") == 4, "transcript must contain four client close events")
    require(kinds.count("client_process_exited") == 4, "transcript must contain four process exits")
    require(kinds.count("server_stopped") == 1, "transcript must contain one server stopped event")
    accepted_responses = [row for row in events if isinstance(row, dict) and row.get("kind") == "server_response" and row.get("responseType") == "command_accepted"]
    require([row.get("clientSlot") for row in accepted_responses] == ["P2", "P1"], "accepted response arrival order mismatch")
    rejected_responses = [row for row in events if isinstance(row, dict) and row.get("kind") == "server_response" and row.get("responseType") == "command_rejected"]
    require([row.get("clientSlot") for row in rejected_responses] == ["P4", "P3"], "P3/P4 rejection arrival order mismatch")
    for index, row in enumerate(events, start=1):
        require(isinstance(row, dict), f"transcript event {index} must be an object")
        if row.get("kind") in {"client_message", "server_response", "client_close"}:
            payload_sha = str(row.get("payloadSha256") or "")
            payload_bytes = row.get("payloadBytes")
            require(len(payload_sha) == 64, f"event {index} missing payload sha")
            require(isinstance(payload_bytes, int) and payload_bytes > 0, f"event {index} missing payload byte count")
    return {"eventCount": len(events), "messageCount": transcript["messageCount"]}


def require_non_claims(bundle: dict[str, Any]) -> None:
    non_claims = object_at(bundle, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")
    required_false = (
        "fourPlayerGameplayProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "coOpModeRuntimeProof",
        "versusModeRuntimeProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "deterministicSyncProof",
        "rollbackProof",
        "antiCheatProof",
        "physicalGamepadProof",
        "rebuildParityProof",
        "noNoticeableDifferenceProof",
    )
    for key in required_false:
        require(key in non_claims, f"missing non-claim: {key}")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    transport = require_transport(bundle)
    authorization = require_authorization(bundle)
    require_session_descriptor(bundle)
    process_boundary = require_process_boundary(bundle)
    concurrency_proof = require_concurrency_proof(bundle)
    require_commands(bundle)
    scheduler = require_scheduler(bundle)
    transcript = require_transcript(bundle, authorization=authorization)
    require_non_claims(bundle)
    require(bundle.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player original-binary runtime proof must remain zero")
    require(bundle.get("activeP3P4OriginalBinaryGameplayProof") is False, "active P3/P4 gameplay proof must remain false")
    require(bundle.get("permanentImpossibilityClaim") is False, "permanent impossibility claim must remain false")
    return {
        "artifact": str(path),
        "schemaVersion": bundle["schemaVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "transport": transport["transport"],
        "processModel": process_boundary["processModel"],
        "processConcurrencyModel": process_boundary["processConcurrencyModel"],
        "simultaneousClientProcessesProven": process_boundary["simultaneousClientProcessesProven"],
        "maxSimultaneousSocketConnectionsProven": concurrency_proof["maxSimultaneousSocketConnectionsProven"],
        "clientReadyBeforeBarrierReleaseCount": concurrency_proof["clientReadyBeforeBarrierReleaseCount"],
        "clientProcessCount": process_boundary["clientProcessCount"],
        "clientProcessIdsDistinctFromBuilder": process_boundary["clientProcessIdsDistinctFromBuilder"],
        "clientProcessIdsDistinctFromEachOther": process_boundary["clientProcessIdsDistinctFromEachOther"],
        "credentialTransportToClientProcesses": process_boundary["credentialTransportToClientProcesses"],
        "clientEnvSensitiveKeyCount": process_boundary["clientEnvSensitiveKeyCount"],
        "sameWorkstationClientProcessesOnly": process_boundary["sameWorkstationClientProcessesOnly"],
        "sameWorkstationNetworkOnly": transport["sameWorkstationNetworkOnly"],
        "privateLanReachableDuringRun": transport["privateLanReachableDuringRun"],
        "foreignPeersRejectedAfterAccept": transport["foreignPeersRejectedAfterAccept"],
        "securityProofScope": authorization["securityProofScope"],
        "slotCapacity": scheduler["slotCapacity"],
        "acceptedSessionParticipantCount": scheduler["acceptedSessionParticipantCount"],
        "acceptedOriginalBinaryGameplayCommandCount": scheduler["acceptedOriginalBinaryGameplayCommandCount"],
        "rejectedOriginalBinaryGameplayCommandCount": scheduler["rejectedOriginalBinaryGameplayCommandCount"],
        "acceptedOriginalBinaryGameplaySlots": scheduler["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": scheduler["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": scheduler["rejectedGameplayRouteSlots"],
        "arrivalOrder": scheduler["arrivalOrder"],
        "deterministicParticipantOrder": scheduler["deterministicParticipantOrder"],
        "deterministicOriginalBinaryRelayOrder": scheduler["deterministicOriginalBinaryRelayOrder"],
        "relayPlanSha256": scheduler["relayPlanSha256"],
        "runtimeCompatibleP1P2RelayHash": scheduler["runtimeCompatibleP1P2RelayHash"],
        "gameInputSentByNSlotScheduler": scheduler["gameInputSentByNSlotScheduler"],
        "hostHelperInputSent": scheduler["hostHelperInputSent"],
        "newBeaLaunchCount": scheduler["newBeaLaunchCount"],
        "cdbAttachCount": scheduler["cdbAttachCount"],
        "nPlayerOriginalBinaryRuntimeProof": bundle.get("nPlayerOriginalBinaryRuntimeProof"),
        "activeP3P4OriginalBinaryGameplayProof": bundle.get("activeP3P4OriginalBinaryGameplayProof"),
        "permanentImpossibilityClaim": bundle.get("permanentImpossibilityClaim"),
        "transcript": transcript,
        "claimBoundary": (
            "This validates only a same-workstation-client/private-interface concurrent four-client N-slot "
            "scheduler/process smoke. It proves four separate slot-scoped local client processes and four "
            "private-interface socket connections can overlap behind a barrier in the host-authority process layer "
            "while only P1/P2 enter the original-binary relay plan. The listener is private-LAN reachable during the "
            "run, foreign peers are rejected after accept, and the HMAC layer is a minimal smoke envelope, not a full "
            "session-security proof. It does not prove active P3/P4 original-binary gameplay, multi-host LAN, public "
            "matchmaking, native BEA netcode, deterministic sync, or rebuild parity."
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
    for index, slot in enumerate(EXPECTED_ARRIVAL_ORDER, start=1):
        events.append(make_event("client_barrier_ready", clientSlot=slot, processId=100 + index))
    events.append(make_event("barrier_released", clientReadyBeforeBarrierReleaseCount=4))
    events.append(make_event("server_active_connection_count", activeConnectionCount=4))
    observed = [
        ("P4", "session_hello", None, "session_accepted", None, None),
        ("P4", "command", EXPECTED_P4_COMMAND_ID, "command_rejected", "required-for-unproven-original-binary-slots", EXPECTED_P4_COMMAND_ID),
        ("P2", "session_hello", None, "session_accepted", None, None),
        ("P2", "command", EXPECTED_P2_COMMAND_ID, "command_accepted", None, EXPECTED_P2_COMMAND_ID),
        ("P3", "session_hello", None, "session_accepted", None, None),
        ("P3", "command", EXPECTED_P3_COMMAND_ID, "command_rejected", "required-for-unproven-original-binary-slots", EXPECTED_P3_COMMAND_ID),
        ("P1", "session_hello", None, "session_accepted", None, None),
        ("P1", "command", EXPECTED_P1_COMMAND_ID, "command_accepted", None, EXPECTED_P1_COMMAND_ID),
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
    for slot in EXPECTED_ARRIVAL_ORDER:
        events.append(make_event("client_close", {"type": "close", "clientSlot": slot}, clientSlot=slot))
    events.append(make_event("close_barrier_released", activeConnectionCount=4))
    for index, slot in enumerate(EXPECTED_ARRIVAL_ORDER, start=1):
        events.append(make_event("client_process_exited", processId=100 + index, clientSlot=slot, exitCode=0))
    events.append(make_event("server_stopped"))
    return events


def make_bundle_fixture(
    root: Path,
    *,
    include_p3_in_relay: bool = False,
    scheduler_input_claim: bool = False,
    same_process_claim: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    relay_plan = [
        {"scheduledTick": 1, "clientSlot": "P1", "commandId": EXPECTED_P1_COMMAND_ID, "mappedInputSequence": EXPECTED_P1_SEQUENCE, "route": "P1/inputDevice0/top-split-half", "hostHelperInputSent": False},
        {"scheduledTick": 1, "clientSlot": "P2", "commandId": EXPECTED_P2_COMMAND_ID, "mappedInputSequence": EXPECTED_P2_SEQUENCE, "route": "P2/inputDevice1/bottom-split-half", "hostHelperInputSent": False},
    ]
    if include_p3_in_relay:
        relay_plan.append({"scheduledTick": 1, "clientSlot": "P3", "commandId": EXPECTED_P3_COMMAND_ID, "mappedInputSequence": EXPECTED_P3_SEQUENCE, "route": "P3/unproven", "hostHelperInputSent": False})
    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "sessionDescriptor": {
            "schemaVersion": EXPECTED_SESSION_SCHEMA,
            "protocolVersion": EXPECTED_PROTOCOL,
            "hostAuthorityModel": "single-host-authoritative-copied-session",
            "slotCapacity": 4,
            "acceptedSessionParticipantCount": 4,
            "originalBinaryActiveSlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "participants": [
                {"slotId": "P1", "clientId": "client-p1", "sessionAdmission": "accepted-active-original-binary-slot", "runtimeRoute": "P1/inputDevice0/top-split-half", "commandPermission": "original-binary-command-allowed-when-authenticated", "identityRequired": True},
                {"slotId": "P2", "clientId": "client-p2", "sessionAdmission": "accepted-active-original-binary-slot", "runtimeRoute": "P2/inputDevice1/bottom-split-half", "commandPermission": "original-binary-command-allowed-when-authenticated", "identityRequired": True},
                {"slotId": "P3", "clientId": "client-p3", "sessionAdmission": "accepted-metadata-only-no-original-binary-gameplay-route", "runtimeRoute": "unsupported-original-binary-active-slot", "commandPermission": "reject-gameplay-input-until-new-proof-class", "identityRequired": True},
                {"slotId": "P4", "clientId": "client-p4", "sessionAdmission": "accepted-metadata-only-no-original-binary-gameplay-route", "runtimeRoute": "unsupported-original-binary-active-slot", "commandPermission": "reject-gameplay-input-until-new-proof-class", "identityRequired": True},
            ],
        },
        "transport": {
            "transport": EXPECTED_TRANSPORT,
            "bindHost": PRIVATE_NON_LOOPBACK_FIXTURE_HOST,
            "actualBindPort": 49155,
            "networkScope": "private-interface-n-slot-concurrent-process-smoke",
            "privateLanInterfaceBound": True,
            "privateLanReachableDuringRun": True,
            "foreignPeersRejectedAfterAccept": True,
            "loopbackInterfaceOnly": False,
            "sameWorkstationClientProcessesOnly": True,
            "sameWorkstationNetworkOnly": False,
            "processSeparatedClients": not same_process_claim,
            "processConcurrencyModel": EXPECTED_CONCURRENCY_MODEL,
            "simultaneousClientProcessesProven": 4,
            "clientReadyBeforeBarrierReleaseCount": 4,
            "barrierReleaseAfterAllClientsReady": True,
            "maxSimultaneousSocketConnectionsProven": 4,
            "clientProcessCount": 4,
            "publicNetworkSocketsOpened": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "natTraversalClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "gameInputSentByNSlotScheduler": scheduler_input_claim,
            "hostHelperInputSent": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
        },
        "authorization": {
            "scheme": "HMAC-SHA256",
            "credentialStorage": "ephemeral-not-serialized",
            "serializedCredentialPresent": False,
            "slotCredentialFingerprints": {"P1": "1" * 64, "P2": "2" * 64, "P3": "3" * 64, "P4": "4" * 64},
            "serverIdentityMode": "pinned-fingerprint",
            "serverIdentityFingerprint": "5" * 64,
            "clientIdentityMode": "pinned-slot-fingerprint",
            "clientIdentityFingerprints": {"P1": "6" * 64, "P2": "7" * 64, "P3": "8" * 64, "P4": "9" * 64},
            "nonceWindowSeconds": 30,
            "replayCacheEnabled": True,
            "replayCacheScope": "slot-nonce-smoke",
            "sequenceEnforced": True,
            "rateLimit": {"maxAcceptedCommandsPerSlot": 1, "maxAcceptedCommandsPerTick": 2},
            "clockMode": "deterministic-smoke-clock",
            "securityProofScope": "minimal-smoke-hmac-envelope-not-full-session-security-proof",
            "sessionScopedMacCoverageProof": False,
            "maxJsonLineBytesEnforced": False,
            "unknownFieldRejectionProof": False,
            "strictMessageSchemaProof": False,
            "tickBoundMacFieldsProof": False,
        },
        "clientProcessBoundary": {
            "processModel": "four-separate-python-client-processes",
            "processConcurrencyModel": EXPECTED_CONCURRENCY_MODEL,
            "simultaneousClientProcessesProven": 4,
            "allClientProcessesReadyBeforeBarrierRelease": True,
            "allClientProcessesAliveAtBarrierRelease": True,
            "allClientSocketsHeldUntilCloseRelease": True,
            "builderProcessId": 100,
            "clientProcessCount": 4,
            "clientProcesses": [
                {"clientSlot": "P4", "clientProcessId": 101, "clientProcessIdFromParent": 101, "clientVerifiedServerIdentity": True, "clientExitCode": 0},
                {"clientSlot": "P2", "clientProcessId": 102, "clientProcessIdFromParent": 102, "clientVerifiedServerIdentity": True, "clientExitCode": 0},
                {"clientSlot": "P3", "clientProcessId": 103, "clientProcessIdFromParent": 103, "clientVerifiedServerIdentity": True, "clientExitCode": 0},
                {"clientSlot": "P1", "clientProcessId": 104 if not same_process_claim else 101, "clientProcessIdFromParent": 104 if not same_process_claim else 101, "clientVerifiedServerIdentity": True, "clientExitCode": 0},
            ],
            "clientProcessIdsDistinctFromBuilder": True,
            "clientProcessIdsDistinctFromEachOther": not same_process_claim,
            "credentialTransportToClientProcesses": "stdin-ephemeral-not-serialized-to-artifact",
            "clientEnvSensitiveKeyCount": 0,
            "clientCommandLineContainsCredential": False,
            "clientEnvironmentContainsCredential": False,
            "clientStdoutContainsCredential": False,
            "clientStderrContainsCredential": False,
            "sameWorkstationClientProcessesOnly": True,
            "sameWorkstationNetworkOnly": False,
            "multiHostLanClaim": False,
            "clientResponses": {
                "P1": [{"label": "session", "type": "session_accepted", "reason": None, "commandId": None}, {"label": "accepted", "type": "command_accepted", "reason": None, "commandId": EXPECTED_P1_COMMAND_ID}],
                "P2": [{"label": "session", "type": "session_accepted", "reason": None, "commandId": None}, {"label": "accepted", "type": "command_accepted", "reason": None, "commandId": EXPECTED_P2_COMMAND_ID}],
                "P3": [{"label": "session", "type": "session_accepted", "reason": None, "commandId": None}, {"label": "rejected-gameplay-route", "type": "command_rejected", "reason": "required-for-unproven-original-binary-slots", "commandId": EXPECTED_P3_COMMAND_ID}],
                "P4": [{"label": "session", "type": "session_accepted", "reason": None, "commandId": None}, {"label": "rejected-gameplay-route", "type": "command_rejected", "reason": "required-for-unproven-original-binary-slots", "commandId": EXPECTED_P4_COMMAND_ID}],
            },
        },
        "concurrencyProof": {
            "processConcurrencyModel": EXPECTED_CONCURRENCY_MODEL,
            "clientReadyBeforeBarrierReleaseCount": 4,
            "barrierReleaseAfterAllClientsReady": True,
            "maxSimultaneousClientProcessesProven": 4,
            "maxSimultaneousSocketConnectionsProven": 4,
            "allClientProcessesAliveAtBarrierRelease": True,
            "allClientSocketsHeldUntilCloseRelease": True,
            "clientProcessTiming": [
                {
                    "clientSlot": slot,
                    "processStartedBeforeBarrierRelease": True,
                    "readyBeforeBarrierRelease": True,
                    "processExitedAfterBarrierRelease": True,
                    "socketOpenedBeforeCloseRelease": True,
                    "socketClosedAfterCloseRelease": True,
                }
                for slot in EXPECTED_ARRIVAL_ORDER
            ],
        },
        "commands": {
            "acceptedOriginalBinaryGameplay": [
                {"commandId": EXPECTED_P2_COMMAND_ID, "clientSlot": "P2", "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P2_SEQUENCE, "scheduledTick": 1, "arrivalOrder": 2, "hostAccepted": True, "gameInputSentByNSlotScheduler": scheduler_input_claim, "hostHelperInputSent": False},
                {"commandId": EXPECTED_P1_COMMAND_ID, "clientSlot": "P1", "command": EXPECTED_COMMAND, "mappedInputSequence": EXPECTED_P1_SEQUENCE, "scheduledTick": 1, "arrivalOrder": 4, "hostAccepted": True, "gameInputSentByNSlotScheduler": scheduler_input_claim, "hostHelperInputSent": False},
            ],
            "rejectedOriginalBinaryGameplay": [
                {"commandId": EXPECTED_P4_COMMAND_ID, "clientSlot": "P4", "reason": "required-for-unproven-original-binary-slots", "hostAccepted": False, "gameInputSentByNSlotScheduler": False, "hostHelperInputSent": False},
                {"commandId": EXPECTED_P3_COMMAND_ID, "clientSlot": "P3", "reason": "required-for-unproven-original-binary-slots", "hostAccepted": False, "gameInputSentByNSlotScheduler": False, "hostHelperInputSent": False},
            ],
        },
        "hostAuthorityNSlotScheduler": {
            "schedulerSchema": "host-authority-n-slot-scheduler.v1",
            "declaredSlotCount": 4,
            "slotCapacity": 4,
            "acceptedSessionParticipantCount": 4,
            "originalBinaryRelaySlotCount": 2,
            "acceptedOriginalBinaryGameplayCommandCount": 2,
            "rejectedOriginalBinaryGameplayCommandCount": 2,
            "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
            "extraSlotRejectionPolicy": "required-for-unproven-original-binary-slots",
            "arrivalOrder": EXPECTED_ARRIVAL_ORDER,
            "deterministicParticipantOrder": EXPECTED_SLOTS,
            "deterministicOriginalBinaryRelayOrder": EXPECTED_ACTIVE_SLOTS,
            "relayPlan": relay_plan,
            "relayPlanSha256": sha256_payload(relay_plan),
            "runtimeCompatibleP1P2RelayHash": EXPECTED_RUNTIME_P1P2_RELAY_HASH,
            "gameInputSentByNSlotScheduler": scheduler_input_claim,
            "hostHelperInputSent": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": False,
            "nativeBeaNetcodeClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "moreThanTwoRuntimePlayerClaim": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
        },
        "transportTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": "5" * 64,
            "messageCount": 20,
            "events": make_transcript_fixture_events(),
        },
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "permanentImpossibilityClaim": False,
        "nonClaims": {
            "fourPlayerGameplayProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "physicalGamepadProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
    }
    output = root / "host-authority-n-slot-process-smoke-proof.json"
    write_json(output, bundle)
    return output


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        validate_bundle(make_bundle_fixture(Path(tmp)))
    for label, mutator in (
        ("top-level N-player overclaim should fail", lambda bundle: bundle.__setitem__("nPlayerOriginalBinaryRuntimeProof", 1)),
        ("active P3/P4 overclaim should fail", lambda bundle: bundle.__setitem__("activeP3P4OriginalBinaryGameplayProof", True)),
        ("permanent impossibility overclaim should fail", lambda bundle: bundle.__setitem__("permanentImpossibilityClaim", True)),
        ("parent/child PID mismatch should fail", lambda bundle: bundle["clientProcessBoundary"]["clientProcesses"][0].__setitem__("clientProcessIdFromParent", 999999)),
        ("serialized credential field should fail", lambda bundle: bundle["authorization"].__setitem__("credentialHex", "00" * 32)),
        ("same-workstation-only network overclaim should fail", lambda bundle: bundle["transport"].__setitem__("sameWorkstationNetworkOnly", True)),
        ("full session-security overclaim should fail", lambda bundle: bundle["authorization"].__setitem__("sessionScopedMacCoverageProof", True)),
        ("missing private-LAN reachability should fail", lambda bundle: bundle["transport"].__setitem__("privateLanReachableDuringRun", False)),
        ("downgraded simultaneous process proof should fail", lambda bundle: bundle["clientProcessBoundary"].__setitem__("simultaneousClientProcessesProven", 1)),
        ("missing socket concurrency proof should fail", lambda bundle: bundle["concurrencyProof"].__setitem__("maxSimultaneousSocketConnectionsProven", 3)),
        ("early barrier release should fail", lambda bundle: bundle["concurrencyProof"].__setitem__("barrierReleaseAfterAllClientsReady", False)),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_bundle_fixture(Path(tmp))
            bundle = read_json(path)
            mutator(bundle)
            write_json(path, bundle)
            try:
                validate_bundle(path)
            except HostAuthorityNSlotProcessSmokeProofError:
                continue
            raise AssertionError(label)
    for label, kwargs in (
        ("P3 relay overclaim should fail", {"include_p3_in_relay": True}),
        ("scheduler direct-input claim should fail", {"scheduler_input_claim": True}),
        ("same-process client claim should fail", {"same_process_claim": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs))
            except HostAuthorityNSlotProcessSmokeProofError:
                continue
            raise AssertionError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority N-slot process smoke checker self-test: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HostAuthorityNSlotProcessSmokeProofError as exc:
        print(f"WinUI original-binary host-authority N-slot process smoke check: FAIL: {exc}")
        raise SystemExit(2)
