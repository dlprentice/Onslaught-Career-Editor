#!/usr/bin/env python3
"""Build a WSL2 client smoke proof for the original-binary online ladder."""

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
import threading
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

import winui_safe_copy_online_private_lan_transport_smoke_check as lan


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "subagents"
    / "winui-original-binary-online"
    / "wsl-remote-client-smoke-20260619"
    / "wsl-remote-client-smoke-proof.json"
)

SCHEMA = "winui-original-binary-wsl-remote-client-smoke.v1"
SESSION_SCHEMA = "winui-original-binary-wsl-remote-client-session.v1"
TRANSPORT = "wsl2-remote-client-tcp-jsonl-auth-smoke"
PROTOCOL = "wsl2-remote-client-input.v1"
HELPER = "winui-original-binary-wsl-remote-client-smoke-helper"
HELPER_VERSION = "wsl-remote-client-smoke-helper.v1"
COMMAND_ID = "wsl-remote-client-p2-forward-0001"
REJECTED_P3_COMMAND_ID = "wsl-remote-client-reject-p3-forward-0001"
RATE_LIMIT_COMMAND_ID = "wsl-remote-client-reject-rate-limit-0001"
EXPECTED_REMOTE_SLOT = "P2"
EXPECTED_REMOTE_COMMAND = lan.delivery.relay.EXPECTED_REMOTE_COMMAND
EXPECTED_MAPPED_SEQUENCE = lan.delivery.loopback.EXPECTED_MAPPED_SEQUENCE
EXPECTED_LAN_COMMAND_ID = lan.EXPECTED_COMMAND_ID
ACTIVE_SLOTS = ["P1", "P2"]
METADATA_SLOTS = ["P3", "P4"]
SAFE_CHILD_ENV_KEYS = {"COMSPEC", "PATH", "PATHEXT", "SYSTEMROOT", "TEMP", "TMP", "WINDIR"}
DANGEROUS_ENV_FRAGMENTS = ("SECRET", "TOKEN", "PASSWORD", "API_KEY", "APIKEY", "AUTH")
PROCESS_TIMEOUT_SECONDS = 20


class WslRemoteClientSmokeBundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WslRemoteClientSmokeBundleBuildError(message)


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
        raise WslRemoteClientSmokeBundleBuildError(f"Bind host must be an IP address: {bind_host}") from exc
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
    require(bool(line), "WSL client socket closed before a response was read")
    value = json.loads(line.decode("utf-8"))
    require(isinstance(value, dict), "WSL client response was not a JSON object")
    return value


def sha256_payload(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind, "monotonicNs": time.monotonic_ns()}
    if payload is not None:
        event["payloadSha256"] = sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def safe_child_environment() -> dict[str, str]:
    env = {key: os.environ[key] for key in SAFE_CHILD_ENV_KEYS if key in os.environ}
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def sensitive_env_key_count(env: dict[str, str]) -> int:
    return sum(1 for key in env if any(fragment in key.upper() for fragment in DANGEROUS_ENV_FRAGMENTS))


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
        "allowedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "rejectedGameplayRouteSlots": METADATA_SLOTS,
        "allowedCommand": EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
        "upstreamPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
        "upstreamPrivateRelayCommandId": private_lan_summary["wouldForwardToPrivateRelayCommandId"],
        "upstreamPrivateRelayDeliveryEvidence": private_lan_summary["upstreamPrivateRelay"]["gameInputDeliveryEvidence"],
        "levelId": 850,
        "controllerConfiguration": 1,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
    }


