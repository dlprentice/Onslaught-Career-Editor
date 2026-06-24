#!/usr/bin/env python3
"""Build a same-host sequential four-client N-slot host-authority process smoke proof."""

from __future__ import annotations

import argparse
import hmac
import ipaddress
import json
import os
import queue
import secrets
import socket
import subprocess
import sys
import threading
from hashlib import sha256
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_n_slot_process_smoke_check as check


SCHEMA = check.EXPECTED_SCHEMA
SESSION_SCHEMA = check.EXPECTED_SESSION_SCHEMA
TRANSPORT = check.EXPECTED_TRANSPORT
PROTOCOL = check.EXPECTED_PROTOCOL
HELPER = check.EXPECTED_HELPER
HELPER_VERSION = check.EXPECTED_HELPER_VERSION
EXPECTED_COMMAND = check.EXPECTED_COMMAND
SLOTS = check.EXPECTED_SLOTS
ACTIVE_SLOTS = check.EXPECTED_ACTIVE_SLOTS
METADATA_SLOTS = check.EXPECTED_METADATA_SLOTS
ARRIVAL_ORDER = check.EXPECTED_ARRIVAL_ORDER
COMMAND_IDS = {
    "P1": check.EXPECTED_P1_COMMAND_ID,
    "P2": check.EXPECTED_P2_COMMAND_ID,
    "P3": check.EXPECTED_P3_COMMAND_ID,
    "P4": check.EXPECTED_P4_COMMAND_ID,
}
SEQUENCES = {
    "P1": check.EXPECTED_P1_SEQUENCE,
    "P2": check.EXPECTED_P2_SEQUENCE,
    "P3": check.EXPECTED_P3_SEQUENCE,
    "P4": check.EXPECTED_P4_SEQUENCE,
}


class HostAuthorityNSlotProcessSmokeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityNSlotProcessSmokeBuildError(message)


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "mac"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: dict[str, Any], credential: bytes) -> dict[str, Any]:
    signed = dict(payload)
    signed["mac"] = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return signed


def write_json_line(handle: Any, payload: dict[str, Any]) -> None:
    handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
    handle.flush()


def read_json_line(handle: Any) -> dict[str, Any]:
    line = handle.readline()
    require(bool(line), "host-authority socket closed before response")
    value = json.loads(line.decode("utf-8"))
    require(isinstance(value, dict), "host-authority response was not a JSON object")
    return value


def require_private_bind_host(bind_host: str) -> None:
    try:
        address = ipaddress.ip_address(bind_host)
    except ValueError as exc:
        raise HostAuthorityNSlotProcessSmokeBuildError(f"Bind host must be an IP address: {bind_host}") from exc
    require(address.is_private, "Bind host must be private")
    require(not address.is_loopback, "Bind host must be non-loopback")
    require(not address.is_link_local, "Bind host must not be link-local")
    require(not address.is_multicast and not address.is_unspecified, "Bind host must be a concrete private interface address")


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = check.sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def participant(slot: str) -> dict[str, Any]:
    active = slot in ACTIVE_SLOTS
    return {
        "slotId": slot,
        "clientId": f"client-{slot.lower()}",
        "sessionAdmission": "accepted-active-original-binary-slot" if active else "accepted-metadata-only-no-original-binary-gameplay-route",
        "runtimeRoute": (
            "P1/inputDevice0/top-split-half"
            if slot == "P1"
            else "P2/inputDevice1/bottom-split-half"
            if slot == "P2"
            else "unsupported-original-binary-active-slot"
        ),
        "commandPermission": "original-binary-command-allowed-when-authenticated" if active else "reject-gameplay-input-until-new-proof-class",
        "identityRequired": True,
    }


def make_session_descriptor() -> dict[str, Any]:
    return {
        "schemaVersion": SESSION_SCHEMA,
        "protocolVersion": PROTOCOL,
        "hostAuthorityModel": "single-host-authoritative-copied-session",
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "originalBinaryActiveSlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "participants": [participant(slot) for slot in SLOTS],
    }


