#!/usr/bin/env python3
"""Build a second-host command-source to copied-runtime bridge proof bundle.

This is a provenance/compatibility rung below player-ready netplay. It binds a
checker-accepted second-host command-source proof to an existing host-authority
runtime executor proof and verifies the accepted P2 command maps to the copied
host's P2 runtime route. It does not claim the live runtime was driven directly
by a remote second-host client.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import build_winui_original_binary_second_host_command_source_bundle as command_builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_second_host_command_source_check as second_check


SCHEMA = "winui-original-binary-second-host-runtime-delivery-bridge.v1"
PROTOCOL = "second-host-runtime-delivery-bridge.v1"
HELPER = "winui-original-binary-second-host-runtime-delivery-bridge"
HELPER_VERSION = "second-host-runtime-delivery-bridge.v1"
BRIDGE_SCOPE = "second-host-command-source-to-runtime-delivery-bridge-not-player-ready-online"
PRIVATE_PROOF_ROOT = executor_check.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "second-host-runtime-delivery-bridge-20260620"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "second-host-runtime-delivery-bridge-proof.json"


class SecondHostRuntimeDeliveryBridgeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimeDeliveryBridgeBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def sha256_file(path: Path) -> str:
    return executor_check.sha256_file(path)


def require_private_path(path: Path) -> Path:
    return executor_check.require_private_proof_path(path)


def private_root_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PRIVATE_PROOF_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise SecondHostRuntimeDeliveryBridgeBuildError(f"artifact outside private proof root: {resolved}") from exc


def resolve_executor_reference(executor_path: Path, raw_path: str) -> Path:
    return executor_check.resolve_path(executor_path, raw_path)


def resolve_host_private_remote_client(host_authority_two_client_proof: Path, host_payload: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    remote_path = executor_check.delivery.host.resolve_artifact_path(
        host_authority_two_client_proof,
        str(host_payload.get("privateRemoteClientProofBundle") or ""),
    )
    require(
        str(host_payload.get("privateRemoteClientProofSha256") or "").lower() == sha256_file(remote_path),
        "host-authority private remote-client proof hash mismatch",
    )
    remote_payload = executor_check.delivery.host.read_json(remote_path)
    return remote_path, remote_payload


def make_source_bound_second_host_fixture(root: Path, host_authority_two_client_proof: Path) -> Path:
    host_authority_two_client_proof = require_private_path(host_authority_two_client_proof)
    host_payload = executor_check.delivery.host.read_json(host_authority_two_client_proof)
    remote_path, remote_payload = resolve_host_private_remote_client(host_authority_two_client_proof, host_payload)
    private_lan_path = executor_check.delivery.resolve_path(
        remote_path,
        str(remote_payload["privateLanTransportProofBundle"]),
    )
    output_path = require_private_path(root / "second-host-command-source-proof.json")
    credential = bytes.fromhex("12" * 32)
    authorization = command_builder.make_authorization(
        credential,
        command_builder.lan.sha256_file(private_lan_path),
        "c" * 64,
    )
    source_safety = command_builder.make_source_safety(
        host_copied_profile_sha256="3" * 64,
        host_installed_game_sha256="4" * 64,
        client_copied_profile_sha256="5" * 64,
        client_installed_game_sha256="6" * 64,
    )
    command_builder.make_bundle_from_observation(
        private_lan_proof_path=private_lan_path,
        output_path=output_path,
        command_source_kind="distinct-vm-private-lan-labeled-vm-only",
        host_bind_address=command_builder.checker.FIXTURE_HOST_ADDRESS,
        host_assigned_addresses=[command_builder.checker.FIXTURE_HOST_ADDRESS],
        host_machine_fingerprint="1" * 64,
        client_source_address=command_builder.checker.FIXTURE_CLIENT_ADDRESS,
        client_assigned_address=command_builder.checker.FIXTURE_CLIENT_ADDRESS,
        client_machine_fingerprint="2" * 64,
        client_identity_fingerprint="c" * 64,
        authorization=authorization,
        source_safety=source_safety,
        transcript_events=[
            command_builder.make_event(kind, {"kind": kind})
            for kind in command_builder.checker.EXPECTED_TRANSCRIPT_EVENTS
        ],
    )
    return output_path


def build_bundle(
    second_host_command_source_proof: Path,
    runtime_executor_proof: Path,
    output_path: Path,
    *,
    allow_fixture_executor: bool = False,
) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    second_host_command_source_proof = require_private_path(second_host_command_source_proof)
    runtime_executor_proof = require_private_path(runtime_executor_proof)
    require(second_host_command_source_proof.is_file(), f"second-host command-source proof is missing: {second_host_command_source_proof}")
    require(runtime_executor_proof.is_file(), f"runtime executor proof is missing: {runtime_executor_proof}")

    second_summary = second_check.validate_bundle(second_host_command_source_proof)
    second_payload = second_check.read_json(second_host_command_source_proof)
    second_descriptor = object_at(second_payload, "sessionDescriptor")
    second_transport = object_at(second_payload, "transport")
    second_commands = object_at(second_payload, "commands")
    accepted_second = second_commands.get("accepted")
    require(isinstance(accepted_second, list) and len(accepted_second) == 1, "second-host proof must contain one accepted command")
    second_command = accepted_second[0]
    require(isinstance(second_command, dict), "accepted second-host command must be an object")

    executor_summary = executor_check.validate_executor_proof(runtime_executor_proof)
    executor_payload = executor_check.read_json(runtime_executor_proof)
    execution = object_at(executor_payload, "execution")
    receipt = object_at(execution, "executionReceipt")
    receipt_mode = str(receipt.get("mode") or "")
    if allow_fixture_executor:
        require(receipt_mode in {"live-executor-subprocess", "self-test-fixture"}, "unexpected runtime executor receipt mode")
    else:
        require(receipt_mode == "live-executor-subprocess", "runtime executor proof must be live")

    host_path = resolve_executor_reference(runtime_executor_proof, str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""))
    host_summary = executor_check.delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_payload = executor_check.delivery.host.read_json(host_path)
    host_remote_path, host_remote_payload = resolve_host_private_remote_client(host_path, host_payload)
    host_descriptor = object_at(host_payload, "sessionDescriptor")
    host_remote_descriptor = object_at(host_remote_payload, "sessionDescriptor")
    host_commands = object_at(host_descriptor, "allowedCommands")
    host_p2 = object_at(host_commands, "P2")
    runtime_delivery_path = resolve_executor_reference(runtime_executor_proof, str(executor_payload.get("runtimeDeliveryProofBundle") or ""))
    runtime_delivery_payload = executor_check.delivery.read_json(runtime_delivery_path)
    runtime_delivery = object_at(runtime_delivery_payload, "delivery")
    runtime_delivery_summary = executor_check.delivery.validate_bundle(runtime_delivery_path)
    live_runtime_path = resolve_executor_reference(runtime_executor_proof, str(executor_payload.get("liveRuntimeArtifact") or ""))

    require(second_summary["acceptedCommandId"] == second_check.EXPECTED_COMMAND_ID, "second-host accepted command mismatch")
    require(second_summary["wouldForwardToPrivateLanCommandId"] == second_check.EXPECTED_PRIVATE_LAN_COMMAND_ID, "second-host private LAN command mismatch")
    require(second_summary["gameInputSentBySecondHostClient"] is False, "second-host proof must not claim direct game input")
    require(second_summary["hostHelperInputSent"] is False, "second-host proof must not claim host-helper input")
    upstream_private_lan_proof_hash_match = (
        second_descriptor.get("upstreamPrivateLanProofSha256")
        == host_remote_descriptor.get("upstreamPrivateLanProofSha256")
    )
    require(upstream_private_lan_proof_hash_match, "second-host and host-authority upstream private-LAN proof hashes must match")
    require(host_descriptor["upstreamPrivateLanCommandId"] == second_summary["wouldForwardToPrivateLanCommandId"], "host-authority private LAN command id does not match second-host proof")
    require(host_summary["upstreamPrivateRemoteClient"]["wouldForwardToPrivateLanCommandId"] == second_summary["wouldForwardToPrivateLanCommandId"], "host upstream private LAN path does not match second-host proof")
    require(host_p2.get("command") == second_command.get("command"), "P2 command name mismatch")
    require(host_p2.get("mappedInputSequence") == executor_check.delivery.host.EXPECTED_P2_SEQUENCE, "P2 mapped input sequence mismatch")
    require(executor_summary["derivedInputSequences"][-1] == host_p2["mappedInputSequence"], "runtime executor P2 input sequence mismatch")
    require(runtime_delivery_summary["hostAuthorityRelayPlanSha256"] == host_summary["relayPlanSha256"], "runtime delivery relay hash mismatch")

    bridge: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "bridgeScope": BRIDGE_SCOPE,
        "sourceArtifacts": {
            "secondHostCommandSourceProof": private_root_relative_path(second_host_command_source_proof),
            "secondHostCommandSourceProofSha256": sha256_file(second_host_command_source_proof),
            "runtimeExecutorProof": private_root_relative_path(runtime_executor_proof),
            "runtimeExecutorProofSha256": sha256_file(runtime_executor_proof),
            "hostAuthorityTwoClientProof": private_root_relative_path(host_path),
            "hostAuthorityTwoClientProofSha256": sha256_file(host_path),
            "hostAuthorityPrivateRemoteClientProof": private_root_relative_path(host_remote_path),
            "hostAuthorityPrivateRemoteClientProofSha256": sha256_file(host_remote_path),
            "runtimeDeliveryProof": private_root_relative_path(runtime_delivery_path),
            "runtimeDeliveryProofSha256": sha256_file(runtime_delivery_path),
            "liveRuntimeArtifact": private_root_relative_path(live_runtime_path),
            "liveRuntimeArtifactSha256": sha256_file(live_runtime_path),
        },
        "secondHostRuntimeDeliveryBridge": {
            "secondHostRuntimeDeliveryBridgeProven": True,
            "secondHostCommandSourceKind": second_summary["commandSourceKind"],
            "secondPhysicalHostProof": second_summary["secondPhysicalHostProof"],
            "secondHostAcceptedCommandId": second_summary["acceptedCommandId"],
            "secondHostRemoteSlot": second_descriptor["remotePlayerSlot"],
            "secondHostCommand": second_descriptor["allowedCommand"],
            "secondHostWouldForwardToPrivateLanCommandId": second_summary["wouldForwardToPrivateLanCommandId"],
            "hostAuthorityUpstreamPrivateLanCommandId": host_descriptor["upstreamPrivateLanCommandId"],
            "upstreamPrivateLanProofHashMatch": upstream_private_lan_proof_hash_match,
            "secondHostUpstreamPrivateLanProofSha256": second_descriptor["upstreamPrivateLanProofSha256"],
            "hostAuthorityPrivateRemoteClientUpstreamPrivateLanProofSha256": host_remote_descriptor["upstreamPrivateLanProofSha256"],
            "hostAuthorityUpstreamPrivateRemoteClientProofSha256": host_descriptor["upstreamPrivateRemoteClientProofSha256"],
            "hostAuthorityAcceptedP2CommandId": host_p2["commandId"],
            "hostAuthorityRelayPlanSha256": host_summary["relayPlanSha256"],
            "runtimeExecutorHostAuthorityRelayPlanSha256": executor_summary["hostAuthorityRelayPlanSha256"],
            "runtimeDeliveryHostAuthorityRelayPlanSha256": runtime_delivery_summary["hostAuthorityRelayPlanSha256"],
            "p2RuntimeRoute": "P2/inputDevice1/bottom-split-half",
            "p2MappedInputSequence": host_p2["mappedInputSequence"],
            "secondHostCommandMatchesRuntimeP2Route": True,
            "privateLanCommandPathMatchCount": 2,
            "runtimeRelayPathMatchCount": 1,
        },
        "runtimeEvidence": {
            "runtimeExecutorReceiptMode": receipt_mode,
            "safeCopyLaunchLevel": execution["safeCopyLaunchLevel"],
            "controllerConfiguration": execution["controllerConfiguration"],
            "newBeaLaunchCount": runtime_delivery["newBeaLaunchCount"],
            "cdbAttachCount": 1,
            "visualCaptureCount": executor_summary["visualCaptureCount"],
            "deliveredOriginalBinaryCommandCount": executor_summary["deliveredOriginalBinaryCommandCount"],
            "hostHelperInputSent": True,
            "gameInputSentBySecondHostClient": False,
            "gameInputSentByHostAuthorityScheduler": False,
            "runtimeDrivenBySecondHostCommandSource": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
            "metadataOnlySlots": ["P3", "P4"],
            "rejectedGameplayRouteSlots": ["P3", "P4"],
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "coOpVersusRuntimeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "rawPrivateProofPathPublished": False,
            "rawPrivateArtifactContentPublished": False,
            "absolutePrivatePathPublished": False,
            "rawRuntimePointerPublished": False,
            "rawRuntimePidPublished": False,
            "rawCdbLogPathPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This proves a checker-accepted second-host/private-LAN P2 command-source artifact is compatible with the "
            "copied original-BEA level-850/config-1 host-authority runtime delivery route for P2. It matches the "
            "second-host accepted command to the private-LAN command id, host-authority relay plan, and copied-host "
            "runtime executor P2 input sequence. It does not prove player-ready online multiplayer, accepted live "
            "second-host runtime delivery, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 "
            "gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    write_json(output_path, bridge)

    import winui_safe_copy_online_second_host_runtime_delivery_bridge_check as checker

    return checker.validate_bundle(output_path, allow_fixture=allow_fixture_executor)


def run_self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory(dir=PRIVATE_PROOF_ROOT) as raw_tmp:
        tmp = Path(raw_tmp)
        executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
        executor_payload = executor_check.read_json(executor_path)
        host_path = resolve_executor_reference(
            executor_path,
            str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""),
        )
        second_path = make_source_bound_second_host_fixture(tmp, host_path)
        output_path = tmp / "bridge" / "second-host-runtime-delivery-bridge-proof.json"
        summary = build_bundle(second_path, executor_path, output_path, allow_fixture_executor=True)
        require(summary["secondHostRuntimeDeliveryBridgeProven"] is True, "self-test bridge was not accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("second_host_command_source_proof", nargs="?", type=Path)
    parser.add_argument("runtime_executor_proof", nargs="?", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--allow-fixture-executor", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime-delivery bridge builder self-test: PASS")
        return 0
    if args.second_host_command_source_proof is None or args.runtime_executor_proof is None:
        raise SystemExit("second_host_command_source_proof and runtime_executor_proof are required unless --self-test is used")
    print(
        json.dumps(
            build_bundle(
                args.second_host_command_source_proof,
                args.runtime_executor_proof,
                args.output,
                allow_fixture_executor=args.allow_fixture_executor,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecondHostRuntimeDeliveryBridgeBuildError,
        executor_check.HostAuthorityRuntimeExecutorError,
        executor_check.delivery.HostAuthorityRuntimeDeliveryError,
        executor_check.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor_check.delivery.host.remote.PrivateRemoteClientSmokeProofError,
        command_builder.SecondHostCommandSourceBundleBuildError,
        second_check.SecondHostCommandSourceProofError,
    ) as exc:
        print(f"WinUI original-binary second-host runtime-delivery bridge build: FAIL: {exc}")
        raise SystemExit(2)
