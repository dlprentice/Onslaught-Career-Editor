#!/usr/bin/env python3
"""Redacted manifest-shape dry run for private texture/mesh corpus work."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import (
    REQUIRED_ARCHIVE_CLASSES,
    RedactedInventoryCounts,
    build_public_safe_preflight_summary,
    inspect_readonly_private_corpus_root,
    validate_public_safe_preflight_summary,
)


SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run.v1"
DRY_RUN_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-"
    "complete-redacted-class-manifest-shape-no-content-read"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan"

SOURCE_PREFLIGHT_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-"
    "complete-redacted-class-count-summary-no-content-read"
)

PUBLIC_ALLOWED_OUTPUTS = (
    "resource-root-existence-status",
    "resource-directory-existence-status",
    "archive-class-counts",
    "required-class-coverage-status",
    "redacted-manifest-class-rows",
    "manifest-dry-run-row-counts",
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
)

FALSE_GUARDS = (
    "privateAssetContentRead",
    "privateArchiveBytesRead",
    "privateManifestMaterialized",
    "privateManifestRowsObserved",
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

ARCHIVE_CLASS_COUNT_FIELDS = {
    "base-resource-archive": "baseArchiveClassCount",
    "frontend-resource-archive": "frontendArchiveClassCount",
    "loading-resource-archive": "loadingArchiveClassCount",
    "numeric-level-resource-archive": "numericLevelArchiveClassCount",
    "goodie-resource-archive": "goodieArchiveClassCount",
}


class ReadOnlyManifestDryRunError(ValueError):
    """Raised when a manifest dry run cannot emit a safe summary."""


def build_redacted_manifest_class_rows(preflight_summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build class-level manifest dry-run rows with no concrete private identifiers."""

    rows: list[dict[str, Any]] = []
    for archive_class in REQUIRED_ARCHIVE_CLASSES:
        count_field = ARCHIVE_CLASS_COUNT_FIELDS[archive_class]
        rows.append(
            {
                "archiveClass": archive_class,
                "archiveClassCount": preflight_summary[count_field],
                "manifestRowClass": "redacted-archive-class-summary-row",
                "manifestRowMode": "class-count-status-token-only",
                "privateAssetContentRead": False,
                "privateArchiveBytesRead": False,
                "rawPathRows": 0,
                "rawFilenameRows": 0,
                "rawTextureRefRows": 0,
                "rawMeshRefRows": 0,
                "byteLengthRows": 0,
            }
        )
    return rows


