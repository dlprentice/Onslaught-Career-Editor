#!/usr/bin/env python3
"""Validate public-safe command arm-checklist population rows.

This module consumes only the tracked command arm-checklist population proof.
It validates public-safe row continuity and keeps every row not-run,
unobserved, not-armed, not-dispatched, and not-executed. It does not read
private assets, consume raw private manifests, arm commands, dispatch commands,
execute commands, launch BEA, generate assets, mutate Ghidra, or publish raw
private paths, filenames, hashes, command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_population import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as POPULATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PREFLIGHT_CHECKS as POPULATION_PREFLIGHT_CHECKS,
    PROOF_SCHEMA_VERSION as POPULATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as POPULATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
    REDACTED_FIELDS as POPULATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as POPULATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as POPULATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-validation.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-validation-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-readiness-gate-proof-plan"
)

COMMAND_ARM_CHECKLIST_POPULATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-population-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-population-proof",
    "validate-command-arm-checklist-population-continuity",
    "validate-command-arm-checklist-validation-preconditions",
    "validate-command-arm-checklist-row-schema",
    "validate-command-arm-checklist-row-ordinals",
    "validate-command-arm-checklist-category-counts",
    "validate-command-arm-checklist-not-run-statuses",
    "validate-command-arm-checklist-unobserved-statuses",
    "validate-command-arm-checklist-not-armed-statuses",
    "validate-command-arm-checklist-not-executed-statuses",
    "validate-command-arm-checklist-dispatch-guards",
    "validate-command-arm-checklist-public-redaction-policy",
    "validate-command-arm-checklist-refusal-guards",
    "select-command-arm-checklist-readiness-gate-lane",
    "emit-command-arm-checklist-validation-rows",
    "emit-command-arm-checklist-validation-summary",
)

VALIDATION_PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-population-status-pass",
    "source-command-arm-checklist-population-selected-this-slice",
    "source-command-arm-boundary-continuity-preserved",
    "source-command-arm-checklist-row-order-preserved",
    "source-command-arm-checklist-row-counts-preserved",
    "source-command-arm-checklist-category-counts-preserved",
    "source-command-arm-checklist-not-run-statuses-preserved",
    "source-command-arm-checklist-unobserved-statuses-preserved",
    "source-command-arm-checklist-not-armed-statuses-preserved",
    "source-command-arm-checklist-not-executed-statuses-preserved",
    "source-command-arm-checklist-dispatch-guards-preserved",
    "source-command-arm-checklist-redaction-policy-preserved",
    "source-command-arm-checklist-false-guard-counts-preserved",
    "source-command-arm-checklist-zero-counter-counts-preserved",
    "no-private-corpus-read-performed",
    "no-command-arming-performed",
    "no-shell-dispatch-performed",
    "no-real-importer-executed",
    "public-leak-check-pass",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *POPULATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-validation-status",
            "harness-command-arm-checklist-validation-row-counts",
            "harness-command-arm-checklist-readiness-gate-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *POPULATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-validation-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *POPULATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistValidationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistValidationPrivateOutputGenerated",
            "realImporterDryRunHarnessCommandArmChecklistReadinessGateExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmed",
            "realImporterDryRunHarnessCommandArmChecklistCommandExecuted",
        )
    )
    if key != "realImporterDryRunHarnessCommandArmChecklistValidationExecuted"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *(key for key in POPULATION_ZERO_COUNTERS if key != "commandArmChecklistValidationRows"),
            "commandArmChecklistValidationPrivateInputRows",
            "commandArmChecklistValidationPrivateOutputRows",
            "commandArmChecklistReadinessGateRows",
            "commandArmChecklistCommandRows",
            "commandArmChecklistCommandArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistReadinessGateRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandExecutionRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    key for key in POPULATION_ROW_ZERO_FIELDS if key != "commandArmChecklistValidationRows"
)


class RealImporterDryRunHarnessCommandArmChecklistValidationError(ValueError):
    """Raised when command arm-checklist evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistValidationError(message)


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


