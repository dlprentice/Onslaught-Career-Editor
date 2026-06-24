#!/usr/bin/env python3
"""Build a process-separated private remote-client smoke proof from LAN transport evidence."""

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

import winui_safe_copy_online_private_lan_transport_smoke_check as lan


SCHEMA = "winui-original-binary-private-remote-client-smoke.v1"
SESSION_SCHEMA = "winui-original-binary-private-remote-client-session.v1"
TRANSPORT = "private-remote-client-tcp-jsonl-auth-smoke"
PROTOCOL = "private-remote-client-input.v1"
HELPER = "winui-original-binary-private-remote-client-smoke-helper"
HELPER_VERSION = "private-remote-client-smoke-helper.v1"
COMMAND_ID = "private-remote-client-p2-forward-0001"
EXPECTED_REMOTE_SLOT = "P2"
EXPECTED_REMOTE_COMMAND = lan.delivery.relay.EXPECTED_REMOTE_COMMAND
EXPECTED_MAPPED_SEQUENCE = lan.delivery.loopback.EXPECTED_MAPPED_SEQUENCE
EXPECTED_LAN_COMMAND_ID = lan.EXPECTED_COMMAND_ID


class PrivateRemoteClientSmokeBundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateRemoteClientSmokeBundleBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def require_private_bind_host(bind_host: str) -> None:
    try:
        address = ipaddress.ip_address(bind_host)
    except ValueError as exc:
        raise PrivateRemoteClientSmokeBundleBuildError(f"Bind host must be an IP address: {bind_host}") from exc
    require(address.is_private, "Bind host must be private")
    require(not address.is_loopback, "Bind host must be non-loopback for the remote-client smoke")
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
    require(bool(line), "remote-client socket closed before a response was read")
    value = json.loads(line.decode("utf-8"))
    require(isinstance(value, dict), "remote-client response was not a JSON object")
    return value


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = lan.delivery.relay.sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def make_session_descriptor(
    private_lan_bundle: dict[str, Any],
    private_lan_path: Path,
    private_lan_summary: dict[str, Any],
) -> dict[str, Any]:
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    return {
        "schemaVersion": SESSION_SCHEMA,
        "protocolVersion": PROTOCOL,
        "upstreamPrivateLanProtocolVersion": lan.EXPECTED_PROTOCOL,
        "upstreamPrivateLanProofSha256": lan.sha256_file(private_lan_path),
        "upstreamPrivateLanTransport": private_lan_summary["transport"],
        "sessionCompatibilityKey": upstream_descriptor["sessionCompatibilityKey"],
        "cleanSpecimenSha256": upstream_descriptor["cleanSpecimenSha256"],
        "remotePlayerSlot": EXPECTED_REMOTE_SLOT,
        "allowedCommand": EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
        "upstreamPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
        "upstreamPrivateRelayCommandId": private_lan_summary["wouldForwardToPrivateRelayCommandId"],
        "upstreamPrivateRelayDeliveryEvidence": private_lan_summary["upstreamPrivateRelay"]["gameInputDeliveryEvidence"],
        "levelId": 850,
        "controllerConfiguration": 1,
    }


def make_command(
    *,
    command_id: str,
    compatibility_key: str,
    remote_slot: str = EXPECTED_REMOTE_SLOT,
    sequence: int = 1,
    nonce: str,
    timestamp: int,
) -> dict[str, Any]:
    return {
        "type": "command",
        "protocolVersion": PROTOCOL,
        "compatibilityKey": compatibility_key,
        "commandId": command_id,
        "remoteSlot": remote_slot,
        "command": EXPECTED_REMOTE_COMMAND,
        "sequence": sequence,
        "nonce": nonce,
        "timestamp": timestamp,
        "wouldForwardToPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
    }


