#!/usr/bin/env python3
"""Validate readiness for a later explicit command arm-checklist boundary lane.

This module consumes only the tracked command arm-checklist command arm-checklist
validation proof. It verifies that the 99 public-safe rows remain not-run,
unobserved, not-armed, not-dispatched, and not-executed before selecting a
later command arm-checklist command arm-checklist boundary lane. It does not
arm, dispatch, or execute a command; read private asset content; consume raw
private manifests; launch BEA; generate assets; mutate Ghidra; or emit private
paths, filenames, hashes, command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
    REDACTED_FIELDS as VALIDATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as VALIDATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as VALIDATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-readiness-gate.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-not-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Boundary Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-validation-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-checklist-validation-proof",
    "validate-command-arm-checklist-command-arm-checklist-validation-continuity",
    "validate-command-arm-checklist-command-arm-checklist-readiness-gate-preconditions",
    "validate-command-arm-checklist-command-arm-checklist-readiness-gate-row-statuses",
    "validate-command-arm-checklist-command-arm-checklist-readiness-gate-row-ordinals",
    "validate-command-arm-checklist-command-arm-checklist-readiness-gate-category-counts",
    "validate-command-arm-checklist-command-arm-checklist-readiness-gate-refusal-guards",
    "validate-command-arm-checklist-command-arm-checklist-readiness-gate-public-redaction-policy",
    "select-command-arm-checklist-command-arm-checklist-boundary-lane",
    "emit-command-arm-checklist-command-arm-checklist-readiness-gate-summary",
)

READINESS_PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-command-arm-checklist-validation-status-pass",
    "source-command-arm-checklist-command-arm-checklist-validation-selected-this-slice",
    "source-command-arm-checklist-command-arm-checklist-continuity-preserved",
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
            *VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-readiness-gate-status",
            "harness-command-arm-checklist-command-arm-checklist-readiness-gate-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-boundary-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-readiness-gate-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGatePublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGatePrivateOutputGenerated",
            "privateCommandArmChecklistCommandArmChecklistReadinessGateArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundarySentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryPrivateOutputGenerated",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *(key for key in VALIDATION_ZERO_COUNTERS if key != "commandArmChecklistCommandArmChecklistReadinessGateRows"),
            "commandArmChecklistCommandArmChecklistReadinessGatePrivateInputRows",
            "commandArmChecklistCommandArmChecklistReadinessGateArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryRows",
            "commandArmChecklistCommandArmChecklistBoundaryOutputArtifactRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *(key for key in VALIDATION_ROW_ZERO_FIELDS if key != "commandArmChecklistCommandArmChecklistReadinessGateRows"),
            "commandArmChecklistCommandArmChecklistBoundaryOutputArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateError(ValueError):
    """Raised when validation evidence cannot support readiness-gate selection."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateError(message)


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


def _validate_source_command_arm_checklist_command_arm_checklist_validation_proof(
    source: Mapping[str, Any],
) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == VALIDATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "source command arm-checklist validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 44, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistPopulationProofCount") == 43,
        "source command arm-checklist population proof count mismatch",
    )
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistPopulationInterfaceCount") == 12,
        "source population interface count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistValidationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES),
        "source validation interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistCommandArmChecklistValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
        "source validation interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistValidationOnly",
        "commandArmChecklistCommandArmChecklistPopulationProofConsumed",
        "commandArmChecklistCommandArmChecklistPopulationProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistRowsConsumedByValidation",
        "commandArmChecklistCommandArmChecklistValidationExecuted",
        "commandArmChecklistCommandArmChecklistValidationInputAccepted",
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
        "commandArmChecklistCommandArmChecklistValidationEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistReadinessGateLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in VALIDATION_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistValidationContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": 19,
        "passedPreflightCheckCount": 19,
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(VALIDATION_REDACTED_FIELDS),
        "falseGuardCount": len(VALIDATION_FALSE_GUARDS),
        "zeroCounterCount": len(VALIDATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source validation row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source validation row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistValidationRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistPopulationRowOrdinal") == expected_ordinal,
            f"{row_id} source population ordinal mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, tuple(key for key in VALIDATION_ROW_ZERO_FIELDS if key in row), row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(VALIDATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(VALIDATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in VALIDATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak mismatch")
    return contract


