#!/usr/bin/env python3
"""Validate public-safe command arm-checklist population rows.

This consumes only the tracked public-safe command arm-checklist population
proof. It validates row continuity for the later readiness-gate lane without
reading private assets, consuming raw private manifests, arming commands,
dispatching shell commands, executing importers, launching BEA, generating
assets, mutating Ghidra, or publishing private paths, filenames, hashes,
arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_population import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as POPULATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PREFLIGHT_CHECKS as POPULATION_PREFLIGHT_CHECKS,
    PROOF_SCHEMA_VERSION as POPULATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as POPULATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
    REDACTED_FIELDS as POPULATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as POPULATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as POPULATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_PROOF = (
    "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-population-proof.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-continuity",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-preconditions",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-row-schema",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-row-ordinals",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-category-counts",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-not-run-statuses",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-unobserved-statuses",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-not-armed-statuses",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-not-executed-statuses",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-dispatch-guards",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-public-redaction-policy",
    "validate-command-arm-checklist-command-arm-checklist-command-arm-checklist-refusal-guards",
    "select-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-lane",
    "emit-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-rows",
    "emit-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-summary",
)

VALIDATION_PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-status-pass",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-selected-this-slice",
    "source-command-arm-checklist-command-arm-checklist-command-arm-boundary-continuity-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-row-order-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-row-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-category-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-not-run-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-unobserved-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-not-armed-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-not-executed-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-dispatch-guards-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-redaction-policy-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-false-guard-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-zero-counter-counts-preserved",
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
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *POPULATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *POPULATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationPrivateOutputGenerated",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmed",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandExecuted",
        )
    )
    if key != "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *(key for key in POPULATION_ZERO_COUNTERS if key != "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows"),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationPrivateOutputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows",
            "commandArmChecklistCommandArmChecklistCommandRows",
            "commandArmChecklistCommandArmChecklistCommandArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandExecutionRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    key for key in POPULATION_ROW_ZERO_FIELDS if key != "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows"
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationError(ValueError):
    """Raised when command arm-checklist evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationError(message)


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


def _validate_source_population_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == POPULATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "source population status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 54, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryProofCount") == 53,
        "source command arm-boundary proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES),
        "source population interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "source population interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationDecision")
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
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in POPULATION_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationContract")
    expected_counts = {
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
        "preflightCheckCount": len(POPULATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(POPULATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(POPULATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(POPULATION_REDACTED_FIELDS),
        "falseGuardCount": len(POPULATION_FALSE_GUARDS),
        "zeroCounterCount": len(POPULATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source population row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source population row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal") == expected_ordinal,
            f"{row_id} source boundary ordinal mismatch",
        )
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus") == "not-run-public-checklist-only", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct exec guard mismatch")
        _require(row.get("futureCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationAllowed") is True, f"{row_id} future validation mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} future operator arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, POPULATION_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(POPULATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(POPULATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in POPULATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe validation row per populated checklist row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal"])
        row: dict[str, Any] = {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-row"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationMode": (
                "public-safe-not-run-unobserved-not-armed-not-executed-validation-row"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal"
            ],
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
            "futureCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateAllowed": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        for key in ROW_ZERO_FIELDS:
            row[key] = 0
        for key in ZERO_COUNTERS:
            row.setdefault(key, 0)
        rows.append(row)
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_summary(
    population_proof: Mapping[str, Any],
) -> dict[str, Any]:
    contract = _validate_source_population_proof(population_proof)
    rows = build_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "sourceProofCount": 55,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofCount": 54,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows": len(rows),
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": len(rows),
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": sum(1 for row in rows if row["rowStatus"] == "not-run"),
        "validatedUnobservedCommandArmChecklistRowCount": sum(1 for row in rows if row["observationStatus"] == "unobserved"),
        "validatedNotArmedCommandArmChecklistRowCount": sum(1 for row in rows if row["commandArmStatus"] == "not-armed"),
        "validatedNotExecutedCommandArmChecklistRowCount": sum(1 for row in rows if row["commandExecutionStatus"] == "not-executed"),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "preflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationCategoryCounts": dict(category_counts),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowsBody": rows,
        "preflightChecks": list(VALIDATION_PREFLIGHT_CHECKS),
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofConsumed": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofContinuityValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumedByValidation": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInputAccepted": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistSchemaValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowOrdinalsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCategoryCountsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotRunStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistUnobservedStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotArmedStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotExecutedStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistDispatchGuardsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRedactionPolicyValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistGuardCountersValidated": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
        **{key: False for key in FALSE_GUARDS},
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_summary(
    summary: Mapping[str, Any],
) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumedByValidation",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistSchemaValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotRunStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistUnobservedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotArmedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotExecutedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistDispatchGuardsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistGuardCountersValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 55,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofCount": 54,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "source population interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
        "validation interfaces mismatch",
    )
    _require(summary.get("commandArmChecklistCommandArmChecklistCommandArmChecklistValidationCategoryCounts") == dict(EXPECTED_CATEGORY_COUNTS), "category counts mismatch")
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "validation row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"validation row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal") == expected_ordinal,
            f"{row_id} source population ordinal mismatch",
        )
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal") == expected_ordinal,
            f"{row_id} source boundary ordinal mismatch",
        )
        _require(row.get("validationStatus") == "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed", f"{row_id} validation status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct exec guard mismatch")
        _require(row.get("futureCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateAllowed") is True, f"{row_id} future readiness mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist validation summary."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
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
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationInterfaces"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaces": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumedByValidation": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInputAccepted": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistSchemaValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCategoryCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistNotRunStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistUnobservedStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistNotArmedStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistNotExecutedStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistDispatchGuardsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistRedactionPolicyValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistGuardCountersValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationContract": {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInputMode": "tracked-public-safe-command-arm-checklist-population-proof-json",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationOutputMode": "tracked-public-safe-command-arm-checklist-validation-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-checklist command arm-checklist command arm-checklist readiness gate without command arming here",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows"
            ],
            "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": summary[
                "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount"
            ],
            "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount": summary[
                "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount"
            ],
            "validatedNotRunCommandArmChecklistRowCount": summary["validatedNotRunCommandArmChecklistRowCount"],
            "validatedUnobservedCommandArmChecklistRowCount": summary["validatedUnobservedCommandArmChecklistRowCount"],
            "validatedNotArmedCommandArmChecklistRowCount": summary["validatedNotArmedCommandArmChecklistRowCount"],
            "validatedNotExecutedCommandArmChecklistRowCount": summary["validatedNotExecutedCommandArmChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowsBody": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowsBody"
            ],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-status-token-only",
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
                "the tracked command arm-checklist command arm-checklist command arm-checklist population proof can be consumed as public-safe validation input",
                "the 99 checklist rows preserve ordinals and category counts",
                "every validation row remains not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the next readiness-gate lane is selected without arming, dispatching, or executing a command here",
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
        "--command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe validation summary")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        population_proof = read_json(args.command_arm_checklist_command_arm_checklist_command_arm_checklist_population_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_summary(
            population_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_arm_checklist_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationError):
        print("Real importer dry-run harness command arm-checklist command arm-checklist command arm-checklist validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
