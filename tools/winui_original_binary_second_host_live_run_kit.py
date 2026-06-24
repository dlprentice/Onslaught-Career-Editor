#!/usr/bin/env python3
"""Build a checked, redacted run kit for a second-host command-source attempt.

This tool packages the host readiness result, a client identity/source-safety
preflight, and the exact proof gates needed for a later live run. It does not
open a listener, create an invitation, launch BEA, attach CDB, send input, or
create a command-source proof bundle.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any

import winui_original_binary_second_host_command_source_client as client_preflight
import winui_original_binary_second_host_live_readiness as readiness
import build_winui_original_binary_second_host_command_source_bundle as command_source_builder
import winui_safe_copy_online_private_lan_transport_smoke_check as private_lan_check
import winui_safe_copy_online_second_host_command_source_check as command_source_check


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "winui-original-binary-second-host-live-run-kit.v1"
SCOPE = "second-host-live-run-kit-not-command-source-proof"
CLIENT_PREFLIGHT_SCHEMA = "winui-original-binary-second-host-client-preflight.v1"
CLIENT_PREFLIGHT_SCOPE = "second-host-client-identity-source-safety-preflight-not-command-source-proof"
PROOF_FALSE_KEYS = readiness.PROOF_FALSE_KEYS


class SecondHostLiveRunKitError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostLiveRunKitError(message)


def fixture_ipv4(*octets: int) -> str:
    return ".".join(str(octet) for octet in octets)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def validate_client_preflight(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == CLIENT_PREFLIGHT_SCHEMA, "client preflight schema mismatch")
    require(payload.get("scope") == CLIENT_PREFLIGHT_SCOPE, "client preflight scope mismatch")
    fingerprint = str(payload.get("clientIdentityFingerprint") or "")
    require(command_source_check.is_hex64(fingerprint), "client identity fingerprint must be hex64")
    for key in (
        "privateProofCreated",
        "gameInputSent",
        "baseOnlineMultiplayerReady",
        "acceptedLiveSecondHostCommandSourceProof",
        "acceptedLiveSecondHostRuntimeDeliveryProof",
    ):
        require(payload.get(key) is False, f"client preflight proof boolean must remain false: {key}")

    source_safety = payload.get("clientSourceSafety")
    require(isinstance(source_safety, dict), "client preflight must include source safety")
    machine_identity = payload.get("machineIdentity")
    require(isinstance(machine_identity, dict), "client preflight must include machine identity")
    require(machine_identity.get("machineFingerprint") == fingerprint, "client identity fingerprint must match machine identity")
    require(machine_identity.get("machineFingerprintComputedByPreflight") is True, "client machine fingerprint must be computed by preflight")
    require(
        machine_identity.get("machineFingerprintSource") == "local-hostname-platform-preflight",
        "client machine fingerprint source must be local-hostname-platform-preflight",
    )
    require(machine_identity.get("machineFingerprintInputsRedacted") is True, "client machine fingerprint inputs must be redacted")
    runtime_kind = str(machine_identity.get("runtimeHostKind") or "")
    require(runtime_kind in command_source_check.ALLOWED_RUNTIME_HOST_KINDS, "client runtime host kind must be accepted")
    require(runtime_kind not in command_source_check.FORBIDDEN_RUNTIME_HOST_KINDS, "client runtime host kind must not be WSL/container/unknown")
    runtime_kind_source = str(machine_identity.get("runtimeHostKindSource") or "")
    require(runtime_kind_source, "client runtime host kind source is required")
    require(machine_identity.get("runtimeHostKindInputsRedacted") is True, "client runtime host kind inputs must be redacted")
    require(machine_identity.get("wslDetectedByPreflight") is False, "client WSL runtime cannot be ready")
    require(machine_identity.get("containerDetectedByPreflight") is False, "client container runtime cannot be ready")
    require(source_safety.get("sourceEvidenceMode") == "local-preflight-computed", "client source safety must be local-preflight-computed")
    require(source_safety.get("computedByPreflight") is True, "client source safety must be computed by preflight")
    require(source_safety.get("pathValuesPublished") is False, "client source safety must not publish raw paths")
    require(source_safety.get("absolutePathsSerialized") is False, "client source safety must not serialize absolute paths")
    require(int(source_safety.get("copiedProfileFileCount") or 0) > 0, "client copied profile file count must be positive")
    require(int(source_safety.get("installedGameFileCount") or 0) > 0, "client installed game file count must be positive")
    return {
        "clientIdentityFingerprint": fingerprint,
        "machineFingerprintComputedByPreflight": bool(machine_identity.get("machineFingerprintComputedByPreflight")),
        "runtimeHostKind": runtime_kind,
        "runtimeHostKindSource": runtime_kind_source,
        "runtimeHostKindOperatorSupplied": runtime_kind_source == "operator-supplied-runtime-host-kind",
        "sourceEvidenceMode": source_safety["sourceEvidenceMode"],
        "copiedProfileHashMode": source_safety.get("copiedProfileHashMode"),
        "installedGameHashMode": source_safety.get("installedGameHashMode"),
        "copiedProfileFileCount": source_safety.get("copiedProfileFileCount"),
        "installedGameFileCount": source_safety.get("installedGameFileCount"),
    }


def validate_client_runtime_kind_for_command_source(
    client_summary: dict[str, Any] | None,
    command_source_kind: str | None,
) -> dict[str, Any]:
    if client_summary is None or command_source_kind is None:
        return {
            "runtimeKindCompatibleWithCommandSourceKind": False,
            "runtimeKindCompatibilityReason": "client-preflight-or-command-source-kind-missing",
        }
    runtime_kind = str(client_summary.get("runtimeHostKind") or "")
    runtime_kind_source = str(client_summary.get("runtimeHostKindSource") or "")
    live_validation_compatible = runtime_kind_source == "auto-platform-preflight"
    if command_source_kind == "distinct-vm-private-lan-labeled-vm-only":
        require(runtime_kind == "vm-guest", "VM-labeled run kit requires client runtimeHostKind=vm-guest")
        return {
            "runtimeKindCompatibleWithCommandSourceKind": True,
            "runtimeKindLiveValidationCompatible": live_validation_compatible,
            "runtimeKindCompatibilityReason": "vm-labeled-client-runtime-kind",
            "vmLabeledProofOnly": True,
            "physicalSecondHostProof": False,
        }
    if command_source_kind == "distinct-physical-host-private-lan":
        require(runtime_kind != "vm-guest", "physical second-host run kit must not use vm-guest client runtime kind")
        require(
            runtime_kind_source == "auto-platform-preflight",
            "physical second-host run kit requires auto-platform-preflight client runtime kind evidence",
        )
        return {
            "runtimeKindCompatibleWithCommandSourceKind": True,
            "runtimeKindLiveValidationCompatible": True,
            "runtimeKindCompatibilityReason": "physical-client-runtime-kind-auto-preflight",
            "vmLabeledProofOnly": False,
            "physicalSecondHostProof": True,
        }
    raise SecondHostLiveRunKitError("unsupported command source kind for client runtime kind validation")


def is_documentation_or_reserved_address(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(address in network for network in command_source_check.DOCUMENTATION_OR_RESERVED_TEST_NETWORKS)


def classify_private_lan_live_candidate(path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    bundle = read_json(path)
    transport = bundle.get("transport")
    authorization = bundle.get("authorization")
    require(isinstance(transport, dict), "private LAN proof must include transport object")
    require(isinstance(authorization, dict), "private LAN proof must include authorization object")
    bind_host = str(summary.get("bindHost") or transport.get("bindHost") or "")
    reasons: list[str] = []
    if not command_source_check.ip_is_private_lan_non_loopback(bind_host):
        if is_documentation_or_reserved_address(bind_host):
            reasons.append("documentation-or-reserved-bind-host")
        else:
            reasons.append("bind-host-not-live-private-lan-non-loopback")
    for key in ("authKeyFingerprint", "serverIdentityFingerprint"):
        if authorization.get(key) in command_source_check.FIXTURE_HEX64_SENTINELS:
            reasons.append(f"fixture-sentinel-{key}")
    return {
        "liveValidationCandidate": not reasons,
        "liveValidationCompatibilityReason": "live-candidate" if not reasons else ";".join(reasons),
        "bindHostDocumentationOrReserved": is_documentation_or_reserved_address(bind_host),
    }


def validate_invitation_path(path: Path | None) -> bool:
    if path is None:
        return False
    try:
        command_source_builder.require_private_invitation_path(path)
    except command_source_builder.SecondHostCommandSourceBundleBuildError as exc:
        raise SecondHostLiveRunKitError(str(exc)) from exc
    return True


def validate_private_lan_proof(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"provided": False, "validated": False, "liveValidationCandidate": False}
    try:
        summary = private_lan_check.validate_bundle(path, expected_controller_configuration=1)
    except Exception as exc:
        raise SecondHostLiveRunKitError("private LAN proof must be an existing valid private LAN transport smoke bundle") from exc
    live_candidate = classify_private_lan_live_candidate(path, summary)
    return {
        "provided": True,
        "validated": True,
        **live_candidate,
        "transport": summary.get("transport"),
        "protocolVersion": summary.get("protocolVersion"),
        "acceptedCommandId": summary.get("acceptedCommandId"),
        "gameInputSentByTransport": summary.get("gameInputSentByTransport"),
        "hostHelperInputSent": summary.get("hostHelperInputSent"),
    }


def validate_host_source_safety(copied_profile_root: Path | None, installed_game_root: Path | None) -> dict[str, Any]:
    if copied_profile_root is None and installed_game_root is None:
        return {"provided": False, "computedByPreflight": False}
    if copied_profile_root is None or installed_game_root is None:
        raise SecondHostLiveRunKitError("host source-safety readiness requires both copied-profile and installed-game roots")
    try:
        evidence = command_source_builder.make_source_safety_side_evidence(
            role="host",
            copied_profile_root=copied_profile_root,
            installed_game_root=installed_game_root,
        )
    except command_source_builder.SecondHostCommandSourceBundleBuildError as exc:
        raise SecondHostLiveRunKitError("host source-safety roots must exist and hash through local preflight") from exc
    return {
        "provided": True,
        "computedByPreflight": bool(evidence.get("computedByPreflight")),
        "sourceEvidenceMode": evidence.get("sourceEvidenceMode"),
        "copiedProfileHashMode": evidence.get("copiedProfileHashMode"),
        "installedGameHashMode": evidence.get("installedGameHashMode"),
        "copiedProfileFileCount": evidence.get("copiedProfileFileCount"),
        "installedGameFileCount": evidence.get("installedGameFileCount"),
        "pathValuesPublished": evidence.get("pathValuesPublished"),
        "absolutePathsSerialized": evidence.get("absolutePathsSerialized"),
    }


def redacted_command_templates(client_identity_fingerprint: str | None) -> dict[str, list[str]]:
    client_fingerprint = client_identity_fingerprint or "<client-identity-fingerprint-from-client-preflight>"
    return {
        "clientIdentityPreflight": [
            "py -3 tools\\winui_original_binary_second_host_command_source_client.py",
            "--identity-preflight",
            "--client-copied-profile-root <client-copied-profile-root>",
            "--client-installed-game-root <client-installed-game-root>",
            "[omit manual runtime-kind overrides for live proof; manual overrides are attempt-only diagnostics]",
        ],
        "hostServer": [
            "py -3 tools\\build_winui_original_binary_second_host_command_source_bundle.py server <private-lan-proof>",
            "--output <private-proof-root>\\second-host-command-source-proof.json",
            "--bind-host <host-private-ip>",
            "--command-source-kind <distinct-physical-host-private-lan|distinct-vm-private-lan-labeled-vm-only>",
            "--client-invitation <os-temp-outside-repo-invitation.json>",
            f"--client-identity-fingerprint {client_fingerprint}",
            "--host-copied-profile-root <host-copied-profile-root>",
            "--host-installed-game-root <host-installed-game-root>",
        ],
        "clientRun": [
            "Copy the host-created invitation JSON to the client/VM private temp location.",
            "py -3 tools\\winui_original_binary_second_host_command_source_client.py <transferred-invitation.json>",
            "--client-copied-profile-root <client-copied-profile-root>",
            "--client-installed-game-root <client-installed-game-root>",
            "[omit manual runtime-kind overrides for live proof; manual overrides are attempt-only diagnostics]",
        ],
        "liveValidation": [
            "py -3 tools\\winui_safe_copy_online_second_host_command_source_check.py <private-proof-root>\\second-host-command-source-proof.json --live"
        ],
    }


def build_summary(
    *,
    interface_rows: list[dict[str, Any]],
    bind_host: str | None = None,
    command_source_kind: str | None = None,
    host_topology: str = "current-host-only",
    private_lan_proof: Path | None = None,
    client_preflight_payload: dict[str, Any] | None = None,
    host_copied_profile_root: Path | None = None,
    host_installed_game_root: Path | None = None,
    invitation_path: Path | None = None,
) -> dict[str, Any]:
    client_summary = validate_client_preflight(client_preflight_payload) if client_preflight_payload else None
    client_runtime_kind_summary = validate_client_runtime_kind_for_command_source(client_summary, command_source_kind)
    readiness_payload = readiness.build_summary(
        interface_rows=interface_rows,
        bind_host=bind_host,
        command_source_kind=command_source_kind,
        host_topology=host_topology,
        private_lan_proof=private_lan_proof,
        client_identity_fingerprint=None if client_summary is None else str(client_summary["clientIdentityFingerprint"]),
    )
    readiness_summary = readiness.validate_summary(readiness_payload)
    private_lan_summary = validate_private_lan_proof(private_lan_proof)
    host_source_safety = validate_host_source_safety(host_copied_profile_root, host_installed_game_root)
    invitation_path_validated = validate_invitation_path(invitation_path)
    host_inputs_complete = bool(host_source_safety["computedByPreflight"] and invitation_path)
    ready_to_attempt = bool(
        readiness_summary["serverCommandInputsComplete"]
        and client_summary is not None
        and client_runtime_kind_summary["runtimeKindCompatibleWithCommandSourceKind"]
        and host_inputs_complete
        and private_lan_summary["validated"]
        and invitation_path_validated
    )
    ready_to_run = bool(
        ready_to_attempt
        and client_runtime_kind_summary["runtimeKindLiveValidationCompatible"]
        and private_lan_summary["liveValidationCandidate"]
    )
    return {
        "schemaVersion": SCHEMA,
        "scope": SCOPE,
        "status": (
            "ready-to-run-live-command-source"
            if ready_to_run
            else "ready-to-attempt-harness-only-not-live-ready"
            if ready_to_attempt
            else "live-run-kit-inputs-incomplete"
        ),
        "readyToAttemptHarness": ready_to_attempt,
        "readyForLiveValidationCandidate": ready_to_run,
        "readyToRunLiveCommandSource": ready_to_run,
        "proofBooleans": {key: False for key in PROOF_FALSE_KEYS},
        "hostReadiness": {
            "candidatePrivateBindAddressCount": readiness_summary["candidatePrivateBindAddressCount"],
            "wslOnHostInterfaceCount": readiness_summary["wslOnHostInterfaceCount"],
            "serverCommandInputsComplete": readiness_summary["serverCommandInputsComplete"],
            "commandSourceKind": command_source_kind,
            "hostTopology": host_topology,
        },
        "clientPreflight": {
            "provided": client_summary is not None,
            **(client_summary or {}),
            **client_runtime_kind_summary,
        },
        "hostSourceSafety": host_source_safety,
        "privateLanProof": private_lan_summary,
        "privateRunInputs": {
            "privateLanProofProvided": private_lan_proof is not None,
            "privateLanProofValidated": bool(private_lan_summary["validated"]),
            "bindHostProvided": bool(bind_host),
            "hostCopiedProfileRootProvided": host_copied_profile_root is not None,
            "hostInstalledGameRootProvided": host_installed_game_root is not None,
            "hostSourceSafetyComputedByPreflight": bool(host_source_safety["computedByPreflight"]),
            "invitationPathProvided": invitation_path is not None,
            "invitationPathValidatedUnderOsTempOutsideRepo": invitation_path_validated,
            "invitationPathMustStayOsTempOutsideRepo": True,
            "rawPrivatePathsSerializedInPublicDocs": False,
        },
        "commandTemplates": redacted_command_templates(None if client_summary is None else str(client_summary["clientIdentityFingerprint"])),
        "nonClaims": {
            "doesNotOpenListener": True,
            "doesNotCreateInvitation": True,
            "doesNotLaunchBea": True,
            "doesNotAttachCdb": True,
            "doesNotSendGameInput": True,
            "doesNotCreateCommandSourceProof": True,
            "doesNotEnableHostJoin": True,
            "doesNotProvePlayerReadyNetplay": True,
        },
    }


def validate_summary(payload: dict[str, Any], *, require_ready: bool = False) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("scope") == SCOPE, "scope mismatch")
    proof = payload.get("proofBooleans")
    require(isinstance(proof, dict), "missing proof booleans")
    for key in PROOF_FALSE_KEYS:
        require(proof.get(key) is False, f"proof boolean must remain false: {key}")
    nonclaims = payload.get("nonClaims")
    require(isinstance(nonclaims, dict), "missing nonClaims")
    for key, value in nonclaims.items():
        require(value is True, f"non-claim token must remain true: {key}")
    host = payload.get("hostReadiness")
    require(isinstance(host, dict), "missing hostReadiness")
    private_inputs = payload.get("privateRunInputs")
    require(isinstance(private_inputs, dict), "missing privateRunInputs")
    if private_inputs.get("privateLanProofProvided") is True:
        require(private_inputs.get("privateLanProofValidated") is True, "provided private LAN proof must validate")
    host_source = payload.get("hostSourceSafety")
    require(isinstance(host_source, dict), "missing hostSourceSafety")
    if private_inputs.get("hostCopiedProfileRootProvided") is True or private_inputs.get("hostInstalledGameRootProvided") is True:
        require(host_source.get("computedByPreflight") is True, "provided host roots must hash through local preflight")
        require(host_source.get("pathValuesPublished") is False, "host source-safety must not publish raw paths")
        require(host_source.get("absolutePathsSerialized") is False, "host source-safety must not serialize absolute paths")
    if private_inputs.get("invitationPathProvided") is True:
        require(
            private_inputs.get("invitationPathValidatedUnderOsTempOutsideRepo") is True,
            "provided invitation path must be validated under OS temp outside repo",
        )
    client = payload.get("clientPreflight")
    require(isinstance(client, dict), "missing clientPreflight")
    ready = bool(payload.get("readyToRunLiveCommandSource"))
    if ready or require_ready:
        require(host.get("serverCommandInputsComplete") is True, "ready kit requires complete server command inputs")
        require(client.get("provided") is True, "ready kit requires client preflight")
        require(client.get("sourceEvidenceMode") == "local-preflight-computed", "ready kit requires computed client source safety")
        require(client.get("runtimeKindCompatibleWithCommandSourceKind") is True, "ready kit requires command-source-compatible client runtime kind")
        require(client.get("runtimeKindLiveValidationCompatible") is True, "ready kit requires live-validation-compatible client runtime kind")
        require(private_inputs.get("privateLanProofValidated") is True, "ready kit requires validated private LAN proof")
        private_lan = payload.get("privateLanProof")
        require(isinstance(private_lan, dict), "ready kit requires private LAN proof summary")
        require(private_lan.get("liveValidationCandidate") is True, "ready kit requires live-validation-compatible private LAN proof")
        require(host_source.get("computedByPreflight") is True, "ready kit requires computed host source safety")
        for key in ("privateLanProofProvided", "bindHostProvided", "hostCopiedProfileRootProvided", "hostInstalledGameRootProvided", "invitationPathProvided"):
            require(private_inputs.get(key) is True, f"ready kit missing private input: {key}")
        require(
            private_inputs.get("invitationPathValidatedUnderOsTempOutsideRepo") is True,
            "ready kit requires OS-temp outside-repo invitation path",
        )
    templates = payload.get("commandTemplates")
    require(isinstance(templates, dict), "missing command templates")
    require("hostServer" in templates and "clientRun" in templates and "liveValidation" in templates, "missing required command templates")
    return {
        "schemaVersion": payload["schemaVersion"],
        "scope": payload["scope"],
        "readyToAttemptHarness": bool(payload.get("readyToAttemptHarness")),
        "readyForLiveValidationCandidate": bool(payload.get("readyForLiveValidationCandidate")),
        "readyToRunLiveCommandSource": ready,
        "serverCommandInputsComplete": host.get("serverCommandInputsComplete"),
        "clientPreflightProvided": client.get("provided"),
        "candidatePrivateBindAddressCount": host.get("candidatePrivateBindAddressCount"),
        "wslOnHostInterfaceCount": host.get("wslOnHostInterfaceCount"),
        "baseOnlineMultiplayerReady": proof["baseOnlineMultiplayerReady"],
        "hostJoinControlsMayBeEnabled": proof["hostJoinControlsMayBeEnabled"],
        "acceptedLiveSecondHostCommandSourceProof": proof["acceptedLiveSecondHostCommandSourceProof"],
    }


def run_self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copied = root / "client-copied-profile"
        installed = root / "client-installed-game"
        (copied / "data").mkdir(parents=True)
        installed.mkdir()
        (copied / "BEA.exe").write_bytes(b"client copied exe")
        (copied / "data" / "base_res_PC.aya").write_bytes(b"client copied resource")
        (installed / "BEA.exe").write_bytes(b"client installed exe")
        host_copied = root / "host-copied-profile"
        host_installed = root / "host-installed-game"
        (host_copied / "data").mkdir(parents=True)
        host_installed.mkdir()
        (host_copied / "BEA.exe").write_bytes(b"host copied exe")
        (host_copied / "data" / "base_res_PC.aya").write_bytes(b"host copied resource")
        (host_installed / "BEA.exe").write_bytes(b"host installed exe")
        fixture_private_lan_proof = private_lan_check.make_bundle_fixture(root / "private-lan-fixture")
        vm_client_summary = client_preflight.build_identity_preflight_summary(
            client_copied_profile_root=copied,
            client_installed_game_root=installed,
            client_runtime_host_kind="vm-guest",
        )
        attempt_only = build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": fixture_ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
            bind_host=fixture_ipv4(172, 20, 10, 7),
            command_source_kind="distinct-vm-private-lan-labeled-vm-only",
            host_topology="vm-labeled-same-physical",
            private_lan_proof=fixture_private_lan_proof,
            client_preflight_payload=vm_client_summary,
            host_copied_profile_root=host_copied,
            host_installed_game_root=host_installed,
            invitation_path=root / "bea-second-host" / "invitation.json",
        )
        attempt_checked = validate_summary(attempt_only)
        require(attempt_checked["readyToAttemptHarness"] is True, "fixture should be attempt-ready")
        require(attempt_checked["readyToRunLiveCommandSource"] is False, "fixture must not be live-ready")

        live_private_lan_proof = private_lan_check.make_bundle_fixture(root / "private-lan-live-candidate")
        live_private_lan = read_json(live_private_lan_proof)
        live_private_lan["transport"]["bindHost"] = fixture_ipv4(10, 77, 20, 114)
        live_private_lan["authorization"]["authKeyFingerprint"] = "0123456789abcdef" * 4
        live_private_lan["authorization"]["serverIdentityFingerprint"] = "fedcba9876543210" * 4
        live_private_lan["transportTranscript"]["serverIdentityFingerprint"] = live_private_lan["authorization"]["serverIdentityFingerprint"]
        live_private_lan["transportTranscript"]["events"][0]["bindHost"] = fixture_ipv4(10, 77, 20, 114)
        live_private_lan_proof.write_text(json.dumps(live_private_lan), encoding="utf-8")

        physical_client_summary = client_preflight.build_identity_preflight_summary(
            client_copied_profile_root=copied,
            client_installed_game_root=installed,
        )
        summary = build_summary(
            interface_rows=[{"InterfaceAlias": "Wi-Fi", "IPAddress": fixture_ipv4(172, 20, 10, 7), "AddressState": "Preferred"}],
            bind_host=fixture_ipv4(172, 20, 10, 7),
            command_source_kind="distinct-physical-host-private-lan",
            host_topology="distinct-physical-private-host",
            private_lan_proof=live_private_lan_proof,
            client_preflight_payload=physical_client_summary,
            host_copied_profile_root=host_copied,
            host_installed_game_root=host_installed,
            invitation_path=root / "bea-second-host" / "invitation.json",
        )
        checked = validate_summary(summary, require_ready=True)
        require(checked["readyToRunLiveCommandSource"] is True, "live-candidate fixture should be ready")

        overclaim = json.loads(json.dumps(summary))
        overclaim["proofBooleans"]["baseOnlineMultiplayerReady"] = True
        try:
            validate_summary(overclaim)
        except SecondHostLiveRunKitError:
            pass
        else:
            raise AssertionError("online overclaim should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--client-preflight", type=Path)
    parser.add_argument("--bind-host")
    parser.add_argument("--command-source-kind", choices=readiness.COMMAND_SOURCE_KINDS)
    parser.add_argument("--host-topology", choices=readiness.HOST_TOPOLOGIES, default="current-host-only")
    parser.add_argument("--private-lan-proof", type=Path)
    parser.add_argument("--host-copied-profile-root", type=Path)
    parser.add_argument("--host-installed-game-root", type=Path)
    parser.add_argument("--invitation-path", type=Path)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host live run kit self-test: PASS")
        return 0

    client_payload = read_json(args.client_preflight) if args.client_preflight else None
    summary = build_summary(
        interface_rows=readiness.collect_windows_ipv4_interfaces(),
        bind_host=args.bind_host,
        command_source_kind=args.command_source_kind,
        host_topology=args.host_topology,
        private_lan_proof=args.private_lan_proof,
        client_preflight_payload=client_payload,
        host_copied_profile_root=args.host_copied_profile_root,
        host_installed_game_root=args.host_installed_game_root,
        invitation_path=args.invitation_path,
    )
    checked = validate_summary(summary, require_ready=args.require_ready)
    if args.check:
        print("WinUI original-binary second-host live run kit check: PASS")
    print(json.dumps(checked if args.check else summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SecondHostLiveRunKitError, json.JSONDecodeError) as exc:
        print(f"WinUI original-binary second-host live run kit check: FAIL: {exc}")
        raise SystemExit(2)
