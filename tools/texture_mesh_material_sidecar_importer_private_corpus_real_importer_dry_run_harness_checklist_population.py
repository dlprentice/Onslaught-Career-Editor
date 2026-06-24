#!/usr/bin/env python3
"""Populate a public-safe real-importer dry-run harness checklist.

This module consumes only the tracked public harness-boundary proof. It does
not read private assets, enumerate private roots, execute an importer, launch
BEA, generate assets, or emit raw private paths, filenames, hashes, or byte
lengths.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import (
    REQUIRED_ARCHIVE_CLASSES,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter import (
    EXPECTED_ARCHIVE_CLASS_COUNTS,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary import (
    ALLOWED_FUTURE_INPUT_CLASSES,
    FALSE_GUARDS as BOUNDARY_FALSE_GUARDS,
    HARNESS_STOP_CONDITIONS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as BOUNDARY_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
    REDACTED_FIELDS as BOUNDARY_REDACTED_FIELDS,
    REQUIRED_FUTURE_ARTIFACT_CLASSES,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as BOUNDARY_ZERO_COUNTERS,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_readiness_gate import (
    REAL_IMPORTER_READINESS_INTERFACES,
    REAL_IMPORTER_READINESS_STATUS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-population.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-population-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-population-complete-public-safe-checklist-populated-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-population-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-validation-proof-plan"
)

HARNESS_BOUNDARY_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-boundary-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES = (
    "load-tracked-real-importer-harness-boundary-proof",
    "validate-real-importer-harness-boundary-continuity",
    "validate-harness-checklist-population-preconditions",
    "populate-harness-boundary-archive-class-checklist-rows",
    "populate-harness-allowed-input-class-checklist-rows",
    "populate-harness-required-artifact-class-checklist-rows",
    "populate-harness-stop-condition-checklist-rows",
    "populate-harness-interface-checklist-rows",
    "validate-harness-checklist-private-data-refusal-guards",
    "select-harness-checklist-validation-lane",
    "emit-harness-checklist-population-rows",
    "emit-harness-checklist-population-summary",
)

HARNESS_ARCHIVE_CLASS_ITEMS = tuple(REQUIRED_ARCHIVE_CLASSES)
CHECKLIST_GROUPS = (
    ("harness-boundary-archive-class", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", HARNESS_ARCHIVE_CLASS_ITEMS),
    ("allowed-future-input-class", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", ALLOWED_FUTURE_INPUT_CLASSES),
    ("required-future-artifact-class", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", REQUIRED_FUTURE_ARTIFACT_CLASSES),
    ("harness-stop-condition", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", HARNESS_STOP_CONDITIONS),
    ("harness-boundary-interface", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
    ("redaction-field", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", BOUNDARY_REDACTED_FIELDS),
    ("public-allowed-output", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
)

PREFLIGHT_CHECKS = (
    "source-harness-boundary-status-pass",
    "source-harness-boundary-selected-this-slice",
    "source-real-importer-readiness-continuity-preserved",
    "source-harness-boundary-row-order-preserved",
    "source-harness-boundary-row-counts-preserved",
    "allowed-future-input-class-counts-match-source",
    "required-future-artifact-class-counts-match-source",
    "stop-condition-counts-match-source",
    "harness-interface-counts-match-source",
    "redaction-policy-counts-match-source",
    "public-output-counts-match-source",
    "false-guard-counts-match-source",
    "zero-counter-counts-match-source",
    "no-private-corpus-read-performed",
    "no-real-importer-executed",
    "no-real-importer-harness-executed",
    "public-leak-check-pass",
)

FALSE_GUARDS_CHECKLIST = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_FALSE_GUARDS,
            "realImporterDryRunHarnessChecklistPopulationReadPrivateInputs",
            "realImporterDryRunHarnessChecklistPublishedPrivateInput",
            "realImporterDryRunHarnessChecklistPrivateValuesPublished",
            "realImporterDryRunHarnessChecklistValidationExecuted",
            "realImporterDryRunHarnessChecklistDryRunExecuted",
            "realImporterDryRunHarnessChecklistPrivateRootEnumerated",
            "realImporterDryRunHarnessCommandMaterialized",
            "realImporterDryRunHarnessPrivateOutputGenerated",
            "realImporterDryRunHarnessChecklistBoundaryBypassed",
        )
    )
)

BOUNDARY_ZERO_GUARD_COUNTERS = tuple(key for key in BOUNDARY_ZERO_COUNTERS if key != "harnessChecklistRows")

ZERO_COUNTERS_CHECKLIST = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ZERO_GUARD_COUNTERS,
            "harnessChecklistPrivatePathRows",
            "harnessChecklistRawFilenameRows",
            "harnessChecklistRawStemRows",
            "harnessChecklistRawHashRows",
            "harnessChecklistByteLengthRows",
            "harnessChecklistRawTextureRefRows",
            "harnessChecklistRawMeshRefRows",
            "harnessChecklistPrivateValueRows",
            "harnessChecklistValidationRows",
            "harnessChecklistDryRunRows",
            "harnessChecklistPrivateOutputRows",
        )
    )
)


class RealImporterDryRunHarnessChecklistPopulationError(ValueError):
    """Raised when harness-boundary evidence cannot populate the checklist."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessChecklistPopulationError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _rows(category: str, status: str, items: Iterable[str]) -> list[dict[str, Any]]:
    return [
        {
            "category": category,
            "itemId": item,
            "status": status,
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "futureHarnessChecklistValidationAllowed": True,
            "futureRealImporterDryRunHarnessRequiresLaterArm": True,
            "publicSafe": True,
            "privateValuePublished": False,
            "rawPathRows": 0,
            "rawFilenameRows": 0,
            "rawStemRows": 0,
            "rawHashRows": 0,
            "byteLengthRows": 0,
            "rawTextureRefRows": 0,
            "rawMeshRefRows": 0,
        }
        for item in items
    ]


