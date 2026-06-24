#!/usr/bin/env python3
"""Validate second-host command-source to copied-runtime bridge proof bundles."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_second_host_runtime_delivery_bridge_bundle as builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_second_host_command_source_check as second_check


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-second-host-runtime-delivery-bridge.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_second_host_runtime_delivery_bridge_2026-06-20.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
FEASIBILITY_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
LOCAL_CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_second_host_runtime_delivery_bridge_check_test.py && "
    r"py -3 tools\build_winui_original_binary_second_host_runtime_delivery_bridge_bundle.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_second_host_runtime_delivery_bridge_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_second_host_runtime_delivery_bridge_check.py --check"
)
SENSITIVE_KEY_PARTS = ("credential", "secret", "token", "password", "authkey", "bearer")


class SecondHostRuntimeDeliveryBridgeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimeDeliveryBridgeError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def require_no_sensitive_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            require(not any(part in lowered for part in SENSITIVE_KEY_PARTS), f"sensitive-like field is not allowed at {path}.{key}")
            require_no_sensitive_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_sensitive_fields(child, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        require("bearer " not in lowered and "sk-" not in lowered, f"sensitive-like string is not allowed at {path}")


def resolve_artifact_path(raw_path: str) -> Path:
    require(raw_path, "referenced artifact path is empty")
    candidate = Path(raw_path)
    require(not candidate.is_absolute(), f"referenced artifact must be private-root-relative: {raw_path}")
    require(".." not in candidate.parts, f"referenced artifact must not contain '..': {raw_path}")
    require(not str(raw_path).startswith(("\\\\", "//")), f"UNC artifact path is not allowed: {raw_path}")
    resolved = (builder.PRIVATE_PROOF_ROOT / candidate).resolve()
    try:
        resolved.relative_to(builder.PRIVATE_PROOF_ROOT.resolve())
    except ValueError as exc:
        raise SecondHostRuntimeDeliveryBridgeError(f"referenced artifact escapes private proof root: {raw_path}") from exc
    require(resolved.is_file(), f"referenced artifact is missing: {resolved}")
    return resolved


def public_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(builder.PRIVATE_PROOF_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("bridgeScope") == builder.BRIDGE_SCOPE, "bridge scope mismatch")


def require_source_artifacts(
    bundle: dict[str, Any],
) -> tuple[Any, ...]:
    artifacts = object_at(bundle, "sourceArtifacts")
    second_path = resolve_artifact_path(str(artifacts.get("secondHostCommandSourceProof") or ""))
    executor_path = resolve_artifact_path(str(artifacts.get("runtimeExecutorProof") or ""))
    host_path = resolve_artifact_path(str(artifacts.get("hostAuthorityTwoClientProof") or ""))
    host_remote_path = resolve_artifact_path(str(artifacts.get("hostAuthorityPrivateRemoteClientProof") or ""))
    delivery_path = resolve_artifact_path(str(artifacts.get("runtimeDeliveryProof") or ""))
    runtime_path = resolve_artifact_path(str(artifacts.get("liveRuntimeArtifact") or ""))

    require(artifacts.get("secondHostCommandSourceProofSha256") == second_check.sha256_file(second_path), "second-host proof hash mismatch")
    require(artifacts.get("runtimeExecutorProofSha256") == executor_check.sha256_file(executor_path), "runtime executor proof hash mismatch")
    require(artifacts.get("hostAuthorityTwoClientProofSha256") == executor_check.sha256_file(host_path), "host-authority proof hash mismatch")
    require(artifacts.get("hostAuthorityPrivateRemoteClientProofSha256") == executor_check.sha256_file(host_remote_path), "host-authority private remote-client proof hash mismatch")
    require(artifacts.get("runtimeDeliveryProofSha256") == executor_check.sha256_file(delivery_path), "runtime delivery proof hash mismatch")
    require(artifacts.get("liveRuntimeArtifactSha256") == executor_check.sha256_file(runtime_path), "live runtime artifact hash mismatch")

    second_summary = second_check.validate_bundle(second_path)
    second_payload = second_check.read_json(second_path)
    executor_summary = executor_check.validate_executor_proof(executor_path)
    executor_payload = executor_check.read_json(executor_path)
    resolved_host = executor_check.resolve_path(executor_path, str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""))
    resolved_delivery = executor_check.resolve_path(executor_path, str(executor_payload.get("runtimeDeliveryProofBundle") or ""))
    resolved_runtime = executor_check.resolve_path(executor_path, str(executor_payload.get("liveRuntimeArtifact") or ""))
    require(resolved_host.resolve() == host_path.resolve(), "executor host-authority reference mismatch")
    require(resolved_delivery.resolve() == delivery_path.resolve(), "executor runtime-delivery reference mismatch")
    require(resolved_runtime.resolve() == runtime_path.resolve(), "executor live-runtime reference mismatch")
    host_summary = executor_check.delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_payload = executor_check.delivery.host.read_json(host_path)
    resolved_remote = executor_check.delivery.host.resolve_artifact_path(host_path, str(host_payload.get("privateRemoteClientProofBundle") or ""))
    require(resolved_remote.resolve() == host_remote_path.resolve(), "host-authority private remote-client reference mismatch")
    host_remote_payload = executor_check.delivery.host.read_json(host_remote_path)
    delivery_summary = executor_check.delivery.validate_bundle(delivery_path)
    return second_path, second_summary, second_payload, executor_path, executor_summary, host_path, host_summary, host_payload, host_remote_path, host_remote_payload, delivery_path, delivery_summary, runtime_path


def require_bridge(
    bundle: dict[str, Any],
    *,
    second_summary: dict[str, Any],
    second_payload: dict[str, Any],
    executor_summary: dict[str, Any],
    host_summary: dict[str, Any],
    host_payload: dict[str, Any],
    host_remote_payload: dict[str, Any],
    delivery_summary: dict[str, Any],
) -> dict[str, Any]:
    bridge = object_at(bundle, "secondHostRuntimeDeliveryBridge")
    second_descriptor = object_at(second_payload, "sessionDescriptor")
    host_descriptor = object_at(host_payload, "sessionDescriptor")
    host_remote_descriptor = object_at(host_remote_payload, "sessionDescriptor")
    require(bridge.get("secondHostRuntimeDeliveryBridgeProven") is True, "bridge flag missing")
    require(bridge.get("secondHostCommandSourceKind") == second_summary["commandSourceKind"], "command source kind mismatch")
    require(bridge.get("secondPhysicalHostProof") == second_summary["secondPhysicalHostProof"], "physical host flag mismatch")
    require(bridge.get("secondHostAcceptedCommandId") == second_check.EXPECTED_COMMAND_ID, "second-host command id mismatch")
    require(bridge.get("secondHostRemoteSlot") == second_check.EXPECTED_REMOTE_SLOT, "second-host remote slot mismatch")
    require(bridge.get("secondHostCommand") == second_check.EXPECTED_REMOTE_COMMAND, "second-host command mismatch")
    require(bridge.get("secondHostWouldForwardToPrivateLanCommandId") == second_check.EXPECTED_PRIVATE_LAN_COMMAND_ID, "private LAN command id mismatch")
    require(bridge.get("hostAuthorityUpstreamPrivateLanCommandId") == second_summary["wouldForwardToPrivateLanCommandId"], "host upstream private LAN id mismatch")
    require(bridge.get("upstreamPrivateLanProofHashMatch") is True, "upstream private-LAN proof hash match flag missing")
    require(bridge.get("secondHostUpstreamPrivateLanProofSha256") == second_descriptor["upstreamPrivateLanProofSha256"], "second-host upstream private-LAN proof hash mismatch")
    require(bridge.get("hostAuthorityPrivateRemoteClientUpstreamPrivateLanProofSha256") == host_remote_descriptor["upstreamPrivateLanProofSha256"], "host private remote-client upstream private-LAN proof hash mismatch")
    require(bridge.get("hostAuthorityUpstreamPrivateRemoteClientProofSha256") == host_descriptor["upstreamPrivateRemoteClientProofSha256"], "host upstream private remote-client proof hash mismatch")
    require(second_descriptor["upstreamPrivateLanProofSha256"] == host_remote_descriptor["upstreamPrivateLanProofSha256"], "second-host and host-authority upstream private-LAN proof hashes must match")
    require(bridge.get("hostAuthorityAcceptedP2CommandId") == executor_check.delivery.host.EXPECTED_P2_COMMAND_ID, "host P2 command id mismatch")
    require(bridge.get("hostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "host relay hash mismatch")
    require(bridge.get("runtimeExecutorHostAuthorityRelayPlanSha256") == executor_summary["hostAuthorityRelayPlanSha256"], "executor relay hash mismatch")
    require(bridge.get("runtimeDeliveryHostAuthorityRelayPlanSha256") == delivery_summary["hostAuthorityRelayPlanSha256"], "delivery relay hash mismatch")
    require(bridge.get("p2RuntimeRoute") == "P2/inputDevice1/bottom-split-half", "P2 runtime route mismatch")
    require(bridge.get("p2MappedInputSequence") == executor_check.delivery.host.EXPECTED_P2_SEQUENCE, "P2 mapped input mismatch")
    require(bridge.get("secondHostCommandMatchesRuntimeP2Route") is True, "P2 route match flag missing")
    require(bridge.get("privateLanCommandPathMatchCount") == 2, "private LAN match count mismatch")
    require(bridge.get("runtimeRelayPathMatchCount") == 1, "runtime relay match count mismatch")
    return bridge


def require_runtime(bundle: dict[str, Any], executor_summary: dict[str, Any], *, allow_fixture: bool) -> dict[str, Any]:
    runtime = object_at(bundle, "runtimeEvidence")
    receipt_mode = runtime.get("runtimeExecutorReceiptMode")
    if allow_fixture:
        require(receipt_mode in {"live-executor-subprocess", "self-test-fixture"}, "unexpected runtime executor receipt mode")
    else:
        require(receipt_mode == "live-executor-subprocess", "runtime executor must be live")
    require(runtime.get("safeCopyLaunchLevel") == 850, "safe-copy launch level mismatch")
    require(runtime.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(runtime.get("newBeaLaunchCount") == 1, "new copied BEA launch count mismatch")
    require(runtime.get("cdbAttachCount") == 1, "CDB attach count mismatch")
    require(runtime.get("visualCaptureCount") == executor_summary["visualCaptureCount"], "visual capture count mismatch")
    require(runtime.get("deliveredOriginalBinaryCommandCount") == executor_summary["deliveredOriginalBinaryCommandCount"] == 2, "delivered command count mismatch")
    require(runtime.get("hostHelperInputSent") is True, "host-helper input flag missing")
    require(runtime.get("gameInputSentBySecondHostClient") is False, "second host must not claim direct game input")
    require(runtime.get("gameInputSentByHostAuthorityScheduler") is False, "scheduler must not claim direct game input")
    require(runtime.get("runtimeDrivenBySecondHostCommandSource") is False, "bridge must not claim the live runtime was directly driven by second-host source")
    require(runtime.get("acceptedLiveSecondHostRuntimeDeliveryProof") is False, "accepted live second-host runtime delivery must remain false")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player proof must stay zero")
    require(runtime.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots mismatch")
    require(runtime.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")
    require(runtime.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected route slots mismatch")
    require(runtime.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    return runtime


def require_nonclaims_and_release(bundle: dict[str, Any]) -> dict[str, Any]:
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    release = object_at(bundle, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key in (
        "rawPrivateProofPathPublished",
        "rawPrivateArtifactContentPublished",
        "absolutePrivatePathPublished",
        "rawRuntimePointerPublished",
        "rawRuntimePidPublished",
        "rawCdbLogPathPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(release.get(key) is False, f"release boundary must remain false: {key}")
    return nonclaims


def validate_bundle(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    path = path.resolve()
    bundle = read_json(path)
    require_no_sensitive_fields(bundle)
    require_helper_contract(bundle)
    (
        second_path,
        second_summary,
        second_payload,
        executor_path,
        executor_summary,
        host_path,
        host_summary,
        host_payload,
        host_remote_path,
        host_remote_payload,
        delivery_path,
        delivery_summary,
        runtime_path,
    ) = require_source_artifacts(bundle)
    require_bridge(
        bundle,
        second_summary=second_summary,
        second_payload=second_payload,
        executor_summary=executor_summary,
        host_summary=host_summary,
        host_payload=host_payload,
        host_remote_payload=host_remote_payload,
        delivery_summary=delivery_summary,
    )
    runtime = require_runtime(bundle, executor_summary, allow_fixture=allow_fixture)
    nonclaims = require_nonclaims_and_release(bundle)
    claim = str(bundle.get("claimBoundary") or "")
    for token in (
        "checker-accepted second-host/private-LAN P2 command-source artifact",
        "copied original-BEA level-850/config-1 host-authority runtime delivery route",
        "does not prove player-ready online multiplayer",
        "accepted live second-host runtime delivery",
        "native BEA netcode",
        "active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": public_path(path),
        "schemaVersion": bundle["schemaVersion"],
        "bridgeScope": bundle["bridgeScope"],
        "secondHostRuntimeDeliveryBridgeProven": True,
        "secondHostCommandSourceProof": public_path(second_path),
        "runtimeExecutorProof": public_path(executor_path),
        "hostAuthorityTwoClientProof": public_path(host_path),
        "runtimeDeliveryProof": public_path(delivery_path),
        "liveRuntimeArtifact": public_path(runtime_path),
        "secondHostAcceptedCommandId": second_summary["acceptedCommandId"],
        "wouldForwardToPrivateLanCommandId": second_summary["wouldForwardToPrivateLanCommandId"],
        "commandSourceKind": second_summary["commandSourceKind"],
        "secondPhysicalHostProof": second_summary["secondPhysicalHostProof"],
        "runtimeExecutorReceiptMode": runtime["runtimeExecutorReceiptMode"],
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": runtime["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": runtime["hostHelperInputSent"],
        "runtimeDrivenBySecondHostCommandSource": runtime["runtimeDrivenBySecondHostCommandSource"],
        "acceptedLiveSecondHostRuntimeDeliveryProof": runtime["acceptedLiveSecondHostRuntimeDeliveryProof"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "multiHostLanPlayProof": nonclaims["multiHostLanPlayProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "nPlayerOriginalBinaryRuntimeProof": runtime["nPlayerOriginalBinaryRuntimeProof"],
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        tmp = Path(raw_tmp)
        executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
        executor_payload = executor_check.read_json(executor_path)
        host_path = builder.resolve_executor_reference(
            executor_path,
            str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""),
        )
        second_path = builder.make_source_bound_second_host_fixture(tmp, host_path)
        output_path = tmp / "bridge" / "second-host-runtime-delivery-bridge-proof.json"
        summary = builder.build_bundle(second_path, executor_path, output_path, allow_fixture_executor=True)
        require(summary["secondHostRuntimeDeliveryBridgeProven"] is True, "self-test fixture was not accepted")

    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        tmp = Path(raw_tmp)
        executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
        executor_payload = executor_check.read_json(executor_path)
        host_path = builder.resolve_executor_reference(
            executor_path,
            str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""),
        )
        second_path = builder.make_source_bound_second_host_fixture(tmp, host_path)
        output_path = tmp / "bridge" / "second-host-runtime-delivery-bridge-proof.json"
        builder.build_bundle(second_path, executor_path, output_path, allow_fixture_executor=True)
        payload = read_json(output_path)
        payload["runtimeEvidence"]["runtimeDrivenBySecondHostCommandSource"] = True
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        try:
            validate_bundle(output_path, allow_fixture=True)
        except SecondHostRuntimeDeliveryBridgeError:
            pass
        else:
            raise AssertionError("runtime-driven-by-second-host overclaim should fail validation")


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path}: missing token {token!r}")


def validate_contract(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    require_no_sensitive_fields(payload)
    require(payload.get("schemaVersion") == builder.SCHEMA, "contract schema mismatch")
    require(payload.get("bridgeScope") == builder.BRIDGE_SCOPE, "contract bridge scope mismatch")
    required_inputs = object_at(payload, "requiredInputs")
    require(
        required_inputs.get("requiresUpstreamPrivateLanProofHashMatch") is True,
        "contract upstream private-LAN proof hash requirement missing",
    )
    require(
        required_inputs.get("requiresHostAuthorityPrivateRemoteClientProofBinding") is True,
        "contract host-authority private remote-client binding requirement missing",
    )
    evidence = object_at(payload, "currentEvidence")
    for key in (
        "acceptedLiveSecondHostCommandSourceProof",
        "acceptedLiveSecondHostRuntimeDeliveryProof",
        "runtimeDrivenBySecondHostCommandSource",
        "hostJoinControlsMayBeEnabled",
        "baseOnlineMultiplayerReady",
        "multiHostLanPlayProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
    ):
        require(evidence.get(key) is False, f"contract evidence must remain false: {key}")
    require(evidence.get("adapterReady") is True, "contract adapter readiness missing")
    return payload


def validate_repo() -> dict[str, Any]:
    failures: list[str] = []
    validate_contract(CONTRACT)
    for path, tokens in {
        READINESS: (
            builder.SCHEMA,
            builder.BRIDGE_SCOPE,
            "secondHostRuntimeDeliveryBridgeAdapterReady=true",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
            "runtimeDrivenBySecondHostCommandSource=false",
            "upstreamPrivateLanProofHashMatch=true",
            "baseOnlineMultiplayerReady=false",
            "privateProofReleaseExcludedByPolicy=true",
        ),
        FEASIBILITY: (
            "Second-host runtime-delivery bridge adapter",
            builder.BRIDGE_SCOPE,
            "secondHostRuntimeDeliveryBridgeAdapterReady=true",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
            "runtimeDrivenBySecondHostCommandSource=false",
            "upstreamPrivateLanProofHashMatch=true",
            "baseOnlineMultiplayerReady=false",
        ),
        REGISTER: (
            "second-host runtime-delivery bridge adapter",
            builder.BRIDGE_SCOPE,
            "secondHostRuntimeDeliveryBridgeAdapterReady=true",
            "host-runtime-delivery-from-source-bound-distinct-command-source remains unproven",
            "upstreamPrivateLanProofHashMatch=true",
            "baseOnlineMultiplayerReady=false",
        ),
        CAPABILITIES: (
            "second-host runtime-delivery bridge adapter",
            builder.BRIDGE_SCOPE,
            "secondHostRuntimeDeliveryBridgeAdapterReady=true",
            "upstreamPrivateLanProofHashMatch=true",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
        ),
        LOCAL_CONTRACT: (
            "Second-host runtime-delivery bridge adapter",
            builder.BRIDGE_SCOPE,
            "upstreamPrivateLanProofHashMatch=true",
            "runtimeDrivenBySecondHostCommandSource=false",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
        ),
    }.items():
        for token in tokens:
            check_token(path, token, failures)
    if read_text(REGISTER) != read_text(REGISTER_MIRROR):
        failures.append("register lore mirror mismatch")
    if read_text(FEASIBILITY) != read_text(FEASIBILITY_MIRROR):
        failures.append("online feasibility lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("current capabilities lore mirror mismatch")
    if read_text(LOCAL_CONTRACT) != read_text(LOCAL_CONTRACT_MIRROR):
        failures.append("local multiplayer contract lore mirror mismatch")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-second-host-runtime-delivery-bridge") != EXPECTED_SCRIPT:
        failures.append("package second-host runtime-delivery bridge script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-second-host-runtime-delivery-bridge" not in aggregate:
        failures.append("aggregate runtime script missing second-host runtime-delivery bridge")
    if failures:
        raise SecondHostRuntimeDeliveryBridgeError("\n".join(failures))
    return {
        "contract": str(CONTRACT),
        "bridgeScope": builder.BRIDGE_SCOPE,
        "secondHostRuntimeDeliveryBridgeAdapterReady": True,
        "acceptedLiveSecondHostRuntimeDeliveryProof": False,
        "runtimeDrivenBySecondHostCommandSource": False,
        "baseOnlineMultiplayerReady": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("--allow-fixture", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime-delivery bridge checker self-test: PASS")
        return 0
    if args.check:
        print(json.dumps(validate_repo(), indent=2, sort_keys=True))
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.proof, allow_fixture=args.allow_fixture), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecondHostRuntimeDeliveryBridgeError,
        builder.SecondHostRuntimeDeliveryBridgeBuildError,
        executor_check.HostAuthorityRuntimeExecutorError,
        executor_check.delivery.HostAuthorityRuntimeDeliveryError,
        executor_check.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor_check.delivery.host.remote.PrivateRemoteClientSmokeProofError,
        second_check.SecondHostCommandSourceProofError,
    ) as exc:
        print(f"WinUI original-binary second-host runtime-delivery bridge check: FAIL: {exc}")
        raise SystemExit(2)
