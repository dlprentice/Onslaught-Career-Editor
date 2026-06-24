#!/usr/bin/env python3
"""Build a same-host two-client host-authority scheduler smoke proof."""

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

import winui_safe_copy_online_private_remote_client_smoke_check as remote


SCHEMA = "winui-original-binary-host-authority-two-client-smoke.v1"
SESSION_SCHEMA = "winui-original-binary-host-authority-two-client-session.v1"
TRANSPORT = "host-authority-two-client-tcp-jsonl-smoke"
PROTOCOL = "host-authority-two-client-input.v1"
HELPER = "winui-original-binary-host-authority-two-client-smoke-helper"
HELPER_VERSION = "host-authority-two-client-smoke-helper.v1"
P1_COMMAND_ID = "host-authority-p1-forward-0001"
P2_COMMAND_ID = "host-authority-p2-forward-0001"
EXPECTED_COMMAND = remote.EXPECTED_REMOTE_COMMAND
P1_SEQUENCE = "down:Q,wait:500,up:Q"
P2_SEQUENCE = remote.EXPECTED_MAPPED_SEQUENCE


class HostAuthorityTwoClientSmokeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityTwoClientSmokeBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def require_private_bind_host(bind_host: str) -> None:
    try:
        address = ipaddress.ip_address(bind_host)
    except ValueError as exc:
        raise HostAuthorityTwoClientSmokeBuildError(f"Bind host must be an IP address: {bind_host}") from exc
    require(address.is_private, "Bind host must be private")
    require(not address.is_loopback, "Bind host must be non-loopback")
    require(not address.is_link_local, "Bind host must not be link-local")
    require(not address.is_multicast and not address.is_unspecified, "Bind host must be a concrete private interface address")


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


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def sha256_payload(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def command_for_slot(slot: str) -> str:
    if slot == "P1":
        return P1_COMMAND_ID
    if slot == "P2":
        return P2_COMMAND_ID
    raise HostAuthorityTwoClientSmokeBuildError(f"unsupported slot: {slot}")


def sequence_for_slot(slot: str) -> str:
    if slot == "P1":
        return P1_SEQUENCE
    if slot == "P2":
        return P2_SEQUENCE
    raise HostAuthorityTwoClientSmokeBuildError(f"unsupported slot: {slot}")


def make_session_descriptor(remote_bundle: dict[str, Any], remote_path: Path, remote_summary: dict[str, Any]) -> dict[str, Any]:
    upstream_descriptor = object_at(remote_bundle, "sessionDescriptor")
    return {
        "schemaVersion": SESSION_SCHEMA,
        "protocolVersion": PROTOCOL,
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
            "P1": {"commandId": P1_COMMAND_ID, "command": EXPECTED_COMMAND, "mappedInputSequence": P1_SEQUENCE},
            "P2": {"commandId": P2_COMMAND_ID, "command": EXPECTED_COMMAND, "mappedInputSequence": P2_SEQUENCE},
        },
        "upstreamPrivateRemoteClientCommandId": remote.EXPECTED_COMMAND_ID,
        "upstreamPrivateLanCommandId": remote_summary["wouldForwardToPrivateLanCommandId"],
    }


