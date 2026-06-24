#!/usr/bin/env python3
"""Validate source-bound second-host-to-runtime causality proof candidates.

This is stricter than the promotion guard's shape check. A candidate must carry
the accepted second-host command payload and invitation lifecycle hash through
raw-artifact receipts for scheduler, bridge, runtime input-window, exact-PID
CDB, mapped P2 sequence, and host-helper delivery evidence in one same-run
chain.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_second_host_runtime_promotion_guard as promotion_guard


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "roadmap" / "original-binary-online-second-host-runtime-causality.v1.json"
PRIVATE_ARTIFACT_ROOT_NAME = "sub" + "agents"
PRIVATE_PROOF_ROOT = ROOT / PRIVATE_ARTIFACT_ROOT_NAME / "winui-safe-copy-live-runtime"
SCHEMA = "winui-original-binary-second-host-runtime-causality.v1"
PROMOTION_SCOPE = promotion_guard.PROMOTION_SCOPE
RECEIPT_MODE = promotion_guard.RECEIPT_MODE
HELPER = "winui-original-binary-second-host-runtime-causality-check"
HELPER_VERSION = "second-host-runtime-causality-check.v1"
PACKAGE_SCRIPT = "test:winui-original-binary-second-host-runtime-causality"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
FIXTURE_RUN_PREFIX = "second-host-runtime-causality-fixture-"
ARTIFACT_REFERENCE_MODE = "candidate-bundle-relative-private-root-contained-files"
RAW_ARTIFACT_RECEIPT_SCHEMA = "winui-original-binary-second-host-runtime-causality-artifact-receipt.v1"
RAW_ARTIFACT_EVIDENCE_SCHEMA = "winui-original-binary-second-host-runtime-causality-raw-evidence.v1"
RAW_ARTIFACT_BODY_SCHEMA = "winui-original-binary-second-host-runtime-causality-raw-evidence-body.v1"
RAW_EVIDENCE_REFERENCE_MODE = "candidate-bundle-relative-private-root-contained-raw-material"
EXPECTED_HOST_HELPER_REMOTE_SLOT = "P2"
EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID = "second-host-p2-forward-0001"
EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID = "host-authority-p2-forward-0001"
EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE = "down:E,wait:500,up:E"
EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256 = hashlib.sha256(
    EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE.encode("utf-8")
).hexdigest()
EXPECTED_HOST_HELPER_RUNTIME_ROUTE = "P2/inputDevice1/bottom-split-half"
EXPECTED_HOST_HELPER_INPUT_DEVICE = 1
CHAIN_HASH_KEYS = (
    "commandSourceProofSha256",
    "schedulerProofSha256",
    "bridgeProofSha256",
    "runtimeInputWindowArtifactSha256",
    "exactPidCdbLogSha256",
    "copiedRuntimeArtifactSha256",
    "copiedRuntimeExeSha256",
    "processIdentitySha256",
)
RAW_ARTIFACT_RECEIPTS = (
    "second-host-command-source-proof",
    "scheduler-proof",
    "bridge-proof",
    "runtime-input-window-artifact",
    "exact-pid-cdb-log",
    "copied-runtime-artifact",
    "copied-runtime-exe-hash",
    "process-identity-proof",
)
RAW_ARTIFACT_ROLE_BY_HASH_KEY = {
    "commandSourceProofSha256": "second-host-command-source-proof",
    "schedulerProofSha256": "scheduler-proof",
    "bridgeProofSha256": "bridge-proof",
    "runtimeInputWindowArtifactSha256": "runtime-input-window-artifact",
    "exactPidCdbLogSha256": "exact-pid-cdb-log",
    "copiedRuntimeArtifactSha256": "copied-runtime-artifact",
    "copiedRuntimeExeSha256": "copied-runtime-exe-hash",
    "processIdentitySha256": "process-identity-proof",
}
RAW_ARTIFACT_RECEIPT_KEYS = {
    "schemaVersion",
    "artifactRole",
    "hashKey",
    "runId",
    "sourceBound",
    "sameRunArtifact",
    "fixtureOrPosthocBinding",
    "acceptedSecondHostCommandRequestPayloadSha256",
    "secondHostInvitationLifecycleSha256",
    "selfTestOnly",
}
RAW_ARTIFACT_ROLE_PROOF_FLAG = {
    "commandSourceProofSha256": "acceptedLiveSecondHostCommandSourceProof",
    "schedulerProofSha256": "secondHostPayloadScheduled",
    "bridgeProofSha256": "secondHostPayloadBridgedToRuntimeInput",
    "runtimeInputWindowArtifactSha256": "runtimeInputWindowArtifact",
    "exactPidCdbLogSha256": "exactPidCdbRuntimeInputEvidence",
    "copiedRuntimeArtifactSha256": "copiedRuntimeArtifact",
    "copiedRuntimeExeSha256": "copiedRuntimeExeHashEvidence",
    "processIdentitySha256": "processIdentityEvidence",
}
RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY = {
    "commandSourceProofSha256": "accepted-second-host-command-source-transcript",
    "schedulerProofSha256": "host-authority-scheduler-relay-plan",
    "bridgeProofSha256": "host-helper-runtime-bridge-map",
    "runtimeInputWindowArtifactSha256": "copied-runtime-input-window-rows",
    "exactPidCdbLogSha256": "exact-pid-cdb-log-lines",
    "copiedRuntimeArtifactSha256": "copied-runtime-delivery-artifact-rows",
    "copiedRuntimeExeSha256": "copied-runtime-executable-bytes",
    "processIdentitySha256": "process-identity-observation",
}
FORBIDDEN_TRUTHY_OVERCLAIM_FLAGS = {
    "hostJoinControlsMayBeEnabled",
    "baseOnlineMultiplayerReady",
    "multiHostLanPlayProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "moreThanTwoOriginalBinaryRuntimePlayersProof",
    "coOpVersusRuntimeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
    "gameInputSentBySecondHostClient",
    "gameInputSentByHostAuthorityScheduler",
}
ALLOWED_TRUTHY_CLAIM_FLAGS = {
    "acceptedLiveSecondHostRuntimeDeliveryProof",
    "acceptedLiveSecondHostCommandSourceProof",
    "privateProofReleaseExcludedByPolicy",
}
RAW_BODY_BASE_KEYS = {
    "schemaVersion",
    "artifactRole",
    "hashKey",
    "runId",
    "evidenceMode",
    "sourceBound",
    "sameRunArtifact",
    "fixtureOrPosthocBinding",
    "acceptedSecondHostCommandRequestPayloadSha256",
    "secondHostInvitationLifecycleSha256",
    "selfTestOnly",
    "rawEvidenceSha256",
    "rawEvidenceReferenceMode",
    "rawEvidenceRelativePath",
    "rawEvidenceMaterialKind",
    "rawEvidenceMaterialUnitCount",
}
HOST_HELPER_RAW_BODY_KEYS = {
    "hostHelperInputBoundToSecondHostCommandSource",
    "hostHelperBoundRemoteSlot",
    "hostHelperBoundAcceptedSecondHostCommandId",
    "hostHelperBoundHostAuthorityCommandId",
    "hostHelperMappedInputSequence",
    "hostHelperMappedInputSequenceSha256",
    "hostHelperRuntimeRoute",
    "hostHelperInputDevice",
    "hostHelperInputSent",
    "p2Button31ReceiveRows",
    "p2ForwardStateStoreRows",
    "gameInputSentBySecondHostClient",
}
RAW_BODY_ROLE_KEYS = {
    "commandSourceProofSha256": {
        "acceptedLiveSecondHostCommandSourceProof",
        "transportTranscriptEventCount",
        "sessionSecurityHardeningEvidenceMode",
    },
    "schedulerProofSha256": {"secondHostPayloadScheduled", "relayPlanSha256"},
    "bridgeProofSha256": {"secondHostPayloadBridgedToRuntimeInput", "runtimeCompatibleRelayHash"},
    "runtimeInputWindowArtifactSha256": {
        "runtimeInputDerivedFromSecondHostCommandSource",
        "runtimeInputWindowEventCount",
        "observedProcessIdentitySha256",
        *HOST_HELPER_RAW_BODY_KEYS,
    },
    "exactPidCdbLogSha256": {
        "exactPidCdbRuntimeInputEvidence",
        "pidObservedInCdbLog",
        "beaExeObservedInCdbLog",
        "cdbLogLineCount",
        "observedProcessIdentitySha256",
        *HOST_HELPER_RAW_BODY_KEYS,
    },
    "copiedRuntimeArtifactSha256": {"copiedRuntimeArtifactRowCount", "copiedRuntimeArtifactSha256"},
    "copiedRuntimeExeSha256": {"computedFromCopiedExeBytes", "copiedRuntimeExeSha256"},
    "processIdentitySha256": {"observedPid", "observedImageName", "observedProcessIdentitySha256"},
}
LIVE_PROMOTION_REQUIREMENT_KEYS = {
    "requiresRawArtifactReceiptsRecomputed",
    "requiresPrivateRuntimeProofRoot",
    "requiresSemanticRawArtifactReceipts",
    "requiresRoleSpecificRawEvidenceBodies",
    "requiresConcreteRawEvidenceBodyFields",
    "requiresRoleSpecificRawEvidenceMaterialDescriptors",
    "requiresRawEvidenceSha256RecomputedFromFiles",
    "requiresCandidateBundleRelativePrivateRootContainedArtifacts",
    "rejectsReceiptOnlyCandidates",
    "rejectsJsonOnlyForgedArtifacts",
    "rejectsSelfTestOnlyRawArtifacts",
    "scansCandidateAndRawArtifactsForPrivatePaths",
    "requiresSameRunArtifactChain",
    "requiresRunIdBoundAcrossReceipts",
    "requiresAcceptedCommandPayloadHashBoundEndToEnd",
    "requiresInvitationLifecycleHashBoundEndToEnd",
    "requiresLocalSourceSafetyPreflightForLiveRuntime",
    "requiresExactPidCdbRuntimeInputEvidence",
    "requiresRuntimeInputDerivedFromSecondHostCommandSource",
    "requiresRuntimeDrivenBySecondHostCommandSource",
    "requiresHostHelperInputBoundToSecondHostCommandSource",
    "requiresMappedP2SequenceReceipt",
    "rejectsSecondHostClientDirectGameInputBypass",
    "rejectsHostAuthorityDerivedRuntimeInput",
    "keepsHostJoinDisabledUntilCompositeGate",
}
CURRENT_EVIDENCE_KEYS = {
    "acceptedLiveSecondHostRuntimeCausalityProof",
    "acceptedLiveSecondHostRuntimeDeliveryProof",
    "runtimeInputDerivedFromSecondHostCommandSource",
    "runtimeDrivenBySecondHostCommandSource",
    "hostJoinControlsMayBeEnabled",
    "baseOnlineMultiplayerReady",
}
NONCLAIM_KEYS = {
    "multiHostLanPlayProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "moreThanTwoOriginalBinaryRuntimePlayersProof",
    "coOpVersusRuntimeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
}
RELEASE_BOUNDARY_KEYS = {
    "privateProofReleaseExcludedByPolicy",
    "privateArtifactContentPublished",
    "rawPrivateProofPathPublished",
    "publicHostOrMatchmakingEndpointPublished",
    "releaseIncludedPrivateArtifact",
}
APPROVED_SOURCE_HASH_MODE = "computed-tree-sha256"


class SecondHostRuntimeCausalityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimeCausalityError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def require_exact_keys(row: dict[str, Any], expected: set[str] | tuple[str, ...], label: str) -> None:
    expected_set = set(expected)
    actual = set(row)
    missing = sorted(expected_set - actual)
    unexpected = sorted(actual - expected_set)
    require(not missing and not unexpected, f"{label} keys mismatch; missing={missing}; unexpected={unexpected}")


def require_hash(value: Any, label: str) -> str:
    text = str(value or "")
    require(bool(HEX64_RE.fullmatch(text)), f"{label} must be a 64-char lowercase sha256")
    return text


def require_positive_int(value: Any, label: str) -> int:
    require(isinstance(value, int) and value > 0, f"{label} must be a positive integer")
    return int(value)


def require_false(row: dict[str, Any], key: str, label: str) -> None:
    require(row.get(key) is False, f"{label} must remain false: {key}")


def require_host_helper_input_boundary(row: dict[str, Any], label: str) -> None:
    require(
        row.get("hostHelperInputBoundToSecondHostCommandSource") is True,
        f"{label} must bind host-helper input to the accepted second-host command source",
    )
    require(row.get("hostHelperBoundRemoteSlot") == EXPECTED_HOST_HELPER_REMOTE_SLOT, f"{label} host-helper remote slot mismatch")
    require(
        row.get("hostHelperBoundAcceptedSecondHostCommandId") == EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
        f"{label} accepted second-host command id mismatch",
    )
    require(
        row.get("hostHelperBoundHostAuthorityCommandId") == EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
        f"{label} host-authority command id mismatch",
    )
    require(row.get("hostHelperMappedInputSequence") == EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE, f"{label} mapped P2 sequence mismatch")
    require(
        row.get("hostHelperMappedInputSequenceSha256") == EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
        f"{label} mapped P2 sequence hash mismatch",
    )
    require(row.get("hostHelperRuntimeRoute") == EXPECTED_HOST_HELPER_RUNTIME_ROUTE, f"{label} runtime route mismatch")
    require(row.get("hostHelperInputDevice") == EXPECTED_HOST_HELPER_INPUT_DEVICE, f"{label} input device mismatch")
    require(row.get("hostHelperInputSent") is True, f"{label} host-helper input flag missing")
    require(int(row.get("p2Button31ReceiveRows") or 0) > 0, f"{label} P2 button31 receive rows missing")
    require(int(row.get("p2ForwardStateStoreRows") or 0) > 0, f"{label} P2 forward state-store rows missing")
    require(
        row.get("gameInputSentBySecondHostClient") is False,
        f"{label} must reject second-host client direct game input",
    )


def require_no_sensitive_text(text: str, label: str) -> None:
    lowered = text.lower()
    forbidden_fragments = (
        "c:\\",
        "c:/",
        "users\\",
        "users/",
        "program files",
        "\\\\",
        "/mnt/",
        "/home/",
        "file://",
        "bearer ",
        "password=",
        "token=",
        "secret=",
        "sk-",
    )
    require(not any(fragment in lowered for fragment in forbidden_fragments), f"sensitive path or secret-like string is not allowed at {label}")
    require(re.search(r"(?i)\b[a-z]:[\\/]", text) is None, f"drive-letter path is not allowed at {label}")


def require_no_sensitive_string_values(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require_no_sensitive_text(str(key), f"{path}.<key>")
            require_no_sensitive_string_values(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_sensitive_string_values(child, f"{path}[{index}]")
    elif isinstance(value, str):
        require_no_sensitive_text(value, path)


def is_truthy_claim_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value is True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered in {"1", "true", "yes", "y", "enabled", "ready", "proof", "proven", "implemented", "on"}
    return False


def require_no_hidden_truthy_overclaim_flags(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            looks_like_claim = lowered.endswith(("proof", "ready", "enabled", "claim", "implemented")) or "proof" in lowered
            if key in FORBIDDEN_TRUTHY_OVERCLAIM_FLAGS and child is not False:
                raise SecondHostRuntimeCausalityError(f"overclaim field must remain false at {path}.{key}")
            if (
                looks_like_claim
                and key not in ALLOWED_TRUTHY_CLAIM_FLAGS
                and not key.startswith("requires")
                and is_truthy_claim_value(child)
            ):
                raise SecondHostRuntimeCausalityError(f"truthy overclaim-like field is not allowed at {path}.{key}")
            require_no_hidden_truthy_overclaim_flags(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_hidden_truthy_overclaim_flags(child, f"{path}[{index}]")


def require_local_source_safety(source_safety: dict[str, Any]) -> None:
    require_exact_keys(source_safety, {"evidenceMode", "computedByPreflight", "pathValuesPublished", "absolutePathsSerialized", "host", "client"}, "sourceSafety")
    require(source_safety.get("evidenceMode") == "local-preflight-computed", "source safety must be local-preflight-computed")
    require(source_safety.get("computedByPreflight") is True, "source safety must be computed by preflight")
    require(source_safety.get("pathValuesPublished") is False, "source safety must not publish raw paths")
    require(source_safety.get("absolutePathsSerialized") is False, "source safety must not serialize absolute paths")
    for role in ("host", "client"):
        side = object_at(source_safety, role)
        require_exact_keys(
            side,
            {
                "sourceEvidenceMode",
                "computedByPreflight",
                "pathValuesPublished",
                "absolutePathsSerialized",
                "copiedProfileHashMode",
                "copiedProfileFileCount",
                "installedGameHashMode",
                "installedGameFileCount",
                "programFilesMutationAttempted",
            },
            f"sourceSafety.{role}",
        )
        require(side.get("sourceEvidenceMode") == "local-preflight-computed", f"{role} source evidence must be local-preflight-computed")
        require(side.get("computedByPreflight") is True, f"{role} source evidence must be computed")
        require(side.get("pathValuesPublished") is False, f"{role} source evidence must not publish paths")
        require(side.get("absolutePathsSerialized") is False, f"{role} source evidence must not serialize absolute paths")
        require(int(side.get("copiedProfileFileCount") or 0) > 0, f"{role} copied-profile file count must be positive")
        require(int(side.get("installedGameFileCount") or 0) > 0, f"{role} installed-game file count must be positive")
        require(side.get("copiedProfileHashMode") == APPROVED_SOURCE_HASH_MODE, f"{role} copied-profile hash mode must be {APPROVED_SOURCE_HASH_MODE}")
        require(side.get("installedGameHashMode") == APPROVED_SOURCE_HASH_MODE, f"{role} installed-game hash mode must be {APPROVED_SOURCE_HASH_MODE}")
        require(side.get("programFilesMutationAttempted") is False, f"{role} Program Files mutation must be false")


def as_promotion_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = {
        "schemaVersion": promotion_guard.SCHEMA,
        "promotionScope": payload.get("promotionScope"),
        "sourceBinding": copy.deepcopy(object_at(payload, "sourceBinding")),
        "secondHostRuntimeExecutor": copy.deepcopy(object_at(payload, "secondHostRuntimeExecutor")),
        "sourceBoundRuntimeCausalityReceipt": copy.deepcopy(object_at(payload, "sourceBoundRuntimeCausalityReceipt")),
        "runtimeEvidence": copy.deepcopy(object_at(payload, "runtimeEvidence")),
        "nonClaims": copy.deepcopy(object_at(payload, "nonClaims")),
    }
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_private_relative_path(root: Path, relative_text: Any, label: str) -> Path:
    text = str(relative_text or "")
    require(text, f"{label} relative path missing")
    require(":" not in text, f"{label} must not contain a drive or URI separator")
    relative = Path(text)
    require(not relative.is_absolute(), f"{label} must be private-root-relative")
    require(".." not in relative.parts, f"{label} must not traverse upward")
    root_resolved = root.resolve()
    target = (root_resolved / relative).resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise SecondHostRuntimeCausalityError(f"{label} escapes private artifact root") from exc
    require(target.is_file(), f"{label} file missing")
    return target


def require_under_private_proof_root(path: Path, label: str) -> None:
    root = PRIVATE_PROOF_ROOT.resolve()
    target = path.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise SecondHostRuntimeCausalityError(f"{label} must stay under private runtime proof root") from exc


def validate_artifact_semantic_receipt(
    path: Path,
    hash_key: str,
    *,
    artifact_root: Path,
    run_id: str,
    accepted_payload_hash: str,
    invitation_hash: str,
    allow_fixture: bool = False,
) -> None:
    artifact = read_json(path)
    require_no_sensitive_string_values(artifact, f"{hash_key} artifact")
    require_no_hidden_truthy_overclaim_flags(artifact, f"{hash_key} artifact")
    expected_self_test = bool(allow_fixture)
    expected_evidence_mode = "self-test-file-backed-artifact" if expected_self_test else "live-runtime-artifact"
    receipt = object_at(artifact, "secondHostRuntimeCausalityArtifact")
    require_exact_keys(receipt, RAW_ARTIFACT_RECEIPT_KEYS, f"{hash_key} semantic receipt")
    require(receipt.get("schemaVersion") == RAW_ARTIFACT_RECEIPT_SCHEMA, f"{hash_key} semantic receipt schema mismatch")
    require(receipt.get("artifactRole") == RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key], f"{hash_key} artifact role mismatch")
    require(receipt.get("hashKey") == hash_key, f"{hash_key} semantic hash key mismatch")
    require(receipt.get("runId") == run_id, f"{hash_key} semantic run id mismatch")
    require(receipt.get("sourceBound") is True, f"{hash_key} semantic receipt must be source-bound")
    require(receipt.get("sameRunArtifact") is True, f"{hash_key} semantic receipt must be same-run")
    require(receipt.get("fixtureOrPosthocBinding") is False, f"{hash_key} semantic receipt must not be fixture/posthoc")
    require(receipt.get("selfTestOnly") is expected_self_test, f"{hash_key} semantic receipt self-test flag mismatch")
    require(
        receipt.get("acceptedSecondHostCommandRequestPayloadSha256") == accepted_payload_hash,
        f"{hash_key} semantic payload hash mismatch",
    )
    require(receipt.get("secondHostInvitationLifecycleSha256") == invitation_hash, f"{hash_key} semantic invitation hash mismatch")
    evidence = object_at(artifact, "roleSpecificRawEvidence")
    require(evidence.get("schemaVersion") == RAW_ARTIFACT_EVIDENCE_SCHEMA, f"{hash_key} role evidence schema mismatch")
    require(evidence.get("artifactRole") == RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key], f"{hash_key} role evidence artifact role mismatch")
    require(evidence.get("hashKey") == hash_key, f"{hash_key} role evidence hash key mismatch")
    require(evidence.get("runId") == run_id, f"{hash_key} role evidence run id mismatch")
    require(evidence.get("evidenceMode") == expected_evidence_mode, f"{hash_key} role evidence mode mismatch")
    require(evidence.get("sourceBound") is True, f"{hash_key} role evidence must be source-bound")
    require(evidence.get("sameRunArtifact") is True, f"{hash_key} role evidence must be same-run")
    require(evidence.get("fixtureOrPosthocBinding") is False, f"{hash_key} role evidence must not be fixture/posthoc")
    require(evidence.get("selfTestOnly") is expected_self_test, f"{hash_key} role evidence self-test flag mismatch")
    require(
        evidence.get("acceptedSecondHostCommandRequestPayloadSha256") == accepted_payload_hash,
        f"{hash_key} role evidence payload hash mismatch",
    )
    require(evidence.get("secondHostInvitationLifecycleSha256") == invitation_hash, f"{hash_key} role evidence invitation hash mismatch")
    require(evidence.get(RAW_ARTIFACT_ROLE_PROOF_FLAG[hash_key]) is True, f"{hash_key} missing role-specific raw evidence flag")
    if hash_key in ("runtimeInputWindowArtifactSha256", "exactPidCdbLogSha256", "processIdentitySha256"):
        require_hash(evidence.get("observedProcessIdentitySha256"), f"{hash_key} role evidence observed process identity")
    if hash_key == "copiedRuntimeArtifactSha256":
        require_hash(evidence.get("copiedRuntimeArtifactSha256"), f"{hash_key} role evidence copied-runtime artifact hash")
    if hash_key == "copiedRuntimeExeSha256":
        require_hash(evidence.get("copiedRuntimeExeSha256"), f"{hash_key} role evidence copied-runtime exe hash")
    validate_role_specific_raw_evidence_body(
        evidence,
        hash_key,
        run_id=run_id,
        accepted_payload_hash=accepted_payload_hash,
        invitation_hash=invitation_hash,
        artifact_root=artifact_root,
        allow_fixture=allow_fixture,
    )


def validate_role_specific_raw_evidence_body(
    evidence: dict[str, Any],
    hash_key: str,
    *,
    run_id: str,
    accepted_payload_hash: str,
    invitation_hash: str,
    artifact_root: Path,
    allow_fixture: bool,
) -> None:
    body = object_at(evidence, "rawEvidenceBody")
    require_exact_keys(body, RAW_BODY_BASE_KEYS | RAW_BODY_ROLE_KEYS[hash_key], f"{hash_key} raw evidence body")
    expected_self_test = bool(allow_fixture)
    expected_evidence_mode = "self-test-file-backed-artifact" if expected_self_test else "live-runtime-artifact"
    require(body.get("schemaVersion") == RAW_ARTIFACT_BODY_SCHEMA, f"{hash_key} raw body schema mismatch")
    require(body.get("hashKey") == hash_key, f"{hash_key} raw body hash key mismatch")
    require(body.get("artifactRole") == RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key], f"{hash_key} raw body role mismatch")
    require(body.get("runId") == run_id, f"{hash_key} raw body run id mismatch")
    require(body.get("evidenceMode") == expected_evidence_mode, f"{hash_key} raw body evidence mode mismatch")
    require(body.get("sourceBound") is True, f"{hash_key} raw body must be source-bound")
    require(body.get("sameRunArtifact") is True, f"{hash_key} raw body must be same-run")
    require(body.get("fixtureOrPosthocBinding") is False, f"{hash_key} raw body must not be fixture/posthoc")
    require(body.get("selfTestOnly") is expected_self_test, f"{hash_key} raw body self-test flag mismatch")
    require(body.get("acceptedSecondHostCommandRequestPayloadSha256") == accepted_payload_hash, f"{hash_key} raw body payload hash mismatch")
    require(body.get("secondHostInvitationLifecycleSha256") == invitation_hash, f"{hash_key} raw body invitation hash mismatch")
    declared_raw_hash = require_hash(body.get("rawEvidenceSha256"), f"{hash_key} raw body raw evidence hash")
    require(body.get("rawEvidenceReferenceMode") == RAW_EVIDENCE_REFERENCE_MODE, f"{hash_key} raw body raw evidence reference mode mismatch")
    raw_evidence_path = resolve_private_relative_path(
        artifact_root,
        body.get("rawEvidenceRelativePath"),
        f"{hash_key} raw body raw evidence relative path",
    )
    require_under_private_proof_root(raw_evidence_path, f"{hash_key} raw body raw evidence relative path")
    require(sha256_file(raw_evidence_path) == declared_raw_hash, f"{hash_key} raw body raw evidence hash mismatch")
    require(
        body.get("rawEvidenceMaterialKind") == RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key],
        f"{hash_key} raw body material kind mismatch",
    )
    material_count = require_positive_int(body.get("rawEvidenceMaterialUnitCount"), f"{hash_key} raw body material unit count")

    if hash_key == "commandSourceProofSha256":
        require(body.get("acceptedLiveSecondHostCommandSourceProof") is True, "command-source raw body must prove accepted command-source proof")
        transcript_count = require_positive_int(body.get("transportTranscriptEventCount"), "command-source transport transcript event count")
        require(material_count == transcript_count, "command-source raw body material count must match transcript event count")
        expected_mode = "self-test-fixture" if allow_fixture else "live-server-client-transcript"
        require(body.get("sessionSecurityHardeningEvidenceMode") == expected_mode, "command-source hardening mode mismatch")
    elif hash_key == "schedulerProofSha256":
        require(body.get("secondHostPayloadScheduled") is True, "scheduler raw body must schedule the second-host payload")
        require(material_count == 1, "scheduler raw body material count must describe one relay plan")
        require_hash(body.get("relayPlanSha256"), "scheduler raw body relay plan hash")
    elif hash_key == "bridgeProofSha256":
        require(body.get("secondHostPayloadBridgedToRuntimeInput") is True, "bridge raw body must bridge the second-host payload")
        require(material_count == 1, "bridge raw body material count must describe one bridge map")
        require_hash(body.get("runtimeCompatibleRelayHash"), "bridge raw body runtime relay hash")
    elif hash_key == "runtimeInputWindowArtifactSha256":
        require(body.get("runtimeInputDerivedFromSecondHostCommandSource") is True, "runtime input-window body must derive from second-host command source")
        require_host_helper_input_boundary(body, "runtime input-window body")
        event_count = require_positive_int(body.get("runtimeInputWindowEventCount"), "runtime input-window event count")
        require(material_count == event_count, "runtime input-window material count must match event count")
        require_hash(body.get("observedProcessIdentitySha256"), "runtime input-window body process identity")
    elif hash_key == "exactPidCdbLogSha256":
        require(body.get("exactPidCdbRuntimeInputEvidence") is True, "CDB raw body must prove exact-PID runtime input")
        require_host_helper_input_boundary(body, "CDB raw body")
        require(body.get("pidObservedInCdbLog") is True, "CDB raw body must observe PID in CDB log")
        require(body.get("beaExeObservedInCdbLog") is True, "CDB raw body must observe BEA.exe in CDB log")
        log_count = require_positive_int(body.get("cdbLogLineCount"), "CDB raw body log line count")
        require(material_count == log_count, "CDB raw body material count must match log line count")
        require_hash(body.get("observedProcessIdentitySha256"), "CDB raw body process identity")
    elif hash_key == "copiedRuntimeArtifactSha256":
        row_count = require_positive_int(body.get("copiedRuntimeArtifactRowCount"), "copied-runtime artifact row count")
        require(material_count == row_count, "copied-runtime artifact material count must match row count")
        require_hash(body.get("copiedRuntimeArtifactSha256"), "copied-runtime artifact body hash")
    elif hash_key == "copiedRuntimeExeSha256":
        require(body.get("computedFromCopiedExeBytes") is True, "copied-runtime exe hash must be computed from copied exe bytes")
        require(material_count == 1, "copied-runtime exe material count must describe one executable")
        require_hash(body.get("copiedRuntimeExeSha256"), "copied-runtime exe body hash")
    elif hash_key == "processIdentitySha256":
        require(material_count == 1, "process identity material count must describe one process identity")
        require_positive_int(body.get("observedPid"), "process identity observed PID")
        require(body.get("observedImageName") == "BEA.exe", "process identity body must observe BEA.exe")
        require_hash(body.get("observedProcessIdentitySha256"), "process identity body hash")
    else:
        raise SecondHostRuntimeCausalityError(f"unknown raw artifact hash key: {hash_key}")


def validate_file_backed_artifacts(
    raw: dict[str, Any],
    chain_hashes: dict[str, str],
    candidate_path: Path | None,
    *,
    run_id: str,
    accepted_payload_hash: str,
    invitation_hash: str,
    allow_fixture: bool = False,
) -> None:
    require(candidate_path is not None, "live causality candidate path is required for file-backed artifact recomputation")
    require_under_private_proof_root(candidate_path, "live causality candidate")
    require(raw.get("artifactReferenceMode") == ARTIFACT_REFERENCE_MODE, "raw artifact references must be candidate-bundle-relative and private-root-contained files")
    require(raw.get("artifactReferencesRecomputedFromFiles") is True, "raw artifact references must be recomputed from files")
    require(raw.get("privateArtifactRootPublished") is False, "private artifact root must not be published")
    receipts = object_at(raw, "artifactReceipts")
    require_exact_keys(receipts, CHAIN_HASH_KEYS, "rawArtifactChain.artifactReceipts")
    root = candidate_path.parent
    for hash_key in CHAIN_HASH_KEYS:
        row = object_at(receipts, hash_key)
        require_exact_keys(row, {"relativePath", "sha256"}, f"artifactReceipts.{hash_key}")
        declared_hash = require_hash(row.get("sha256"), f"artifactReceipts.{hash_key}.sha256")
        require(declared_hash == chain_hashes[hash_key], f"artifact receipt hash mismatch: {hash_key}")
        path = resolve_private_relative_path(root, row.get("relativePath"), f"artifactReceipts.{hash_key}.relativePath")
        require_under_private_proof_root(path, f"artifactReceipts.{hash_key}.relativePath")
        computed_hash = sha256_file(path)
        require(computed_hash == chain_hashes[hash_key], f"artifact file hash mismatch: {hash_key}")
        validate_artifact_semantic_receipt(
            path,
            hash_key,
            artifact_root=root,
            run_id=run_id,
            accepted_payload_hash=accepted_payload_hash,
            invitation_hash=invitation_hash,
            allow_fixture=allow_fixture,
        )


def replace_scalar_values(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: replace_scalar_values(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_scalar_values(item, replacements) for item in value]
    if isinstance(value, str) and value in replacements:
        return replacements[value]
    return value


def validate_receipts(
    payload: dict[str, Any],
    accepted_payload_hash: str,
    invitation_hash: str,
    run_id: str,
    *,
    candidate_path: Path | None = None,
    allow_fixture: bool = False,
) -> dict[str, str]:
    raw = object_at(payload, "rawArtifactChain")
    require(raw.get("rawArtifactReceiptsRecomputed") is True, "raw artifact receipts must be recomputed")
    require(raw.get("receiptOnlyCandidate") is False, "receipt-only candidates are not accepted")
    require(raw.get("fixtureOrPosthocBinding") is False, "fixture/posthoc raw binding must be false")
    require(raw.get("runId") == run_id, "raw artifact chain run id mismatch")

    chain_hashes = {key: require_hash(raw.get(key), f"rawArtifactChain.{key}") for key in CHAIN_HASH_KEYS}
    if not allow_fixture or candidate_path is not None:
        validate_file_backed_artifacts(
            raw,
            chain_hashes,
            candidate_path,
            run_id=run_id,
            accepted_payload_hash=accepted_payload_hash,
            invitation_hash=invitation_hash,
            allow_fixture=allow_fixture,
        )

    receipt = object_at(payload, "sourceBoundRuntimeCausalityReceipt")
    require(receipt.get("runId") == run_id, "causality receipt run id mismatch")

    mapping = {
        "schedulerReceipt": ("schedulerProofSha256", "scheduler"),
        "bridgeReceipt": ("bridgeProofSha256", "bridge"),
        "runtimeInputWindowReceipt": ("runtimeInputWindowArtifactSha256", "runtime input-window"),
        "exactPidCdbReceipt": ("exactPidCdbLogSha256", "exact-PID CDB"),
        "mappedP2SequenceReceipt": ("runtimeInputWindowArtifactSha256", "mapped P2 sequence"),
        "hostHelperDeliveryReceipt": ("exactPidCdbLogSha256", "host-helper delivery"),
    }
    for receipt_key, (hash_key, label) in mapping.items():
        row = object_at(receipt, receipt_key)
        require(row.get("runId") == run_id, f"{label} receipt run id mismatch")
        require(row.get("artifactSha256") == chain_hashes[hash_key], f"{label} artifact hash mismatch")
        require(row.get("acceptedSecondHostCommandRequestPayloadSha256") == accepted_payload_hash, f"{label} payload hash mismatch")
        require(row.get("secondHostInvitationLifecycleSha256") == invitation_hash, f"{label} invitation lifecycle hash mismatch")

    runtime_row = object_at(raw, "runtimeInputWindow")
    cdb_row = object_at(raw, "exactPidCdb")
    for row, label in ((runtime_row, "runtime input-window"), (cdb_row, "exact-PID CDB")):
        require(row.get("runId") == run_id, f"{label} raw row run id mismatch")
        require(row.get("acceptedSecondHostCommandRequestPayloadSha256") == accepted_payload_hash, f"{label} raw payload hash mismatch")
        require(row.get("secondHostInvitationLifecycleSha256") == invitation_hash, f"{label} raw invitation lifecycle hash mismatch")
        require(row.get("sourceBound") is True, f"{label} raw row must be source-bound")
        require(row.get("sameRunArtifact") is True, f"{label} raw row must be same-run")
        require(row.get("fixtureOrPosthocBinding") is False, f"{label} raw row must not be fixture/posthoc")
        require_host_helper_input_boundary(row, f"{label} raw row")
    require(
        runtime_row.get("observedProcessIdentitySha256") == chain_hashes["processIdentitySha256"],
        "runtime input-window process identity mismatch",
    )
    require(cdb_row.get("observedProcessIdentitySha256") == chain_hashes["processIdentitySha256"], "exact-PID CDB process identity mismatch")
    require(cdb_row.get("exactPidCdbRuntimeInputEvidence") is True, "exact-PID CDB raw row must prove runtime input evidence")
    return chain_hashes


def validate_causality_candidate(payload: dict[str, Any], *, candidate_path: Path | None = None, allow_fixture: bool = False) -> dict[str, Any]:
    require_no_sensitive_string_values(payload)
    require_no_hidden_truthy_overclaim_flags(payload)
    require_exact_keys(
        payload,
        {
            "schemaVersion",
            "generatedBy",
            "helperVersion",
            "promotionScope",
            "runId",
            "sourceBinding",
            "sourceSafety",
            "secondHostRuntimeExecutor",
            "sourceBoundRuntimeCausalityReceipt",
            "rawArtifactChain",
            "runtimeEvidence",
            "nonClaims",
            "releaseBoundary",
        },
        "causality candidate",
    )
    require(payload.get("schemaVersion") == SCHEMA, "schema mismatch")
    require(payload.get("generatedBy") == HELPER, "helper mismatch")
    require(payload.get("helperVersion") == HELPER_VERSION, "helper version mismatch")
    require(payload.get("promotionScope") == PROMOTION_SCOPE, "promotion scope mismatch")
    run_id = str(payload.get("runId") or "")
    require(run_id.startswith("second-host-runtime-causality-"), "run id missing expected prefix")
    is_fixture = run_id.startswith(FIXTURE_RUN_PREFIX)
    require(allow_fixture or not is_fixture, "self-test fixture candidates require explicit allow_fixture")

    source_binding = object_at(payload, "sourceBinding")
    accepted_payload_hash = require_hash(
        source_binding.get("acceptedSecondHostCommandRequestPayloadSha256"),
        "sourceBinding.acceptedSecondHostCommandRequestPayloadSha256",
    )
    invitation_hash = require_hash(source_binding.get("secondHostInvitationLifecycleSha256"), "sourceBinding.secondHostInvitationLifecycleSha256")
    require(source_binding.get("runId") == run_id, "source binding run id mismatch")

    require_local_source_safety(object_at(payload, "sourceSafety"))
    chain_hashes = validate_receipts(
        payload,
        accepted_payload_hash,
        invitation_hash,
        run_id,
        candidate_path=candidate_path,
        allow_fixture=allow_fixture,
    )

    try:
        promotion_summary = promotion_guard.validate_promotion_candidate(as_promotion_candidate(payload))
    except promotion_guard.SecondHostRuntimePromotionGuardError as exc:
        raise SecondHostRuntimeCausalityError(str(exc)) from exc

    runtime = object_at(payload, "runtimeEvidence")
    require(runtime.get("runId") == run_id, "runtime evidence run id mismatch")
    require(runtime.get("runtimeInputWindowArtifactSha256") == chain_hashes["runtimeInputWindowArtifactSha256"], "runtime input artifact hash mismatch")
    require(runtime.get("exactPidCdbLogSha256") == chain_hashes["exactPidCdbLogSha256"], "runtime CDB log hash mismatch")
    require(runtime.get("copiedRuntimeArtifactSha256") == chain_hashes["copiedRuntimeArtifactSha256"], "copied runtime artifact hash mismatch")
    require(runtime.get("copiedRuntimeExeSha256") == chain_hashes["copiedRuntimeExeSha256"], "copied runtime exe hash mismatch")

    nonclaims = object_at(payload, "nonClaims")
    for key in (
        "hostJoinControlsMayBeEnabled",
        "baseOnlineMultiplayerReady",
        "multiHostLanPlayProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "moreThanTwoOriginalBinaryRuntimePlayersProof",
        "coOpVersusRuntimeProof",
        "deterministicSyncProof",
        "rollbackProof",
        "antiCheatProof",
        "rebuildParityProof",
        "noNoticeableDifferenceProof",
    ):
        require_false(nonclaims, key, "non-claim")

    release = object_at(payload, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key in ("privateArtifactContentPublished", "rawPrivateProofPathPublished", "publicHostOrMatchmakingEndpointPublished", "releaseIncludedPrivateArtifact"):
        require_false(release, key, "release boundary")

    return {
        "schemaVersion": payload["schemaVersion"],
        "promotionScope": payload["promotionScope"],
        "runId": run_id,
        "acceptedSecondHostCommandRequestPayloadSha256": accepted_payload_hash,
        "secondHostInvitationLifecycleSha256": invitation_hash,
        "selfTestFixtureCandidate": is_fixture,
        "shapePreflightAccepted": promotion_summary["shapePreflightAccepted"],
        "runtimeInputDerivedFromSecondHostCommandSource": False if is_fixture else True,
        "runtimeDrivenBySecondHostCommandSource": False if is_fixture else True,
        "acceptedLiveSecondHostRuntimeDeliveryProof": False if is_fixture else True,
        "rawArtifactReceiptsRecomputed": False if is_fixture else True,
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
    }


def make_future_raw_artifact_fixture() -> dict[str, Any]:
    run_id = "second-host-runtime-causality-fixture-run-0001"
    payload_hash = "a" * 64
    invitation_hash = "b" * 64
    hashes = {
        "commandSourceProofSha256": "c" * 64,
        "schedulerProofSha256": "d" * 64,
        "bridgeProofSha256": "e" * 64,
        "runtimeInputWindowArtifactSha256": "f" * 64,
        "exactPidCdbLogSha256": "1" * 64,
        "copiedRuntimeArtifactSha256": "2" * 64,
        "copiedRuntimeExeSha256": "3" * 64,
        "processIdentitySha256": "4" * 64,
    }

    def receipt_row(artifact_hash: str) -> dict[str, Any]:
        return {
            "present": True,
            "sourceBound": True,
            "sameRunArtifact": True,
            "runId": run_id,
            "artifactSha256": artifact_hash,
            "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
            "acceptedSecondHostCommandId": EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
            "acceptedSecondHostRemoteSlot": EXPECTED_HOST_HELPER_REMOTE_SLOT,
            "wouldForwardToPrivateLanCommandId": "private-lan-p2-forward-0001",
            "hostAuthorityAcceptedP2CommandId": EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
            "p2MappedInputSequence": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE,
            "p2MappedInputSequenceSha256": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
            "p2RuntimeRoute": EXPECTED_HOST_HELPER_RUNTIME_ROUTE,
            "inputDevice": EXPECTED_HOST_HELPER_INPUT_DEVICE,
            "hostHelperInputSent": True,
            "hostHelperInputBoundToSecondHostCommandSource": True,
            "gameInputSentBySecondHostClient": False,
        }

    raw_row = {
        "runId": run_id,
        "sourceBound": True,
        "sameRunArtifact": True,
        "fixtureOrPosthocBinding": False,
        "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
        "secondHostInvitationLifecycleSha256": invitation_hash,
        "observedProcessIdentitySha256": hashes["processIdentitySha256"],
        "hostHelperInputBoundToSecondHostCommandSource": True,
        "hostHelperBoundRemoteSlot": EXPECTED_HOST_HELPER_REMOTE_SLOT,
        "hostHelperBoundAcceptedSecondHostCommandId": EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
        "hostHelperBoundHostAuthorityCommandId": EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
        "hostHelperMappedInputSequence": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE,
        "hostHelperMappedInputSequenceSha256": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
        "hostHelperRuntimeRoute": EXPECTED_HOST_HELPER_RUNTIME_ROUTE,
        "hostHelperInputDevice": EXPECTED_HOST_HELPER_INPUT_DEVICE,
        "hostHelperInputSent": True,
        "p2Button31ReceiveRows": 1,
        "p2ForwardStateStoreRows": 1,
        "gameInputSentBySecondHostClient": False,
    }
    return {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "promotionScope": PROMOTION_SCOPE,
        "runId": run_id,
        "sourceBinding": {
            "runId": run_id,
            "requiredBeforeAcceptedLiveRuntimeDelivery": True,
            "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
        },
        "sourceSafety": {
            "evidenceMode": "local-preflight-computed",
            "computedByPreflight": True,
            "pathValuesPublished": False,
            "absolutePathsSerialized": False,
            "host": {
                "sourceEvidenceMode": "local-preflight-computed",
                "computedByPreflight": True,
                "pathValuesPublished": False,
                "absolutePathsSerialized": False,
                "copiedProfileHashMode": "computed-tree-sha256",
                "copiedProfileFileCount": 12,
                "installedGameHashMode": "computed-tree-sha256",
                "installedGameFileCount": 12,
                "programFilesMutationAttempted": False,
            },
            "client": {
                "sourceEvidenceMode": "local-preflight-computed",
                "computedByPreflight": True,
                "pathValuesPublished": False,
                "absolutePathsSerialized": False,
                "copiedProfileHashMode": "computed-tree-sha256",
                "copiedProfileFileCount": 12,
                "installedGameHashMode": "computed-tree-sha256",
                "installedGameFileCount": 12,
                "programFilesMutationAttempted": False,
            },
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
            "fixtureOrPosthocBinding": False,
            "selfTestFixtureArtifact": False,
            "sameRunArtifactChain": True,
            "runId": run_id,
            "acceptedSecondHostCommandRequestPayloadSha256": payload_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
            "schedulerReceipt": receipt_row(hashes["schedulerProofSha256"]),
            "bridgeReceipt": receipt_row(hashes["bridgeProofSha256"]),
            "runtimeInputWindowReceipt": receipt_row(hashes["runtimeInputWindowArtifactSha256"]),
            "exactPidCdbReceipt": receipt_row(hashes["exactPidCdbLogSha256"]),
            "mappedP2SequenceReceipt": receipt_row(hashes["runtimeInputWindowArtifactSha256"]),
            "hostHelperDeliveryReceipt": receipt_row(hashes["exactPidCdbLogSha256"]),
        },
        "rawArtifactChain": {
            "rawArtifactReceiptsRecomputed": True,
            "receiptOnlyCandidate": False,
            "fixtureOrPosthocBinding": False,
            "runId": run_id,
            **hashes,
            "runtimeInputWindow": dict(raw_row),
            "exactPidCdb": {
                **raw_row,
                "exactPidCdbRuntimeInputEvidence": True,
            },
        },
        "runtimeEvidence": {
            "runId": run_id,
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
            "p2Button31ReceiveRows": 1,
            "p2ForwardStateStoreRows": 1,
            "gameInputSentBySecondHostClient": False,
            "gameInputSentByHostAuthorityScheduler": False,
            "newBeaLaunchCount": 1,
            "cdbAttachCount": 1,
            "runtimeInputWindowArtifactSha256": hashes["runtimeInputWindowArtifactSha256"],
            "exactPidCdbLogSha256": hashes["exactPidCdbLogSha256"],
            "copiedRuntimeArtifactSha256": hashes["copiedRuntimeArtifactSha256"],
            "copiedRuntimeExeSha256": hashes["copiedRuntimeExeSha256"],
        },
        "nonClaims": {
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "coOpVersusRuntimeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "privateArtifactContentPublished": False,
            "rawPrivateProofPathPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_file_backed_self_test_candidate(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = make_future_raw_artifact_fixture()
    old_run_id = str(payload["runId"])
    run_id = "second-host-runtime-causality-fixture-file-backed-selftest-0001"
    old_hashes = {key: str(payload["rawArtifactChain"][key]) for key in CHAIN_HASH_KEYS}
    artifact_hashes: dict[str, str] = {}
    artifact_receipts: dict[str, dict[str, str]] = {}

    def role_evidence(hash_key: str) -> dict[str, Any]:
        raw_relative_path = Path("raw-evidence") / f"{hash_key}.txt"
        raw_path = root / raw_relative_path
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(
            "\n".join(
                (
                    f"schema={RAW_ARTIFACT_BODY_SCHEMA}",
                    f"runId={run_id}",
                    f"hashKey={hash_key}",
                    f"artifactRole={RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key]}",
                    f"materialKind={RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key]}",
                    f"sourceHash={old_hashes[hash_key]}",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        raw_hash = sha256_file(raw_path)
        raw_body: dict[str, Any] = {
            "schemaVersion": RAW_ARTIFACT_BODY_SCHEMA,
            "artifactRole": RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key],
            "hashKey": hash_key,
            "runId": run_id,
            "evidenceMode": "self-test-file-backed-artifact",
            "sourceBound": True,
            "sameRunArtifact": True,
            "fixtureOrPosthocBinding": False,
            "acceptedSecondHostCommandRequestPayloadSha256": payload["sourceBinding"]["acceptedSecondHostCommandRequestPayloadSha256"],
            "secondHostInvitationLifecycleSha256": payload["sourceBinding"]["secondHostInvitationLifecycleSha256"],
            "selfTestOnly": True,
            "rawEvidenceSha256": raw_hash,
            "rawEvidenceReferenceMode": RAW_EVIDENCE_REFERENCE_MODE,
            "rawEvidenceRelativePath": raw_relative_path.as_posix(),
            "rawEvidenceMaterialKind": RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key],
            "rawEvidenceMaterialUnitCount": 1,
        }
        if hash_key == "commandSourceProofSha256":
            raw_body.update(
                {
                    "acceptedLiveSecondHostCommandSourceProof": True,
                    "transportTranscriptEventCount": 33,
                    "rawEvidenceMaterialUnitCount": 33,
                    "sessionSecurityHardeningEvidenceMode": "self-test-fixture",
                }
            )
        elif hash_key == "schedulerProofSha256":
            raw_body.update({"secondHostPayloadScheduled": True, "relayPlanSha256": "5" * 64})
        elif hash_key == "bridgeProofSha256":
            raw_body.update({"secondHostPayloadBridgedToRuntimeInput": True, "runtimeCompatibleRelayHash": "6" * 64})
        elif hash_key == "runtimeInputWindowArtifactSha256":
            raw_body.update(
                {
                    "runtimeInputDerivedFromSecondHostCommandSource": True,
                    "hostHelperInputBoundToSecondHostCommandSource": True,
                    "hostHelperBoundRemoteSlot": EXPECTED_HOST_HELPER_REMOTE_SLOT,
                    "hostHelperBoundAcceptedSecondHostCommandId": EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
                    "hostHelperBoundHostAuthorityCommandId": EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
                    "hostHelperMappedInputSequence": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE,
                    "hostHelperMappedInputSequenceSha256": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
                    "hostHelperRuntimeRoute": EXPECTED_HOST_HELPER_RUNTIME_ROUTE,
                    "hostHelperInputDevice": EXPECTED_HOST_HELPER_INPUT_DEVICE,
                    "hostHelperInputSent": True,
                    "p2Button31ReceiveRows": 1,
                    "p2ForwardStateStoreRows": 1,
                    "gameInputSentBySecondHostClient": False,
                    "runtimeInputWindowEventCount": 2,
                    "rawEvidenceMaterialUnitCount": 2,
                    "observedProcessIdentitySha256": old_hashes["processIdentitySha256"],
                }
            )
        elif hash_key == "exactPidCdbLogSha256":
            raw_body.update(
                {
                    "exactPidCdbRuntimeInputEvidence": True,
                    "hostHelperInputBoundToSecondHostCommandSource": True,
                    "hostHelperBoundRemoteSlot": EXPECTED_HOST_HELPER_REMOTE_SLOT,
                    "hostHelperBoundAcceptedSecondHostCommandId": EXPECTED_HOST_HELPER_SECOND_HOST_COMMAND_ID,
                    "hostHelperBoundHostAuthorityCommandId": EXPECTED_HOST_HELPER_HOST_AUTHORITY_COMMAND_ID,
                    "hostHelperMappedInputSequence": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE,
                    "hostHelperMappedInputSequenceSha256": EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
                    "hostHelperRuntimeRoute": EXPECTED_HOST_HELPER_RUNTIME_ROUTE,
                    "hostHelperInputDevice": EXPECTED_HOST_HELPER_INPUT_DEVICE,
                    "hostHelperInputSent": True,
                    "p2Button31ReceiveRows": 1,
                    "p2ForwardStateStoreRows": 1,
                    "gameInputSentBySecondHostClient": False,
                    "pidObservedInCdbLog": True,
                    "beaExeObservedInCdbLog": True,
                    "cdbLogLineCount": 12,
                    "rawEvidenceMaterialUnitCount": 12,
                    "observedProcessIdentitySha256": old_hashes["processIdentitySha256"],
                }
            )
        elif hash_key == "copiedRuntimeArtifactSha256":
            raw_body.update(
                {
                    "copiedRuntimeArtifactRowCount": 4,
                    "rawEvidenceMaterialUnitCount": 4,
                    "copiedRuntimeArtifactSha256": old_hashes["copiedRuntimeArtifactSha256"],
                }
            )
        elif hash_key == "copiedRuntimeExeSha256":
            raw_body.update({"computedFromCopiedExeBytes": True, "copiedRuntimeExeSha256": old_hashes["copiedRuntimeExeSha256"]})
        elif hash_key == "processIdentitySha256":
            raw_body.update({"observedPid": 4242, "observedImageName": "BEA.exe", "observedProcessIdentitySha256": old_hashes["processIdentitySha256"]})
        evidence: dict[str, Any] = {
            "schemaVersion": RAW_ARTIFACT_EVIDENCE_SCHEMA,
            "artifactRole": RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key],
            "hashKey": hash_key,
            "runId": run_id,
            "evidenceMode": "self-test-file-backed-artifact",
            "sourceBound": True,
            "sameRunArtifact": True,
            "fixtureOrPosthocBinding": False,
            "acceptedSecondHostCommandRequestPayloadSha256": payload["sourceBinding"]["acceptedSecondHostCommandRequestPayloadSha256"],
            "secondHostInvitationLifecycleSha256": payload["sourceBinding"]["secondHostInvitationLifecycleSha256"],
            "selfTestOnly": True,
            RAW_ARTIFACT_ROLE_PROOF_FLAG[hash_key]: True,
            "rawEvidenceBody": raw_body,
        }
        if hash_key in ("runtimeInputWindowArtifactSha256", "exactPidCdbLogSha256", "processIdentitySha256"):
            evidence["observedProcessIdentitySha256"] = old_hashes["processIdentitySha256"]
        if hash_key == "copiedRuntimeArtifactSha256":
            evidence["copiedRuntimeArtifactSha256"] = old_hashes["copiedRuntimeArtifactSha256"]
        if hash_key == "copiedRuntimeExeSha256":
            evidence["copiedRuntimeExeSha256"] = old_hashes["copiedRuntimeExeSha256"]
        return evidence

    for hash_key in CHAIN_HASH_KEYS:
        relative_path = Path("artifacts") / f"{hash_key}.json"
        artifact_path = root / relative_path
        artifact_payload = {
            "secondHostRuntimeCausalityArtifact": {
                "schemaVersion": RAW_ARTIFACT_RECEIPT_SCHEMA,
                "artifactRole": RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key],
                "hashKey": hash_key,
                "runId": run_id,
                "sourceBound": True,
                "sameRunArtifact": True,
                "fixtureOrPosthocBinding": False,
                "acceptedSecondHostCommandRequestPayloadSha256": payload["sourceBinding"]["acceptedSecondHostCommandRequestPayloadSha256"],
                "secondHostInvitationLifecycleSha256": payload["sourceBinding"]["secondHostInvitationLifecycleSha256"],
                "selfTestOnly": True,
            },
            "roleSpecificRawEvidence": role_evidence(hash_key),
        }
        write_json(artifact_path, artifact_payload)
        artifact_hash = sha256_file(artifact_path)
        artifact_hashes[hash_key] = artifact_hash
        artifact_receipts[hash_key] = {
            "relativePath": relative_path.as_posix(),
            "sha256": artifact_hash,
        }
    replacements = {old_run_id: run_id}
    replacements.update({old_hashes[key]: artifact_hashes[key] for key in CHAIN_HASH_KEYS})
    payload = replace_scalar_values(payload, replacements)
    payload["rawArtifactChain"]["artifactReferenceMode"] = ARTIFACT_REFERENCE_MODE
    payload["rawArtifactChain"]["artifactReferencesRecomputedFromFiles"] = True
    payload["rawArtifactChain"]["privateArtifactRootPublished"] = False
    payload["rawArtifactChain"]["artifactReceipts"] = artifact_receipts
    candidate_path = root / "second-host-runtime-causality-candidate.json"
    write_json(candidate_path, payload)
    return candidate_path


def make_contract_fixture() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "gateScope": "second-host-runtime-causality-proof-gate-not-host-join-enable",
        "status": "validator-ready-no-accepted-live-second-host-runtime-causality-proof",
        "validator": {
            "script": "tools/winui_safe_copy_online_second_host_runtime_causality_check.py",
            "packageScript": PACKAGE_SCRIPT,
            "validatesPrivateProofSchema": SCHEMA,
        },
        "requiredRawArtifactReceipts": [
            "second-host-command-source-proof",
            "scheduler-proof",
            "bridge-proof",
            "runtime-input-window-artifact",
            "exact-pid-cdb-log",
            "copied-runtime-artifact",
            "copied-runtime-exe-hash",
            "process-identity-proof",
        ],
        "livePromotionRequirements": {
            "requiresRawArtifactReceiptsRecomputed": True,
            "requiresPrivateRuntimeProofRoot": True,
            "requiresSemanticRawArtifactReceipts": True,
            "requiresRoleSpecificRawEvidenceBodies": True,
            "requiresConcreteRawEvidenceBodyFields": True,
            "requiresRoleSpecificRawEvidenceMaterialDescriptors": True,
            "requiresRawEvidenceSha256RecomputedFromFiles": True,
            "requiresCandidateBundleRelativePrivateRootContainedArtifacts": True,
            "rejectsReceiptOnlyCandidates": True,
            "rejectsJsonOnlyForgedArtifacts": True,
            "rejectsSelfTestOnlyRawArtifacts": True,
            "scansCandidateAndRawArtifactsForPrivatePaths": True,
            "requiresSameRunArtifactChain": True,
            "requiresRunIdBoundAcrossReceipts": True,
            "requiresAcceptedCommandPayloadHashBoundEndToEnd": True,
            "requiresInvitationLifecycleHashBoundEndToEnd": True,
            "requiresLocalSourceSafetyPreflightForLiveRuntime": True,
            "requiresExactPidCdbRuntimeInputEvidence": True,
            "requiresRuntimeInputDerivedFromSecondHostCommandSource": True,
            "requiresRuntimeDrivenBySecondHostCommandSource": True,
            "requiresHostHelperInputBoundToSecondHostCommandSource": True,
            "requiresMappedP2SequenceReceipt": True,
            "rejectsSecondHostClientDirectGameInputBypass": True,
            "rejectsHostAuthorityDerivedRuntimeInput": True,
            "keepsHostJoinDisabledUntilCompositeGate": True,
        },
        "currentEvidence": {
            "acceptedLiveSecondHostRuntimeCausalityProof": False,
            "acceptedLiveSecondHostRuntimeDeliveryProof": False,
            "runtimeInputDerivedFromSecondHostCommandSource": False,
            "runtimeDrivenBySecondHostCommandSource": False,
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
        },
        "nonClaims": {
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "coOpVersusRuntimeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "privateArtifactContentPublished": False,
            "rawPrivateProofPathPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This gate defines the proof class for source-bound second-host command to copied-runtime causality. "
            "It does not enable Host/Join, base online multiplayer, public matchmaking, native BEA netcode, P3/P4 "
            "original-binary gameplay, co-op/versus runtime behavior, deterministic sync, rollback, anti-cheat, "
            "rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    require_no_hidden_truthy_overclaim_flags(payload)
    require(payload.get("schemaVersion") == SCHEMA, "contract schema mismatch")
    require(payload.get("gateScope") == "second-host-runtime-causality-proof-gate-not-host-join-enable", "contract scope mismatch")
    validator = object_at(payload, "validator")
    require(validator.get("script") == "tools/winui_safe_copy_online_second_host_runtime_causality_check.py", "validator script mismatch")
    require(validator.get("packageScript") == PACKAGE_SCRIPT, "validator package script mismatch")
    require(validator.get("validatesPrivateProofSchema") == SCHEMA, "private proof schema mismatch")
    required_receipts = payload.get("requiredRawArtifactReceipts")
    require(isinstance(required_receipts, list), "required raw artifact receipts must be a list")
    require(required_receipts == list(RAW_ARTIFACT_RECEIPTS), "required raw artifact receipts mismatch")
    requirements = object_at(payload, "livePromotionRequirements")
    require_exact_keys(requirements, LIVE_PROMOTION_REQUIREMENT_KEYS, "livePromotionRequirements")
    for key in LIVE_PROMOTION_REQUIREMENT_KEYS:
        require(requirements.get(key) is True, f"live promotion requirement must be true: {key}")
    evidence = object_at(payload, "currentEvidence")
    require_exact_keys(evidence, CURRENT_EVIDENCE_KEYS, "currentEvidence")
    for key in CURRENT_EVIDENCE_KEYS:
        require(evidence.get(key) is False, f"current evidence must remain false until live proof exists: {key}")
    nonclaims = object_at(payload, "nonClaims")
    require_exact_keys(nonclaims, NONCLAIM_KEYS, "nonClaims")
    for key in NONCLAIM_KEYS:
        require_false(nonclaims, key, "contract non-claim")
    release = object_at(payload, "releaseBoundary")
    require_exact_keys(release, RELEASE_BOUNDARY_KEYS, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof boundary missing")
    for key in ("privateArtifactContentPublished", "rawPrivateProofPathPublished", "publicHostOrMatchmakingEndpointPublished", "releaseIncludedPrivateArtifact"):
        require_false(release, key, "contract release boundary")
    claim = str(payload.get("claimBoundary") or "")
    for token in ("does not enable Host/Join", "base online multiplayer", "public matchmaking", "native BEA netcode", "P3/P4"):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "schemaVersion": payload["schemaVersion"],
        "gateScope": payload["gateScope"],
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
    }


def run_self_test() -> None:
    PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    validate_causality_candidate(make_future_raw_artifact_fixture(), allow_fixture=True)
    with tempfile.TemporaryDirectory(prefix="second-host-runtime-causality-selftest-", dir=PRIVATE_PROOF_ROOT) as tmp:
        candidate_path = write_file_backed_self_test_candidate(Path(tmp))
        validate_causality_candidate(read_json(candidate_path), candidate_path=candidate_path, allow_fixture=True)
    validate_contract(make_contract_fixture())
    try:
        validate_causality_candidate(promotion_guard.make_future_candidate_fixture())
    except SecondHostRuntimeCausalityError:
        pass
    else:
        raise AssertionError("shape-only promotion fixture must fail raw-artifact causality check")
    for label, mutator in (
        ("bridge-hash", lambda p: p["rawArtifactChain"].__setitem__("bridgeProofSha256", "1" * 64)),
        ("run-id", lambda p: p["sourceBoundRuntimeCausalityReceipt"]["schedulerReceipt"].__setitem__("runId", "wrong-run")),
        ("source-safety", lambda p: p["sourceSafety"].__setitem__("evidenceMode", "self-test-fixture")),
        ("host-join", lambda p: p["nonClaims"].__setitem__("hostJoinControlsMayBeEnabled", True)),
    ):
        with tempfile.TemporaryDirectory(prefix="second-host-runtime-causality-negative-", dir=PRIVATE_PROOF_ROOT) as tmp:
            candidate_path = write_file_backed_self_test_candidate(Path(tmp))
            payload = read_json(candidate_path)
            mutator(payload)
            try:
                validate_causality_candidate(payload, candidate_path=candidate_path, allow_fixture=True)
            except SecondHostRuntimeCausalityError:
                pass
            else:
                raise AssertionError(f"mutated causality fixture should fail: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime causality checker self-test: PASS")
        return 0
    if args.check:
        summary = validate_contract(read_json(CONTRACT_PATH))
        print("WinUI original-binary second-host runtime causality gate check: PASS")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    require(args.candidate is not None, "candidate path is required unless --self-test or --check is used")
    print(json.dumps(validate_causality_candidate(read_json(args.candidate), candidate_path=args.candidate), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SecondHostRuntimeCausalityError, json.JSONDecodeError) as exc:
        print(f"WinUI original-binary second-host runtime causality check: FAIL: {exc}")
        raise SystemExit(2)
