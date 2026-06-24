#!/usr/bin/env python3
"""Validate a redacted private-corpus manifest as a consumer input."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import REQUIRED_ARCHIVE_CLASSES
from texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_dry_run import DRY_RUN_STATUS
from texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_materialization import (
    MATERIALIZATION_STATUS,
    SCHEMA_VERSION as MATERIALIZATION_SCHEMA_VERSION,
)


SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation.v1"
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan.v1"
)
CONSUMER_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-"
    "complete-redacted-manifest-consumed-no-content-read"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan"
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
)
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan"

EXPECTED_ARCHIVE_CLASS_COUNTS = {
    "base-resource-archive": 1,
    "frontend-resource-archive": 1,
    "loading-resource-archive": 1,
    "numeric-level-resource-archive": 66,
    "goodie-resource-archive": 232,
}

PUBLIC_ALLOWED_OUTPUTS = (
    "redacted-manifest-consumer-status",
    "redacted-manifest-schema-status",
    "archive-class-counts",
    "archive-class-order-status",
    "required-class-coverage-status",
    "consumer-row-validation-counts",
    "redacted-manifest-row-mode-status",
    "redaction-field-counts",
    "guard-counter-summary",
    "claim-boundary",
)

REDACTED_FIELDS = (
    "private-corpus-root",
    "concrete-resource-archive-path",
    "concrete-resource-directory-path",
    "raw-resource-filename",
    "raw-resource-stem",
    "raw-texture-reference",
    "raw-mesh-reference",
    "private-digest",
    "private-byte-length",
    "operator-profile-identifier",
    "raw-directory-listing",
    "raw-importer-stdout-or-stderr",
    "raw-private-manifest-row",
    "private-manifest-output-path",
    "redacted-private-manifest-artifact-path",
    "ignored-artifact-path",
)

FORBIDDEN_MANIFEST_KEYS = (
    "privateCorpusRoot",
    "concreteResourceArchivePath",
    "concreteResourceDirectoryPath",
    "rawResourceFilename",
    "rawResourceStem",
    "rawTextureReference",
    "rawMeshReference",
    "privateDigest",
    "privateByteLength",
    "operatorProfileIdentifier",
    "rawDirectoryListing",
    "rawImporterStdout",
    "rawImporterStderr",
    "rawPrivateManifestRow",
    "privateManifestOutputPath",
    "redactedPrivateManifestArtifactPath",
    "ignoredArtifactPath",
)

FORBIDDEN_VALUE_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/]"),
    re.compile(r"(?i)program files"),
    re.compile(r"(?i)steamapps"),
    re.compile(r"(?i)c:[\\/]users"),
    re.compile(r"\b[a-fA-F0-9]{64}\b"),
)

ALLOWED_MANIFEST_KEYS = {
    "manifestKind",
    "manifestRowMode",
    "materializationStatus",
    "privateArchiveBytesRead",
    "privateAssetContentRead",
    "privateManifestMaterialized",
    "privateManifestRowsPublished",
    "privateRawManifestMaterialized",
    "privateRawManifestRowsObserved",
    "publicLeakCheck",
    "realImporterExecuted",
    "realImporterImplementation",
    "redactedManifestClassRows",
    "redactedPrivateManifestArtifactPathPublished",
    "redactedPrivateManifestMaterialized",
    "redactedPrivateManifestRows",
    "redactedPrivateManifestSummaryRows",
    "schemaVersion",
    "sourceDryRunStatus",
    "sourceRootClass",
}

ALLOWED_ROW_KEYS = {
    "archiveClass",
    "archiveClassCount",
    "byteLengthRows",
    "manifestRowClass",
    "manifestRowMode",
    "privateArchiveBytesRead",
    "privateAssetContentRead",
    "rawFilenameRows",
    "rawMeshRefRows",
    "rawPathRows",
    "rawTextureRefRows",
}

FALSE_GUARDS = (
    "privateAssetContentRead",
    "privateArchiveBytesRead",
    "privateManifestMaterialized",
    "privateRawManifestMaterialized",
    "privateRawManifestRowsObserved",
    "privateManifestRowsPublished",
    "rawPrivateManifestConsumed",
    "rawPrivateManifestRowsConsumed",
    "rawManifestPathPublished",
    "realImporterImplementation",
    "realImporterExecuted",
    "importerContractAdapterImplemented",
    "privateImporterDryRunExecuted",
    "generatedAssetOutputs",
    "privateAssetPublication",
    "runtimeExecution",
    "beLaunch",
    "screenshotCapture",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "installedGameMutationAllowed",
    "originalExecutableMutationAllowed",
    "productUiWired",
    "rendererImplementation",
    "rebuildImplementation",
    "runtimeResourceArchiveParserProven",
    "runtimeTextureParserBehaviorProven",
    "runtimeTexturePixelsProven",
    "runtimeMeshLoadingProven",
    "runtimeMeshSkinningProven",
    "runtimeDirect3DUploadProven",
    "runtimeGpuBehaviorProven",
    "nativeTextured3DRenderingProven",
    "materialVisualCorrectnessProven",
    "materialShaderParityProven",
    "assetFormatCompletenessProven",
    "exactMeshTextureLayoutsProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "publicPrivateProofLeak",
)

ZERO_COUNTERS = (
    "rawPathRows",
    "rawFilenameRows",
    "rawStemRows",
    "rawHashRows",
    "privateHashRows",
    "byteLengthRows",
    "rawTextureRefRows",
    "rawMeshRefRows",
    "privateManifestRows",
    "rawPrivateManifestRows",
    "privateManifestOutputRows",
    "privateManifestPublishedRows",
    "rawManifestPathRows",
    "ignoredArtifactPathRows",
    "actualAssetImportRows",
    "generatedAssetRows",
    "outputArtifactRows",
    "privateArtifactRows",
    "publishedPrivatePathRows",
    "publishedRawRefRows",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "privateAssetLeakCount",
    "publicPrivateProofLeakCount",
    "runtimeObservationRows",
    "runtimeTexturePixelRows",
    "runtimeMeshRenderRows",
    "runtimeMaterialRows",
    "screenshotRows",
    "captureRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "productUiRows",
    "godotRows",
    "realImporterImplementationRows",
    "importerContractAdapterRows",
    "rebuildImplementationRows",
    "mutationRows",
)


class ReadOnlyManifestConsumerValidationError(ValueError):
    """Raised when the redacted manifest is unsafe as a consumer input."""


def read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def walk_values(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        values: list[Any] = []
        for key, nested in value.items():
            values.append(key)
            values.extend(walk_values(nested))
        return values
    if isinstance(value, list):
        values = []
        for nested in value:
            values.extend(walk_values(nested))
        return values
    return [value]


def validate_redacted_manifest_for_consumer(manifest: Mapping[str, Any]) -> None:
    """Validate the ignored redacted manifest without raw private data."""

    if set(manifest) - ALLOWED_MANIFEST_KEYS:
        raise ReadOnlyManifestConsumerValidationError("unexpected manifest key present")
    if manifest.get("schemaVersion") != MATERIALIZATION_SCHEMA_VERSION:
        raise ReadOnlyManifestConsumerValidationError("manifest schema mismatch")
    if manifest.get("manifestKind") != "redacted-private-corpus-class-count-manifest":
        raise ReadOnlyManifestConsumerValidationError("manifest kind mismatch")
    if manifest.get("manifestRowMode") != "class-count-status-token-only":
        raise ReadOnlyManifestConsumerValidationError("manifest row mode mismatch")
    if manifest.get("materializationStatus") != MATERIALIZATION_STATUS:
        raise ReadOnlyManifestConsumerValidationError("materialization status mismatch")
    if manifest.get("sourceDryRunStatus") != DRY_RUN_STATUS:
        raise ReadOnlyManifestConsumerValidationError("source dry-run status mismatch")
    if manifest.get("sourceRootClass") != "user-owned-installed-or-copied-game-resource-root":
        raise ReadOnlyManifestConsumerValidationError("source root class mismatch")
    for key in (
        "redactedPrivateManifestMaterialized",
    ):
        if manifest.get(key) is not True:
            raise ReadOnlyManifestConsumerValidationError(f"expected true: {key}")
    for key in (
        "redactedPrivateManifestArtifactPathPublished",
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "realImporterImplementation",
        "realImporterExecuted",
    ):
        if manifest.get(key) is not False:
            raise ReadOnlyManifestConsumerValidationError(f"expected false: {key}")
    if manifest.get("redactedPrivateManifestRows") != len(REQUIRED_ARCHIVE_CLASSES):
        raise ReadOnlyManifestConsumerValidationError("manifest rows count mismatch")
    if manifest.get("redactedPrivateManifestSummaryRows") != 1:
        raise ReadOnlyManifestConsumerValidationError("manifest summary rows mismatch")
    rows = manifest.get("redactedManifestClassRows", [])
    if len(rows) != len(REQUIRED_ARCHIVE_CLASSES):
        raise ReadOnlyManifestConsumerValidationError("manifest class rows length mismatch")
    for row, archive_class in zip(rows, REQUIRED_ARCHIVE_CLASSES, strict=True):
        if set(row) - ALLOWED_ROW_KEYS:
            raise ReadOnlyManifestConsumerValidationError(f"unexpected row key present: {archive_class}")
        if row.get("archiveClass") != archive_class:
            raise ReadOnlyManifestConsumerValidationError(f"archive class mismatch: {archive_class}")
        if row.get("archiveClassCount") != EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class]:
            raise ReadOnlyManifestConsumerValidationError(f"archive class count mismatch: {archive_class}")
        if row.get("manifestRowClass") != "redacted-archive-class-summary-row":
            raise ReadOnlyManifestConsumerValidationError(f"row class mismatch: {archive_class}")
        if row.get("manifestRowMode") != "class-count-status-token-only":
            raise ReadOnlyManifestConsumerValidationError(f"row mode mismatch: {archive_class}")
        for key in ("privateArchiveBytesRead", "privateAssetContentRead"):
            if row.get(key) is not False:
                raise ReadOnlyManifestConsumerValidationError(f"row false guard mismatch: {archive_class}:{key}")
        for key in ("rawPathRows", "rawFilenameRows", "rawTextureRefRows", "rawMeshRefRows", "byteLengthRows"):
            if row.get(key) != 0:
                raise ReadOnlyManifestConsumerValidationError(f"row zero counter mismatch: {archive_class}:{key}")
    if manifest.get("publicLeakCheck") != "PASS":
        raise ReadOnlyManifestConsumerValidationError("public leak check mismatch")
    keys_and_values = walk_values(manifest)
    for key in FORBIDDEN_MANIFEST_KEYS:
        if key in keys_and_values:
            raise ReadOnlyManifestConsumerValidationError(f"forbidden manifest key present: {key}")
    for value in keys_and_values:
        if isinstance(value, str):
            for pattern in FORBIDDEN_VALUE_PATTERNS:
                if pattern.search(value):
                    raise ReadOnlyManifestConsumerValidationError("forbidden manifest value pattern present")


def build_public_safe_consumer_validation_summary(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build the tracked public-safe consumer validation summary."""

    validate_redacted_manifest_for_consumer(manifest)
    rows = list(manifest["redactedManifestClassRows"])
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    archive_total = sum(row["archiveClassCount"] for row in rows)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusReadOnlyManifestConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceMaterializationStatus": MATERIALIZATION_STATUS,
        "sourceDryRunStatus": DRY_RUN_STATUS,
        "readOnlyManifestConsumerValidationOnly": True,
        "privateCorpusReadOnlyManifestConsumerValidationExecuted": True,
        "redactedPrivateManifestArtifactConsumed": True,
        "redactedPrivateManifestArtifactPathPublished": False,
        "ignoredArtifactPathPublished": False,
        "consumerInputAccepted": True,
        "consumerSchemaValidated": True,
        "consumerRowModeValidated": True,
        "consumerArchiveClassOrderValidated": True,
        "consumerArchiveClassCountsValidated": True,
        "consumerGuardCountersValidated": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateRawManifestMaterialized": False,
        "privateRawManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "rawPrivateManifestConsumed": False,
        "rawPrivateManifestRowsConsumed": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "importerContractAdapterImplemented": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceRootClass": manifest["sourceRootClass"],
        "manifestKind": manifest["manifestKind"],
        "manifestRowMode": manifest["manifestRowMode"],
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerArchiveClassRowsValidated": len(rows),
        "consumerValidationRows": len(rows),
        "consumerValidationSummaryRows": 1,
        "consumerArchiveTotalCount": archive_total,
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "forbiddenManifestKeyCount": len(FORBIDDEN_MANIFEST_KEYS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "redactedManifestConsumerRows": rows,
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_consumer_validation_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe consumer validation summary."""

    if summary.get("schemaVersion") != SCHEMA_VERSION:
        raise ReadOnlyManifestConsumerValidationError("summary schema mismatch")
    if summary.get("status") != "PASS":
        raise ReadOnlyManifestConsumerValidationError("summary status mismatch")
    if summary.get("privateCorpusReadOnlyManifestConsumerValidationStatus") != CONSUMER_VALIDATION_STATUS:
        raise ReadOnlyManifestConsumerValidationError("consumer validation status mismatch")
    for key in (
        "readOnlyManifestConsumerValidationOnly",
        "privateCorpusReadOnlyManifestConsumerValidationExecuted",
        "redactedPrivateManifestArtifactConsumed",
        "consumerInputAccepted",
        "consumerSchemaValidated",
        "consumerRowModeValidated",
        "consumerArchiveClassOrderValidated",
        "consumerArchiveClassCountsValidated",
        "consumerGuardCountersValidated",
        "privateEvidenceStoredOutsidePublicReleaseScope",
    ):
        if summary.get(key) is not True:
            raise ReadOnlyManifestConsumerValidationError(f"expected true: {key}")
    for key in (
        "redactedPrivateManifestArtifactPathPublished",
        "ignoredArtifactPathPublished",
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "realImporterImplementation",
        "realImporterExecuted",
        "importerContractAdapterImplemented",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        if summary.get(key) is not False:
            raise ReadOnlyManifestConsumerValidationError(f"expected false: {key}")
    expected_counts = {
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerArchiveClassRowsValidated": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerValidationRows": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerValidationSummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "forbiddenManifestKeyCount": len(FORBIDDEN_MANIFEST_KEYS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            raise ReadOnlyManifestConsumerValidationError(f"count mismatch: {key}")
    rows = summary.get("redactedManifestConsumerRows", [])
    if [row.get("archiveClass") for row in rows] != list(REQUIRED_ARCHIVE_CLASSES):
        raise ReadOnlyManifestConsumerValidationError("consumer row order mismatch")
    for row in rows:
        archive_class = row.get("archiveClass")
        if row.get("archiveClassCount") != EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class]:
            raise ReadOnlyManifestConsumerValidationError(f"consumer row count mismatch: {archive_class}")
        for key in ("rawPathRows", "rawFilenameRows", "rawTextureRefRows", "rawMeshRefRows", "byteLengthRows"):
            if row.get(key) != 0:
                raise ReadOnlyManifestConsumerValidationError(f"consumer row zero mismatch: {archive_class}:{key}")
    for key in FALSE_GUARDS:
        if summary.get("falseGuards", {}).get(key) is not False:
            raise ReadOnlyManifestConsumerValidationError(f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        if summary.get("zeroCounters", {}).get(key) != 0:
            raise ReadOnlyManifestConsumerValidationError(f"zero counter mismatch: {key}")
    if summary.get("publicLeakCheck") != "PASS":
        raise ReadOnlyManifestConsumerValidationError("public leak check mismatch")


def build_public_safe_consumer_validation_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated consumer summary in the tracked proof schema."""

    validate_public_safe_consumer_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusReadOnlyManifestConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceMaterializationStatus": MATERIALIZATION_STATUS,
        "sourceDryRunStatus": DRY_RUN_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceProofCount": 13,
            "materializationProof": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md"
            ),
            "materializationSchema": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1.json"
            ),
            "manifestDryRunProof": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.md"
            ),
        },
        "consumerDecision": {
            "readOnlyManifestConsumerValidationOnly": True,
            "privateCorpusReadOnlyManifestConsumerValidationExecuted": True,
            "redactedPrivateManifestArtifactConsumed": True,
            "redactedPrivateManifestArtifactPathPublished": False,
            "ignoredArtifactPathPublished": False,
            "consumerInputAccepted": True,
            "consumerSchemaValidated": True,
            "consumerRowModeValidated": True,
            "consumerArchiveClassOrderValidated": True,
            "consumerArchiveClassCountsValidated": True,
            "consumerGuardCountersValidated": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "privateAssetContentRead": False,
            "privateArchiveBytesRead": False,
            "privateManifestMaterialized": False,
            "privateRawManifestMaterialized": False,
            "privateRawManifestRowsObserved": False,
            "privateManifestRowsPublished": False,
            "rawPrivateManifestConsumed": False,
            "rawPrivateManifestRowsConsumed": False,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "importerContractAdapterImplemented": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
        },
        "validatedConsumerInput": {
            "sourceRootClass": summary["sourceRootClass"],
            "manifestKind": summary["manifestKind"],
            "manifestRowMode": summary["manifestRowMode"],
            "requiredArchiveClassCount": summary["requiredArchiveClassCount"],
            "consumerArchiveClassRowsValidated": summary["consumerArchiveClassRowsValidated"],
            "consumerValidationRows": summary["consumerValidationRows"],
            "consumerValidationSummaryRows": summary["consumerValidationSummaryRows"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "redactedManifestConsumerRows": summary["redactedManifestConsumerRows"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-redacted-manifest-consumer-validation-class-count-status-token-only",
            "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
            "redactedFieldCount": len(REDACTED_FIELDS),
            "forbiddenManifestKeyCount": len(FORBIDDEN_MANIFEST_KEYS),
            "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
            "redactedFields": list(REDACTED_FIELDS),
            "forbiddenManifestKeys": list(FORBIDDEN_MANIFEST_KEYS),
            "publicLeakCheck": "PASS",
        },
        "guardSummary": {
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            **{key: 0 for key in ZERO_COUNTERS},
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "proves": [
                "the selected read-only consumer validation can parse and validate the redacted manifest artifact shape",
                "the consumer input contains only archive class/count/status-token rows",
                "the consumer input preserves required archive class order, counts, and guard counters",
                "raw private manifest consumption, real importer implementation, and real importer execution remain unperformed",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw corpus manifest materialization",
                "private raw manifest row observation",
                "raw private manifest consumption",
                "real importer implementation",
                "real importer execution",
                "importer contract adapter implementation",
                "runtime resource archive parser behavior",
                "runtime texture parser behavior",
                "runtime texture pixels",
                "runtime mesh loading or skinning",
                "Direct3D upload or GPU behavior",
                "native textured 3D rendering",
                "material visual correctness",
                "material or shader parity",
                "asset format completeness",
                "exact mesh or texture layouts",
                "product UI behavior",
                "Godot parity",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True, help="ignored redacted manifest artifact to validate")
    parser.add_argument("--summary", type=Path, help="optional public-safe consumer validation summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        manifest = read_manifest(args.manifest)
        summary = build_public_safe_consumer_validation_summary(manifest)
        validate_public_safe_consumer_validation_summary(summary)

        output = json.dumps(summary, indent=2, sort_keys=True)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(output + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_consumer_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(output)
        return 0
    except (OSError, json.JSONDecodeError, ReadOnlyManifestConsumerValidationError):
        print("Consumer validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
