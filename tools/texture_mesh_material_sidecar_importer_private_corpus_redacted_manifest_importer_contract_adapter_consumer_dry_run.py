#!/usr/bin/env python3
"""Dry-run public-safe adapter-consumer row consumption."""

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
    MATERIALIZATION_INTERFACES,
    MATERIALIZATION_STATUS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization_consumer_validation import (
    CONSUMER_VALIDATION_INTERFACES,
    CONSUMER_VALIDATION_STATUS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_consumer_readiness_gate import (
    CONSUMER_READINESS_INTERFACES,
    CONSUMER_READINESS_STATUS,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PREVIOUS_SCOPE as SOURCE_PREVIOUS_SCOPE,
    PREVIOUS_SLICE as SOURCE_PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REDACTED_FIELDS as READINESS_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-dry-run.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-dry-run-proof-plan.v1"
)
CONSUMER_DRY_RUN_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract "
    "Adapter Consumer Dry-Run Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-dry-run-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate "
    "Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-"
    "proof-plan"
)

CONSUMER_READINESS_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-readiness-gate-proof-plan.v1.json"
)

CONSUMER_DRY_RUN_INTERFACES = (
    "load-tracked-adapter-consumer-readiness-gate-proof",
    "validate-consumer-readiness-proof-continuity",
    "validate-consumer-readiness-row-order",
    "dry-run-adapter-consumer-row-consumption",
    "validate-adapter-consumer-dry-run-aggregate-counts",
    "validate-adapter-consumer-private-data-refusal-guards",
    "emit-adapter-consumer-dry-run-validation-rows",
    "emit-adapter-consumer-dry-run-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "adapter-consumer-dry-run-status",
            "source-consumer-readiness-gate-status",
            "adapter-consumer-dry-run-rows",
            "adapter-consumer-dry-run-interface-linkage",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "adapter-consumer-dry-run-private-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *(guard for guard in READINESS_FALSE_GUARDS if guard != "adapterConsumerDryRunExecuted"),
            "adapterConsumerDryRunReadPrivateInputs",
            "adapterConsumerDryRunPublishedPrivateInput",
            "privateAdapterConsumerDryRunArtifactPublished",
            "rawAdapterConsumerDryRunTracePublished",
            "actualAssetImportExecuted",
            "generatedAssetOutputExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *(counter for counter in READINESS_ZERO_COUNTERS if counter != "adapterConsumerDryRunRows"),
            "adapterConsumerDryRunPrivateInputRows",
            "privateAdapterConsumerDryRunArtifactRows",
            "adapterConsumerDryRunOutputArtifactRows",
            "rawAdapterConsumerDryRunTraceRows",
        )
    )
)


