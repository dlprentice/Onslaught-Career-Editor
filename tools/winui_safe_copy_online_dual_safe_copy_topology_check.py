#!/usr/bin/env python3
"""Validate the dual-safe-copy topology contract for original-binary netplay work."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-dual-safe-copy-topology.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_dual_safe_copy_topology_2026-06-22.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
PACKAGE_JSON = ROOT / "package.json"

SCHEMA = "winui-original-binary-online-dual-safe-copy-topology.v1"
SCOPE = "dual-safe-copy-same-workstation-topology-not-online-play"
EXPECTED_STATUS = "complete public-safe dual-safe-copy topology contract; no BEA launch or runtime proof"
EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_dual_safe_copy_topology_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_dual_safe_copy_topology_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_dual_safe_copy_topology_check.py --check"
)

COMMAND_SOURCE_ID = "distinct-endpoint-command-source-proof"
SOURCE_BOUND_RUNTIME_CAUSALITY_ID = "source-bound-copied-runtime-causality-proof"
HOST_JOIN_COMPOSITE_ID = "host-join-enablement-composite-proof"
PLAYER_READY_ID = "player-ready-host-join-release-proof"

EXPECTED_ROLES = ["host", "joiner"]
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
SECRET_LIKE_KEYS = {
    "secret",
    "sharedsecret",
    "rawsecret",
    "authkey",
    "credential",
    "password",
    "token",
    "privatekey",
    "apikey",
}
PATH_LEAK_RE = re.compile(r"([A-Za-z]:\\|\\\\|/|%USERPROFILE%|%APPDATA%|Program Files|Steam\\steamapps)", re.IGNORECASE)


class DualSafeCopyTopologyError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DualSafeCopyTopologyError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def list_at(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    require(isinstance(value, list), f"missing list: {key}")
    return value


def require_no_secret_like_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(key.lower() not in SECRET_LIKE_KEYS, f"secret-like field is not allowed at {path}.{key}")
            require_no_secret_like_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_secret_like_keys(child, f"{path}[{index}]")


def require_public_safe_label(value: Any, field: str) -> str:
    require(isinstance(value, str) and value.strip(), f"{field} must be a non-empty string")
    require(PATH_LEAK_RE.search(value) is None, f"{field} must not contain a private or absolute path")
    require(value == value.strip(), f"{field} must not contain leading/trailing whitespace")
    return value


def make_fixture() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "status": EXPECTED_STATUS,
        "date": "2026-06-22",
        "scope": SCOPE,
        "topology": {
            "topologyKind": "same-workstation-two-app-owned-safe-copies",
            "topologyProofClass": "topology-contract-not-runtime-proof",
            "safeCopyCount": 2,
            "sameWorkstationOnly": True,
            "samePhysicalMachineOnly": True,
            "separateGameViewsProven": False,
            "distinctEndpointProof": False,
            "playerReadyOnlineProof": False,
        },
        "safeCopies": [
            {
                "role": "host",
                "safeCopyRootLabel": "host-safe-copy-root",
                "rootPathPublished": False,
                "absolutePathsSerialized": False,
                "safeCopyRootPathFingerprint": "1111111111111111111111111111111111111111111111111111111111111111",
                "safeCopyContentManifestSha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "copiedExecutableLabel": "host-copied-bea-exe",
                "executableRelativePath": "BEA.exe",
                "executableSha256": "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                "sourceRootLabel": "selected-game-root-read-only",
                "appOwnedRootRequired": True,
                "separateRootRequired": True,
                "launchAllowedByThisRung": False,
                "installedGameMutationAllowed": False,
                "originalExecutableMutationAllowed": False,
                "steamInstallWriteAllowed": False,
                "runtimeRole": "future-host-copied-runtime",
            },
            {
                "role": "joiner",
                "safeCopyRootLabel": "joiner-safe-copy-root",
                "rootPathPublished": False,
                "absolutePathsSerialized": False,
                "safeCopyRootPathFingerprint": "2222222222222222222222222222222222222222222222222222222222222222",
                "safeCopyContentManifestSha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "copiedExecutableLabel": "joiner-copied-bea-exe",
                "executableRelativePath": "BEA.exe",
                "executableSha256": "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                "sourceRootLabel": "selected-game-root-read-only",
                "appOwnedRootRequired": True,
                "separateRootRequired": True,
                "launchAllowedByThisRung": False,
                "installedGameMutationAllowed": False,
                "originalExecutableMutationAllowed": False,
                "steamInstallWriteAllowed": False,
                "runtimeRole": "future-joiner-command-source-safe-copy",
            },
        ],
        "topologyCounters": {
            "safeCopyRootDescriptorCount": 2,
            "safeCopyExecutableDescriptorCount": 2,
            "distinctSafeCopyRootPairCount": 1,
            "sessionRoleDescriptorCount": 2,
            "newBeaLaunchCount": 0,
            "processStartCount": 0,
            "cdbAttachCount": 0,
            "listenerOpenCount": 0,
            "invitationCreateCount": 0,
            "hostJoinControlsEnabledCount": 0,
            "nPlayerOriginalBinaryRuntimeProof": 0,
        },
        "proofBoundary": {
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
            "acceptedLiveSecondHostCommandSourceProof": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "acceptedLiveSecondHostRuntimeCausalityProof": False,
            "secondHostProof": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "hostHelperInputSent": False,
            "gameInputSentByTopologyTool": False,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "maxOriginalBinaryActiveSlotsProven": 2,
            "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
            "metadataOnlySlots": ["P3", "P4"],
        },
        "sideEffects": {
            "beaLaunchCount": 0,
            "processStartCount": 0,
            "cdbAttachCount": 0,
            "listenerOpened": False,
            "invitationCreated": False,
            "inputSent": False,
            "patchBytesChanged": False,
            "publicReleaseCreated": False,
        },
        "requiredFutureEvidence": [
            {
                "id": COMMAND_SOURCE_ID,
                "mustProve": [
                    "distinctEndpointIdentity",
                    "privateNonLoopbackCommandSource",
                    "sessionScopedAuthentication",
                    "acceptedP2Command",
                    "noInstalledGameMutation",
                ],
            },
            {
                "id": SOURCE_BOUND_RUNTIME_CAUSALITY_ID,
                "mustProve": [
                    "acceptedCommandPayloadHashBoundToRuntimeInput",
                    "invitationLifecycleHashBoundToRuntimeInput",
                    "exactPidCdbEvidence",
                    "copiedRuntimeArtifact",
                    "hostHelperDeliveryReceipt",
                ],
            },
            {
                "id": HOST_JOIN_COMPOSITE_ID,
                "mustProve": [
                    COMMAND_SOURCE_ID,
                    SOURCE_BOUND_RUNTIME_CAUSALITY_ID,
                    "fixtureAndPosthocArtifactsRejected",
                ],
            },
            {
                "id": PLAYER_READY_ID,
                "mustProve": [
                    "userFacingHostJoinFlow",
                    "releaseTestedCleanupAndRecovery",
                    "noPublicPrivateProofLeakage",
                ],
            },
        ],
        "nonClaims": {
            "separateScreenNetplayProof": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "coOpVersusRuntimeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "privateArtifactContentPublished": False,
            "copiedExecutablePublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "installedGameMutationAllowed": False,
            "secretsSerialized": False,
        },
    }


def validate_safe_copies(payload: dict[str, Any]) -> list[str]:
    rows = list_at(payload, "safeCopies")
    require(len(rows) == 2, "dual-safe-copy topology must carry exactly two safe-copy rows")
    roles: list[str] = []
    roots: set[str] = set()
    exe_labels: set[str] = set()
    for row in rows:
        require(isinstance(row, dict), "safe-copy row must be an object")
        role = require_public_safe_label(row.get("role"), "safe copy role")
        require(role in EXPECTED_ROLES, f"unexpected safe-copy role: {role}")
        roles.append(role)
        root_label = require_public_safe_label(row.get("safeCopyRootLabel"), f"{role} safeCopyRootLabel")
        exe_label = require_public_safe_label(row.get("copiedExecutableLabel"), f"{role} copiedExecutableLabel")
        require_public_safe_label(row.get("sourceRootLabel"), f"{role} sourceRootLabel")
        root_fingerprint = require_public_safe_label(
            row.get("safeCopyRootPathFingerprint"), f"{role} safeCopyRootPathFingerprint"
        )
        manifest_sha = require_public_safe_label(
            row.get("safeCopyContentManifestSha256"), f"{role} safeCopyContentManifestSha256"
        )
        exe_sha = require_public_safe_label(row.get("executableSha256"), f"{role} executableSha256")
        require(bool(HEX64_RE.match(root_fingerprint)), f"{role} root fingerprint must be hex64")
        require(bool(HEX64_RE.match(manifest_sha)), f"{role} content manifest SHA-256 must be hex64")
        require(row.get("executableRelativePath") == "BEA.exe", f"{role} executable relative path must be BEA.exe")
        require(bool(HEX64_RE.match(exe_sha)), f"{role} executable SHA-256 must be hex64")
        require(root_label not in roots, "safe-copy root labels must be distinct")
        require(exe_label not in exe_labels, "copied executable labels must be distinct")
        roots.add(root_label)
        exe_labels.add(exe_label)
        for key in ("appOwnedRootRequired", "separateRootRequired"):
            require(row.get(key) is True, f"{role} {key} must be true")
        for key in ("rootPathPublished", "absolutePathsSerialized", "launchAllowedByThisRung"):
            require(row.get(key) is False, f"{role} {key} must be false")
        for key in ("installedGameMutationAllowed", "originalExecutableMutationAllowed", "steamInstallWriteAllowed"):
            require(row.get(key) is False, f"{role} {key} must be false")
        require_public_safe_label(row.get("runtimeRole"), f"{role} runtimeRole")
    require(roles == EXPECTED_ROLES, "safe-copy roles must be host then joiner")
    return roles


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    require_no_secret_like_keys(payload)
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("scope") == SCOPE, "scope mismatch")
    require(payload.get("status") == EXPECTED_STATUS, "status mismatch")

    topology = object_at(payload, "topology")
    require(topology.get("topologyKind") == "same-workstation-two-app-owned-safe-copies", "topology kind mismatch")
    require(topology.get("topologyProofClass") == "topology-contract-not-runtime-proof", "topology proof class mismatch")
    require(topology.get("safeCopyCount") == 2, "safe-copy count must be two")
    require(topology.get("sameWorkstationOnly") is True, "same-workstation boundary must be explicit")
    require(topology.get("samePhysicalMachineOnly") is True, "same-physical-machine boundary must be explicit")
    for key in ("separateGameViewsProven", "distinctEndpointProof", "playerReadyOnlineProof"):
        require(topology.get(key) is False, f"topology overclaim must be false: {key}")

    roles = validate_safe_copies(payload)

    counters = object_at(payload, "topologyCounters")
    expected_counters = {
        "safeCopyRootDescriptorCount": 2,
        "safeCopyExecutableDescriptorCount": 2,
        "distinctSafeCopyRootPairCount": 1,
        "sessionRoleDescriptorCount": 2,
        "newBeaLaunchCount": 0,
        "processStartCount": 0,
        "cdbAttachCount": 0,
        "listenerOpenCount": 0,
        "invitationCreateCount": 0,
        "hostJoinControlsEnabledCount": 0,
        "nPlayerOriginalBinaryRuntimeProof": 0,
    }
    for key, expected in expected_counters.items():
        require(counters.get(key) == expected, f"topology counter mismatch for {key}")

    proof = object_at(payload, "proofBoundary")
    for key in (
        "hostJoinControlsMayBeEnabled",
        "baseOnlineMultiplayerReady",
        "acceptedLiveSecondHostCommandSourceProof",
        "acceptedLiveSecondHostRuntimeDeliveryProof",
        "acceptedLiveSecondHostRuntimeCausalityProof",
        "secondHostProof",
        "multiHostLanPlayProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "moreThanTwoOriginalBinaryRuntimePlayersProof",
        "hostHelperInputSent",
        "gameInputSentByTopologyTool",
    ):
        require(proof.get(key) is False, f"proof overclaim must remain false: {key}")
    require(proof.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(proof.get("maxOriginalBinaryActiveSlotsProven") == 2, "original-binary active slot proof must stay two")
    require(proof.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots must stay P1/P2")
    require(proof.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots must stay P3/P4")

    side_effects = object_at(payload, "sideEffects")
    for key in ("beaLaunchCount", "processStartCount", "cdbAttachCount"):
        require(side_effects.get(key) == 0, f"side-effect count must stay zero: {key}")
    for key in ("listenerOpened", "invitationCreated", "inputSent", "patchBytesChanged", "publicReleaseCreated"):
        require(side_effects.get(key) is False, f"side-effect overclaim must stay false: {key}")

    required = list_at(payload, "requiredFutureEvidence")
    required_ids = {str(row.get("id") or "") for row in required if isinstance(row, dict)}
    for evidence_id in (COMMAND_SOURCE_ID, SOURCE_BOUND_RUNTIME_CAUSALITY_ID, HOST_JOIN_COMPOSITE_ID, PLAYER_READY_ID):
        require(evidence_id in required_ids, f"missing future evidence gate: {evidence_id}")
    for row in required:
        require(isinstance(row, dict), "future evidence row must be an object")
        require_public_safe_label(row.get("id"), "future evidence id")
        must_prove = row.get("mustProve")
        require(isinstance(must_prove, list) and must_prove, f"future evidence row lacks mustProve: {row.get('id')}")
        for item in must_prove:
            require_public_safe_label(item, f"future evidence token for {row.get('id')}")

    non_claims = object_at(payload, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")

    release = object_at(payload, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof boundary must be true")
    for key in (
        "privateArtifactContentPublished",
        "copiedExecutablePublished",
        "publicHostOrMatchmakingEndpointPublished",
        "installedGameMutationAllowed",
        "secretsSerialized",
    ):
        require(release.get(key) is False, f"release boundary must remain false: {key}")

    return {
        "schemaVersion": payload["schemaVersion"],
        "scope": payload["scope"],
        "safeCopyCount": topology["safeCopyCount"],
        "roles": roles,
        "sameWorkstationOnly": topology["sameWorkstationOnly"],
        "samePhysicalMachineOnly": topology["samePhysicalMachineOnly"],
        "topologyCounters": counters,
        "hostJoinControlsMayBeEnabled": proof["hostJoinControlsMayBeEnabled"],
        "baseOnlineMultiplayerReady": proof["baseOnlineMultiplayerReady"],
        "acceptedLiveSecondHostCommandSourceProof": proof["acceptedLiveSecondHostCommandSourceProof"],
        "acceptedLiveSecondHostRuntimeCausalityProof": proof["acceptedLiveSecondHostRuntimeCausalityProof"],
        "beaLaunchCount": side_effects["beaLaunchCount"],
        "cdbAttachCount": side_effects["cdbAttachCount"],
        "requiredFutureEvidence": sorted(required_ids),
        "claimBoundary": (
            "This validates a public-safe same-workstation topology contract for two app-owned safe copies. "
            "It does not launch BEA, attach CDB, open a listener, create an invitation, enable Host/Join, "
            "prove distinct-endpoint command source, or prove player-ready netplay."
        ),
    }


def require_doc_tokens() -> None:
    token_sets = {
        READINESS: (
            "Original Binary Dual Safe-Copy Topology Readiness Note",
            "winui-original-binary-online-dual-safe-copy-topology.v1",
            "dual-safe-copy-same-workstation-topology-not-online-play",
            "safeCopyCount=2",
            "roles=host,joiner",
            "safeCopyRootDescriptorCount=2",
            "sameWorkstationOnly=true",
            "samePhysicalMachineOnly=true",
            "hostJoinControlsMayBeEnabled=false",
            "baseOnlineMultiplayerReady=false",
            "BEA launch count: 0",
            "CDB attach count: 0",
        ),
        FEASIBILITY: (
            "dual-safe-copy same-workstation topology",
            "original-binary-online-dual-safe-copy-topology.v1.json",
            "safeCopyCount=2",
            "roles=host,joiner",
            "safeCopyRootDescriptorCount=2",
            "sameWorkstationOnly=true",
            "not player-ready netplay",
        ),
        REGISTER: (
            "dual-safe-copy same-workstation topology",
            "safeCopyCount=2",
            "roles=host,joiner",
            "safeCopyRootDescriptorCount=2",
            "hostJoinControlsMayBeEnabled=false",
            "baseOnlineMultiplayerReady=false",
        ),
        CAPABILITIES: (
            "dual-safe-copy same-workstation topology",
            "safeCopyCount=2",
            "roles=host,joiner",
            "safeCopyRootDescriptorCount=2",
            "sameWorkstationOnly=true",
            "not player-ready netplay",
        ),
    }
    for path, tokens in token_sets.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path} missing token: {token}")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:winui-original-binary-dual-safe-copy-topology") == EXPECTED_SCRIPT,
        "missing package dual-safe-copy topology script",
    )


def validate_repo_contract() -> dict[str, Any]:
    summary = validate_contract(read_json(CONTRACT))
    require_doc_tokens()
    return summary


def run_self_test() -> None:
    validate_contract(make_fixture())
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, make_fixture())
        validate_contract(read_json(path))

    for edit in (
        lambda payload: payload["proofBoundary"].__setitem__("hostJoinControlsMayBeEnabled", True),
        lambda payload: payload["sideEffects"].__setitem__("beaLaunchCount", 1),
        lambda payload: payload["nonClaims"].__setitem__("multiHostLanPlayProof", True),
        lambda payload: payload["safeCopies"][1].__setitem__("safeCopyRootLabel", "host-safe-copy-root"),
        lambda payload: payload["safeCopies"][0].__setitem__("safeCopyRootLabel", r"C:\Users\david\leak"),
    ):
        payload = make_fixture()
        edit(payload)
        try:
            validate_contract(payload)
        except DualSafeCopyTopologyError:
            pass
        else:
            raise AssertionError("invalid dual-safe-copy topology fixture should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=CONTRACT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary dual-safe-copy topology checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("use --check or --self-test")
    if args.path == CONTRACT:
        summary = validate_repo_contract()
    else:
        summary = validate_contract(read_json(args.path))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DualSafeCopyTopologyError, json.JSONDecodeError) as exc:
        print(f"WinUI original-binary dual-safe-copy topology check: FAIL: {exc}")
        raise SystemExit(2)
