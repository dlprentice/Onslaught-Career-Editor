#!/usr/bin/env python3
"""Validate the Host/Join enablement gate for original-binary netplay work."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import winui_safe_copy_online_second_host_readiness_check as readiness_check
import winui_safe_copy_online_second_host_runtime_causality_check as runtime_causality_check


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "roadmap" / "original-binary-online-host-join-enablement.v1.json"
READINESS_PATH = ROOT / "roadmap" / "original-binary-online-second-host-readiness.v1.json"
COMMAND_SOURCE_PATH = ROOT / "roadmap" / "original-binary-online-second-host-command-source.v1.json"
RUNTIME_EXECUTOR_PATH = ROOT / "roadmap" / "original-binary-online-second-host-runtime-executor.v1.json"
RUNTIME_CAUSALITY_PATH = ROOT / "roadmap" / "original-binary-online-second-host-runtime-causality.v1.json"
SCHEMA = "winui-original-binary-host-join-enablement.v1"
SCOPE = "host-join-controls-composite-proof-gate-not-player-ready-online"
ENABLEMENT_PROOF_ID = "host-join-enablement-composite-proof"
COMMAND_SOURCE_PROOF_ID = "distinct-private-host-command-source-proof"
RUNTIME_CAUSALITY_PROOF_ID = "host-runtime-delivery-from-source-bound-distinct-command-source"
ACCEPTED_SLOTS = ["P1", "P2"]
METADATA_SLOTS = ["P3", "P4"]
LIVE_PROMOTION_REQUIREMENT_KEYS = {
    "requiresAcceptedLiveDistinctCommandSourceProof",
    "requiresDirectSecondHostRuntimeCausalityReceipt",
    "requiresRuntimeInputDerivedFromSecondHostCommandSource",
    "requiresRuntimeDrivenBySecondHostCommandSource",
    "requiresAcceptedCommandPayloadHashBoundEndToEnd",
    "requiresInvitationLifecycleHashBoundEndToEnd",
    "requiresExactPidCdbEvidence",
    "requiresAcceptedSecondHostPayloadHashInSchedulerReceipt",
    "requiresAcceptedSecondHostPayloadHashInBridgeReceipt",
    "requiresAcceptedSecondHostPayloadHashInRuntimeInputWindowReceipt",
    "requiresAcceptedSecondHostPayloadHashInExactPidCdbReceipt",
    "requiresHostHelperInputBoundToSecondHostCommandSource",
    "requiresMappedP2SequenceReceipt",
    "rejectsSecondHostClientDirectGameInputBypass",
    "requiresNoFixtureReceiptMode",
    "rejectsFixtureOrPosthocRuntimeBinding",
    "rejectsSelfTestFixtureArtifacts",
    "rejectsCommandSourceOnlyEnablement",
    "rejectsCompatibilityExecutorPromotion",
    "requiresSecondHostRuntimePromotionGuard",
    "keepsPublicMatchmakingSeparate",
    "keepsNativeBeaNetcodeSeparate",
    "keepsP3P4OriginalBinaryGameplaySeparate",
}
CURRENT_EVIDENCE_KEYS = {
    "acceptedLiveDistinctCommandSourceProof",
    "acceptedLiveSecondHostRuntimeDeliveryProof",
    "runtimeInputDerivedFromSecondHostCommandSource",
    "runtimeDrivenBySecondHostCommandSource",
    "exactPidCdbRuntimeInputEvidence",
    "hostJoinControlsMayBeEnabled",
    "baseOnlineMultiplayerReady",
    "multiHostLanPlayProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "activeP3P4OriginalBinaryGameplayProof",
}
NONCLAIM_KEYS = {
    "baseOnlineMultiplayerReady",
    "multiHostLanPlayProof",
    "publicMatchmakingProof",
    "publicServerProof",
    "nativeBeaNetcodeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "moreThanTwoOriginalBinaryRuntimePlayersProof",
    "coOpVersusRuntimeProof",
    "physicalGamepadProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
}


class HostJoinEnablementError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostJoinEnablementError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def list_at(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    require(isinstance(value, list), f"missing list: {key}")
    return value


def require_exact_keys(row: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(row))
    unexpected = sorted(set(row) - expected)
    require(not missing and not unexpected, f"{label} keys mismatch; missing={missing}; unexpected={unexpected}")


def make_readiness_fixture() -> dict[str, Any]:
    payload = readiness_check.make_fixture()
    for row in payload["blockedActions"]:
        if row["id"] in {"host-online-session", "join-online-session"}:
            row["requires"] = ENABLEMENT_PROOF_ID
    if not any(row.get("id") == ENABLEMENT_PROOF_ID for row in payload["requiredNextEvidence"]):
        payload["requiredNextEvidence"].append(
            {
                "id": ENABLEMENT_PROOF_ID,
                "description": "Composite Host/Join enablement proof that combines accepted distinct-host command source and direct copied-runtime causality.",
                "mustProve": [
                    COMMAND_SOURCE_PROOF_ID,
                    RUNTIME_CAUSALITY_PROOF_ID,
                    "exactPidCdbRuntimeInputEvidence",
                    "noFixtureOrPosthocRuntimeBinding",
                ],
            }
        )
    return payload


def make_fixture() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "enablementScope": SCOPE,
        "status": "host-join-disabled-until-command-source-and-runtime-causality-proof",
        "requiredProofs": [
            {
                "id": COMMAND_SOURCE_PROOF_ID,
                "description": "Accepted live distinct private-host or VM-labeled command-source proof.",
            },
            {
                "id": RUNTIME_CAUSALITY_PROOF_ID,
                "description": "Source-bound copied-runtime causality proof from the accepted second-host command source with exact-PID CDB evidence.",
            },
        ],
        "acceptedOriginalBinaryGameplaySlots": ACCEPTED_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "blockedActions": [
            {
                "id": "host-online-session",
                "enabled": False,
                "requires": ENABLEMENT_PROOF_ID,
            },
            {
                "id": "join-online-session",
                "enabled": False,
                "requires": ENABLEMENT_PROOF_ID,
            },
        ],
        "livePromotionRequirements": {
            "requiresAcceptedLiveDistinctCommandSourceProof": True,
            "requiresDirectSecondHostRuntimeCausalityReceipt": True,
            "requiresRuntimeInputDerivedFromSecondHostCommandSource": True,
            "requiresRuntimeDrivenBySecondHostCommandSource": True,
            "requiresAcceptedCommandPayloadHashBoundEndToEnd": True,
            "requiresInvitationLifecycleHashBoundEndToEnd": True,
            "requiresExactPidCdbEvidence": True,
            "requiresAcceptedSecondHostPayloadHashInSchedulerReceipt": True,
            "requiresAcceptedSecondHostPayloadHashInBridgeReceipt": True,
            "requiresAcceptedSecondHostPayloadHashInRuntimeInputWindowReceipt": True,
            "requiresAcceptedSecondHostPayloadHashInExactPidCdbReceipt": True,
            "requiresHostHelperInputBoundToSecondHostCommandSource": True,
            "requiresMappedP2SequenceReceipt": True,
            "rejectsSecondHostClientDirectGameInputBypass": True,
            "requiresNoFixtureReceiptMode": True,
            "rejectsFixtureOrPosthocRuntimeBinding": True,
            "rejectsSelfTestFixtureArtifacts": True,
            "rejectsCommandSourceOnlyEnablement": True,
            "rejectsCompatibilityExecutorPromotion": True,
            "requiresSecondHostRuntimePromotionGuard": True,
            "keepsPublicMatchmakingSeparate": True,
            "keepsNativeBeaNetcodeSeparate": True,
            "keepsP3P4OriginalBinaryGameplaySeparate": True,
        },
        "currentEvidence": {
            "acceptedLiveDistinctCommandSourceProof": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "runtimeInputDerivedFromSecondHostCommandSource": False,
            "runtimeDrivenBySecondHostCommandSource": False,
            "exactPidCdbRuntimeInputEvidence": False,
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "multiHostLanPlayProof": False,
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
            "privateArtifactContentPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "Host/Join remains disabled until an accepted live distinct command-source proof and a direct "
            "source-bound runtime-causality proof with exact-PID CDB evidence both exist. Command-source proof "
            "alone does not enable Host/Join. Fixture, self-test, and posthoc compatibility artifacts are not "
            "player-ready online netplay proof. The current compatibility runtime executor must fail the "
            "promotion guard until scheduler, bridge, runtime input-window, and exact-PID CDB receipts bind the "
            "accepted second-host payload hash, mapped P2 sequence, host-helper receipt, and invitation lifecycle hash in one same-run chain. The remote "
            "client sends command envelopes, not direct game input; accepted runtime promotion requires "
            "hostHelperInputBoundToSecondHostCommandSource=true, requiresMappedP2SequenceReceipt=true, and gameInputSentBySecondHostClient=false."
        ),
    }


def proof_ids(payload: dict[str, Any]) -> list[str]:
    rows = list_at(payload, "requiredProofs")
    ids: list[str] = []
    for row in rows:
        require(isinstance(row, dict), "required proof row must be an object")
        proof_id = str(row.get("id") or "")
        require(proof_id, "required proof id is missing")
        ids.append(proof_id)
    return ids


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("enablementScope") == SCOPE, "scope mismatch")
    ids = proof_ids(payload)
    require(ids == [COMMAND_SOURCE_PROOF_ID, RUNTIME_CAUSALITY_PROOF_ID], "Host/Join must require command-source plus runtime-causality proofs")
    require(list_at(payload, "acceptedOriginalBinaryGameplaySlots") == ACCEPTED_SLOTS, "accepted gameplay slots must remain P1/P2")
    require(list_at(payload, "metadataOnlySlots") == METADATA_SLOTS, "metadata-only slots must remain P3/P4")

    blocked = list_at(payload, "blockedActions")
    require(len(blocked) >= 2, "blocked Host/Join actions are missing")
    by_id: dict[str, dict[str, Any]] = {}
    for row in blocked:
        require(isinstance(row, dict), "blocked action row must be an object")
        action_id = str(row.get("id") or "")
        require(action_id, "blocked action id missing")
        by_id[action_id] = row
        require(row.get("enabled") is False, f"action must remain disabled: {action_id}")
    for action_id in ("host-online-session", "join-online-session"):
        require(action_id in by_id, f"missing blocked action: {action_id}")
        require(by_id[action_id].get("requires") == ENABLEMENT_PROOF_ID, f"{action_id} must require composite Host/Join proof")

    requirements = object_at(payload, "livePromotionRequirements")
    require_exact_keys(requirements, LIVE_PROMOTION_REQUIREMENT_KEYS, "livePromotionRequirements")
    for key in LIVE_PROMOTION_REQUIREMENT_KEYS:
        require(requirements.get(key) is True, f"missing live promotion requirement: {key}")

    evidence = object_at(payload, "currentEvidence")
    require_exact_keys(evidence, CURRENT_EVIDENCE_KEYS, "currentEvidence")
    for key in CURRENT_EVIDENCE_KEYS:
        require(evidence.get(key) is False, f"current evidence must remain false until direct proof exists: {key}")
    nonclaims = object_at(payload, "nonClaims")
    require_exact_keys(nonclaims, NONCLAIM_KEYS, "nonClaims")
    for key in NONCLAIM_KEYS:
        require(nonclaims.get(key) is False, f"non-claim must remain false: {key}")
    release = object_at(payload, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof boundary missing")
    for key in (
        "privateArtifactContentPublished",
        "publicHostOrMatchmakingEndpointPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(release.get(key) is False, f"release boundary must remain false: {key}")
    claim = str(payload.get("claimBoundary") or "")
    for token in (
        "Host/Join remains disabled",
        "Command-source proof alone does not enable Host/Join",
        "exact-PID CDB evidence",
        "Fixture, self-test, and posthoc compatibility artifacts are not player-ready online netplay proof",
        "current compatibility runtime executor must fail the promotion guard",
        "accepted second-host payload hash, mapped P2 sequence, host-helper receipt, and invitation lifecycle hash in one same-run chain",
        "remote client sends command envelopes, not direct game input",
        "hostHelperInputBoundToSecondHostCommandSource=true",
        "requiresMappedP2SequenceReceipt=true",
        "gameInputSentBySecondHostClient=false",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "schemaVersion": payload["schemaVersion"],
        "enablementScope": payload["enablementScope"],
        "requiredProofs": ids,
        "acceptedOriginalBinaryGameplaySlots": ACCEPTED_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "hostJoinControlsMayBeEnabled": evidence["hostJoinControlsMayBeEnabled"],
        "baseOnlineMultiplayerReady": evidence["baseOnlineMultiplayerReady"],
        "requiredProofCount": len(ids),
    }


def validate_readiness_contract(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        summary = readiness_check.validate_contract(payload)
    except readiness_check.SecondHostReadinessError as exc:
        raise HostJoinEnablementError(str(exc)) from exc
    blocked = list_at(payload, "blockedActions")
    by_id = {str(row.get("id") or ""): row for row in blocked if isinstance(row, dict)}
    for action_id in ("host-online-session", "join-online-session"):
        require(by_id.get(action_id, {}).get("requires") == ENABLEMENT_PROOF_ID, f"{action_id} readiness must require composite Host/Join proof")
    required = list_at(payload, "requiredNextEvidence")
    required_ids = {str(row.get("id") or "") for row in required if isinstance(row, dict)}
    for required_id in (COMMAND_SOURCE_PROOF_ID, RUNTIME_CAUSALITY_PROOF_ID, ENABLEMENT_PROOF_ID):
        require(required_id in required_ids, f"readiness missing required evidence: {required_id}")
    composite = next((row for row in required if isinstance(row, dict) and row.get("id") == ENABLEMENT_PROOF_ID), None)
    require(isinstance(composite, dict), "readiness missing composite Host/Join evidence row")
    composite_must_prove = composite.get("mustProve")
    require(isinstance(composite_must_prove, list), "composite Host/Join row must have mustProve list")
    require(COMMAND_SOURCE_PROOF_ID in composite_must_prove, "composite Host/Join row missing command-source proof")
    require(RUNTIME_CAUSALITY_PROOF_ID in composite_must_prove, "composite Host/Join row missing source-bound runtime causality proof")
    return summary


def validate_command_source_contract(payload: dict[str, Any]) -> None:
    evidence = object_at(payload, "currentEvidence")
    require(evidence.get("acceptedLiveSecondHostCommandSourceProof") is False, "tracked command-source gate must not claim accepted live proof")
    require(evidence.get("acceptedLiveSecondHostRuntimeDeliveryProof") is False, "command-source gate must not claim runtime delivery")
    require(evidence.get("hostJoinControlsMayBeEnabled") is False, "command-source gate must keep Host/Join disabled")
    next_required = object_at(payload, "nextRequiredProof")
    require(next_required.get("id") == RUNTIME_CAUSALITY_PROOF_ID, "command-source gate must point to source-bound runtime proof id")
    require(next_required.get("requiredBeforeHostJoinEnablement") is True, "command-source gate must point to later Host/Join runtime proof")


def validate_runtime_executor_contract(payload: dict[str, Any]) -> None:
    blockers = object_at(payload, "livePromotionBlockers")
    for key in (
        "requiresDirectSecondHostRuntimeCausalityReceipt",
        "requiresFreshCopiedRuntimeExecutor",
        "requiresExactPidCdbEvidence",
        "requiresHostHelperInputBoundToSecondHostCommandSource",
        "requiresMappedP2SequenceReceipt",
    ):
        require(blockers.get(key) is True, f"runtime executor blocker missing: {key}")
    evidence = object_at(payload, "currentEvidence")
    for key in (
        "acceptedLiveSecondHostRuntimeDeliveryProof",
        "runtimeDrivenBySecondHostCommandSource",
        "hostJoinControlsMayBeEnabled",
        "baseOnlineMultiplayerReady",
    ):
        require(evidence.get(key) is False, f"runtime executor evidence must remain false: {key}")
    next_required = object_at(payload, "nextRequiredProof")
    require(next_required.get("id") == RUNTIME_CAUSALITY_PROOF_ID, "runtime executor next proof id mismatch")


def validate_runtime_causality_contract(payload: dict[str, Any]) -> None:
    try:
        summary = runtime_causality_check.validate_contract(payload)
    except runtime_causality_check.SecondHostRuntimeCausalityError as exc:
        raise HostJoinEnablementError(str(exc)) from exc
    require(summary["hostJoinControlsMayBeEnabled"] is False, "runtime causality gate must not enable Host/Join")
    require(summary["baseOnlineMultiplayerReady"] is False, "runtime causality gate must not claim base online readiness")


def validate_repo_contracts(
    *,
    enablement_path: Path = CONTRACT_PATH,
    readiness_path: Path = READINESS_PATH,
    command_source_path: Path | None = COMMAND_SOURCE_PATH,
    runtime_executor_path: Path | None = RUNTIME_EXECUTOR_PATH,
    runtime_causality_path: Path | None = RUNTIME_CAUSALITY_PATH,
) -> dict[str, Any]:
    summary = validate_contract(read_json(enablement_path))
    validate_readiness_contract(read_json(readiness_path))
    if command_source_path is not None:
        validate_command_source_contract(read_json(command_source_path))
    if runtime_executor_path is not None:
        validate_runtime_executor_contract(read_json(runtime_executor_path))
    if runtime_causality_path is not None:
        try:
            runtime_causality_payload = read_json(runtime_causality_path)
        except FileNotFoundError as exc:
            raise HostJoinEnablementError(f"runtime causality contract missing: {runtime_causality_path}") from exc
        validate_runtime_causality_contract(runtime_causality_payload)
    return summary


def run_self_test() -> None:
    validate_contract(make_fixture())
    validate_readiness_contract(make_readiness_fixture())
    overclaim = make_fixture()
    overclaim["currentEvidence"]["hostJoinControlsMayBeEnabled"] = True
    try:
        validate_contract(overclaim)
    except HostJoinEnablementError:
        pass
    else:
        raise AssertionError("Host/Join enablement overclaim should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", nargs="?", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary Host/Join enablement checker self-test: PASS")
        return 0
    if args.check:
        print("WinUI original-binary Host/Join enablement gate check: PASS")
        print(json.dumps(validate_repo_contracts(enablement_path=args.contract), indent=2, sort_keys=True))
        return 0
    print(json.dumps(validate_contract(read_json(args.contract)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostJoinEnablementError,
        readiness_check.SecondHostReadinessError,
        runtime_causality_check.SecondHostRuntimeCausalityError,
        json.JSONDecodeError,
    ) as exc:
        print(f"WinUI original-binary Host/Join enablement check: FAIL: {exc}")
        raise SystemExit(2)
