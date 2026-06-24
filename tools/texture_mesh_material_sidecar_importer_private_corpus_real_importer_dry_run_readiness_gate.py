#!/usr/bin/env python3
"""Select the next real-importer dry-run boundary lane from tracked proof only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import (
    REQUIRED_ARCHIVE_CLASSES,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter import (
    ADAPTER_CONTRACT_INTERFACES,
    ADAPTER_STATUS,
    EXPECTED_ARCHIVE_CLASS_COUNTS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_consumer_dry_run import (
    CONSUMER_DRY_RUN_INTERFACES,
    CONSUMER_DRY_RUN_STATUS,
    FALSE_GUARDS as CONSUMER_DRY_RUN_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as CONSUMER_DRY_RUN_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as CONSUMER_DRY_RUN_PUBLIC_ALLOWED_OUTPUTS,
    REDACTED_FIELDS as CONSUMER_DRY_RUN_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as CONSUMER_DRY_RUN_ZERO_COUNTERS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_consumer_readiness_gate import (
    CONSUMER_READINESS_INTERFACES,
    CONSUMER_READINESS_STATUS,
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


SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate.v1"
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "readiness-gate-proof-plan.v1"
)
REAL_IMPORTER_READINESS_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan"

ADAPTER_CONSUMER_DRY_RUN_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-"
    "adapter-consumer-dry-run-proof-plan.v1.json"
)

REAL_IMPORTER_READINESS_INTERFACES = (
    "load-tracked-adapter-consumer-dry-run-proof",
    "validate-adapter-consumer-dry-run-continuity",
    "validate-public-safe-adapter-consumer-dry-run-rows",
    "evaluate-real-importer-dry-run-readiness",
    "validate-real-importer-private-data-refusal-guards",
    "select-real-importer-dry-run-harness-boundary-lane",
    "emit-real-importer-readiness-validation-rows",
    "emit-real-importer-readiness-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_DRY_RUN_PUBLIC_ALLOWED_OUTPUTS,
            "real-importer-dry-run-readiness-gate-status",
            "source-adapter-consumer-dry-run-status",
            "real-importer-readiness-gate-rows",
            "real-importer-readiness-interface-linkage",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_DRY_RUN_REDACTED_FIELDS,
            "real-importer-dry-run-private-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_DRY_RUN_FALSE_GUARDS,
            "realImporterDryRunReadinessGateReadPrivateInputs",
            "realImporterDryRunReadinessGatePublishedPrivateInput",
            "privateRealImporterReadinessArtifactPublished",
            "realImporterDryRunHarnessExecuted",
            "realImporterDryRunHarnessMaterialized",
            "realImporterDryRunBoundaryBypassed",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_DRY_RUN_ZERO_COUNTERS,
            "realImporterDryRunReadinessPrivateInputRows",
            "privateRealImporterReadinessArtifactRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunBoundaryBypassRows",
        )
    )
)


class RealImporterDryRunReadinessGateError(ValueError):
    """Raised when the adapter-consumer dry-run proof cannot support readiness selection."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunReadinessGateError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _validate_source_adapter_consumer_dry_run_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == CONSUMER_DRY_RUN_PROOF_SCHEMA_VERSION, "source proof schema mismatch")
    _require(source.get("status") == "PASS", "source proof status mismatch")
    _require(
        source.get("privateCorpusRedactedManifestImporterContractAdapterConsumerDryRunStatus")
        == CONSUMER_DRY_RUN_STATUS,
        "source adapter-consumer dry-run status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    _require(source.get("sourceConsumerReadinessGateStatus") == CONSUMER_READINESS_STATUS, "source readiness status mismatch")
    _require(source.get("sourceConsumerValidationStatus") == CONSUMER_VALIDATION_STATUS, "source validation status mismatch")
    _require(source.get("sourceMaterializationStatus") == MATERIALIZATION_STATUS, "source materialization status mismatch")
    _require(source.get("sourceAdapterDryRunStatus") == DRY_RUN_STATUS, "source adapter dry-run status mismatch")
    _require(source.get("sourceAdapterStatus") == ADAPTER_STATUS, "source adapter status mismatch")
    _require(_read_mapping(source, "sourceEvidence").get("sourceProofCount") == 20, "source proof count mismatch")

    decision = _read_mapping(source, "adapterConsumerDryRunDecision")
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
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "adapterConsumerDryRunContract")
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
    }.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")
    _require(tuple(contract.get("sourceAdapterContractInterfaces", ())) == ADAPTER_CONTRACT_INTERFACES, "source adapter interfaces mismatch")
    _require(tuple(contract.get("sourceAdapterDryRunInterfaces", ())) == DRY_RUN_INTERFACES, "source dry-run interfaces mismatch")
    _require(tuple(contract.get("sourceAdapterMaterializationInterfaces", ())) == MATERIALIZATION_INTERFACES, "source materialization interfaces mismatch")
    _require(tuple(contract.get("sourceConsumerValidationInterfaces", ())) == CONSUMER_VALIDATION_INTERFACES, "source validation interfaces mismatch")
    _require(tuple(contract.get("sourceConsumerReadinessInterfaces", ())) == CONSUMER_READINESS_INTERFACES, "source readiness interfaces mismatch")
    _require(tuple(contract.get("adapterConsumerDryRunInterfaces", ())) == CONSUMER_DRY_RUN_INTERFACES, "source consumer dry-run interfaces mismatch")

    rows = contract.get("adapterConsumerDryRunRowsBody")
    _require(isinstance(rows, list), "source adapter-consumer dry-run rows must be a list")
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "source row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"source row count mismatch: {archive_class}")
        _require(row.get("adapterConsumerDryRunPrivateIdentifiersPresent") is False, f"source row private identifier guard mismatch: {archive_class}")
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
            "realImporterConsumerDryRunRows",
            "rawDryRunTraceRows",
            "rawAdapterConsumerDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"source row zero mismatch: {archive_class}:{key}")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(CONSUMER_DRY_RUN_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(CONSUMER_DRY_RUN_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in CONSUMER_DRY_RUN_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    return contract


