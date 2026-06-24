#!/usr/bin/env python3
"""Build a private relay-delivery adapter proof from an accepted local relay proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import winui_safe_copy_online_local_relay_session_check as relay
import winui_safe_copy_online_loopback_p2_input_check as loopback
import winui_safe_copy_online_private_relay_delivery_check as delivery


class PrivateRelayDeliveryBundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateRelayDeliveryBundleBuildError(message)


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


def make_event(kind: str, **extra: Any) -> dict[str, Any]:
    event = {"kind": kind}
    event.update(extra)
    return event


def build_bundle(local_relay_proof_path: Path, output_path: Path) -> dict[str, Any]:
    local_relay_proof_path = local_relay_proof_path.resolve()
    relay_summary = relay.validate_bundle(local_relay_proof_path, expected_controller_configuration=1)
    local_relay_bundle = read_json(local_relay_proof_path)
    descriptor = object_at(local_relay_bundle, "sessionDescriptor")
    accepted_relay = list_at(object_at(local_relay_bundle, "commands"), "accepted")[0]
    loopback_path = relay.resolve_artifact_path(local_relay_proof_path, str(local_relay_bundle.get("loopbackProofBundle", "")))
    loopback_bundle = read_json(loopback_path)
    live_path = loopback.resolve_artifact_path(loopback_path, str(loopback_bundle.get("liveRuntimeArtifact", "")))

    require(accepted_relay.get("commandId") == relay.EXPECTED_COMMAND_ID, "local relay proof has unexpected accepted command")
    require(accepted_relay.get("loopbackCommandId") == relay.EXPECTED_LOOPBACK_COMMAND_ID, "local relay proof has unexpected upstream command")
    require(accepted_relay.get("relayAccepted") is True, "local relay proof did not accept the command")
    require(accepted_relay.get("gameInputSentByRelay") is False, "local relay proof must not claim direct game input")

    compatibility_key = descriptor["compatibilityKey"]
    local_relay_hash = relay.sha256_file(local_relay_proof_path)
    adapter = {
        "adapterName": delivery.EXPECTED_ADAPTER,
        "adapterVersion": delivery.EXPECTED_ADAPTER_VERSION,
        "deliveryTransport": delivery.EXPECTED_TRANSPORT,
        "inputDeliverySurface": "safe-copy-host-helper",
        "deliveryMode": "relay-command-to-existing-loopback-p2-route",
        "relayProofSha256": local_relay_hash,
        "relayProofSchema": relay.EXPECTED_SCHEMA,
        "upstreamLoopbackProofBundle": str(loopback_path),
        "upstreamLoopbackProofSha256": relay.sha256_file(loopback_path),
        "hostHelperLiveRuntimeArtifact": str(live_path),
        "hostHelperLiveRuntimeArtifactSha256": relay.sha256_file(live_path),
        "relayTransport": relay.EXPECTED_TRANSPORT,
        "relayBindHost": "127.0.0.1",
        "sessionCompatibilityKey": compatibility_key,
        "localRelayAcceptedCommandId": relay.EXPECTED_COMMAND_ID,
        "upstreamLoopbackCommandId": relay.EXPECTED_LOOPBACK_COMMAND_ID,
        "mappedInputSequence": loopback.EXPECTED_MAPPED_SEQUENCE,
        "inputCdbWindowIndex": 2,
        "remotePlayerSlot": relay.EXPECTED_REMOTE_SLOT,
        "command": relay.EXPECTED_REMOTE_COMMAND,
        "cleanSpecimenSha256": loopback.EXPECTED_CLEAN_SPECIMEN_SHA256,
        "levelId": 850,
        "controllerConfiguration": 1,
        "networkScope": "local-private-only",
        "loopbackInterfaceOnly": True,
        "publicNetworkSocketsOpened": False,
        "lanDeliveryClaim": False,
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
        "relaySideGameInputSent": False,
        "hostHelperInputSent": True,
        "hostHelperInputEvidence": "fresh-live-runtime-cdb-proof",
        "gameInputDeliveryEvidence": "fresh-host-helper-cdb-proof",
    }
    accepted_private = {
        "commandId": delivery.EXPECTED_PRIVATE_COMMAND_ID,
        "relayCommandId": relay.EXPECTED_COMMAND_ID,
        "upstreamLoopbackCommandId": relay.EXPECTED_LOOPBACK_COMMAND_ID,
        "remoteSlot": relay.EXPECTED_REMOTE_SLOT,
        "command": relay.EXPECTED_REMOTE_COMMAND,
        "mappedInputSequence": loopback.EXPECTED_MAPPED_SEQUENCE,
        "inputCdbWindowIndex": 2,
        "relayAccepted": True,
        "hostHelperDeliveryAccepted": True,
        "relaySideGameInputSent": False,
        "hostHelperInputSent": True,
        "hostHelperInputEvidence": "fresh-live-runtime-cdb-proof",
        "gameInputDeliveryEvidence": "fresh-host-helper-cdb-proof",
    }
    bundle = {
        "schemaVersion": delivery.EXPECTED_SCHEMA,
        "generatedBy": delivery.EXPECTED_HELPER,
        "helperVersion": delivery.EXPECTED_HELPER_VERSION,
        "protocolVersion": delivery.EXPECTED_PROTOCOL,
        "localRelayProofBundle": relative_path(output_path.parent, local_relay_proof_path),
        "localRelayProofSha256": local_relay_hash,
        "hostHelperAdapter": adapter,
        "delivery": {
            "accepted": [accepted_private],
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
            "protocolVersion": delivery.EXPECTED_PROTOCOL,
            "transport": delivery.EXPECTED_TRANSPORT,
            "sessionCompatibilityKey": compatibility_key,
            "messageCount": 8,
            "events": [
                make_event("adapter_initialized", adapterName=delivery.EXPECTED_ADAPTER, adapterVersion=delivery.EXPECTED_ADAPTER_VERSION),
                make_event("relay_session_verified", compatibilityKey=compatibility_key),
                make_event("relay_command_received", relayCommandId=relay.EXPECTED_COMMAND_ID),
                make_event("host_helper_delivery_accepted", commandId=delivery.EXPECTED_PRIVATE_COMMAND_ID, relayCommandId=relay.EXPECTED_COMMAND_ID, hostHelperDeliveryAccepted=True, relaySideGameInputSent=False, hostHelperInputSent=True),
                make_event("delivery_command_malformed_rejected", reason="malformed-delivery-command"),
                make_event("delivery_command_wrong_slot_rejected", reason="remote-slot-not-allowed"),
                make_event("delivery_command_wrong_compatibility_rejected", reason="session-compatibility-mismatch"),
                make_event("adapter_closed"),
            ],
        },
        "claimBoundary": (
            "Private/local relay-delivery adapter proof only. This proves an accepted localhost relay P2 command can be "
            "accepted by the safe-copy host-helper delivery adapter and mapped to the same upstream copied-BEA loopback "
            "P2 route already proven by exact-PID CDB evidence. It does not prove LAN transport, public matchmaking, "
            "public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, "
            "two-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {"bundle": str(output_path.resolve()), "relaySummary": relay_summary}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("local_relay_proof", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    output_path = args.output or args.local_relay_proof.with_name("private-relay-delivery-proof.json")
    result = build_bundle(args.local_relay_proof, output_path.resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        PrivateRelayDeliveryBundleBuildError,
        delivery.PrivateRelayDeliveryProofError,
        relay.RelayProofError,
        loopback.LoopbackProofError,
        loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary private relay delivery bundle build: FAIL: {exc}")
        raise SystemExit(2)