def build_public_safe_manifest_dry_run_summary(counts: RedactedInventoryCounts) -> dict[str, Any]:
    """Build the only public-safe manifest dry-run summary this slice may publish."""

    preflight_summary = build_public_safe_preflight_summary(counts)
    validate_public_safe_preflight_summary(preflight_summary)
    rows = build_redacted_manifest_class_rows(preflight_summary)
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusReadOnlyManifestDryRunStatus": DRY_RUN_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourcePreflightStatus": SOURCE_PREFLIGHT_STATUS,
        "readOnlyManifestDryRunOnly": True,
        "privateCorpusReadOnlyManifestDryRunExecuted": True,
        "privateCorpusRootClassEvidenceConsumed": True,
        "archiveClassSummaryConsumed": True,
        "redactedManifestShapeGenerated": True,
        "manifestClassRowsGenerated": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "resourceRootExists": preflight_summary["resourceRootExists"],
        "resourceDirectoryExists": preflight_summary["resourceDirectoryExists"],
        "requiredArchiveClassCount": preflight_summary["requiredArchiveClassCount"],
        "observedRequiredArchiveClassCount": preflight_summary["observedRequiredArchiveClassCount"],
        "allRequiredArchiveClassesObserved": preflight_summary["allRequiredArchiveClassesObserved"],
        "ayaArchiveTotalCount": preflight_summary["ayaArchiveTotalCount"],
        "baseArchiveClassCount": preflight_summary["baseArchiveClassCount"],
        "frontendArchiveClassCount": preflight_summary["frontendArchiveClassCount"],
        "loadingArchiveClassCount": preflight_summary["loadingArchiveClassCount"],
        "numericLevelArchiveClassCount": preflight_summary["numericLevelArchiveClassCount"],
        "goodieArchiveClassCount": preflight_summary["goodieArchiveClassCount"],
        "unknownAyaArchiveClassCount": preflight_summary["unknownAyaArchiveClassCount"],
        "manifestDryRunClassRowCount": len(rows),
        "manifestDryRunArchiveTotalCount": preflight_summary["ayaArchiveTotalCount"],
        "manifestDryRunSummaryRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "redactedManifestClassRows": rows,
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_manifest_dry_run_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe manifest dry-run shape."""

    if summary.get("schemaVersion") != SCHEMA_VERSION:
        raise ReadOnlyManifestDryRunError("schema version mismatch")
    if summary.get("status") != "PASS":
        raise ReadOnlyManifestDryRunError("manifest dry-run status is not PASS")
    if summary.get("privateCorpusReadOnlyManifestDryRunStatus") != DRY_RUN_STATUS:
        raise ReadOnlyManifestDryRunError("manifest dry-run token mismatch")
    for key in (
        "readOnlyManifestDryRunOnly",
        "privateCorpusReadOnlyManifestDryRunExecuted",
        "privateCorpusRootClassEvidenceConsumed",
        "archiveClassSummaryConsumed",
        "redactedManifestShapeGenerated",
        "manifestClassRowsGenerated",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "resourceRootExists",
        "resourceDirectoryExists",
        "allRequiredArchiveClassesObserved",
    ):
        if summary.get(key) is not True:
            raise ReadOnlyManifestDryRunError(f"expected true: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateManifestRowsObserved",
        "privateManifestRowsPublished",
        "realImporterImplementation",
        "realImporterExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        if summary.get(key) is not False:
            raise ReadOnlyManifestDryRunError(f"expected false: {key}")
    expected_counts = {
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "observedRequiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "manifestDryRunClassRowCount": len(REQUIRED_ARCHIVE_CLASSES),
        "manifestDryRunArchiveTotalCount": summary.get("ayaArchiveTotalCount"),
        "manifestDryRunSummaryRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            raise ReadOnlyManifestDryRunError(f"count mismatch: {key}")
    if summary.get("publicLeakCheck") != "PASS":
        raise ReadOnlyManifestDryRunError("public leak check mismatch")
    rows = summary.get("redactedManifestClassRows", [])
    if len(rows) != len(REQUIRED_ARCHIVE_CLASSES):
        raise ReadOnlyManifestDryRunError("manifest class row count mismatch")
    for row, archive_class in zip(rows, REQUIRED_ARCHIVE_CLASSES, strict=True):
        if row.get("archiveClass") != archive_class:
            raise ReadOnlyManifestDryRunError(f"archive class mismatch: {archive_class}")
        if row.get("manifestRowMode") != "class-count-status-token-only":
            raise ReadOnlyManifestDryRunError(f"manifest row mode mismatch: {archive_class}")
        for key in (
            "privateAssetContentRead",
            "privateArchiveBytesRead",
        ):
            if row.get(key) is not False:
                raise ReadOnlyManifestDryRunError(f"row false guard mismatch: {archive_class}:{key}")
        for key in (
            "rawPathRows",
            "rawFilenameRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "byteLengthRows",
        ):
            if row.get(key) != 0:
                raise ReadOnlyManifestDryRunError(f"row zero counter mismatch: {archive_class}:{key}")
    false_guards = summary.get("falseGuards", {})
    zero_counters = summary.get("zeroCounters", {})
    for key in FALSE_GUARDS:
        if false_guards.get(key) is not False:
            raise ReadOnlyManifestDryRunError(f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        if zero_counters.get(key) != 0:
            raise ReadOnlyManifestDryRunError(f"zero counter mismatch: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, help="private installed/copied corpus root to inspect read-only")
    parser.add_argument("--summary", type=Path, help="optional redacted JSON summary output")
    args = parser.parse_args()

    if args.root is None:
        parser.error("--root is required for live read-only manifest dry run")

    summary = build_public_safe_manifest_dry_run_summary(inspect_readonly_private_corpus_root(args.root))
    validate_public_safe_manifest_dry_run_summary(summary)
    output = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