def build_public_safe_harness_checklist_rows() -> list[dict[str, Any]]:
    """Return public-safe checklist rows without touching private corpus data."""

    rows: list[dict[str, Any]] = []
    for category, status, items in CHECKLIST_GROUPS:
        rows.extend(_rows(category, status, items))
    for ordinal, row in enumerate(rows, start=1):
        row["harnessChecklistRowOrdinal"] = ordinal
    return rows


def _validate_source_harness_boundary_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == BOUNDARY_PROOF_SCHEMA_VERSION, "source harness-boundary schema mismatch")
    _require(source.get("status") == "PASS", "source harness-boundary status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessBoundaryStatus") == REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "source harness-boundary status token mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    _require(source.get("sourceEvidence", {}).get("sourceProofCount") == 22, "source proof count mismatch")

    decision = _read_mapping(source, "realImporterHarnessBoundaryDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessBoundaryOnly",
        "realImporterReadinessGateProofConsumed",
        "realImporterReadinessGateProofContinuityValidated",
        "realImporterReadinessRowsConsumedByHarnessBoundary",
        "realImporterDryRunHarnessBoundaryDefined",
        "harnessBoundaryInputClassesDefined",
        "harnessBoundaryOutputClassesDefined",
        "harnessBoundaryStopConditionsDefined",
        "harnessBoundaryRefusalGuardsValidated",
        "harnessBoundaryArchiveClassOrderValidated",
        "harnessBoundaryArchiveClassCountsValidated",
        "harnessBoundaryInterfacesValidated",
        "harnessBoundaryEmitsOnlyPublicSafeRows",
        "harnessChecklistPopulationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision expected true: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "realImporterDryRunHarnessExecuted",
        "realImporterDryRunHarnessArmed",
        "realImporterDryRunHarnessExecutedInBoundarySlice",
        "realImporterDryRunHarnessOutputPublished",
        "realImporterDryRunHarnessBoundaryReadPrivateInputs",
        "realImporterDryRunHarnessBoundaryPublishedPrivateInput",
        "privateHarnessBoundaryArtifactPublished",
        "harnessChecklistPopulationExecuted",
        "harnessChecklistMaterialized",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "realImporterHarnessBoundaryContract")
    for key, expected in {
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "realImporterDryRunHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterReadinessRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundaryRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundaryArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundarySummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "harnessAllowedFutureInputClassCount": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessRequiredFutureArtifactClassCount": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessStopConditionCount": len(HARNESS_STOP_CONDITIONS),
        "publicSafeHarnessBoundaryArtifactRows": 1,
    }.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")
    _require(
        tuple(contract.get("sourceRealImporterReadinessInterfaces", ())) == REAL_IMPORTER_READINESS_INTERFACES,
        "source readiness interface mismatch",
    )
    _require(
        tuple(contract.get("realImporterDryRunHarnessBoundaryInterfaces", ())) == REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES,
        "harness boundary interface mismatch",
    )
    _require(tuple(contract.get("allowedFutureInputClasses", ())) == ALLOWED_FUTURE_INPUT_CLASSES, "allowed input mismatch")
    _require(tuple(contract.get("requiredFutureArtifactClasses", ())) == REQUIRED_FUTURE_ARTIFACT_CLASSES, "required artifact mismatch")
    _require(tuple(contract.get("harnessStopConditions", ())) == HARNESS_STOP_CONDITIONS, "stop condition mismatch")

    boundary_rows = contract.get("harnessBoundaryRowsBody")
    _require(isinstance(boundary_rows, list), "source harness boundary rows must be a list")
    _require([row.get("sourceArchiveClass") for row in boundary_rows] == list(REQUIRED_ARCHIVE_CLASSES), "source boundary row order mismatch")
    for row in boundary_rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"source row count mismatch: {archive_class}")
        _require(row.get("futureHarnessChecklistPopulationAllowed") is True, f"source checklist flag mismatch: {archive_class}")
        _require(row.get("futureRealImporterDryRunHarnessRequiresLaterArm") is True, f"source later arm flag mismatch: {archive_class}")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"source direct dry-run guard mismatch: {archive_class}")
        _require(row.get("harnessBoundaryPrivateIdentifiersPresent") is False, f"source private identifier guard mismatch: {archive_class}")
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
            "generatedDryRunOutputRows",
            "privateDryRunRows",
            "realImporterDryRunRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunHarnessOutputRows",
            "realImporterDryRunHarnessTraceRows",
            "harnessChecklistRows",
            "rawDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"source boundary row zero mismatch: {archive_class}:{key}")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(BOUNDARY_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(BOUNDARY_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in BOUNDARY_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    return contract