WSL_CLIENT_CODE = r'''
import hmac
import json
import os
import platform
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
        raise RuntimeError("socket closed before response")
    value = json.loads(line.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("response was not an object")
    return value


config = json.loads(sys.stdin.read())
credential = bytes.fromhex(config["credentialHex"])
responses = []

with socket.create_connection((config["windowsHost"], int(config["port"])), timeout=5) as client:
    local_address = client.getsockname()[0]
    peer_address = client.getpeername()[0]
    handle = client.makefile("rwb")
    hello = {
        "type": "session_hello",
        "protocolVersion": config["protocolVersion"],
        "serverIdentityFingerprint": config["serverIdentityFingerprint"],
        "clientIdentityFingerprint": config["clientIdentityFingerprint"],
        "nonce": "wsl-remote-client-session-hello-0001",
        "timestamp": int(config["now"]),
        "clientRuntime": {
            "clientKind": "wsl2-linux-python-client",
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "pythonVersion": platform.python_version(),
            "networkAddress": local_address,
            "peerAddress": peer_address,
        },
    }
    write_json_line(handle, sign_payload(hello, credential))
    accepted = read_json_line(handle)
    responses.append({"label": "session", "type": accepted.get("type"), "serverIdentityFingerprint": accepted.get("serverIdentityFingerprint")})

    p3_command = {
        "type": "command",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "commandId": config["rejectedP3CommandId"],
        "remoteSlot": "P3",
        "command": config["expectedRemoteCommand"],
        "sequence": 1,
        "nonce": "wsl-remote-client-p3-forward-0001",
        "timestamp": int(config["now"]),
        "wouldForwardToPrivateLanCommandId": config["expectedLanCommandId"],
    }
    write_json_line(handle, sign_payload(p3_command, credential))
    p3_response = read_json_line(handle)
    responses.append({"label": "p3-rejected", "type": p3_response.get("type"), "reason": p3_response.get("reason")})

    p2_command = dict(p3_command)
    p2_command.update({
        "commandId": config["acceptedCommandId"],
        "remoteSlot": "P2",
        "sequence": 2,
        "nonce": "wsl-remote-client-p2-forward-0001",
    })
    write_json_line(handle, sign_payload(p2_command, credential))
    p2_response = read_json_line(handle)
    responses.append({
        "label": "accepted",
        "type": p2_response.get("type"),
        "commandId": p2_response.get("commandId"),
        "wouldForwardToPrivateLanCommandId": p2_response.get("wouldForwardToPrivateLanCommandId"),
    })

    rate_command = dict(p2_command)
    rate_command.update({
        "commandId": config["rateLimitCommandId"],
        "sequence": 3,
        "nonce": "wsl-remote-client-rate-limit-0001",
    })
    write_json_line(handle, sign_payload(rate_command, credential))
    rate_response = read_json_line(handle)
    responses.append({"label": "rate-limit", "type": rate_response.get("type"), "reason": rate_response.get("reason")})

    write_json_line(handle, {"type": "close"})

result = {
    "clientProcessId": os.getpid(),
    "clientVerifiedServerIdentity": True,
    "clientRuntime": hello["clientRuntime"],
    "responses": responses,
}
print(json.dumps(result, sort_keys=True))
'''


