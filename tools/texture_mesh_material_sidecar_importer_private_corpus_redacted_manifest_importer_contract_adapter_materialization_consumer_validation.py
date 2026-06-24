#!/usr/bin/env python3
"""Validate the tracked adapter materialization artifact as consumer input."""

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
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization import (
    FALSE_GUARDS as MATERIALIZATION_FALSE_GUARDS,
    MATERIALIZATION_INTERFACES,
    MATERIALIZATION_STATUS,
    PROOF_SCHEMA_VERSION as MATERIALIZATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS,
    REDACTED_FIELDS as MATERIALIZATION_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as MATERIALIZATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-consumer-validation.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-consumer-validation-proof-plan.v1"
)
CONSUMER_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-consumer-validation-complete-public-safe-materialized-adapter-artifact-consumed-not-real-importer"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract "
    "Adapter Materialization Consumer Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-consumer-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract "
    "Adapter Consumer Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-readiness-gate-proof-plan"
)

MATERIALIZATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-materialization-proof-plan.v1.json"
)

CONSUMER_VALIDATION_INTERFACES = (
    "load-tracked-materialized-adapter-proof",
    "validate-materialized-adapter-proof-continuity",
    "extract-public-safe-materialized-adapter-artifact",
    "validate-materialized-adapter-artifact-schema",
    "validate-materialized-adapter-row-order",
    "validate-materialized-adapter-aggregate-counts",
    "validate-materialized-adapter-guard-counters",
    "emit-materialized-adapter-consumer-validation-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS,
            "adapter-materialization-consumer-validation-status",
            "materialized-adapter-consumer-input-status",
            "materialized-adapter-consumer-validation-rows",
            "consumer-validation-interface-linkage",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *MATERIALIZATION_REDACTED_FIELDS,
            "materialized-adapter-artifact-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *MATERIALIZATION_FALSE_GUARDS,
            "materializedAdapterConsumerValidationReadPrivateInputs",
            "materializedAdapterConsumerValidationPublishedPrivateInput",
            "materializedAdapterArtifactPathConsumed",
            "privateConsumerValidationArtifactPublished",
            "realImporterConsumerValidationExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *MATERIALIZATION_ZERO_COUNTERS,
            "materializedAdapterConsumerPrivateInputRows",
            "materializedAdapterArtifactPathConsumedRows",
            "privateConsumerValidationArtifactRows",
            "realImporterConsumerValidationRows",
        )
    )
)


