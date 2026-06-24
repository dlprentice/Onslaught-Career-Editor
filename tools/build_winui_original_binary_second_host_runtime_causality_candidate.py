#!/usr/bin/env python3
"""Materialize second-host runtime-causality candidate artifacts.

This helper is intentionally conservative. It can create a file-backed self-test
candidate for the strict runtime-causality checker, and it rejects the current
host-authority-derived compatibility executor as live material. A later live
builder must supply source-bound raw runtime/CDB evidence before Host/Join can
move.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import winui_safe_copy_online_second_host_runtime_causality_check as causality
import winui_safe_copy_online_second_host_runtime_executor_check as executor_check


HELPER = "winui-original-binary-second-host-runtime-causality-candidate-builder"
HELPER_VERSION = "second-host-runtime-causality-candidate-builder.v1"
DEFAULT_ARTIFACT_ROOT = causality.PRIVATE_PROOF_ROOT / "second-host-runtime-causality-candidate-materializer-20260622"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "second-host-runtime-causality-candidate.json"
RAW_MATERIAL_PLAN_SCHEMA = "winui-original-binary-second-host-runtime-causality-raw-material-plan.v1"
RAW_MATERIAL_PLAN_SCOPE = "raw-material-intake-plan-not-live-runtime-causality-proof"
DEFAULT_RAW_MATERIAL_PLAN_OUTPUT = DEFAULT_ARTIFACT_ROOT / "second-host-runtime-causality-raw-material-plan.json"
RAW_MATERIAL_MANIFEST_SCHEMA = "winui-original-binary-second-host-runtime-causality-raw-material-manifest.v1"
RAW_MATERIAL_MANIFEST_SCOPE = "raw-material-manifest-preflight-not-live-runtime-causality-proof"
DEFAULT_RAW_MATERIAL_MANIFEST_OUTPUT = DEFAULT_ARTIFACT_ROOT / "second-host-runtime-causality-raw-material-manifest.json"
WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"(?i)\b[a-z]:[\\/][^\r\n]*")
UNC_ABSOLUTE_PATH_RE = re.compile(r"\\\\[^\r\n]+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?:(?:/home|/users|/tmp|/var/tmp)/[^\r\n]+)", re.IGNORECASE)
RAW_PLAN_CURRENT_EVIDENCE_FALSE_KEYS = (
    "acceptedLiveSecondHostRuntimeCausalityProof",
    *sorted(causality.CURRENT_EVIDENCE_KEYS),
)
RAW_PLAN_NONCLAIM_FALSE_KEYS = (
    "hostJoinControlsMayBeEnabled",
    "baseOnlineMultiplayerReady",
    *sorted(causality.NONCLAIM_KEYS),
)
RAW_PLAN_TOP_LEVEL_KEYS = {
    "schemaVersion",
    "generatedBy",
    "helperVersion",
    "planScope",
    "candidateSchemaVersion",
    "rawArtifactReceiptSchema",
    "rawEvidenceSchema",
    "rawEvidenceBodySchema",
    "artifactReferenceMode",
    "rawEvidenceReferenceMode",
    "requiredRawMaterialRoles",
    "requiredEndToEndBindings",
    "requiredLivePromotionChecks",
    "currentEvidence",
    "nonClaims",
    "releaseBoundary",
    "claimBoundary",
}
RAW_PLAN_ROLE_KEYS = {
    "hashKey",
    "artifactRole",
    "roleProofFlag",
    "rawEvidenceMaterialKind",
    "requiredReceiptKeys",
    "requiredRawEvidenceBodyKeys",
    "requiredEvidenceMode",
    "sourceBoundRequired",
    "sameRunArtifactRequired",
    "fixtureOrPosthocBindingAllowed",
    "fileBackedRawEvidenceRequired",
    "rawEvidenceSha256RecomputedFromFile",
    "privateRootRelativeReferenceRequired",
    "selfTestOnlyAllowedOnlyWithExplicitFixtureMode",
}
RAW_PLAN_END_TO_END_BINDINGS = (
    "runId",
    "acceptedSecondHostCommandRequestPayloadSha256",
    "secondHostInvitationLifecycleSha256",
    "observedProcessIdentitySha256",
    "hostHelperMappedInputSequenceSha256",
)
RAW_PLAN_RELEASE_BOUNDARY_KEYS = {
    "privateProofReleaseExcludedByPolicy",
    "privateProofRootPublished",
    "privateArtifactContentPublished",
    "rawPrivateProofPathPublished",
    "publicHostOrMatchmakingEndpointPublished",
    "releaseIncludedPrivateArtifact",
}
RAW_MANIFEST_TOP_LEVEL_KEYS = {
    "schemaVersion",
    "generatedBy",
    "helperVersion",
    "manifestScope",
    "candidateSchemaVersion",
    "sourceCandidateRelativePath",
    "sourceCandidateSha256",
    "artifactReferenceMode",
    "rawEvidenceReferenceMode",
    "runId",
    "acceptedSecondHostCommandRequestPayloadSha256",
    "secondHostInvitationLifecycleSha256",
    "observedProcessIdentitySha256",
    "hostHelperMappedInputSequenceSha256",
    "rawMaterialRoles",
    "currentEvidence",
    "nonClaims",
    "releaseBoundary",
    "claimBoundary",
}
RAW_MANIFEST_ROLE_KEYS = {
    "hashKey",
    "artifactRole",
    "roleProofFlag",
    "rawEvidenceMaterialKind",
    "artifactRelativePath",
    "artifactSha256",
    "rawEvidenceRelativePath",
    "rawEvidenceSha256",
    "rawEvidenceBodyKeyCount",
    "rawEvidenceMaterialUnitCount",
    "evidenceMode",
    "sourceBound",
    "sameRunArtifact",
    "fixtureOrPosthocBinding",
    "selfTestOnly",
}


class SecondHostRuntimeCausalityCandidateBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostRuntimeCausalityCandidateBuildError(message)


def redact_private_paths(message: str) -> str:
    redacted = WINDOWS_ABSOLUTE_PATH_RE.sub("<redacted-private-path>", message)
    redacted = UNC_ABSOLUTE_PATH_RE.sub("<redacted-private-path>", redacted)
    redacted = POSIX_PRIVATE_PATH_RE.sub("<redacted-private-path>", redacted)
    return redacted


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "JSON payload must be an object")
    return value


def require_private_path(path: Path, *, must_exist: bool = False) -> Path:
    root = causality.PRIVATE_PROOF_ROOT.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SecondHostRuntimeCausalityCandidateBuildError("artifact must stay under the private runtime proof root") from exc
    if must_exist:
        require(resolved.is_file(), "required private artifact is missing")
    return resolved


def private_root_relative(path: Path) -> str:
    return path.resolve().relative_to(causality.PRIVATE_PROOF_ROOT.resolve()).as_posix()


def make_raw_material_plan() -> dict[str, Any]:
    roles: list[dict[str, Any]] = []
    for hash_key in causality.CHAIN_HASH_KEYS:
        role_keys = sorted(causality.RAW_BODY_BASE_KEYS | causality.RAW_BODY_ROLE_KEYS[hash_key])
        roles.append(
            {
                "hashKey": hash_key,
                "artifactRole": causality.RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key],
                "roleProofFlag": causality.RAW_ARTIFACT_ROLE_PROOF_FLAG[hash_key],
                "rawEvidenceMaterialKind": causality.RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key],
                "requiredReceiptKeys": sorted(causality.RAW_ARTIFACT_RECEIPT_KEYS),
                "requiredRawEvidenceBodyKeys": role_keys,
                "requiredEvidenceMode": "live-runtime-artifact",
                "sourceBoundRequired": True,
                "sameRunArtifactRequired": True,
                "fixtureOrPosthocBindingAllowed": False,
                "fileBackedRawEvidenceRequired": True,
                "rawEvidenceSha256RecomputedFromFile": True,
                "privateRootRelativeReferenceRequired": True,
                "selfTestOnlyAllowedOnlyWithExplicitFixtureMode": True,
            }
        )
    return {
        "schemaVersion": RAW_MATERIAL_PLAN_SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "planScope": RAW_MATERIAL_PLAN_SCOPE,
        "candidateSchemaVersion": causality.SCHEMA,
        "rawArtifactReceiptSchema": causality.RAW_ARTIFACT_RECEIPT_SCHEMA,
        "rawEvidenceSchema": causality.RAW_ARTIFACT_EVIDENCE_SCHEMA,
        "rawEvidenceBodySchema": causality.RAW_ARTIFACT_BODY_SCHEMA,
        "artifactReferenceMode": causality.ARTIFACT_REFERENCE_MODE,
        "rawEvidenceReferenceMode": causality.RAW_EVIDENCE_REFERENCE_MODE,
        "requiredRawMaterialRoles": roles,
        "requiredEndToEndBindings": list(RAW_PLAN_END_TO_END_BINDINGS),
        "requiredLivePromotionChecks": {key: True for key in sorted(causality.LIVE_PROMOTION_REQUIREMENT_KEYS)},
        "currentEvidence": {key: False for key in RAW_PLAN_CURRENT_EVIDENCE_FALSE_KEYS},
        "nonClaims": {key: False for key in RAW_PLAN_NONCLAIM_FALSE_KEYS},
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "privateProofRootPublished": False,
            "privateArtifactContentPublished": False,
            "rawPrivateProofPathPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This is a raw-material intake plan for a future source-bound second-host runtime-causality "
            "candidate. It does not create or accept live runtime causality, enable Host/Join, prove "
            "player-ready online multiplayer, publish private artifact roots, open a listener, create an "
            "invitation, launch BEA, attach CDB, or send input."
        ),
    }


def validate_raw_material_plan(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        causality.require_no_sensitive_string_values(payload)
        causality.require_no_hidden_truthy_overclaim_flags(payload)
    except causality.SecondHostRuntimeCausalityError as exc:
        raise SecondHostRuntimeCausalityCandidateBuildError(str(exc)) from exc
    require(set(payload) == RAW_PLAN_TOP_LEVEL_KEYS, "raw-material plan top-level key set mismatch")
    require(payload.get("schemaVersion") == RAW_MATERIAL_PLAN_SCHEMA, "raw-material plan schema mismatch")
    require(payload.get("generatedBy") == HELPER, "raw-material plan helper mismatch")
    require(payload.get("helperVersion") == HELPER_VERSION, "raw-material plan helper version mismatch")
    require(payload.get("planScope") == RAW_MATERIAL_PLAN_SCOPE, "raw-material plan scope mismatch")
    require(payload.get("candidateSchemaVersion") == causality.SCHEMA, "raw-material plan candidate schema mismatch")
    require(payload.get("rawArtifactReceiptSchema") == causality.RAW_ARTIFACT_RECEIPT_SCHEMA, "raw-material plan receipt schema mismatch")
    require(payload.get("rawEvidenceSchema") == causality.RAW_ARTIFACT_EVIDENCE_SCHEMA, "raw-material plan evidence schema mismatch")
    require(payload.get("rawEvidenceBodySchema") == causality.RAW_ARTIFACT_BODY_SCHEMA, "raw-material plan body schema mismatch")
    require(payload.get("artifactReferenceMode") == causality.ARTIFACT_REFERENCE_MODE, "raw-material plan artifact reference mode mismatch")
    require(payload.get("rawEvidenceReferenceMode") == causality.RAW_EVIDENCE_REFERENCE_MODE, "raw-material plan raw evidence reference mode mismatch")
    require(
        payload.get("requiredEndToEndBindings") == list(RAW_PLAN_END_TO_END_BINDINGS),
        "raw-material plan end-to-end bindings mismatch",
    )
    roles = payload.get("requiredRawMaterialRoles")
    require(isinstance(roles, list), "requiredRawMaterialRoles must be a list")
    by_hash: dict[str, dict[str, Any]] = {}
    for row in roles:
        require(isinstance(row, dict), "raw-material role rows must be objects")
        require(set(row) == RAW_PLAN_ROLE_KEYS, "raw-material role key set mismatch")
        hash_key = str(row.get("hashKey") or "")
        require(hash_key, "raw-material role hashKey is missing")
        require(hash_key not in by_hash, f"duplicate raw-material role hashKey: {hash_key}")
        by_hash[hash_key] = row
    expected_hash_keys = set(causality.CHAIN_HASH_KEYS)
    require(set(by_hash) == expected_hash_keys, "raw-material role set mismatch")
    for hash_key in causality.CHAIN_HASH_KEYS:
        row = by_hash[hash_key]
        require(row.get("artifactRole") == causality.RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key], f"artifact role mismatch: {hash_key}")
        require(row.get("roleProofFlag") == causality.RAW_ARTIFACT_ROLE_PROOF_FLAG[hash_key], f"role proof flag mismatch: {hash_key}")
        require(
            row.get("rawEvidenceMaterialKind") == causality.RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key],
            f"raw material kind mismatch: {hash_key}",
        )
        require(row.get("requiredEvidenceMode") == "live-runtime-artifact", f"required evidence mode mismatch: {hash_key}")
        require(row.get("requiredReceiptKeys") == sorted(causality.RAW_ARTIFACT_RECEIPT_KEYS), f"receipt keys mismatch: {hash_key}")
        require(
            row.get("requiredRawEvidenceBodyKeys") == sorted(causality.RAW_BODY_BASE_KEYS | causality.RAW_BODY_ROLE_KEYS[hash_key]),
            f"raw evidence body keys mismatch: {hash_key}",
        )
        for key in (
            "sourceBoundRequired",
            "sameRunArtifactRequired",
            "fileBackedRawEvidenceRequired",
            "rawEvidenceSha256RecomputedFromFile",
            "privateRootRelativeReferenceRequired",
            "selfTestOnlyAllowedOnlyWithExplicitFixtureMode",
        ):
            require(row.get(key) is True, f"{hash_key} must require {key}")
        require(row.get("fixtureOrPosthocBindingAllowed") is False, f"{hash_key} must reject fixture/posthoc binding")
    checks = payload.get("requiredLivePromotionChecks")
    require(isinstance(checks, dict), "requiredLivePromotionChecks must be an object")
    require(set(checks) == set(causality.LIVE_PROMOTION_REQUIREMENT_KEYS), "requiredLivePromotionChecks key set mismatch")
    for key, value in checks.items():
        require(value is True, f"required live promotion check must stay true: {key}")
    current = payload.get("currentEvidence")
    require(isinstance(current, dict), "currentEvidence must be an object")
    require(set(current) == set(RAW_PLAN_CURRENT_EVIDENCE_FALSE_KEYS), "currentEvidence key set mismatch")
    for key, value in current.items():
        require(value is False, f"current evidence must remain false: {key}")
    nonclaims = payload.get("nonClaims")
    require(isinstance(nonclaims, dict), "nonClaims must be an object")
    require(set(nonclaims) == set(RAW_PLAN_NONCLAIM_FALSE_KEYS), "nonClaims key set mismatch")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    release = payload.get("releaseBoundary")
    require(isinstance(release, dict), "releaseBoundary must be an object")
    require(set(release) == RAW_PLAN_RELEASE_BOUNDARY_KEYS, "releaseBoundary key set mismatch")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key in (
        "privateProofRootPublished",
        "privateArtifactContentPublished",
        "rawPrivateProofPathPublished",
        "publicHostOrMatchmakingEndpointPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(release.get(key) is False, f"release boundary must remain false: {key}")
    return {
        "schemaVersion": payload["schemaVersion"],
        "planScope": payload["planScope"],
        "requiredRoleCount": len(roles),
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
        "acceptedLiveSecondHostRuntimeCausalityProof": False,
        "privateProofRootPublished": False,
    }


def build_raw_material_plan(output_path: Path = DEFAULT_RAW_MATERIAL_PLAN_OUTPUT) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    require(
        output_path.name.lower() != DEFAULT_OUTPUT.name.lower(),
        "raw-material plan output cannot use the runtime-causality candidate artifact filename",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = make_raw_material_plan()
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = validate_raw_material_plan(read_json(output_path))
    summary.update(
        {
            "artifact": private_root_relative(output_path),
            "generatedBy": HELPER,
            "helperVersion": HELPER_VERSION,
        }
    )
    return summary


def resolve_manifest_relative_path(root: Path, relative_text: Any, label: str) -> Path:
    text = str(relative_text or "")
    require(text, f"{label} is missing")
    require(":" not in text, f"{label} must not contain a drive or URI separator")
    relative = Path(text)
    require(not relative.is_absolute(), f"{label} must be manifest-relative")
    require(".." not in relative.parts, f"{label} must not traverse upward")
    root_resolved = root.resolve()
    target = (root_resolved / relative).resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise SecondHostRuntimeCausalityCandidateBuildError(f"{label} escapes the manifest root") from exc
    require(target.is_file(), f"{label} file is missing")
    require_private_path(target, must_exist=True)
    return target


def manifest_relative(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def make_raw_material_manifest_from_candidate(candidate_path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    candidate_path = require_private_path(candidate_path, must_exist=True)
    payload = read_json(candidate_path)
    causality.validate_causality_candidate(
        payload,
        candidate_path=candidate_path,
        allow_fixture=allow_fixture,
    )
    root = candidate_path.parent
    source_binding = object_at(payload, "sourceBinding")
    raw = object_at(payload, "rawArtifactChain")
    receipts = object_at(raw, "artifactReceipts")
    roles: list[dict[str, Any]] = []
    observed_process_identity_sha256 = ""
    for hash_key in causality.CHAIN_HASH_KEYS:
        receipt = object_at(receipts, hash_key)
        artifact_path = resolve_manifest_relative_path(root, receipt.get("relativePath"), f"{hash_key} artifact relative path")
        artifact_payload = read_json(artifact_path)
        evidence = object_at(artifact_payload, "roleSpecificRawEvidence")
        body = object_at(evidence, "rawEvidenceBody")
        raw_evidence_path = resolve_manifest_relative_path(
            root,
            body.get("rawEvidenceRelativePath"),
            f"{hash_key} raw evidence relative path",
        )
        role = {
            "hashKey": hash_key,
            "artifactRole": causality.RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key],
            "roleProofFlag": causality.RAW_ARTIFACT_ROLE_PROOF_FLAG[hash_key],
            "rawEvidenceMaterialKind": causality.RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key],
            "artifactRelativePath": manifest_relative(root, artifact_path),
            "artifactSha256": causality.sha256_file(artifact_path),
            "rawEvidenceRelativePath": manifest_relative(root, raw_evidence_path),
            "rawEvidenceSha256": causality.sha256_file(raw_evidence_path),
            "rawEvidenceBodyKeyCount": len(body),
            "rawEvidenceMaterialUnitCount": int(body.get("rawEvidenceMaterialUnitCount") or 0),
            "evidenceMode": str(body.get("evidenceMode") or ""),
            "sourceBound": body.get("sourceBound"),
            "sameRunArtifact": body.get("sameRunArtifact"),
            "fixtureOrPosthocBinding": body.get("fixtureOrPosthocBinding"),
            "selfTestOnly": body.get("selfTestOnly"),
        }
        roles.append(role)
        if hash_key == "processIdentitySha256":
            observed_process_identity_sha256 = str(body.get("observedProcessIdentitySha256") or "")
    return {
        "schemaVersion": RAW_MATERIAL_MANIFEST_SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "manifestScope": RAW_MATERIAL_MANIFEST_SCOPE,
        "candidateSchemaVersion": causality.SCHEMA,
        "sourceCandidateRelativePath": manifest_relative(root, candidate_path),
        "sourceCandidateSha256": causality.sha256_file(candidate_path),
        "artifactReferenceMode": causality.ARTIFACT_REFERENCE_MODE,
        "rawEvidenceReferenceMode": causality.RAW_EVIDENCE_REFERENCE_MODE,
        "runId": raw.get("runId"),
        "acceptedSecondHostCommandRequestPayloadSha256": source_binding.get("acceptedSecondHostCommandRequestPayloadSha256"),
        "secondHostInvitationLifecycleSha256": source_binding.get("secondHostInvitationLifecycleSha256"),
        "observedProcessIdentitySha256": observed_process_identity_sha256,
        "hostHelperMappedInputSequenceSha256": causality.EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
        "rawMaterialRoles": roles,
        "currentEvidence": {key: False for key in RAW_PLAN_CURRENT_EVIDENCE_FALSE_KEYS},
        "nonClaims": {key: False for key in RAW_PLAN_NONCLAIM_FALSE_KEYS},
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "privateProofRootPublished": False,
            "privateArtifactContentPublished": False,
            "rawPrivateProofPathPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This manifest inventories candidate-bundle-relative raw material for the second-host runtime "
            "causality gate. It does not create or accept live runtime causality, enable Host/Join, prove "
            "player-ready online multiplayer, publish private artifact roots, open a listener, create an "
            "invitation, launch BEA, attach CDB, or send input."
        ),
    }


def validate_raw_material_manifest(
    payload: dict[str, Any],
    *,
    manifest_path: Path | None = None,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    try:
        causality.require_no_sensitive_string_values(payload)
        causality.require_no_hidden_truthy_overclaim_flags(payload)
    except causality.SecondHostRuntimeCausalityError as exc:
        raise SecondHostRuntimeCausalityCandidateBuildError(str(exc)) from exc
    require(set(payload) == RAW_MANIFEST_TOP_LEVEL_KEYS, "raw-material manifest top-level key set mismatch")
    require(payload.get("schemaVersion") == RAW_MATERIAL_MANIFEST_SCHEMA, "raw-material manifest schema mismatch")
    require(payload.get("generatedBy") == HELPER, "raw-material manifest helper mismatch")
    require(payload.get("helperVersion") == HELPER_VERSION, "raw-material manifest helper version mismatch")
    require(payload.get("manifestScope") == RAW_MATERIAL_MANIFEST_SCOPE, "raw-material manifest scope mismatch")
    require(payload.get("candidateSchemaVersion") == causality.SCHEMA, "raw-material manifest candidate schema mismatch")
    require(payload.get("artifactReferenceMode") == causality.ARTIFACT_REFERENCE_MODE, "raw-material manifest artifact mode mismatch")
    require(payload.get("rawEvidenceReferenceMode") == causality.RAW_EVIDENCE_REFERENCE_MODE, "raw-material manifest raw evidence mode mismatch")
    accepted_payload_hash = causality.require_hash(
        payload.get("acceptedSecondHostCommandRequestPayloadSha256"),
        "manifest accepted payload hash",
    )
    invitation_hash = causality.require_hash(payload.get("secondHostInvitationLifecycleSha256"), "manifest invitation hash")
    observed_process_identity = causality.require_hash(payload.get("observedProcessIdentitySha256"), "manifest observed process identity")
    require(
        payload.get("hostHelperMappedInputSequenceSha256") == causality.EXPECTED_HOST_HELPER_MAPPED_INPUT_SEQUENCE_SHA256,
        "manifest mapped input sequence hash mismatch",
    )
    roles = payload.get("rawMaterialRoles")
    require(isinstance(roles, list), "rawMaterialRoles must be a list")
    by_hash: dict[str, dict[str, Any]] = {}
    for row in roles:
        require(isinstance(row, dict), "raw material role rows must be objects")
        require(set(row) == RAW_MANIFEST_ROLE_KEYS, "raw material manifest role key set mismatch")
        hash_key = str(row.get("hashKey") or "")
        require(hash_key not in by_hash, f"duplicate raw material manifest role: {hash_key}")
        by_hash[hash_key] = row
    require(set(by_hash) == set(causality.CHAIN_HASH_KEYS), "raw material manifest role set mismatch")
    expected_evidence_mode = "self-test-file-backed-artifact" if allow_fixture else "live-runtime-artifact"
    expected_self_test = bool(allow_fixture)
    root = manifest_path.parent if manifest_path is not None else None
    if root is not None:
        require_private_path(manifest_path, must_exist=True)
        candidate_path = resolve_manifest_relative_path(root, payload.get("sourceCandidateRelativePath"), "manifest source candidate path")
        require(causality.sha256_file(candidate_path) == payload.get("sourceCandidateSha256"), "manifest source candidate hash mismatch")
    for hash_key in causality.CHAIN_HASH_KEYS:
        row = by_hash[hash_key]
        require(row.get("artifactRole") == causality.RAW_ARTIFACT_ROLE_BY_HASH_KEY[hash_key], f"manifest artifact role mismatch: {hash_key}")
        require(row.get("roleProofFlag") == causality.RAW_ARTIFACT_ROLE_PROOF_FLAG[hash_key], f"manifest proof flag mismatch: {hash_key}")
        require(row.get("rawEvidenceMaterialKind") == causality.RAW_EVIDENCE_MATERIAL_KIND_BY_HASH_KEY[hash_key], f"manifest material kind mismatch: {hash_key}")
        require(row.get("evidenceMode") == expected_evidence_mode, f"manifest evidence mode mismatch: {hash_key}")
        require(row.get("sourceBound") is True, f"manifest role must be source-bound: {hash_key}")
        require(row.get("sameRunArtifact") is True, f"manifest role must be same-run: {hash_key}")
        require(row.get("fixtureOrPosthocBinding") is False, f"manifest role must not be fixture/posthoc: {hash_key}")
        require(row.get("selfTestOnly") is expected_self_test, f"manifest self-test flag mismatch: {hash_key}")
        require(int(row.get("rawEvidenceBodyKeyCount") or 0) == len(causality.RAW_BODY_BASE_KEYS | causality.RAW_BODY_ROLE_KEYS[hash_key]), f"manifest body key count mismatch: {hash_key}")
        require(int(row.get("rawEvidenceMaterialUnitCount") or 0) > 0, f"manifest material unit count missing: {hash_key}")
        if root is not None:
            artifact_path = resolve_manifest_relative_path(root, row.get("artifactRelativePath"), f"{hash_key} manifest artifact path")
            raw_path = resolve_manifest_relative_path(root, row.get("rawEvidenceRelativePath"), f"{hash_key} manifest raw evidence path")
            require(causality.sha256_file(artifact_path) == row.get("artifactSha256"), f"manifest artifact hash mismatch: {hash_key}")
            require(causality.sha256_file(raw_path) == row.get("rawEvidenceSha256"), f"manifest raw evidence hash mismatch: {hash_key}")
            causality.validate_artifact_semantic_receipt(
                artifact_path,
                hash_key,
                artifact_root=root,
                run_id=str(payload.get("runId") or ""),
                accepted_payload_hash=accepted_payload_hash,
                invitation_hash=invitation_hash,
                allow_fixture=allow_fixture,
            )
    require(by_hash["processIdentitySha256"]["rawEvidenceSha256"], "manifest process identity raw evidence hash missing")
    require(observed_process_identity, "manifest observed process identity missing")
    current = object_at(payload, "currentEvidence")
    require(set(current) == set(RAW_PLAN_CURRENT_EVIDENCE_FALSE_KEYS), "manifest currentEvidence key set mismatch")
    for key, value in current.items():
        require(value is False, f"manifest current evidence must remain false: {key}")
    nonclaims = object_at(payload, "nonClaims")
    require(set(nonclaims) == set(RAW_PLAN_NONCLAIM_FALSE_KEYS), "manifest nonClaims key set mismatch")
    for key, value in nonclaims.items():
        require(value is False, f"manifest non-claim must remain false: {key}")
    release = object_at(payload, "releaseBoundary")
    require(set(release) == RAW_PLAN_RELEASE_BOUNDARY_KEYS, "manifest releaseBoundary key set mismatch")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "manifest private release boundary missing")
    for key in (
        "privateProofRootPublished",
        "privateArtifactContentPublished",
        "rawPrivateProofPathPublished",
        "publicHostOrMatchmakingEndpointPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(release.get(key) is False, f"manifest release boundary must remain false: {key}")
    return {
        "schemaVersion": payload["schemaVersion"],
        "manifestScope": payload["manifestScope"],
        "requiredRoleCount": len(roles),
        "allowFixtureMaterial": bool(allow_fixture),
        "acceptedLiveSecondHostRuntimeCausalityProof": False,
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
        "privateProofRootPublished": False,
    }


def build_raw_material_manifest_from_candidate(
    candidate_path: Path,
    output_path: Path | None = None,
    *,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    candidate_path = require_private_path(candidate_path, must_exist=True)
    output_path = require_private_path(output_path or candidate_path.with_name(DEFAULT_RAW_MATERIAL_MANIFEST_OUTPUT.name))
    require(
        output_path.name.lower() != DEFAULT_OUTPUT.name.lower(),
        "raw-material manifest output cannot use the runtime-causality candidate artifact filename",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = make_raw_material_manifest_from_candidate(candidate_path, allow_fixture=allow_fixture)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = validate_raw_material_manifest(read_json(output_path), manifest_path=output_path, allow_fixture=allow_fixture)
    summary.update(
        {
            "artifact": private_root_relative(output_path),
            "generatedBy": HELPER,
            "helperVersion": HELPER_VERSION,
        }
    )
    return summary


def build_file_backed_self_test_candidate(output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path = causality.write_file_backed_self_test_candidate(output_path.parent)
    if generated_path.resolve() != output_path.resolve():
        if output_path.exists():
            output_path.unlink()
        generated_path.replace(output_path)
    summary = causality.validate_causality_candidate(
        causality.read_json(output_path),
        candidate_path=output_path,
        allow_fixture=True,
    )
    summary.update(
        {
            "artifact": private_root_relative(output_path),
            "generatedBy": HELPER,
            "helperVersion": HELPER_VERSION,
            "materializerScope": "file-backed-self-test-only-not-live-second-host-runtime-causality",
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
        }
    )
    return summary


def build_candidate_from_runtime_executor(
    runtime_executor_proof: Path,
    output_path: Path = DEFAULT_OUTPUT,
    *,
    allow_fixture_executor: bool = False,
) -> dict[str, Any]:
    runtime_executor_proof = require_private_path(runtime_executor_proof, must_exist=True)
    output_path = require_private_path(output_path)
    try:
        summary = executor_check.validate_bundle(runtime_executor_proof, allow_fixture=allow_fixture_executor)
    except Exception as exc:  # noqa: BLE001 - normalize nested validator errors for a fail-closed CLI.
        raise SecondHostRuntimeCausalityCandidateBuildError(
            f"runtime executor proof rejected: {redact_private_paths(str(exc))}"
        ) from exc

    missing_live_boundary = [
        key
        for key in (
            "runtimeInputDerivedFromSecondHostCommandSource",
            "runtimeDrivenBySecondHostCommandSource",
            "acceptedLiveSecondHostRuntimeDeliveryProof",
        )
        if summary.get(key) is not True
    ]
    if missing_live_boundary:
        raise SecondHostRuntimeCausalityCandidateBuildError(
            "host-authority-derived compatibility executor is not live second-host runtime-causality material; "
            f"missing true fields: {', '.join(missing_live_boundary)}"
        )

    # Reaching this branch requires a future executor proof class that already
    # carries direct source-bound runtime input and delivery receipts. Keep this
    # fail-closed until that raw material format exists.
    raise SecondHostRuntimeCausalityCandidateBuildError(
        "accepted source-bound runtime executor materialization requires a future raw-evidence adapter"
    )


def run_self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory(dir=causality.PRIVATE_PROOF_ROOT) as raw_tmp:
        output = Path(raw_tmp) / "second-host-runtime-causality-candidate.json"
        summary = build_file_backed_self_test_candidate(output)
        require(summary["selfTestFixtureCandidate"] is True, "self-test candidate must be fixture-scoped")
        require(summary["acceptedLiveSecondHostRuntimeDeliveryProof"] is False, "self-test candidate must not claim live delivery")
        plan = build_raw_material_plan(Path(raw_tmp) / "second-host-runtime-causality-raw-material-plan.json")
        require(plan["requiredRoleCount"] == len(causality.CHAIN_HASH_KEYS), "raw-material plan role count mismatch")
        require(plan["acceptedLiveSecondHostRuntimeCausalityProof"] is False, "raw-material plan must not claim live causality")
        manifest = build_raw_material_manifest_from_candidate(
            output,
            Path(raw_tmp) / "second-host-runtime-causality-raw-material-manifest.json",
            allow_fixture=True,
        )
        require(manifest["requiredRoleCount"] == len(causality.CHAIN_HASH_KEYS), "raw-material manifest role count mismatch")
        require(manifest["acceptedLiveSecondHostRuntimeCausalityProof"] is False, "raw-material manifest must not claim live causality")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--from-runtime-executor", type=Path)
    parser.add_argument("--raw-material-plan", action="store_true")
    parser.add_argument("--raw-material-manifest-from-candidate", type=Path)
    parser.add_argument("--allow-fixture-raw-material", action="store_true")
    parser.add_argument("--allow-fixture-executor", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host runtime-causality candidate builder self-test: PASS")
        return 0
    if args.raw_material_plan:
        require(args.from_runtime_executor is None, "--raw-material-plan cannot be combined with --from-runtime-executor")
        require(args.raw_material_manifest_from_candidate is None, "--raw-material-plan cannot be combined with --raw-material-manifest-from-candidate")
        print(json.dumps(build_raw_material_plan(args.output or DEFAULT_RAW_MATERIAL_PLAN_OUTPUT), indent=2, sort_keys=True))
    elif args.raw_material_manifest_from_candidate is not None:
        require(args.from_runtime_executor is None, "--raw-material-manifest-from-candidate cannot be combined with --from-runtime-executor")
        print(
            json.dumps(
                build_raw_material_manifest_from_candidate(
                    args.raw_material_manifest_from_candidate,
                    args.output,
                    allow_fixture=args.allow_fixture_raw_material,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    elif args.from_runtime_executor is None:
        require(not args.allow_fixture_raw_material, "--allow-fixture-raw-material requires --raw-material-manifest-from-candidate")
        print(json.dumps(build_file_backed_self_test_candidate(args.output or DEFAULT_OUTPUT), indent=2, sort_keys=True))
    else:
        require(not args.allow_fixture_raw_material, "--allow-fixture-raw-material requires --raw-material-manifest-from-candidate")
        print(
            json.dumps(
                build_candidate_from_runtime_executor(
                    args.from_runtime_executor,
                    args.output or DEFAULT_OUTPUT,
                    allow_fixture_executor=args.allow_fixture_executor,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecondHostRuntimeCausalityCandidateBuildError,
        causality.SecondHostRuntimeCausalityError,
        executor_check.SecondHostRuntimeExecutorError,
        json.JSONDecodeError,
    ) as exc:
        print(f"WinUI original-binary second-host runtime-causality candidate build: FAIL: {exc}")
        raise SystemExit(2)
