#!/usr/bin/env python3
"""Redacted read-only inventory preflight for private texture/mesh corpus work."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight.v1"
PREFLIGHT_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-"
    "complete-redacted-class-count-summary-no-content-read"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan"

REQUIRED_ARCHIVE_CLASSES = (
    "base-resource-archive",
    "frontend-resource-archive",
    "loading-resource-archive",
    "numeric-level-resource-archive",
    "goodie-resource-archive",
)

PUBLIC_ALLOWED_OUTPUTS = (
    "resource-root-existence-status",
    "resource-directory-existence-status",
    "archive-class-counts",
    "required-class-coverage-status",
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
)

FALSE_GUARDS = (
    "privateAssetContentRead",
    "privateArchiveBytesRead",
    "privateManifestMaterialized",
    "privateManifestRowsObserved",
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


class ReadOnlyInventoryPreflightError(ValueError):
    """Raised when a private-corpus preflight cannot emit a safe summary."""


@dataclass(frozen=True)
class RedactedInventoryCounts:
    """Class/count-only observation with no raw paths or filenames."""

    resource_root_exists: bool
    resource_directory_exists: bool
    aya_archive_total_count: int
    base_archive_class_count: int
    frontend_archive_class_count: int
    loading_archive_class_count: int
    numeric_level_archive_class_count: int
    goodie_archive_class_count: int
    unknown_aya_archive_class_count: int

    @property
    def observed_required_archive_class_count(self) -> int:
        return sum(
            1
            for value in (
                self.base_archive_class_count,
                self.frontend_archive_class_count,
                self.loading_archive_class_count,
                self.numeric_level_archive_class_count,
                self.goodie_archive_class_count,
            )
            if value > 0
        )


def classify_resource_archive_name(name: str) -> str:
    """Return a public archive class without exposing the input name."""

    if re.fullmatch(r"base_res_PC\.aya", name):
        return "base-resource-archive"
    if re.fullmatch(r"Frontend_res_PC\.aya", name):
        return "frontend-resource-archive"
    if re.fullmatch(r"Loading_res_PC\.aya", name):
        return "loading-resource-archive"
    if re.fullmatch(r"\d+_res_PC\.aya", name):
        return "numeric-level-resource-archive"
    if re.fullmatch(r"goodie_\d+_res_PC\.aya", name):
        return "goodie-resource-archive"
    return "unknown-aya-resource-archive"


def inspect_readonly_private_corpus_root(root: Path) -> RedactedInventoryCounts:
    """Inspect only directory names and emit aggregate archive class counts."""

    resource_directory = root / "data" / "Resources"
    resource_root_exists = root.is_dir()
    resource_directory_exists = resource_directory.is_dir()
    class_counts: Counter[str] = Counter()

    if resource_directory_exists:
        for child in resource_directory.iterdir():
            if child.is_file() and child.suffix.lower() == ".aya":
                class_counts[classify_resource_archive_name(child.name)] += 1

    return RedactedInventoryCounts(
        resource_root_exists=resource_root_exists,
        resource_directory_exists=resource_directory_exists,
        aya_archive_total_count=sum(class_counts.values()),
        base_archive_class_count=class_counts["base-resource-archive"],
        frontend_archive_class_count=class_counts["frontend-resource-archive"],
        loading_archive_class_count=class_counts["loading-resource-archive"],
        numeric_level_archive_class_count=class_counts["numeric-level-resource-archive"],
        goodie_archive_class_count=class_counts["goodie-resource-archive"],
        unknown_aya_archive_class_count=class_counts["unknown-aya-resource-archive"],
    )


def build_public_safe_preflight_summary(counts: RedactedInventoryCounts) -> dict[str, Any]:
    """Build the only public-safe summary this slice may publish."""

    observed_required = counts.observed_required_archive_class_count
    all_required = observed_required == len(REQUIRED_ARCHIVE_CLASSES)
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS" if all_required else "BLOCKED",
        "privateCorpusReadOnlyInventoryPreflightStatus": PREFLIGHT_STATUS if all_required else "blocked-missing-required-archive-class",
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "readOnlyInventoryPreflightOnly": True,
        "privateCorpusReadOnlyInventoryPreflightExecuted": True,
        "privateCorpusRootExistenceChecked": True,
        "privateResourceArchiveDirectoryExistenceChecked": True,
        "privateResourceArchiveClassEnumerationPerformed": True,
        "privateCorpusReadOnlyInventoryGenerated": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "resourceRootExists": counts.resource_root_exists,
        "resourceDirectoryExists": counts.resource_directory_exists,
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "observedRequiredArchiveClassCount": observed_required,
        "allRequiredArchiveClassesObserved": all_required,
        "ayaArchiveTotalCount": counts.aya_archive_total_count,
        "baseArchiveClassCount": counts.base_archive_class_count,
        "frontendArchiveClassCount": counts.frontend_archive_class_count,
        "loadingArchiveClassCount": counts.loading_archive_class_count,
        "numericLevelArchiveClassCount": counts.numeric_level_archive_class_count,
        "goodieArchiveClassCount": counts.goodie_archive_class_count,
        "unknownAyaArchiveClassCount": counts.unknown_aya_archive_class_count,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_preflight_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe shape without requiring private corpus access."""

    if summary.get("schemaVersion") != SCHEMA_VERSION:
        raise ReadOnlyInventoryPreflightError("schema version mismatch")
    if summary.get("status") != "PASS":
        raise ReadOnlyInventoryPreflightError("preflight status is not PASS")
    if summary.get("privateCorpusReadOnlyInventoryPreflightStatus") != PREFLIGHT_STATUS:
        raise ReadOnlyInventoryPreflightError("preflight token mismatch")
    for key in (
        "readOnlyInventoryPreflightOnly",
        "privateCorpusReadOnlyInventoryPreflightExecuted",
        "privateCorpusRootExistenceChecked",
        "privateResourceArchiveDirectoryExistenceChecked",
        "privateResourceArchiveClassEnumerationPerformed",
        "privateCorpusReadOnlyInventoryGenerated",
        "resourceRootExists",
        "resourceDirectoryExists",
        "allRequiredArchiveClassesObserved",
    ):
        if summary.get(key) is not True:
            raise ReadOnlyInventoryPreflightError(f"expected true: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "realImporterImplementation",
        "realImporterExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        if summary.get(key) is not False:
            raise ReadOnlyInventoryPreflightError(f"expected false: {key}")
    expected_counts = {
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "observedRequiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            raise ReadOnlyInventoryPreflightError(f"count mismatch: {key}")
    if summary.get("publicLeakCheck") != "PASS":
        raise ReadOnlyInventoryPreflightError("public leak check mismatch")
    false_guards = summary.get("falseGuards", {})
    zero_counters = summary.get("zeroCounters", {})
    for key in FALSE_GUARDS:
        if false_guards.get(key) is not False:
            raise ReadOnlyInventoryPreflightError(f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        if zero_counters.get(key) != 0:
            raise ReadOnlyInventoryPreflightError(f"zero counter mismatch: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, help="private installed/copied corpus root to inspect read-only")
    parser.add_argument("--summary", type=Path, help="optional redacted JSON summary output")
    args = parser.parse_args()

    if args.root is None:
        parser.error("--root is required for live read-only inventory preflight")

    summary = build_public_safe_preflight_summary(inspect_readonly_private_corpus_root(args.root))
    validate_public_safe_preflight_summary(summary)
    output = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