CLIENT_CODE = r'''
import hmac
import json
import os
import socket
import sys


def canonical_bytes(payload):
    clean = {key: value for key, value in payload.items() if key != "mac"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload, credential):
    signed = dict(payload)
    signed["mac"] = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return signed


def write_json_line(handle, payload):
    handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
    handle.flush()


def read_json_line(handle):
    line = handle.readline()
    if not line:
        raise RuntimeError("host closed before response")
    value = json.loads(line.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("host response was not an object")
    return value


config = json.loads(sys.stdin.read())
credential = bytes.fromhex(config["credentialHex"])
slot = config["slot"]
responses = []

with socket.create_connection((config["bindHost"], int(config["port"])), timeout=5) as client:
    handle = client.makefile("rwb")
    hello = {
        "type": "session_hello",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "serverIdentityFingerprint": config["serverIdentityFingerprint"],
        "clientIdentityFingerprint": config["clientIdentityFingerprint"],
        "clientSlot": slot,
        "nonce": f"{slot.lower()}-session-hello-0001",
        "timestamp": int(config["now"]),
    }
    write_json_line(handle, sign_payload(hello, credential))
    session_response = read_json_line(handle)
    responses.append({"label": "session", "type": session_response.get("type"), "reason": session_response.get("reason"), "commandId": session_response.get("commandId")})
    if session_response.get("serverIdentityFingerprint") != config["serverIdentityFingerprint"]:
        raise RuntimeError("server identity mismatch")

    command = {
        "type": "command",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "clientSlot": slot,
        "commandId": config["commandId"],
        "command": config["expectedCommand"],
        "sequence": 1,
        "nonce": f"{slot.lower()}-forward-0001",
        "timestamp": int(config["now"]),
        "mappedInputSequence": config["mappedInputSequence"],
        "directGameInputClaim": False,
        "publicMatchmakingClaim": False,
    }
    write_json_line(handle, sign_payload(command, credential))
    response = read_json_line(handle)
    responses.append({
        "label": "accepted" if response.get("type") == "command_accepted" else "rejected-gameplay-route",
        "type": response.get("type"),
        "reason": response.get("reason"),
        "commandId": response.get("commandId"),
        "scheduledTick": response.get("scheduledTick"),
    })
    write_json_line(handle, {"type": "close", "clientSlot": slot})

print(json.dumps({
    "clientProcessId": os.getpid(),
    "slot": slot,
    "clientVerifiedServerIdentity": True,
    "responses": responses,
}, sort_keys=True))
'''