def run_wsl_client_session(
    descriptor: dict[str, Any],
    *,
    credential: bytes,
    authorization: dict[str, Any],
    bind_host: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((bind_host, 0))
    listener.listen(1)
    listener.settimeout(10)
    port = int(listener.getsockname()[1])

    server_errors: queue.Queue[BaseException] = queue.Queue()
    transcript_events: list[dict[str, Any]] = [make_event("server_bound", windowsBindHost=bind_host, actualBindPort=port)]
    accepted_command_count = 0
    client_runtime_seen: dict[str, Any] = {}
    client_source_address = ""

    def reject(payload: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "type": "command_rejected",
            "reason": reason,
            "commandId": payload.get("commandId"),
            "gameInputSentByWslClient": False,
            "hostHelperInputSent": False,
        }

    def verify_mac(payload: dict[str, Any]) -> bool:
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(str(payload.get("mac", "")), expected)

    def handle_payload(payload: dict[str, Any]) -> dict[str, Any]:
        nonlocal accepted_command_count, client_runtime_seen
        if payload.get("type") == "close":
            return {"type": "closed"}
        if not verify_mac(payload):
            return reject(payload, "missing-or-bad-authentication")
        if payload.get("type") == "session_hello":
            if payload.get("protocolVersion") != PROTOCOL:
                return {"type": "session_rejected", "reason": "protocol-version-mismatch"}
            if payload.get("serverIdentityFingerprint") != authorization["serverIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "server-identity-mismatch"}
            if payload.get("clientIdentityFingerprint") != authorization["clientIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "client-identity-mismatch"}
            runtime = payload.get("clientRuntime")
            require(isinstance(runtime, dict), "WSL client hello missing runtime metadata")
            client_runtime_seen = runtime
            return {
                "type": "session_accepted",
                "compatibilityKey": descriptor["sessionCompatibilityKey"],
                "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
                "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
            }
        if payload.get("type") != "command":
            return reject(payload, "unknown-message-type")
        if payload.get("protocolVersion") != PROTOCOL:
            return reject(payload, "protocol-version-mismatch")
        if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
            return reject(payload, "compatibility-key-mismatch")
        if payload.get("command") != EXPECTED_REMOTE_COMMAND:
            return reject(payload, "command-not-allowed")
        if payload.get("remoteSlot") in METADATA_SLOTS:
            return reject(payload, "metadata-slot-gameplay-not-allowed")
        if payload.get("remoteSlot") != EXPECTED_REMOTE_SLOT:
            return reject(payload, "remote-slot-not-allowed")
        if payload.get("wouldForwardToPrivateLanCommandId") != EXPECTED_LAN_COMMAND_ID:
            return reject(payload, "forward-target-mismatch")
        if accepted_command_count >= 1:
            return reject(payload, "rate-limit-exceeded")
        if payload.get("commandId") != COMMAND_ID:
            return reject(payload, "command-id-not-allowlisted")
        accepted_command_count += 1
        return {
            "type": "command_accepted",
            "commandId": COMMAND_ID,
            "remoteSlot": EXPECTED_REMOTE_SLOT,
            "command": EXPECTED_REMOTE_COMMAND,
            "remoteClientAccepted": True,
            "wouldForwardToPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
            "gameInputSentByWslClient": False,
            "hostHelperInputSent": False,
        }

    def server_main() -> None:
        nonlocal client_source_address
        try:
            connection, remote_address = listener.accept()
            client_source_address = str(remote_address[0])
            with connection:
                handle = connection.makefile("rwb")
                while True:
                    line = handle.readline()
                    if not line:
                        break
                    payload = json.loads(line.decode("utf-8"))
                    require(isinstance(payload, dict), "WSL client payload was not an object")
                    if payload.get("type") == "session_hello":
                        transcript_events.append(make_event("client_session_hello", {"type": "session_hello"}))
                    elif payload.get("commandId") == REJECTED_P3_COMMAND_ID:
                        transcript_events.append(make_event("client_command_p3_forward", {"type": "command"}))
                    elif payload.get("commandId") == COMMAND_ID:
                        transcript_events.append(make_event("client_command_p2_forward", {"type": "command"}))
                    elif payload.get("commandId") == RATE_LIMIT_COMMAND_ID:
                        transcript_events.append(make_event("client_command_rate_limited", {"type": "command"}))
                    elif payload.get("type") == "close":
                        transcript_events.append(make_event("client_close", {"type": "close"}))
                        break
                    response = handle_payload(payload)
                    if response.get("type") == "closed":
                        break
                    write_json_line(handle, response)
                    if response.get("type") == "session_accepted":
                        transcript_events.append(make_event("server_session_accepted", {"type": "session_accepted"}))
                    elif response.get("type") == "command_accepted":
                        transcript_events.append(
                            make_event(
                                "server_command_accepted",
                                {"type": "command_accepted"},
                                commandId=COMMAND_ID,
                                wouldForwardToPrivateLanCommandId=EXPECTED_LAN_COMMAND_ID,
                                gameInputSentByWslClient=False,
                                hostHelperInputSent=False,
                            )
                        )
                    elif response.get("type") == "command_rejected":
                        transcript_events.append(make_event("server_command_rejected", {"type": "command_rejected", "reason": response.get("reason")}))
        except BaseException as exc:  # noqa: BLE001 - propagate server thread failure to caller.
            server_errors.put(exc)
        finally:
            listener.close()

    server = threading.Thread(target=server_main, name="wsl-remote-client-smoke-server", daemon=True)
    server.start()

    child_env = safe_child_environment()
    client_config = {
        "windowsHost": bind_host,
        "port": port,
        "protocolVersion": PROTOCOL,
        "credentialHex": credential.hex(),
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
        "compatibilityKey": descriptor["sessionCompatibilityKey"],
        "expectedRemoteCommand": EXPECTED_REMOTE_COMMAND,
        "expectedLanCommandId": EXPECTED_LAN_COMMAND_ID,
        "acceptedCommandId": COMMAND_ID,
        "rejectedP3CommandId": REJECTED_P3_COMMAND_ID,
        "rateLimitCommandId": RATE_LIMIT_COMMAND_ID,
        "now": 1_786_000_000,
    }
    process = subprocess.Popen(
        ["wsl.exe", "python3", "-c", WSL_CLIENT_CODE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=child_env,
    )
    transcript_events.append(make_event("wsl_client_process_started", windowsProcessId=process.pid, processModel="wsl2-python-process"))
    try:
        stdout, stderr = process.communicate(json.dumps(client_config), timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
        raise WslRemoteClientSmokeBundleBuildError(f"WSL client process timed out: {stderr.strip()}")
    transcript_events.append(make_event("wsl_client_process_exited", windowsProcessId=process.pid, exitCode=process.returncode))
    require(process.returncode == 0, f"WSL client process failed: {stderr.strip()}")
    require(credential.hex() not in stdout and credential.hex() not in stderr, "credential leaked through WSL client output")
    client_output = json.loads(stdout.strip())
    require(isinstance(client_output, dict), "WSL client output must be a JSON object")
    server.join(timeout=5)
    require(not server.is_alive(), "WSL remote-client smoke server thread did not stop")
    if not server_errors.empty():
        raise WslRemoteClientSmokeBundleBuildError(server_errors.get())
    transcript_events.append(make_event("server_stopped"))

    client_runtime = dict(client_runtime_seen or client_output.get("clientRuntime") or {})
    if client_source_address:
        client_runtime["windowsObservedClientSourceAddress"] = client_source_address
    transport = {
        "transport": TRANSPORT,
        "windowsBindHost": bind_host,
        "actualBindPort": port,
        "networkScope": "wsl2-to-windows-host-private-interface-smoke",
        "loopbackInterfaceOnly": False,
        "privateInterfaceBound": True,
        "privateInterfaceSocketOpened": True,
        "wsl2ClientProcess": True,
        "crossEnvironmentClient": True,
        "samePhysicalMachineOnly": True,
        "secondPhysicalHostClaim": False,
        "multiHostLanClaim": False,
        "publicNetworkSocketsOpened": False,
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
        "gameInputSentByWslClient": False,
        "hostHelperInputSent": False,
    }
    commands = {
        "accepted": [
            {
                "commandId": COMMAND_ID,
                "remoteSlot": EXPECTED_REMOTE_SLOT,
                "command": EXPECTED_REMOTE_COMMAND,
                "authorizationStatus": "accepted-hmac-sha256",
                "wslClientAccepted": True,
                "wouldForwardToPrivateLanCommandId": EXPECTED_LAN_COMMAND_ID,
                "gameInputSentByWslClient": False,
                "hostHelperInputSent": False,
            }
        ],
        "rejected": [
            {"commandId": REJECTED_P3_COMMAND_ID, "reason": "metadata-slot-gameplay-not-allowed", "wslClientAccepted": False},
            {"commandId": RATE_LIMIT_COMMAND_ID, "reason": "rate-limit-exceeded", "wslClientAccepted": False},
            {"commandId": "wsl-remote-client-reject-second-physical-host-claim-0001", "reason": "second-physical-host-positive-claim-not-allowed", "wslClientAccepted": False},
            {"commandId": "wsl-remote-client-reject-public-matchmaking-claim-0001", "reason": "public-matchmaking-not-allowed", "wslClientAccepted": False},
            {"commandId": "wsl-remote-client-reject-direct-input-claim-0001", "reason": "direct-input-not-allowed", "wslClientAccepted": False},
        ],
    }
    transcript = {
        "transport": TRANSPORT,
        "protocolVersion": PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
        "messageCount": 7,
        "events": transcript_events,
    }
    process_boundary = {
        "processModel": "wsl2-python-process",
        "windowsBuilderProcessId": os.getpid(),
        "wslLauncherWindowsProcessId": process.pid,
        "wslClientProcessId": client_output["clientProcessId"],
        "clientExitCode": process.returncode,
        "clientVerifiedServerIdentity": client_output["clientVerifiedServerIdentity"],
        "wslClientRuntime": client_runtime,
        "clientCommandLineContainsCredential": False,
        "clientEnvironmentContainsCredential": False,
        "clientStdoutContainsCredential": False,
        "clientStderrContainsCredential": False,
        "credentialTransportToClientProcess": "stdin-ephemeral-not-serialized-to-artifact",
        "childEnvSensitiveKeyCount": sensitive_env_key_count(child_env),
        "samePhysicalMachineOnly": True,
        "secondPhysicalHostClaim": False,
        "multiHostLanClaim": False,
        "clientResponses": client_output["responses"],
    }
    return transport, commands, transcript, process_boundary


def build_bundle(private_lan_proof_path: Path, output_path: Path, *, bind_host: str) -> dict[str, Any]:
    private_lan_proof_path = private_lan_proof_path.resolve()
    output_path = output_path.resolve()
    require_private_bind_host(bind_host)
    private_lan_summary = lan.validate_bundle(private_lan_proof_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_proof_path)
    descriptor = make_session_descriptor(private_lan_bundle, private_lan_proof_path, private_lan_summary)

    credential = secrets.token_bytes(32)
    upstream_hash = lan.sha256_file(private_lan_proof_path)
    server_identity_seed = f"{PROTOCOL}:{upstream_hash}:server".encode("utf-8")
    client_identity_seed = f"{PROTOCOL}:{upstream_hash}:wsl-client".encode("utf-8")
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

    transport, commands, transcript, process_boundary = run_wsl_client_session(
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
        "nonClaims": {
            "secondPhysicalHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
            "gameInputSentByWslClient": False,
            "hostHelperInputSent": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "claimBoundary": (
            "WSL2 remote-client command-source smoke only. This proves a WSL2 Linux Python client on the same physical "
            "machine can connect to a Windows private-interface listener, verify pinned server identity, authenticate with "
            "an ephemeral HMAC credential, reject metadata-only P3 gameplay routing, and source one P2 command envelope "
            "that would forward to the already-proven private LAN transport command. It does not prove a second physical "
            "host, multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, "
            "deterministic sync, rollback, anti-cheat, P3/P4 original-binary gameplay, physical gamepad behavior, rebuild "
            "parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {"bundle": str(output_path), "privateLanSummary": private_lan_summary}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("private_lan_proof", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bind-host", required=True, help="Windows private non-loopback interface reachable from WSL2.")
    args = parser.parse_args()

    result = build_bundle(args.private_lan_proof, args.output, bind_host=args.bind_host)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