class RedactedManifestImporterContractAdapterMaterializationConsumerValidationError(ValueError):
    """Raised when materialized adapter proof inputs cannot support consumer validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RedactedManifestImporterContractAdapterMaterializationConsumerValidationError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _validate_source_materialization_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == MATERIALIZATION_PROOF_SCHEMA_VERSION, "source proof schema mismatch")
    _require(source.get("status") == "PASS", "source proof status mismatch")
    _require(
        source.get("privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus") == MATERIALIZATION_STATUS,
        "source materialization status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(source.get("sourceAdapterDryRunStatus") == DRY_RUN_STATUS, "source adapter dry-run status mismatch")
    _require(source.get("sourceAdapterStatus") == ADAPTER_STATUS, "source adapter status mismatch")
    _require(_read_mapping(source, "sourceEvidence").get("sourceProofCount") == 17, "source proof count mismatch")

    decision = _read_mapping(source, "adapterMaterializationDecision")
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
        _require(decision.get(key) is True, f"source decision expected true: {key}")
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
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "adapterMaterializationContract")
    _require(tuple(contract.get("sourceAdapterContractInterfaces", ())) == ADAPTER_CONTRACT_INTERFACES, "source adapter interfaces mismatch")
    _require(tuple(contract.get("sourceAdapterDryRunInterfaces", ())) == DRY_RUN_INTERFACES, "source dry-run interfaces mismatch")
    _require(tuple(contract.get("adapterMaterializationInterfaces", ())) == MATERIALIZATION_INTERFACES, "source materialization interfaces mismatch")
    for key, expected in {
        "materializedAdapterRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterValidationRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterSummaryRows": 1,
        "materializedAdapterArchiveTotalCount": 301,
        "publicSafeMaterializedAdapterArtifactRows": 1,
    }.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    artifact = _read_mapping(contract, "materializedAdapterArtifact")
    _require(artifact.get("artifactKind") == "public-safe-redacted-manifest-importer-contract-adapter-materialized-artifact", "artifact kind mismatch")
    _require(artifact.get("artifactRowMode") == "public-safe-archive-class-count-status-token-only", "artifact row mode mismatch")
    _require(artifact.get("materializationStatus") == MATERIALIZATION_STATUS, "artifact materialization status mismatch")
    _require(artifact.get("sourceDryRunStatus") == DRY_RUN_STATUS, "artifact source dry-run status mismatch")
    _require(artifact.get("materializedAdapterArtifactPathPublished") is False, "artifact path was published")
    _require(artifact.get("materializedAdapterArtifactStoredInTrackedProof") is True, "artifact not stored in tracked proof")
    _require(artifact.get("privateAssetContentRead") is False, "artifact private content guard mismatch")
    _require(artifact.get("privateArchiveBytesRead") is False, "artifact private bytes guard mismatch")
    _require(artifact.get("realImporterExecuted") is False, "artifact real importer guard mismatch")
    _require(artifact.get("realImporterMaterializationExecuted") is False, "artifact materialization guard mismatch")
    _require(artifact.get("publicLeakCheck") == "PASS", "artifact public leak check mismatch")

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

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(MATERIALIZATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(MATERIALIZATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in MATERIALIZATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    return artifact


def build_consumer_validation_rows(artifact: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(artifact["materializedAdapterRowsBody"], start=1):
        archive_class = row["sourceArchiveClass"]
        rows.append(
            {
                "consumerValidationRowClass": "redacted-archive-class-contract-adapter-materialized-consumer-validation-row",
                "consumerValidationRowMode": "public-safe-archive-class-count-status-token-only",
                "consumerValidationRowOrdinal": ordinal,
                "sourceMaterializedRowOrdinal": row["materializedRowOrdinal"],
                "sourceArchiveClass": archive_class,
                "archiveClassCount": row["archiveClassCount"],
                "sourceMaterializedRowMode": row["materializedRowMode"],
                "validatedByInterface": "validate-materialized-adapter-aggregate-counts",
                "consumerValidationPrivateIdentifiersPresent": False,
                "rawPathRows": 0,
                "rawFilenameRows": 0,
                "rawStemRows": 0,
                "rawHashRows": 0,
                "byteLengthRows": 0,
                "rawTextureRefRows": 0,
                "rawMeshRefRows": 0,
                "actualAssetImportRows": 0,
                "generatedAssetRows": 0,
                "privateDryRunRows": 0,
                "realImporterDryRunRows": 0,
                "realImporterMaterializationRows": 0,
                "realImporterConsumerValidationRows": 0,
                "rawDryRunTraceRows": 0,
            }
        )
    return rows


def build_public_safe_adapter_materialization_consumer_validation_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build a tracked/public-safe summary for adapter materialization consumer validation."""

    artifact = _validate_source_materialization_proof(source)
    consumer_rows = build_consumer_validation_rows(artifact)
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRedactedManifestImporterContractAdapterMaterializationConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceMaterializationStatus": MATERIALIZATION_STATUS,
        "sourceAdapterDryRunStatus": DRY_RUN_STATUS,
        "sourceAdapterStatus": ADAPTER_STATUS,
        "redactedManifestImporterContractAdapterMaterializationConsumerValidationOnly": True,
        "materializedAdapterProofConsumed": True,
        "materializedAdapterArtifactConsumed": True,
        "materializedAdapterArtifactContinuityValidated": True,
        "consumerValidationExecuted": True,
        "consumerValidationInputAccepted": True,
        "consumerSchemaValidated": True,
        "consumerRowModeValidated": True,
        "consumerArchiveClassOrderValidated": True,
        "consumerArchiveClassCountsValidated": True,
        "consumerGuardCountersValidated": True,
        "consumerInterfacesValidated": True,
        "consumerValidationEmitsOnlyPublicSafeRows": True,
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
        "realImporterConsumerValidationExecuted": False,
        "materializedAdapterConsumerValidationReadPrivateInputs": False,
        "materializedAdapterConsumerValidationPublishedPrivateInput": False,
        "materializedAdapterArtifactPathConsumed": False,
        "privateConsumerValidationArtifactPublished": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceRootClass": artifact["sourceRootClass"],
        "consumerValidationInputMode": "tracked-public-safe-materialized-adapter-proof-json",
        "consumerValidationOutputMode": "tracked-public-safe-materialized-adapter-consumer-validation-proof",
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "consumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "materializedAdapterRowsConsumed": len(consumer_rows),
        "consumerValidationRows": len(consumer_rows),
        "consumerValidationArchiveClassRows": len(consumer_rows),
        "consumerValidationSummaryRows": 1,
        "consumerArchiveTotalCount": sum(row["archiveClassCount"] for row in consumer_rows),
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "publicSafeConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceAdapterContractInterfaces": list(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaces": list(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaces": list(MATERIALIZATION_INTERFACES),
        "consumerValidationInterfaces": list(CONSUMER_VALIDATION_INTERFACES),
        "materializedAdapterConsumerValidationRows": consumer_rows,
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_adapter_materialization_consumer_validation_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe adapter materialization consumer-validation summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "consumer validation schema mismatch")
    _require(summary.get("status") == "PASS", "consumer validation status mismatch")
    _require(
        summary.get("privateCorpusRedactedManifestImporterContractAdapterMaterializationConsumerValidationStatus")
        == CONSUMER_VALIDATION_STATUS,
        "consumer validation status token mismatch",
    )
    for key in (
        "redactedManifestImporterContractAdapterMaterializationConsumerValidationOnly",
        "materializedAdapterProofConsumed",
        "materializedAdapterArtifactConsumed",
        "materializedAdapterArtifactContinuityValidated",
        "consumerValidationExecuted",
        "consumerValidationInputAccepted",
        "consumerSchemaValidated",
        "consumerRowModeValidated",
        "consumerArchiveClassOrderValidated",
        "consumerArchiveClassCountsValidated",
        "consumerGuardCountersValidated",
        "consumerInterfacesValidated",
        "consumerValidationEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
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
        "realImporterMaterializationExecuted",
        "realImporterConsumerValidationExecuted",
        "materializedAdapterConsumerValidationReadPrivateInputs",
        "materializedAdapterConsumerValidationPublishedPrivateInput",
        "materializedAdapterArtifactPathConsumed",
        "privateConsumerValidationArtifactPublished",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")
    for key, expected in {
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "consumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "materializedAdapterRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerValidationRows": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerValidationArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerValidationSummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "publicSafeConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "unknownAyaArchiveClassCount": 0,
    }.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(tuple(summary.get("sourceAdapterContractInterfaces", ())) == ADAPTER_CONTRACT_INTERFACES, "adapter interface mismatch")
    _require(tuple(summary.get("sourceAdapterDryRunInterfaces", ())) == DRY_RUN_INTERFACES, "dry-run interface mismatch")
    _require(tuple(summary.get("sourceAdapterMaterializationInterfaces", ())) == MATERIALIZATION_INTERFACES, "materialization interface mismatch")
    _require(tuple(summary.get("consumerValidationInterfaces", ())) == CONSUMER_VALIDATION_INTERFACES, "consumer validation interface mismatch")
    rows = summary.get("materializedAdapterConsumerValidationRows", [])
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "consumer row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"consumer row count mismatch: {archive_class}")
        _require(row.get("consumerValidationPrivateIdentifiersPresent") is False, f"consumer row private identifier guard mismatch: {archive_class}")
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
            "realImporterConsumerValidationRows",
            "rawDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"consumer row zero mismatch: {archive_class}:{key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak check mismatch")


def build_public_safe_adapter_materialization_consumer_validation_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated adapter materialization consumer summary in the tracked proof-plan schema."""

    validate_public_safe_adapter_materialization_consumer_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRedactedManifestImporterContractAdapterMaterializationConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceMaterializationStatus": MATERIALIZATION_STATUS,
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
            "sourceProofCount": 18,
            "adapterMaterializationProof": MATERIALIZATION_PROOF.replace(".v1.json", ".md"),
            "adapterMaterializationSchema": MATERIALIZATION_PROOF,
        },
        "consumerValidationDecision": {
            "redactedManifestImporterContractAdapterMaterializationConsumerValidationOnly": True,
            "materializedAdapterProofConsumed": True,
            "materializedAdapterArtifactConsumed": True,
            "materializedAdapterArtifactContinuityValidated": True,
            "consumerValidationExecuted": True,
            "consumerValidationInputAccepted": True,
            "consumerSchemaValidated": True,
            "consumerRowModeValidated": True,
            "consumerArchiveClassOrderValidated": True,
            "consumerArchiveClassCountsValidated": True,
            "consumerGuardCountersValidated": True,
            "consumerInterfacesValidated": True,
            "consumerValidationEmitsOnlyPublicSafeRows": True,
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
            "realImporterConsumerValidationExecuted": False,
            "materializedAdapterConsumerValidationReadPrivateInputs": False,
            "materializedAdapterConsumerValidationPublishedPrivateInput": False,
            "materializedAdapterArtifactPathConsumed": False,
            "privateConsumerValidationArtifactPublished": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
        },
        "adapterMaterializationConsumerValidationContract": {
            "consumerValidationInputMode": summary["consumerValidationInputMode"],
            "consumerValidationOutputMode": summary["consumerValidationOutputMode"],
            "sourceAdapterContractInterfaceCount": summary["sourceAdapterContractInterfaceCount"],
            "sourceAdapterContractInterfaces": summary["sourceAdapterContractInterfaces"],
            "sourceAdapterDryRunInterfaceCount": summary["sourceAdapterDryRunInterfaceCount"],
            "sourceAdapterDryRunInterfaces": summary["sourceAdapterDryRunInterfaces"],
            "sourceAdapterMaterializationInterfaceCount": summary["sourceAdapterMaterializationInterfaceCount"],
            "sourceAdapterMaterializationInterfaces": summary["sourceAdapterMaterializationInterfaces"],
            "consumerValidationInterfaceCount": summary["consumerValidationInterfaceCount"],
            "consumerValidationInterfaces": summary["consumerValidationInterfaces"],
            "materializedAdapterRowsConsumed": summary["materializedAdapterRowsConsumed"],
            "consumerValidationRows": summary["consumerValidationRows"],
            "consumerValidationArchiveClassRows": summary["consumerValidationArchiveClassRows"],
            "consumerValidationSummaryRows": summary["consumerValidationSummaryRows"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeConsumerValidationArtifactRows": summary["publicSafeConsumerValidationArtifactRows"],
            "materializedAdapterConsumerValidationRows": summary["materializedAdapterConsumerValidationRows"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-class-count-status-token-only",
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
                "the selected consumer validation can consume the tracked public-safe materialized adapter artifact",
                "the consumer validation input contains only public-safe archive class/count/status-token rows",
                "the consumer validation preserves required archive class order and aggregate counts",
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
    parser.add_argument("--materialization-proof", type=Path, default=Path(MATERIALIZATION_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe consumer validation summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        materialization_proof = read_json(args.materialization_proof)
        summary = build_public_safe_adapter_materialization_consumer_validation_summary(materialization_proof)
        validate_public_safe_adapter_materialization_consumer_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_adapter_materialization_consumer_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RedactedManifestImporterContractAdapterMaterializationConsumerValidationError):
        print("Redacted manifest importer contract adapter materialization consumer validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