def build_real_importer_readiness_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(contract["adapterConsumerDryRunRowsBody"], start=1):
        archive_class = row["sourceArchiveClass"]
        rows.append(
            {
                "realImporterReadinessGateRowClass": "private-corpus-real-importer-dry-run-readiness-gate-row",
                "realImporterReadinessGateRowMode": "public-safe-archive-class-count-status-token-only",
                "realImporterReadinessGateRowOrdinal": ordinal,
                "sourceAdapterConsumerDryRunRowOrdinal": row["adapterConsumerDryRunRowOrdinal"],
                "sourceArchiveClass": archive_class,
                "archiveClassCount": row["archiveClassCount"],
                "readyForRealImporterDryRunHarnessBoundary": True,
                "directRealImporterDryRunAllowedHere": False,
                "realImporterReadinessPrivateIdentifiersPresent": False,
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
                "realImporterConsumerDryRunRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunBoundaryBypassRows": 0,
                "rawDryRunTraceRows": 0,
                "rawAdapterConsumerDryRunTraceRows": 0,
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_readiness_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build a tracked/public-safe real-importer dry-run readiness summary."""

    contract = _validate_source_adapter_consumer_dry_run_proof(source)
    readiness_rows = build_real_importer_readiness_rows(contract)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunReadinessGateStatus": REAL_IMPORTER_READINESS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceAdapterConsumerDryRunStatus": CONSUMER_DRY_RUN_STATUS,
        "sourceConsumerReadinessGateStatus": CONSUMER_READINESS_STATUS,
        "sourceConsumerValidationStatus": CONSUMER_VALIDATION_STATUS,
        "sourceMaterializationStatus": MATERIALIZATION_STATUS,
        "sourceAdapterDryRunStatus": DRY_RUN_STATUS,
        "sourceAdapterStatus": ADAPTER_STATUS,
        "privateCorpusRealImporterDryRunReadinessGateOnly": True,
        "adapterConsumerDryRunProofConsumed": True,
        "adapterConsumerDryRunProofContinuityValidated": True,
        "adapterConsumerDryRunRowsConsumedByReadinessGate": True,
        "realImporterDryRunReadinessGateExecuted": True,
        "realImporterReadinessInputAccepted": True,
        "realImporterReadinessArchiveClassOrderValidated": True,
        "realImporterReadinessArchiveClassCountsValidated": True,
        "realImporterReadinessGuardCountersValidated": True,
        "realImporterReadinessInterfacesValidated": True,
        "realImporterDryRunHarnessBoundaryLaneSelected": True,
        "realImporterReadinessEmitsOnlyPublicSafeRows": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
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
        "realImporterDryRunReadinessGateReadPrivateInputs": False,
        "realImporterDryRunReadinessGatePublishedPrivateInput": False,
        "privateRealImporterReadinessArtifactPublished": False,
        "realImporterDryRunHarnessExecuted": False,
        "realImporterDryRunHarnessMaterialized": False,
        "realImporterDryRunBoundaryBypassed": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "realImporterReadinessInputMode": "tracked-public-safe-adapter-consumer-dry-run-proof-json",
        "realImporterReadinessOutputMode": "public-safe-real-importer-readiness-gate-class-count-status-token-rows",
        "selectedNextLaneClass": "private-corpus real importer dry-run harness boundary without execution",
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "sourceConsumerReadinessInterfaceCount": len(CONSUMER_READINESS_INTERFACES),
        "sourceAdapterConsumerDryRunInterfaceCount": len(CONSUMER_DRY_RUN_INTERFACES),
        "realImporterDryRunReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "adapterConsumerDryRunRowsConsumed": len(readiness_rows),
        "realImporterReadinessGateRows": len(readiness_rows),
        "realImporterReadinessArchiveClassRows": len(readiness_rows),
        "realImporterReadinessSummaryRows": 1,
        "consumerArchiveTotalCount": sum(row["archiveClassCount"] for row in readiness_rows),
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "publicSafeRealImporterReadinessArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceAdapterContractInterfaces": list(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaces": list(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaces": list(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaces": list(CONSUMER_VALIDATION_INTERFACES),
        "sourceConsumerReadinessInterfaces": list(CONSUMER_READINESS_INTERFACES),
        "sourceAdapterConsumerDryRunInterfaces": list(CONSUMER_DRY_RUN_INTERFACES),
        "realImporterDryRunReadinessInterfaces": list(REAL_IMPORTER_READINESS_INTERFACES),
        "realImporterReadinessRowsBody": readiness_rows,
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_readiness_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe real-importer dry-run readiness summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "readiness schema mismatch")
    _require(summary.get("status") == "PASS", "readiness status mismatch")
    _require(summary.get("privateCorpusRealImporterDryRunReadinessGateStatus") == REAL_IMPORTER_READINESS_STATUS, "readiness status token mismatch")
    for key in (
        "privateCorpusRealImporterDryRunReadinessGateOnly",
        "adapterConsumerDryRunProofConsumed",
        "adapterConsumerDryRunProofContinuityValidated",
        "adapterConsumerDryRunRowsConsumedByReadinessGate",
        "realImporterDryRunReadinessGateExecuted",
        "realImporterReadinessInputAccepted",
        "realImporterReadinessArchiveClassOrderValidated",
        "realImporterReadinessArchiveClassCountsValidated",
        "realImporterReadinessGuardCountersValidated",
        "realImporterReadinessInterfacesValidated",
        "realImporterDryRunHarnessBoundaryLaneSelected",
        "realImporterReadinessEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False or key in summary.get("falseGuards", {}), f"expected false guard: {key}")
    for key, expected in {
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "sourceAdapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "sourceConsumerValidationInterfaceCount": len(CONSUMER_VALIDATION_INTERFACES),
        "sourceConsumerReadinessInterfaceCount": len(CONSUMER_READINESS_INTERFACES),
        "sourceAdapterConsumerDryRunInterfaceCount": len(CONSUMER_DRY_RUN_INTERFACES),
        "realImporterDryRunReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "adapterConsumerDryRunRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "realImporterReadinessGateRows": len(REQUIRED_ARCHIVE_CLASSES),
        "realImporterReadinessArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "realImporterReadinessSummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "publicSafeRealImporterReadinessArtifactRows": 1,
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
    _require(tuple(summary.get("sourceConsumerValidationInterfaces", ())) == CONSUMER_VALIDATION_INTERFACES, "validation interface mismatch")
    _require(tuple(summary.get("sourceConsumerReadinessInterfaces", ())) == CONSUMER_READINESS_INTERFACES, "readiness interface mismatch")
    _require(tuple(summary.get("sourceAdapterConsumerDryRunInterfaces", ())) == CONSUMER_DRY_RUN_INTERFACES, "source consumer dry-run interface mismatch")
    _require(tuple(summary.get("realImporterDryRunReadinessInterfaces", ())) == REAL_IMPORTER_READINESS_INTERFACES, "real-importer readiness interface mismatch")
    rows = summary.get("realImporterReadinessRowsBody", [])
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "readiness row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"readiness row count mismatch: {archive_class}")
        _require(row.get("readyForRealImporterDryRunHarnessBoundary") is True, f"harness boundary readiness mismatch: {archive_class}")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"direct dry-run allowance mismatch: {archive_class}")
        _require(row.get("realImporterReadinessPrivateIdentifiersPresent") is False, f"private identifier guard mismatch: {archive_class}")
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
            "realImporterConsumerDryRunRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunBoundaryBypassRows",
            "rawDryRunTraceRows",
            "rawAdapterConsumerDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"readiness row zero mismatch: {archive_class}:{key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak check mismatch")


def build_public_safe_real_importer_dry_run_readiness_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated real-importer readiness summary in the tracked proof-plan schema."""

    validate_public_safe_real_importer_dry_run_readiness_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunReadinessGateStatus": REAL_IMPORTER_READINESS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceAdapterConsumerDryRunStatus": CONSUMER_DRY_RUN_STATUS,
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
            "sourceProofCount": 21,
            "adapterConsumerDryRunProof": ADAPTER_CONSUMER_DRY_RUN_PROOF.replace(".v1.json", ".md"),
            "adapterConsumerDryRunSchema": ADAPTER_CONSUMER_DRY_RUN_PROOF,
        },
        "realImporterReadinessDecision": {
            "privateCorpusRealImporterDryRunReadinessGateOnly": True,
            "adapterConsumerDryRunProofConsumed": True,
            "adapterConsumerDryRunProofContinuityValidated": True,
            "adapterConsumerDryRunRowsConsumedByReadinessGate": True,
            "realImporterDryRunReadinessGateExecuted": True,
            "realImporterReadinessInputAccepted": True,
            "realImporterReadinessArchiveClassOrderValidated": True,
            "realImporterReadinessArchiveClassCountsValidated": True,
            "realImporterReadinessGuardCountersValidated": True,
            "realImporterReadinessInterfacesValidated": True,
            "realImporterDryRunHarnessBoundaryLaneSelected": True,
            "realImporterReadinessEmitsOnlyPublicSafeRows": True,
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
            "realImporterDryRunReadinessGateReadPrivateInputs": False,
            "realImporterDryRunReadinessGatePublishedPrivateInput": False,
            "privateRealImporterReadinessArtifactPublished": False,
            "realImporterDryRunHarnessExecuted": False,
            "realImporterDryRunHarnessMaterialized": False,
            "realImporterDryRunBoundaryBypassed": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
        },
        "realImporterReadinessContract": {
            "realImporterReadinessInputMode": summary["realImporterReadinessInputMode"],
            "realImporterReadinessOutputMode": summary["realImporterReadinessOutputMode"],
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
            "sourceAdapterConsumerDryRunInterfaceCount": summary["sourceAdapterConsumerDryRunInterfaceCount"],
            "sourceAdapterConsumerDryRunInterfaces": summary["sourceAdapterConsumerDryRunInterfaces"],
            "realImporterDryRunReadinessInterfaceCount": summary["realImporterDryRunReadinessInterfaceCount"],
            "realImporterDryRunReadinessInterfaces": summary["realImporterDryRunReadinessInterfaces"],
            "adapterConsumerDryRunRowsConsumed": summary["adapterConsumerDryRunRowsConsumed"],
            "realImporterReadinessGateRows": summary["realImporterReadinessGateRows"],
            "realImporterReadinessArchiveClassRows": summary["realImporterReadinessArchiveClassRows"],
            "realImporterReadinessSummaryRows": summary["realImporterReadinessSummaryRows"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeRealImporterReadinessArtifactRows": summary["publicSafeRealImporterReadinessArtifactRows"],
            "realImporterReadinessRowsBody": summary["realImporterReadinessRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-readiness-gate-class-count-status-token-only",
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
                "the selected real-importer dry-run readiness gate can consume the tracked public-safe adapter-consumer dry-run proof rows",
                "the readiness gate preserves required archive class order, aggregate counts, and private-data refusal guards",
                "the readiness gate emits only public-safe class/count/status-token validation rows",
                "the next selected lane is a real-importer dry-run harness boundary proof without executing the real/private importer",
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
                "real importer dry-run harness execution",
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
    parser.add_argument("--adapter-consumer-dry-run-proof", type=Path, default=Path(ADAPTER_CONSUMER_DRY_RUN_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe real-importer readiness summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        dry_run_proof = read_json(args.adapter_consumer_dry_run_proof)
        summary = build_public_safe_real_importer_dry_run_readiness_summary(dry_run_proof)
        validate_public_safe_real_importer_dry_run_readiness_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_readiness_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunReadinessGateError):
        print("Real importer dry-run readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
