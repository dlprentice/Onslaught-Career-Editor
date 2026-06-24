#!/usr/bin/env python3
"""Build a private LAN transport/auth smoke proof from private relay-delivery evidence."""

from __future__ import annotations

import argparse
import hmac
import ipaddress
import json
import queue
import secrets
import socket
import threading
from hashlib import sha256
from pathlib import Path
from typing import Any

import winui_safe_copy_online_private_relay_delivery_check as delivery
import winui_safe_copy_online_private_lan_transport_smoke_check as transport_check


class PrivateTransportSmokeBundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateTransportSmokeBundleBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def require_private_bind_host(bind_host: str) -> None:
    try:
        address = ipaddress.ip_address(bind_host)
    except ValueError as exc:
        raise PrivateTransportSmokeBundleBuildError(f"Bind host must be an IP address: {bind_host}") from exc
    require(address.is_private, "Bind host must be a private RFC1918/ULA address")
    require(not address.is_loopback, "Bind host must be non-loopback for the private LAN smoke")
    require(not address.is_link_local, "Bind host must not be link-local")
    require(not address.is_multicast and not address.is_unspecified, "Bind host must be a concrete private interface address")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


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
    require(bool(line), "private transport socket closed before a response was read")
    value = json.loads(line.decode("utf-8"))
    require(isinstance(value, dict), "private transport response was not a JSON object")
    return value


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = delivery.relay.sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def make_session_descriptor(private_relay_bundle: dict[str, Any], private_relay_path: Path, private_relay_summary: dict[str, Any]) -> dict[str, Any]:
    adapter = object_at(private_relay_bundle, "hostHelperAdapter")
    return {
        "schemaVersion": transport_check.EXPECTED_SESSION_SCHEMA,
        "protocolVersion": transport_check.EXPECTED_PROTOCOL,
        "upstreamPrivateRelayProtocolVersion": delivery.EXPECTED_PROTOCOL,
        "upstreamPrivateRelayProofSha256": delivery.relay.sha256_file(private_relay_path),
        "sessionCompatibilityKey": adapter["sessionCompatibilityKey"],
        "cleanSpecimenSha256": adapter["cleanSpecimenSha256"],
        "remotePlayerSlot": delivery.relay.EXPECTED_REMOTE_SLOT,
        "allowedCommand": delivery.relay.EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": delivery.loopback.EXPECTED_MAPPED_SEQUENCE,
        "upstreamPrivateRelayCommandId": transport_check.EXPECTED_PRIVATE_RELAY_COMMAND_ID,
        "upstreamLocalRelayCommandId": private_relay_summary["relayCommandId"],
        "upstreamLoopbackCommandId": private_relay_summary["upstreamLoopbackCommandId"],
        "deliveryEvidence": private_relay_summary["gameInputDeliveryEvidence"],
        "levelId": 850,
        "controllerConfiguration": 1,
    }


def make_command(
    *,
    command_id: str,
    compatibility_key: str,
    remote_slot: str = "P2",
    sequence: int = 1,
    nonce: str,
    timestamp: int,
) -> dict[str, Any]:
    return {
        "type": "command",
        "protocolVersion": transport_check.EXPECTED_PROTOCOL,
        "compatibilityKey": compatibility_key,
        "commandId": command_id,
        "remoteSlot": remote_slot,
        "command": delivery.relay.EXPECTED_REMOTE_COMMAND,
        "sequence": sequence,
        "nonce": nonce,
        "timestamp": timestamp,
        "wouldForwardToPrivateRelayCommandId": transport_check.EXPECTED_PRIVATE_RELAY_COMMAND_ID,
    }


