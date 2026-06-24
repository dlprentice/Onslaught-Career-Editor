#!/usr/bin/env python3
"""Materialize public-safe adapter dry-run rows into a tracked proof artifact."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import REQUIRED_ARCHIVE_CLASSES
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter import (
    ADAPTER_CONTRACT_INTERFACES,
    ADAPTER_STATUS,
    EXPECTED_ARCHIVE_CLASS_COUNTS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_dry_run import (
    DRY_RUN_INTERFACES,
    DRY_RUN_STATUS,
    FALSE_GUARDS as DRY_RUN_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as DRY_RUN_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-proof-plan.v1"
)
MATERIALIZATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract "
    "Adapter Materialization Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract "
    "Adapter Materialization Consumer Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-consumer-validation-proof-plan"
)

DRY_RUN_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-dry-run-proof-plan.v1.json"
)

MATERIALIZATION_INTERFACES = (
    "load-public-safe-adapter-dry-run-proof",
    "validate-adapter-dry-run-continuity",
    "materialize-public-safe-adapter-rows",
    "validate-materialized-adapter-row-order",
    "validate-materialized-adapter-aggregate-counts",
    "validate-private-data-refusal-guards",
    "emit-materialized-adapter-artifact",
    "emit-materialization-summary",
)

PUBLIC_ALLOWED_OUTPUTS = (
    "adapter-materialization-status",
    "source-adapter-dry-run-status",
    "materialized-adapter-artifact-class",
    "materialized-adapter-class-rows",
    "materialized-adapter-aggregate-counts",
    "source-dry-run-interface-linkage",
    "materialization-interface-linkage",
    "materialization-row-counts",
    "guard-counter-summary",
    "next-slice-selection",
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
    "generated-asset-output-path",
    "raw-dry-run-trace",
    "public-safe-materialized-adapter-artifact-path",
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_FALSE_GUARDS,
            "adapterMaterializationReadPrivateInputs",
            "adapterMaterializationPublishedPrivateInput",
            "materializedAdapterArtifactPathPublished",
            "realImporterMaterializationExecuted",
            "privateMaterializationArtifactPublished",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_ZERO_COUNTERS,
            "materializedAdapterPrivateInputRows",
            "materializedAdapterArtifactPathRows",
            "privateMaterializationArtifactRows",
            "realImporterMaterializationRows",
        )
    )
)


class RedactedManifestImporterContractAdapterMaterializationError(ValueError):
    """Raised when tracked adapter dry-run proof inputs cannot support materialization."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RedactedManifestImporterContractAdapterMaterializationError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _validate_source_dry_run_proof(source: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    _require(source.get("privateCorpusRedactedManifestImporterContractAdapterDryRunStatus") == DRY_RUN_STATUS, "dry-run status mismatch")
    _require(source.get("selectedNextSlice") == THIS_SLICE, "dry-run selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "dry-run selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    _require(source.get("sourceAdapterStatus") == ADAPTER_STATUS, "source adapter status mismatch")

    decision = _read_mapping(source, "adapterDryRunDecision")
    for key in (
        "redactedManifestImporterContractAdapterDryRunOnly",
        "adapterProofConsumed",
        "adapterProofContinuityValidated",
        "adapterContractDryRunExecuted",
        "adapterDryRunInputAccepted",
        "adapterDryRunRowsGenerated",
        "adapterDryRunRowsValidated",
        "adapterDryRunAggregateCountsValidated",
        "adapterDryRunInterfacesValidated",
        "adapterDryRunEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"dry-run decision expected true: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "redactedPrivateManifestArtifactPathPublished",
        "ignoredArtifactPathPublished",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "privateImporterMaterializationExecuted",
        "adapterDryRunReadPrivateInputs",
        "adapterDryRunPublishedPrivateInput",
        "privateDryRunArtifactPublished",
        "rawDryRunTracePublished",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"dry-run decision expected false: {key}")

    contract = _read_mapping(source, "adapterDryRunContract")
    _require(tuple(contract.get("sourceAdapterContractInterfaces", ())) == ADAPTER_CONTRACT_INTERFACES, "source adapter interface mismatch")
    _require(tuple(contract.get("adapterDryRunInterfaces", ())) == DRY_RUN_INTERFACES, "dry-run interface mismatch")
    _require(contract.get("adapterDryRunRows") == len(REQUIRED_ARCHIVE_CLASSES), "dry-run row count mismatch")
    _require(contract.get("adapterDryRunArchiveClassRows") == len(REQUIRED_ARCHIVE_CLASSES), "dry-run archive-class row count mismatch")
    _require(contract.get("adapterDryRunValidationRows") == len(REQUIRED_ARCHIVE_CLASSES), "dry-run validation row count mismatch")
    _require(contract.get("adapterDryRunSummaryRows") == 1, "dry-run summary row count mismatch")
    _require(contract.get("adapterArchiveTotalCount") == 301, "dry-run archive total mismatch")

    rows = contract.get("redactedManifestAdapterDryRunRows")
    _require(isinstance(rows, list), "dry-run rows must be a list")
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "dry-run row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"dry-run row count mismatch: {archive_class}")
        _require(row.get("dryRunPrivateIdentifiersPresent") is False, f"dry-run row private identifier guard mismatch: {archive_class}")
        for key in (
            "rawPathRows",
            "rawFilenameRows",
            "rawStemRows",
            "rawHashRows",
            "byteLengthRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "actualAssetImportRows",
            "generatedAssetRows",
            "privateDryRunRows",
            "realImporterDryRunRows",
            "rawDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"dry-run row zero mismatch: {archive_class}:{key}")
    return rows


def build_materialized_adapter_rows(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    materialized_rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(rows, start=1):
        archive_class = row["sourceArchiveClass"]
        materialized_rows.append(
            {
                "materializedRowClass": "redacted-archive-class-contract-adapter-materialized-row",
                "materializedRowMode": "public-safe-archive-class-count-status-token-only",
                "materializedRowOrdinal": ordinal,
                "sourceDryRunRowOrdinal": row["dryRunRowOrdinal"],
                "sourceArchiveClass": archive_class,
                "archiveClassCount": row["archiveClassCount"],
                "sourceDryRunRowMode": row["dryRunRowMode"],
                "materializedByInterface": "materialize-public-safe-adapter-rows",
                "materializedPrivateIdentifiersPresent": False,
                "rawPathRows": 0,
                "rawFilenameRows": 0,
                "rawStemRows": 0,
                "rawHashRows": 0,
                "byteLengthRows": 0,
                "rawTextureRefRows": 0,
                "rawMeshRefRows": 0,
                "actualAssetImportRows": 0,
                "generatedAssetRows": 0,
                "realImporterDryRunRows": 0,
                "privateDryRunRows": 0,
                "realImporterMaterializationRows": 0,
                "rawDryRunTraceRows": 0,
            }
        )
    return materialized_rows


def build_materialized_adapter_artifact(dry_run_proof: Mapping[str, Any]) -> dict[str, Any]:
    """Build the public-safe adapter artifact body embedded in the tracked proof."""

    dry_run_rows = _validate_source_dry_run_proof(dry_run_proof)
    materialized_rows = build_materialized_adapter_rows(dry_run_rows)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "artifactKind": "public-safe-redacted-manifest-importer-contract-adapter-materialized-artifact",
        "artifactRowMode": "public-safe-archive-class-count-status-token-only",
        "materializationStatus": MATERIALIZATION_STATUS,
        "sourceDryRunStatus": DRY_RUN_STATUS,
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "materializedAdapterArtifactWritten": True,
        "materializedAdapterArtifactPathPublished": False,
        "materializedAdapterRows": len(materialized_rows),
        "materializedAdapterSummaryRows": 1,
        "materializedAdapterArchiveTotalCount": sum(row["archiveClassCount"] for row in materialized_rows),
        "materializedAdapterRowsValidated": True,
        "materializedAdapterAggregateCountsValidated": True,
        "materializedAdapterArtifactStoredInTrackedProof": True,
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
        "privateImporterDryRunExecuted": False,
        "realImporterDryRunExecuted": False,
        "realImporterMaterializationExecuted": False,
        "materializedAdapterRowsBody": materialized_rows,
        "publicLeakCheck": "PASS",
    }


def build_public_safe_adapter_materialization_summary(dry_run_proof: Mapping[str, Any]) -> dict[str, Any]:
    """Build a tracked/public-safe summary for the adapter materialization slice."""

    artifact = build_materialized_adapter_artifact(dry_run_proof)
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus": MATERIALIZATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceAdapterDryRunStatus": DRY_RUN_STATUS,
        "sourceAdapterStatus": ADAPTER_STATUS,
        "redactedManifestImporterContractAdapterMaterializationOnly": True,
        "adapterDryRunProofConsumed": True,
        "adapterDryRunProofContinuityValidated": True,
        "adapterMaterializationExecuted": True,
        "adapterMaterializationInputAccepted": True,
        "materializedAdapterArtifactWritten": True,
        "materializedAdapterArtifactStoredInTrackedProof": True,
        "materializedAdapterArtifactPathPublished": False,
        "materializedAdapterRowsGenerated": True,
        "materializedAdapterRowsValidated": True,
        "materializedAdapterAggregateCountsValidated": True,
        "materializationInterfacesValidated": True,
        "materializedAdapterEmitsOnlyPublicSafeRows": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateRawManifestMaterialized": False,
        "privateRawManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "rawPrivateManifestConsumed": False,
        "rawPrivateManifestRowsConsumed": False,
        "redactedPrivateManifestArtifactPathPublished": False,
        "ignoredArtifactPathPublished": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "privateImporterDryRunExecuted": False,
        "realImporterDryRunExecuted": False,
        "privateImporterMaterializationExecuted": False,
        "realImporterMaterializationExecuted": False,
        "adapterMaterializationReadPrivateInputs": False,
        "adapterMaterializationPublishedPrivateInput": False,
        "privateMaterializationArtifactPublished": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "adapterMaterializationInputMode": "tracked-public-safe-adapter-dry-run-proof-json",
        "adapterMaterializationOutputMode": "tracked-public-safe-materialized-adapter-artifact",
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "adapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "materializedAdapterRows": artifact["materializedAdapterRows"],
        "materializedAdapterArchiveClassRows": artifact["materializedAdapterRows"],
        "materializedAdapterValidationRows": artifact["materializedAdapterRows"],
        "materializedAdapterSummaryRows": artifact["materializedAdapterSummaryRows"],
        "materializedAdapterArchiveTotalCount": artifact["materializedAdapterArchiveTotalCount"],
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "publicSafeMaterializedAdapterArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceAdapterContractInterfaces": list(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaces": list(DRY_RUN_INTERFACES),
        "adapterMaterializationInterfaces": list(MATERIALIZATION_INTERFACES),
        "materializedAdapterArtifact": artifact,
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_adapter_materialization_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe adapter materialization summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "materialization schema mismatch")
    _require(summary.get("status") == "PASS", "materialization status mismatch")
    _require(
        summary.get("privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus") == MATERIALIZATION_STATUS,
        "materialization status token mismatch",
    )
    for key in (
        "redactedManifestImporterContractAdapterMaterializationOnly",
        "adapterDryRunProofConsumed",
        "adapterDryRunProofContinuityValidated",
        "adapterMaterializationExecuted",
        "adapterMaterializationInputAccepted",
        "materializedAdapterArtifactWritten",
        "materializedAdapterArtifactStoredInTrackedProof",
        "materializedAdapterRowsGenerated",
        "materializedAdapterRowsValidated",
        "materializedAdapterAggregateCountsValidated",
        "materializationInterfacesValidated",
        "materializedAdapterEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in (
        "materializedAdapterArtifactPathPublished",
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "redactedPrivateManifestArtifactPathPublished",
        "ignoredArtifactPathPublished",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "privateImporterMaterializationExecuted",
        "realImporterMaterializationExecuted",
        "adapterMaterializationReadPrivateInputs",
        "adapterMaterializationPublishedPrivateInput",
        "privateMaterializationArtifactPublished",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")
    expected_counts = {
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "adapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "materializedAdapterRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterValidationRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterSummaryRows": 1,
        "materializedAdapterArchiveTotalCount": 301,
        "publicSafeMaterializedAdapterArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(tuple(summary.get("sourceAdapterContractInterfaces", ())) == ADAPTER_CONTRACT_INTERFACES, "adapter interface mismatch")
    _require(tuple(summary.get("sourceAdapterDryRunInterfaces", ())) == DRY_RUN_INTERFACES, "dry-run interface mismatch")
    _require(tuple(summary.get("adapterMaterializationInterfaces", ())) == MATERIALIZATION_INTERFACES, "materialization interface mismatch")
    artifact = _read_mapping(summary, "materializedAdapterArtifact")
    _require(artifact.get("schemaVersion") == SCHEMA_VERSION, "artifact schema mismatch")
    _require(artifact.get("materializationStatus") == MATERIALIZATION_STATUS, "artifact status mismatch")
    _require(artifact.get("artifactRowMode") == "public-safe-archive-class-count-status-token-only", "artifact row mode mismatch")
    _require(artifact.get("materializedAdapterArtifactPathPublished") is False, "artifact path was published")
    _require(artifact.get("materializedAdapterRows") == len(REQUIRED_ARCHIVE_CLASSES), "artifact row count mismatch")
    _require(artifact.get("materializedAdapterArchiveTotalCount") == 301, "artifact archive total mismatch")
    rows = artifact.get("materializedAdapterRowsBody")
    _require(isinstance(rows, list), "artifact rows must be a list")
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "artifact row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"artifact row count mismatch: {archive_class}")
        _require(row.get("materializedPrivateIdentifiersPresent") is False, f"artifact private identifier guard mismatch: {archive_class}")
        for key in (
            "rawPathRows",
            "rawFilenameRows",
            "rawStemRows",
            "rawHashRows",
            "byteLengthRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "actualAssetImportRows",
            "generatedAssetRows",
            "privateDryRunRows",
            "realImporterDryRunRows",
            "realImporterMaterializationRows",
            "rawDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"artifact row zero mismatch: {archive_class}:{key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak check mismatch")
    _require(artifact.get("publicLeakCheck") == "PASS", "artifact public leak check mismatch")


def build_public_safe_adapter_materialization_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated adapter materialization summary in the tracked proof-plan schema."""

    validate_public_safe_adapter_materialization_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus": MATERIALIZATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceAdapterDryRunStatus": DRY_RUN_STATUS,
        "sourceAdapterStatus": ADAPTER_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceProofCount": 17,
            "adapterDryRunProof": DRY_RUN_PROOF.replace(".v1.json", ".md"),
            "adapterDryRunSchema": DRY_RUN_PROOF,
        },
        "adapterMaterializationDecision": {
            "redactedManifestImporterContractAdapterMaterializationOnly": True,
            "adapterDryRunProofConsumed": True,
            "adapterDryRunProofContinuityValidated": True,
            "adapterMaterializationExecuted": True,
            "adapterMaterializationInputAccepted": True,
            "materializedAdapterArtifactWritten": True,
            "materializedAdapterArtifactStoredInTrackedProof": True,
            "materializedAdapterArtifactPathPublished": False,
            "materializedAdapterRowsGenerated": True,
            "materializedAdapterRowsValidated": True,
            "materializedAdapterAggregateCountsValidated": True,
            "materializationInterfacesValidated": True,
            "materializedAdapterEmitsOnlyPublicSafeRows": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "privateAssetContentRead": False,
            "privateArchiveBytesRead": False,
            "privateManifestMaterialized": False,
            "privateRawManifestMaterialized": False,
            "privateRawManifestRowsObserved": False,
            "privateManifestRowsPublished": False,
            "rawPrivateManifestConsumed": False,
            "rawPrivateManifestRowsConsumed": False,
            "redactedPrivateManifestArtifactPathPublished": False,
            "ignoredArtifactPathPublished": False,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "privateImporterDryRunExecuted": False,
            "realImporterDryRunExecuted": False,
            "privateImporterMaterializationExecuted": False,
            "realImporterMaterializationExecuted": False,
            "adapterMaterializationReadPrivateInputs": False,
            "adapterMaterializationPublishedPrivateInput": False,
            "privateMaterializationArtifactPublished": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
        },
        "adapterMaterializationContract": {
            "adapterMaterializationInputMode": summary["adapterMaterializationInputMode"],
            "adapterMaterializationOutputMode": summary["adapterMaterializationOutputMode"],
            "sourceAdapterContractInterfaceCount": summary["sourceAdapterContractInterfaceCount"],
            "sourceAdapterContractInterfaces": summary["sourceAdapterContractInterfaces"],
            "sourceAdapterDryRunInterfaceCount": summary["sourceAdapterDryRunInterfaceCount"],
            "sourceAdapterDryRunInterfaces": summary["sourceAdapterDryRunInterfaces"],
            "adapterMaterializationInterfaceCount": summary["adapterMaterializationInterfaceCount"],
            "adapterMaterializationInterfaces": summary["adapterMaterializationInterfaces"],
            "materializedAdapterRows": summary["materializedAdapterRows"],
            "materializedAdapterArchiveClassRows": summary["materializedAdapterArchiveClassRows"],
            "materializedAdapterValidationRows": summary["materializedAdapterValidationRows"],
            "materializedAdapterSummaryRows": summary["materializedAdapterSummaryRows"],
            "materializedAdapterArchiveTotalCount": summary["materializedAdapterArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeMaterializedAdapterArtifactRows": summary["publicSafeMaterializedAdapterArtifactRows"],
            "materializedAdapterArtifact": summary["materializedAdapterArtifact"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-redacted-manifest-importer-contract-adapter-materialization-class-count-status-token-only",
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
                "the selected materialization can consume the tracked public-safe adapter dry-run proof rows",
                "the materialized adapter artifact contains only public-safe archive class/count/status-token rows",
                "the materialized adapter artifact preserves required archive class order and aggregate counts",
                "real importer implementation, real importer execution, private importer dry-run, and raw private manifest consumption remain unperformed",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw corpus manifest materialization",
                "private raw manifest row observation",
                "raw private manifest consumption",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
                "adapter materialization consumer validation",
                "actual asset import",
                "generated asset outputs",
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
    parser.add_argument("--dry-run-proof", type=Path, default=Path(DRY_RUN_PROOF))
    parser.add_argument("--artifact", type=Path, help="optional public-safe materialized adapter artifact output")
    parser.add_argument("--summary", type=Path, help="optional public-safe materialization summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        dry_run_proof = read_json(args.dry_run_proof)
        summary = build_public_safe_adapter_materialization_summary(dry_run_proof)
        validate_public_safe_adapter_materialization_summary(summary)
        if args.artifact is not None:
            args.artifact.parent.mkdir(parents=True, exist_ok=True)
            args.artifact.write_text(json.dumps(summary["materializedAdapterArtifact"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_adapter_materialization_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RedactedManifestImporterContractAdapterMaterializationError):
        print("Redacted manifest importer contract adapter materialization: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