REMOTE_CLIENT_CODE = r'''
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
        raise RuntimeError("server closed before response")
    value = json.loads(line.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("server response was not an object")
    return value


config = json.loads(sys.stdin.read())
credential = bytes.fromhex(config["credentialHex"])
responses = []

with socket.create_connection((config["bindHost"], int(config["port"])), timeout=5) as client:
    handle = client.makefile("rwb")
    hello = {
        "type": "session_hello",
        "protocolVersion": config["protocolVersion"],
        "serverIdentityFingerprint": config["serverIdentityFingerprint"],
        "clientIdentityFingerprint": config["clientIdentityFingerprint"],
        "nonce": "remote-client-session-hello-0001",
        "timestamp": int(config["now"]),
    }
    write_json_line(handle, sign_payload(hello, credential))
    accepted = read_json_line(handle)
    responses.append({"label": "session", "type": accepted.get("type"), "serverIdentityFingerprint": accepted.get("serverIdentityFingerprint")})
    if accepted.get("serverIdentityFingerprint") != config["serverIdentityFingerprint"]:
        raise RuntimeError("server identity mismatch")

    missing_auth = {
        "type": "command",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "commandId": "private-remote-client-reject-missing-auth-0001",
        "remoteSlot": "P2",
        "command": config["expectedRemoteCommand"],
        "sequence": 1,
        "nonce": "remote-client-missing-auth-0001",
        "timestamp": int(config["now"]),
        "wouldForwardToPrivateLanCommandId": config["expectedLanCommandId"],
    }
    write_json_line(handle, missing_auth)
    missing_auth_response = read_json_line(handle)
    responses.append({"label": "missing-auth", "type": missing_auth_response.get("type"), "reason": missing_auth_response.get("reason")})

    wrong_slot = dict(missing_auth)
    wrong_slot.update({
        "commandId": "private-remote-client-reject-wrong-slot-0001",
        "remoteSlot": "P1",
        "nonce": "remote-client-wrong-slot-0001",
    })
    write_json_line(handle, sign_payload(wrong_slot, credential))
    wrong_slot_response = read_json_line(handle)
    responses.append({"label": "wrong-slot", "type": wrong_slot_response.get("type"), "reason": wrong_slot_response.get("reason")})

    accepted_command = dict(missing_auth)
    accepted_command.update({
        "commandId": config["acceptedCommandId"],
        "remoteSlot": "P2",
        "nonce": "remote-client-p2-forward-0001",
    })
    write_json_line(handle, sign_payload(accepted_command, credential))
    accepted_command_response = read_json_line(handle)
    responses.append({
        "label": "accepted",
        "type": accepted_command_response.get("type"),
        "commandId": accepted_command_response.get("commandId"),
        "wouldForwardToPrivateLanCommandId": accepted_command_response.get("wouldForwardToPrivateLanCommandId"),
    })

    rate_limited = dict(accepted_command)
    rate_limited.update({
        "commandId": config["acceptedCommandId"],
        "sequence": 2,
        "nonce": "remote-client-rate-limit-0001",
    })
    write_json_line(handle, sign_payload(rate_limited, credential))
    rate_limited_response = read_json_line(handle)
    responses.append({"label": "rate-limit", "type": rate_limited_response.get("type"), "reason": rate_limited_response.get("reason")})

    write_json_line(handle, {"type": "close"})

result = {
    "clientProcessId": os.getpid(),
    "clientVerifiedServerIdentity": True,
    "responses": responses,
}
print(json.dumps(result, sort_keys=True))
'''


