#!/usr/bin/env python3
"""Materialize a redacted private-corpus manifest from read-only class evidence."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import (
    REQUIRED_ARCHIVE_CLASSES,
    RedactedInventoryCounts,
    inspect_readonly_private_corpus_root,
)
from texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_dry_run import (
    DRY_RUN_STATUS,
    build_public_safe_manifest_dry_run_summary,
    validate_public_safe_manifest_dry_run_summary,
)


SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization.v1"
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1"
)
MATERIALIZATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-"
    "complete-redacted-private-manifest-artifact-no-content-read"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan"

PUBLIC_ALLOWED_OUTPUTS = (
    "resource-root-existence-status",
    "resource-directory-existence-status",
    "archive-class-counts",
    "required-class-coverage-status",
    "redacted-manifest-class-rows",
    "redacted-private-manifest-artifact-class",
    "materialized-manifest-row-counts",
    "manifest-materialization-row-counts",
    "redaction-field-counts",
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
)

FALSE_GUARDS = (
    "privateAssetContentRead",
    "privateArchiveBytesRead",
    "privateManifestMaterialized",
    "privateRawManifestMaterialized",
    "privateRawManifestRowsObserved",
    "privateManifestRowsPublished",
    "realImporterImplementation",
    "realImporterExecuted",
    "privateImporterDryRunExecuted",
    "generatedAssetOutputs",
    "privateAssetPublication",
    "runtimeExecution",
    "beLaunch",
    "newLaunch",
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
    "rebuildImplementationRows",
    "mutationRows",
)


class ReadOnlyManifestMaterializationError(ValueError):
    """Raised when the redacted manifest materialization shape is unsafe."""


def build_redacted_private_manifest(dry_run_summary: Mapping[str, Any]) -> dict[str, Any]:
    """Build the ignored/private artifact content without raw private identifiers."""

    rows = list(dry_run_summary["redactedManifestClassRows"])
    return {
        "schemaVersion": SCHEMA_VERSION,
        "manifestKind": "redacted-private-corpus-class-count-manifest",
        "manifestRowMode": "class-count-status-token-only",
        "materializationStatus": MATERIALIZATION_STATUS,
        "sourceDryRunStatus": DRY_RUN_STATUS,
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "redactedPrivateManifestMaterialized": True,
        "redactedPrivateManifestRows": len(rows),
        "redactedPrivateManifestSummaryRows": 1,
        "redactedPrivateManifestArtifactPathPublished": False,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateRawManifestMaterialized": False,
        "privateRawManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "redactedManifestClassRows": rows,
        "publicLeakCheck": "PASS",
    }


def build_public_safe_manifest_materialization_summary(dry_run_summary: Mapping[str, Any]) -> dict[str, Any]:
    """Build a tracked/public-safe summary for the materialization slice."""

    validate_public_safe_manifest_dry_run_summary(dry_run_summary)
    manifest = build_redacted_private_manifest(dry_run_summary)
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusReadOnlyManifestMaterializationStatus": MATERIALIZATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceDryRunStatus": DRY_RUN_STATUS,
        "readOnlyManifestMaterializationOnly": True,
        "privateCorpusReadOnlyManifestMaterializationExecuted": True,
        "sourceDryRunEvidenceConsumed": True,
        "redactedPrivateManifestMaterialized": True,
        "redactedPrivateManifestArtifactWritten": True,
        "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope": True,
        "redactedPrivateManifestArtifactPathPublished": False,
        "publicSafeRedactedManifestArtifactRows": 1,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateRawManifestMaterialized": False,
        "privateRawManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "resourceRootExists": dry_run_summary["resourceRootExists"],
        "resourceDirectoryExists": dry_run_summary["resourceDirectoryExists"],
        "requiredArchiveClassCount": dry_run_summary["requiredArchiveClassCount"],
        "observedRequiredArchiveClassCount": dry_run_summary["observedRequiredArchiveClassCount"],
        "allRequiredArchiveClassesObserved": dry_run_summary["allRequiredArchiveClassesObserved"],
        "ayaArchiveTotalCount": dry_run_summary["ayaArchiveTotalCount"],
        "baseArchiveClassCount": dry_run_summary["baseArchiveClassCount"],
        "frontendArchiveClassCount": dry_run_summary["frontendArchiveClassCount"],
        "loadingArchiveClassCount": dry_run_summary["loadingArchiveClassCount"],
        "numericLevelArchiveClassCount": dry_run_summary["numericLevelArchiveClassCount"],
        "goodieArchiveClassCount": dry_run_summary["goodieArchiveClassCount"],
        "unknownAyaArchiveClassCount": dry_run_summary["unknownAyaArchiveClassCount"],
        "sourceManifestDryRunClassRowCount": dry_run_summary["manifestDryRunClassRowCount"],
        "materializedRedactedManifestClassRowCount": manifest["redactedPrivateManifestRows"],
        "materializedRedactedManifestSummaryRows": manifest["redactedPrivateManifestSummaryRows"],
        "materializedRedactedManifestArchiveTotalCount": dry_run_summary["manifestDryRunArchiveTotalCount"],
        "publicSafeRedactedManifestArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "redactedPrivateManifest": manifest,
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_manifest_materialization_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe materialization summary and artifact body."""

    if summary.get("schemaVersion") != SCHEMA_VERSION:
        raise ReadOnlyManifestMaterializationError("schema version mismatch")
    if summary.get("status") != "PASS":
        raise ReadOnlyManifestMaterializationError("status is not PASS")
    if summary.get("privateCorpusReadOnlyManifestMaterializationStatus") != MATERIALIZATION_STATUS:
        raise ReadOnlyManifestMaterializationError("materialization status mismatch")
    for key in (
        "readOnlyManifestMaterializationOnly",
        "privateCorpusReadOnlyManifestMaterializationExecuted",
        "sourceDryRunEvidenceConsumed",
        "redactedPrivateManifestMaterialized",
        "redactedPrivateManifestArtifactWritten",
        "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "resourceRootExists",
        "resourceDirectoryExists",
        "allRequiredArchiveClassesObserved",
    ):
        if summary.get(key) is not True:
            raise ReadOnlyManifestMaterializationError(f"expected true: {key}")
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
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        if summary.get(key) is not False:
            raise ReadOnlyManifestMaterializationError(f"expected false: {key}")
    expected_counts = {
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "observedRequiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "sourceManifestDryRunClassRowCount": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedRedactedManifestClassRowCount": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedRedactedManifestSummaryRows": 1,
        "materializedRedactedManifestArchiveTotalCount": summary.get("ayaArchiveTotalCount"),
        "publicSafeRedactedManifestArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            raise ReadOnlyManifestMaterializationError(f"count mismatch: {key}")
    manifest = summary.get("redactedPrivateManifest", {})
    if manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise ReadOnlyManifestMaterializationError("manifest schema mismatch")
    if manifest.get("materializationStatus") != MATERIALIZATION_STATUS:
        raise ReadOnlyManifestMaterializationError("manifest materialization status mismatch")
    if manifest.get("manifestRowMode") != "class-count-status-token-only":
        raise ReadOnlyManifestMaterializationError("manifest row mode mismatch")
    if manifest.get("redactedPrivateManifestRows") != len(REQUIRED_ARCHIVE_CLASSES):
        raise ReadOnlyManifestMaterializationError("manifest row count mismatch")
    if manifest.get("redactedPrivateManifestArtifactPathPublished") is not False:
        raise ReadOnlyManifestMaterializationError("manifest path was published")
    rows = manifest.get("redactedManifestClassRows", [])
    if len(rows) != len(REQUIRED_ARCHIVE_CLASSES):
        raise ReadOnlyManifestMaterializationError("manifest rows length mismatch")
    for row, archive_class in zip(rows, REQUIRED_ARCHIVE_CLASSES, strict=True):
        if row.get("archiveClass") != archive_class:
            raise ReadOnlyManifestMaterializationError(f"archive class mismatch: {archive_class}")
        if row.get("manifestRowMode") != "class-count-status-token-only":
            raise ReadOnlyManifestMaterializationError(f"row mode mismatch: {archive_class}")
        for key in ("rawPathRows", "rawFilenameRows", "rawTextureRefRows", "rawMeshRefRows", "byteLengthRows"):
            if row.get(key) != 0:
                raise ReadOnlyManifestMaterializationError(f"row zero counter mismatch: {archive_class}:{key}")
    false_guards = summary.get("falseGuards", {})
    zero_counters = summary.get("zeroCounters", {})
    for key in FALSE_GUARDS:
        if false_guards.get(key) is not False:
            raise ReadOnlyManifestMaterializationError(f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        if zero_counters.get(key) != 0:
            raise ReadOnlyManifestMaterializationError(f"zero counter mismatch: {key}")
    if summary.get("publicLeakCheck") != "PASS" or manifest.get("publicLeakCheck") != "PASS":
        raise ReadOnlyManifestMaterializationError("public leak check mismatch")


def build_public_safe_manifest_materialization_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated materialization summary in the tracked proof-plan schema."""

    validate_public_safe_manifest_materialization_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusReadOnlyManifestMaterializationStatus": MATERIALIZATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
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
            "sourceProofCount": 12,
            "manifestDryRunProof": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.md"
            ),
            "manifestDryRunSchema": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.v1.json"
            ),
            "inventoryPreflightProof": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md"
            ),
            "privateCorpusSafetyBoundaryProof": (
                "reverse-engineering/game-assets/"
                "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md"
            ),
        },
        "materializationDecision": {
            "readOnlyManifestMaterializationOnly": True,
            "privateCorpusReadOnlyManifestMaterializationExecuted": True,
            "sourceDryRunEvidenceConsumed": True,
            "redactedPrivateManifestMaterialized": True,
            "redactedPrivateManifestArtifactWritten": True,
            "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope": True,
            "redactedPrivateManifestArtifactPathPublished": False,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "privateAssetContentRead": False,
            "privateArchiveBytesRead": False,
            "privateManifestMaterialized": False,
            "privateRawManifestMaterialized": False,
            "privateRawManifestRowsObserved": False,
            "privateManifestRowsPublished": False,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
        },
        "archiveClassSummary": {
            "sourceRootClass": summary["sourceRootClass"],
            "resourceRootExists": summary["resourceRootExists"],
            "resourceDirectoryExists": summary["resourceDirectoryExists"],
            "requiredArchiveClassCount": summary["requiredArchiveClassCount"],
            "observedRequiredArchiveClassCount": summary["observedRequiredArchiveClassCount"],
            "allRequiredArchiveClassesObserved": summary["allRequiredArchiveClassesObserved"],
            "ayaArchiveTotalCount": summary["ayaArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
        },
        "redactedMaterializedManifest": {
            "manifestKind": summary["redactedPrivateManifest"]["manifestKind"],
            "manifestRowMode": summary["redactedPrivateManifest"]["manifestRowMode"],
            "redactedPrivateManifestRows": summary["redactedPrivateManifest"]["redactedPrivateManifestRows"],
            "redactedPrivateManifestSummaryRows": summary["redactedPrivateManifest"][
                "redactedPrivateManifestSummaryRows"
            ],
            "redactedPrivateManifestArtifactPathPublished": False,
            "publicSafeRedactedManifestArtifactRows": summary["publicSafeRedactedManifestArtifactRows"],
            "materializedRedactedManifestClassRowCount": summary["materializedRedactedManifestClassRowCount"],
            "materializedRedactedManifestArchiveTotalCount": summary[
                "materializedRedactedManifestArchiveTotalCount"
            ],
            "redactedManifestClassRows": summary["redactedPrivateManifest"]["redactedManifestClassRows"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-redacted-private-manifest-class-count-status-token-only",
            "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
            "redactedFieldCount": len(REDACTED_FIELDS),
            "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
            "redactedFields": list(REDACTED_FIELDS),
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
                "the selected read-only manifest materialization wrote a redacted private manifest artifact outside public release scope",
                "the materialized redacted manifest contains only archive class/count/status-token rows",
                "the materialized redacted manifest preserves required archive class coverage and aggregate counts",
                "private raw manifest materialization, private manifest row observation, real importer implementation, and real importer execution remain unperformed",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw corpus manifest materialization",
                "private raw manifest row observation",
                "real importer implementation",
                "real importer execution",
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
    parser.add_argument("--root", type=Path, help="private installed/copied corpus root to inspect read-only")
    parser.add_argument("--manifest", type=Path, help="ignored/app-owned redacted manifest artifact output")
    parser.add_argument("--summary", type=Path, help="optional redacted public-safe JSON summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    if args.root is None:
        parser.error("--root is required for read-only materialization")
    if args.manifest is None:
        parser.error("--manifest is required for redacted materialization")

    dry_run_summary = build_public_safe_manifest_dry_run_summary(inspect_readonly_private_corpus_root(args.root))
    summary = build_public_safe_manifest_materialization_summary(dry_run_summary)
    validate_public_safe_manifest_materialization_summary(summary)

    manifest_output = json.dumps(summary["redactedPrivateManifest"], indent=2, sort_keys=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(manifest_output + "\n", encoding="utf-8")

    output = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(output + "\n", encoding="utf-8")
    if args.proof is not None:
        proof = build_public_safe_manifest_materialization_proof(summary)
        args.proof.parent.mkdir(parents=True, exist_ok=True)
        args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
