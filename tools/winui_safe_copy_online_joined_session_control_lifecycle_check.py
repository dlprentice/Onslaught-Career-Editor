#!/usr/bin/env python3
"""Validate same-host joined-session control-lifecycle proof for the online ladder."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-joined-session-control-lifecycle.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_joined_session_control_lifecycle_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
FEASIBILITY_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCHEMA = "winui-original-binary-joined-session-control-lifecycle.v1"
EXPECTED_SCOPE = "original-binary-online-joined-session-control-lifecycle"
EXPECTED_STATUS = "complete public-safe same-host joined-session control-lifecycle proof; no BEA launch, CDB attach, true online multiplayer, second-host LAN, public matchmaking, native BEA netcode, active P3/P4 gameplay, or mode-runtime proof"
EXPECTED_PROOF_CLASS = "control-plane-lifecycle-harness-not-runtime-gameplay-proof"
EXPECTED_CONTROL_SCOPE = "joined-session-control-lifecycle-same-host-not-online-play"
EXPECTED_SAME_HOST_SESSION_CONTROL_SCHEMA = "winui-original-binary-joined-session-same-host-session-control.v1"
EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE = "joined-session-same-host-session-control-not-online-play"
EXPECTED_SECURITY_SCOPE = "same-host-session-control-message-smoke-not-production-security-proof"
EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_joined_session_control_lifecycle_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_joined_session_control_lifecycle_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_joined_session_control_lifecycle_check.py --check"
)
EXPECTED_CONTROL_ACTIONS = {
    "register-copied-host-session",
    "list-compatible-session",
    "issue-p2-join-ticket",
    "activate-p2-join-ticket",
    "heartbeat-p2-active",
    "pause-command-stream",
    "resume-command-stream",
    "soft-reconnect-p2-same-ticket-fingerprint",
    "spectator-metadata-query",
    "admin-metadata-query",
    "graceful-leave-p2",
}
EXPECTED_REJECTION_REASONS = {
    "expired-join-ticket",
    "replay-cache-hit",
    "session-identity-mismatch",
    "join-ticket-slot-mismatch",
    "metadata-slot-gameplay-not-allowed",
    "spectator-metadata-only",
    "admin-metadata-only",
    "control-plane-never-sends-game-input",
    "public-matchmaking-not-proven",
    "second-physical-host-not-proven",
    "native-bea-netcode-not-proven",
    "co-op-versus-mode-runtime-not-proven",
    "unknown-field",
    "max-json-line-bytes-exceeded",
    "stale-heartbeat",
    "non-next-control-sequence",
    "missing-runtime-compatible-relay-hash",
    "runtime-compatible-relay-hash-mismatch",
    "secret-bearing-message-rejected",
    "raw-private-path-message-rejected",
    "left-session-requires-new-ticket",
}
EXPECTED_REJECTED_CASES = {
    "expired-ticket": "expired-join-ticket",
    "replayed-ticket": "replay-cache-hit",
    "wrong-session-id": "session-identity-mismatch",
    "wrong-client-slot": "join-ticket-slot-mismatch",
    "p3-gameplay-activation": "metadata-slot-gameplay-not-allowed",
    "p4-gameplay-activation": "metadata-slot-gameplay-not-allowed",
    "spectator-gameplay-command": "spectator-metadata-only",
    "admin-gameplay-mutation": "admin-metadata-only",
    "direct-game-input-from-control-plane": "control-plane-never-sends-game-input",
    "public-matchmaking-request": "public-matchmaking-not-proven",
    "second-host-claim": "second-physical-host-not-proven",
    "native-netcode-claim": "native-bea-netcode-not-proven",
    "mode-runtime-claim": "co-op-versus-mode-runtime-not-proven",
    "unknown-field": "unknown-field",
    "oversized-control-message": "max-json-line-bytes-exceeded",
    "stale-heartbeat": "stale-heartbeat",
    "bad-sequence": "non-next-control-sequence",
    "missing-runtime-relay-hash": "missing-runtime-compatible-relay-hash",
    "wrong-runtime-relay-hash": "runtime-compatible-relay-hash-mismatch",
    "secret-bearing-control-message": "secret-bearing-message-rejected",
    "raw-private-path-control-message": "raw-private-path-message-rejected",
    "reconnect-after-leave": "left-session-requires-new-ticket",
}
FALSE_NON_CLAIM_KEYS = {
    "baseOnlineMultiplayerReady",
    "secondPhysicalHostProof",
    "multiHostLanProof",
    "publicMatchmakingProof",
    "publicServerProof",
    "nativeBeaNetcodeProof",
    "coOpModeRuntimeProof",
    "versusModeRuntimeProof",
    "teamVersusRuntimeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "physicalGamepadProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "joinedSessionVisibleMovementCausalityProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
}


class JoinedSessionControlLifecycleError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise JoinedSessionControlLifecycleError(message)


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


def validate_contract(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(payload.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(payload.get("status") == EXPECTED_STATUS, "status boundary drifted")

    boundary = object_at(payload, "proofBoundary")
    require(boundary.get("proofClass") == EXPECTED_PROOF_CLASS, "proof class mismatch")
    require(boundary.get("sessionControlScope") == EXPECTED_CONTROL_SCOPE, "session-control scope mismatch")
    require(boundary.get("sameHostSessionControlSchema") == EXPECTED_SAME_HOST_SESSION_CONTROL_SCHEMA, "same-host session-control schema alias mismatch")
    require(boundary.get("sameHostSessionControlScope") == EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE, "same-host session-control scope alias mismatch")
    require(boundary.get("sourceRuntimeProfile") == "original-binary-copied-local-splitscreen", "source runtime profile mismatch")
    require(boundary.get("acceptedJoinTicketSlot") == "P2", "accepted ticket slot mismatch")
    require(boundary.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots mismatch")
    require(boundary.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")
    require(boundary.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected gameplay slots mismatch")
    require(boundary.get("sessionControlLifecycleProven") is True, "lifecycle flag missing")
    require(boundary.get("sessionControlBoundToRuntimeRelayHash") is True, "runtime relay binding flag missing")
    require(boundary.get("upstreamJoinedSessionRuntimeCausalityProven") is True, "upstream causality flag missing")
    require(boundary.get("upstreamNewBeaLaunchCount") == 1, "upstream launch count mismatch")
    require(boundary.get("upstreamCdbAttachCount") == 1, "upstream CDB count mismatch")
    for key in ("newBeaLaunchCount", "cdbAttachCount", "nPlayerOriginalBinaryRuntimeProof"):
        require(boundary.get(key) == 0, f"{key} must stay zero")
    for key in (
        "hostHelperInputSentBySessionControl",
        "gameInputSentBySessionControl",
        "activeP3P4OriginalBinaryGameplayProof",
        "baseOnlineMultiplayerReady",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "publicBind",
        "publicNetworkSocketsOpened",
    ):
        require(boundary.get(key) is False, f"{key} must stay false")
    require(boundary.get("sameHostOnly") is True, "same-host flag missing")
    require(boundary.get("samePhysicalMachineOnly") is True, "same-physical-machine flag missing")

    lifecycle = object_at(payload, "controlLifecycle")
    require(lifecycle.get("acceptedControlActionCount") == 11, "accepted control action count mismatch")
    require(lifecycle.get("rejectedControlCaseCount") == 22, "rejected control case count mismatch")
    require(lifecycle.get("reconnectProofScope") == "metadata-reconnect-only-not-runtime-reconnect", "reconnect scope mismatch")
    require(lifecycle.get("spectatorAdminMetadataOnly") is True, "spectator/admin metadata-only flag missing")
    require(lifecycle.get("coOpVersusModeRuntimeProofSlices") == 0, "co-op/versus proof must stay zero")
    actions = list_at(lifecycle, "controlActionsAccepted")
    require({str(row.get("actionId")) for row in actions if isinstance(row, dict)} == EXPECTED_CONTROL_ACTIONS, "accepted control action set mismatch")
    require(len(actions) == lifecycle["acceptedControlActionCount"], "accepted control action list/count mismatch")
    for row in actions:
        require(isinstance(row, dict), "control action rows must be objects")
        require(row.get("accepted") is True, f"control action must be accepted: {row}")

    security = object_at(payload, "controlSecurity")
    require(security.get("securityScope") == EXPECTED_SECURITY_SCOPE, "security scope mismatch")
    require(security.get("inheritsSessionSecurityProof") is True, "session-security inheritance flag missing")
    for key in (
        "controlMessagesSchemaAllowlisted",
        "unknownFieldRejectionProof",
        "strictControlSchemaProof",
        "maxJsonLineBytesEnforced",
        "ticketReplayRejectionProof",
        "expiredTicketRejectionProof",
        "sequenceEnforcementProof",
        "staleHeartbeatRejectionProof",
        "pausedStreamDropsGameplayCommands",
        "reconnectAfterLeaveRejected",
    ):
        require(security.get(key) is True, f"security proof flag missing: {key}")
    require(security.get("maxJsonLineBytes") == 4096, "max JSON line bytes mismatch")
    require(security.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    for key in ("rawCredentialSerialized", "operatorSecretsRequired", "publicBind", "publicNetworkSocketsOpened"):
        require(security.get(key) is False, f"security boundary must stay false: {key}")

    rejected = list_at(payload, "rejectedControlCases")
    require(len(rejected) == lifecycle["rejectedControlCaseCount"], "rejected case count mismatch")
    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require(EXPECTED_REJECTION_REASONS.issubset(reasons), "rejection matrix missing required reasons")
    case_map = {str(row.get("caseId")): str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require(case_map == EXPECTED_REJECTED_CASES, "rejected case map drifted")
    for row in rejected:
        require(isinstance(row, dict), "rejected control case rows must be objects")
        require(row.get("accepted") is False, f"rejected case accepted: {row}")

    release = object_at(payload, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "release boundary missing")
    for key in (
        "rawPrivateProofPathPublished",
        "rawPrivateArtifactContentPublished",
        "absolutePrivatePathPublished",
        "rawRuntimePointerPublished",
        "rawRuntimePidPublished",
        "rawCdbLogPathPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(release.get(key) is False, f"release boundary must stay false: {key}")

    nonclaims = object_at(payload, "nonClaims")
    require(set(nonclaims) == FALSE_NON_CLAIM_KEYS, "non-claim key set drifted")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")

    claim = str(payload.get("claimBoundary", ""))
    for token in (
        "same-host joined-session control-lifecycle harness",
        "does not launch BEA",
        "prove base online multiplayer readiness",
        "prove a second physical host",
        "prove public matchmaking",
        "prove active P3/P4 original-binary gameplay",
        "prove co-op/versus runtime behavior",
    ):
        require(token in claim, f"claim boundary missing token: {token}")

    return {
        "schemaVersion": payload["schemaVersion"],
        "proofClass": boundary["proofClass"],
        "sessionControlScope": boundary["sessionControlScope"],
        "sameHostSessionControlScope": boundary["sameHostSessionControlScope"],
        "sessionControlLifecycleProven": boundary["sessionControlLifecycleProven"],
        "acceptedControlActionCount": lifecycle["acceptedControlActionCount"],
        "rejectedControlCaseCount": lifecycle["rejectedControlCaseCount"],
        "sameHostOnly": boundary["sameHostOnly"],
        "acceptedJoinTicketSlot": boundary["acceptedJoinTicketSlot"],
        "acceptedOriginalBinaryGameplaySlots": boundary["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": boundary["metadataOnlySlots"],
        "newBeaLaunchCount": boundary["newBeaLaunchCount"],
        "cdbAttachCount": boundary["cdbAttachCount"],
        "gameInputSentBySessionControl": boundary["gameInputSentBySessionControl"],
        "baseOnlineMultiplayerReady": boundary["baseOnlineMultiplayerReady"],
        "activeP3P4OriginalBinaryGameplayProof": boundary["activeP3P4OriginalBinaryGameplayProof"],
        "publicMatchmakingProof": boundary["publicMatchmakingProof"],
        "multiHostLanProof": boundary["multiHostLanProof"],
        "nativeBeaNetcodeProof": boundary["nativeBeaNetcodeProof"],
    }


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path}: missing token {token!r}")


def validate_repo() -> None:
    failures: list[str] = []
    validate_contract(CONTRACT)
    for path, tokens in {
        READINESS: (
            EXPECTED_SCHEMA,
            EXPECTED_CONTROL_SCOPE,
            EXPECTED_SAME_HOST_SESSION_CONTROL_SCHEMA,
            EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE,
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "metadata-reconnect-only-not-runtime-reconnect",
            "sameHostOnly=true",
            "newBeaLaunchCount=0",
            "cdbAttachCount=0",
            "gameInputSentBySessionControl=false",
            "baseOnlineMultiplayerReady=false",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
        ),
        FEASIBILITY: (
            "Joined-session control-lifecycle proof",
            EXPECTED_CONTROL_SCOPE,
            EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE,
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "metadata-reconnect-only-not-runtime-reconnect",
            "gameInputSentBySessionControl=false",
        ),
        REGISTER: (
            "joined-session control-lifecycle proof",
            EXPECTED_CONTROL_SCOPE,
            EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE,
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "sameHostOnly=true",
            "gameInputSentBySessionControl=false",
        ),
        CAPABILITIES: (
            "joined-session control-lifecycle proof",
            EXPECTED_CONTROL_SCOPE,
            EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE,
            "sessionControlLifecycleProven=true",
            "baseOnlineMultiplayerReady=false",
        ),
    }.items():
        for token in tokens:
            check_token(path, token, failures)
    if read_text(FEASIBILITY) != read_text(FEASIBILITY_MIRROR):
        failures.append("online feasibility lore mirror mismatch")
    if read_text(REGISTER) != read_text(REGISTER_MIRROR):
        failures.append("register lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("current capabilities lore mirror mismatch")

    scalability = read_json(SCALABILITY)
    policy = object_at(object_at(scalability, "scalableArchitecture"), "joinedSessionControlLifecyclePolicy")
    expected_policy = {
        "proofSchema": EXPECTED_SCHEMA,
        "sameHostSessionControlSchema": EXPECTED_SAME_HOST_SESSION_CONTROL_SCHEMA,
        "protocolVersion": "joined-session-same-host-session-control.v1",
        "sessionControlScope": EXPECTED_CONTROL_SCOPE,
        "sameHostSessionControlScope": EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE,
        "proofClass": EXPECTED_PROOF_CLASS,
        "sourceJoinedAuthoritySchema": "winui-original-binary-joined-session-same-host-runtime-authority.v1",
        "sourceJoinedCausalitySchema": "winui-original-binary-joined-session-runtime-causality.v1",
        "sessionControlLifecycleProven": True,
        "sessionControlBoundToRuntimeRelayHash": True,
        "upstreamJoinedSessionRuntimeCausalityProven": True,
        "acceptedJoinTicketSlot": "P2",
        "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
        "metadataOnlySlots": ["P3", "P4"],
        "rejectedGameplayRouteSlots": ["P3", "P4"],
        "acceptedControlActionCount": 11,
        "rejectedControlCaseCount": 22,
        "reconnectProofScope": "metadata-reconnect-only-not-runtime-reconnect",
        "spectatorAdminMetadataOnly": True,
        "securityScope": EXPECTED_SECURITY_SCOPE,
        "sameHostOnly": True,
        "samePhysicalMachineOnly": True,
        "newBeaLaunchCount": 0,
        "cdbAttachCount": 0,
        "hostHelperInputSentBySessionControl": False,
        "gameInputSentBySessionControl": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "baseOnlineMultiplayerReady": False,
        "secondPhysicalHostProof": False,
        "multiHostLanProof": False,
        "publicMatchmakingProof": False,
        "nativeBeaNetcodeProof": False,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "publicBind": False,
        "publicNetworkSocketsOpened": False,
        "rawCredentialSerialized": False,
        "operatorSecretsRequired": False,
        "privateProofReleaseExcludedByPolicy": True,
    }
    for key, expected in expected_policy.items():
        require(policy.get(key) == expected, f"scalability lifecycle policy drifted: {key}")

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-joined-session-control-lifecycle") != EXPECTED_SCRIPT:
        failures.append("package joined-session control-lifecycle script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-joined-session-control-lifecycle" not in aggregate:
        failures.append("aggregate runtime script missing joined-session control-lifecycle check")
    if failures:
        raise JoinedSessionControlLifecycleError("\n".join(failures))


def run_self_test() -> None:
    good = read_json(CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, good)
        validate_contract(path)
        mutations = (
            ("base online overclaim should fail", lambda v: v["proofBoundary"].__setitem__("baseOnlineMultiplayerReady", True)),
            ("BEA launch overclaim should fail", lambda v: v["proofBoundary"].__setitem__("newBeaLaunchCount", 1)),
            ("P3 gameplay overclaim should fail", lambda v: v["proofBoundary"].__setitem__("acceptedOriginalBinaryGameplaySlots", ["P1", "P2", "P3"])),
            ("direct game input should fail", lambda v: v["proofBoundary"].__setitem__("gameInputSentBySessionControl", True)),
            ("missing P4 rejection should fail", lambda v: v["proofBoundary"].__setitem__("rejectedGameplayRouteSlots", ["P3"])),
            ("public bind should fail", lambda v: v["controlSecurity"].__setitem__("publicBind", True)),
            ("replay rejection missing should fail", lambda v: v["controlSecurity"].__setitem__("ticketReplayRejectionProof", False)),
            ("rejected case accepted should fail", lambda v: v["rejectedControlCases"][0].__setitem__("accepted", True)),
            ("non-claim removed should fail", lambda v: v["nonClaims"].pop("nativeBeaNetcodeProof", None)),
        )
        for label, mutate in mutations:
            bad = json.loads(json.dumps(good))
            mutate(bad)
            write_json(path, bad)
            try:
                validate_contract(path)
            except JoinedSessionControlLifecycleError:
                continue
            raise JoinedSessionControlLifecycleError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", nargs="?", type=Path, default=CONTRACT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary joined-session control-lifecycle checker self-test: PASS")
        return 0
    if args.check:
        validate_repo()
        print(json.dumps(validate_contract(CONTRACT), indent=2, sort_keys=True))
        return 0
    print(json.dumps(validate_contract(args.contract), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except JoinedSessionControlLifecycleError as exc:
        print(f"WinUI original-binary joined-session control-lifecycle check: FAIL: {exc}")
        raise SystemExit(2)
