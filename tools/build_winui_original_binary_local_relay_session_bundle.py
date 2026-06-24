#!/usr/bin/env python3
"""Build a localhost relay/session proof bundle from an accepted loopback P2 proof."""

from __future__ import annotations

import argparse
import json
import queue
import socket
import threading
from pathlib import Path
from typing import Any

import winui_safe_copy_online_local_relay_session_check as relay_check
import winui_safe_copy_online_loopback_p2_input_check as loopback_check


class RelayBundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RelayBundleBuildError(message)


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


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def write_json_line(handle: Any, payload: dict[str, Any]) -> None:
    handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
    handle.flush()


def read_json_line(handle: Any) -> dict[str, Any]:
    line = handle.readline()
    require(bool(line), "relay socket closed before a response was read")
    value = json.loads(line.decode("utf-8"))
    require(isinstance(value, dict), "relay response was not a JSON object")
    return value


def make_descriptor(loopback_bundle: dict[str, Any], loopback_path: Path) -> dict[str, Any]:
    session = object_at(loopback_bundle, "session")
    descriptor = {
        "schemaVersion": relay_check.EXPECTED_DESCRIPTOR_SCHEMA,
        "helperName": relay_check.EXPECTED_HELPER,
        "helperVersion": relay_check.EXPECTED_HELPER_VERSION,
        "protocolVersion": relay_check.EXPECTED_PROTOCOL,
        "cleanSpecimenSha256": loopback_check.EXPECTED_CLEAN_SPECIMEN_SHA256,
        "profileManifestSha256": session["profileManifestSha256"],
        "patchKeys": session["patchKeys"],
        "launchArguments": session["launchArguments"],
        "levelId": 850,
        "controllerConfiguration": 1,
        "remotePlayerSlot": relay_check.EXPECTED_REMOTE_SLOT,
        "allowedCommand": relay_check.EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": loopback_check.EXPECTED_MAPPED_SEQUENCE,
        "inputCdbWindowIndex": 2,
        "upstreamLoopbackProtocolVersion": loopback_check.EXPECTED_PROTOCOL,
        "upstreamLoopbackCommandId": relay_check.EXPECTED_LOOPBACK_COMMAND_ID,
        "upstreamLoopbackProofSha256": relay_check.sha256_file(loopback_path),
    }
    descriptor["compatibilityKey"] = relay_check.descriptor_compatibility_key(descriptor)
    descriptor["descriptorId"] = descriptor["compatibilityKey"][:16]
    return descriptor


def handle_relay_message(payload: dict[str, Any], descriptor: dict[str, Any]) -> dict[str, Any]:
    message_type = payload.get("type")
    if message_type == "session_hello":
        if payload.get("protocolVersion") != relay_check.EXPECTED_PROTOCOL:
            return {"type": "session_rejected", "reason": "protocol-version-mismatch"}
        if payload.get("compatibilityKey") != descriptor["compatibilityKey"]:
            return {"type": "session_rejected", "reason": "compatibility-key-mismatch"}
        return {"type": "session_accepted", "compatibilityKey": descriptor["compatibilityKey"]}

    if message_type == "command":
        command_id = payload.get("commandId")
        remote_slot = payload.get("remoteSlot")
        command = payload.get("command")
        if remote_slot is None or command is None:
            return {
                "type": "command_rejected",
                "commandId": command_id,
                "reason": "malformed-command",
                "gameInputSentByRelay": False,
            }
        if remote_slot != relay_check.EXPECTED_REMOTE_SLOT:
            return {
                "type": "command_rejected",
                "commandId": command_id,
                "reason": "remote-slot-not-allowed",
                "gameInputSentByRelay": False,
            }
        if command != relay_check.EXPECTED_REMOTE_COMMAND:
            return {
                "type": "command_rejected",
                "commandId": command_id,
                "reason": "command-not-allowed",
                "gameInputSentByRelay": False,
            }
        if payload.get("loopbackCommandId") != relay_check.EXPECTED_LOOPBACK_COMMAND_ID:
            return {
                "type": "command_rejected",
                "commandId": command_id,
                "reason": "loopback-command-mismatch",
                "gameInputSentByRelay": False,
            }
        return {
            "type": "command_accepted",
            "commandId": relay_check.EXPECTED_COMMAND_ID,
            "loopbackCommandId": relay_check.EXPECTED_LOOPBACK_COMMAND_ID,
            "gameInputSentByRelay": False,
        }

    return {"type": "message_rejected", "reason": "unknown-message-type", "gameInputSentByRelay": False}


