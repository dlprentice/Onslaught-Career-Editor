#!/usr/bin/env python3
"""Build a second-host command-source to copied-runtime executor proof.

This is the proof rung after the bridge adapter. In live mode it consumes a
checker-accepted second-host command-source proof, runs the existing copied-BEA
host-authority runtime executor from a matching host-authority proof, and emits
a private compatibility proof. It does not claim the second-host client directly
drove runtime input until a later receipt carries the second-host payload through
the scheduler/bridge/runtime/CDB input windows.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import build_winui_original_binary_second_host_runtime_delivery_bridge_bundle as bridge_builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_second_host_command_source_check as second_check
import winui_safe_copy_online_second_host_runtime_delivery_bridge_check as bridge_check


SCHEMA = "winui-original-binary-second-host-runtime-executor.v1"
PROTOCOL = "second-host-runtime-executor.v1"
HELPER = "winui-original-binary-second-host-runtime-executor"
HELPER_VERSION = "second-host-runtime-executor.v1"
RUNTIME_EXECUTOR_SCOPE = "second-host-command-source-to-fresh-copied-runtime-executor-not-player-ready-online"
PRIVATE_PROOF_ROOT = executor_check.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "second-host-runtime-executor-20260620"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "second-host-runtime-executor-proof.json"
DEFAULT_EXE_OVERRIDE = executor_check.DEFAULT_EXE_OVERRIDE
REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS = second_check.REQUIRED_SESSION_SECURITY_HARDENING_FLAGS


class SecondHostRuntimeExecutorBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimeExecutorBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def require_second_host_security_hardening(second_payload: dict[str, Any]) -> dict[str, Any]:
    hardening = second_payload.get("sessionSecurityHardening")
    require(isinstance(hardening, dict), "live second-host runtime promotion requires sessionSecurityHardening")
    require(hardening.get("evidenceMode") == "live-server-client-transcript", "live second-host runtime promotion requires live hardening evidence")
    require(hardening.get("liveNegativeCaseTranscript") is True, "live second-host runtime promotion requires live negative-case transcript")
    require(hardening.get("requiredBeforeAcceptedLiveRuntimeDelivery") is True, "live second-host runtime promotion requires hardening gate")
    for key in REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS:
        require(hardening.get(key) is True, f"live second-host runtime promotion requires {key}=true")
    return hardening


def require_live_source_safety_preflight(second_payload: dict[str, Any]) -> dict[str, Any]:
    source_safety = object_at(second_payload, "sourceSafety")
    require(source_safety.get("evidenceMode") == "local-preflight-computed", "live second-host runtime promotion requires local source-safety preflight")
    require(source_safety.get("computedByPreflight") is True, "live second-host runtime promotion requires computed source-safety preflight")
    for role in ("host", "client"):
        side = object_at(source_safety, role)
        require(side.get("sourceEvidenceMode") == "local-preflight-computed", f"live second-host runtime promotion requires {role} local source-safety evidence")
        require(side.get("computedByPreflight") is True, f"live second-host runtime promotion requires {role} computed source-safety evidence")
        require(side.get("pathValuesPublished") is False, f"live second-host runtime promotion forbids {role} path publication")
        require(side.get("absolutePathsSerialized") is False, f"live second-host runtime promotion forbids {role} absolute path serialization")
        require(int(side.get("copiedProfileFileCount") or 0) > 0, f"live second-host runtime promotion requires {role} copied-profile file count")
        require(int(side.get("installedGameFileCount") or 0) > 0, f"live second-host runtime promotion requires {role} installed-game file count")
        require(side.get("copiedProfileHashMode") != "operator-supplied-sha256", f"live second-host runtime promotion rejects {role} operator copied-profile hash")
        require(side.get("installedGameHashMode") != "operator-supplied-sha256", f"live second-host runtime promotion rejects {role} operator installed-game hash")
        require(side.get("programFilesMutationAttempted") is False, f"live second-host runtime promotion forbids {role} Program Files mutation")
    return source_safety


def require_private_path(path: Path, *, must_exist: bool = False) -> Path:
    resolved = executor_check.require_private_proof_path(path)
    if must_exist:
        require(resolved.is_file(), f"private proof artifact is missing: {resolved}")
    return resolved


def private_root_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PRIVATE_PROOF_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise SecondHostRuntimeExecutorBuildError(f"artifact outside private proof root: {resolved}") from exc


def sha256_file(path: Path) -> str:
    return executor_check.sha256_file(path)


def sha256_json(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def make_fixture_executor_for_host(host_authority_proof: Path, artifact_root: Path) -> Path:
    artifact_root = require_private_path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)
    host_authority_proof = require_private_path(host_authority_proof, must_exist=True)
    host_payload = executor_check.delivery.host.read_json(host_authority_proof)
    runtime_artifact = executor_check.delivery.state_delta.make_artifact(
        artifact_root,
        controller_configuration=1,
        qe_proof_lever="input-isolation-forward-qe",
    )
    runtime_payload = executor_check.delivery.state_delta.read_json(runtime_artifact)
    runtime_payload["source"]["overrideHashBefore"] = host_payload["sessionDescriptor"]["cleanSpecimenSha256"]
    runtime_artifact.write_text(json.dumps(runtime_payload, indent=2) + "\n", encoding="utf-8")
    runtime_delivery = artifact_root / "host-authority-runtime-delivery-proof.json"
    executor_check.delivery.build_bundle(host_authority_proof, runtime_artifact, runtime_delivery)
    executor_proof = artifact_root / "host-authority-runtime-executor-proof.json"
    executor_check.make_executor_proof(host_authority_proof, runtime_artifact, runtime_delivery, executor_proof)
    return executor_proof


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


def build_bundle(
    second_host_command_source_proof: Path,
    host_authority_two_client_proof: Path,
    output_path: Path,
    *,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
    exe_override: Path = DEFAULT_EXE_OVERRIDE,
    allow_fixture_executor: bool = False,
) -> dict[str, Any]:
    artifact_root = require_private_path(artifact_root)
    output_path = require_private_path(output_path)
    second_host_command_source_proof = require_private_path(second_host_command_source_proof, must_exist=True)
    host_authority_two_client_proof = require_private_path(host_authority_two_client_proof, must_exist=True)

    second_summary = second_check.validate_bundle(second_host_command_source_proof)
    second_payload = second_check.read_json(second_host_command_source_proof)
    second_descriptor = object_at(second_payload, "sessionDescriptor")
    second_commands = object_at(second_payload, "commands")
    second_invitation_lifecycle = object_at(second_payload, "invitationLifecycle")
    accepted_second = second_commands.get("accepted")
    require(isinstance(accepted_second, list) and len(accepted_second) == 1, "second-host proof must contain one accepted command")
    second_command = accepted_second[0]
    require(isinstance(second_command, dict), "accepted second-host command must be an object")

    host_summary = executor_check.delivery.host.validate_bundle(
        host_authority_two_client_proof,
        expected_controller_configuration=1,
    )
    host_payload = executor_check.delivery.host.read_json(host_authority_two_client_proof)
    host_remote_path, host_remote_payload = resolve_host_private_remote_client(host_authority_two_client_proof, host_payload)
    host_remote_descriptor = object_at(host_remote_payload, "sessionDescriptor")
    host_descriptor = object_at(host_payload, "sessionDescriptor")
    host_commands = object_at(host_descriptor, "allowedCommands")
    host_p2 = object_at(host_commands, "P2")
    require(
        host_summary["upstreamPrivateRemoteClient"]["wouldForwardToPrivateLanCommandId"]
        == second_summary["wouldForwardToPrivateLanCommandId"],
        "second-host command source does not match host-authority private-LAN command id",
    )
    require(host_p2.get("command") == second_command.get("command"), "second-host P2 command does not match host-authority P2 command")
    require(host_p2.get("mappedInputSequence") == executor_check.delivery.host.EXPECTED_P2_SEQUENCE, "host-authority P2 mapped sequence mismatch")
    host_p2_sequence = str(host_p2["mappedInputSequence"])
    host_p2_sequence_sha256 = sha256_text(host_p2_sequence)
    host_p2_runtime_route = "P2/inputDevice1/bottom-split-half"
    host_p2_input_device = 1
    session_compatibility_match = second_descriptor.get("sessionCompatibilityKey") == host_descriptor.get("sessionCompatibilityKey")
    clean_specimen_match = second_descriptor.get("cleanSpecimenSha256") == host_descriptor.get("cleanSpecimenSha256")
    upstream_private_lan_proof_hash_match = (
        second_descriptor.get("upstreamPrivateLanProofSha256")
        == host_remote_descriptor.get("upstreamPrivateLanProofSha256")
    )
    require(clean_specimen_match, "second-host and host-authority clean specimen hashes must match")
    require(upstream_private_lan_proof_hash_match, "second-host and host-authority upstream private-LAN proof hashes must match")
    require(second_descriptor.get("upstreamPrivateLanCommandId") == host_descriptor.get("upstreamPrivateLanCommandId"), "upstream private-LAN command id mismatch")
    require(second_descriptor.get("levelId") == host_descriptor.get("levelId") == 850, "level id mismatch")
    require(second_descriptor.get("controllerConfiguration") == host_descriptor.get("controllerConfiguration") == 1, "controller configuration mismatch")
    if not allow_fixture_executor:
        require(session_compatibility_match, "live runtime promotion requires matching session compatibility keys")

    security_hardening_accepted = False
    if allow_fixture_executor:
        runtime_executor_proof = make_fixture_executor_for_host(
            host_authority_two_client_proof,
            artifact_root / "fixture-runtime-executor",
        )
    else:
        require_second_host_security_hardening(second_payload)
        require_live_source_safety_preflight(second_payload)
        security_hardening_accepted = True
        runtime_summary = executor_check.build_live_executor_proof(
            host_authority_two_client_proof,
            artifact_root / "live-runtime-executor",
            exe_override=exe_override,
        )
        runtime_executor_proof = Path(str(runtime_summary["artifact"]))

    executor_summary = executor_check.validate_executor_proof(runtime_executor_proof)
    executor_payload = executor_check.read_json(runtime_executor_proof)
    execution = object_at(executor_payload, "execution")
    receipt = object_at(execution, "executionReceipt")
    receipt_mode = str(receipt.get("mode") or "")
    is_live_runtime = receipt_mode == "live-executor-subprocess" and not allow_fixture_executor
    require(executor_summary["derivedInputSequences"][-1] == host_p2["mappedInputSequence"], "runtime executor P2 input sequence mismatch")
    host_authority_relay_match = host_summary["relayPlanSha256"] == executor_summary["hostAuthorityRelayPlanSha256"]
    require(host_authority_relay_match, "runtime executor relay plan hash mismatch")

    bridge_output = output_path.with_name("second-host-runtime-delivery-bridge-proof.json")
    bridge_summary = bridge_builder.build_bundle(
        second_host_command_source_proof,
        runtime_executor_proof,
        bridge_output,
        allow_fixture_executor=allow_fixture_executor,
    )
    bridge_check.validate_bundle(bridge_output, allow_fixture=allow_fixture_executor)

    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "runtimeExecutorScope": RUNTIME_EXECUTOR_SCOPE,
        "sourceArtifacts": {
            "secondHostCommandSourceProof": private_root_relative_path(second_host_command_source_proof),
            "secondHostCommandSourceProofSha256": sha256_file(second_host_command_source_proof),
            "hostAuthorityTwoClientProof": private_root_relative_path(host_authority_two_client_proof),
            "hostAuthorityTwoClientProofSha256": sha256_file(host_authority_two_client_proof),
            "hostAuthorityPrivateRemoteClientProof": private_root_relative_path(host_remote_path),
            "hostAuthorityPrivateRemoteClientProofSha256": sha256_file(host_remote_path),
            "runtimeExecutorProof": private_root_relative_path(runtime_executor_proof),
            "runtimeExecutorProofSha256": sha256_file(runtime_executor_proof),
            "bridgeProof": private_root_relative_path(bridge_output),
            "bridgeProofSha256": sha256_file(bridge_output),
        },
        "sourceBinding": {
            "bindingMode": "live-second-host-to-runtime-bound-by-source-evidence" if is_live_runtime else "fixture-or-posthoc-compatibility-only",
            "requiredBeforeAcceptedLiveRuntimeDelivery": True,
            "acceptedSecondHostCommandPayloadSha256": sha256_json(second_command),
            "acceptedSecondHostCommandRequestEvent": second_command["requestEvent"],
            "acceptedSecondHostCommandRequestPayloadSha256": second_command["requestPayloadSha256"],
            "acceptedSecondHostCommandResponseEvent": second_command["responseEvent"],
            "acceptedSecondHostCommandResponsePayloadSha256": second_command["responsePayloadSha256"],
            "acceptedSecondHostCommandId": second_command["commandId"],
            "acceptedSecondHostRemoteSlot": second_command["remoteSlot"],
            "acceptedSecondHostCommand": second_command["command"],
            "hostAuthorityAcceptedP2CommandId": host_p2["commandId"],
            "hostAuthorityAcceptedP2Command": host_p2["command"],
            "hostAuthorityAcceptedP2MappedInputSequence": host_p2_sequence,
            "hostAuthorityAcceptedP2MappedInputSequenceSha256": host_p2_sequence_sha256,
            "hostAuthorityAcceptedP2RuntimeRoute": host_p2_runtime_route,
            "hostAuthorityAcceptedP2InputDevice": host_p2_input_device,
            "hostHelperInputBoundToAcceptedSecondHostCommand": True,
            "hostHelperInputBoundToMappedP2Sequence": True,
            "secondHostNetworkIdentityEvidenceSha256": sha256_json(object_at(second_payload, "networkIdentityEvidence")),
            "secondHostSourceSafetySha256": sha256_json(object_at(second_payload, "sourceSafety")),
            "secondHostAuthorizationSha256": sha256_json(object_at(second_payload, "authorization")),
            "secondHostInvitationLifecycleSha256": sha256_json(second_invitation_lifecycle),
            "secondHostInvitationLifecycleDeleted": second_invitation_lifecycle["deletionSucceeded"],
            "secondHostInvitationLifecyclePostDeleteAbsent": second_invitation_lifecycle["postDeleteExists"] is False,
            "secondHostClientIdentityFingerprint": object_at(second_payload, "authorization")["clientIdentityFingerprint"],
            "secondHostClientMachineFingerprint": object_at(object_at(second_payload, "networkIdentityEvidence"), "client")["machineFingerprint"],
            "sessionCompatibilityKeyMatch": session_compatibility_match,
            "secondHostSessionCompatibilityKeySha256": sha256_text(str(second_descriptor["sessionCompatibilityKey"])),
            "hostAuthoritySessionCompatibilityKeySha256": sha256_text(str(host_descriptor["sessionCompatibilityKey"])),
            "cleanSpecimenHashMatch": clean_specimen_match,
            "secondHostCleanSpecimenSha256": second_descriptor["cleanSpecimenSha256"],
            "hostAuthorityCleanSpecimenSha256": host_descriptor["cleanSpecimenSha256"],
            "upstreamPrivateLanProofHashMatch": upstream_private_lan_proof_hash_match,
            "secondHostUpstreamPrivateLanProofSha256": second_descriptor["upstreamPrivateLanProofSha256"],
            "hostAuthorityPrivateRemoteClientUpstreamPrivateLanProofSha256": host_remote_descriptor["upstreamPrivateLanProofSha256"],
            "hostAuthorityUpstreamPrivateRemoteClientProofSha256": host_descriptor["upstreamPrivateRemoteClientProofSha256"],
            "privateLanCommandIdMatch": host_descriptor["upstreamPrivateLanCommandId"] == second_summary["wouldForwardToPrivateLanCommandId"],
            "secondHostWouldForwardToPrivateLanCommandId": second_summary["wouldForwardToPrivateLanCommandId"],
            "hostAuthorityUpstreamPrivateLanCommandId": host_descriptor["upstreamPrivateLanCommandId"],
            "hostAuthorityRelayPlanMatch": host_authority_relay_match,
            "hostAuthorityRelayPlanSha256": host_summary["relayPlanSha256"],
            "runtimeExecutorHostAuthorityRelayPlanSha256": executor_summary["hostAuthorityRelayPlanSha256"],
        },
        "secondHostRuntimeExecutor": {
            "secondHostRuntimeExecutorProofBuilt": True,
            "secondHostCommandSourceProofAccepted": True,
            "secondHostCommandSourceKind": second_summary["commandSourceKind"],
            "secondHostSessionSecurityHardeningRequired": True,
            "secondHostSessionSecurityHardeningAccepted": security_hardening_accepted,
            "secondPhysicalHostProof": second_summary["secondPhysicalHostProof"],
            "secondHostAcceptedCommandId": second_summary["acceptedCommandId"],
            "secondHostRemoteSlot": second_descriptor["remotePlayerSlot"],
            "secondHostCommand": second_descriptor["allowedCommand"],
            "secondHostWouldForwardToPrivateLanCommandId": second_summary["wouldForwardToPrivateLanCommandId"],
            "hostAuthorityUpstreamPrivateLanCommandId": host_descriptor["upstreamPrivateLanCommandId"],
            "hostAuthorityAcceptedP2CommandId": host_p2["commandId"],
            "hostAuthorityRelayPlanSha256": host_summary["relayPlanSha256"],
            "runtimeExecutorHostAuthorityRelayPlanSha256": executor_summary["hostAuthorityRelayPlanSha256"],
            "upstreamPrivateLanProofHashMatch": upstream_private_lan_proof_hash_match,
            "runtimeInputDerivedFromHostAuthorityProof": is_live_runtime,
            "runtimeInputDerivedFromSecondHostCommandSource": False,
            "runtimeDrivenBySecondHostCommandSource": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "secondHostDirectRuntimeCausalityProofRequired": True,
            "bridgeAdapterAccepted": bridge_summary["secondHostRuntimeDeliveryBridgeProven"],
            "bridgeAdapterRuntimeDrivenFlag": bridge_summary["runtimeDrivenBySecondHostCommandSource"],
        },
        "runtimeEvidence": {
            "runtimeExecutorReceiptMode": receipt_mode,
            "safeCopyLaunchLevel": execution["safeCopyLaunchLevel"],
            "controllerConfiguration": execution["controllerConfiguration"],
            "newBeaLaunchCount": 1 if is_live_runtime else 0,
            "cdbAttachCount": 1 if is_live_runtime else 0,
            "visualCaptureCount": executor_summary["visualCaptureCount"],
            "deliveredOriginalBinaryCommandCount": executor_summary["deliveredOriginalBinaryCommandCount"],
            "hostHelperInputSent": executor_summary["deliveredOriginalBinaryCommandCount"] == 2,
            "hostHelperInputBoundToSecondHostCommandSource": True,
            "hostHelperInputDeliveryAuthority": "host-helper-on-host-from-accepted-second-host-command-source",
            "hostHelperBoundAcceptedSecondHostCommandId": second_summary["acceptedCommandId"],
            "hostHelperBoundHostAuthorityCommandId": host_p2["commandId"],
            "hostHelperBoundRemoteSlot": second_descriptor["remotePlayerSlot"],
            "hostHelperMappedInputSequence": host_p2_sequence,
            "hostHelperMappedInputSequenceSha256": host_p2_sequence_sha256,
            "hostHelperRuntimeRoute": host_p2_runtime_route,
            "hostHelperInputDevice": host_p2_input_device,
            "gameInputSentBySecondHostClient": False,
            "gameInputSentByHostAuthorityScheduler": False,
            "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
            "metadataOnlySlots": ["P3", "P4"],
            "rejectedGameplayRouteSlots": ["P3", "P4"],
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "hostJoinControlsMayBeEnabled": False,
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
            "This proof class binds a checker-accepted second-host/private-LAN P2 command-source proof to one fresh "
            "copied original-BEA level-850/config-1 host-authority runtime executor run. In live mode it may prove "
            "the accepted second-host P2 command source selected the P2 runtime input route that the copied host "
            "executor delivered with exact-PID CDB evidence. It does not prove player-ready online multiplayer, "
            "Host/Join enablement, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, "
            "co-op/versus semantics, active P3/P4 gameplay, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    write_json(output_path, bundle)

    import winui_safe_copy_online_second_host_runtime_executor_check as checker

    return checker.validate_bundle(output_path, allow_fixture=allow_fixture_executor)


def run_self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory(dir=PRIVATE_PROOF_ROOT) as raw_tmp:
        root = Path(raw_tmp)
        host_path = executor_check.delivery.host.make_bundle_fixture(root / "host-authority")
        second_path = bridge_builder.make_source_bound_second_host_fixture(root, host_path)
        output_path = root / "executor" / "second-host-runtime-executor-proof.json"
        summary = build_bundle(
            second_path,
            host_path,
            output_path,
            artifact_root=root / "runtime",
            allow_fixture_executor=True,
        )
        require(summary["secondHostRuntimeExecutorProofBuilt"] is True, "self-test executor proof was not accepted")
        require(summary["acceptedLiveSecondHostRuntimeDeliveryProof"] is False, "fixture self-test must not claim live second-host runtime delivery")
        require(summary["runtimeDrivenBySecondHostCommandSource"] is False, "fixture self-test must not claim second-host-driven runtime")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("second_host_command_source_proof", nargs="?", type=Path)
    parser.add_argument("host_authority_two_client_proof", nargs="?", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--exe-override", type=Path, default=DEFAULT_EXE_OVERRIDE)
    parser.add_argument("--allow-fixture-executor", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime executor builder self-test: PASS")
        return 0
    if args.second_host_command_source_proof is None or args.host_authority_two_client_proof is None:
        raise SystemExit("second_host_command_source_proof and host_authority_two_client_proof are required unless --self-test is used")
    print(
        json.dumps(
            build_bundle(
                args.second_host_command_source_proof,
                args.host_authority_two_client_proof,
                args.output,
                artifact_root=args.artifact_root,
                exe_override=args.exe_override,
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
        SecondHostRuntimeExecutorBuildError,
        bridge_builder.SecondHostRuntimeDeliveryBridgeBuildError,
        bridge_check.SecondHostRuntimeDeliveryBridgeError,
        executor_check.HostAuthorityRuntimeExecutorError,
        executor_check.delivery.HostAuthorityRuntimeDeliveryError,
        executor_check.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor_check.delivery.host.remote.PrivateRemoteClientSmokeProofError,
        bridge_builder.command_builder.SecondHostCommandSourceBundleBuildError,
        second_check.SecondHostCommandSourceProofError,
    ) as exc:
        print(f"WinUI original-binary second-host runtime executor build: FAIL: {exc}")
        raise SystemExit(2)