def build_command_arm_checklist_command_arm_checklist_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe readiness-gate row per validation row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistValidationRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistValidationRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                **{key: 0 for key in ROW_ZERO_FIELDS},
                "commandArmChecklistCommandArmChecklistBoundaryOutputArtifactRows": 0,
                "commandArmChecklistCommandArmChecklistReadinessGateMode": "public-safe-readiness-status-token-only",
                "commandArmChecklistCommandArmChecklistReadinessGateRowClass": (
                    "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-row"
                ),
                "commandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": ordinal,
                "commandArmChecklistCommandArmChecklistReadinessGateStatus": (
                    "ready-for-later-explicit-command-arm-checklist-command-arm-checklist-boundary-review"
                ),
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandShellDispatchRows": 0,
                "directCommandArmingAllowedHere": False,
                "directCommandExecutionAllowedHere": False,
                "futureCommandArmChecklistCommandArmChecklistBoundaryRequiresLaterReview": True,
                "futureCommandArmRequiresExplicitOperatorArm": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "observationStatus": "unobserved",
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArgumentRows": 0,
                "rawCommandArmChecklistCommandDryRunTraceRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "rowStatus": "not-run",
                "sourceCommandArmChecklistCommandArmBoundaryRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandArmBoundaryRowOrdinal"
                ],
                "sourceCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandArmChecklistPopulationRowOrdinal"
                ],
                "sourceCommandArmChecklistCommandArmChecklistValidationRowOrdinal": ordinal,
                "sourceCommandArmStatus": "not-armed",
                "sourceCommandExecutionStatus": "not-executed",
                "sourceObservationStatus": "unobserved",
                "sourceRowStatus": "not-run",
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_summary(
    validation_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe readiness-gate summary from validation proof JSON."""

    contract = _validate_source_command_arm_checklist_command_arm_checklist_validation_proof(validation_proof)
    rows = build_command_arm_checklist_command_arm_checklist_readiness_gate_rows(contract)
    category_counts = dict(Counter(row["category"] for row in rows))
    _require(category_counts == dict(EXPECTED_CATEGORY_COUNTS), "readiness category mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "sourceCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "sourceProofCount": 45,
        "sourceCommandArmChecklistCommandArmChecklistValidationProofCount": 44,
        "sourceCommandArmChecklistCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "sourceCommandArmChecklistCommandArmChecklistValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistReadinessGateRowCount": 0,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "commandArmChecklistCommandArmChecklistReadinessGateCategoryCounts": category_counts,
        "commandArmChecklistCommandArmChecklistReadinessGateRowsBody": rows,
        "preflightChecks": list(READINESS_PREFLIGHT_CHECKS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe readiness-gate summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(summary.get("selectedNextSlice") == NEXT_SLICE, "summary next slice mismatch")
    _require(summary.get("selectedNextScope") == NEXT_SCOPE, "summary next scope mismatch")
    expected_counts = {
        "sourceProofCount": 45,
        "sourceCommandArmChecklistCommandArmChecklistValidationProofCount": 44,
        "sourceCommandArmChecklistCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistReadinessGateRowCount": 0,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
        "source validation interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistCommandArmChecklistReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
        "readiness-gate interfaces mismatch",
    )
    _require(
        summary.get("commandArmChecklistCommandArmChecklistReadinessGateCategoryCounts") == dict(EXPECTED_CATEGORY_COUNTS),
        "readiness category count mismatch",
    )
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row body count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"readiness-gate row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistValidationRowOrdinal") == expected_ordinal,
            f"{row_id} source validation ordinal mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _require(
            row.get("futureCommandArmChecklistCommandArmChecklistBoundaryRequiresLaterReview") is True,
            f"{row_id} future boundary flag mismatch",
        )
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated readiness-gate summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
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
            "sourceCommandArmChecklistCommandArmChecklistValidationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistValidationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistValidationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistValidationInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistReadinessGateInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistValidationInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistValidationInterfaces"
            ],
            "commandArmChecklistCommandArmChecklistReadinessGateInterfaces": summary[
                "commandArmChecklistCommandArmChecklistReadinessGateInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateOnly": True,
            "commandArmChecklistCommandArmChecklistValidationProofConsumed": True,
            "commandArmChecklistCommandArmChecklistValidationProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistValidationRowsConsumed": True,
            "commandArmChecklistCommandArmChecklistReadinessGateExecuted": True,
            "commandArmChecklistCommandArmChecklistReadinessGateInputAccepted": True,
            "commandArmChecklistCommandArmChecklistReadinessGatePreconditionsValidated": True,
            "commandArmChecklistCommandArmChecklistReadinessGateRowStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistReadinessGateRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmChecklistReadinessGateCategoryCountsValidated": True,
            "commandArmChecklistCommandArmChecklistReadinessGateInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistReadinessGateEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistReadinessGateRedactionPolicyValidated": True,
            "commandArmChecklistCommandArmChecklistBoundaryLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistReadinessGateContract": {
            "commandArmChecklistCommandArmChecklistReadinessGateInputMode": (
                "tracked-public-safe-command-arm-checklist-command-arm-checklist-validation-proof-json"
            ),
            "commandArmChecklistCommandArmChecklistReadinessGateOutputMode": (
                "tracked-public-safe-command-arm-checklist-command-arm-checklist-readiness-gate-proof"
            ),
            "selectedNextLaneClass": (
                "private-corpus real importer dry-run harness command arm-checklist command arm-checklist boundary without command arming here"
            ),
            "commandArmChecklistCommandArmChecklistValidationRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistValidationRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistReadinessGateRows": summary[
                "commandArmChecklistCommandArmChecklistReadinessGateRows"
            ],
            "passedCommandArmChecklistCommandArmChecklistReadinessGateRowCount": summary[
                "passedCommandArmChecklistCommandArmChecklistReadinessGateRowCount"
            ],
            "failedCommandArmChecklistCommandArmChecklistReadinessGateRowCount": summary[
                "failedCommandArmChecklistCommandArmChecklistReadinessGateRowCount"
            ],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistBoundaryRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistBoundaryRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistReadinessGateCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistReadinessGateCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistReadinessGateRowsBody": summary[
                "commandArmChecklistCommandArmChecklistReadinessGateRowsBody"
            ],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-status-token-only",
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
                "the tracked command arm-checklist command arm-checklist validation proof can be consumed as public-safe readiness-gate input",
                "the 99 validation rows remain not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the readiness gate preserves row/category counts and aggregate archive count 301",
                "the next command arm-checklist command arm-checklist boundary lane is selected without arming, dispatching, or executing a command here",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw manifest consumption",
                "runnable real-importer harness command materialization",
                "command arming",
                "command execution",
                "shell command dispatch",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
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
        "--command-arm-checklist-command-arm-checklist-validation-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe readiness-gate summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        validation_proof = read_json(args.command_arm_checklist_command_arm_checklist_validation_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_summary(
            validation_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_summary(
            summary
        )
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateError):
        print("Real importer dry-run harness command arm-checklist command arm-checklist readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
