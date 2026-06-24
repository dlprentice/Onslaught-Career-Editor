#!/usr/bin/env python3
"""Validate a private relay-delivery adapter proof chained to local relay/session evidence."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_local_relay_session_check as relay
import winui_safe_copy_online_loopback_p2_input_check as loopback


EXPECTED_SCHEMA = "winui-original-binary-private-relay-delivery.v1"
EXPECTED_TRANSPORT = "localhost-relay-host-helper-adapter"
EXPECTED_PROTOCOL = "private-relay-delivery.v1"
EXPECTED_HELPER = "winui-original-binary-private-relay-delivery-helper"
EXPECTED_HELPER_VERSION = "private-relay-delivery-helper.v1"
EXPECTED_ADAPTER = "safe-copy-host-helper-delivery-adapter"
EXPECTED_ADAPTER_VERSION = "host-helper-delivery-adapter.v1"
EXPECTED_PRIVATE_COMMAND_ID = "private-relay-p2-forward-0001"
EXPECTED_RELAY_COMMAND_ID = relay.EXPECTED_COMMAND_ID
EXPECTED_LOOPBACK_COMMAND_ID = relay.EXPECTED_LOOPBACK_COMMAND_ID


class PrivateRelayDeliveryProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateRelayDeliveryProofError(message)


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
    require(candidate.is_file(), f"referenced relay proof bundle is missing: {candidate}")
    return candidate


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected private relay delivery schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected private relay delivery helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected private relay delivery helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected private relay delivery protocol")


def require_host_helper_adapter(
    bundle: dict[str, Any],
    *,
    local_relay_summary: dict[str, Any],
    local_relay_bundle: dict[str, Any],
    local_relay_path: Path,
) -> dict[str, Any]:
    adapter = object_at(bundle, "hostHelperAdapter")
    descriptor = object_at(local_relay_bundle, "sessionDescriptor")
    relay_contract = object_at(local_relay_bundle, "relay")
    loopback_path = resolve_artifact_path(local_relay_path, str(local_relay_bundle.get("loopbackProofBundle", "")))
    loopback_bundle = read_json(loopback_path)
    live_path = loopback.resolve_artifact_path(loopback_path, str(loopback_bundle.get("liveRuntimeArtifact", "")))

    require(adapter.get("adapterName") == EXPECTED_ADAPTER, "unexpected host-helper adapter name")
    require(adapter.get("adapterVersion") == EXPECTED_ADAPTER_VERSION, "unexpected host-helper adapter version")
    require(adapter.get("deliveryTransport") == EXPECTED_TRANSPORT, "unexpected delivery transport")
    require(adapter.get("inputDeliverySurface") == "safe-copy-host-helper", "unexpected input delivery surface")
    require(adapter.get("deliveryMode") == "relay-command-to-existing-loopback-p2-route", "unexpected delivery mode")
    require(adapter.get("relayProofSha256") == relay.sha256_file(local_relay_path), "local relay proof hash mismatch")
    require(adapter.get("relayProofSchema") == relay.EXPECTED_SCHEMA, "local relay schema mismatch")
    require(adapter.get("upstreamLoopbackProofBundle") == str(loopback_path), "upstream loopback proof path mismatch")
    require(adapter.get("upstreamLoopbackProofSha256") == relay.sha256_file(loopback_path), "upstream loopback proof hash mismatch")
    require(adapter.get("hostHelperLiveRuntimeArtifact") == str(live_path), "host-helper live artifact path mismatch")
    require(adapter.get("hostHelperLiveRuntimeArtifactSha256") == relay.sha256_file(live_path), "host-helper live artifact hash mismatch")
    require(adapter.get("relayTransport") == relay.EXPECTED_TRANSPORT, "local relay transport mismatch")
    require(adapter.get("relayBindHost") == "127.0.0.1", "relay bind host must stay localhost")
    require(adapter.get("sessionCompatibilityKey") == descriptor.get("compatibilityKey"), "adapter compatibility key mismatch")
    require(adapter.get("localRelayAcceptedCommandId") == EXPECTED_RELAY_COMMAND_ID, "wrong relay accepted command id")
    require(adapter.get("upstreamLoopbackCommandId") == EXPECTED_LOOPBACK_COMMAND_ID, "wrong upstream loopback command id")
    require(adapter.get("mappedInputSequence") == loopback.EXPECTED_MAPPED_SEQUENCE, "wrong mapped input sequence")
    require(adapter.get("inputCdbWindowIndex") == 2, "adapter must correlate to CDB input window 2")
    require(adapter.get("remotePlayerSlot") == relay.EXPECTED_REMOTE_SLOT, "adapter must target P2")
    require(adapter.get("command") == relay.EXPECTED_REMOTE_COMMAND, "adapter command mismatch")
    require(adapter.get("cleanSpecimenSha256") == loopback.EXPECTED_CLEAN_SPECIMEN_SHA256, "clean specimen hash mismatch")
    require(adapter.get("levelId") == 850, "adapter must target level 850")
    require(adapter.get("controllerConfiguration") == 1, "adapter controller configuration must be 1")
    require(adapter.get("networkScope") == "local-private-only", "adapter network scope must be local-private-only")
    require(adapter.get("loopbackInterfaceOnly") is True, "adapter must remain loopback-interface-only")
    require(adapter.get("publicNetworkSocketsOpened") is False, "adapter must not open public sockets")
    require(adapter.get("lanDeliveryClaim") is False, "adapter must not claim LAN delivery")
    require(adapter.get("publicMatchmakingClaim") is False, "adapter must not claim public matchmaking")
    require(adapter.get("matchmakingServerContacted") is False, "adapter must not contact matchmaking")
    require(adapter.get("publicServerClaim") is False, "adapter must not claim public server behavior")
    require(adapter.get("nativeBeaNetcodeClaim") is False, "adapter must not claim native BEA netcode")
    require(adapter.get("natTraversalClaim") is False, "adapter must not claim NAT traversal")
    require(adapter.get("antiCheatClaim") is False, "adapter must not claim anti-cheat")
    require(adapter.get("deterministicSyncClaim") is False, "adapter must not claim deterministic sync")
    require(adapter.get("rollbackClaim") is False, "adapter must not claim rollback")
    require(adapter.get("twoClientParityClaim") is False, "adapter must not claim two-client parity")
    require(adapter.get("physicalGamepadClaim") is False, "adapter must not claim physical gamepad behavior")
    require(adapter.get("rebuildParityClaim") is False, "adapter must not claim rebuild parity")
    require(adapter.get("relaySideGameInputSent") is False, "relay side must not claim direct game input")
    require(adapter.get("hostHelperInputSent") is True, "host helper must send focused input in this proof")
    require(adapter.get("hostHelperInputEvidence") == "fresh-live-runtime-cdb-proof", "unexpected host-helper input evidence")
    require(adapter.get("gameInputDeliveryEvidence") == "fresh-host-helper-cdb-proof", "unexpected game-input evidence boundary")
    require(local_relay_summary["acceptedCommandId"] == EXPECTED_RELAY_COMMAND_ID, "validated relay command mismatch")
    require(relay_contract.get("gameInputSentByRelay") is False, "relay proof must not claim direct game input")
    return adapter


def require_delivery_commands(bundle: dict[str, Any], *, adapter: dict[str, Any]) -> dict[str, Any]:
    delivery = object_at(bundle, "delivery")
    accepted = list_at(delivery, "accepted")
    rejected = list_at(delivery, "rejected")
    require(len(accepted) == 1, "private relay delivery expects exactly one accepted delivery")
    accepted_command = accepted[0]
    require(isinstance(accepted_command, dict), "accepted delivery row is not an object")
    require(accepted_command.get("commandId") == EXPECTED_PRIVATE_COMMAND_ID, "unexpected private relay command id")
    require(accepted_command.get("relayCommandId") == EXPECTED_RELAY_COMMAND_ID, "accepted delivery relay command mismatch")
    require(accepted_command.get("upstreamLoopbackCommandId") == EXPECTED_LOOPBACK_COMMAND_ID, "accepted delivery upstream command mismatch")
    require(accepted_command.get("remoteSlot") == relay.EXPECTED_REMOTE_SLOT, "accepted delivery slot mismatch")
    require(accepted_command.get("command") == relay.EXPECTED_REMOTE_COMMAND, "accepted delivery command mismatch")
    require(accepted_command.get("mappedInputSequence") == loopback.EXPECTED_MAPPED_SEQUENCE, "accepted delivery sequence mismatch")
    require(accepted_command.get("inputCdbWindowIndex") == 2, "accepted delivery must correlate to CDB window 2")
    require(accepted_command.get("relayAccepted") is True, "delivery did not accept the relay command")
    require(accepted_command.get("hostHelperDeliveryAccepted") is True, "host helper did not accept delivery")
    require(accepted_command.get("relaySideGameInputSent") is False, "accepted delivery must not claim relay-side game input")
    require(accepted_command.get("hostHelperInputSent") is True, "accepted delivery must record host-helper input")
    require(accepted_command.get("hostHelperInputEvidence") == adapter.get("hostHelperInputEvidence"), "host-helper input evidence mismatch")
    require(accepted_command.get("gameInputDeliveryEvidence") == adapter.get("gameInputDeliveryEvidence"), "delivery evidence mismatch")

    require(len(rejected) >= 3, "private relay delivery expects malformed/P1/compatibility rejection rows")
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require("malformed-delivery-command" in reasons, "missing malformed delivery rejection")
    require("remote-slot-not-allowed" in reasons, "missing P1 delivery rejection")
    require("session-compatibility-mismatch" in reasons, "missing compatibility-key rejection")
    for index, row in enumerate(rejected, start=1):
        require(isinstance(row, dict), f"rejected delivery row {index} is not an object")
        require(row.get("hostHelperDeliveryAccepted") is False, f"rejected delivery row {index} was accepted")
        require(row.get("relaySideGameInputSent") is False, f"rejected delivery row {index} sent relay-side game input")
        require(row.get("hostHelperInputSent") is False, f"rejected delivery row {index} sent host-helper input")
    return accepted_command


def require_transcript(bundle: dict[str, Any], *, adapter: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "adapterTranscript")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "adapter transcript protocol mismatch")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "adapter transcript transport mismatch")
    require(transcript.get("sessionCompatibilityKey") == adapter.get("sessionCompatibilityKey"), "adapter transcript compatibility key mismatch")
    require(transcript.get("messageCount") == 8, "adapter transcript should have eight logical messages")
    events = list_at(transcript, "events")
    expected_kinds = [
        "adapter_initialized",
        "relay_session_verified",
        "relay_command_received",
        "host_helper_delivery_accepted",
        "delivery_command_malformed_rejected",
        "delivery_command_wrong_slot_rejected",
        "delivery_command_wrong_compatibility_rejected",
        "adapter_closed",
    ]
    actual_kinds = [row.get("kind") if isinstance(row, dict) else None for row in events]
    require(actual_kinds == expected_kinds, "adapter transcript event sequence mismatch")
    accepted = events[3]
    require(accepted.get("commandId") == EXPECTED_PRIVATE_COMMAND_ID, "transcript accepted command mismatch")
    require(accepted.get("relayCommandId") == EXPECTED_RELAY_COMMAND_ID, "transcript relay command mismatch")
    require(accepted.get("hostHelperDeliveryAccepted") is True, "transcript missing host-helper accepted row")
    require(accepted.get("relaySideGameInputSent") is False, "transcript must not claim relay-side game input")
    require(accepted.get("hostHelperInputSent") is True, "transcript missing host-helper input")
    return {"eventCount": len(events), "messageCount": transcript["messageCount"]}


def validate_bundle(path: Path, *, expected_controller_configuration: int) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)

    local_relay_path = resolve_artifact_path(path, str(bundle.get("localRelayProofBundle", "")))
    require(str(bundle.get("localRelayProofSha256", "")).lower() == relay.sha256_file(local_relay_path), "local relay proof bundle hash mismatch")
    local_relay_summary = relay.validate_bundle(
        local_relay_path,
        expected_controller_configuration=expected_controller_configuration,
    )
    local_relay_bundle = read_json(local_relay_path)

    adapter = require_host_helper_adapter(
        bundle,
        local_relay_summary=local_relay_summary,
        local_relay_bundle=local_relay_bundle,
        local_relay_path=local_relay_path,
    )
    accepted_command = require_delivery_commands(bundle, adapter=adapter)
    transcript_summary = require_transcript(bundle, adapter=adapter)

    return {
        "artifact": str(path),
        "localRelayProofBundle": str(local_relay_path),
        "claim": "private/local relay-delivery adapter accepted one P2 command into the safe-copy host-helper path proven by upstream loopback CDB evidence",
        "transport": adapter["deliveryTransport"],
        "helperVersion": bundle["helperVersion"],
        "adapterVersion": adapter["adapterVersion"],
        "acceptedCommandId": accepted_command["commandId"],
        "relayCommandId": accepted_command["relayCommandId"],
        "upstreamLoopbackCommandId": accepted_command["upstreamLoopbackCommandId"],
        "remoteSlot": accepted_command["remoteSlot"],
        "mappedInputSequence": accepted_command["mappedInputSequence"],
        "relaySideGameInputSent": accepted_command["relaySideGameInputSent"],
        "hostHelperInputSent": accepted_command["hostHelperInputSent"],
        "gameInputDeliveryEvidence": accepted_command["gameInputDeliveryEvidence"],
        "localRelay": {
            "acceptedCommandId": local_relay_summary["acceptedCommandId"],
            "transport": local_relay_summary["transport"],
            "bindHost": local_relay_summary["bindHost"],
        },
        "upstreamLoopbackDelivery": local_relay_summary["loopbackDelivery"],
        "transcript": transcript_summary,
        "claimBoundary": (
            "This proves only a local/private relay-delivery adapter contract chained to a localhost relay proof and "
            "the existing copied original-BEA loopback P2 CDB proof. It does not prove LAN transport, public matchmaking, "
            "public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, "
            "dual-binary parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_event(kind: str, **extra: Any) -> dict[str, Any]:
    event = {"kind": kind}
    event.update(extra)
    return event


def make_bundle_fixture(
    root: Path,
    *,
    wrong_hash: bool = False,
    direct_input_claim: bool = False,
    host_helper_input_missing: bool = False,
    public_matchmaking_claim: bool = False,
    wrong_compatibility: bool = False,
    p1_accepted: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    local_relay_path = relay.make_bundle_fixture(root / "local-relay")
    local_relay_bundle = read_json(local_relay_path)
    descriptor = object_at(local_relay_bundle, "sessionDescriptor")
    loopback_path = resolve_artifact_path(local_relay_path, str(local_relay_bundle.get("loopbackProofBundle", "")))
    loopback_bundle = read_json(loopback_path)
    live_path = loopback.resolve_artifact_path(loopback_path, str(loopback_bundle.get("liveRuntimeArtifact", "")))
    compatibility_key = "0" * 64 if wrong_compatibility else descriptor["compatibilityKey"]
    local_relay_hash = relay.sha256_file(local_relay_path)
    adapter = {
        "adapterName": EXPECTED_ADAPTER,
        "adapterVersion": EXPECTED_ADAPTER_VERSION,
        "deliveryTransport": EXPECTED_TRANSPORT,
        "inputDeliverySurface": "safe-copy-host-helper",
        "deliveryMode": "relay-command-to-existing-loopback-p2-route",
        "relayProofSha256": ("1" * 64 if wrong_hash else local_relay_hash),
        "relayProofSchema": relay.EXPECTED_SCHEMA,
        "upstreamLoopbackProofBundle": str(loopback_path),
        "upstreamLoopbackProofSha256": relay.sha256_file(loopback_path),
        "hostHelperLiveRuntimeArtifact": str(live_path),
        "hostHelperLiveRuntimeArtifactSha256": relay.sha256_file(live_path),
        "relayTransport": relay.EXPECTED_TRANSPORT,
        "relayBindHost": "127.0.0.1",
        "sessionCompatibilityKey": compatibility_key,
        "localRelayAcceptedCommandId": EXPECTED_RELAY_COMMAND_ID,
        "upstreamLoopbackCommandId": EXPECTED_LOOPBACK_COMMAND_ID,
        "mappedInputSequence": loopback.EXPECTED_MAPPED_SEQUENCE,
        "inputCdbWindowIndex": 2,
        "remotePlayerSlot": "P1" if p1_accepted else relay.EXPECTED_REMOTE_SLOT,
        "command": relay.EXPECTED_REMOTE_COMMAND,
        "cleanSpecimenSha256": loopback.EXPECTED_CLEAN_SPECIMEN_SHA256,
        "levelId": 850,
        "controllerConfiguration": 1,
        "networkScope": "local-private-only",
        "loopbackInterfaceOnly": True,
        "publicNetworkSocketsOpened": False,
        "lanDeliveryClaim": False,
        "publicMatchmakingClaim": public_matchmaking_claim,
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
        "relaySideGameInputSent": direct_input_claim,
        "hostHelperInputSent": not host_helper_input_missing,
        "hostHelperInputEvidence": "fresh-live-runtime-cdb-proof",
        "gameInputDeliveryEvidence": "fresh-host-helper-cdb-proof",
    }
    accepted = {
        "commandId": EXPECTED_PRIVATE_COMMAND_ID,
        "relayCommandId": EXPECTED_RELAY_COMMAND_ID,
        "upstreamLoopbackCommandId": EXPECTED_LOOPBACK_COMMAND_ID,
        "remoteSlot": adapter["remotePlayerSlot"],
        "command": relay.EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": loopback.EXPECTED_MAPPED_SEQUENCE,
        "inputCdbWindowIndex": 2,
        "relayAccepted": True,
        "hostHelperDeliveryAccepted": True,
        "relaySideGameInputSent": direct_input_claim,
        "hostHelperInputSent": not host_helper_input_missing,
        "hostHelperInputEvidence": "fresh-live-runtime-cdb-proof",
        "gameInputDeliveryEvidence": "fresh-host-helper-cdb-proof",
    }
    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "localRelayProofBundle": str(local_relay_path),
        "localRelayProofSha256": local_relay_hash,
        "hostHelperAdapter": adapter,
        "delivery": {
            "accepted": [accepted],
            "rejected": [
                {
                    "commandId": "private-relay-reject-malformed-0001",
                    "reason": "malformed-delivery-command",
                    "hostHelperDeliveryAccepted": False,
                    "relaySideGameInputSent": False,
                    "hostHelperInputSent": False,
                },
                {
                    "commandId": "private-relay-reject-p1-0001",
                    "remoteSlot": "P1",
                    "reason": "remote-slot-not-allowed",
                    "hostHelperDeliveryAccepted": False,
                    "relaySideGameInputSent": False,
                    "hostHelperInputSent": False,
                },
                {
                    "commandId": "private-relay-reject-compatibility-0001",
                    "reason": "session-compatibility-mismatch",
                    "hostHelperDeliveryAccepted": False,
                    "relaySideGameInputSent": False,
                    "hostHelperInputSent": False,
                },
            ],
        },
        "adapterTranscript": {
            "protocolVersion": EXPECTED_PROTOCOL,
            "transport": EXPECTED_TRANSPORT,
            "sessionCompatibilityKey": compatibility_key,
            "messageCount": 8,
            "events": [
                make_event("adapter_initialized", adapterName=EXPECTED_ADAPTER, adapterVersion=EXPECTED_ADAPTER_VERSION),
                make_event("relay_session_verified", compatibilityKey=compatibility_key),
                make_event("relay_command_received", relayCommandId=EXPECTED_RELAY_COMMAND_ID),
                make_event("host_helper_delivery_accepted", commandId=EXPECTED_PRIVATE_COMMAND_ID, relayCommandId=EXPECTED_RELAY_COMMAND_ID, hostHelperDeliveryAccepted=True, relaySideGameInputSent=direct_input_claim, hostHelperInputSent=not host_helper_input_missing),
                make_event("delivery_command_malformed_rejected", reason="malformed-delivery-command"),
                make_event("delivery_command_wrong_slot_rejected", reason="remote-slot-not-allowed"),
                make_event("delivery_command_wrong_compatibility_rejected", reason="session-compatibility-mismatch"),
                make_event("adapter_closed"),
            ],
        },
    }
    bundle_path = root / "private-relay-delivery-proof.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_bundle(make_bundle_fixture(Path(tmp)), expected_controller_configuration=1)
        require(summary["acceptedCommandId"] == EXPECTED_PRIVATE_COMMAND_ID, "fixture command mismatch")
        require(summary["relaySideGameInputSent"] is False, "fixture should not claim relay-side input")
        require(summary["hostHelperInputSent"] is True, "fixture should prove host-helper input")

    for label, kwargs in (
        ("wrong local relay hash should fail", {"wrong_hash": True}),
        ("relay-side input claim should fail", {"direct_input_claim": True}),
        ("missing host-helper input should fail", {"host_helper_input_missing": True}),
        ("public matchmaking claim should fail", {"public_matchmaking_claim": True}),
        ("wrong compatibility should fail", {"wrong_compatibility": True}),
        ("P1 accepted delivery should fail", {"p1_accepted": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs), expected_controller_configuration=1)
            except (PrivateRelayDeliveryProofError, relay.RelayProofError, loopback.LoopbackProofError, loopback.state_delta.ArtifactError):
                pass
            else:
                raise PrivateRelayDeliveryProofError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--expected-controller-configuration", type=int, default=1, choices=(1, 2, 3, 4))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary private relay delivery checker self-test: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    summary = validate_bundle(args.bundle, expected_controller_configuration=args.expected_controller_configuration)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PrivateRelayDeliveryProofError, relay.RelayProofError, loopback.LoopbackProofError, loopback.state_delta.ArtifactError) as exc:
        print(f"WinUI original-binary private relay delivery check: FAIL: {exc}")
        raise SystemExit(2)
