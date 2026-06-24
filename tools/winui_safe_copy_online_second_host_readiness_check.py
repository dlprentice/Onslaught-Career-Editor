#!/usr/bin/env python3
"""Validate the second-host readiness contract for original-binary netplay work."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "roadmap" / "original-binary-online-second-host-readiness.v1.json"
SCHEMA = "winui-original-binary-second-host-readiness.v1"
SCOPE = "second-host-command-source-readiness-not-runtime-proof"
NEXT_EVIDENCE_ID = "distinct-private-host-command-source-proof"
HOST_JOIN_ENABLEMENT_ID = "host-join-enablement-composite-proof"
RUNTIME_EVIDENCE_ID = "host-runtime-delivery-from-source-bound-distinct-command-source"
SOURCE_BOUND_RUNTIME_EVIDENCE_ID = RUNTIME_EVIDENCE_ID
LIVE_READINESS_EVIDENCE_ID = "host-live-run-readiness-preflight"
LIVE_RUN_KIT_EVIDENCE_ID = "second-host-live-run-kit"
LIVE_CRITERIA_KEYS = (
    "supportsExplicitLiveValidationMode",
    "requiresLiveValidationModeBeforeRuntimePromotion",
    "requiresLiveServerClientTranscript",
    "requiresLiveNegativeCaseTranscript",
    "requiresPerEventServerObservedAtUnixForLiveProof",
    "requiresMonotonicServerObservedTimestampsInsideInvitationWindowForLiveProof",
    "requiresNonFixtureMachineFingerprintSourcesForLiveProof",
    "requiresAutoPlatformRuntimeHostKindSourcesForLiveProof",
    "rejectsSyntheticLiveLabeledFixtures",
    "requiresListenerLifecycleReceipt",
    "requiresListenerTeardownEvidence",
    "requiresListenerPostCloseConnectRejection",
    "requiresSignedClientSourceSafetyPostflight",
    "requiresTwoPhasePrePostSourceSafetyForLiveProof",
    "requiresOperatorSuppliedHashOnlyLiveProofRejection",
    "requiresVmLabeledProofSamePhysicalMachineOnly",
    "requiresPhysicalSecondHostProofNotSamePhysicalMachineOnly",
)


class SecondHostReadinessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostReadinessError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def list_at(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    require(isinstance(value, list), f"missing list: {key}")
    return value


def make_fixture() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "readinessScope": SCOPE,
        "status": "ready-to-run-when-distinct-private-host-exists",
        "readiness": {
            "baseOnlineMultiplayerReady": False,
            "secondHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "hostJoinControlsMayBeEnabled": False,
            "currentWorkstationMaySelfCertifySecondHost": False,
        },
        "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
        "metadataOnlySlots": ["P3", "P4"],
        "secondHostAcceptanceCriteria": {
            "allowedCommandSourceKinds": [
                "distinct-physical-host-private-lan",
                "distinct-vm-private-lan-labeled-vm-only",
            ],
            "forbiddenCommandSourceKinds": [
                "loopback",
                "same-workstation-process",
                "wsl-on-host",
                "public-internet-host",
                "unknown-peer",
            ],
            "requiresDifferentHostIdentity": True,
            "requiresNonLoopbackPrivateAddress": True,
            "requiresAddressAssignedToLocalInterface": True,
            "requiresSanitizedHostAndClientInterfaceEvidence": True,
            "requiresPinnedHostIdentity": True,
            "requiresSessionScopedAuthentication": True,
            "requiresCopiedProfileHashesOnBothSides": True,
            "requiresInstalledGamePrePostHashesOnBothSides": True,
            "supportsExplicitLiveValidationMode": True,
            "requiresLiveValidationModeBeforeRuntimePromotion": True,
            "requiresLiveServerClientTranscript": True,
            "requiresLiveNegativeCaseTranscript": True,
            "requiresPerEventServerObservedAtUnixForLiveProof": True,
            "requiresMonotonicServerObservedTimestampsInsideInvitationWindowForLiveProof": True,
            "requiresNonFixtureMachineFingerprintSourcesForLiveProof": True,
            "requiresAutoPlatformRuntimeHostKindSourcesForLiveProof": True,
            "rejectsSyntheticLiveLabeledFixtures": True,
            "requiresListenerLifecycleReceipt": True,
            "requiresListenerTeardownEvidence": True,
            "requiresListenerPostCloseConnectRejection": True,
            "requiresSignedClientSourceSafetyPostflight": True,
            "requiresTwoPhasePrePostSourceSafetyForLiveProof": True,
            "requiresOperatorSuppliedHashOnlyLiveProofRejection": True,
            "requiresVmLabeledProofSamePhysicalMachineOnly": True,
            "requiresPhysicalSecondHostProofNotSamePhysicalMachineOnly": True,
            "rejectsProgramFilesMutationTargets": True,
            "vmEvidenceIsNotPhysicalSecondHostProof": True,
        },
        "blockedActions": [
            {
                "id": "host-online-session",
                "label": "Host online session",
                "enabled": False,
                "requires": HOST_JOIN_ENABLEMENT_ID,
            },
            {
                "id": "join-online-session",
                "label": "Join online session",
                "enabled": False,
                "requires": HOST_JOIN_ENABLEMENT_ID,
            },
            {
                "id": "public-matchmaking",
                "label": "Public matchmaking",
                "enabled": False,
                "requires": "public-server-matchmaking-release-security-proof",
            },
            {
                "id": "native-bea-netcode",
                "label": "Native BEA netcode",
                "enabled": False,
                "requires": "native-bea-network-code-path-proof",
            },
        ],
        "requiredNextEvidence": [
            {
                "id": LIVE_READINESS_EVIDENCE_ID,
                "description": "A host-side preflight classifies usable private bind interfaces and the exact inputs required for a live distinct-host or VM-labeled command-source run without opening a listener or claiming proof.",
                "mustProve": [
                    "privateBindCandidateClassification",
                    "wslOnHostRejectedAsSecondHost",
                    "physicalModeRequiresDistinctPhysicalHostTopology",
                    "vmModeRequiresVmLabeledSamePhysicalMachineTopology",
                    "allProofBooleansRemainFalse",
                ],
            },
            {
                "id": LIVE_RUN_KIT_EVIDENCE_ID,
                "description": "A public-safe checked run kit packages host readiness, computed client identity/source-safety preflight, required private live-run inputs, and redacted command templates without opening a listener or claiming proof.",
                "mustProve": [
                    "computedClientIdentityPreflightRequired",
                    "validatedPrivateLanProofRequired",
                    "computedHostSourceSafetyRootsRequired",
                    "osTempOutsideRepoJsonInvitationPathRequired",
                    "pairedLiveCommandSourceRejectsSyntheticLiveFixtures",
                    "redactedHostClientCommandTemplates",
                    "selectedBindHostEligibleForLiveRun",
                    "noListenerInvitationBeaCdbOrInput",
                    "allProofBooleansRemainFalse",
                ],
            },
            {
                "id": NEXT_EVIDENCE_ID,
                "description": "A command source running from a distinct private host or VM feeds the existing host-authority P1/P2 relay path.",
                "mustProve": [
                    "distinctHostIdentity",
                    "privateAddressNotLoopback",
                    "pinnedServerIdentity",
                    "sessionScopedAuthentication",
                    "acceptedP2Command",
                    "rejectedP3P4GameplayCommands",
                    "noPublicSocket",
                    "noInstalledGameMutation",
                ],
            },
            {
                "id": RUNTIME_EVIDENCE_ID,
                "description": "The accepted distinct-host command is delivered through the copied BEA host-helper path with mapped P2 sequence and exact-PID CDB evidence.",
                "mustProve": [
                    "hostHelperInputSent",
                    "hostHelperInputBoundToSecondHostCommandSource",
                    "requiresMappedP2SequenceReceipt",
                    "p2MappedInputSequence=down:E,wait:500,up:E",
                    "p2RuntimeRoute=P2/inputDevice1/bottom-split-half",
                    "deliveredOriginalBinaryCommandCount",
                    "acceptedOriginalBinaryGameplaySlotsP1P2",
                    "metadataOnlySlotsP3P4",
                    "newBeaLaunchOrFreshRuntimeArtifact",
                ],
            },
            {
                "id": HOST_JOIN_ENABLEMENT_ID,
                "description": "Composite Host/Join enablement proof requiring both distinct-host command-source proof and direct copied-runtime causality proof.",
                "mustProve": [
                    NEXT_EVIDENCE_ID,
                    SOURCE_BOUND_RUNTIME_EVIDENCE_ID,
                    "exactPidCdbRuntimeInputEvidence",
                    "noFixtureOrPosthocRuntimeBinding",
                ],
            },
        ],
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "secondHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "coOpVersusRuntimeProof": False,
            "physicalGamepadProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "secretsSerialized": False,
            "privateArtifactContentPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "installedGameMutationAllowed": False,
        },
    }


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("readinessScope") == SCOPE, "readiness scope mismatch")

    readiness = object_at(payload, "readiness")
    for key in (
        "baseOnlineMultiplayerReady",
        "secondHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "hostJoinControlsMayBeEnabled",
        "currentWorkstationMaySelfCertifySecondHost",
    ):
        require(readiness.get(key) is False, f"readiness overclaim must remain false: {key}")

    accepted_slots = list_at(payload, "acceptedOriginalBinaryGameplaySlots")
    metadata_slots = list_at(payload, "metadataOnlySlots")
    require(accepted_slots == ["P1", "P2"], "accepted original-binary gameplay slots must remain P1/P2")
    require(metadata_slots == ["P3", "P4"], "metadata-only slots must remain P3/P4")

    criteria = object_at(payload, "secondHostAcceptanceCriteria")
    allowed_sources = criteria.get("allowedCommandSourceKinds")
    forbidden_sources = criteria.get("forbiddenCommandSourceKinds")
    require(isinstance(allowed_sources, list) and allowed_sources, "allowed command-source kinds are missing")
    require(isinstance(forbidden_sources, list) and forbidden_sources, "forbidden command-source kinds are missing")
    require(
        allowed_sources == [
            "distinct-physical-host-private-lan",
            "distinct-vm-private-lan-labeled-vm-only",
        ],
        "allowed command-source kinds must stay distinct-host/private-LAN only",
    )
    for forbidden in (
        "loopback",
        "same-workstation-process",
        "wsl-on-host",
        "public-internet-host",
        "unknown-peer",
    ):
        require(forbidden in forbidden_sources, f"missing forbidden command-source kind: {forbidden}")
    for key in (
        "requiresDifferentHostIdentity",
        "requiresNonLoopbackPrivateAddress",
        "requiresAddressAssignedToLocalInterface",
        "requiresSanitizedHostAndClientInterfaceEvidence",
        "requiresPinnedHostIdentity",
        "requiresSessionScopedAuthentication",
        "requiresCopiedProfileHashesOnBothSides",
        "requiresInstalledGamePrePostHashesOnBothSides",
        *LIVE_CRITERIA_KEYS,
        "rejectsProgramFilesMutationTargets",
        "vmEvidenceIsNotPhysicalSecondHostProof",
    ):
        require(criteria.get(key) is True, f"second-host acceptance criterion must remain true: {key}")

    blocked_actions = list_at(payload, "blockedActions")
    require(len(blocked_actions) >= 4, "blocked action list is incomplete")
    blocked_by_id = {}
    for row in blocked_actions:
        require(isinstance(row, dict), "blocked action row must be an object")
        action_id = str(row.get("id") or "")
        require(action_id, "blocked action id is missing")
        blocked_by_id[action_id] = row
        require(row.get("enabled") is False, f"blocked action must remain disabled: {action_id}")
    for action_id in ("host-online-session", "join-online-session", "public-matchmaking", "native-bea-netcode"):
        require(action_id in blocked_by_id, f"missing blocked action: {action_id}")
    require(blocked_by_id["host-online-session"].get("requires") == HOST_JOIN_ENABLEMENT_ID, "host action must require composite Host/Join proof")
    require(blocked_by_id["join-online-session"].get("requires") == HOST_JOIN_ENABLEMENT_ID, "join action must require composite Host/Join proof")

    required_next = list_at(payload, "requiredNextEvidence")
    required_ids = {str(row.get("id") or "") for row in required_next if isinstance(row, dict)}
    require(LIVE_READINESS_EVIDENCE_ID in required_ids, "missing host live-run readiness preflight requirement")
    require(LIVE_RUN_KIT_EVIDENCE_ID in required_ids, "missing second-host live-run kit requirement")
    require(NEXT_EVIDENCE_ID in required_ids, "missing distinct-host next evidence requirement")
    require(RUNTIME_EVIDENCE_ID in required_ids, "missing distinct-host runtime evidence requirement")
    require(HOST_JOIN_ENABLEMENT_ID in required_ids, "missing composite Host/Join enablement evidence requirement")
    for row in required_next:
        require(isinstance(row, dict), "required evidence row must be an object")
        must_prove = row.get("mustProve")
        require(isinstance(must_prove, list) and must_prove, f"required evidence row lacks mustProve list: {row.get('id')}")
        if row.get("id") == LIVE_RUN_KIT_EVIDENCE_ID:
            for token in (
                "validatedPrivateLanProofRequired",
                "computedHostSourceSafetyRootsRequired",
                "osTempOutsideRepoJsonInvitationPathRequired",
                "pairedLiveCommandSourceRejectsSyntheticLiveFixtures",
            ):
                require(token in must_prove, f"live-run-kit row missing mustProve token: {token}")

    nonclaims = object_at(payload, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")

    release = object_at(payload, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof boundary missing")
    for key in (
        "secretsSerialized",
        "privateArtifactContentPublished",
        "publicHostOrMatchmakingEndpointPublished",
        "installedGameMutationAllowed",
    ):
        require(release.get(key) is False, f"release boundary must remain false: {key}")

    return {
        "schemaVersion": payload["schemaVersion"],
        "readinessScope": payload["readinessScope"],
        "baseOnlineMultiplayerReady": readiness["baseOnlineMultiplayerReady"],
        "secondHostProof": readiness["secondHostProof"],
        "multiHostLanProof": readiness["multiHostLanProof"],
        "publicMatchmakingProof": readiness["publicMatchmakingProof"],
        "nativeBeaNetcodeProof": readiness["nativeBeaNetcodeProof"],
        "activeP3P4OriginalBinaryGameplayProof": readiness["activeP3P4OriginalBinaryGameplayProof"],
        "acceptedOriginalBinaryGameplaySlots": accepted_slots,
        "metadataOnlySlots": metadata_slots,
        "allowedCommandSourceKinds": allowed_sources,
        "forbiddenCommandSourceKinds": forbidden_sources,
        "minimumRequiredNextEvidence": NEXT_EVIDENCE_ID,
        "blockedActionCount": len(blocked_actions),
        "requiredNextEvidenceCount": len(required_next),
    }


def run_self_test() -> None:
    validate_contract(make_fixture())
    overclaim = make_fixture()
    overclaim["readiness"]["multiHostLanProof"] = True
    try:
        validate_contract(overclaim)
    except SecondHostReadinessError:
        pass
    else:
        raise AssertionError("multi-host overclaim should fail validation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("Second-host readiness self-test: PASS")
        return 0
    summary = validate_contract(read_json(args.path))
    if args.check:
        print("Second-host readiness contract check: PASS")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SecondHostReadinessError, json.JSONDecodeError) as exc:
        print(f"Second-host readiness contract check: FAIL: {exc}")
        raise SystemExit(2)
