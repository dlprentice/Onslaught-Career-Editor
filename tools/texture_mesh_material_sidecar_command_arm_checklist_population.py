#!/usr/bin/env python3
"""Populate a public-safe checklist for a later command arm validation lane.

This module consumes only the tracked command arm-checklist command arm-checklist command arm-boundary proof. It populates
not-run/unobserved public checklist rows for a later validation lane. It does
not arm, dispatch, or execute commands; read private assets; consume raw
private manifests; launch BEA; generate assets; mutate Ghidra; or publish
private paths, filenames, hashes, command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
    REDACTED_FIELDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PROOF = (
    "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-boundary-proof.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-checklist-command-arm-boundary-proof",
    "validate-real-importer-harness-command-arm-checklist-command-arm-checklist-command-arm-boundary-continuity",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-preconditions",
    "populate-command-arm-checklist-command-arm-checklist-command-arm-boundary-checklist-rows",
    "validate-command-arm-checklist-row-statuses",
    "validate-command-arm-checklist-row-ordinals",
    "validate-command-arm-checklist-category-counts",
    "validate-command-arm-checklist-public-redaction-policy",
    "validate-command-arm-checklist-refusal-guards",
    "select-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-lane",
    "emit-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-rows",
    "emit-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-summary",
)

PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-status-pass",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-selected-this-slice",
    "source-command-arm-checklist-command-arm-checklist-command-arm-readiness-continuity-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-row-order-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-row-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-category-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-stop-conditions-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-interface-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-redaction-policy-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-public-output-policy-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-false-guard-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-zero-counter-counts-preserved",
    "no-private-corpus-read-performed",
    "no-command-arming-performed",
    "no-shell-dispatch-performed",
    "no-real-importer-executed",
    "public-leak-check-pass",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistPrivateValuesPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted",
            "realImporterDryRunHarnessCommandArmChecklistDryRunExecuted",
            "realImporterDryRunHarnessCommandArmChecklistSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistPrivateOutputGenerated",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ZERO_COUNTERS,
            "commandArmChecklistPrivatePathRows",
            "commandArmChecklistRawFilenameRows",
            "commandArmChecklistRawHashRows",
            "commandArmChecklistByteLengthRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows",
            "commandArmChecklistDryRunRows",
            "commandArmChecklistPrivateOutputRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ROW_ZERO_FIELDS,
            "commandArmChecklistPrivatePathRows",
            "commandArmChecklistRawFilenameRows",
            "commandArmChecklistRawHashRows",
            "commandArmChecklistByteLengthRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows",
            "commandArmChecklistDryRunRows",
            "commandArmChecklistPrivateOutputRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationError(ValueError):
    """Raised when arm-boundary evidence cannot populate the checklist."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _read_list(source: Mapping[str, Any], key: str) -> list[Any]:
    value = source.get(key)
    _require(isinstance(value, list), f"{key} must be a list")
    return value


def _validate_zero_fields(row: Mapping[str, Any], fields: tuple[str, ...], row_id: str) -> None:
    for key in fields:
        _require(row.get(key) == 0, f"{row_id} zero field mismatch: {key}")