def make_command(
    *,
    slot: str,
    command_id: str,
    compatibility_key: str,
    sequence: int = 1,
    nonce: str,
    timestamp: int,
    direct_input_claim: bool = False,
    public_matchmaking_claim: bool = False,
) -> dict[str, Any]:
    return {
        "type": "command",
        "protocolVersion": PROTOCOL,
        "compatibilityKey": compatibility_key,
        "clientSlot": slot,
        "commandId": command_id,
        "command": EXPECTED_COMMAND,
        "sequence": sequence,
        "nonce": nonce,
        "timestamp": timestamp,
        "mappedInputSequence": sequence_for_slot(slot),
        "directGameInputClaim": direct_input_claim,
        "publicMatchmakingClaim": public_matchmaking_claim,
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
responses = []

with socket.create_connection((config["bindHost"], int(config["port"])), timeout=5) as client:
    handle = client.makefile("rwb")
    hello = {
        "type": "session_hello",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "serverIdentityFingerprint": config["serverIdentityFingerprint"],
        "clientIdentityFingerprint": config["clientIdentityFingerprint"],
        "clientSlot": config["slot"],
        "nonce": f"{config['slot'].lower()}-session-hello-0001",
        "timestamp": int(config["now"]),
    }
    write_json_line(handle, sign_payload(hello, credential))
    session_response = read_json_line(handle)
    responses.append({"label": "session", "type": session_response.get("type"), "slot": config["slot"]})
    if session_response.get("serverIdentityFingerprint") != config["serverIdentityFingerprint"]:
        raise RuntimeError("server identity mismatch")

    for row in config["commands"]:
        payload = {
            "type": "command",
            "protocolVersion": config["protocolVersion"],
            "compatibilityKey": config["compatibilityKey"],
            "clientSlot": row["slot"],
            "commandId": row["commandId"],
            "command": config["expectedCommand"],
            "sequence": row["sequence"],
            "nonce": row["nonce"],
            "timestamp": int(config["now"]),
            "mappedInputSequence": row["mappedInputSequence"],
            "directGameInputClaim": bool(row.get("directGameInputClaim", False)),
            "publicMatchmakingClaim": bool(row.get("publicMatchmakingClaim", False)),
        }
        if row.get("omitMac"):
            write_json_line(handle, payload)
        else:
            write_json_line(handle, sign_payload(payload, credential))
        response = read_json_line(handle)
        responses.append({
            "label": row["label"],
            "type": response.get("type"),
            "reason": response.get("reason"),
            "commandId": response.get("commandId"),
            "scheduledTick": response.get("scheduledTick"),
            "clientSlot": response.get("clientSlot"),
        })

    write_json_line(handle, {"type": "close"})

print(json.dumps({
    "clientProcessId": os.getpid(),
    "slot": config["slot"],
    "clientVerifiedServerIdentity": True,
    "responses": responses,
}, sort_keys=True))
'''


def run_client(config: dict[str, Any], credential: bytes) -> dict[str, Any]:
    full_config = dict(config)
    full_config["credentialHex"] = credential.hex()
    process = subprocess.Popen(
        [sys.executable, "-c", CLIENT_CODE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(json.dumps(full_config), timeout=15)
    require(process.returncode == 0, f"{config['slot']} client process failed: {stderr.strip()}")
    require(credential.hex() not in stdout and credential.hex() not in stderr, f"{config['slot']} credential leaked through client output")
    output = json.loads(stdout.strip())
    require(isinstance(output, dict), f"{config['slot']} client output must be an object")
    output["clientExitCode"] = process.returncode
    output["processIdFromParent"] = process.pid
    return output


def run_host_authority_session(
    descriptor: dict[str, Any],
    *,
    credentials: dict[str, bytes],
    authorization: dict[str, Any],
    bind_host: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    ready: queue.Queue[int] = queue.Queue()
    server_errors: queue.Queue[str] = queue.Queue()
    seen_nonces: set[str] = set()
    expected_sequence = {"P1": 1, "P2": 1}
    accepted_commands: list[dict[str, Any]] = []
    rejected_commands: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    now = 2_100_000_000

    def reject(payload: dict[str, Any], reason: str) -> dict[str, Any]:
        row = {
            "commandId": payload.get("commandId"),
            "clientSlot": payload.get("clientSlot"),
            "reason": reason,
            "hostAccepted": False,
            "gameInputSentByScheduler": False,
            "hostHelperInputSent": False,
        }
        rejected_commands.append(row)
        return {"type": "command_rejected", **row}

    def verify_mac(payload: dict[str, Any], credential: bytes) -> bool:
        mac = payload.get("mac")
        if not isinstance(mac, str):
            return False
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(mac, expected)

    def handle_payload(payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("type") == "session_hello":
            slot = payload.get("clientSlot")
            if slot not in credentials:
                return {"type": "session_rejected", "reason": "client-slot-not-allowed", "clientSlot": slot}
            if not verify_mac(payload, credentials[str(slot)]):
                return {"type": "session_rejected", "reason": "bad-hmac", "clientSlot": slot}
            timestamp = payload.get("timestamp")
            if not isinstance(timestamp, int) or abs(timestamp - now) > int(authorization["nonceWindowSeconds"]):
                return {"type": "session_rejected", "reason": "expired-timestamp", "clientSlot": slot}
            nonce = payload.get("nonce")
            if not isinstance(nonce, str) or not nonce:
                return {"type": "session_rejected", "reason": "missing-nonce", "clientSlot": slot}
            if nonce in seen_nonces:
                return {"type": "session_rejected", "reason": "replay-nonce", "clientSlot": slot}
            seen_nonces.add(nonce)
            if payload.get("protocolVersion") != PROTOCOL:
                return {"type": "session_rejected", "reason": "protocol-mismatch", "clientSlot": slot}
            if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
                return {"type": "session_rejected", "reason": "session-compatibility-mismatch", "clientSlot": slot}
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
        slot = payload.get("clientSlot")
        if slot not in credentials:
            return reject(payload, "client-slot-not-allowed")
        if not verify_mac(payload, credentials[str(slot)]):
            return reject(payload, "missing-authentication" if "mac" not in payload else "bad-hmac")
        timestamp = payload.get("timestamp")
        if not isinstance(timestamp, int) or abs(timestamp - now) > int(authorization["nonceWindowSeconds"]):
            return reject(payload, "expired-timestamp")
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or not nonce:
            return reject(payload, "missing-nonce")
        if nonce in seen_nonces:
            return reject(payload, "replay-nonce")
        seen_nonces.add(nonce)
        if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
            return reject(payload, "session-compatibility-mismatch")
        if payload.get("commandId") != command_for_slot(str(slot)):
            return reject(payload, "command-id-not-allowed")
        if payload.get("command") != EXPECTED_COMMAND:
            return reject(payload, "command-not-allowed")
        if payload.get("mappedInputSequence") != sequence_for_slot(str(slot)):
            return reject(payload, "mapped-input-sequence-mismatch")
        if payload.get("sequence") != expected_sequence[str(slot)]:
            return reject(payload, "sequence-not-next")
        if payload.get("directGameInputClaim") is True:
            return reject(payload, "direct-input-not-allowed")
        if payload.get("publicMatchmakingClaim") is True:
            return reject(payload, "public-matchmaking-not-allowed")
        if sum(1 for row in accepted_commands if row["clientSlot"] == slot) >= 1:
            return reject(payload, "slot-rate-limit-exceeded")

        tick = 1
        expected_sequence[str(slot)] += 1
        row = {
            "commandId": payload.get("commandId"),
            "clientSlot": slot,
            "command": EXPECTED_COMMAND,
            "mappedInputSequence": payload.get("mappedInputSequence"),
            "scheduledTick": tick,
            "arrivalOrder": len(accepted_commands) + 1,
            "hostAccepted": True,
            "gameInputSentByScheduler": False,
            "hostHelperInputSent": False,
        }
        accepted_commands.append(row)
        return {"type": "command_accepted", **row}

    def server_main(listener: socket.socket) -> None:
        try:
            listener.listen(2)
            ready.put(listener.getsockname()[1])
            for _ in range(2):
                conn, _addr = listener.accept()
                with conn:
                    handle = conn.makefile("rwb")
                    while True:
                        line = handle.readline()
                        if not line:
                            break
                        payload = json.loads(line.decode("utf-8"))
                        if payload.get("type") == "close":
                            events.append(make_event("client_close", payload))
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
    p2_config = {
        **common,
        "slot": "P2",
        "clientIdentityFingerprint": authorization["clientIdentityFingerprints"]["P2"],
        "commands": [
            {
                "label": "wrong-command-id",
                "slot": "P2",
                "commandId": "host-authority-reject-wrong-command-id-0001",
                "sequence": 1,
                "nonce": "p2-wrong-command-id-0001",
                "mappedInputSequence": P2_SEQUENCE,
            },
            {
                "label": "accepted",
                "slot": "P2",
                "commandId": P2_COMMAND_ID,
                "sequence": 1,
                "nonce": "p2-forward-0001",
                "mappedInputSequence": P2_SEQUENCE,
            },
            {
                "label": "replay",
                "slot": "P2",
                "commandId": P2_COMMAND_ID,
                "sequence": 2,
                "nonce": "p2-forward-0001",
                "mappedInputSequence": P2_SEQUENCE,
            },
            {
                "label": "rate-limit",
                "slot": "P2",
                "commandId": P2_COMMAND_ID,
                "sequence": 2,
                "nonce": "p2-rate-limit-0001",
                "mappedInputSequence": P2_SEQUENCE,
            },
        ],
    }
    p1_config = {
        **common,
        "slot": "P1",
        "clientIdentityFingerprint": authorization["clientIdentityFingerprints"]["P1"],
        "commands": [
            {
                "label": "missing-auth",
                "slot": "P1",
                "commandId": P1_COMMAND_ID,
                "sequence": 1,
                "nonce": "p1-missing-auth-0001",
                "mappedInputSequence": P1_SEQUENCE,
                "omitMac": True,
            },
            {
                "label": "public-matchmaking-claim",
                "slot": "P1",
                "commandId": P1_COMMAND_ID,
                "sequence": 1,
                "nonce": "p1-public-matchmaking-0001",
                "mappedInputSequence": P1_SEQUENCE,
                "publicMatchmakingClaim": True,
            },
            {
                "label": "accepted",
                "slot": "P1",
                "commandId": P1_COMMAND_ID,
                "sequence": 1,
                "nonce": "p1-forward-0001",
                "mappedInputSequence": P1_SEQUENCE,
            },
            {
                "label": "direct-input-claim",
                "slot": "P1",
                "commandId": P1_COMMAND_ID,
                "sequence": 2,
                "nonce": "p1-direct-input-0001",
                "mappedInputSequence": P1_SEQUENCE,
                "directGameInputClaim": True,
            },
        ],
    }

    p2_output = run_client(p2_config, credentials["P2"])
    p1_output = run_client(p1_config, credentials["P1"])
    require(
        [(row.get("label"), row.get("type"), row.get("reason"), row.get("commandId")) for row in p2_output["responses"]]
        == [
            ("session", "session_accepted", None, None),
            ("wrong-command-id", "command_rejected", "command-id-not-allowed", "host-authority-reject-wrong-command-id-0001"),
            ("accepted", "command_accepted", None, P2_COMMAND_ID),
            ("replay", "command_rejected", "replay-nonce", P2_COMMAND_ID),
            ("rate-limit", "command_rejected", "slot-rate-limit-exceeded", P2_COMMAND_ID),
        ],
        "P2 client response sequence mismatch",
    )
    require(
        [(row.get("label"), row.get("type"), row.get("reason"), row.get("commandId")) for row in p1_output["responses"]]
        == [
            ("session", "session_accepted", None, None),
            ("missing-auth", "command_rejected", "missing-authentication", P1_COMMAND_ID),
            ("public-matchmaking-claim", "command_rejected", "public-matchmaking-not-allowed", P1_COMMAND_ID),
            ("accepted", "command_accepted", None, P1_COMMAND_ID),
            ("direct-input-claim", "command_rejected", "direct-input-not-allowed", P1_COMMAND_ID),
        ],
        "P1 client response sequence mismatch",
    )
    thread.join(timeout=5)
    require(not thread.is_alive(), "host-authority server thread did not stop")
    if not server_errors.empty():
        raise HostAuthorityTwoClientSmokeBuildError(server_errors.get())
    events.append(make_event("client_process_exited", processId=p2_output["clientProcessId"], clientSlot="P2", exitCode=p2_output["clientExitCode"]))
    events.append(make_event("client_process_exited", processId=p1_output["clientProcessId"], clientSlot="P1", exitCode=p1_output["clientExitCode"]))
    events.append(make_event("server_stopped"))

    schedule = sorted(accepted_commands, key=lambda row: (int(row["scheduledTick"]), str(row["clientSlot"])))
    relay_plan = [
        {
            "scheduledTick": row["scheduledTick"],
            "clientSlot": row["clientSlot"],
            "command": row["command"],
            "mappedInputSequence": row["mappedInputSequence"],
            "route": "P1/inputDevice0/top-split-half" if row["clientSlot"] == "P1" else "P2/inputDevice1/bottom-split-half",
            "hostHelperInputSent": False,
        }
        for row in schedule
    ]
    scheduler = {
        "authorityModel": "single-host-authoritative-copied-session",
        "arrivalOrder": [row["clientSlot"] for row in accepted_commands],
        "deterministicScheduleOrder": [row["clientSlot"] for row in schedule],
        "scheduledTickCount": 1,
        "acceptedCommandCount": len(accepted_commands),
        "rejectedCommandCount": len(rejected_commands),
        "relayPlan": relay_plan,
        "relayPlanSha256": sha256_payload(relay_plan),
        "gameInputSentByScheduler": False,
        "hostHelperInputSent": False,
        "sameWorkstationOnly": True,
        "multiHostLanClaim": False,
        "publicMatchmakingClaim": False,
        "nativeBeaNetcodeClaim": False,
        "deterministicSyncClaim": False,
        "dualClientParityClaim": False,
    }
    transport = {
        "transport": TRANSPORT,
        "bindHost": bind_host,
        "actualBindPort": port,
        "networkScope": "private-interface-two-client-host-authority-smoke",
        "privateLanInterfaceBound": True,
        "loopbackInterfaceOnly": False,
        "sameWorkstationOnly": True,
        "processSeparatedClients": True,
        "twoDistinctClientProcesses": True,
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
        "gameInputSentByScheduler": False,
        "hostHelperInputSent": False,
    }
    process_boundary = {
        "processModel": "two-separate-python-client-processes",
        "builderProcessId": os.getpid(),
        "clientProcesses": [
            {"clientSlot": "P2", "clientProcessId": p2_output["clientProcessId"], "clientVerifiedServerIdentity": p2_output["clientVerifiedServerIdentity"], "clientExitCode": p2_output["clientExitCode"]},
            {"clientSlot": "P1", "clientProcessId": p1_output["clientProcessId"], "clientVerifiedServerIdentity": p1_output["clientVerifiedServerIdentity"], "clientExitCode": p1_output["clientExitCode"]},
        ],
        "clientProcessIdsDistinctFromBuilder": all(row["clientProcessId"] != os.getpid() for row in (p1_output, p2_output)),
        "clientProcessIdsDistinctFromEachOther": p1_output["clientProcessId"] != p2_output["clientProcessId"],
        "credentialTransportToClientProcesses": "stdin-ephemeral-not-serialized-to-artifact",
        "clientCommandLineContainsCredential": False,
        "clientEnvironmentContainsCredential": False,
        "clientStdoutContainsCredential": False,
        "clientStderrContainsCredential": False,
        "sameWorkstationOnly": True,
        "multiHostLanClaim": False,
        "clientResponses": {"P1": p1_output["responses"], "P2": p2_output["responses"]},
    }
    transcript = {
        "transport": TRANSPORT,
        "protocolVersion": PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "messageCount": 22,
        "events": events,
    }
    commands = {"accepted": accepted_commands, "rejected": rejected_commands}
    return transport, commands, scheduler, process_boundary, transcript


def build_bundle(remote_client_proof_path: Path, output_path: Path, *, bind_host: str) -> dict[str, Any]:
    remote_client_proof_path = remote_client_proof_path.resolve()
    require_private_bind_host(bind_host)
    remote_summary = remote.validate_bundle(remote_client_proof_path, expected_controller_configuration=1)
    remote_bundle = read_json(remote_client_proof_path)
    descriptor = make_session_descriptor(remote_bundle, remote_client_proof_path, remote_summary)

    credentials = {"P1": secrets.token_bytes(32), "P2": secrets.token_bytes(32)}
    upstream_hash = remote.sha256_file(remote_client_proof_path)
    authorization = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "slotCredentialFingerprints": {slot: sha256(value).hexdigest() for slot, value in credentials.items()},
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256(f"{PROTOCOL}:{upstream_hash}:server".encode("utf-8")).hexdigest(),
        "clientIdentityMode": "pinned-slot-fingerprint",
        "clientIdentityFingerprints": {
            "P1": sha256(f"{PROTOCOL}:{upstream_hash}:P1".encode("utf-8")).hexdigest(),
            "P2": sha256(f"{PROTOCOL}:{upstream_hash}:P2".encode("utf-8")).hexdigest(),
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
        "privateRemoteClientProofBundle": relative_path(output_path.parent, remote_client_proof_path),
        "privateRemoteClientProofSha256": upstream_hash,
        "sessionDescriptor": descriptor,
        "transport": transport,
        "authorization": authorization,
        "clientProcessBoundary": process_boundary,
        "commands": commands,
        "hostAuthorityScheduler": scheduler,
        "transportTranscript": transcript,
        "claimBoundary": (
            "Same-workstation two-client host-authority scheduler smoke only. This proves two separate local client "
            "processes can authenticate with slot-scoped ephemeral HMAC credentials, source one P1 and one P2 movement "
            "command, and be deterministically scheduled into a host input plan. It does not send game input, does not "
            "launch BEA, and does not prove multi-host LAN play, public matchmaking, public relay/server behavior, "
            "native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad "
            "behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {"bundle": str(output_path.resolve()), "privateRemoteClientSummary": remote_summary}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("private_remote_client_proof", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--bind-host", required=True)
    args = parser.parse_args()

    output_path = args.output or args.private_remote_client_proof.with_name("host-authority-two-client-smoke-proof.json")
    result = build_bundle(args.private_remote_client_proof, output_path.resolve(), bind_host=args.bind_host)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityTwoClientSmokeBuildError,
        remote.PrivateRemoteClientSmokeProofError,
        remote.lan.PrivateTransportSmokeProofError,
        remote.lan.delivery.PrivateRelayDeliveryProofError,
        remote.lan.delivery.relay.RelayProofError,
        remote.lan.delivery.loopback.LoopbackProofError,
        remote.lan.delivery.loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary host-authority two-client smoke bundle build: FAIL: {exc}")
        raise SystemExit(2)
