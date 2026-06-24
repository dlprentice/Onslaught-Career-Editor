#!/usr/bin/env python3
"""Validate a local relay/session descriptor proof chained to a loopback P2 proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_loopback_p2_input_check as loopback


EXPECTED_SCHEMA = "winui-original-binary-local-relay-session.v1"
EXPECTED_DESCRIPTOR_SCHEMA = "winui-original-binary-local-session-descriptor.v1"
EXPECTED_TRANSPORT = "localhost-tcp-jsonl"
EXPECTED_PROTOCOL = "local-relay-input.v1"
EXPECTED_HELPER = "winui-original-binary-local-relay-helper"
EXPECTED_HELPER_VERSION = "local-relay-helper.v1"
EXPECTED_REMOTE_SLOT = "P2"
EXPECTED_REMOTE_COMMAND = "movement-forward"
EXPECTED_COMMAND_ID = "local-relay-p2-forward-0001"
EXPECTED_LOOPBACK_COMMAND_ID = "loopback-p2-forward-0001"


class RelayProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RelayProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_payload(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    require(candidate.is_file(), f"referenced proof bundle is missing: {candidate}")
    return candidate


def descriptor_compatibility_payload(descriptor: dict[str, Any]) -> dict[str, Any]:
    return {
        "cleanSpecimenSha256": str(descriptor.get("cleanSpecimenSha256") or "").lower(),
        "profileManifestSha256": str(descriptor.get("profileManifestSha256") or "").lower(),
        "patchKeys": list(descriptor.get("patchKeys") or []),
        "launchArguments": list(descriptor.get("launchArguments") or []),
        "levelId": descriptor.get("levelId"),
        "controllerConfiguration": descriptor.get("controllerConfiguration"),
        "remotePlayerSlot": descriptor.get("remotePlayerSlot"),
        "helperVersion": descriptor.get("helperVersion"),
        "protocolVersion": descriptor.get("protocolVersion"),
        "upstreamLoopbackProtocolVersion": descriptor.get("upstreamLoopbackProtocolVersion"),
        "upstreamLoopbackProofSha256": descriptor.get("upstreamLoopbackProofSha256"),
    }


def descriptor_compatibility_key(descriptor: dict[str, Any]) -> str:
    return sha256_payload(descriptor_compatibility_payload(descriptor))


def require_descriptor(descriptor: dict[str, Any], *, loopback_bundle: dict[str, Any], loopback_path: Path) -> dict[str, Any]:
    session = object_at(loopback_bundle, "session")
    accepted = list_at(object_at(loopback_bundle, "commands"), "accepted")[0]

    require(descriptor.get("schemaVersion") == EXPECTED_DESCRIPTOR_SCHEMA, "unexpected session descriptor schema")
    require(descriptor.get("helperName") == EXPECTED_HELPER, "unexpected relay helper name")
    require(descriptor.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected relay helper version")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected relay protocol version")
    require(descriptor.get("upstreamLoopbackProtocolVersion") == loopback.EXPECTED_PROTOCOL, "upstream loopback protocol mismatch")
    require(descriptor.get("upstreamLoopbackCommandId") == EXPECTED_LOOPBACK_COMMAND_ID, "wrong upstream loopback command id")
    require(descriptor.get("remotePlayerSlot") == EXPECTED_REMOTE_SLOT, "descriptor remote player slot mismatch")
    require(descriptor.get("allowedCommand") == EXPECTED_REMOTE_COMMAND, "descriptor allowed command mismatch")
    require(descriptor.get("mappedInputSequence") == loopback.EXPECTED_MAPPED_SEQUENCE, "descriptor mapped input sequence mismatch")
    require(descriptor.get("inputCdbWindowIndex") == 2, "descriptor must correlate to CDB input window 2")
    require(str(descriptor.get("cleanSpecimenSha256", "")).lower() == loopback.EXPECTED_CLEAN_SPECIMEN_SHA256, "descriptor clean specimen hash mismatch")
    require(str(descriptor.get("profileManifestSha256", "")).lower() == str(session.get("profileManifestSha256", "")).lower(), "descriptor manifest hash mismatch")
    require(descriptor.get("patchKeys") == session.get("patchKeys"), "descriptor patch keys mismatch")
    require(descriptor.get("launchArguments") == session.get("launchArguments"), "descriptor launch args mismatch")
    require(descriptor.get("levelId") == 850, "descriptor level must be 850")
    require(descriptor.get("controllerConfiguration") == 1, "descriptor controller configuration must be 1")
    require(str(descriptor.get("upstreamLoopbackProofSha256", "")).lower() == sha256_file(loopback_path), "upstream loopback proof hash mismatch")
    require(accepted.get("commandId") == EXPECTED_LOOPBACK_COMMAND_ID, "upstream accepted command mismatch")

    expected_key = descriptor_compatibility_key(descriptor)
    require(descriptor.get("compatibilityKey") == expected_key, "descriptor compatibility key mismatch")
    return {
        "compatibilityKey": expected_key,
        "cleanSpecimenSha256": descriptor["cleanSpecimenSha256"],
        "profileManifestSha256": descriptor["profileManifestSha256"],
        "launchArguments": descriptor["launchArguments"],
    }


def require_relay_contract(bundle: dict[str, Any]) -> dict[str, Any]:
    relay = object_at(bundle, "relay")
    require(relay.get("transport") == EXPECTED_TRANSPORT, "relay transport must be localhost-tcp-jsonl")
    require(relay.get("bindHost") == "127.0.0.1", "relay must bind only 127.0.0.1")
    require(relay.get("networkScope") == "local-host-only", "relay network scope must be local-host-only")
    require(relay.get("loopbackInterfaceOnly") is True, "relay must be loopback-interface-only")
    require(relay.get("localTcpSocketOpened") is True, "relay must prove a local TCP socket was opened")
    require(relay.get("publicNetworkSocketsOpened") is False, "relay must not open public network sockets")
    require(relay.get("lanRelayClaim") is False, "relay must not claim LAN relay")
    require(relay.get("matchmakingServerContacted") is False, "relay must not contact matchmaking")
    require(relay.get("publicMatchmakingClaim") is False, "relay must not claim public/private matchmaking")
    require(relay.get("publicServerClaim") is False, "relay must not claim public server behavior")
    require(relay.get("nativeBeaNetcodeClaim") is False, "relay must not claim native BEA netcode")
    require(relay.get("natTraversalClaim") is False, "relay must not claim NAT traversal")
    require(relay.get("antiCheatClaim") is False, "relay must not claim anti-cheat")
    require(relay.get("deterministicSyncClaim") is False, "relay must not claim deterministic sync")
    require(relay.get("twoClientParityClaim") is False, "relay must not claim two-client parity")
    require(relay.get("physicalGamepadClaim") is False, "relay must not claim physical gamepad behavior")
    require(relay.get("rebuildParityClaim") is False, "relay must not claim rebuild parity")
    require(relay.get("gameInputSentByRelay") is False, "relay proof must not claim the relay itself sent game input")
    port = relay.get("actualBindPort")
    require(isinstance(port, int) and 0 < port < 65536, "relay actualBindPort must be a TCP port")
    return relay


def require_commands(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    rejected = list_at(commands, "rejected")
    require(len(accepted) == 1, "relay proof expects exactly one accepted command")
    accepted_command = accepted[0]
    require(isinstance(accepted_command, dict), "accepted command row is not an object")
    require(accepted_command.get("commandId") == EXPECTED_COMMAND_ID, "unexpected relay command id")
    require(accepted_command.get("remoteSlot") == EXPECTED_REMOTE_SLOT, "accepted relay command slot mismatch")
    require(accepted_command.get("command") == EXPECTED_REMOTE_COMMAND, "accepted relay command mismatch")
    require(accepted_command.get("loopbackCommandId") == EXPECTED_LOOPBACK_COMMAND_ID, "accepted relay command loopback id mismatch")
    require(accepted_command.get("relayAccepted") is True, "accepted relay command was not accepted")
    require(accepted_command.get("gameInputSentByRelay") is False, "relay command must not claim direct game input")
    require(accepted_command.get("inputCdbWindowIndex") == 2, "relay command must correlate to CDB window 2")

    require(len(rejected) >= 2, "relay proof expects malformed and wrong-slot rejection rows")
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require("malformed-command" in reasons, "missing malformed-command relay rejection")
    require("remote-slot-not-allowed" in reasons, "missing wrong-slot relay rejection")
    for index, row in enumerate(rejected, start=1):
        require(isinstance(row, dict), f"rejected command row {index} is not an object")
        require(row.get("relayAccepted") is False, f"rejected command row {index} was accepted")
        require(row.get("gameInputSentByRelay") is False, f"rejected command row {index} sent game input")
    return accepted_command


def require_transcript(bundle: dict[str, Any], *, descriptor: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "relayTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "transcript protocol mismatch")
    require(transcript.get("sessionCompatibilityKey") == descriptor.get("compatibilityKey"), "transcript compatibility key mismatch")
    require(transcript.get("messageCount") == 9, "relay transcript should have nine wire messages")
    events = list_at(transcript, "events")
    expected_kinds = [
        "server_bound",
        "client_session_hello",
        "server_session_accepted",
        "client_command_malformed",
        "server_command_rejected",
        "client_command_wrong_slot",
        "server_command_rejected",
        "client_command_p2_forward",
        "server_command_accepted",
        "client_close",
        "server_stopped",
    ]
    actual_kinds = [row.get("kind") if isinstance(row, dict) else None for row in events]
    require(actual_kinds == expected_kinds, "relay transcript event sequence mismatch")

    for index, row in enumerate(events, start=1):
        require(isinstance(row, dict), f"relay transcript event {index} is not an object")
        if row["kind"].startswith("client_") or row["kind"].startswith("server_"):
            if row["kind"] not in {"server_bound", "server_stopped"}:
                payload_sha = str(row.get("payloadSha256") or "")
                payload_bytes = row.get("payloadBytes")
                require(len(payload_sha) == 64, f"event {index} missing payload sha")
                require(isinstance(payload_bytes, int) and payload_bytes > 0, f"event {index} missing payload byte count")

    accepted = events[8]
    require(accepted.get("commandId") == EXPECTED_COMMAND_ID, "accepted transcript command id mismatch")
    require(accepted.get("loopbackCommandId") == EXPECTED_LOOPBACK_COMMAND_ID, "accepted transcript loopback id mismatch")
    require(accepted.get("gameInputSentByRelay") is False, "accepted transcript must not claim direct game input")
    return {"eventCount": len(events), "messageCount": transcript["messageCount"]}


def validate_bundle(path: Path, *, expected_controller_configuration: int) -> dict[str, Any]:
    bundle = read_json(path)
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected relay proof schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected relay proof generator")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected protocol version")

    loopback_path = resolve_artifact_path(path, str(bundle.get("loopbackProofBundle", "")))
    loopback_summary = loopback.validate_bundle(
        loopback_path,
        expected_controller_configuration=expected_controller_configuration,
    )
    loopback_bundle = read_json(loopback_path)

    descriptor = object_at(bundle, "sessionDescriptor")
    descriptor_summary = require_descriptor(descriptor, loopback_bundle=loopback_bundle, loopback_path=loopback_path)
    relay = require_relay_contract(bundle)
    accepted_command = require_commands(bundle)
    transcript_summary = require_transcript(bundle, descriptor=descriptor)

    return {
        "artifact": str(path),
        "loopbackProofBundle": str(loopback_path),
        "claim": "localhost TCP JSONL relay/session descriptor accepted one P2 command compatible with the prior copied-BEA loopback proof",
        "transport": relay["transport"],
        "bindHost": relay["bindHost"],
        "actualBindPort": relay["actualBindPort"],
        "helperVersion": bundle["helperVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "acceptedCommandId": accepted_command["commandId"],
        "upstreamLoopbackCommandId": accepted_command["loopbackCommandId"],
        "descriptor": descriptor_summary,
        "transcript": transcript_summary,
        "loopbackDelivery": loopback_summary["delivery"],
        "claimBoundary": (
            "This proves only a localhost TCP JSONL relay/session descriptor and command-acceptance boundary chained "
            "to an existing safe copied original-BEA loopback P2 input proof. It does not prove LAN transport, public "
            "matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, anti-cheat, "
            "dual-binary parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_descriptor(loopback_bundle: dict[str, Any], loopback_path: Path) -> dict[str, Any]:
    session = object_at(loopback_bundle, "session")
    descriptor = {
        "schemaVersion": EXPECTED_DESCRIPTOR_SCHEMA,
        "helperName": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "cleanSpecimenSha256": loopback.EXPECTED_CLEAN_SPECIMEN_SHA256,
        "profileManifestSha256": session["profileManifestSha256"],
        "patchKeys": session["patchKeys"],
        "launchArguments": session["launchArguments"],
        "levelId": 850,
        "controllerConfiguration": 1,
        "remotePlayerSlot": EXPECTED_REMOTE_SLOT,
        "allowedCommand": EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": loopback.EXPECTED_MAPPED_SEQUENCE,
        "inputCdbWindowIndex": 2,
        "upstreamLoopbackProtocolVersion": loopback.EXPECTED_PROTOCOL,
        "upstreamLoopbackCommandId": EXPECTED_LOOPBACK_COMMAND_ID,
        "upstreamLoopbackProofSha256": sha256_file(loopback_path),
    }
    descriptor["compatibilityKey"] = descriptor_compatibility_key(descriptor)
    descriptor["descriptorId"] = descriptor["compatibilityKey"][:16]
    return descriptor


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


def make_bundle_fixture(root: Path, *, wrong_host: bool = False, wrong_key: bool = False, direct_input_claim: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "loopback").mkdir(parents=True, exist_ok=True)
    loopback_path = loopback.make_bundle_fixture(root / "loopback")
    loopback_bundle = read_json(loopback_path)
    descriptor = make_descriptor(loopback_bundle, loopback_path)
    if wrong_key:
        descriptor["compatibilityKey"] = "0" * 64

    session_hello = {
        "type": "session_hello",
        "protocolVersion": EXPECTED_PROTOCOL,
        "compatibilityKey": descriptor["compatibilityKey"],
    }
    session_accepted = {"type": "session_accepted", "compatibilityKey": descriptor["compatibilityKey"]}
    malformed = {"type": "command", "commandId": "local-relay-reject-malformed-0001"}
    malformed_rejected = {"type": "command_rejected", "reason": "malformed-command"}
    wrong_slot = {
        "type": "command",
        "commandId": "local-relay-reject-p1-0001",
        "remoteSlot": "P1",
        "command": EXPECTED_REMOTE_COMMAND,
    }
    wrong_slot_rejected = {"type": "command_rejected", "reason": "remote-slot-not-allowed"}
    accepted = {
        "type": "command",
        "commandId": EXPECTED_COMMAND_ID,
        "remoteSlot": EXPECTED_REMOTE_SLOT,
        "command": EXPECTED_REMOTE_COMMAND,
        "loopbackCommandId": EXPECTED_LOOPBACK_COMMAND_ID,
    }
    accepted_reply = {
        "type": "command_accepted",
        "commandId": EXPECTED_COMMAND_ID,
        "loopbackCommandId": EXPECTED_LOOPBACK_COMMAND_ID,
        "gameInputSentByRelay": direct_input_claim,
    }
    close = {"type": "close"}

    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "loopbackProofBundle": str(loopback_path),
        "loopbackProofSha256": sha256_file(loopback_path),
        "sessionDescriptor": descriptor,
        "relay": {
            "transport": EXPECTED_TRANSPORT,
            "bindHost": "0.0.0.0" if wrong_host else "127.0.0.1",
            "actualBindPort": 49152,
            "networkScope": "local-host-only",
            "loopbackInterfaceOnly": not wrong_host,
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
            "gameInputSentByRelay": direct_input_claim,
        },
        "commands": {
            "accepted": [
                {
                    "commandId": EXPECTED_COMMAND_ID,
                    "remoteSlot": EXPECTED_REMOTE_SLOT,
                    "command": EXPECTED_REMOTE_COMMAND,
                    "loopbackCommandId": EXPECTED_LOOPBACK_COMMAND_ID,
                    "relayAccepted": True,
                    "gameInputSentByRelay": direct_input_claim,
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
        "relayTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "sessionCompatibilityKey": descriptor["compatibilityKey"],
            "messageCount": 9,
            "events": [
                make_event("server_bound", bindHost="127.0.0.1", actualBindPort=49152),
                make_event("client_session_hello", session_hello),
                make_event("server_session_accepted", session_accepted),
                make_event("client_command_malformed", malformed),
                make_event("server_command_rejected", malformed_rejected),
                make_event("client_command_wrong_slot", wrong_slot),
                make_event("server_command_rejected", wrong_slot_rejected),
                make_event("client_command_p2_forward", accepted),
                make_event("server_command_accepted", accepted_reply, commandId=EXPECTED_COMMAND_ID, loopbackCommandId=EXPECTED_LOOPBACK_COMMAND_ID, gameInputSentByRelay=direct_input_claim),
                make_event("client_close", close),
                make_event("server_stopped"),
            ],
        },
    }
    bundle_path = root / "local-relay-session-proof.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_bundle(make_bundle_fixture(Path(tmp)), expected_controller_configuration=1)
        require(summary["transport"] == EXPECTED_TRANSPORT, "fixture transport mismatch")
        require(summary["acceptedCommandId"] == EXPECTED_COMMAND_ID, "fixture command mismatch")

    for label, kwargs in (
        ("wrong host should fail", {"wrong_host": True}),
        ("wrong compatibility key should fail", {"wrong_key": True}),
        ("direct input claim should fail", {"direct_input_claim": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs), expected_controller_configuration=1)
            except (RelayProofError, loopback.LoopbackProofError):
                pass
            else:
                raise RelayProofError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary local relay session checker self-test: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    summary = validate_bundle(args.bundle, expected_controller_configuration=args.expected_controller_configuration)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RelayProofError, loopback.LoopbackProofError, loopback.state_delta.ArtifactError) as exc:
        print(f"WinUI original-binary local relay session check: FAIL: {exc}")
        raise SystemExit(2)