def run_relay_session(descriptor: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    ready: queue.Queue[int] = queue.Queue()
    server_errors: queue.Queue[str] = queue.Queue()

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
                    response = handle_relay_message(payload, descriptor)
                    write_json_line(handle, response)
        except Exception as exc:  # pragma: no cover - surfaced through build failure
            server_errors.put(str(exc))
        finally:
            listener.close()

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    thread = threading.Thread(target=server_main, args=(listener,), daemon=True)
    thread.start()
    port = ready.get(timeout=5)

    events: list[dict[str, Any]] = [
        relay_check.make_event("server_bound", bindHost="127.0.0.1", actualBindPort=port)
    ]

    def exchange(handle: Any, client_kind: str, server_kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        write_json_line(handle, payload)
        events.append(relay_check.make_event(client_kind, payload))
        response = read_json_line(handle)
        extra: dict[str, Any] = {}
        if server_kind == "server_command_accepted":
            extra = {
                "commandId": response.get("commandId"),
                "loopbackCommandId": response.get("loopbackCommandId"),
                "gameInputSentByRelay": response.get("gameInputSentByRelay"),
            }
        events.append(relay_check.make_event(server_kind, response, **extra))
        return response

    session_hello = {
        "type": "session_hello",
        "protocolVersion": relay_check.EXPECTED_PROTOCOL,
        "compatibilityKey": descriptor["compatibilityKey"],
    }
    malformed = {
        "type": "command",
        "commandId": "local-relay-reject-malformed-0001",
    }
    wrong_slot = {
        "type": "command",
        "commandId": "local-relay-reject-p1-0001",
        "remoteSlot": "P1",
        "command": relay_check.EXPECTED_REMOTE_COMMAND,
    }
    accepted = {
        "type": "command",
        "commandId": relay_check.EXPECTED_COMMAND_ID,
        "remoteSlot": relay_check.EXPECTED_REMOTE_SLOT,
        "command": relay_check.EXPECTED_REMOTE_COMMAND,
        "loopbackCommandId": relay_check.EXPECTED_LOOPBACK_COMMAND_ID,
    }
    close = {"type": "close"}

    with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
        handle = client.makefile("rwb")
        require(exchange(handle, "client_session_hello", "server_session_accepted", session_hello).get("type") == "session_accepted", "relay session was not accepted")
        require(exchange(handle, "client_command_malformed", "server_command_rejected", malformed).get("reason") == "malformed-command", "malformed command was not rejected")
        require(exchange(handle, "client_command_wrong_slot", "server_command_rejected", wrong_slot).get("reason") == "remote-slot-not-allowed", "wrong-slot command was not rejected")
        require(exchange(handle, "client_command_p2_forward", "server_command_accepted", accepted).get("type") == "command_accepted", "P2 command was not accepted")
        write_json_line(handle, close)
        events.append(relay_check.make_event("client_close", close))

    thread.join(timeout=5)
    require(not thread.is_alive(), "relay server thread did not stop")
    if not server_errors.empty():
        raise RelayBundleBuildError(server_errors.get())
    events.append(relay_check.make_event("server_stopped"))

    relay = {
        "transport": relay_check.EXPECTED_TRANSPORT,
        "bindHost": "127.0.0.1",
        "actualBindPort": port,
        "networkScope": "local-host-only",
        "loopbackInterfaceOnly": True,
        "localTcpSocketOpened": True,
        "publicNetworkSocketsOpened": False,
        "lanRelayClaim": False,
        "matchmakingServerContacted": False,
        "publicMatchmakingClaim": False,
        "publicServerClaim": False,
        "nativeBeaNetcodeClaim": False,
        "natTraversalClaim": False,
        "antiCheatClaim": False,
        "deterministicSyncClaim": False,
        "twoClientParityClaim": False,
        "physicalGamepadClaim": False,
        "rebuildParityClaim": False,
        "gameInputSentByRelay": False,
    }
    transcript = {
        "transport": relay_check.EXPECTED_TRANSPORT,
        "protocolVersion": relay_check.EXPECTED_PROTOCOL,
        "sessionCompatibilityKey": descriptor["compatibilityKey"],
        "messageCount": 9,
        "events": events,
    }
    return relay, transcript


def build_bundle(loopback_proof_path: Path, output_path: Path) -> dict[str, Any]:
    loopback_proof_path = loopback_proof_path.resolve()
    loopback_check.validate_bundle(loopback_proof_path, expected_controller_configuration=1)
    loopback_bundle = read_json(loopback_proof_path)
    descriptor = make_descriptor(loopback_bundle, loopback_proof_path)
    relay, transcript = run_relay_session(descriptor)

    bundle = {
        "schemaVersion": relay_check.EXPECTED_SCHEMA,
        "generatedBy": relay_check.EXPECTED_HELPER,
        "helperVersion": relay_check.EXPECTED_HELPER_VERSION,
        "protocolVersion": relay_check.EXPECTED_PROTOCOL,
        "loopbackProofBundle": relative_path(output_path.parent, loopback_proof_path),
        "loopbackProofSha256": relay_check.sha256_file(loopback_proof_path),
        "sessionDescriptor": descriptor,
        "relay": relay,
        "commands": {
            "accepted": [
                {
                    "commandId": relay_check.EXPECTED_COMMAND_ID,
                    "remoteSlot": relay_check.EXPECTED_REMOTE_SLOT,
                    "command": relay_check.EXPECTED_REMOTE_COMMAND,
                    "loopbackCommandId": relay_check.EXPECTED_LOOPBACK_COMMAND_ID,
                    "relayAccepted": True,
                    "gameInputSentByRelay": False,
                    "inputCdbWindowIndex": 2,
                }
            ],
            "rejected": [
                {
                    "commandId": "local-relay-reject-malformed-0001",
                    "reason": "malformed-command",
                    "relayAccepted": False,
                    "gameInputSentByRelay": False,
                },
                {
                    "commandId": "local-relay-reject-p1-0001",
                    "remoteSlot": "P1",
                    "reason": "remote-slot-not-allowed",
                    "relayAccepted": False,
                    "gameInputSentByRelay": False,
                },
            ],
        },
        "relayTranscript": transcript,
        "claimBoundary": (
            "Local relay/session descriptor proof only. This proves a localhost TCP JSONL helper accepted one P2 "
            "command compatible with an existing copied-original-BEA loopback proof. It is not online play, matchmaking, "
            "public relay/server behavior, LAN proof, native BEA netcode, NAT traversal, anti-cheat, deterministic sync, "
            "rollback, two-client parity, physical gamepad proof, rebuild parity, or no-noticeable-difference online parity."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("loopback_proof", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    output_path = args.output or args.loopback_proof.with_name("local-relay-session-proof.json")
    build_bundle(args.loopback_proof, output_path.resolve())
    print(json.dumps({"bundle": str(output_path.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RelayBundleBuildError, loopback_check.LoopbackProofError, loopback_check.state_delta.ArtifactError) as exc:
        print(f"WinUI original-binary local relay session bundle build: FAIL: {exc}")
        raise SystemExit(2)