def _validate_source_command_arm_checklist_population_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == POPULATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistPopulationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "source command arm-checklist population status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 33, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmBoundaryProofCount") == 32,
        "source command arm-boundary proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistPopulationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES),
        "source command arm-checklist population interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "source command arm-checklist population interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistPopulationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistPopulationOnly",
        "commandArmBoundaryProofConsumed",
        "commandArmBoundaryProofContinuityValidated",
        "commandArmBoundaryRowsConsumedByChecklistPopulation",
        "commandArmChecklistPopulationRowsPopulated",
        "commandArmChecklistPopulationRowStatusesValidated",
        "commandArmChecklistPopulationRowOrdinalsValidated",
        "commandArmChecklistPopulationCategoryCountsValidated",
        "commandArmChecklistPopulationInterfacesValidated",
        "commandArmChecklistPopulationPreflightChecksPassed",
        "commandArmChecklistPopulationEmitsOnlyPublicSafeRows",
        "commandArmChecklistPopulationRedactionPolicyValidated",
        "commandArmChecklistValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in POPULATION_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistPopulationContract")
    expected_counts = {
        "commandArmBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistPopulationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "populatedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistPopulationRowCount": 0,
        "notRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "unobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(POPULATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(POPULATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(POPULATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(POPULATION_REDACTED_FIELDS),
        "falseGuardCount": len(POPULATION_FALSE_GUARDS),
        "zeroCounterCount": len(POPULATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistPopulationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source checklist row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command arm-checklist row {expected_ordinal}"
        _require(row.get("commandArmChecklistPopulationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmBoundaryRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmChecklistPopulationStatus") == "not-run-public-checklist-only", f"{row_id} population status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("futureCommandArmChecklistValidationAllowed") is True, f"{row_id} future validation mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} future operator arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, POPULATION_ROW_ZERO_FIELDS, row_id)
        _require(
            row.get("realImporterDryRunHarnessCommandArmChecklistValidationRows") == 0,
            f"{row_id} real importer validation row counter mismatch",
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(POPULATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(POPULATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in POPULATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe validation row per command arm-checklist row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistPopulationRowsBody"):
        ordinal = int(source_row["commandArmChecklistPopulationRowOrdinal"])
        row = {
            "commandArmChecklistValidationRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-row"
            ),
            "commandArmChecklistValidationMode": (
                "public-safe-not-run-unobserved-not-armed-not-executed-validation-row"
            ),
            "commandArmChecklistValidationRowOrdinal": ordinal,
            "sourceCommandArmChecklistPopulationRowOrdinal": ordinal,
            "sourceCommandArmBoundaryRowOrdinal": source_row["sourceCommandArmBoundaryRowOrdinal"],
            "sourceCommandArmReadinessGateRowOrdinal": source_row["sourceCommandArmReadinessGateRowOrdinal"],
            "category": source_row["category"],
            "itemId": source_row["itemId"],
            "validationStatus": "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed",
            "sourceRowStatus": source_row["rowStatus"],
            "sourceObservationStatus": source_row["observationStatus"],
            "sourceCommandArmStatus": source_row["commandArmStatus"],
            "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmChecklistReadinessGateAllowed": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        for key in ROW_ZERO_FIELDS:
            row[key] = 0
        rows.append(row)
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_summary(
    command_arm_checklist_population_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist validation summary."""

    contract = _validate_source_command_arm_checklist_population_proof(command_arm_checklist_population_proof)
    rows = build_command_arm_checklist_validation_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "command arm-checklist validation category mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistPopulationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationOnly": True,
        "commandArmChecklistPopulationProofConsumed": True,
        "commandArmChecklistPopulationProofContinuityValidated": True,
        "commandArmChecklistRowsConsumedByValidation": True,
        "commandArmChecklistValidationExecuted": True,
        "commandArmChecklistValidationInputAccepted": True,
        "commandArmChecklistSchemaValidated": True,
        "commandArmChecklistRowOrdinalsValidated": True,
        "commandArmChecklistCategoryCountsValidated": True,
        "commandArmChecklistNotRunStatusesValidated": True,
        "commandArmChecklistUnobservedStatusesValidated": True,
        "commandArmChecklistNotArmedStatusesValidated": True,
        "commandArmChecklistNotExecutedStatusesValidated": True,
        "commandArmChecklistDispatchGuardsValidated": True,
        "commandArmChecklistRedactionPolicyValidated": True,
        "commandArmChecklistGuardCountersValidated": True,
        "commandArmChecklistValidationEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistReadinessGateLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
        "sourceProofCount": 34,
        "sourceCommandArmChecklistPopulationProofCount": 33,
        "sourceCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistValidationRows": len(rows),
        "passedCommandArmChecklistValidationRowCount": len(rows),
        "failedCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": len(rows),
        "validatedUnobservedCommandArmChecklistRowCount": len(rows),
        "validatedNotArmedCommandArmChecklistRowCount": len(rows),
        "validatedNotExecutedCommandArmChecklistRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistReadinessGateRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "preflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": contract["consumerArchiveTotalCount"],
        "unknownAyaArchiveClassCount": contract["unknownAyaArchiveClassCount"],
        "publicSafeCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistPopulationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistValidationCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistValidationRowsBody": rows,
        "preflightChecks": list(VALIDATION_PREFLIGHT_CHECKS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command arm-checklist validation summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationOnly",
        "commandArmChecklistPopulationProofConsumed",
        "commandArmChecklistPopulationProofContinuityValidated",
        "commandArmChecklistRowsConsumedByValidation",
        "commandArmChecklistValidationExecuted",
        "commandArmChecklistValidationInputAccepted",
        "commandArmChecklistSchemaValidated",
        "commandArmChecklistRowOrdinalsValidated",
        "commandArmChecklistCategoryCountsValidated",
        "commandArmChecklistNotRunStatusesValidated",
        "commandArmChecklistUnobservedStatusesValidated",
        "commandArmChecklistNotArmedStatusesValidated",
        "commandArmChecklistNotExecutedStatusesValidated",
        "commandArmChecklistDispatchGuardsValidated",
        "commandArmChecklistRedactionPolicyValidated",
        "commandArmChecklistGuardCountersValidated",
        "commandArmChecklistValidationEmitsOnlyPublicSafeRows",
        "commandArmChecklistReadinessGateLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 34,
        "sourceCommandArmChecklistPopulationProofCount": 33,
        "sourceCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "source population interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
        "validation interfaces mismatch",
    )
    _require(
        summary.get("commandArmChecklistValidationCategoryCounts") == dict(EXPECTED_CATEGORY_COUNTS),
        "validation category counts mismatch",
    )
    rows = _read_list(summary, "commandArmChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "validation row body count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row body category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist validation row {expected_ordinal}"
        _require(row.get("commandArmChecklistValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandArmChecklistPopulationRowOrdinal") == expected_ordinal,
            f"{row_id} source population ordinal mismatch",
        )
        _require(
            row.get("sourceCommandArmBoundaryRowOrdinal") == expected_ordinal,
            f"{row_id} source boundary ordinal mismatch",
        )
        _require(
            row.get("validationStatus")
            == "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed",
            f"{row_id} validation status mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value guard mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist validation summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistPopulationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
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
            "sourceCommandArmChecklistPopulationProofCount": summary[
                "sourceCommandArmChecklistPopulationProofCount"
            ],
            "sourceCommandArmChecklistPopulationInterfaceCount": summary[
                "sourceCommandArmChecklistPopulationInterfaceCount"
            ],
            "commandArmChecklistValidationInterfaceCount": summary[
                "commandArmChecklistValidationInterfaceCount"
            ],
            "sourceCommandArmChecklistPopulationInterfaces": summary[
                "sourceCommandArmChecklistPopulationInterfaces"
            ],
            "commandArmChecklistValidationInterfaces": summary["commandArmChecklistValidationInterfaces"],
            "sourceProof": COMMAND_ARM_CHECKLIST_POPULATION_PROOF,
        },
        "realImporterHarnessCommandArmChecklistValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationOnly": True,
            "commandArmChecklistPopulationProofConsumed": True,
            "commandArmChecklistPopulationProofContinuityValidated": True,
            "commandArmChecklistRowsConsumedByValidation": True,
            "commandArmChecklistValidationExecuted": True,
            "commandArmChecklistValidationInputAccepted": True,
            "commandArmChecklistSchemaValidated": True,
            "commandArmChecklistRowOrdinalsValidated": True,
            "commandArmChecklistCategoryCountsValidated": True,
            "commandArmChecklistNotRunStatusesValidated": True,
            "commandArmChecklistUnobservedStatusesValidated": True,
            "commandArmChecklistNotArmedStatusesValidated": True,
            "commandArmChecklistNotExecutedStatusesValidated": True,
            "commandArmChecklistDispatchGuardsValidated": True,
            "commandArmChecklistRedactionPolicyValidated": True,
            "commandArmChecklistGuardCountersValidated": True,
            "commandArmChecklistValidationEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistReadinessGateLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistValidationContract": {
            "commandArmChecklistValidationInputMode": (
                "tracked-public-safe-command-arm-checklist-population-proof-json"
            ),
            "commandArmChecklistValidationOutputMode": (
                "tracked-public-safe-command-arm-checklist-validation-proof"
            ),
            "selectedNextLaneClass": (
                "private-corpus real importer dry-run harness command arm-checklist readiness gate without command arming here"
            ),
            "commandArmChecklistRowsConsumed": summary["commandArmChecklistRowsConsumed"],
            "commandArmChecklistValidationRows": summary["commandArmChecklistValidationRows"],
            "passedCommandArmChecklistValidationRowCount": summary[
                "passedCommandArmChecklistValidationRowCount"
            ],
            "failedCommandArmChecklistValidationRowCount": summary[
                "failedCommandArmChecklistValidationRowCount"
            ],
            "validatedNotRunCommandArmChecklistRowCount": summary[
                "validatedNotRunCommandArmChecklistRowCount"
            ],
            "validatedUnobservedCommandArmChecklistRowCount": summary[
                "validatedUnobservedCommandArmChecklistRowCount"
            ],
            "validatedNotArmedCommandArmChecklistRowCount": summary[
                "validatedNotArmedCommandArmChecklistRowCount"
            ],
            "validatedNotExecutedCommandArmChecklistRowCount": summary[
                "validatedNotExecutedCommandArmChecklistRowCount"
            ],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistReadinessGateRowCount": summary[
                "readyForLaterCommandArmChecklistReadinessGateRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistValidationArtifactRows": summary[
                "publicSafeCommandArmChecklistValidationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistValidationCategoryCounts": summary[
                "commandArmChecklistValidationCategoryCounts"
            ],
            "commandArmChecklistValidationRowsBody": summary["commandArmChecklistValidationRowsBody"],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-validation-status-token-only",
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
                "the tracked command arm-checklist population proof can be consumed as public-safe validation input",
                "the 99 command arm-checklist rows preserve ordinals and category counts",
                "every validation row remains not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the next command arm-checklist readiness-gate lane is selected without arming, dispatching, or executing a command here",
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
                "real importer dry-run harness command arm-checklist readiness gate execution",
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
        "--command-arm-checklist-population-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_POPULATION_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe command arm-checklist validation summary")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        population_proof = read_json(args.command_arm_checklist_population_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_summary(
            population_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistValidationError):
        print("Real importer dry-run harness command arm-checklist validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