def run_client(config: dict[str, Any], credential: bytes) -> dict[str, Any]:
    full_config = dict(config)
    full_config["credentialHex"] = credential.hex()
    child_env = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in {"COMSPEC", "PATH", "PATHEXT", "SYSTEMROOT", "TEMP", "TMP", "WINDIR"}
    }
    child_env["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.Popen(
        [sys.executable, "-c", CLIENT_CODE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=child_env,
    )
    try:
        stdout, stderr = process.communicate(json.dumps(full_config), timeout=15)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
        raise HostAuthorityNSlotProcessSmokeBuildError(f"{config['slot']} client process timed out: {stderr.strip()}") from exc
    require(process.returncode == 0, f"{config['slot']} client process failed: {stderr.strip()}")
    require(credential.hex() not in stdout and credential.hex() not in stderr, f"{config['slot']} credential leaked through client output")
    output = json.loads(stdout.strip())
    require(isinstance(output, dict), f"{config['slot']} client output must be an object")
    require(output.get("clientProcessId") == process.pid, f"{config['slot']} child PID did not match parent-observed PID")
    output["clientExitCode"] = process.returncode
    output["clientProcessIdFromParent"] = process.pid
    return output


def run_host_authority_session(
    descriptor: dict[str, Any],
    *,
    credentials: dict[str, bytes],
    authorization: dict[str, Any],
    bind_host: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    ready: queue.Queue[int] = queue.Queue()
    server_errors: queue.Queue[str] = queue.Queue()
    seen_nonces: set[str] = set()
    expected_sequence = {slot: 1 for slot in SLOTS}
    accepted_commands: list[dict[str, Any]] = []
    rejected_commands: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    now = 2_100_000_000
    stop_event = threading.Event()

    def reject(payload: dict[str, Any], reason: str) -> dict[str, Any]:
        row = {
            "commandId": payload.get("commandId"),
            "clientSlot": payload.get("clientSlot"),
            "reason": reason,
            "hostAccepted": False,
            "gameInputSentByNSlotScheduler": False,
            "hostHelperInputSent": False,
        }
        if payload.get("clientSlot") in METADATA_SLOTS and reason == "required-for-unproven-original-binary-slots":
            rejected_commands.append(row)
        return {"type": "command_rejected", **row}

    def verify_mac(payload: dict[str, Any], credential: bytes) -> bool:
        mac = payload.get("mac")
        if not isinstance(mac, str):
            return False
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(mac, expected)

    def handle_payload(payload: dict[str, Any]) -> dict[str, Any]:
        slot = payload.get("clientSlot")
        if slot not in credentials:
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "client-slot-not-allowed", "clientSlot": slot}
        if not verify_mac(payload, credentials[str(slot)]):
            reason = "missing-authentication" if "mac" not in payload else "bad-hmac"
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": reason, "clientSlot": slot}
        timestamp = payload.get("timestamp")
        if not isinstance(timestamp, int) or abs(timestamp - now) > int(authorization["nonceWindowSeconds"]):
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "expired-timestamp", "clientSlot": slot}
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or not nonce:
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "missing-nonce", "clientSlot": slot}
        if nonce in seen_nonces:
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "replay-nonce", "clientSlot": slot}
        seen_nonces.add(nonce)
        if payload.get("protocolVersion") != PROTOCOL:
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "protocol-mismatch", "clientSlot": slot}
        if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
            return {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "session-compatibility-mismatch", "clientSlot": slot}

        if payload.get("type") == "session_hello":
            if payload.get("serverIdentityFingerprint") != authorization["serverIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "server-identity-mismatch", "clientSlot": slot}
            if payload.get("clientIdentityFingerprint") != authorization["clientIdentityFingerprints"][str(slot)]:
                return {"type": "session_rejected", "reason": "client-identity-mismatch", "clientSlot": slot}
            return {
                "type": "session_accepted",
                "clientSlot": slot,
                "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
            }

        if payload.get("type") != "command":
            return reject(payload, "unknown-message-type")
        if payload.get("sequence") != expected_sequence[str(slot)]:
            return reject(payload, "sequence-not-next")
        if payload.get("command") != EXPECTED_COMMAND:
            return reject(payload, "command-not-allowed")
        if payload.get("commandId") != COMMAND_IDS[str(slot)]:
            return reject(payload, "command-id-not-allowed")
        if payload.get("mappedInputSequence") != SEQUENCES[str(slot)]:
            return reject(payload, "mapped-input-sequence-mismatch")
        if payload.get("directGameInputClaim") is True:
            return reject(payload, "direct-input-not-allowed")
        if payload.get("publicMatchmakingClaim") is True:
            return reject(payload, "public-matchmaking-not-allowed")
        if slot in METADATA_SLOTS:
            return reject(payload, "required-for-unproven-original-binary-slots")

        tick = 1
        expected_sequence[str(slot)] += 1
        row = {
            "commandId": payload.get("commandId"),
            "clientSlot": slot,
            "command": EXPECTED_COMMAND,
            "mappedInputSequence": payload.get("mappedInputSequence"),
            "scheduledTick": tick,
            "arrivalOrder": len([r for r in accepted_commands + rejected_commands if r.get("clientSlot") in SLOTS]) + 1,
            "hostAccepted": True,
            "gameInputSentByNSlotScheduler": False,
            "hostHelperInputSent": False,
        }
        accepted_commands.append(row)
        return {"type": "command_accepted", **row}

    def server_main(listener: socket.socket) -> None:
        try:
            listener.listen(4)
            listener.settimeout(1.0)
            ready.put(listener.getsockname()[1])
            accepted_connections = 0
            while accepted_connections < 4 and not stop_event.is_set():
                try:
                    conn, _addr = listener.accept()
                except socket.timeout:
                    continue
                accepted_connections += 1
                with conn:
                    conn.settimeout(5.0)
                    handle = conn.makefile("rwb")
                    while not stop_event.is_set():
                        try:
                            line = handle.readline()
                        except socket.timeout as exc:
                            raise HostAuthorityNSlotProcessSmokeBuildError("client socket timed out waiting for JSONL input") from exc
                        if not line:
                            break
                        payload = json.loads(line.decode("utf-8"))
                        if payload.get("type") == "close":
                            events.append(make_event("client_close", payload, clientSlot=payload.get("clientSlot")))
                            break
                        events.append(
                            make_event(
                                "client_message",
                                payload,
                                clientSlot=payload.get("clientSlot"),
                                messageType=payload.get("type"),
                                commandId=payload.get("commandId"),
                            )
                        )
                        response = handle_payload(payload)
                        events.append(
                            make_event(
                                "server_response",
                                response,
                                clientSlot=response.get("clientSlot"),
                                responseType=response.get("type"),
                                reason=response.get("reason"),
                                commandId=response.get("commandId"),
                                scheduledTick=response.get("scheduledTick"),
                            )
                        )
                        write_json_line(handle, response)
        except Exception as exc:  # pragma: no cover - surfaced in generated proof failures
            server_errors.put(str(exc))
        finally:
            listener.close()

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((bind_host, 0))
    thread = threading.Thread(target=server_main, args=(listener,), daemon=True)
    thread.start()
    outputs: dict[str, dict[str, Any]] = {}
    client_error: BaseException | None = None
    try:
        port = ready.get(timeout=5)
        events.append(make_event("server_bound", bindHost=bind_host, actualBindPort=port))

        common = {
            "bindHost": bind_host,
            "port": port,
            "protocolVersion": PROTOCOL,
            "compatibilityKey": descriptor["sessionCompatibilityKey"],
            "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
            "expectedCommand": EXPECTED_COMMAND,
            "now": now,
        }
        for slot in ARRIVAL_ORDER:
            config = {
                **common,
                "slot": slot,
                "clientIdentityFingerprint": authorization["clientIdentityFingerprints"][slot],
                "commandId": COMMAND_IDS[slot],
                "mappedInputSequence": SEQUENCES[slot],
            }
            outputs[slot] = run_client(config, credentials[slot])
    except BaseException as exc:
        client_error = exc
    finally:
        stop_event.set()
        try:
            listener.close()
        except OSError:
            pass
        thread.join(timeout=5)
    require(not thread.is_alive(), "host-authority N-slot server thread did not stop")
    if not server_errors.empty():
        raise HostAuthorityNSlotProcessSmokeBuildError(server_errors.get())
    if client_error is not None:
        raise client_error
    for slot in ARRIVAL_ORDER:
        output = outputs[slot]
        events.append(make_event("client_process_exited", processId=output["clientProcessId"], clientSlot=slot, exitCode=output["clientExitCode"]))
    events.append(make_event("server_stopped"))

    schedule = sorted(accepted_commands, key=lambda row: (int(row["scheduledTick"]), str(row["clientSlot"])))
    relay_plan = [
        {
            "scheduledTick": row["scheduledTick"],
            "clientSlot": row["clientSlot"],
            "commandId": row["commandId"],
            "mappedInputSequence": row["mappedInputSequence"],
            "route": "P1/inputDevice0/top-split-half" if row["clientSlot"] == "P1" else "P2/inputDevice1/bottom-split-half",
            "hostHelperInputSent": False,
        }
        for row in schedule
    ]
    scheduler = {
        "schedulerSchema": "host-authority-n-slot-scheduler.v1",
        "declaredSlotCount": 4,
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "originalBinaryRelaySlotCount": 2,
        "acceptedOriginalBinaryGameplayCommandCount": len(accepted_commands),
        "rejectedOriginalBinaryGameplayCommandCount": len(rejected_commands),
        "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "rejectedGameplayRouteSlots": METADATA_SLOTS,
        "extraSlotRejectionPolicy": "required-for-unproven-original-binary-slots",
        "arrivalOrder": ARRIVAL_ORDER,
        "deterministicParticipantOrder": SLOTS,
        "deterministicOriginalBinaryRelayOrder": [row["clientSlot"] for row in schedule],
        "relayPlan": relay_plan,
        "relayPlanSha256": check.sha256_payload(relay_plan),
        "runtimeCompatibleP1P2RelayHash": check.EXPECTED_RUNTIME_P1P2_RELAY_HASH,
        "gameInputSentByNSlotScheduler": False,
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
    }
    transport = {
        "transport": TRANSPORT,
        "bindHost": bind_host,
        "actualBindPort": port,
        "networkScope": "private-interface-n-slot-process-smoke",
        "privateLanInterfaceBound": True,
        "loopbackInterfaceOnly": False,
        "sameWorkstationOnly": True,
        "processSeparatedClients": True,
        "processConcurrencyModel": "sequential-distinct-client-processes",
        "simultaneousClientProcessesProven": 1,
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
        "gameInputSentByNSlotScheduler": False,
        "hostHelperInputSent": False,
        "newBeaLaunchCount": 0,
        "cdbAttachCount": 0,
    }
    process_boundary = {
        "processModel": "four-separate-python-client-processes",
        "processConcurrencyModel": "sequential-distinct-client-processes",
        "simultaneousClientProcessesProven": 1,
        "builderProcessId": os.getpid(),
        "clientProcessCount": 4,
        "clientProcesses": [
            {
                "clientSlot": slot,
                "clientProcessId": outputs[slot]["clientProcessId"],
                "clientProcessIdFromParent": outputs[slot]["clientProcessIdFromParent"],
                "clientVerifiedServerIdentity": outputs[slot]["clientVerifiedServerIdentity"],
                "clientExitCode": outputs[slot]["clientExitCode"],
            }
            for slot in ARRIVAL_ORDER
        ],
        "clientProcessIdsDistinctFromBuilder": all(outputs[slot]["clientProcessId"] != os.getpid() for slot in SLOTS),
        "clientProcessIdsDistinctFromEachOther": len({outputs[slot]["clientProcessId"] for slot in SLOTS}) == 4,
        "credentialTransportToClientProcesses": "stdin-ephemeral-not-serialized-to-artifact",
        "clientEnvSensitiveKeyCount": 0,
        "clientCommandLineContainsCredential": False,
        "clientEnvironmentContainsCredential": False,
        "clientStdoutContainsCredential": False,
        "clientStderrContainsCredential": False,
        "sameWorkstationOnly": True,
        "multiHostLanClaim": False,
        "clientResponses": {slot: outputs[slot]["responses"] for slot in SLOTS},
    }
    transcript = {
        "transport": TRANSPORT,
        "protocolVersion": PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "messageCount": 20,
        "events": events,
    }
    commands = {
        "acceptedOriginalBinaryGameplay": accepted_commands,
        "rejectedOriginalBinaryGameplay": rejected_commands,
    }
    return transport, commands, scheduler, process_boundary, transcript


def build_bundle(output_path: Path, *, bind_host: str) -> dict[str, Any]:
    require_private_bind_host(bind_host)
    descriptor = make_session_descriptor()
    compatibility_key = sha256(f"{PROTOCOL}:n-slot-process-smoke:v1".encode("utf-8")).hexdigest()
    descriptor["sessionCompatibilityKey"] = compatibility_key
    credentials = {slot: secrets.token_bytes(32) for slot in SLOTS}
    authorization = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "slotCredentialFingerprints": {slot: sha256(value).hexdigest() for slot, value in credentials.items()},
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256(f"{PROTOCOL}:server:n-slot-process-smoke".encode("utf-8")).hexdigest(),
        "clientIdentityMode": "pinned-slot-fingerprint",
        "clientIdentityFingerprints": {
            slot: sha256(f"{PROTOCOL}:client:{slot}".encode("utf-8")).hexdigest()
            for slot in SLOTS
        },
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSlot": 1,
            "maxAcceptedCommandsPerTick": 2,
        },
        "clockMode": "deterministic-smoke-clock",
    }
    transport, commands, scheduler, process_boundary, transcript = run_host_authority_session(
        descriptor,
        credentials=credentials,
        authorization=authorization,
        bind_host=bind_host,
    )
    bundle = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "sessionDescriptor": descriptor,
        "transport": transport,
        "authorization": authorization,
        "clientProcessBoundary": process_boundary,
        "commands": commands,
        "hostAuthorityNSlotScheduler": scheduler,
        "transportTranscript": transcript,
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
        "claimBoundary": (
            "Same-workstation sequential four-client N-slot scheduler/process smoke only. This proves four separate "
            "local client processes can authenticate with slot-scoped ephemeral HMAC credentials and participate "
            "sequentially in the host-authority process layer while only P1/P2 are scheduled into the original-binary "
            "relay plan. It does not prove four concurrent client processes, does not launch BEA, does not attach CDB, "
            "does not send host-helper input, does not prove active P3/P4 original-binary gameplay, and does not prove "
            "multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, "
            "physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    summary = check.validate_bundle(output_path)
    return {
        "bundle": str(output_path.resolve()),
        "bundleSha256": sha256_file(output_path),
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bind-host", required=True)
    args = parser.parse_args()

    print(json.dumps(build_bundle(args.output.resolve(), bind_host=args.bind_host), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HostAuthorityNSlotProcessSmokeBuildError, check.HostAuthorityNSlotProcessSmokeProofError) as exc:
        print(f"WinUI original-binary host-authority N-slot process smoke bundle build: FAIL: {exc}")
        raise SystemExit(2)
