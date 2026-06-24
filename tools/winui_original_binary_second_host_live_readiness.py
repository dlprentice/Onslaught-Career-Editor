#!/usr/bin/env python3
"""Host-side readiness preflight for the original-binary second-host live run.

This is a planning/preflight helper only. It does not open a listener, create an
invitation, launch BEA, attach CDB, send input, or create a proof bundle.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "winui-original-binary-second-host-live-readiness.v1"
SCOPE = "host-live-run-readiness-preflight-not-command-source-proof"
COMMAND_SOURCE_KINDS = (
    "distinct-physical-host-private-lan",
    "distinct-vm-private-lan-labeled-vm-only",
)
HOST_TOPOLOGIES = (
    "current-host-only",
    "vm-labeled-same-physical",
    "distinct-physical-private-host",
)
PROOF_FALSE_KEYS = (
    "acceptedLiveSecondHostCommandSourceProof",
    "acceptedLiveSecondHostRuntimeDeliveryProof",
    "acceptedLiveSecondHostRuntimeCausalityProof",
    "baseOnlineMultiplayerReady",
    "hostJoinControlsMayBeEnabled",
    "multiHostLanPlayProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "activeP3P4OriginalBinaryGameplayProof",
)
PRIVATE_IPV4_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in (
        (0x0A000000, 8),
        (0xAC100000, 12),
        (0xC0A80000, 16),
    )
)
DOCUMENTATION_OR_RESERVED_TEST_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in (
        (0xC0000200, 24),
        (0xC6336400, 24),
        (0xCB007100, 24),
    )
)
REQUIRED_LIVE_REQUIREMENTS = (
    "requiresExplicitLiveValidationMode",
    "requiresLiveServerClientTranscript",
    "requiresListenerLifecycleReceipt",
    "requiresListenerTeardownEvidence",
    "requiresListenerPostCloseConnectRejection",
    "requiresTwoPhasePrePostSourceSafety",
    "requiresSignedClientSourceSafetyPostflight",
    "requiresNoRawPathsInPublicDocs",
    "requiresNoPublicEndpoint",
    "requiresHostJoinRemainDisabled",
)


class SecondHostLiveReadinessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostLiveReadinessError(message)


def fixture_ipv4(*octets: int) -> str:
    return ".".join(str(octet) for octet in octets)


def is_private_lan_ipv4(raw: str) -> bool:
    try:
        address = ipaddress.ip_address(raw)
    except ValueError:
        return False
    if address.version != 4:
        return False
    if address.is_loopback or address.is_link_local or address.is_multicast or address.is_unspecified:
        return False
    if any(address in network for network in DOCUMENTATION_OR_RESERVED_TEST_NETWORKS):
        return False
    return any(address in network for network in PRIVATE_IPV4_NETWORKS)


def normalized_interface_row(row: dict[str, Any]) -> dict[str, Any]:
    alias = str(row.get("InterfaceAlias") or row.get("interfaceAlias") or row.get("alias") or "")
    ip_address = str(row.get("IPAddress") or row.get("ipAddress") or row.get("address") or "")
    state = str(row.get("AddressState") or row.get("addressState") or row.get("state") or "")
    prefix = row.get("PrefixLength", row.get("prefixLength"))
    return {
        "interfaceAlias": alias,
        "ipAddress": ip_address,
        "prefixLength": prefix,
        "addressState": state,
    }


def classify_interface(row: dict[str, Any]) -> dict[str, Any]:
    normalized = normalized_interface_row(row)
    alias_lower = normalized["interfaceAlias"].lower()
    ip_address = normalized["ipAddress"]
    is_private = is_private_lan_ipv4(ip_address)
    is_wsl = "wsl" in alias_lower
    is_preferred = normalized["addressState"].lower() in {"preferred", "4", ""}
    eligible = is_private and is_preferred and not is_wsl
    reasons: list[str] = []
    if not is_private:
        reasons.append("not-private-rfc1918-non-loopback")
    if not is_preferred:
        reasons.append("not-preferred-address-state")
    if is_wsl:
        reasons.append("wsl-on-host-not-second-host-proof")
    if eligible:
        reasons.append("candidate-host-bind-address")
    return {
        **normalized,
        "privateRfc1918NonLoopback": is_private,
        "wslOnHostInterface": is_wsl,
        "eligibleForLiveSecondHostServerBind": eligible,
        "classification": reasons,
    }


def collect_windows_ipv4_interfaces() -> list[dict[str, Any]]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-NetIPAddress -AddressFamily IPv4 | "
            "Select-Object InterfaceAlias,IPAddress,PrefixLength,AddressState | "
            "ConvertTo-Json -Depth 3"
        ),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0 and result.stdout.strip():
        value = json.loads(result.stdout)
        if isinstance(value, dict):
            return [value]
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]

    rows: list[dict[str, Any]] = []
    for info in socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET):
        address = info[4][0]
        rows.append({"InterfaceAlias": "socket-hostname-fallback", "IPAddress": address, "AddressState": "Preferred"})
    return rows


def build_summary(
    *,
    interface_rows: list[dict[str, Any]],
    bind_host: str | None = None,
    command_source_kind: str | None = None,
    host_topology: str = "current-host-only",
    private_lan_proof: Path | None = None,
    client_identity_fingerprint: str | None = None,
) -> dict[str, Any]:
    classified = [classify_interface(row) for row in interface_rows]
    candidates = [row for row in classified if row["eligibleForLiveSecondHostServerBind"]]
    selected = None
    if bind_host:
        matches = [row for row in classified if row["ipAddress"] == bind_host]
        selected = matches[0] if matches else {"ipAddress": bind_host, "eligibleForLiveSecondHostServerBind": False}
    selected_bind_host_eligible = bool(selected["eligibleForLiveSecondHostServerBind"]) if selected else bool(candidates)

    command_source_allowed_by_contract = command_source_kind in COMMAND_SOURCE_KINDS if command_source_kind else None
    command_source_allowed_by_topology = False
    if command_source_kind == "distinct-vm-private-lan-labeled-vm-only":
        command_source_allowed_by_topology = host_topology == "vm-labeled-same-physical"
    elif command_source_kind == "distinct-physical-host-private-lan":
        command_source_allowed_by_topology = host_topology == "distinct-physical-private-host"
    server_inputs_complete = bool(
        private_lan_proof
        and client_identity_fingerprint
        and selected_bind_host_eligible
        and command_source_allowed_by_contract
        and command_source_allowed_by_topology
    )
    return {
        "schemaVersion": SCHEMA,
        "scope": SCOPE,
        "status": "host-preflight-ready-for-external-client" if candidates else "host-preflight-needs-private-bind-address",
        "proofBooleans": {key: False for key in PROOF_FALSE_KEYS},
        "hostInterfacePreflight": {
            "interfaceCount": len(classified),
            "candidatePrivateBindAddressCount": len(candidates),
            "wslOnHostInterfaceCount": sum(1 for row in classified if row["wslOnHostInterface"]),
            "currentWorkstationMaySelfCertifySecondHost": False,
            "wslOnHostMayCountAsSecondHost": False,
            "distinctPhysicalHostRequiredForPhysicalProof": True,
            "vmLabeledProofMustRemainSamePhysicalMachineOnly": True,
            "selectedBindHost": selected,
            "interfaces": classified,
        },
        "requestedRunInputs": {
            "commandSourceKind": command_source_kind,
            "hostTopology": host_topology,
            "commandSourceKindAllowedByContract": command_source_allowed_by_contract,
            "commandSourceKindAllowedByHostTopology": command_source_allowed_by_topology,
            "privateLanProofPathProvided": private_lan_proof is not None,
            "clientIdentityFingerprintProvided": bool(client_identity_fingerprint),
            "selectedBindHostEligible": selected_bind_host_eligible,
            "serverCommandInputsComplete": server_inputs_complete,
        },
        "liveRunRequirements": {key: True for key in REQUIRED_LIVE_REQUIREMENTS},
        "nextCommands": [
            "py -3 tools\\winui_original_binary_second_host_command_source_client.py --identity-preflight --client-copied-profile-root <client-copied-profile-root> --client-installed-game-root <client-installed-game-root> [omit manual runtime-kind overrides for live proof; manual overrides are attempt-only diagnostics]",
            "py -3 tools\\build_winui_original_binary_second_host_command_source_bundle.py server <private-lan-proof> --bind-host <host-private-ip> --command-source-kind <distinct-physical-host-private-lan|distinct-vm-private-lan-labeled-vm-only> --client-invitation <os-temp-json> --client-identity-fingerprint <client-fingerprint> --host-copied-profile-root <host-copied-profile-root> --host-installed-game-root <host-installed-game-root>",
            "py -3 tools\\winui_original_binary_second_host_command_source_client.py <os-temp-json> --client-copied-profile-root <client-copied-profile-root> --client-installed-game-root <client-installed-game-root> [omit manual runtime-kind overrides for live proof; manual overrides are attempt-only diagnostics]",
            "py -3 tools\\winui_safe_copy_online_second_host_command_source_check.py <private-bundle> --live",
        ],
        "nonClaims": {
            "doesNotOpenListener": True,
            "doesNotCreateInvitation": True,
            "doesNotLaunchBea": True,
            "doesNotAttachCdb": True,
            "doesNotSendGameInput": True,
            "doesNotEnableHostJoin": True,
            "doesNotProvePlayerReadyNetplay": True,
        },
    }


def validate_summary(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("scope") == SCOPE, "scope mismatch")
    proof = payload.get("proofBooleans")
    require(isinstance(proof, dict), "missing proofBooleans")
    for key in PROOF_FALSE_KEYS:
        require(proof.get(key) is False, f"proof boolean must remain false: {key}")
    requirements = payload.get("liveRunRequirements")
    require(isinstance(requirements, dict), "missing liveRunRequirements")
    for key in REQUIRED_LIVE_REQUIREMENTS:
        require(requirements.get(key) is True, f"live run requirement must remain true: {key}")
    host = payload.get("hostInterfacePreflight")
    require(isinstance(host, dict), "missing hostInterfacePreflight")
    require(host.get("currentWorkstationMaySelfCertifySecondHost") is False, "host must not self-certify second-host proof")
    require(host.get("wslOnHostMayCountAsSecondHost") is False, "WSL-on-host must not count as second-host proof")
    requested = payload.get("requestedRunInputs")
    require(isinstance(requested, dict), "missing requestedRunInputs")
    topology = requested.get("hostTopology")
    require(topology in HOST_TOPOLOGIES, "unknown host topology")
    source_kind = requested.get("commandSourceKind")
    if requested.get("serverCommandInputsComplete") is True:
        require(requested.get("selectedBindHostEligible") is True, "complete server inputs require an eligible selected bind host")
    if source_kind == "distinct-physical-host-private-lan":
        require(
            requested.get("commandSourceKindAllowedByHostTopology") is (topology == "distinct-physical-private-host"),
            "physical command-source mode must require explicit distinct physical host topology",
        )
    if source_kind == "distinct-vm-private-lan-labeled-vm-only":
        require(
            requested.get("commandSourceKindAllowedByHostTopology") is (topology == "vm-labeled-same-physical"),
            "VM command-source mode must require explicit VM-labeled topology",
        )
    nonclaims = payload.get("nonClaims")
    require(isinstance(nonclaims, dict), "missing nonClaims")
    for key, value in nonclaims.items():
        require(value is True, f"non-claim token must remain true: {key}")
    return {
        "schemaVersion": payload["schemaVersion"],
        "scope": payload["scope"],
        "candidatePrivateBindAddressCount": host.get("candidatePrivateBindAddressCount"),
        "wslOnHostInterfaceCount": host.get("wslOnHostInterfaceCount"),
        "serverCommandInputsComplete": payload.get("requestedRunInputs", {}).get("serverCommandInputsComplete"),
        "baseOnlineMultiplayerReady": proof["baseOnlineMultiplayerReady"],
        "hostJoinControlsMayBeEnabled": proof["hostJoinControlsMayBeEnabled"],
        "acceptedLiveSecondHostCommandSourceProof": proof["acceptedLiveSecondHostCommandSourceProof"],
    }


def run_self_test() -> None:
    fixture_rows = [
        {"InterfaceAlias": "Wi-Fi", "IPAddress": fixture_ipv4(172, 20, 10, 7), "PrefixLength": 28, "AddressState": "Preferred"},
        {"InterfaceAlias": "vEthernet (WSL (Hyper-V firewall))", "IPAddress": fixture_ipv4(172, 26, 112, 1), "PrefixLength": 20, "AddressState": "Preferred"},
        {"InterfaceAlias": "Loopback Pseudo-Interface 1", "IPAddress": fixture_ipv4(127, 0, 0, 1), "PrefixLength": 8, "AddressState": "Preferred"},
    ]
    summary = build_summary(interface_rows=fixture_rows)
    checked = validate_summary(summary)
    require(checked["candidatePrivateBindAddressCount"] == 1, "fixture should have one non-WSL private candidate")
    require(checked["wslOnHostInterfaceCount"] == 1, "fixture should classify one WSL interface")

    overclaim = json.loads(json.dumps(summary))
    overclaim["proofBooleans"]["baseOnlineMultiplayerReady"] = True
    try:
        validate_summary(overclaim)
    except SecondHostLiveReadinessError:
        pass
    else:
        raise AssertionError("base online overclaim should fail")

    weakened = json.loads(json.dumps(summary))
    weakened["liveRunRequirements"]["requiresListenerPostCloseConnectRejection"] = False
    try:
        validate_summary(weakened)
    except SecondHostLiveReadinessError:
        pass
    else:
        raise AssertionError("missing live listener teardown requirement should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bind-host")
    parser.add_argument("--command-source-kind", choices=COMMAND_SOURCE_KINDS)
    parser.add_argument("--host-topology", choices=HOST_TOPOLOGIES, default="current-host-only")
    parser.add_argument("--private-lan-proof", type=Path)
    parser.add_argument("--client-identity-fingerprint")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host live readiness self-test: PASS")
        return 0

    summary = build_summary(
        interface_rows=collect_windows_ipv4_interfaces(),
        bind_host=args.bind_host,
        command_source_kind=args.command_source_kind,
        host_topology=args.host_topology,
        private_lan_proof=args.private_lan_proof,
        client_identity_fingerprint=args.client_identity_fingerprint,
    )
    checked = validate_summary(summary)
    if args.check:
        print("WinUI original-binary second-host live readiness check: PASS")
    print(json.dumps(checked if args.check else summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SecondHostLiveReadinessError, json.JSONDecodeError) as exc:
        print(f"WinUI original-binary second-host live readiness check: FAIL: {exc}")
        raise SystemExit(2)