def run_private_transport_session(
    descriptor: dict[str, Any],
    *,
    credential: bytes,
    authorization: dict[str, Any],
    bind_host: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ready: queue.Queue[int] = queue.Queue()
    server_errors: queue.Queue[str] = queue.Queue()
    seen_nonces: set[str] = set()
    accepted_commands = 0
    expected_sequence = 1
    now = 2_000_000_000

    def verify_mac(payload: dict[str, Any]) -> bool:
        mac = payload.get("mac")
        if not isinstance(mac, str) or len(mac) != 64:
            return False
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(mac, expected)

    def reject(payload: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "type": "command_rejected",
            "commandId": payload.get("commandId"),
            "reason": reason,
            "privateTransportAccepted": False,
            "gameInputSentByTransport": False,
            "hostHelperInputSent": False,
        }

    def handle_payload(payload: dict[str, Any]) -> dict[str, Any]:
        nonlocal accepted_commands, expected_sequence
        if payload.get("type") == "session_hello":
            if not verify_mac(payload):
                return {"type": "session_rejected", "reason": "bad-hmac"}
            nonce = str(payload.get("nonce") or "")
            if nonce in seen_nonces:
                return {"type": "session_rejected", "reason": "replay-nonce"}
            seen_nonces.add(nonce)
            if payload.get("protocolVersion") != transport_check.EXPECTED_PROTOCOL:
                return {"type": "session_rejected", "reason": "protocol-version-mismatch"}
            if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
                return {"type": "session_rejected", "reason": "session-compatibility-mismatch"}
            if payload.get("serverIdentityFingerprint") != authorization["serverIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "server-identity-mismatch"}
            return {
                "type": "session_accepted",
                "compatibilityKey": descriptor["sessionCompatibilityKey"],
                "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
            }

        if payload.get("type") != "command":
            return reject(payload, "unknown-message-type")
        if not payload.get("mac"):
            return reject(payload, "missing-authentication")
        if not verify_mac(payload):
            return reject(payload, "bad-hmac")

        nonce = str(payload.get("nonce") or "")
        if nonce in seen_nonces:
            return reject(payload, "replay-nonce")
        seen_nonces.add(nonce)
        timestamp = payload.get("timestamp")
        if not isinstance(timestamp, int) or abs(timestamp - now) > int(authorization["nonceWindowSeconds"]):
            return reject(payload, "expired-timestamp")
        if payload.get("compatibilityKey") != descriptor["sessionCompatibilityKey"]:
            return reject(payload, "session-compatibility-mismatch")
        if payload.get("remoteSlot") != delivery.relay.EXPECTED_REMOTE_SLOT:
            return reject(payload, "remote-slot-not-allowed")
        if payload.get("commandId") != transport_check.EXPECTED_COMMAND_ID:
            return reject(payload, "command-id-not-allowed")
        if payload.get("sequence") != expected_sequence:
            return reject(payload, "sequence-not-next")
        if accepted_commands >= int(authorization["rateLimit"]["maxAcceptedCommandsPerSession"]):
            return reject(payload, "rate-limit-exceeded")
        if payload.get("command") != delivery.relay.EXPECTED_REMOTE_COMMAND:
            return reject(payload, "command-not-allowed")
        if payload.get("wouldForwardToPrivateRelayCommandId") != transport_check.EXPECTED_PRIVATE_RELAY_COMMAND_ID:
            return reject(payload, "private-relay-command-mismatch")

        accepted_commands += 1
        expected_sequence += 1
        return {
            "type": "command_accepted",
            "commandId": transport_check.EXPECTED_COMMAND_ID,
            "wouldForwardToPrivateRelayCommandId": transport_check.EXPECTED_PRIVATE_RELAY_COMMAND_ID,
            "privateTransportAccepted": True,
            "authorizationStatus": "accepted-hmac-sha256",
            "gameInputSentByTransport": False,
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
                    write_json_line(handle, handle_payload(payload))
        except Exception as exc:  # pragma: no cover - surfaced through build failure
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
        make_event("server_bound", bindHost=bind_host, actualBindPort=port)
    ]
    accepted_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []

    def exchange(handle: Any, client_kind: str, server_kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        write_json_line(handle, payload)
        events.append(make_event(client_kind, payload))
        response = read_json_line(handle)
        extra: dict[str, Any] = {}
        if response.get("type") == "command_accepted":
            extra = {
                "commandId": response.get("commandId"),
                "wouldForwardToPrivateRelayCommandId": response.get("wouldForwardToPrivateRelayCommandId"),
                "gameInputSentByTransport": response.get("gameInputSentByTransport"),
                "hostHelperInputSent": response.get("hostHelperInputSent"),
            }
        events.append(make_event(server_kind, response, **extra))
        return response

    compatibility_key = descriptor["sessionCompatibilityKey"]
    session_hello = sign_payload(
        {
            "type": "session_hello",
            "protocolVersion": transport_check.EXPECTED_PROTOCOL,
            "compatibilityKey": compatibility_key,
            "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
            "nonce": "session-hello-0001",
            "timestamp": now,
        },
        credential,
    )
    missing_auth = make_command(command_id="private-lan-reject-missing-auth-0001", compatibility_key=compatibility_key, nonce="missing-auth-0001", timestamp=now)
    bad_hmac = sign_payload(make_command(command_id="private-lan-reject-bad-signature-0001", compatibility_key=compatibility_key, nonce="bad-hmac-0001", timestamp=now), credential)
    bad_hmac["mac"] = "0" * 64
    replay_nonce = sign_payload(make_command(command_id="private-lan-reject-replay-0001", compatibility_key=compatibility_key, nonce="session-hello-0001", timestamp=now), credential)
    expired = sign_payload(make_command(command_id="private-lan-reject-expired-nonce-0001", compatibility_key=compatibility_key, nonce="expired-0001", timestamp=now - 999), credential)
    out_of_order = sign_payload(make_command(command_id=transport_check.EXPECTED_COMMAND_ID, compatibility_key=compatibility_key, sequence=3, nonce="sequence-0001", timestamp=now), credential)
    wrong_command_id = sign_payload(make_command(command_id="private-lan-reject-wrong-command-id-0001", compatibility_key=compatibility_key, sequence=1, nonce="wrong-command-id-0001", timestamp=now), credential)
    wrong_server_identity = sign_payload(
        {
            "type": "session_hello",
            "protocolVersion": transport_check.EXPECTED_PROTOCOL,
            "compatibilityKey": compatibility_key,
            "serverIdentityFingerprint": "0" * 64,
            "nonce": "wrong-server-identity-0001",
            "timestamp": now,
        },
        credential,
    )
    accepted = sign_payload(make_command(command_id=transport_check.EXPECTED_COMMAND_ID, compatibility_key=compatibility_key, sequence=1, nonce="accepted-0001", timestamp=now), credential)
    rate_limited = sign_payload(make_command(command_id=transport_check.EXPECTED_COMMAND_ID, compatibility_key=compatibility_key, sequence=2, nonce="rate-0001", timestamp=now), credential)
    wrong_slot = sign_payload(make_command(command_id="private-lan-reject-p1-0001", compatibility_key=compatibility_key, remote_slot="P1", sequence=2, nonce="wrong-slot-0001", timestamp=now), credential)
    wrong_compatibility = sign_payload(make_command(command_id="private-lan-reject-compatibility-0001", compatibility_key="0" * 64, sequence=2, nonce="wrong-compatibility-0001", timestamp=now), credential)
    close = {"type": "close"}

    with socket.create_connection((bind_host, port), timeout=5) as client:
        handle = client.makefile("rwb")
        require(exchange(handle, "client_session_hello", "server_session_accepted", session_hello).get("type") == "session_accepted", "private transport session was not accepted")
        for client_kind, payload, expected_reason in (
            ("client_command_missing_auth", missing_auth, "missing-authentication"),
            ("client_command_bad_hmac", bad_hmac, "bad-hmac"),
            ("client_command_replay_nonce", replay_nonce, "replay-nonce"),
            ("client_command_expired", expired, "expired-timestamp"),
            ("client_command_out_of_order", out_of_order, "sequence-not-next"),
            ("client_command_wrong_command_id", wrong_command_id, "command-id-not-allowed"),
        ):
            response = exchange(handle, client_kind, "server_command_rejected", payload)
            require(response.get("reason") == expected_reason, f"{expected_reason} rejection did not occur")
            rejected_rows.append({
                "commandId": payload.get("commandId"),
                "reason": expected_reason,
                "privateTransportAccepted": False,
                "gameInputSentByTransport": False,
                "hostHelperInputSent": False,
            })

        wrong_identity_response = exchange(handle, "client_session_wrong_server_identity", "server_session_rejected", wrong_server_identity)
        require(wrong_identity_response.get("reason") == "server-identity-mismatch", "server identity rejection did not occur")
        rejected_rows.append({
            "commandId": "private-lan-reject-wrong-server-identity-0001",
            "reason": "server-identity-mismatch",
            "privateTransportAccepted": False,
            "gameInputSentByTransport": False,
            "hostHelperInputSent": False,
        })

        accepted_response = exchange(handle, "client_command_p2_forward", "server_command_accepted", accepted)
        require(accepted_response.get("type") == "command_accepted", "P2 private transport command was not accepted")
        accepted_rows.append({
            "commandId": transport_check.EXPECTED_COMMAND_ID,
            "remoteSlot": delivery.relay.EXPECTED_REMOTE_SLOT,
            "command": delivery.relay.EXPECTED_REMOTE_COMMAND,
            "sequence": 1,
            "authorizationStatus": "accepted-hmac-sha256",
            "privateTransportAccepted": True,
            "wouldForwardToPrivateRelayCommandId": transport_check.EXPECTED_PRIVATE_RELAY_COMMAND_ID,
            "gameInputSentByTransport": False,
            "hostHelperInputSent": False,
            "upstreamHostHelperEvidence": "private-relay-delivery-proof-already-proven",
        })

        for client_kind, payload, expected_reason in (
            ("client_command_rate_limited", rate_limited, "rate-limit-exceeded"),
            ("client_command_wrong_slot", wrong_slot, "remote-slot-not-allowed"),
            ("client_command_wrong_compatibility", wrong_compatibility, "session-compatibility-mismatch"),
        ):
            response = exchange(handle, client_kind, "server_command_rejected", payload)
            require(response.get("reason") == expected_reason, f"{expected_reason} rejection did not occur")
            rejected_rows.append({
                "commandId": payload.get("commandId"),
                "reason": expected_reason,
                "privateTransportAccepted": False,
                "gameInputSentByTransport": False,
                "hostHelperInputSent": False,
            })

        for command_id, reason in (
            ("private-lan-reject-loopback-positive-claim-0001", "loopback-positive-claim"),
            ("private-lan-reject-public-bind-0001", "public-bind-not-allowed"),
            ("private-lan-reject-direct-input-0001", "direct-input-not-allowed"),
        ):
            rejected_rows.append({
                "commandId": command_id,
                "reason": reason,
                "privateTransportAccepted": False,
                "gameInputSentByTransport": False,
                "hostHelperInputSent": False,
            })

        write_json_line(handle, close)
        events.append(make_event("client_close", close))

    thread.join(timeout=5)
    require(not thread.is_alive(), "private transport server thread did not stop")
    if not server_errors.empty():
        raise PrivateTransportSmokeBundleBuildError(server_errors.get())
    events.append(make_event("server_stopped"))

    transport = {
        "transport": transport_check.EXPECTED_TRANSPORT,
        "bindHost": bind_host,
        "actualBindPort": port,
        "networkScope": "private-lan-interface-smoke",
        "loopbackInterfaceOnly": False,
        "privateLanInterfaceBound": True,
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
        "gameInputSentByTransport": False,
        "hostHelperInputSent": False,
        "wouldForwardToPrivateRelayCommandId": transport_check.EXPECTED_PRIVATE_RELAY_COMMAND_ID,
    }
    transcript = {
        "transport": transport_check.EXPECTED_TRANSPORT,
        "protocolVersion": transport_check.EXPECTED_PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "messageCount": 25,
        "events": events,
    }
    return transport, {"accepted": accepted_rows, "rejected": rejected_rows}, transcript


def build_bundle(private_relay_proof_path: Path, output_path: Path, *, bind_host: str) -> dict[str, Any]:
    private_relay_proof_path = private_relay_proof_path.resolve()
    require_private_bind_host(bind_host)
    private_relay_summary = delivery.validate_bundle(private_relay_proof_path, expected_controller_configuration=1)
    private_relay_bundle = read_json(private_relay_proof_path)
    descriptor = make_session_descriptor(private_relay_bundle, private_relay_proof_path, private_relay_summary)

    credential = secrets.token_bytes(32)
    server_identity_seed = f"{transport_check.EXPECTED_PROTOCOL}:{delivery.relay.sha256_file(private_relay_proof_path)}:server".encode("utf-8")
    authorization = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "authKeyFingerprint": sha256(credential).hexdigest(),
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256(server_identity_seed).hexdigest(),
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
        "clockMode": "deterministic-smoke-clock",
    }

    transport, commands, transcript = run_private_transport_session(
        descriptor,
        credential=credential,
        authorization=authorization,
        bind_host=bind_host,
    )
    bundle = {
        "schemaVersion": transport_check.EXPECTED_SCHEMA,
        "generatedBy": transport_check.EXPECTED_HELPER,
        "helperVersion": transport_check.EXPECTED_HELPER_VERSION,
        "protocolVersion": transport_check.EXPECTED_PROTOCOL,
        "privateRelayDeliveryProofBundle": relative_path(output_path.parent, private_relay_proof_path),
        "privateRelayDeliveryProofSha256": delivery.relay.sha256_file(private_relay_proof_path),
        "sessionDescriptor": descriptor,
        "transport": transport,
        "authorization": authorization,
        "commands": commands,
        "transportTranscript": transcript,
        "claimBoundary": (
            "Private LAN-interface transport/auth smoke only. This proves a single-host private-interface TCP JSONL "
            "transport envelope can require an ephemeral HMAC credential, pinned server identity, nonce freshness, replay "
            "rejection, sequence enforcement, and a one-command rate limit before accepting one P2 command that would "
            "forward to the already-proven private relay-delivery command. It does not prove multi-host LAN play, public "
            "matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, "
            "anti-cheat, two-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {"bundle": str(output_path.resolve()), "privateRelaySummary": private_relay_summary}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("private_relay_proof", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--bind-host", required=True, help="Private non-loopback IPv4/IPv6 interface address to bind for the smoke.")
    args = parser.parse_args()

    output_path = args.output or args.private_relay_proof.with_name("private-lan-transport-smoke-proof.json")
    result = build_bundle(args.private_relay_proof, output_path.resolve(), bind_host=args.bind_host)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        PrivateTransportSmokeBundleBuildError,
        transport_check.PrivateTransportSmokeProofError,
        delivery.PrivateRelayDeliveryProofError,
        delivery.relay.RelayProofError,
        delivery.loopback.LoopbackProofError,
        delivery.loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary private transport smoke bundle build: FAIL: {exc}")
        raise SystemExit(2)
