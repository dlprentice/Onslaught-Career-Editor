#!/usr/bin/env python3
"""Build a private remote-client to copied-runtime causality proof bundle."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check


SCHEMA = "winui-original-binary-private-remote-client-runtime-causality.v1"
PROTOCOL = "private-remote-client-runtime-causality.v1"
HELPER = "winui-original-binary-private-remote-client-runtime-causality"
HELPER_VERSION = "private-remote-client-runtime-causality.v1"
CAUSALITY_SCOPE = "private-remote-client-to-runtime-executor-same-workstation-not-online-play"
PRIVATE_PROOF_ROOT = executor_check.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "private-remote-client-runtime-causality-20260620"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "private-remote-client-runtime-causality-proof.json"


class PrivateRemoteClientRuntimeCausalityBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateRemoteClientRuntimeCausalityBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def sha256_file(path: Path) -> str:
    return executor_check.sha256_file(path)


def relative_path(base: Path, target: Path) -> str:
    return executor_check.relative_path(base, target)


def private_root_relative_path(target: Path) -> str:
    target = target.resolve()
    try:
        return target.relative_to(PRIVATE_PROOF_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise PrivateRemoteClientRuntimeCausalityBuildError(f"source artifact outside private proof root: {target}") from exc


def require_private_output(path: Path) -> Path:
    return executor_check.require_private_proof_path(path)


def resolve_executor_reference(executor_path: Path, raw_path: str) -> Path:
    return executor_check.resolve_path(executor_path, raw_path)


def build_bundle_from_executor(
    runtime_executor_proof: Path,
    output_path: Path,
    *,
    allow_fixture_executor: bool = False,
) -> dict[str, Any]:
    output_path = require_private_output(output_path)
    runtime_executor_proof = require_private_output(runtime_executor_proof)
    require(runtime_executor_proof.is_file(), f"runtime executor proof is missing: {runtime_executor_proof}")

    executor_summary = executor_check.validate_executor_proof(runtime_executor_proof)
    executor_payload = executor_check.read_json(runtime_executor_proof)
    execution = object_at(executor_payload, "execution")
    receipt = object_at(execution, "executionReceipt")
    receipt_mode = str(receipt.get("mode") or "")
    if allow_fixture_executor:
        require(receipt_mode in {"live-executor-subprocess", "self-test-fixture"}, "unexpected executor receipt mode")
    else:
        require(receipt_mode == "live-executor-subprocess", "runtime executor proof must be live")

    host_path = resolve_executor_reference(
        runtime_executor_proof,
        str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""),
    )
    host_summary = executor_check.delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_payload = executor_check.delivery.host.read_json(host_path)
    host_descriptor = object_at(host_payload, "sessionDescriptor")
    remote_path = Path(host_summary["privateRemoteClientProofBundle"]).resolve()
    remote_summary = executor_check.delivery.host.remote.validate_bundle(remote_path, expected_controller_configuration=1)

    runtime_delivery_path = resolve_executor_reference(
        runtime_executor_proof,
        str(executor_payload.get("runtimeDeliveryProofBundle") or ""),
    )
    runtime_delivery_payload = executor_check.delivery.read_json(runtime_delivery_path)
    runtime_delivery_summary = executor_check.delivery.validate_bundle(runtime_delivery_path)
    live_runtime_path = resolve_executor_reference(
        runtime_executor_proof,
        str(executor_payload.get("liveRuntimeArtifact") or ""),
    )

    require(host_summary["upstreamPrivateRemoteClient"]["acceptedCommandId"] == remote_summary["acceptedCommandId"], "remote command id did not reach host summary")
    require(host_summary["upstreamPrivateRemoteClient"]["remoteClientAccepted"] is True, "remote client accepted flag missing")
    require(host_summary["upstreamPrivateRemoteClient"]["gameInputSentByRemoteClient"] is False, "remote client must not claim direct game input")
    require(host_summary["upstreamPrivateRemoteClient"]["hostHelperInputSent"] is False, "remote client smoke must not claim host-helper input")
    require(executor_summary["derivedInputSequences"] == execution["derivedInputSequences"], "executor derived sequence mismatch")
    require(executor_summary["deliveredOriginalBinaryCommandCount"] == 2, "executor delivered command count mismatch")
    require(runtime_delivery_summary["hostAuthorityRelayPlanSha256"] == host_summary["relayPlanSha256"], "delivery relay hash mismatch")

    delivery = object_at(runtime_delivery_payload, "delivery")
    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "causalityScope": CAUSALITY_SCOPE,
        "sourceArtifacts": {
            "privateRemoteClientProof": private_root_relative_path(remote_path),
            "privateRemoteClientProofSha256": sha256_file(remote_path),
            "hostAuthorityTwoClientProof": private_root_relative_path(host_path),
            "hostAuthorityTwoClientProofSha256": sha256_file(host_path),
            "runtimeExecutorProof": private_root_relative_path(runtime_executor_proof),
            "runtimeExecutorProofSha256": sha256_file(runtime_executor_proof),
            "runtimeDeliveryProof": private_root_relative_path(runtime_delivery_path),
            "runtimeDeliveryProofSha256": sha256_file(runtime_delivery_path),
            "liveRuntimeArtifact": private_root_relative_path(live_runtime_path),
            "liveRuntimeArtifactSha256": sha256_file(live_runtime_path),
        },
        "privateRemoteClientRuntimeCausality": {
            "privateRemoteClientRuntimeCausalityProven": True,
            "remoteClientAcceptedCommandId": remote_summary["acceptedCommandId"],
            "remoteClientTransport": remote_summary["transport"],
            "remoteClientProcessModel": remote_summary["processBoundary"]["processModel"],
            "remoteClientProcessSeparated": remote_summary["processBoundary"]["clientProcessDifferentFromBuilder"],
            "remoteClientSameWorkstationOnly": remote_summary["processBoundary"]["sameWorkstationOnly"],
            "remoteClientWouldForwardToPrivateLanCommandId": remote_summary["wouldForwardToPrivateLanCommandId"],
            "hostAuthorityAcceptedCommandIds": host_summary["acceptedCommandIds"],
            "hostAuthorityRelayPlanSha256": host_summary["relayPlanSha256"],
            "hostAuthorityUpstreamPrivateRemoteClientCommandId": host_descriptor["upstreamPrivateRemoteClientCommandId"],
            "runtimeExecutorDerivedInputSequences": executor_summary["derivedInputSequences"],
            "runtimeExecutorHostAuthorityRelayPlanSha256": executor_summary["hostAuthorityRelayPlanSha256"],
            "runtimeDeliveryHostAuthorityRelayPlanSha256": runtime_delivery_summary["hostAuthorityRelayPlanSha256"],
            "remoteClientToHostRelayPathMatchCount": 1,
            "hostRelayToRuntimeExecutorPathMatchCount": 1,
        },
        "runtimeEvidence": {
            "runtimeExecutorReceiptMode": receipt_mode,
            "safeCopyLaunchLevel": execution["safeCopyLaunchLevel"],
            "controllerConfiguration": execution["controllerConfiguration"],
            "newBeaLaunchCount": delivery["newBeaLaunchCount"],
            "cdbAttachCount": 1,
            "visualCaptureCount": runtime_delivery_summary["visualCaptureCount"],
            "deliveredOriginalBinaryCommandCount": runtime_delivery_summary["deliveredOriginalBinaryCommandCount"],
            "hostHelperInputSent": True,
            "gameInputSentByRemoteClient": False,
            "gameInputSentByHostAuthorityScheduler": False,
            "bridgeSendsNewNetworkInput": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
            "metadataOnlySlots": ["P3", "P4"],
            "rejectedGameplayRouteSlots": ["P3", "P4"],
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "secondPhysicalHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "physicalGamepadProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
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
            "This proves a same-workstation process-separated private remote-client command source is on the "
            "validated provenance path into one copied original-BEA level-850/config-1 host-authority runtime "
            "executor proof. It links the private remote-client accepted P2 command to the host-authority relay "
            "plan and to the safe-copy runtime-delivery proof. It does not prove player-ready online multiplayer, "
            "a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 "
            "gameplay, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or "
            "no-noticeable-difference online parity."
        ),
    }
    write_json(output_path, bundle)

    import winui_safe_copy_online_private_remote_client_runtime_causality_check as checker

    return checker.validate_bundle(output_path, allow_fixture=allow_fixture_executor)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime_executor_proof", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--allow-fixture-executor", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            build_bundle_from_executor(
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
        PrivateRemoteClientRuntimeCausalityBuildError,
        executor_check.HostAuthorityRuntimeExecutorError,
        executor_check.delivery.HostAuthorityRuntimeDeliveryError,
        executor_check.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor_check.delivery.host.remote.PrivateRemoteClientSmokeProofError,
    ) as exc:
        print(f"WinUI original-binary private remote-client runtime-causality bundle build: FAIL: {exc}")
        raise SystemExit(2)
