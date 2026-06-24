#!/usr/bin/env python3
"""Validate second-host command-source to copied-runtime executor proofs."""

from __future__ import annotations

import argparse
import json
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any

import build_winui_original_binary_second_host_runtime_executor_bundle as builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_second_host_command_source_check as second_check
import winui_safe_copy_online_second_host_runtime_delivery_bridge_check as bridge_check


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-second-host-runtime-executor.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_second_host_runtime_executor_2026-06-20.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
FEASIBILITY_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_second_host_runtime_executor_check_test.py && "
    r"py -3 tools\build_winui_original_binary_second_host_runtime_executor_bundle.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_second_host_runtime_executor_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_second_host_runtime_executor_check.py --check"
)
SENSITIVE_KEY_PARTS = ("credential", "secret", "token", "password", "authkey", "bearer")
REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS = builder.REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS


class SecondHostRuntimeExecutorError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimeExecutorError(message)


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
        raise SecondHostRuntimeExecutorError(f"referenced artifact escapes private proof root: {raw_path}") from exc
    require(resolved.is_file(), f"referenced artifact is missing: {resolved}")
    return resolved


def public_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(builder.PRIVATE_PROOF_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def sha256_json(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("runtimeExecutorScope") == builder.RUNTIME_EXECUTOR_SCOPE, "runtime executor scope mismatch")


def require_source_artifacts(
    bundle: dict[str, Any],
    *,
    allow_fixture: bool,
) -> tuple[Any, ...]:
    artifacts = object_at(bundle, "sourceArtifacts")
    second_path = resolve_artifact_path(str(artifacts.get("secondHostCommandSourceProof") or ""))
    host_path = resolve_artifact_path(str(artifacts.get("hostAuthorityTwoClientProof") or ""))
    host_remote_path = resolve_artifact_path(str(artifacts.get("hostAuthorityPrivateRemoteClientProof") or ""))
    executor_path = resolve_artifact_path(str(artifacts.get("runtimeExecutorProof") or ""))
    bridge_path = resolve_artifact_path(str(artifacts.get("bridgeProof") or ""))
    require(artifacts.get("secondHostCommandSourceProofSha256") == second_check.sha256_file(second_path), "second-host proof hash mismatch")
    require(artifacts.get("hostAuthorityTwoClientProofSha256") == executor_check.sha256_file(host_path), "host-authority proof hash mismatch")
    require(artifacts.get("hostAuthorityPrivateRemoteClientProofSha256") == executor_check.sha256_file(host_remote_path), "host-authority private remote-client proof hash mismatch")
    require(artifacts.get("runtimeExecutorProofSha256") == executor_check.sha256_file(executor_path), "runtime executor proof hash mismatch")
    require(artifacts.get("bridgeProofSha256") == executor_check.sha256_file(bridge_path), "bridge proof hash mismatch")
    second_summary = second_check.validate_bundle(second_path)
    second_payload = second_check.read_json(second_path)
    host_summary = executor_check.delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_payload = executor_check.delivery.host.read_json(host_path)
    resolved_remote = executor_check.delivery.host.resolve_artifact_path(host_path, str(host_payload.get("privateRemoteClientProofBundle") or ""))
    require(resolved_remote.resolve() == host_remote_path.resolve(), "host-authority private remote-client reference mismatch")
    host_remote_payload = executor_check.delivery.host.read_json(host_remote_path)
    executor_summary = executor_check.validate_executor_proof(executor_path)
    try:
        bridge_summary = bridge_check.validate_bundle(bridge_path, allow_fixture=allow_fixture)
    except bridge_check.SecondHostRuntimeDeliveryBridgeError as exc:
        raise SecondHostRuntimeExecutorError(f"bridge proof invalid: {exc}") from exc
    bridge_payload = bridge_check.read_json(bridge_path)
    bridge_artifacts = object_at(bridge_payload, "sourceArtifacts")
    executor_payload = executor_check.read_json(executor_path)
    resolved_host = executor_check.resolve_path(executor_path, str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""))
    resolved_delivery = executor_check.resolve_path(executor_path, str(executor_payload.get("runtimeDeliveryProofBundle") or ""))
    resolved_runtime = executor_check.resolve_path(executor_path, str(executor_payload.get("liveRuntimeArtifact") or ""))
    require(resolved_host.resolve() == host_path.resolve(), "executor host-authority reference mismatch")
    bridge_second_path = bridge_check.resolve_artifact_path(str(bridge_artifacts.get("secondHostCommandSourceProof") or ""))
    bridge_executor_path = bridge_check.resolve_artifact_path(str(bridge_artifacts.get("runtimeExecutorProof") or ""))
    bridge_host_path = bridge_check.resolve_artifact_path(str(bridge_artifacts.get("hostAuthorityTwoClientProof") or ""))
    bridge_host_remote_path = bridge_check.resolve_artifact_path(str(bridge_artifacts.get("hostAuthorityPrivateRemoteClientProof") or ""))
    bridge_delivery_path = bridge_check.resolve_artifact_path(str(bridge_artifacts.get("runtimeDeliveryProof") or ""))
    bridge_runtime_path = bridge_check.resolve_artifact_path(str(bridge_artifacts.get("liveRuntimeArtifact") or ""))
    require(bridge_second_path.resolve() == second_path.resolve(), "bridge second-host artifact reference mismatch")
    require(bridge_executor_path.resolve() == executor_path.resolve(), "bridge runtime-executor artifact reference mismatch")
    require(bridge_host_path.resolve() == host_path.resolve(), "bridge host-authority artifact reference mismatch")
    require(bridge_host_remote_path.resolve() == host_remote_path.resolve(), "bridge private remote-client artifact reference mismatch")
    require(bridge_delivery_path.resolve() == resolved_delivery.resolve(), "bridge runtime-delivery artifact reference mismatch")
    require(bridge_runtime_path.resolve() == resolved_runtime.resolve(), "bridge live-runtime artifact reference mismatch")
    for key in (
        "secondHostCommandSourceProofSha256",
        "runtimeExecutorProofSha256",
        "hostAuthorityTwoClientProofSha256",
        "hostAuthorityPrivateRemoteClientProofSha256",
    ):
        require(bridge_artifacts.get(key) == artifacts.get(key), f"bridge artifact hash mismatch: {key}")
    return second_summary, second_payload, host_summary, host_payload, host_remote_path, host_remote_payload, executor_summary, bridge_summary