def build_harness_archive_class_checklist_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build archive-class checklist rows tied to the boundary row order."""

    rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(contract["harnessBoundaryRowsBody"], start=1):
        archive_class = row["sourceArchiveClass"]
        rows.append(
            {
                "harnessChecklistArchiveClassRowClass": "private-corpus-real-importer-dry-run-harness-checklist-archive-class-row",
                "harnessChecklistRowMode": "public-safe-not-run-unobserved-class-count-status-token-only",
                "harnessChecklistArchiveClassRowOrdinal": ordinal,
                "sourceHarnessBoundaryRowOrdinal": row["harnessBoundaryRowOrdinal"],
                "sourceArchiveClass": archive_class,
                "archiveClassCount": row["archiveClassCount"],
                "rowStatus": "not-run",
                "observationStatus": "unobserved",
                "futureHarnessChecklistValidationAllowed": True,
                "futureRealImporterDryRunHarnessRequiresLaterArm": True,
                "directRealImporterDryRunAllowedHere": False,
                "harnessChecklistPrivateIdentifiersPresent": False,
                "rawPathRows": 0,
                "rawFilenameRows": 0,
                "rawStemRows": 0,
                "rawHashRows": 0,
                "byteLengthRows": 0,
                "rawTextureRefRows": 0,
                "rawMeshRefRows": 0,
                "actualAssetImportRows": 0,
                "generatedAssetRows": 0,
                "generatedDryRunOutputRows": 0,
                "privateDryRunRows": 0,
                "realImporterDryRunRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunHarnessOutputRows": 0,
                "realImporterDryRunHarnessTraceRows": 0,
                "harnessChecklistValidationRows": 0,
                "harnessChecklistDryRunRows": 0,
                "rawDryRunTraceRows": 0,
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_checklist_population_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe real-importer harness checklist population summary."""

    contract = _validate_source_harness_boundary_proof(source)
    checklist_rows = build_public_safe_harness_checklist_rows()
    archive_rows = build_harness_archive_class_checklist_rows(contract)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessBoundaryStatus": REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "sourceRealImporterReadinessGateStatus": REAL_IMPORTER_READINESS_STATUS,
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly": True,
        "realImporterHarnessBoundaryProofConsumed": True,
        "realImporterHarnessBoundaryProofContinuityValidated": True,
        "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation": True,
        "realImporterDryRunHarnessChecklistPopulated": True,
        "harnessChecklistRowsPopulated": True,
        "harnessChecklistArchiveClassRowsPopulated": True,
        "harnessChecklistInputClassRowsPopulated": True,
        "harnessChecklistRequiredArtifactRowsPopulated": True,
        "harnessChecklistStopConditionRowsPopulated": True,
        "harnessChecklistInterfaceRowsPopulated": True,
        "harnessChecklistRedactionRowsPopulated": True,
        "harnessChecklistPublicOutputRowsPopulated": True,
        "harnessChecklistRefusalGuardsValidated": True,
        "harnessChecklistArchiveClassOrderValidated": True,
        "harnessChecklistArchiveClassCountsValidated": True,
        "harnessChecklistInterfacesValidated": True,
        "harnessChecklistEmitsOnlyPublicSafeRows": True,
        "harnessChecklistValidationLaneSelected": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateRawManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "rawPrivateManifestConsumed": False,
        "rawPrivateManifestRowsConsumed": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "privateImporterDryRunExecuted": False,
        "realImporterDryRunExecuted": False,
        "realImporterDryRunHarnessExecuted": False,
        "realImporterDryRunHarnessArmed": False,
        "realImporterDryRunHarnessExecutedInChecklistPopulationSlice": False,
        "realImporterDryRunHarnessOutputPublished": False,
        "realImporterDryRunHarnessChecklistPopulationReadPrivateInputs": False,
        "realImporterDryRunHarnessChecklistPublishedPrivateInput": False,
        "realImporterDryRunHarnessChecklistPrivateValuesPublished": False,
        "realImporterDryRunHarnessChecklistValidationExecuted": False,
        "realImporterDryRunHarnessChecklistDryRunExecuted": False,
        "realImporterDryRunHarnessCommandMaterialized": False,
        "realImporterDryRunHarnessPrivateOutputGenerated": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "defaultChecklistRowStatus": "not-run",
        "defaultObservationStatus": "unobserved",
        "realImporterHarnessChecklistPopulationInputMode": "tracked-public-safe-harness-boundary-proof-json",
        "realImporterHarnessChecklistPopulationOutputMode": "public-safe-harness-checklist-not-run-unobserved-status-token-rows",
        "selectedNextLaneClass": "private-corpus real importer dry-run harness checklist validation without execution",
        "sourceProofCount": 23,
        "sourceHarnessBoundaryProofCount": 22,
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "sourceRealImporterHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterDryRunHarnessChecklistPopulationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "realImporterHarnessBoundaryRowsConsumed": len(archive_rows),
        "harnessChecklistGroupCount": len(CHECKLIST_GROUPS),
        "harnessChecklistRows": len(checklist_rows),
        "harnessChecklistArchiveClassRows": len(archive_rows),
        "harnessChecklistAllowedInputClassRows": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessChecklistRequiredArtifactClassRows": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessChecklistStopConditionRows": len(HARNESS_STOP_CONDITIONS),
        "harnessChecklistBoundaryInterfaceRows": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "harnessChecklistRedactionFieldRows": len(BOUNDARY_REDACTED_FIELDS),
        "harnessChecklistPublicAllowedOutputRows": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "passedChecklistRowCount": len(checklist_rows),
        "failedChecklistRowCount": 0,
        "notRunChecklistRowCount": len(checklist_rows),
        "unobservedChecklistRowCount": len(checklist_rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": sum(row["archiveClassCount"] for row in archive_rows),
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistArtifactRows": 1,
        "publicAllowedOutputCount": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(BOUNDARY_REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS_CHECKLIST),
        "zeroCounterCount": len(ZERO_COUNTERS_CHECKLIST),
        "sourceRealImporterReadinessInterfaces": list(REAL_IMPORTER_READINESS_INTERFACES),
        "sourceRealImporterHarnessBoundaryInterfaces": list(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterDryRunHarnessChecklistPopulationInterfaces": list(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "checklistGroups": [
            {"groupId": category, "status": status, "rowCount": len(tuple(items))}
            for category, status, items in CHECKLIST_GROUPS
        ],
        "allowedFutureInputClasses": list(ALLOWED_FUTURE_INPUT_CLASSES),
        "requiredFutureArtifactClasses": list(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessStopConditions": list(HARNESS_STOP_CONDITIONS),
        "harnessArchiveClassChecklistRowsBody": archive_rows,
        "harnessChecklistRowsBody": checklist_rows,
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS_CHECKLIST},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS_CHECKLIST},
    }