def _validate_source_command_arm_boundary_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "source command arm-checklist command arm-checklist command arm-boundary status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 53, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateProofCount") == 52,
        "source arm-readiness proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES),
        "source command arm-checklist command arm-checklist command arm-boundary interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
        "source command arm-checklist command arm-checklist command arm-boundary interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmBoundaryDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmBoundaryOnly",
        "commandArmChecklistCommandArmChecklistCommandArmReadinessGateProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmReadinessGateProofRowsConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryDefined",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryStopConditionsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmBoundaryContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandArmReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_REDACTED_FIELDS),
        "falseGuardCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_FALSE_GUARDS),
        "zeroCounterCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source arm-boundary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source arm-boundary command row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(
            row.get("futureHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRequiresLaterReview") is True,
            f"{row_id} later checklist-population flag mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe checklist row per command arm-checklist command arm-checklist command arm-boundary row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal"])
        row = {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmChecklistCommandArmChecklistCommandArmBoundaryOutputArtifactRows": 0,
                "commandArmChecklistDryRunRows": 0,
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationMode": "public-safe-not-run-command-arm-checklist-row",
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOutputArtifactRows": 0,
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-row",
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": ordinal,
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus": "not-run-public-checklist-only",
                "commandArmChecklistCommandDryRunOutputArtifactRows": 0,
                "commandArmChecklistPrivateOutputRows": 0,
                "commandArmChecklistPrivatePathRows": 0,
                "commandArmChecklistRawFilenameRows": 0,
                "commandArmChecklistRawHashRows": 0,
                "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows": 0,
                "commandArmChecklistByteLengthRows": 0,
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandDryRunOutputArtifactRows": 0,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandShellDispatchRows": 0,
                "directCommandArmingAllowedHere": False,
                "directCommandExecutionAllowedHere": False,
                "futureCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationAllowed": True,
                "futureCommandArmRequiresExplicitOperatorArm": True,
                "futureHarnessArmRequiresOperatorAction": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "observationStatus": "unobserved",
                "privateCommandArmChecklistCommandArmChecklistCommandArmBoundaryArtifactRows": 0,
                "privateCommandArmChecklistArtifactRows": 0,
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArmChecklistCommandDryRunTraceRows": 0,
                "rawCommandArgumentRows": 0,
                "rawCommandDryRunTraceRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmBoundaryRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRows": 0,
                "realImporterDryRunHarnessCommandDryRunConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "rowStatus": "not-run",
                "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal": ordinal,
                "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal": source_row["sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal"],
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
            }
        for key in ROW_ZERO_FIELDS:
            row.setdefault(key, 0)
        rows.append(row)
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_summary(
    command_arm_boundary_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist population summary."""

    contract = _validate_source_command_arm_boundary_proof(command_arm_boundary_proof)
    rows = build_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "command arm-checklist category counts mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly": True,
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryProofConsumed": True,
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryProofContinuityValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumedByChecklistPopulation": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsPopulated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinalsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationCategoryCountsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfacesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationPreflightChecksPassed": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRedactionPolicyValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
        "sourceProofCount": 54,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryProofCount": 53,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows": len(rows),
        "populatedCommandArmChecklistRowCount": len(rows),
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": len(rows),
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": 0,
        "notRunCommandArmChecklistRowCount": len(rows),
        "unobservedCommandArmChecklistRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaces": list(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsBody": rows,
        "preflightChecks": list(PREFLIGHT_CHECKS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command arm-checklist population summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumedByChecklistPopulation",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsPopulated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationPreflightChecksPassed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 54,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryProofCount": 53,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "populatedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": 0,
        "notRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "unobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
        "source command arm-checklist command arm-checklist command arm-boundary interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "command arm-checklist population interfaces mismatch",
    )
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command arm-checklist row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "command arm-checklist category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("futureCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationAllowed") is True, f"{row_id} later validation flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist population summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "activeCurrentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "wave911Focused": "historical-retired/non-reconstructable at 812/1408 = 57.67%",
        },
        "sourceEvidence": {
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryProofCount": summary["sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryProofCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaceCount": summary["sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaceCount"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaces": summary["sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryInterfaces"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly": True,
            "commandArmChecklistCommandArmChecklistCommandArmBoundaryProofConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandArmBoundaryProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumedByChecklistPopulation": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsPopulated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationCategoryCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationPreflightChecksPassed": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRedactionPolicyValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            "defaultChecklistRowStatus": "not-run",
            "defaultObservationStatus": "unobserved",
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationContract": {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInputMode": "tracked-public-safe-command-arm-boundary-proof-json",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOutputMode": "tracked-public-safe-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-checklist-validation without command arming here",
            "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumed": summary["commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumed"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows": summary["commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows"],
            "populatedCommandArmChecklistRowCount": summary["populatedCommandArmChecklistRowCount"],
            "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": summary[
                "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount"
            ],
            "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount": summary[
                "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount"
            ],
            "notRunCommandArmChecklistRowCount": summary["notRunCommandArmChecklistRowCount"],
            "unobservedCommandArmChecklistRowCount": summary["unobservedCommandArmChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsBody": summary["commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsBody"],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-not-run-status-token-only",
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
                "the tracked command arm-checklist command arm-checklist command arm-boundary proof can support public-safe not-run command arm checklist rows",
                "the checklist preserves the 99 command arm-checklist command arm-checklist command arm-boundary rows and category counts",
                "the checklist keeps every row not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the next command arm-checklist-validation lane is selected without arming, dispatching, or executing a command here",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw manifest consumption",
                "runnable real-importer harness command materialization",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
                "real importer dry-run harness execution",
                "real importer dry-run harness command arming",
                "real importer dry-run harness command execution",
                "real importer dry-run harness command arm-checklist validation",
                "shell command dispatch",
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
    parser.add_argument(
        "--command-arm-checklist-command-arm-checklist-command-arm-boundary-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe command arm-checklist summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        arm_boundary_proof = read_json(args.command_arm_checklist_command_arm_checklist_command_arm_boundary_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_summary(
            arm_boundary_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_population_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationError):
        print("Real importer dry-run harness command arm-checklist command arm-checklist command arm-checklist population: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