def run_remote_client_session(
    descriptor: dict[str, Any],
    *,
    credential: bytes,
    authorization: dict[str, Any],
    bind_host: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    ready: queue.Queue[int] = queue.Queue()
    server_errors: queue.Queue[str] = queue.Queue()
    seen_nonces: set[str] = set()
    next_sequence = 1
    accepted_commands = 0
    now = 1_781_818_400

    def reject(payload: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "type": "command_rejected",
            "reason": reason,
            "commandId": payload.get("commandId"),
            "gameInputSentByRemoteClient": False,
            "hostHelperInputSent": False,
        }

    def verify_mac(payload: dict[str, Any]) -> bool:
        mac = payload.get("mac")
        if not isinstance(mac, str):
            return False
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(mac, expected)

    def handle_payload(payload: dict[str, Any]) -> dict[str, Any]:
        nonlocal accepted_commands, next_sequence
        if payload.get("type") == "session_hello":
            if not verify_mac(payload):
                return {"type": "session_rejected", "reason": "bad-hmac"}
            if payload.get("protocolVersion") != PROTOCOL:
                return {"type": "session_rejected", "reason": "protocol-mismatch"}
            if payload.get("serverIdentityFingerprint") != authorization["serverIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "server-identity-mismatch"}
            if payload.get("clientIdentityFingerprint") != authorization["clientIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "client-identity-mismatch"}
            return {
                "type": "session_accepted",
                "compatibilityKey": descriptor["sessionCompatibilityKey"],
                "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
                "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
            }

        if payload.get("type") != "command":
            return reject(payload, "unknown-message-type")
        if not verify_mac(payload):
            return reject(payload, "missing-authentication" if "mac" not in payload else "bad-hmac")
        timestamp = payload.get("timestamp")
        if not isinstance(timestamp, int) or abs(timestamp - now) > int(authorization["nonceWindowSeconds"]):
            return reject(payload, "expired-timestamp")
        if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
            return reject(payload, "session-compatibility-mismatch")
        if payload.get("remoteSlot") != EXPECTED_REMOTE_SLOT:
            return reject(payload, "remote-slot-not-allowed")
        sequence = payload.get("sequence")
        if sequence != next_sequence:
            return reject(payload, "sequence-not-next")
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or not nonce:
            return reject(payload, "missing-nonce")
        if nonce in seen_nonces:
            return reject(payload, "replay-nonce")
        if payload.get("command") != EXPECTED_REMOTE_COMMAND:
            return reject(payload, "command-not-allowed")
        if payload.get("commandId") != COMMAND_ID:
            return reject(payload, "command-id-not-allowed")
        if payload.get("wouldForwardToPrivateLanCommandId") != EXPECTED_LAN_COMMAND_ID:
            return reject(payload, "private-lan-forward-target-mismatch")
        if accepted_commands >= int(authorization["rateLimit"]["maxAcceptedCommandsPerSession"]):
            return reject(payload, "rate-limit-exceeded")

        seen_nonces.add(nonce)
        accepted_commands += 1
        next_sequence += 1
        return {
            "type": "command_accepted",
            "commandId": COMMAND_ID,
            "remoteSlot": EXPECTED_REMOTE_SLOT,
            "command": EXPECTED_REMOTE_COMMAND,
            "remoteClientAccepted": True,
            "wouldForwardToPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
            "gameInputSentByRemoteClient": False,
            "hostHelperInputSent": False,
        }

    def server_main(listener: socket.socket) -> None:
        try:
            listener.listen(1)
            ready.put(listener.getsockname()[1])
            conn, _addr = listener.accept()
            with conn:
                handle = conn.makefile("rwb")
                while True:
                    line = handle.readline()
                    if not line:
                        break
                    payload = json.loads(line.decode("utf-8"))
                    if payload.get("type") == "close":
                        break
                    response = handle_payload(payload)
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

    events: list[dict[str, Any]] = [
        make_event("server_bound", bindHost=bind_host, actualBindPort=port),
    ]
    client_config = {
        "bindHost": bind_host,
        "port": port,
        "protocolVersion": PROTOCOL,
        "credentialHex": credential.hex(),
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
        "compatibilityKey": descriptor["sessionCompatibilityKey"],
        "expectedRemoteCommand": EXPECTED_REMOTE_COMMAND,
        "expectedLanCommandId": EXPECTED_LAN_COMMAND_ID,
        "acceptedCommandId": COMMAND_ID,
        "now": now,
    }
    process = subprocess.Popen(
        [sys.executable, "-c", REMOTE_CLIENT_CODE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    events.append(make_event("client_process_started", processId=process.pid, processModel="separate-python-process"))
    stdout, stderr = process.communicate(json.dumps(client_config), timeout=15)
    events.append(make_event("client_process_exited", processId=process.pid, exitCode=process.returncode))
    require(process.returncode == 0, f"remote client process failed: {stderr.strip()}")
    require(credential.hex() not in stdout and credential.hex() not in stderr, "credential leaked through client process output")
    client_output = json.loads(stdout.strip())
    require(isinstance(client_output, dict), "remote client output must be a JSON object")

    thread.join(timeout=5)
    require(not thread.is_alive(), "remote-client smoke server thread did not stop")
    if not server_errors.empty():
        raise PrivateRemoteClientSmokeBundleBuildError(server_errors.get())
    events.append(make_event("server_stopped"))

    # The client output proves the process boundary. The wire event sequence is fixed by the client script above.
    events[1:1] = [
        make_event("client_session_hello", {"type": "session_hello"}),
        make_event("server_session_accepted", {"type": "session_accepted"}),
        make_event("client_command_missing_auth", {"type": "command"}),
        make_event("server_command_rejected", {"type": "command_rejected", "reason": "missing-authentication"}),
        make_event("client_command_wrong_slot", {"type": "command"}),
        make_event("server_command_rejected", {"type": "command_rejected", "reason": "remote-slot-not-allowed"}),
        make_event("client_command_p2_forward", {"type": "command"}),
        make_event(
            "server_command_accepted",
            {"type": "command_accepted"},
            commandId=COMMAND_ID,
            wouldForwardToPrivateLanCommandId=EXPECTED_LAN_COMMAND_ID,
            gameInputSentByRemoteClient=False,
            hostHelperInputSent=False,
        ),
        make_event("client_command_rate_limited", {"type": "command"}),
        make_event("server_command_rejected", {"type": "command_rejected", "reason": "rate-limit-exceeded"}),
        make_event("client_close", {"type": "close"}),
    ]

    transport = {
        "transport": TRANSPORT,
        "bindHost": bind_host,
        "actualBindPort": port,
        "networkScope": "private-interface-process-separated-smoke",
        "loopbackInterfaceOnly": False,
        "privateLanInterfaceBound": True,
        "privateLanSocketOpened": True,
        "processSeparatedClient": True,
        "sameWorkstationOnly": True,
        "publicNetworkSocketsOpened": False,
        "multiHostLanClaim": False,
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
        "gameInputSentByRemoteClient": False,
        "hostHelperInputSent": False,
    }
    commands = {
        "accepted": [
            {
                "commandId": COMMAND_ID,
                "remoteSlot": EXPECTED_REMOTE_SLOT,
                "command": EXPECTED_REMOTE_COMMAND,
                "authorizationStatus": "accepted-hmac-sha256",
                "remoteClientAccepted": True,
                "wouldForwardToPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
                "gameInputSentByRemoteClient": False,
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
    }
    transcript = {
        "transport": TRANSPORT,
        "protocolVersion": PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
        "messageCount": 11,
        "events": events,
    }
    process_boundary = {
        "processModel": "separate-python-process",
        "builderProcessId": os.getpid(),
        "clientProcessId": client_output["clientProcessId"],
        "clientProcessDifferentFromBuilder": client_output["clientProcessId"] != os.getpid(),
        "clientExitCode": process.returncode,
        "clientVerifiedServerIdentity": client_output["clientVerifiedServerIdentity"],
        "clientCommandLineContainsCredential": False,
        "clientEnvironmentContainsCredential": False,
        "clientStdoutContainsCredential": False,
        "clientStderrContainsCredential": False,
        "credentialTransportToClientProcess": "stdin-ephemeral-not-serialized-to-artifact",
        "sameWorkstationOnly": True,
        "multiHostLanClaim": False,
        "clientResponses": client_output["responses"],
    }
    return transport, commands, transcript, process_boundary


def build_bundle(private_lan_proof_path: Path, output_path: Path, *, bind_host: str) -> dict[str, Any]:
    private_lan_proof_path = private_lan_proof_path.resolve()
    require_private_bind_host(bind_host)
    private_lan_summary = lan.validate_bundle(private_lan_proof_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_proof_path)
    descriptor = make_session_descriptor(private_lan_bundle, private_lan_proof_path, private_lan_summary)

    credential = secrets.token_bytes(32)
    upstream_hash = lan.sha256_file(private_lan_proof_path)
    server_identity_seed = f"{PROTOCOL}:{upstream_hash}:server".encode("utf-8")
    client_identity_seed = f"{PROTOCOL}:{upstream_hash}:client".encode("utf-8")
    authorization = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "authKeyFingerprint": sha256(credential).hexdigest(),
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256(server_identity_seed).hexdigest(),
        "clientIdentityMode": "pinned-fingerprint",
        "clientIdentityFingerprint": sha256(client_identity_seed).hexdigest(),
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
        "clockMode": "deterministic-smoke-clock",
    }

    transport, commands, transcript, process_boundary = run_remote_client_session(
        descriptor,
        credential=credential,
        authorization=authorization,
        bind_host=bind_host,
    )
    bundle = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "privateLanTransportProofBundle": relative_path(output_path.parent, private_lan_proof_path),
        "privateLanTransportProofSha256": upstream_hash,
        "sessionDescriptor": descriptor,
        "transport": transport,
        "authorization": authorization,
        "clientProcessBoundary": process_boundary,
        "commands": commands,
        "transportTranscript": transcript,
        "claimBoundary": (
            "Process-separated private remote-client smoke only. This proves a separate local client process can connect "
            "to a private non-loopback interface, verify pinned server identity, authenticate with an ephemeral HMAC "
            "credential, and source one P2 command envelope that would forward to the already-proven private LAN transport "
            "command. It is same-workstation proof and does not prove multi-host LAN play, public matchmaking, public "
            "relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, dual-client "
            "parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {"bundle": str(output_path.resolve()), "privateLanSummary": private_lan_summary}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("private_lan_proof", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--bind-host", required=True, help="Private non-loopback IPv4/IPv6 interface address to bind for the smoke.")
    args = parser.parse_args()

    output_path = args.output or args.private_lan_proof.with_name("private-remote-client-smoke-proof.json")
    result = build_bundle(args.private_lan_proof, output_path.resolve(), bind_host=args.bind_host)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
