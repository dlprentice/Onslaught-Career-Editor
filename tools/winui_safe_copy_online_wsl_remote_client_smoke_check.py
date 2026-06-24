#!/usr/bin/env python3
"""Validate a WSL2 remote-client smoke proof for original-binary online groundwork."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_wsl_remote_client_smoke_bundle as builder
import winui_safe_copy_online_private_lan_transport_smoke_check as lan


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "original_binary_wsl_remote_client_smoke_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCHEMA = builder.SCHEMA
EXPECTED_SESSION_SCHEMA = builder.SESSION_SCHEMA
EXPECTED_TRANSPORT = builder.TRANSPORT
EXPECTED_PROTOCOL = builder.PROTOCOL
EXPECTED_HELPER = builder.HELPER
EXPECTED_HELPER_VERSION = builder.HELPER_VERSION
EXPECTED_COMMAND_ID = builder.COMMAND_ID
EXPECTED_REJECTED_P3_COMMAND_ID = builder.REJECTED_P3_COMMAND_ID
EXPECTED_RATE_LIMIT_COMMAND_ID = builder.RATE_LIMIT_COMMAND_ID
EXPECTED_PRIVATE_LAN_COMMAND_ID = builder.EXPECTED_LAN_COMMAND_ID
EXPECTED_REMOTE_SLOT = builder.EXPECTED_REMOTE_SLOT
EXPECTED_REMOTE_COMMAND = builder.EXPECTED_REMOTE_COMMAND
EXPECTED_MAPPED_SEQUENCE = builder.EXPECTED_MAPPED_SEQUENCE
EXPECTED_ACTIVE_SLOTS = builder.ACTIVE_SLOTS
EXPECTED_METADATA_SLOTS = builder.METADATA_SLOTS
EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_wsl_remote_client_smoke_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_wsl_remote_client_smoke_check.py --check"
)


class WslRemoteClientSmokeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WslRemoteClientSmokeProofError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


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
    require(candidate.is_file(), f"referenced private LAN transport proof is missing: {candidate}")
    return candidate


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if lowered not in {
                "authkeyfingerprint",
                "credentialstorage",
                "serializedcredentialpresent",
                "credentialtransporttoclientprocess",
                "clientcommandlinecontainscredential",
                "clientenvironmentcontainscredential",
                "clientstdoutcontainscredential",
                "clientstderrcontainscredential",
            }:
                require(
                    not any(fragment in lowered for fragment in ("secret", "password", "token", "authkey", "credential", "apikey", "api_key")),
                    f"serialized credential-like field is not allowed at {path}.{key}",
                )
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected WSL remote-client smoke schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected WSL remote-client smoke helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected WSL remote-client smoke helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected WSL remote-client smoke protocol")


def require_private_lan_reference(bundle: dict[str, Any], path: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    private_lan_path = resolve_artifact_path(path, str(bundle.get("privateLanTransportProofBundle", "")))
    require(str(bundle.get("privateLanTransportProofSha256", "")).lower() == lan.sha256_file(private_lan_path), "private LAN transport proof hash mismatch")
    summary = lan.validate_bundle(private_lan_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_path)
    return private_lan_path, summary, private_lan_bundle


def require_session_descriptor(
    bundle: dict[str, Any],
    *,
    private_lan_path: Path,
    private_lan_summary: dict[str, Any],
    private_lan_bundle: dict[str, Any],
) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "unexpected WSL remote-client session schema")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "WSL remote-client session protocol mismatch")
    require(descriptor.get("upstreamPrivateLanProtocolVersion") == lan.EXPECTED_PROTOCOL, "upstream private LAN protocol mismatch")
    require(descriptor.get("upstreamPrivateLanProofSha256") == lan.sha256_file(private_lan_path), "upstream private LAN hash mismatch")
    require(descriptor.get("upstreamPrivateLanTransport") == private_lan_summary["transport"], "upstream private LAN transport mismatch")
    require(descriptor.get("sessionCompatibilityKey") == upstream_descriptor["sessionCompatibilityKey"], "session compatibility key mismatch")
    require(descriptor.get("cleanSpecimenSha256") == upstream_descriptor["cleanSpecimenSha256"], "clean specimen hash mismatch")
    require(descriptor.get("remotePlayerSlot") == EXPECTED_REMOTE_SLOT, "WSL remote-client smoke must target P2")
    require(descriptor.get("allowedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "active gameplay slots must stay P1/P2")
    require(descriptor.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata-only slots must stay P3/P4")
    require(descriptor.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "P3/P4 gameplay routes must be rejected")
    require(descriptor.get("allowedCommand") == EXPECTED_REMOTE_COMMAND, "WSL remote-client command mismatch")
    require(descriptor.get("mappedInputSequence") == EXPECTED_MAPPED_SEQUENCE, "mapped input sequence mismatch")
    require(descriptor.get("upstreamPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "wrong upstream private LAN command id")
    require(descriptor.get("upstreamPrivateRelayCommandId") == private_lan_summary["wouldForwardToPrivateRelayCommandId"], "wrong upstream private relay command id")
    require(descriptor.get("upstreamPrivateRelayDeliveryEvidence") == private_lan_summary["upstreamPrivateRelay"]["gameInputDeliveryEvidence"], "private relay delivery evidence mismatch")
    require(descriptor.get("levelId") == 850, "session level must remain 850")
    require(descriptor.get("controllerConfiguration") == 1, "session controller configuration must remain 1")
    require(descriptor.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player original-binary runtime proof must remain zero")
    require(descriptor.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 gameplay proof must remain false")
    return descriptor


def require_transport(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == EXPECTED_TRANSPORT, "unexpected WSL remote-client transport")
    port = transport.get("actualBindPort")
    require(isinstance(port, int) and 0 < port < 65536, "actualBindPort must be a TCP port")
    require(transport.get("networkScope") == "wsl2-to-windows-host-private-interface-smoke", "unexpected WSL remote-client network scope")
    require(transport.get("loopbackInterfaceOnly") is False, "WSL smoke must not be loopback-only")
    require(transport.get("privateInterfaceBound") is True, "WSL smoke must bind a Windows private interface")
    require(transport.get("privateInterfaceSocketOpened") is True, "WSL smoke must open a private-interface TCP socket")
    require(transport.get("wsl2ClientProcess") is True, "WSL smoke must use a WSL2 client process")
    require(transport.get("crossEnvironmentClient") is True, "WSL smoke must prove a cross-environment client")
    require(transport.get("samePhysicalMachineOnly") is True, "WSL smoke must record same-physical-machine boundary")
    require(transport.get("secondPhysicalHostClaim") is False, "WSL smoke must not claim second physical host proof")
    require(transport.get("multiHostLanClaim") is False, "WSL smoke must not claim multi-host LAN play")
    require(transport.get("publicNetworkSocketsOpened") is False, "WSL smoke must not open public sockets")
    require(transport.get("publicMatchmakingClaim") is False, "WSL smoke must not claim public matchmaking")
    require(transport.get("matchmakingServerContacted") is False, "WSL smoke must not contact matchmaking")
    require(transport.get("publicServerClaim") is False, "WSL smoke must not claim public server behavior")
    require(transport.get("nativeBeaNetcodeClaim") is False, "WSL smoke must not claim native BEA netcode")
    require(transport.get("natTraversalClaim") is False, "WSL smoke must not claim NAT traversal")
    require(transport.get("deterministicSyncClaim") is False, "WSL smoke must not claim deterministic sync")
    require(transport.get("rollbackClaim") is False, "WSL smoke must not claim rollback")
    require(transport.get("antiCheatClaim") is False, "WSL smoke must not claim anti-cheat")
    require(transport.get("physicalGamepadClaim") is False, "WSL smoke must not claim physical gamepad behavior")
    require(transport.get("rebuildParityClaim") is False, "WSL smoke must not claim rebuild parity")
    require(transport.get("gameInputSentByWslClient") is False, "WSL smoke must not claim direct game input")
    require(transport.get("hostHelperInputSent") is False, "WSL smoke must not claim new host-helper input")
    return transport


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must be false")
    require(isinstance(authorization.get("authKeyFingerprint"), str) and len(authorization["authKeyFingerprint"]) == 64, "auth key fingerprint missing")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(authorization.get("clientIdentityMode") == "pinned-fingerprint", "client identity mode mismatch")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("sequenceEnforced") is True, "sequence must be enforced")
    rate_limit = object_at(authorization, "rateLimit")
    require(rate_limit.get("maxAcceptedCommandsPerSession") == 1, "accepted command rate limit mismatch")
    return authorization


def require_process_boundary(bundle: dict[str, Any]) -> dict[str, Any]:
    boundary = object_at(bundle, "clientProcessBoundary")
    require(boundary.get("processModel") == "wsl2-python-process", "unexpected WSL client process model")
    require(isinstance(boundary.get("windowsBuilderProcessId"), int) and boundary["windowsBuilderProcessId"] > 0, "builder pid must be positive")
    require(isinstance(boundary.get("wslLauncherWindowsProcessId"), int) and boundary["wslLauncherWindowsProcessId"] > 0, "launcher pid must be positive")
    require(isinstance(boundary.get("wslClientProcessId"), int) and boundary["wslClientProcessId"] > 0, "WSL client pid must be positive")
    require(boundary.get("clientExitCode") == 0, "WSL client process must exit cleanly")
    require(boundary.get("clientVerifiedServerIdentity") is True, "WSL client must verify pinned server identity")
    runtime = object_at(boundary, "wslClientRuntime")
    require(runtime.get("clientKind") == "wsl2-linux-python-client", "WSL client kind mismatch")
    require(isinstance(runtime.get("hostname"), str) and runtime["hostname"], "WSL hostname missing")
    require(isinstance(runtime.get("pythonVersion"), str) and runtime["pythonVersion"], "WSL python version missing")
    require(isinstance(runtime.get("networkAddress"), str) and runtime["networkAddress"], "WSL network address missing")
    require(isinstance(runtime.get("peerAddress"), str) and runtime["peerAddress"], "WSL peer address missing")
    require(boundary.get("clientCommandLineContainsCredential") is False, "credential must not be placed on command line")
    require(boundary.get("clientEnvironmentContainsCredential") is False, "credential must not be placed in environment")
    require(boundary.get("clientStdoutContainsCredential") is False, "credential must not leak through stdout")
    require(boundary.get("clientStderrContainsCredential") is False, "credential must not leak through stderr")
    require(boundary.get("credentialTransportToClientProcess") == "stdin-ephemeral-not-serialized-to-artifact", "unexpected credential transport boundary")
    require(boundary.get("childEnvSensitiveKeyCount") == 0, "sanitized child env must not carry sensitive-looking keys")
    require(boundary.get("samePhysicalMachineOnly") is True, "WSL boundary must record same-physical-machine proof")
    require(boundary.get("secondPhysicalHostClaim") is False, "WSL boundary must not claim second physical host")
    require(boundary.get("multiHostLanClaim") is False, "WSL boundary must not claim multi-host LAN")
    labels = [row.get("label") for row in list_at(boundary, "clientResponses") if isinstance(row, dict)]
    require(labels == ["session", "p3-rejected", "accepted", "rate-limit"], "WSL client response sequence mismatch")
    return boundary


def require_commands(bundle: dict[str, Any]) -> dict[str, Any]:
    commands = object_at(bundle, "commands")
    accepted = list_at(commands, "accepted")
    require(len(accepted) == 1 and isinstance(accepted[0], dict), "expected one accepted WSL command")
    accepted_command = accepted[0]
    require(accepted_command.get("commandId") == EXPECTED_COMMAND_ID, "accepted WSL command id mismatch")
    require(accepted_command.get("remoteSlot") == EXPECTED_REMOTE_SLOT, "accepted WSL command slot mismatch")
    require(accepted_command.get("command") == EXPECTED_REMOTE_COMMAND, "accepted WSL command mismatch")
    require(accepted_command.get("authorizationStatus") == "accepted-hmac-sha256", "accepted WSL authorization mismatch")
    require(accepted_command.get("wslClientAccepted") is True, "accepted WSL command was not accepted")
    require(accepted_command.get("wouldForwardToPrivateLanCommandId") == EXPECTED_PRIVATE_LAN_COMMAND_ID, "accepted WSL command forward target mismatch")
    require(accepted_command.get("gameInputSentByWslClient") is False, "accepted WSL command must not send direct game input")
    require(accepted_command.get("hostHelperInputSent") is False, "accepted WSL command must not send host-helper input")
    rejected = list_at(commands, "rejected")
    reasons = {row.get("reason") for row in rejected if isinstance(row, dict)}
    for reason in {
        "metadata-slot-gameplay-not-allowed",
        "rate-limit-exceeded",
        "second-physical-host-positive-claim-not-allowed",
        "public-matchmaking-not-allowed",
        "direct-input-not-allowed",
    }:
        require(reason in reasons, f"missing WSL rejection reason: {reason}")
    return accepted_command


def require_transcript(bundle: dict[str, Any], authorization: dict[str, Any]) -> dict[str, Any]:
    transcript = object_at(bundle, "transportTranscript")
    require(transcript.get("transport") == EXPECTED_TRANSPORT, "WSL transcript transport mismatch")
    require(transcript.get("protocolVersion") == EXPECTED_PROTOCOL, "WSL transcript protocol mismatch")
    require(transcript.get("serverIdentityFingerprint") == authorization["serverIdentityFingerprint"], "transcript server fingerprint mismatch")
    require(transcript.get("clientIdentityFingerprint") == authorization["clientIdentityFingerprint"], "transcript client fingerprint mismatch")
    require(transcript.get("messageCount") == 7, "WSL transcript message count mismatch")
    event_kinds = [event.get("kind") for event in list_at(transcript, "events") if isinstance(event, dict)]
    for expected in (
        "server_bound",
        "wsl_client_process_started",
        "client_session_hello",
        "server_session_accepted",
        "client_command_p3_forward",
        "server_command_rejected",
        "client_command_p2_forward",
        "server_command_accepted",
        "client_command_rate_limited",
        "client_close",
        "wsl_client_process_exited",
        "server_stopped",
    ):
        require(expected in event_kinds, f"missing WSL transcript event: {expected}")
    return transcript


def require_nonclaims(bundle: dict[str, Any]) -> None:
    nonclaims = object_at(bundle, "nonClaims")
    expected_false = (
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "gameInputSentByWslClient",
        "hostHelperInputSent",
        "rebuildParityProof",
        "noNoticeableDifferenceProof",
    )
    for key in expected_false:
        require(nonclaims.get(key) is False, f"nonclaim must be false: {key}")
    require(nonclaims.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must remain zero")
    require(nonclaims.get("newBeaLaunchCount") == 0, "WSL smoke must not launch BEA")
    require(nonclaims.get("cdbAttachCount") == 0, "WSL smoke must not attach CDB")


def validate_bundle(path: Path) -> dict[str, Any]:
    path = path.resolve()
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    private_lan_path, private_lan_summary, private_lan_bundle = require_private_lan_reference(bundle, path)
    require_session_descriptor(
        bundle,
        private_lan_path=private_lan_path,
        private_lan_summary=private_lan_summary,
        private_lan_bundle=private_lan_bundle,
    )
    transport = require_transport(bundle)
    authorization = require_authorization(bundle)
    process_boundary = require_process_boundary(bundle)
    accepted_command = require_commands(bundle)
    transcript = require_transcript(bundle, authorization)
    require_nonclaims(bundle)
    boundary = str(bundle.get("claimBoundary", ""))
    for token in (
        "WSL2 remote-client command-source smoke only",
        "same physical machine",
        "does not prove a second physical host",
        "multi-host LAN play",
        "public matchmaking",
        "native BEA netcode",
        "P3/P4 original-binary gameplay",
    ):
        require(token in boundary, f"claim boundary missing token: {token}")
    return {
        "artifact": str(path),
        "privateLanTransportProofBundle": str(private_lan_path),
        "claim": "WSL2 same-physical-machine remote-client accepted one signed P2 command envelope that would forward to the already-proven private LAN transport command",
        "transport": transport["transport"],
        "networkScope": transport["networkScope"],
        "windowsBindHost": transport["windowsBindHost"],
        "actualBindPort": transport["actualBindPort"],
        "wslClient": {
            "processModel": process_boundary["processModel"],
            "hostname": process_boundary["wslClientRuntime"]["hostname"],
            "networkAddress": process_boundary["wslClientRuntime"]["networkAddress"],
            "peerAddress": process_boundary["wslClientRuntime"]["peerAddress"],
            "samePhysicalMachineOnly": process_boundary["samePhysicalMachineOnly"],
            "childEnvSensitiveKeyCount": process_boundary["childEnvSensitiveKeyCount"],
        },
        "acceptedCommandId": accepted_command["commandId"],
        "wouldForwardToPrivateLanCommandId": accepted_command["wouldForwardToPrivateLanCommandId"],
        "gameInputSentByWslClient": accepted_command["gameInputSentByWslClient"],
        "hostHelperInputSent": accepted_command["hostHelperInputSent"],
        "messageCount": transcript["messageCount"],
        "nonClaims": bundle["nonClaims"],
    }


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path}: missing token {token!r}")


def validate_repo() -> None:
    failures: list[str] = []
    for path, tokens in {
        READINESS: (
            EXPECTED_SCHEMA,
            EXPECTED_TRANSPORT,
            "same-physical-machine WSL2 client",
            "acceptedCommandId=wsl-remote-client-p2-forward-0001",
            "acceptedOriginalBinaryGameplaySlots=P1,P2",
            "metadataOnlySlots=P3,P4",
            "rejectedGameplayRouteSlots=P3,P4",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
            "newBeaLaunchCount=0",
            "cdbAttachCount=0",
        ),
        FEASIBILITY: (
            "WSL2 remote-client command-source smoke",
            EXPECTED_TRANSPORT,
            "same physical machine",
            "acceptedCommandId=wsl-remote-client-p2-forward-0001",
            "P3/P4 metadata-only",
            "multiHostLanProof=false",
        ),
        REGISTER: (
            "WSL2 remote-client command-source smoke",
            "same-physical-machine WSL2 client",
            "multiHostLanProof=false",
            "publicMatchmakingProof=false",
        ),
        CAPABILITIES: (
            "WSL2 remote-client command-source smoke",
            "same-physical-machine",
            "publicMatchmakingProof=false",
            "nativeBeaNetcodeProof=false",
        ),
    }.items():
        for token in tokens:
            check_token(path, token, failures)
    if read_text(REGISTER) != read_text(REGISTER_MIRROR):
        failures.append("register lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("current capabilities lore mirror mismatch")
    scalability = read_json(SCALABILITY)
    policy = object_at(object_at(scalability, "scalableArchitecture"), "wslRemoteClientSmokePolicy")
    require(policy.get("proofSchema") == EXPECTED_SCHEMA, "scalability contract WSL schema mismatch")
    require(policy.get("transport") == EXPECTED_TRANSPORT, "scalability contract WSL transport mismatch")
    require(policy.get("samePhysicalMachineOnly") is True, "scalability contract must preserve same-physical-machine boundary")
    require(policy.get("secondPhysicalHostProof") is False, "scalability contract must not claim second physical host")
    require(policy.get("multiHostLanProof") is False, "scalability contract must not claim multi-host LAN")
    require(policy.get("publicMatchmakingProof") is False, "scalability contract must not claim public matchmaking")
    require(policy.get("nativeBeaNetcodeProof") is False, "scalability contract must not claim native BEA netcode")
    require(policy.get("nPlayerOriginalBinaryRuntimeProof") == 0, "scalability contract N-player proof must remain zero")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-wsl-remote-client-smoke") != EXPECTED_SCRIPT:
        failures.append("package WSL remote-client script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-wsl-remote-client-smoke" not in aggregate:
        failures.append("aggregate runtime script missing WSL remote-client smoke")
    if failures:
        raise WslRemoteClientSmokeProofError("\n".join(failures))


def make_fixture(root: Path, **mutations: Any) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    private_lan_path = lan.make_bundle_fixture(root / "private-lan")
    private_lan_bundle = read_json(private_lan_path)
    private_lan_summary = lan.validate_bundle(private_lan_path, expected_controller_configuration=1)
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    auth = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "authKeyFingerprint": "a" * 64,
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": "b" * 64,
        "clientIdentityMode": "pinned-fingerprint",
        "clientIdentityFingerprint": "c" * 64,
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
    }
    bundle: dict[str, Any] = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "privateLanTransportProofBundle": private_lan_path.resolve().relative_to(root.resolve()).as_posix(),
        "privateLanTransportProofSha256": lan.sha256_file(private_lan_path),
        "sessionDescriptor": {
            "schemaVersion": EXPECTED_SESSION_SCHEMA,
            "protocolVersion": EXPECTED_PROTOCOL,
            "upstreamPrivateLanProtocolVersion": lan.EXPECTED_PROTOCOL,
            "upstreamPrivateLanProofSha256": lan.sha256_file(private_lan_path),
            "upstreamPrivateLanTransport": private_lan_summary["transport"],
            "sessionCompatibilityKey": upstream_descriptor["sessionCompatibilityKey"],
            "cleanSpecimenSha256": upstream_descriptor["cleanSpecimenSha256"],
            "remotePlayerSlot": EXPECTED_REMOTE_SLOT,
            "allowedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
            "allowedCommand": EXPECTED_REMOTE_COMMAND,
            "mappedInputSequence": EXPECTED_MAPPED_SEQUENCE,
            "upstreamPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
            "upstreamPrivateRelayCommandId": private_lan_summary["wouldForwardToPrivateRelayCommandId"],
            "upstreamPrivateRelayDeliveryEvidence": private_lan_summary["upstreamPrivateRelay"]["gameInputDeliveryEvidence"],
            "levelId": 850,
            "controllerConfiguration": 1,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "transport": {
            "transport": EXPECTED_TRANSPORT,
            "windowsBindHost": "192.0.2.114",
            "actualBindPort": 49155,
            "networkScope": "wsl2-to-windows-host-private-interface-smoke",
            "loopbackInterfaceOnly": False,
            "privateInterfaceBound": True,
            "privateInterfaceSocketOpened": True,
            "wsl2ClientProcess": True,
            "crossEnvironmentClient": True,
            "samePhysicalMachineOnly": True,
            "secondPhysicalHostClaim": False,
            "multiHostLanClaim": False,
            "publicNetworkSocketsOpened": False,
            "publicMatchmakingClaim": False,
            "matchmakingServerContacted": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "natTraversalClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "dualClientParityClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "gameInputSentByWslClient": False,
            "hostHelperInputSent": False,
        },
        "authorization": auth,
        "clientProcessBoundary": {
            "processModel": "wsl2-python-process",
            "windowsBuilderProcessId": 100,
            "wslLauncherWindowsProcessId": 101,
            "wslClientProcessId": 102,
            "clientExitCode": 0,
            "clientVerifiedServerIdentity": True,
            "wslClientRuntime": {
                "clientKind": "wsl2-linux-python-client",
                "hostname": "DEV-LAPTOP",
                "platform": "Linux",
                "pythonVersion": "3.12.3",
                "networkAddress": "192.0.2.115",
                "peerAddress": "192.0.2.114",
                "windowsObservedClientSourceAddress": "192.0.2.115",
            },
            "clientCommandLineContainsCredential": False,
            "clientEnvironmentContainsCredential": False,
            "clientStdoutContainsCredential": False,
            "clientStderrContainsCredential": False,
            "credentialTransportToClientProcess": "stdin-ephemeral-not-serialized-to-artifact",
            "childEnvSensitiveKeyCount": 0,
            "samePhysicalMachineOnly": True,
            "secondPhysicalHostClaim": False,
            "multiHostLanClaim": False,
            "clientResponses": [
                {"label": "session", "type": "session_accepted"},
                {"label": "p3-rejected", "type": "command_rejected", "reason": "metadata-slot-gameplay-not-allowed"},
                {"label": "accepted", "type": "command_accepted", "commandId": EXPECTED_COMMAND_ID, "wouldForwardToPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID},
                {"label": "rate-limit", "type": "command_rejected", "reason": "rate-limit-exceeded"},
            ],
        },
        "commands": {
            "accepted": [
                {
                    "commandId": EXPECTED_COMMAND_ID,
                    "remoteSlot": EXPECTED_REMOTE_SLOT,
                    "command": EXPECTED_REMOTE_COMMAND,
                    "authorizationStatus": "accepted-hmac-sha256",
                    "wslClientAccepted": True,
                    "wouldForwardToPrivateLanCommandId": EXPECTED_PRIVATE_LAN_COMMAND_ID,
                    "gameInputSentByWslClient": False,
                    "hostHelperInputSent": False,
                }
            ],
            "rejected": [
                {"commandId": EXPECTED_REJECTED_P3_COMMAND_ID, "reason": "metadata-slot-gameplay-not-allowed", "wslClientAccepted": False},
                {"commandId": EXPECTED_RATE_LIMIT_COMMAND_ID, "reason": "rate-limit-exceeded", "wslClientAccepted": False},
                {"commandId": "wsl-remote-client-reject-second-physical-host-claim-0001", "reason": "second-physical-host-positive-claim-not-allowed", "wslClientAccepted": False},
                {"commandId": "wsl-remote-client-reject-public-matchmaking-claim-0001", "reason": "public-matchmaking-not-allowed", "wslClientAccepted": False},
                {"commandId": "wsl-remote-client-reject-direct-input-claim-0001", "reason": "direct-input-not-allowed", "wslClientAccepted": False},
            ],
        },
        "transportTranscript": {
            "transport": EXPECTED_TRANSPORT,
            "protocolVersion": EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": auth["serverIdentityFingerprint"],
            "clientIdentityFingerprint": auth["clientIdentityFingerprint"],
            "messageCount": 7,
            "events": [
                {"kind": "server_bound"},
                {"kind": "wsl_client_process_started"},
                {"kind": "client_session_hello"},
                {"kind": "server_session_accepted"},
                {"kind": "client_command_p3_forward"},
                {"kind": "server_command_rejected"},
                {"kind": "client_command_p2_forward"},
                {"kind": "server_command_accepted"},
                {"kind": "client_command_rate_limited"},
                {"kind": "client_close"},
                {"kind": "wsl_client_process_exited"},
                {"kind": "server_stopped"},
            ],
        },
        "nonClaims": {
            "secondPhysicalHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
            "gameInputSentByWslClient": False,
            "hostHelperInputSent": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "claimBoundary": "WSL2 remote-client command-source smoke only; same physical machine; does not prove a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, or P3/P4 original-binary gameplay.",
    }
    for key, value in mutations.items():
        if key == "second_host_claim":
            bundle["transport"]["secondPhysicalHostClaim"] = value
        elif key == "multi_host_claim":
            bundle["transport"]["multiHostLanClaim"] = value
        elif key == "p3_gameplay_claim":
            bundle["sessionDescriptor"]["activeP3P4OriginalBinaryGameplayProof"] = value
        elif key == "direct_input_claim":
            bundle["commands"]["accepted"][0]["gameInputSentByWslClient"] = value
        elif key == "sensitive_env_count":
            bundle["clientProcessBoundary"]["childEnvSensitiveKeyCount"] = value
        elif key == "serialized_credential":
            bundle["authorization"]["rawCredential"] = "secret_value"
    output = root / "wsl-remote-client-smoke-proof.json"
    write_json(output, bundle)
    return output


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fixture = make_fixture(Path(tmp))
        validate_bundle(fixture)
    for name, kwargs in (
        ("second physical host claim should fail", {"second_host_claim": True}),
        ("multi-host claim should fail", {"multi_host_claim": True}),
        ("P3 gameplay claim should fail", {"p3_gameplay_claim": True}),
        ("direct input claim should fail", {"direct_input_claim": True}),
        ("sensitive env should fail", {"sensitive_env_count": 1}),
        ("serialized credential should fail", {"serialized_credential": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = make_fixture(Path(tmp), **kwargs)
            try:
                validate_bundle(fixture)
            except WslRemoteClientSmokeProofError:
                continue
            raise WslRemoteClientSmokeProofError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary WSL remote-client smoke checker self-test: PASS")
        return 0
    if args.check:
        validate_repo()
        if builder.DEFAULT_OUTPUT.is_file():
            print(json.dumps(validate_bundle(builder.DEFAULT_OUTPUT), indent=2, sort_keys=True))
        else:
            print("WinUI original-binary WSL remote-client smoke repo check: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WslRemoteClientSmokeProofError as exc:
        print(f"WinUI original-binary WSL remote-client smoke check: FAIL: {exc}")
        raise SystemExit(2)