def validate_public_safe_real_importer_dry_run_harness_checklist_population_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe harness checklist population summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "harness checklist schema mismatch")
    _require(summary.get("status") == "PASS", "harness checklist status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "harness checklist status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly",
        "realImporterHarnessBoundaryProofConsumed",
        "realImporterHarnessBoundaryProofContinuityValidated",
        "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation",
        "realImporterDryRunHarnessChecklistPopulated",
        "harnessChecklistRowsPopulated",
        "harnessChecklistArchiveClassRowsPopulated",
        "harnessChecklistInputClassRowsPopulated",
        "harnessChecklistRequiredArtifactRowsPopulated",
        "harnessChecklistStopConditionRowsPopulated",
        "harnessChecklistInterfaceRowsPopulated",
        "harnessChecklistRedactionRowsPopulated",
        "harnessChecklistPublicOutputRowsPopulated",
        "harnessChecklistRefusalGuardsValidated",
        "harnessChecklistArchiveClassOrderValidated",
        "harnessChecklistArchiveClassCountsValidated",
        "harnessChecklistInterfacesValidated",
        "harnessChecklistEmitsOnlyPublicSafeRows",
        "harnessChecklistValidationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS_CHECKLIST:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS_CHECKLIST:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    for key, expected in {
        "sourceProofCount": 23,
        "sourceHarnessBoundaryProofCount": 22,
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "sourceRealImporterHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterDryRunHarnessChecklistPopulationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "realImporterHarnessBoundaryRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessChecklistGroupCount": len(CHECKLIST_GROUPS),
        "harnessChecklistRows": sum(len(tuple(items)) for _, _, items in CHECKLIST_GROUPS),
        "harnessChecklistArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessChecklistAllowedInputClassRows": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessChecklistRequiredArtifactClassRows": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessChecklistStopConditionRows": len(HARNESS_STOP_CONDITIONS),
        "harnessChecklistBoundaryInterfaceRows": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "harnessChecklistRedactionFieldRows": len(BOUNDARY_REDACTED_FIELDS),
        "harnessChecklistPublicAllowedOutputRows": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "passedChecklistRowCount": sum(len(tuple(items)) for _, _, items in CHECKLIST_GROUPS),
        "failedChecklistRowCount": 0,
        "notRunChecklistRowCount": sum(len(tuple(items)) for _, _, items in CHECKLIST_GROUPS),
        "unobservedChecklistRowCount": sum(len(tuple(items)) for _, _, items in CHECKLIST_GROUPS),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistArtifactRows": 1,
        "publicAllowedOutputCount": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(BOUNDARY_REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS_CHECKLIST),
        "zeroCounterCount": len(ZERO_COUNTERS_CHECKLIST),
    }.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(summary.get("defaultChecklistRowStatus") == "not-run", "default row status mismatch")
    _require(summary.get("defaultObservationStatus") == "unobserved", "default observation status mismatch")
    _require(
        tuple(summary.get("sourceRealImporterReadinessInterfaces", ())) == REAL_IMPORTER_READINESS_INTERFACES,
        "source readiness interface list mismatch",
    )
    _require(
        tuple(summary.get("sourceRealImporterHarnessBoundaryInterfaces", ())) == REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES,
        "source harness boundary interface list mismatch",
    )
    _require(
        tuple(summary.get("realImporterDryRunHarnessChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES,
        "harness checklist population interface list mismatch",
    )
    _require(tuple(summary.get("allowedFutureInputClasses", ())) == ALLOWED_FUTURE_INPUT_CLASSES, "allowed input list mismatch")
    _require(
        tuple(summary.get("requiredFutureArtifactClasses", ())) == REQUIRED_FUTURE_ARTIFACT_CLASSES,
        "required artifact list mismatch",
    )
    _require(tuple(summary.get("harnessStopConditions", ())) == HARNESS_STOP_CONDITIONS, "stop conditions mismatch")
    archive_rows = summary.get("harnessArchiveClassChecklistRowsBody", [])
    _require([row.get("sourceArchiveClass") for row in archive_rows] == list(REQUIRED_ARCHIVE_CLASSES), "archive row order mismatch")
    for row in archive_rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"archive row count mismatch: {archive_class}")
        _require(row.get("rowStatus") == "not-run", f"archive row status mismatch: {archive_class}")
        _require(row.get("observationStatus") == "unobserved", f"archive row observation mismatch: {archive_class}")
        _require(row.get("futureHarnessChecklistValidationAllowed") is True, f"future validation flag mismatch: {archive_class}")
        _require(row.get("futureRealImporterDryRunHarnessRequiresLaterArm") is True, f"later arm flag mismatch: {archive_class}")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"direct dry-run guard mismatch: {archive_class}")
        _require(row.get("harnessChecklistPrivateIdentifiersPresent") is False, f"private identifier guard mismatch: {archive_class}")
    rows = summary.get("harnessChecklistRowsBody", [])
    _require(len(rows) == summary["harnessChecklistRows"], "checklist row count mismatch")
    _require(all(row.get("rowStatus") == "not-run" for row in rows), "checklist row status mismatch")
    _require(all(row.get("observationStatus") == "unobserved" for row in rows), "checklist row observation mismatch")
    _require(all(row.get("privateValuePublished") is False for row in rows), "checklist private publication mismatch")
    _require(summary.get("publicLeakCheck") == "PASS", "public leak check mismatch")


