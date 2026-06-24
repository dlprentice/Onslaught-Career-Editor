#!/usr/bin/env python3
"""Shape-preflight Host/Join-grade second-host runtime promotion candidates.

The current second-host runtime executor is a compatibility/source-binding proof.
This checker defines the stricter no-BEA shape preflight for a later direct
second-host-to-runtime causality proof. It does not accept live runtime proof;
file-backed causality validation owns that decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_second_host_runtime_executor_bundle as executor_builder
import winui_safe_copy_online_second_host_runtime_executor_check_test as executor_test


SCHEMA = "winui-original-binary-second-host-runtime-promotion-guard.v1"
PROMOTION_SCOPE = "source-bound-second-host-command-to-copied-runtime-causality-not-host-join-enable"
RECEIPT_MODE = "live-source-bound-second-host-runtime-causality"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_HOST_HELPER_REMOTE_SLOT = "P2"
EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID = "second-host-p2-forward-0001"
EXPECTED_HOST_HELPER_PRIVATE_LAN_COMMAND_ID = "private-lan-p2-forward-0001"
EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID = "host-authority-p2-forward-0001"
EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE = "down:E,wait:500,up:E"
EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256 = hashlib.sha256(
    EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE.encode("utf-8")
).hexdigest()
EXPECTED_HOST_HELPER_RUNTIME_ROUTE = "P2/inputDevice1/bottom-split-half"
EXPECTED_HOST_HELPER_INPUT_DEVICE = 1


class SecondHostRuntimePromotionGuardError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimePromotionGuardError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def require_hash(value: Any, label: str) -> str:
    text = str(value or "")
    require(bool(HEX64_RE.fullmatch(text)), f"{label} must be a 64-char lowercase sha256")
    return text


def require_payload_hash_match(row: dict[str, Any], key: str, expected_hash: str, label: str) -> None:
    require(row.get(key) == expected_hash, f"{label} must bind accepted second-host request payload hash")


def require_mapped_p2_receipt(row: dict[str, Any], label: str) -> None:
    require(row.get("acceptedSecondHostCommandId") == EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID, f"{label} accepted command id mismatch")
    require(row.get("wouldForwardToPrivateLanCommandId") == EXPECTED_HOST_HELPER_PRIVATE_LAN_COMMAND_ID, f"{label} private-LAN command id mismatch")
    require(row.get("hostAuthorityAcceptedP2CommandId") == EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID, f"{label} host-authority command id mismatch")
    require(row.get("acceptedSecondHostRemoteSlot") == EXPECTED_HOST_HELPER_REMOTE_SLOT, f"{label} remote slot mismatch")
    require(row.get("p2MappedInputSequence") == EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE, f"{label} mapped P2 sequence mismatch")
    require(row.get("p2MappedInputSequenceSha256") == EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256, f"{label} mapped P2 sequence hash mismatch")
    require(row.get("p2RuntimeRoute") == EXPECTED_HOST_HELPER_RUNTIME_ROUTE, f"{label} runtime route mismatch")
    require(row.get("inputDevice") == EXPECTED_HOST_HELPER_INPUT_DEVICE, f"{label} input device mismatch")
    require(row.get("hostHelperInputSent") is True, f"{label} host-helper input flag missing")
    require(row.get("hostHelperInputBoundToSecondHostCommandSource") is True, f"{label} host-helper source binding missing")
    require(row.get("gameInputSentBySecondHostClient") is False, f"{label} direct second-host game input must be rejected")


def validate_promotion_candidate(payload: dict[str, Any], *, allow_synthetic_fixture: bool = False) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("promotionScope") == PROMOTION_SCOPE, "promotion scope mismatch")

    source_binding = object_at(payload, "sourceBinding")
    accepted_payload_hash = require_hash(
        source_binding.get("acceptedSecondHostCommandRequestPayloadSha256"),
        "sourceBinding.acceptedSecondHostCommandRequestPayloadSha256",
    )
    invitation_lifecycle_hash = require_hash(
        source_binding.get("secondHostInvitationLifecycleSha256"),
        "sourceBinding.secondHostInvitationLifecycleSha256",
    )
    require(
        source_binding.get("requiredBeforeAcceptedLiveRuntimeDelivery") is True,
        "source binding must remain required before live runtime delivery",
    )

    runtime_executor = object_at(payload, "secondHostRuntimeExecutor")
    for key in (
        "runtimeInputDerivedFromSecondHostCommandSource",
        "runtimeDrivenBySecondHostCommandSource",
        "acceptedLiveSecondHostRuntimeDeliveryProof",
    ):
        require(runtime_executor.get(key) is True, f"promotion candidate requires {key}=true")
    require(
        runtime_executor.get("runtimeInputDerivedFromHostAuthorityProof") is False,
        "promotion candidate must not be host-authority-derived runtime input",
    )
    require(
        runtime_executor.get("secondHostDirectRuntimeCausalityProofRequired") is False,
        "promotion candidate must satisfy, not defer, direct runtime causality",
    )

    receipt = object_at(payload, "sourceBoundRuntimeCausalityReceipt")
    require(receipt.get("receiptMode") == RECEIPT_MODE, "receipt mode mismatch")
    if allow_synthetic_fixture:
        require(payload.get("syntheticPromotionGuardFixture") is True, "synthetic self-test fixture must be explicit")
        require(receipt.get("fixtureOrPosthocBinding") is True, "synthetic self-test fixture must be marked fixture/posthoc")
        require(receipt.get("selfTestFixtureArtifact") is True, "synthetic self-test fixture must be marked self-test-only")
    else:
        require(payload.get("syntheticPromotionGuardFixture") is not True, "synthetic self-test fixture is not live promotion material")
        require(receipt.get("fixtureOrPosthocBinding") is False, "fixture/posthoc binding must be absent")
        require(receipt.get("selfTestFixtureArtifact") is False, "self-test fixture artifact must be absent")
    require(receipt.get("sameRunArtifactChain") is True, "promotion requires one same-run artifact chain")
    require_payload_hash_match(
        receipt,
        "acceptedSecondHostCommandRequestPayloadSha256",
        accepted_payload_hash,
        "causality receipt",
    )
    require_payload_hash_match(
        receipt,
        "secondHostInvitationLifecycleSha256",
        invitation_lifecycle_hash,
        "causality receipt",
    )

    receipt_rows = {
        "schedulerReceipt": "scheduler",
        "bridgeReceipt": "bridge",
        "runtimeInputWindowReceipt": "runtime input window",
        "exactPidCdbReceipt": "exact-PID CDB",
        "mappedP2SequenceReceipt": "mapped P2 sequence",
        "hostHelperDeliveryReceipt": "host-helper delivery",
    }
    for key, label in receipt_rows.items():
        row = object_at(receipt, key)
        require(row.get("present") is True, f"{label} receipt must be present")
        require(row.get("sourceBound") is True, f"{label} receipt must be source-bound")
        require(row.get("sameRunArtifact") is True, f"{label} receipt must be same-run")
        require_payload_hash_match(
            row,
            "acceptedSecondHostCommandRequestPayloadSha256",
            accepted_payload_hash,
            label,
        )
        require_payload_hash_match(
            row,
            "secondHostInvitationLifecycleSha256",
            invitation_lifecycle_hash,
            label,
        )
        if key in {"mappedP2SequenceReceipt", "hostHelperDeliveryReceipt"}:
            require_mapped_p2_receipt(row, label)

    runtime = object_at(payload, "runtimeEvidence")
    for key in (
        "exactPidCdbRuntimeInputEvidence",
        "hostHelperInputSent",
        "hostHelperInputBoundToSecondHostCommandSource",
    ):
        require(runtime.get(key) is True, f"runtime evidence requires {key}=true")
    require(runtime.get("hostHelperBoundRemoteSlot") == EXPECTED_HOST_HELPER_REMOTE_SLOT, "runtime evidence remote slot mismatch")
    require(
        runtime.get("hostHelperBoundAcceptedSecondHostCommandId") == EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
        "runtime evidence accepted second-host command id mismatch",
    )
    require(
        runtime.get("hostHelperBoundHostAuthorityCommandId") == EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
        "runtime evidence host-authority command id mismatch",
    )
    require(runtime.get("hostHelperMappedInputSequence") == EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE, "runtime evidence mapped P2 sequence mismatch")
    require(
        runtime.get("hostHelperMappedInputSequenceSha256") == EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
        "runtime evidence mapped P2 sequence hash mismatch",
    )
    require(runtime.get("hostHelperRuntimeRoute") == EXPECTED_HOST_HELPER_RUNTIME_ROUTE, "runtime evidence route mismatch")
    require(runtime.get("hostHelperInputDevice") == EXPECTED_HOST_HELPER_INPUT_DEVICE, "runtime evidence input device mismatch")
    require(
        runtime.get("gameInputSentBySecondHostClient") is False,
        "second-host client direct game input must remain a rejected bypass",
    )
    require(runtime.get("gameInputSentByHostAuthorityScheduler") is False, "runtime input must not be host-authority-scheduler sent")
    require(runtime.get("newBeaLaunchCount") == 1, "promotion requires one fresh copied-BEA launch")
    require(runtime.get("cdbAttachCount") == 1, "promotion requires one exact-PID CDB attach")

    nonclaims = object_at(payload, "nonClaims")
    for key in (
        "hostJoinControlsMayBeEnabled",
        "baseOnlineMultiplayerReady",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
    ):
        require(nonclaims.get(key) is False, f"non-claim must remain false: {key}")

    return {
        "schemaVersion": payload["schemaVersion"],
        "promotionScope": payload["promotionScope"],
        "acceptedSecondHostCommandRequestPayloadSha256": accepted_payload_hash,
        "secondHostInvitationLifecycleSha256": invitation_lifecycle_hash,
        "shapePreflightAccepted": True,
        "liveRuntimeProofAccepted": False,
        "requiresFileBackedRuntimeCausalityGate": True,
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
    }


def make_future_candidate_fixture() -> dict[str, Any]:
    payload_hash = "a" * 64
    invitation_hash = "b" * 64
    receipt_row = {
        "present": True,
        "sourceBound": True,
        "sameRunArtifact": True,
        "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
        "secondHostInvitationLifecycleSha256": invitation_hash,
        "acceptedSecondHostCommandId": EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
        "acceptedSecondHostRemoteSlot": EXPECTED_HOST_HELPER_REMOTE_SLOT,
        "wouldForwardToPrivateLanCommandId": EXPECTED_HOST_HELPER_PRIVATE_LAN_COMMAND_ID,
        "hostAuthorityAcceptedP2CommandId": EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
        "p2MappedInputSequence": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE,
        "p2MappedInputSequenceSha256": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
        "p2RuntimeRoute": EXPECTED_HOST_HELPER_RUNTIME_ROUTE,
        "inputDevice": EXPECTED_HOST_HELPER_INPUT_DEVICE,
        "hostHelperInputSent": True,
        "hostHelperInputBoundToSecondHostCommandSource": True,
        "gameInputSentBySecondHostClient": False,
    }
    return {
        "schemaVersion": SCHEMA,
        "promotionScope": PROMOTION_SCOPE,
        "syntheticPromotionGuardFixture": True,
        "sourceBinding": {
            "requiredBeforeAcceptedLiveRuntimeDelivery": True,
            "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
        },
        "secondHostRuntimeExecutor": {
            "runtimeInputDerivedFromHostAuthorityProof": False,
            "runtimeInputDerivedFromSecondHostCommandSource": True,
            "runtimeDrivenBySecondHostCommandSource": True,
            "acceptedLiveSecondHostRuntimeDeliveryProof": True,
            "secondHostDirectRuntimeCausalityProofRequired": False,
        },
        "sourceBoundRuntimeCausalityReceipt": {
            "receiptMode": RECEIPT_MODE,
            "fixtureOrPosthocBinding": True,
            "selfTestFixtureArtifact": True,
            "sameRunArtifactChain": True,
            "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
            "schedulerReceipt": dict(receipt_row),
            "bridgeReceipt": dict(receipt_row),
            "runtimeInputWindowReceipt": dict(receipt_row),
            "exactPidCdbReceipt": dict(receipt_row),
            "mappedP2SequenceReceipt": dict(receipt_row),
            "hostHelperDeliveryReceipt": dict(receipt_row),
        },
        "runtimeEvidence": {
            "exactPidCdbRuntimeInputEvidence": True,
            "hostHelperInputSent": True,
            "hostHelperInputBoundToSecondHostCommandSource": True,
            "hostHelperBoundRemoteSlot": EXPECTED_HOST_HELPER_REMOTE_SLOT,
            "hostHelperBoundAcceptedSecondHostCommandId": EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
            "hostHelperBoundHostAuthorityCommandId": EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
            "hostHelperMappedInputSequence": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE,
            "hostHelperMappedInputSequenceSha256": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
            "hostHelperRuntimeRoute": EXPECTED_HOST_HELPER_RUNTIME_ROUTE,
            "hostHelperInputDevice": EXPECTED_HOST_HELPER_INPUT_DEVICE,
            "gameInputSentBySecondHostClient": False,
            "gameInputSentByHostAuthorityScheduler": False,
            "newBeaLaunchCount": 1,
            "cdbAttachCount": 1,
        },
        "nonClaims": {
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
    }


def make_current_compatibility_executor_fixture(root: Path) -> dict[str, Any]:
    case = executor_test.SecondHostRuntimeExecutorTests()
    output_path = case.build_fixture(root)
    return read_json(output_path)


def run_self_test() -> None:
    future_candidate = make_future_candidate_fixture()
    try:
        validate_promotion_candidate(future_candidate)
    except SecondHostRuntimePromotionGuardError:
        pass
    else:
        raise AssertionError("synthetic future candidate fixture must not satisfy default promotion guard")
    validate_promotion_candidate(future_candidate, allow_synthetic_fixture=True)

    with tempfile.TemporaryDirectory(dir=executor_builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        try:
            validate_promotion_candidate(make_current_compatibility_executor_fixture(Path(raw_tmp)))
        except SecondHostRuntimePromotionGuardError:
            pass
        else:
            raise AssertionError("current compatibility executor must not satisfy promotion guard")

    for label, mutator in (
        ("fixture-marker", lambda p: p["sourceBoundRuntimeCausalityReceipt"].__setitem__("fixtureOrPosthocBinding", False)),
        ("flag", lambda p: p["secondHostRuntimeExecutor"].__setitem__("runtimeDrivenBySecondHostCommandSource", False)),
        (
            "runtime-window-hash",
            lambda p: p["sourceBoundRuntimeCausalityReceipt"]["runtimeInputWindowReceipt"].__setitem__(
                "acceptedSecondHostCommandRequestPayloadSha256", "b" * 64
            ),
        ),
        (
            "invitation-lifecycle-hash",
            lambda p: p["sourceBoundRuntimeCausalityReceipt"]["bridgeReceipt"].__setitem__(
                "secondHostInvitationLifecycleSha256", "c" * 64
            ),
        ),
        ("cdb", lambda p: p["sourceBoundRuntimeCausalityReceipt"]["exactPidCdbReceipt"].__setitem__("present", False)),
    ):
        payload = make_future_candidate_fixture()
        mutator(payload)
        try:
            validate_promotion_candidate(payload, allow_synthetic_fixture=True)
        except SecondHostRuntimePromotionGuardError:
            pass
        else:
            raise AssertionError(f"mutated promotion fixture should fail: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime promotion guard self-test: PASS")
        return 0
    require(args.candidate is not None, "candidate path is required unless --self-test is used")
    print(json.dumps(validate_promotion_candidate(read_json(args.candidate)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SecondHostRuntimePromotionGuardError, json.JSONDecodeError) as exc:
        print(f"WinUI original-binary second-host runtime promotion guard: FAIL: {exc}")
        raise SystemExit(2)