def require_source_binding(
    bundle: dict[str, Any],
    *,
    second_summary: dict[str, Any],
    second_payload: dict[str, Any],
    host_summary: dict[str, Any],
    host_payload: dict[str, Any],
    host_remote_payload: dict[str, Any],
    executor_summary: dict[str, Any],
    allow_fixture: bool,
) -> dict[str, Any]:
    binding = object_at(bundle, "sourceBinding")
    second_descriptor = object_at(second_payload, "sessionDescriptor")
    host_descriptor = object_at(host_payload, "sessionDescriptor")
    host_remote_descriptor = object_at(host_remote_payload, "sessionDescriptor")
    second_commands = object_at(second_payload, "commands")
    second_authorization = object_at(second_payload, "authorization")
    second_identity = object_at(second_payload, "networkIdentityEvidence")
    second_invitation_lifecycle = object_at(second_payload, "invitationLifecycle")
    second_client_identity = object_at(second_identity, "client")
    accepted = second_commands.get("accepted")
    require(isinstance(accepted, list) and len(accepted) == 1, "second-host proof must contain one accepted command")
    second_command = accepted[0]
    require(isinstance(second_command, dict), "accepted second-host command must be an object")
    host_commands = object_at(host_descriptor, "allowedCommands")
    host_p2 = object_at(host_commands, "P2")
    host_p2_sequence = str(host_p2.get("mappedInputSequence") or "")
    host_p2_sequence_sha256 = sha256_text(host_p2_sequence)
    host_p2_runtime_route = "P2/inputDevice1/bottom-split-half"
    host_p2_input_device = 1
    session_match = second_descriptor.get("sessionCompatibilityKey") == host_descriptor.get("sessionCompatibilityKey")
    clean_match = second_descriptor.get("cleanSpecimenSha256") == host_descriptor.get("cleanSpecimenSha256")
    upstream_hash_match = second_descriptor.get("upstreamPrivateLanProofSha256") == host_remote_descriptor.get("upstreamPrivateLanProofSha256")
    relay_match = host_summary["relayPlanSha256"] == executor_summary["hostAuthorityRelayPlanSha256"]
    require(binding.get("requiredBeforeAcceptedLiveRuntimeDelivery") is True, "source binding must gate live runtime delivery")
    require(binding.get("acceptedSecondHostCommandPayloadSha256") == sha256_json(second_command), "accepted second-host command payload hash mismatch")
    require(binding.get("acceptedSecondHostCommandRequestEvent") == second_command["requestEvent"], "accepted second-host request event binding mismatch")
    require(binding.get("acceptedSecondHostCommandRequestPayloadSha256") == second_command["requestPayloadSha256"], "accepted second-host request payload hash binding mismatch")
    require(binding.get("acceptedSecondHostCommandResponseEvent") == second_command["responseEvent"], "accepted second-host response event binding mismatch")
    require(binding.get("acceptedSecondHostCommandResponsePayloadSha256") == second_command["responsePayloadSha256"], "accepted second-host response payload hash binding mismatch")
    require(binding.get("acceptedSecondHostCommandId") == second_command["commandId"], "accepted second-host command id binding mismatch")
    require(binding.get("acceptedSecondHostRemoteSlot") == second_command["remoteSlot"] == second_check.EXPECTED_REMOTE_SLOT, "accepted second-host slot binding mismatch")
    require(binding.get("acceptedSecondHostCommand") == second_command["command"], "accepted second-host command binding mismatch")
    require(binding.get("hostAuthorityAcceptedP2CommandId") == host_p2["commandId"] == executor_check.delivery.host.EXPECTED_P2_COMMAND_ID, "host-authority P2 command id binding mismatch")
    require(binding.get("hostAuthorityAcceptedP2Command") == host_p2["command"], "host-authority P2 command binding mismatch")
    require(binding.get("hostAuthorityAcceptedP2MappedInputSequence") == host_p2_sequence == executor_check.delivery.host.EXPECTED_P2_SEQUENCE, "host-authority P2 mapped sequence binding mismatch")
    require(binding.get("hostAuthorityAcceptedP2MappedInputSequenceSha256") == host_p2_sequence_sha256, "host-authority P2 mapped sequence hash binding mismatch")
    require(binding.get("hostAuthorityAcceptedP2RuntimeRoute") == host_p2_runtime_route, "host-authority P2 runtime route binding mismatch")
    require(binding.get("hostAuthorityAcceptedP2InputDevice") == host_p2_input_device, "host-authority P2 input device binding mismatch")
    require(binding.get("hostHelperInputBoundToAcceptedSecondHostCommand") is True, "host-helper accepted-command binding flag missing")
    require(binding.get("hostHelperInputBoundToMappedP2Sequence") is True, "host-helper mapped P2 sequence binding flag missing")
    require(binding.get("secondHostNetworkIdentityEvidenceSha256") == sha256_json(second_identity), "second-host identity evidence hash mismatch")
    require(binding.get("secondHostSourceSafetySha256") == sha256_json(object_at(second_payload, "sourceSafety")), "second-host source-safety hash mismatch")
    require(binding.get("secondHostAuthorizationSha256") == sha256_json(second_authorization), "second-host authorization hash mismatch")
    require(binding.get("secondHostInvitationLifecycleSha256") == sha256_json(second_invitation_lifecycle), "second-host invitation lifecycle hash mismatch")
    require(binding.get("secondHostInvitationLifecycleDeleted") is True, "second-host invitation lifecycle deletion receipt missing")
    require(binding.get("secondHostInvitationLifecyclePostDeleteAbsent") is True, "second-host invitation lifecycle post-delete absence receipt missing")
    require(binding.get("secondHostClientIdentityFingerprint") == second_authorization["clientIdentityFingerprint"], "second-host client identity fingerprint mismatch")
    require(binding.get("secondHostClientMachineFingerprint") == second_client_identity["machineFingerprint"], "second-host client machine fingerprint mismatch")
    require(binding.get("sessionCompatibilityKeyMatch") is session_match, "session compatibility match flag mismatch")
    require(binding.get("secondHostSessionCompatibilityKeySha256") == sha256_text(str(second_descriptor["sessionCompatibilityKey"])), "second-host session key hash mismatch")
    require(binding.get("hostAuthoritySessionCompatibilityKeySha256") == sha256_text(str(host_descriptor["sessionCompatibilityKey"])), "host-authority session key hash mismatch")
    require(binding.get("cleanSpecimenHashMatch") is clean_match, "clean specimen match flag mismatch")
    require(binding.get("secondHostCleanSpecimenSha256") == second_descriptor["cleanSpecimenSha256"], "second-host clean specimen hash mismatch")
    require(binding.get("hostAuthorityCleanSpecimenSha256") == host_descriptor["cleanSpecimenSha256"], "host-authority clean specimen hash mismatch")
    require(clean_match, "second-host and host-authority clean specimen hashes must match")
    require(binding.get("upstreamPrivateLanProofHashMatch") is upstream_hash_match, "upstream private-LAN proof hash match flag mismatch")
    require(binding.get("secondHostUpstreamPrivateLanProofSha256") == second_descriptor["upstreamPrivateLanProofSha256"], "second-host upstream private-LAN proof hash mismatch")
    require(binding.get("hostAuthorityPrivateRemoteClientUpstreamPrivateLanProofSha256") == host_remote_descriptor["upstreamPrivateLanProofSha256"], "host private remote-client upstream private-LAN proof hash mismatch")
    require(binding.get("hostAuthorityUpstreamPrivateRemoteClientProofSha256") == host_descriptor["upstreamPrivateRemoteClientProofSha256"], "host-authority upstream private remote-client proof hash mismatch")
    require(upstream_hash_match, "second-host and host-authority upstream private-LAN proof hashes must match")
    require(binding.get("privateLanCommandIdMatch") is True, "private-LAN command id match flag missing")
    require(binding.get("secondHostWouldForwardToPrivateLanCommandId") == second_summary["wouldForwardToPrivateLanCommandId"], "second-host private-LAN command id binding mismatch")
    require(binding.get("hostAuthorityUpstreamPrivateLanCommandId") == host_descriptor["upstreamPrivateLanCommandId"], "host-authority private-LAN command id binding mismatch")
    require(host_descriptor["upstreamPrivateLanCommandId"] == second_summary["wouldForwardToPrivateLanCommandId"], "host and second-host private-LAN command ids must match")
    require(binding.get("hostAuthorityRelayPlanMatch") is relay_match, "relay plan match flag mismatch")
    require(binding.get("hostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "host relay plan binding mismatch")
    require(binding.get("runtimeExecutorHostAuthorityRelayPlanSha256") == executor_summary["hostAuthorityRelayPlanSha256"], "runtime executor relay plan binding mismatch")
    require(relay_match, "host and runtime executor relay plan hashes must match")
    if allow_fixture:
        require(binding.get("bindingMode") in {"fixture-or-posthoc-compatibility-only", "live-second-host-to-runtime-bound-by-source-evidence"}, "unexpected fixture binding mode")
    else:
        require(binding.get("bindingMode") == "live-second-host-to-runtime-bound-by-source-evidence", "live proof requires source-bound binding mode")
        require(session_match, "live proof requires matching session compatibility keys")
    return binding


def require_second_host_security_hardening(second_payload: dict[str, Any]) -> None:
    hardening = second_payload.get("sessionSecurityHardening")
    require(isinstance(hardening, dict), "live second-host runtime proof requires sessionSecurityHardening")
    require(hardening.get("evidenceMode") == "live-server-client-transcript", "live second-host runtime proof requires live hardening evidence")
    require(hardening.get("liveNegativeCaseTranscript") is True, "live second-host runtime proof requires live negative-case transcript")
    require(hardening.get("requiredBeforeAcceptedLiveRuntimeDelivery") is True, "live second-host runtime proof requires hardening gate")
    for key in REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS:
        require(hardening.get(key) is True, f"live second-host runtime proof requires {key}=true")


def require_live_source_safety_preflight(second_payload: dict[str, Any]) -> None:
    source_safety = object_at(second_payload, "sourceSafety")
    require(source_safety.get("evidenceMode") == "local-preflight-computed", "live second-host runtime proof requires local source-safety preflight")
    require(source_safety.get("computedByPreflight") is True, "live second-host runtime proof requires computed source-safety preflight")
    for role in ("host", "client"):
        side = object_at(source_safety, role)
        require(side.get("sourceEvidenceMode") == "local-preflight-computed", f"live second-host runtime proof requires {role} local source-safety evidence")
        require(side.get("computedByPreflight") is True, f"live second-host runtime proof requires {role} computed source-safety evidence")
        require(side.get("pathValuesPublished") is False, f"live second-host runtime proof forbids {role} path publication")
        require(side.get("absolutePathsSerialized") is False, f"live second-host runtime proof forbids {role} absolute path serialization")
        require(int(side.get("copiedProfileFileCount") or 0) > 0, f"live second-host runtime proof requires {role} copied-profile file count")
        require(int(side.get("installedGameFileCount") or 0) > 0, f"live second-host runtime proof requires {role} installed-game file count")
        require(side.get("copiedProfileHashMode") != "operator-supplied-sha256", f"live second-host runtime proof rejects {role} operator copied-profile hash")
        require(side.get("installedGameHashMode") != "operator-supplied-sha256", f"live second-host runtime proof rejects {role} operator installed-game hash")
        require(side.get("programFilesMutationAttempted") is False, f"live second-host runtime proof forbids {role} Program Files mutation")


def require_executor(
    bundle: dict[str, Any],
    *,
    second_summary: dict[str, Any],
    second_payload: dict[str, Any],
    host_summary: dict[str, Any],
    host_payload: dict[str, Any],
    executor_summary: dict[str, Any],
    bridge_summary: dict[str, Any],
    allow_fixture: bool,
) -> dict[str, Any]:
    runtime_executor = object_at(bundle, "secondHostRuntimeExecutor")
    runtime = object_at(bundle, "runtimeEvidence")
    host_descriptor = object_at(host_payload, "sessionDescriptor")
    host_commands = object_at(host_descriptor, "allowedCommands")
    host_p2 = object_at(host_commands, "P2")
    host_p2_sequence = str(host_p2.get("mappedInputSequence") or "")
    host_p2_sequence_sha256 = sha256_text(host_p2_sequence)
    host_p2_runtime_route = "P2/inputDevice1/bottom-split-half"
    host_p2_input_device = 1
    require(runtime_executor.get("secondHostRuntimeExecutorProofBuilt") is True, "executor proof-built flag missing")
    require(runtime_executor.get("secondHostCommandSourceProofAccepted") is True, "second-host accepted flag missing")
    require(runtime_executor.get("secondHostSessionSecurityHardeningRequired") is True, "security hardening requirement flag missing")
    require(runtime_executor.get("secondHostAcceptedCommandId") == second_check.EXPECTED_COMMAND_ID, "accepted second-host command mismatch")
    require(runtime_executor.get("secondHostRemoteSlot") == second_check.EXPECTED_REMOTE_SLOT, "second-host remote slot mismatch")
    require(runtime_executor.get("secondHostCommand") == second_check.EXPECTED_REMOTE_COMMAND, "second-host command mismatch")
    require(runtime_executor.get("secondHostWouldForwardToPrivateLanCommandId") == second_summary["wouldForwardToPrivateLanCommandId"], "private-LAN command id mismatch")
    require(runtime_executor.get("hostAuthorityUpstreamPrivateLanCommandId") == second_summary["wouldForwardToPrivateLanCommandId"], "host upstream private-LAN id mismatch")
    require(runtime_executor.get("hostAuthorityAcceptedP2CommandId") == executor_check.delivery.host.EXPECTED_P2_COMMAND_ID, "host P2 command id mismatch")
    require(runtime_executor.get("hostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "host relay hash mismatch")
    require(runtime_executor.get("runtimeExecutorHostAuthorityRelayPlanSha256") == executor_summary["hostAuthorityRelayPlanSha256"], "executor relay hash mismatch")
    require(runtime_executor.get("upstreamPrivateLanProofHashMatch") is True, "upstream private-LAN proof hash match flag missing")
    require(runtime_executor.get("secondHostDirectRuntimeCausalityProofRequired") is True, "direct second-host runtime causality gate missing")
    require(runtime_executor.get("bridgeAdapterAccepted") is True, "bridge adapter acceptance missing")
    require(runtime_executor.get("bridgeAdapterRuntimeDrivenFlag") == bridge_summary["runtimeDrivenBySecondHostCommandSource"] is False, "bridge adapter must preserve post-hoc boundary")
    require(runtime.get("safeCopyLaunchLevel") == 850, "safe-copy launch level mismatch")
    require(runtime.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(runtime.get("visualCaptureCount") == executor_summary["visualCaptureCount"], "visual capture count mismatch")
    require(runtime.get("deliveredOriginalBinaryCommandCount") == executor_summary["deliveredOriginalBinaryCommandCount"] == 2, "delivered command count mismatch")
    require(runtime.get("hostHelperInputSent") is True, "host-helper input flag missing")
    require(runtime.get("hostHelperInputBoundToSecondHostCommandSource") is True, "host-helper source-bound input flag missing")
    require(runtime.get("hostHelperInputDeliveryAuthority") == "host-helper-on-host-from-accepted-second-host-command-source", "host-helper delivery authority mismatch")
    require(runtime.get("hostHelperBoundAcceptedSecondHostCommandId") == second_summary["acceptedCommandId"], "host-helper accepted second-host command id mismatch")
    require(runtime.get("hostHelperBoundHostAuthorityCommandId") == host_p2["commandId"] == executor_check.delivery.host.EXPECTED_P2_COMMAND_ID, "host-helper host-authority command id mismatch")
    require(runtime.get("hostHelperBoundRemoteSlot") == second_check.EXPECTED_REMOTE_SLOT, "host-helper remote slot mismatch")
    require(runtime.get("hostHelperMappedInputSequence") == host_p2_sequence == executor_check.delivery.host.EXPECTED_P2_SEQUENCE, "host-helper mapped input sequence mismatch")
    require(runtime.get("hostHelperMappedInputSequenceSha256") == host_p2_sequence_sha256, "host-helper mapped input sequence hash mismatch")
    require(runtime.get("hostHelperRuntimeRoute") == host_p2_runtime_route, "host-helper runtime route mismatch")
    require(runtime.get("hostHelperInputDevice") == host_p2_input_device, "host-helper input device mismatch")
    require(runtime.get("gameInputSentBySecondHostClient") is False, "second-host client must not claim direct game input")
    require(runtime.get("gameInputSentByHostAuthorityScheduler") is False, "host-authority scheduler must not claim direct game input")
    require(runtime.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots mismatch")
    require(runtime.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")
    require(runtime.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected route slots mismatch")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(runtime.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    receipt_mode = str(runtime.get("runtimeExecutorReceiptMode") or "")
    if allow_fixture:
        require(receipt_mode in {"self-test-fixture", "live-executor-subprocess"}, "unexpected fixture receipt mode")
        require(runtime_executor.get("runtimeInputDerivedFromHostAuthorityProof") in {False, True}, "fixture host-authority-derived flag mismatch")
        require(runtime_executor.get("runtimeInputDerivedFromSecondHostCommandSource") is False, "fixture must not claim second-host-derived runtime")
        require(runtime_executor.get("runtimeDrivenBySecondHostCommandSource") is False, "fixture must not claim second-host-driven runtime")
        require(runtime_executor.get("acceptedLiveSecondHostRuntimeDeliveryProof") is False, "fixture must not claim accepted live second-host runtime delivery")
        require(runtime_executor.get("secondHostSessionSecurityHardeningAccepted") is False, "fixture must not claim second-host security hardening")
        require(runtime.get("newBeaLaunchCount") == 0, "fixture must not record a new BEA launch")
        require(runtime.get("cdbAttachCount") == 0, "fixture must not record a CDB attach")
    else:
        require_second_host_security_hardening(second_payload)
        require_live_source_safety_preflight(second_payload)
        require(receipt_mode == "live-executor-subprocess", "live proof must use live executor receipt")
        require(runtime_executor.get("runtimeInputDerivedFromHostAuthorityProof") is True, "live compatibility proof must derive runtime input from host-authority proof")
        require(runtime_executor.get("runtimeInputDerivedFromSecondHostCommandSource") is False, "live compatibility proof must not claim direct second-host-derived runtime")
        require(runtime_executor.get("runtimeDrivenBySecondHostCommandSource") is False, "live compatibility proof must not claim second-host-driven runtime")
        require(runtime_executor.get("acceptedLiveSecondHostRuntimeDeliveryProof") is False, "live compatibility proof must not claim accepted second-host runtime delivery")
        require(runtime_executor.get("secondHostSessionSecurityHardeningAccepted") is True, "live proof must accept second-host security hardening")
        require(runtime.get("newBeaLaunchCount") == 1, "live proof must record one BEA launch")
        require(runtime.get("cdbAttachCount") == 1, "live proof must record one CDB attach")
    return runtime_executor


def require_nonclaims_and_release(bundle: dict[str, Any]) -> None:
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


def validate_bundle(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    payload = read_json(path)
    require_no_sensitive_fields(payload)
    require_helper_contract(payload)
    second_summary, second_payload, host_summary, host_payload, _host_remote_path, host_remote_payload, executor_summary, bridge_summary = require_source_artifacts(
        payload,
        allow_fixture=allow_fixture,
    )
    require_source_binding(
        payload,
        second_summary=second_summary,
        second_payload=second_payload,
        host_summary=host_summary,
        host_payload=host_payload,
        host_remote_payload=host_remote_payload,
        executor_summary=executor_summary,
        allow_fixture=allow_fixture,
    )
    runtime_executor = require_executor(
        payload,
        second_summary=second_summary,
        second_payload=second_payload,
        host_summary=host_summary,
        host_payload=host_payload,
        executor_summary=executor_summary,
        bridge_summary=bridge_summary,
        allow_fixture=allow_fixture,
    )
    require_nonclaims_and_release(payload)
    claim = str(payload.get("claimBoundary") or "")
    for token in (
        "checker-accepted second-host/private-LAN P2 command-source proof",
        "fresh copied original-BEA level-850/config-1 host-authority runtime executor run",
        "does not prove player-ready online multiplayer",
        "Host/Join enablement",
        "native BEA netcode",
        "active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": public_path(path),
        "schemaVersion": payload["schemaVersion"],
        "runtimeExecutorScope": payload["runtimeExecutorScope"],
        "secondHostRuntimeExecutorProofBuilt": runtime_executor["secondHostRuntimeExecutorProofBuilt"],
        "secondHostAcceptedCommandId": runtime_executor["secondHostAcceptedCommandId"],
        "runtimeInputDerivedFromSecondHostCommandSource": runtime_executor["runtimeInputDerivedFromSecondHostCommandSource"],
        "runtimeDrivenBySecondHostCommandSource": runtime_executor["runtimeDrivenBySecondHostCommandSource"],
        "acceptedLiveSecondHostRuntimeDeliveryProof": runtime_executor["acceptedLiveSecondHostRuntimeDeliveryProof"],
        "baseOnlineMultiplayerReady": False,
        "hostJoinControlsMayBeEnabled": False,
        "nativeBeaNetcodeProof": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
    }


def validate_contract(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    require_no_sensitive_fields(payload)
    require(payload.get("schemaVersion") == builder.SCHEMA, "contract schema mismatch")
    require(payload.get("runtimeExecutorScope") == builder.RUNTIME_EXECUTOR_SCOPE, "contract scope mismatch")
    blockers = object_at(payload, "livePromotionBlockers")
    require(
        blockers.get("requiredSecondHostSecurityHardeningFlags") == list(REQUIRED_SECOND_HOST_SECURITY_HARDENING_FLAGS),
        "contract second-host security hardening flags mismatch",
    )
    require(blockers.get("requiresSourceBindingEvidence") is True, "contract source-binding requirement missing")
    require(
        blockers.get("requiresAcceptedCommandTranscriptHashBinding") is True,
        "contract accepted-command transcript hash binding requirement missing",
    )
    require(
        blockers.get("requiresInvitationLifecycleHashBinding") is True,
        "contract invitation lifecycle hash binding requirement missing",
    )
    require(
        blockers.get("requiresLocalSourceSafetyPreflightForLiveRuntime") is True,
        "contract live source-safety preflight requirement missing",
    )
    required_inputs = object_at(payload, "requiredInputs")
    require(
        required_inputs.get("requiresAcceptedCommandTranscriptBinding") is True,
        "contract accepted-command transcript binding input requirement missing",
    )
    require(
        required_inputs.get("requiresLocalSourceSafetyPreflightForLiveRuntime") is True,
        "contract live source-safety preflight input requirement missing",
    )
    require(
        required_inputs.get("requiresUpstreamPrivateLanProofHashMatch") is True,
        "contract upstream private-LAN proof hash input requirement missing",
    )
    require(
        required_inputs.get("requiresBridgeProofSameBundleOwnership") is True,
        "contract same-bundle bridge ownership input requirement missing",
    )
    require(
        required_inputs.get("requiresInvitationLifecycleHashBinding") is True,
        "contract invitation lifecycle binding input requirement missing",
    )
    require(
        required_inputs.get("requiresMappedP2SequenceReceipt") is True,
        "contract mapped P2 sequence receipt input requirement missing",
    )
    require(
        required_inputs.get("requiresHostHelperReceiptBoundToMappedP2Sequence") is True,
        "contract host-helper mapped P2 receipt input requirement missing",
    )
    evidence = object_at(payload, "currentEvidence")
    require(
        blockers.get("requiresUpstreamPrivateLanProofHashMatch") is True,
        "contract upstream private-LAN proof hash blocker missing",
    )
    require(
        blockers.get("requiresBridgeProofSameBundleOwnership") is True,
        "contract same-bundle bridge ownership blocker missing",
    )
    require(
        blockers.get("requiresDirectSecondHostRuntimeCausalityReceipt") is True,
        "contract direct second-host runtime causality blocker missing",
    )
    require(
        blockers.get("requiresHostHelperInputBoundToSecondHostCommandSource") is True,
        "contract host-helper source-bound input blocker missing",
    )
    require(
        blockers.get("requiresMappedP2SequenceReceipt") is True,
        "contract mapped P2 sequence receipt blocker missing",
    )
    require(evidence.get("runtimeExecutorBuilderReady") is True, "contract builder readiness missing")
    for key in (
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
    return payload


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path}: missing token {token!r}")


def validate_repo() -> dict[str, Any]:
    failures: list[str] = []
    validate_contract(CONTRACT)
    for path, tokens in {
        READINESS: (
            builder.SCHEMA,
            builder.RUNTIME_EXECUTOR_SCOPE,
            "runtimeExecutorBuilderReady=true",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
            "runtimeDrivenBySecondHostCommandSource=false",
            "sourceBinding.requiredBeforeAcceptedLiveRuntimeDelivery=true",
            "sourceBinding.sessionCompatibilityKeyMatch=true",
            "sourceBinding.upstreamPrivateLanProofHashMatch=true",
            "sourceBinding.secondHostInvitationLifecycleSha256",
            "sourceSafety.evidenceMode=local-preflight-computed",
            "bridgeProofSameBundleOwnership=true",
            "baseOnlineMultiplayerReady=false",
            "privateProofReleaseExcludedByPolicy=true",
        ),
        FEASIBILITY: (
            "Second-host runtime executor builder",
            builder.RUNTIME_EXECUTOR_SCOPE,
            "runtimeExecutorBuilderReady=true",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
            "runtimeDrivenBySecondHostCommandSource=false",
            "upstreamPrivateLanProofHashMatch=true",
            "bridgeProofSameBundleOwnership=true",
            "baseOnlineMultiplayerReady=false",
        ),
        REGISTER: (
            "second-host runtime executor builder",
            builder.RUNTIME_EXECUTOR_SCOPE,
            "runtimeExecutorBuilderReady=true",
            "acceptedLiveSecondHostRuntimeDeliveryProof=false",
            "bridgeProofSameBundleOwnership=true",
            "Host/Join remains disabled",
        ),
        CAPABILITIES: (
            "second-host runtime executor builder",
            builder.RUNTIME_EXECUTOR_SCOPE,
            "runtimeExecutorBuilderReady=true",
            "bridgeProofSameBundleOwnership=true",
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
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-second-host-runtime-executor") != EXPECTED_SCRIPT:
        failures.append("package second-host runtime executor script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-second-host-runtime-executor" not in aggregate:
        failures.append("aggregate runtime script missing second-host runtime executor")
    if failures:
        raise SecondHostRuntimeExecutorError("\n".join(failures))
    return {
        "contract": str(CONTRACT),
        "runtimeExecutorScope": builder.RUNTIME_EXECUTOR_SCOPE,
        "runtimeExecutorBuilderReady": True,
        "acceptedLiveSecondHostRuntimeDeliveryProof": False,
        "runtimeDrivenBySecondHostCommandSource": False,
        "baseOnlineMultiplayerReady": False,
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        root = Path(raw_tmp)
        host_path = executor_check.delivery.host.make_bundle_fixture(root / "host-authority")
        second_path = builder.bridge_builder.make_source_bound_second_host_fixture(root, host_path)
        output_path = root / "executor" / "second-host-runtime-executor-proof.json"
        builder.build_bundle(second_path, host_path, output_path, artifact_root=root / "runtime", allow_fixture_executor=True)
        summary = validate_bundle(output_path, allow_fixture=True)
        require(summary["acceptedLiveSecondHostRuntimeDeliveryProof"] is False, "fixture self-test must remain non-live")

    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        root = Path(raw_tmp)
        host_path = executor_check.delivery.host.make_bundle_fixture(root / "host-authority")
        second_path = builder.bridge_builder.make_source_bound_second_host_fixture(root, host_path)
        output_path = root / "executor" / "second-host-runtime-executor-proof.json"
        builder.build_bundle(second_path, host_path, output_path, artifact_root=root / "runtime", allow_fixture_executor=True)
        payload = read_json(output_path)
        payload["nonClaims"]["baseOnlineMultiplayerReady"] = True
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            validate_bundle(output_path, allow_fixture=True)
        except SecondHostRuntimeExecutorError:
            pass
        else:
            raise AssertionError("base online overclaim should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("--allow-fixture", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime executor checker self-test: PASS")
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
        SecondHostRuntimeExecutorError,
        builder.SecondHostRuntimeExecutorBuildError,
        executor_check.HostAuthorityRuntimeExecutorError,
        executor_check.delivery.HostAuthorityRuntimeDeliveryError,
        executor_check.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor_check.delivery.host.remote.PrivateRemoteClientSmokeProofError,
        second_check.SecondHostCommandSourceProofError,
        bridge_check.SecondHostRuntimeDeliveryBridgeError,
    ) as exc:
        print(f"WinUI original-binary second-host runtime executor check: FAIL: {exc}")
        raise SystemExit(2)
