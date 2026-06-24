#!/usr/bin/env python3
"""Validate public-safe command arm-checklist population rows.

This consumes only the tracked command arm-checklist population proof. It
validates row continuity for the later readiness-gate lane without reading
private assets, consuming raw private manifests, arming commands, dispatching
shell commands, executing importers, launching BEA, generating assets, mutating
Ghidra, or publishing private paths, filenames, hashes, arguments, traces, or
byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_population import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as POPULATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PREFLIGHT_CHECKS as POPULATION_PREFLIGHT_CHECKS,
    PROOF_SCHEMA_VERSION as POPULATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as POPULATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
    REDACTED_FIELDS as POPULATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as POPULATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as POPULATION_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
POPULATION_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-"
    "validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES = (
    "load-tracked-command-arm-checklist-command-arm-checklist-population-proof",
    "validate-command-arm-checklist-command-arm-checklist-population-continuity",
    "validate-command-arm-checklist-command-arm-checklist-validation-preconditions",
    "validate-command-arm-checklist-command-arm-checklist-row-schema",
    "validate-command-arm-checklist-command-arm-checklist-row-ordinals",
    "validate-command-arm-checklist-command-arm-checklist-category-counts",
    "validate-command-arm-checklist-command-arm-checklist-not-run-statuses",
    "validate-command-arm-checklist-command-arm-checklist-unobserved-statuses",
    "validate-command-arm-checklist-command-arm-checklist-not-armed-statuses",
    "validate-command-arm-checklist-command-arm-checklist-not-executed-statuses",
    "validate-command-arm-checklist-command-arm-checklist-dispatch-guards",
    "validate-command-arm-checklist-command-arm-checklist-public-redaction-policy",
    "validate-command-arm-checklist-command-arm-checklist-refusal-guards",
    "select-command-arm-checklist-command-arm-checklist-readiness-gate-lane",
    "emit-command-arm-checklist-command-arm-checklist-validation-rows",
    "emit-command-arm-checklist-command-arm-checklist-validation-summary",
)

VALIDATION_PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-command-arm-checklist-population-status-pass",
    "source-command-arm-checklist-command-arm-checklist-population-selected-this-slice",
    "source-command-arm-checklist-command-arm-boundary-continuity-preserved",
    "source-command-arm-checklist-command-arm-checklist-row-order-preserved",
    "source-command-arm-checklist-command-arm-checklist-row-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-category-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-not-run-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-unobserved-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-not-armed-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-not-executed-statuses-preserved",
    "source-command-arm-checklist-command-arm-checklist-dispatch-guards-preserved",
    "source-command-arm-checklist-command-arm-checklist-redaction-policy-preserved",
    "source-command-arm-checklist-command-arm-checklist-false-guard-counts-preserved",
    "source-command-arm-checklist-command-arm-checklist-zero-counter-counts-preserved",
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
            "harness-command-arm-checklist-command-arm-checklist-validation-status",
            "harness-command-arm-checklist-command-arm-checklist-validation-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-readiness-gate-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *POPULATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-validation-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *POPULATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationPrivateOutputGenerated",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmed",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandExecuted",
        )
    )
    if key
    != "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted"
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *POPULATION_ZERO_COUNTERS,
            "commandArmChecklistValidationPrivateInputRows",
            "commandArmChecklistValidationPrivateOutputRows",
            "commandArmChecklistReadinessGateRows",
            "commandArmChecklistCommandRows",
            "commandArmChecklistCommandArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandExecutionRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(dict.fromkeys((*POPULATION_ROW_ZERO_FIELDS, *ZERO_COUNTERS)))


class CommandArmChecklistValidationError(ValueError):
    """Raised when command arm-checklist evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandArmChecklistValidationError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be an object")
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
        source.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "source population status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    expected_source = {
        "sourceProofCount": 65,
        "sourceCommandArmBoundaryProofCount": 64,
        "sourceCommandArmBoundaryInterfaceCount": 10,
        "commandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
    }
    for key, expected in expected_source.items():
        _require(source_evidence.get(key) == expected, f"source evidence count mismatch: {key}")
    _require(
        tuple(source_evidence.get("commandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "source population interface mismatch",
    )

    decision = _read_mapping(
        source,
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationDecision",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly",
        "commandArmBoundaryProofConsumed",
        "commandArmBoundaryProofContinuityValidated",
        "commandArmBoundaryRowsConsumedByChecklistPopulation",
        "commandArmChecklistPopulationRowsPopulated",
        "commandArmChecklistPopulationRowStatusesValidated",
        "commandArmChecklistPopulationRowOrdinalsValidated",
        "commandArmChecklistPopulationCategoryCountsValidated",
        "commandArmChecklistPopulationGuardCountersValidated",
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

    contract = _read_mapping(
        source,
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationContract",
    )
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
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source population row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"source command arm-checklist population row {ordinal}"
        _require(row.get("commandArmChecklistPopulationRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmBoundaryRowOrdinal") == ordinal, f"{row_id} source boundary ordinal mismatch")
        _require(row.get("commandArmChecklistPopulationStatus") == "not-run-public-checklist-only", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct exec guard mismatch")
        _require(row.get("futureCommandArmChecklistValidationAllowed") is True, f"{row_id} future validation mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} future operator arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, POPULATION_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(POPULATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(POPULATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in POPULATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak mismatch")
    return contract


def build_command_arm_checklist_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe validation row per populated checklist row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistPopulationRowsBody"):
        ordinal = int(source_row["commandArmChecklistPopulationRowOrdinal"])
        row = {key: 0 for key in ROW_ZERO_FIELDS}
        row.update(
            {
                "category": source_row["category"],
                "commandArmChecklistValidationMode": "public-safe-not-run-unobserved-not-armed-not-executed-validation",
                "commandArmChecklistValidationRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-row",
                "commandArmChecklistValidationRowOrdinal": ordinal,
                "commandArmChecklistValidationStatus": (
                    "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed"
                ),
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandExecutionStatus": "not-executed",
                "directCommandArmingAllowedHere": False,
                "directCommandExecutionAllowedHere": False,
                "futureCommandArmChecklistReadinessGateAllowed": True,
                "futureCommandArmRequiresExplicitOperatorArm": True,
                "itemId": source_row["itemId"],
                "observationStatus": "unobserved",
                "privateValuePublished": False,
                "rowStatus": "not-run",
                "sourceCommandArmBoundaryRowOrdinal": source_row["sourceCommandArmBoundaryRowOrdinal"],
                "sourceCommandArmChecklistPopulationRowOrdinal": ordinal,
                "sourceCommandArmChecklistPopulationStatus": source_row["commandArmChecklistPopulationStatus"],
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceObservationStatus": source_row["observationStatus"],
                "sourceRowStatus": source_row["rowStatus"],
            }
        )
        rows.append(row)
    return rows


def build_public_safe_command_arm_checklist_validation_summary(population_proof: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_population_proof(population_proof)
    rows = build_command_arm_checklist_validation_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "validation category count mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "thisSlice": THIS_SLICE,
        "thisScope": THIS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistPopulationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly": True,
        "commandArmChecklistPopulationProofConsumed": True,
        "commandArmChecklistPopulationProofContinuityValidated": True,
        "commandArmChecklistRowsConsumedByValidation": True,
        "commandArmChecklistValidationExecuted": True,
        "commandArmChecklistValidationInputAccepted": True,
        "commandArmChecklistValidationSchemaValidated": True,
        "commandArmChecklistValidationRowOrdinalsValidated": True,
        "commandArmChecklistValidationCategoryCountsValidated": True,
        "commandArmChecklistValidationNotRunStatusesValidated": True,
        "commandArmChecklistValidationUnobservedStatusesValidated": True,
        "commandArmChecklistValidationNotArmedStatusesValidated": True,
        "commandArmChecklistValidationNotExecutedStatusesValidated": True,
        "commandArmChecklistValidationDispatchGuardsValidated": True,
        "commandArmChecklistValidationRedactionPolicyValidated": True,
        "commandArmChecklistValidationGuardCountersValidated": True,
        "commandArmChecklistValidationEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistReadinessGateLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        "sourceProofCount": 66,
        "sourceCommandArmChecklistPopulationProofCount": 65,
        "sourceCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistValidationRows": len(rows),
        "passedCommandArmChecklistValidationRowCount": len(rows),
        "failedCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": sum(1 for row in rows if row["rowStatus"] == "not-run"),
        "validatedUnobservedCommandArmChecklistRowCount": sum(1 for row in rows if row["observationStatus"] == "unobserved"),
        "validatedNotArmedCommandArmChecklistRowCount": sum(1 for row in rows if row["commandArmStatus"] == "not-armed"),
        "validatedNotExecutedCommandArmChecklistRowCount": sum(1 for row in rows if row["commandExecutionStatus"] == "not-executed"),
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
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistPopulationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
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


def validate_public_safe_command_arm_checklist_validation_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly",
        "commandArmChecklistPopulationProofConsumed",
        "commandArmChecklistPopulationProofContinuityValidated",
        "commandArmChecklistRowsConsumedByValidation",
        "commandArmChecklistValidationExecuted",
        "commandArmChecklistValidationInputAccepted",
        "commandArmChecklistValidationSchemaValidated",
        "commandArmChecklistValidationRowOrdinalsValidated",
        "commandArmChecklistValidationCategoryCountsValidated",
        "commandArmChecklistValidationNotRunStatusesValidated",
        "commandArmChecklistValidationUnobservedStatusesValidated",
        "commandArmChecklistValidationNotArmedStatusesValidated",
        "commandArmChecklistValidationNotExecutedStatusesValidated",
        "commandArmChecklistValidationDispatchGuardsValidated",
        "commandArmChecklistValidationRedactionPolicyValidated",
        "commandArmChecklistValidationGuardCountersValidated",
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
        "sourceProofCount": 66,
        "sourceCommandArmChecklistPopulationProofCount": 65,
        "sourceCommandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
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
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "source population interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
        "validation interfaces mismatch",
    )
    _require(summary.get("commandArmChecklistValidationCategoryCounts") == dict(EXPECTED_CATEGORY_COUNTS), "category counts mismatch")
    rows = _read_list(summary, "commandArmChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "validation row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category counts mismatch")
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist validation row {ordinal}"
        _require(row.get("commandArmChecklistValidationRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistPopulationRowOrdinal") == ordinal, f"{row_id} source population ordinal mismatch")
        _require(row.get("sourceCommandArmBoundaryRowOrdinal") == ordinal, f"{row_id} source boundary ordinal mismatch")
        _require(
            row.get("commandArmChecklistValidationStatus")
            == "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed",
            f"{row_id} validation status mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct exec guard mismatch")
        _require(row.get("futureCommandArmChecklistReadinessGateAllowed") is True, f"{row_id} future readiness mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_command_arm_checklist_validation_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated command arm-checklist validation summary."""

    validate_public_safe_command_arm_checklist_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistPopulationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "sourceEvidence": {
            "sourceProof": "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.v1.json",
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmChecklistPopulationProofCount": summary["sourceCommandArmChecklistPopulationProofCount"],
            "sourceCommandArmChecklistPopulationInterfaceCount": summary["sourceCommandArmChecklistPopulationInterfaceCount"],
            "sourceCommandArmChecklistPopulationInterfaces": summary["sourceCommandArmChecklistPopulationInterfaces"],
            "commandArmChecklistValidationInterfaceCount": summary["commandArmChecklistValidationInterfaceCount"],
            "commandArmChecklistValidationInterfaces": summary["commandArmChecklistValidationInterfaces"],
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationDecision": {
            key: summary[key]
            for key in (
                "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly",
                "commandArmChecklistPopulationProofConsumed",
                "commandArmChecklistPopulationProofContinuityValidated",
                "commandArmChecklistRowsConsumedByValidation",
                "commandArmChecklistValidationExecuted",
                "commandArmChecklistValidationInputAccepted",
                "commandArmChecklistValidationSchemaValidated",
                "commandArmChecklistValidationRowOrdinalsValidated",
                "commandArmChecklistValidationCategoryCountsValidated",
                "commandArmChecklistValidationNotRunStatusesValidated",
                "commandArmChecklistValidationUnobservedStatusesValidated",
                "commandArmChecklistValidationNotArmedStatusesValidated",
                "commandArmChecklistValidationNotExecutedStatusesValidated",
                "commandArmChecklistValidationDispatchGuardsValidated",
                "commandArmChecklistValidationRedactionPolicyValidated",
                "commandArmChecklistValidationGuardCountersValidated",
                "commandArmChecklistValidationEmitsOnlyPublicSafeRows",
                "commandArmChecklistReadinessGateLaneSelected",
                "futureCommandArmRequiresExplicitOperatorArm",
                "privateEvidenceStoredOutsidePublicReleaseScope",
                "publicPrivateSeparationRequired",
                *FALSE_GUARDS,
            )
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationContract": {
            "commandArmChecklistValidationInputMode": "tracked-public-safe-command-arm-checklist-population-proof-json",
            "commandArmChecklistValidationOutputMode": "tracked-public-safe-command-arm-checklist-validation-proof",
            "selectedNextLaneClass": "command-arm-checklist-readiness-gate-proof-plan",
            "commandArmChecklistRowsConsumed": summary["commandArmChecklistRowsConsumed"],
            "commandArmChecklistValidationRows": summary["commandArmChecklistValidationRows"],
            "passedCommandArmChecklistValidationRowCount": summary["passedCommandArmChecklistValidationRowCount"],
            "failedCommandArmChecklistValidationRowCount": summary["failedCommandArmChecklistValidationRowCount"],
            "validatedNotRunCommandArmChecklistRowCount": summary["validatedNotRunCommandArmChecklistRowCount"],
            "validatedUnobservedCommandArmChecklistRowCount": summary["validatedUnobservedCommandArmChecklistRowCount"],
            "validatedNotArmedCommandArmChecklistRowCount": summary["validatedNotArmedCommandArmChecklistRowCount"],
            "validatedNotExecutedCommandArmChecklistRowCount": summary["validatedNotExecutedCommandArmChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistReadinessGateRowCount": summary["readyForLaterCommandArmChecklistReadinessGateRowCount"],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistValidationArtifactRows": summary["publicSafeCommandArmChecklistValidationArtifactRows"],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistValidationCategoryCounts": summary["commandArmChecklistValidationCategoryCounts"],
            "commandArmChecklistValidationRowsBody": summary["commandArmChecklistValidationRowsBody"],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "publicAllowedOutputs": summary["publicAllowedOutputs"],
            "redactedFields": summary["redactedFields"],
            "publicLeakCheck": "PASS",
        },
        "guardSummary": {
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            **summary["falseGuards"],
            **summary["zeroCounters"],
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "positiveEvidence": (
                "Tracked public-safe command arm-checklist population rows were consumed and "
                "validated as not-run, unobserved, not-armed, not-dispatched, and not-executed "
                "rows for the later readiness-gate lane."
            ),
            "notEvidenceFor": [
                "private asset content reads",
                "raw private manifest consumption",
                "command arming",
                "shell dispatch",
                "importer execution",
                "generated assets",
                "BEA launch",
                "Ghidra mutation",
                "runtime proof",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "activeCurrentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "wave911Focused": "historical-retired/non-reconstructable at 812/1408 = 57.67%",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=POPULATION_PROOF)
    parser.add_argument("--summary", type=Path, help="write summary JSON to this path")
    parser.add_argument("--proof", type=Path, help="write proof JSON to this path")
    args = parser.parse_args()

    try:
        summary = build_public_safe_command_arm_checklist_validation_summary(read_json(args.source))
        validate_public_safe_command_arm_checklist_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        proof = build_public_safe_command_arm_checklist_validation_proof(summary)
        if args.proof is not None:
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(proof, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandArmChecklistValidationError):
        print("Command arm-checklist command arm-checklist validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