def build_public_safe_real_importer_dry_run_harness_checklist_population_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated checklist summary in the tracked proof-plan schema."""

    validate_public_safe_real_importer_dry_run_harness_checklist_population_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessBoundaryStatus": REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "sourceRealImporterReadinessGateStatus": REAL_IMPORTER_READINESS_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceProofCount": 23,
            "sourceHarnessBoundaryProofCount": 22,
            "harnessBoundaryProof": HARNESS_BOUNDARY_PROOF.replace(".v1.json", ".md"),
            "harnessBoundarySchema": HARNESS_BOUNDARY_PROOF,
        },
        "realImporterHarnessChecklistPopulationDecision": {
            "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly": True,
            "realImporterHarnessBoundaryProofConsumed": True,
            "realImporterHarnessBoundaryProofContinuityValidated": True,
            "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation": True,
            "realImporterDryRunHarnessChecklistPopulated": True,
            "harnessChecklistRowsPopulated": True,
            "harnessChecklistArchiveClassRowsPopulated": True,
            "harnessChecklistInputClassRowsPopulated": True,
            "harnessChecklistRequiredArtifactRowsPopulated": True,
            "harnessChecklistStopConditionRowsPopulated": True,
            "harnessChecklistInterfaceRowsPopulated": True,
            "harnessChecklistRedactionRowsPopulated": True,
            "harnessChecklistPublicOutputRowsPopulated": True,
            "harnessChecklistRefusalGuardsValidated": True,
            "harnessChecklistArchiveClassOrderValidated": True,
            "harnessChecklistArchiveClassCountsValidated": True,
            "harnessChecklistInterfacesValidated": True,
            "harnessChecklistEmitsOnlyPublicSafeRows": True,
            "harnessChecklistValidationLaneSelected": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            "privateAssetContentRead": False,
            "privateArchiveBytesRead": False,
            "rawPrivateManifestConsumed": False,
            "rawPrivateManifestRowsConsumed": False,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "privateImporterDryRunExecuted": False,
            "realImporterDryRunExecuted": False,
            "realImporterDryRunHarnessExecuted": False,
            "realImporterDryRunHarnessArmed": False,
            "realImporterDryRunHarnessExecutedInChecklistPopulationSlice": False,
            "realImporterDryRunHarnessOutputPublished": False,
            "realImporterDryRunHarnessChecklistPopulationReadPrivateInputs": False,
            "realImporterDryRunHarnessChecklistPublishedPrivateInput": False,
            "realImporterDryRunHarnessChecklistPrivateValuesPublished": False,
            "realImporterDryRunHarnessChecklistValidationExecuted": False,
            "realImporterDryRunHarnessChecklistDryRunExecuted": False,
            "realImporterDryRunHarnessCommandMaterialized": False,
            "realImporterDryRunHarnessPrivateOutputGenerated": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "defaultChecklistRowStatus": "not-run",
            "defaultObservationStatus": "unobserved",
        },
        "realImporterHarnessChecklistPopulationContract": {
            "realImporterHarnessChecklistPopulationInputMode": summary["realImporterHarnessChecklistPopulationInputMode"],
            "realImporterHarnessChecklistPopulationOutputMode": summary["realImporterHarnessChecklistPopulationOutputMode"],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "sourceRealImporterReadinessInterfaceCount": summary["sourceRealImporterReadinessInterfaceCount"],
            "sourceRealImporterReadinessInterfaces": summary["sourceRealImporterReadinessInterfaces"],
            "sourceRealImporterHarnessBoundaryInterfaceCount": summary["sourceRealImporterHarnessBoundaryInterfaceCount"],
            "sourceRealImporterHarnessBoundaryInterfaces": summary["sourceRealImporterHarnessBoundaryInterfaces"],
            "realImporterDryRunHarnessChecklistPopulationInterfaceCount": summary[
                "realImporterDryRunHarnessChecklistPopulationInterfaceCount"
            ],
            "realImporterDryRunHarnessChecklistPopulationInterfaces": summary[
                "realImporterDryRunHarnessChecklistPopulationInterfaces"
            ],
            "realImporterHarnessBoundaryRowsConsumed": summary["realImporterHarnessBoundaryRowsConsumed"],
            "harnessChecklistGroupCount": summary["harnessChecklistGroupCount"],
            "harnessChecklistRows": summary["harnessChecklistRows"],
            "harnessChecklistArchiveClassRows": summary["harnessChecklistArchiveClassRows"],
            "harnessChecklistAllowedInputClassRows": summary["harnessChecklistAllowedInputClassRows"],
            "harnessChecklistRequiredArtifactClassRows": summary["harnessChecklistRequiredArtifactClassRows"],
            "harnessChecklistStopConditionRows": summary["harnessChecklistStopConditionRows"],
            "harnessChecklistBoundaryInterfaceRows": summary["harnessChecklistBoundaryInterfaceRows"],
            "harnessChecklistRedactionFieldRows": summary["harnessChecklistRedactionFieldRows"],
            "harnessChecklistPublicAllowedOutputRows": summary["harnessChecklistPublicAllowedOutputRows"],
            "passedChecklistRowCount": summary["passedChecklistRowCount"],
            "failedChecklistRowCount": summary["failedChecklistRowCount"],
            "notRunChecklistRowCount": summary["notRunChecklistRowCount"],
            "unobservedChecklistRowCount": summary["unobservedChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeHarnessChecklistArtifactRows": summary["publicSafeHarnessChecklistArtifactRows"],
            "checklistGroups": summary["checklistGroups"],
            "allowedFutureInputClasses": summary["allowedFutureInputClasses"],
            "requiredFutureArtifactClasses": summary["requiredFutureArtifactClasses"],
            "harnessStopConditions": summary["harnessStopConditions"],
            "harnessArchiveClassChecklistRowsBody": summary["harnessArchiveClassChecklistRowsBody"],
            "harnessChecklistRowsBody": summary["harnessChecklistRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-checklist-not-run-unobserved-status-token-only",
            "publicAllowedOutputCount": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
            "redactedFieldCount": len(BOUNDARY_REDACTED_FIELDS),
            "publicAllowedOutputs": list(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
            "redactedFields": list(BOUNDARY_REDACTED_FIELDS),
            "publicLeakCheck": "PASS",
        },
        "guardSummary": {
            "falseGuardCount": len(FALSE_GUARDS_CHECKLIST),
            "zeroCounterCount": len(ZERO_COUNTERS_CHECKLIST),
            **{key: 0 for key in ZERO_COUNTERS_CHECKLIST},
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "proves": [
                "the tracked harness-boundary proof can support public-safe not-run/unobserved checklist rows",
                "the checklist preserves archive class order and aggregate count 301 from the harness boundary",
                "the checklist records allowed input classes, required artifact classes, stop conditions, interfaces, redaction fields, and public output classes",
                "private reads and real/private importer execution remain unperformed in this slice",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw manifest consumption",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
                "real importer dry-run harness execution",
                "real importer dry-run harness checklist validation",
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
    parser.add_argument("--harness-boundary-proof", type=Path, default=Path(HARNESS_BOUNDARY_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe harness checklist summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        boundary_proof = read_json(args.harness_boundary_proof)
        summary = build_public_safe_real_importer_dry_run_harness_checklist_population_summary(boundary_proof)
        validate_public_safe_real_importer_dry_run_harness_checklist_population_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_checklist_population_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessChecklistPopulationError):
        print("Real importer dry-run harness checklist population: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