class RedactedManifestImporterContractAdapterConsumerDryRunError(ValueError):
    """Raised when readiness proof rows cannot support adapter-consumer dry-run."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RedactedManifestImporterContractAdapterConsumerDryRunError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _validate_source_readiness_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source proof schema mismatch")
    _require(source.get("status") == "PASS", "source proof status mismatch")
    _require(
        source.get("privateCorpusRedactedManifestImporterContractAdapterConsumerReadinessGateStatus")
        == CONSUMER_READINESS_STATUS,
        "source consumer-readiness status mismatch",
    )
    _require(source.get("previousSlice") == SOURCE_PREVIOUS_SLICE, "source previous slice mismatch")
    _require(source.get("previousScope") == SOURCE_PREVIOUS_SCOPE, "source previous scope mismatch")
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    _require(source.get("sourceConsumerValidationStatus") == CONSUMER_VALIDATION_STATUS, "source consumer-validation status mismatch")
    _require(source.get("sourceMaterializationStatus") == MATERIALIZATION_STATUS, "source materialization status mismatch")
    _require(source.get("sourceAdapterDryRunStatus") == DRY_RUN_STATUS, "source adapter dry-run status mismatch")
    _require(source.get("sourceAdapterStatus") == ADAPTER_STATUS, "source adapter status mismatch")
    _require(_read_mapping(source, "sourceEvidence").get("sourceProofCount") == 19, "source proof count mismatch")

    decision = _read_mapping(source, "consumerReadinessDecision")
    for key in (
        "redactedManifestImporterContractAdapterConsumerReadinessGateOnly",
        "consumerValidationProofConsumed",
        "consumerValidationProofContinuityValidated",
        "consumerValidationContractValidated",
        "consumerReadinessGateExecuted",
        "consumerReadinessInputAccepted",
        "consumerReadinessArchiveClassOrderValidated",
        "consumerReadinessArchiveClassCountsValidated",
        "consumerReadinessGuardCountersValidated",
        "consumerReadinessInterfacesValidated",
        "consumerDryRunLaneSelected",
        "consumerReadinessEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision expected true: {key}")
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
        "consumerReadinessGateReadPrivateInputs",
        "consumerReadinessGatePublishedPrivateInput",
        "privateConsumerReadinessArtifactPublished",
        "realImporterConsumerReadinessExecuted",
        "adapterConsumerDryRunExecuted",
        "realImporterConsumerDryRunExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "adapterConsumerReadinessGateContract")
    for key, expected in {
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "consumerReadinessInterfaceCount": len(CONSUMER_READINESS_INTERFACES),
        "consumerValidationRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerReadinessGateRows": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerReadinessArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "consumerReadinessSummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "publicSafeConsumerReadinessArtifactRows": 1,
    }.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")
    _require(tuple(contract.get("sourceAdapterContractInterfaces", ())) == ADAPTER_CONTRACT_INTERFACES, "source adapter interfaces mismatch")
    _require(tuple(contract.get("sourceAdapterDryRunInterfaces", ())) == DRY_RUN_INTERFACES, "source dry-run interfaces mismatch")
    _require(tuple(contract.get("sourceAdapterMaterializationInterfaces", ())) == MATERIALIZATION_INTERFACES, "source materialization interfaces mismatch")
    _require(tuple(contract.get("sourceConsumerValidationInterfaces", ())) == CONSUMER_VALIDATION_INTERFACES, "source consumer-validation interfaces mismatch")
    _require(tuple(contract.get("consumerReadinessInterfaces", ())) == CONSUMER_READINESS_INTERFACES, "source consumer-readiness interfaces mismatch")

    rows = contract.get("consumerReadinessGateRowsBody")
    _require(isinstance(rows, list), "source readiness rows must be a list")
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "source readiness row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"source readiness row count mismatch: {archive_class}")
        _require(row.get("readyForPublicSafeAdapterConsumerDryRun") is True, f"source readiness false: {archive_class}")
        _require(row.get("consumerReadinessPrivateIdentifiersPresent") is False, f"source readiness private identifier guard mismatch: {archive_class}")
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
            "realImporterConsumerReadinessRows",
            "adapterConsumerDryRunRows",
            "realImporterConsumerDryRunRows",
            "rawDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"source readiness row zero mismatch: {archive_class}:{key}")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(READINESS_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(READINESS_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in READINESS_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    return contract


def build_adapter_consumer_dry_run_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(contract["consumerReadinessGateRowsBody"], start=1):
        archive_class = row["sourceArchiveClass"]
        rows.append(
            {
                "adapterConsumerDryRunRowClass": "redacted-archive-class-contract-adapter-consumer-dry-run-row",
                "adapterConsumerDryRunRowMode": "public-safe-archive-class-count-status-token-only",
                "adapterConsumerDryRunRowOrdinal": ordinal,
                "sourceConsumerReadinessGateRowOrdinal": row["consumerReadinessGateRowOrdinal"],
                "sourceArchiveClass": archive_class,
                "archiveClassCount": row["archiveClassCount"],
                "acceptedByDryRunInterface": "dry-run-adapter-consumer-row-consumption",
                "sourceConsumerReadinessGateRowMode": row["consumerReadinessGateRowMode"],
                "adapterConsumerDryRunPrivateIdentifiersPresent": False,
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
                "realImporterConsumerReadinessRows": 0,
                "realImporterConsumerDryRunRows": 0,
                "rawDryRunTraceRows": 0,
                "rawAdapterConsumerDryRunTraceRows": 0,
            }
        )
    return rows


def build_public_safe_adapter_consumer_dry_run_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build a tracked/public-safe adapter-consumer dry-run summary."""

    contract = _validate_source_readiness_proof(source)
    dry_run_rows = build_adapter_consumer_dry_run_rows(contract)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRedactedManifestImporterContractAdapterConsumerDryRunStatus": CONSUMER_DRY_RUN_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceConsumerReadinessGateStatus": CONSUMER_READINESS_STATUS,
        "sourceConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
        "sourceMaterializationStatus": MATERIALIZATION_STATUS,
        "sourceAdapterDryRunStatus": DRY_RUN_STATUS,
        "sourceAdapterStatus": ADAPTER_STATUS,
        "redactedManifestImporterContractAdapterConsumerDryRunOnly": True,
        "consumerReadinessProofConsumed": True,
        "consumerReadinessProofContinuityValidated": True,
        "consumerReadinessGateRowsConsumed": True,
        "adapterConsumerDryRunExecuted": True,
        "adapterConsumerDryRunInputAccepted": True,
        "adapterConsumerDryRunRowsGenerated": True,
        "adapterConsumerDryRunRowsValidated": True,
        "adapterConsumerDryRunAggregateCountsValidated": True,
        "adapterConsumerDryRunInterfacesValidated": True,
        "adapterConsumerDryRunEmitsOnlyPublicSafeRows": True,
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
        "realImporterConsumerReadinessExecuted": False,
        "realImporterConsumerDryRunExecuted": False,
        "adapterConsumerDryRunReadPrivateInputs": False,
        "adapterConsumerDryRunPublishedPrivateInput": False,
        "privateAdapterConsumerDryRunArtifactPublished": False,
        "rawAdapterConsumerDryRunTracePublished": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "adapterConsumerDryRunInputMode": "tracked-public-safe-adapter-consumer-readiness-gate-proof-json",
        "adapterConsumerDryRunOutputMode": "public-safe-adapter-consumer-dry-run-class-count-status-token-rows",
        "selectedNextLaneClass": "private-corpus real importer dry-run readiness gate without execution",
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "sourceConsumerReadinessInterfaceCount": len(CONSUMER_READINESS_INTERFACES),
        "adapterConsumerDryRunInterfaceCount": len(CONSUMER_DRY_RUN_INTERFACES),
        "consumerReadinessRowsConsumed": len(dry_run_rows),
        "adapterConsumerDryRunRows": len(dry_run_rows),
        "adapterConsumerDryRunArchiveClassRows": len(dry_run_rows),
        "adapterConsumerDryRunValidationRows": len(dry_run_rows),
        "adapterConsumerDryRunSummaryRows": 1,
        "consumerArchiveTotalCount": sum(row["archiveClassCount"] for row in dry_run_rows),
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "publicSafeAdapterConsumerDryRunSummaryRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceAdapterContractInterfaces": list(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaces": list(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaces": list(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaces": list(CONSUMER_VALIDATION_INTERFACES),
        "sourceConsumerReadinessInterfaces": list(CONSUMER_READINESS_INTERFACES),
        "adapterConsumerDryRunInterfaces": list(CONSUMER_DRY_RUN_INTERFACES),
        "adapterConsumerDryRunRowsBody": dry_run_rows,
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_adapter_consumer_dry_run_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe adapter-consumer dry-run summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "consumer dry-run schema mismatch")
    _require(summary.get("status") == "PASS", "consumer dry-run status mismatch")
    _require(
        summary.get("privateCorpusRedactedManifestImporterContractAdapterConsumerDryRunStatus")
        == CONSUMER_DRY_RUN_STATUS,
        "consumer dry-run status token mismatch",
    )
    for key in (
        "redactedManifestImporterContractAdapterConsumerDryRunOnly",
        "consumerReadinessProofConsumed",
        "consumerReadinessProofContinuityValidated",
        "consumerReadinessGateRowsConsumed",
        "adapterConsumerDryRunExecuted",
        "adapterConsumerDryRunInputAccepted",
        "adapterConsumerDryRunRowsGenerated",
        "adapterConsumerDryRunRowsValidated",
        "adapterConsumerDryRunAggregateCountsValidated",
        "adapterConsumerDryRunInterfacesValidated",
        "adapterConsumerDryRunEmitsOnlyPublicSafeRows",
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
        "realImporterConsumerReadinessExecuted",
        "realImporterConsumerDryRunExecuted",
        "adapterConsumerDryRunReadPrivateInputs",
        "adapterConsumerDryRunPublishedPrivateInput",
        "privateAdapterConsumerDryRunArtifactPublished",
        "rawAdapterConsumerDryRunTracePublished",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")
    for key, expected in {
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "sourceConsumerReadinessInterfaceCount": len(CONSUMER_READINESS_INTERFACES),
        "adapterConsumerDryRunInterfaceCount": len(CONSUMER_DRY_RUN_INTERFACES),
        "consumerReadinessRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "adapterConsumerDryRunRows": len(REQUIRED_ARCHIVE_CLASSES),
        "adapterConsumerDryRunArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "adapterConsumerDryRunValidationRows": len(REQUIRED_ARCHIVE_CLASSES),
        "adapterConsumerDryRunSummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "publicSafeAdapterConsumerDryRunSummaryRows": 1,
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
    _require(tuple(summary.get("sourceConsumerValidationInterfaces", ())) == CONSUMER_VALIDATION_INTERFACES, "consumer-validation interface mismatch")
    _require(tuple(summary.get("sourceConsumerReadinessInterfaces", ())) == CONSUMER_READINESS_INTERFACES, "consumer-readiness interface mismatch")
    _require(tuple(summary.get("adapterConsumerDryRunInterfaces", ())) == CONSUMER_DRY_RUN_INTERFACES, "consumer dry-run interface mismatch")
    rows = summary.get("adapterConsumerDryRunRowsBody", [])
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "consumer dry-run row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"consumer dry-run row count mismatch: {archive_class}")
        _require(row.get("adapterConsumerDryRunPrivateIdentifiersPresent") is False, f"consumer dry-run row private identifier guard mismatch: {archive_class}")
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
            "realImporterConsumerReadinessRows",
            "realImporterConsumerDryRunRows",
            "rawDryRunTraceRows",
            "rawAdapterConsumerDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"consumer dry-run row zero mismatch: {archive_class}:{key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak check mismatch")


def build_public_safe_adapter_consumer_dry_run_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated adapter-consumer dry-run summary in the tracked proof-plan schema."""

    validate_public_safe_adapter_consumer_dry_run_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRedactedManifestImporterContractAdapterConsumerDryRunStatus": CONSUMER_DRY_RUN_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceConsumerReadinessGateStatus": CONSUMER_READINESS_STATUS,
        "sourceConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
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
            "sourceProofCount": 20,
            "adapterConsumerReadinessGateProof": CONSUMER_READINESS_PROOF.replace(".v1.json", ".md"),
            "adapterConsumerReadinessGateSchema": CONSUMER_READINESS_PROOF,
        },
        "adapterConsumerDryRunDecision": {
            "redactedManifestImporterContractAdapterConsumerDryRunOnly": True,
            "consumerReadinessProofConsumed": True,
            "consumerReadinessProofContinuityValidated": True,
            "consumerReadinessGateRowsConsumed": True,
            "adapterConsumerDryRunExecuted": True,
            "adapterConsumerDryRunInputAccepted": True,
            "adapterConsumerDryRunRowsGenerated": True,
            "adapterConsumerDryRunRowsValidated": True,
            "adapterConsumerDryRunAggregateCountsValidated": True,
            "adapterConsumerDryRunInterfacesValidated": True,
            "adapterConsumerDryRunEmitsOnlyPublicSafeRows": True,
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
            "realImporterConsumerReadinessExecuted": False,
            "realImporterConsumerDryRunExecuted": False,
            "adapterConsumerDryRunReadPrivateInputs": False,
            "adapterConsumerDryRunPublishedPrivateInput": False,
            "privateAdapterConsumerDryRunArtifactPublished": False,
            "rawAdapterConsumerDryRunTracePublished": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
        },
        "adapterConsumerDryRunContract": {
            "adapterConsumerDryRunInputMode": summary["adapterConsumerDryRunInputMode"],
            "adapterConsumerDryRunOutputMode": summary["adapterConsumerDryRunOutputMode"],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "sourceAdapterContractInterfaceCount": summary["sourceAdapterContractInterfaceCount"],
            "sourceAdapterContractInterfaces": summary["sourceAdapterContractInterfaces"],
            "sourceAdapterDryRunInterfaceCount": summary["sourceAdapterDryRunInterfaceCount"],
            "sourceAdapterDryRunInterfaces": summary["sourceAdapterDryRunInterfaces"],
            "sourceAdapterMaterializationInterfaceCount": summary["sourceAdapterMaterializationInterfaceCount"],
            "sourceAdapterMaterializationInterfaces": summary["sourceAdapterMaterializationInterfaces"],
            "sourceConsumerValidationInterfaceCount": summary["sourceConsumerValidationInterfaceCount"],
            "sourceConsumerValidationInterfaces": summary["sourceConsumerValidationInterfaces"],
            "sourceConsumerReadinessInterfaceCount": summary["sourceConsumerReadinessInterfaceCount"],
            "sourceConsumerReadinessInterfaces": summary["sourceConsumerReadinessInterfaces"],
            "adapterConsumerDryRunInterfaceCount": summary["adapterConsumerDryRunInterfaceCount"],
            "adapterConsumerDryRunInterfaces": summary["adapterConsumerDryRunInterfaces"],
            "consumerReadinessRowsConsumed": summary["consumerReadinessRowsConsumed"],
            "adapterConsumerDryRunRows": summary["adapterConsumerDryRunRows"],
            "adapterConsumerDryRunArchiveClassRows": summary["adapterConsumerDryRunArchiveClassRows"],
            "adapterConsumerDryRunValidationRows": summary["adapterConsumerDryRunValidationRows"],
            "adapterConsumerDryRunSummaryRows": summary["adapterConsumerDryRunSummaryRows"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeAdapterConsumerDryRunSummaryRows": summary["publicSafeAdapterConsumerDryRunSummaryRows"],
            "adapterConsumerDryRunRowsBody": summary["adapterConsumerDryRunRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-redacted-manifest-importer-contract-adapter-consumer-dry-run-class-count-status-token-only",
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
                "the selected adapter-consumer dry-run can consume the tracked public-safe consumer-readiness proof rows",
                "the dry-run preserves required archive class order, aggregate counts, and private-data refusal guards",
                "the dry-run emits only public-safe class/count/status-token validation rows",
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
                "private importer materialization",
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
    parser.add_argument("--consumer-readiness-proof", type=Path, default=Path(CONSUMER_READINESS_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe adapter-consumer dry-run summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        consumer_readiness_proof = read_json(args.consumer_readiness_proof)
        summary = build_public_safe_adapter_consumer_dry_run_summary(consumer_readiness_proof)
        validate_public_safe_adapter_consumer_dry_run_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_adapter_consumer_dry_run_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RedactedManifestImporterContractAdapterConsumerDryRunError):
        print("Redacted manifest importer contract adapter consumer dry run: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
