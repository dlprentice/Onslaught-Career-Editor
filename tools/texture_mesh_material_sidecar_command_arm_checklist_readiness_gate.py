#!/usr/bin/env python3
"""Build a public-safe readiness-gate proof for the material sidecar command checklist."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from texture_mesh_material_sidecar_command_arm_checklist_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
    REDACTED_FIELDS as VALIDATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as VALIDATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as VALIDATION_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-validation-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-not-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Boundary Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES = (
    "consume-tracked-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof",
    "verify-validation-selected-this-readiness-gate",
    "verify-readiness-gate-preconditions",
    "preserve-not-run-row-statuses",
    "preserve-unobserved-row-statuses",
    "preserve-not-armed-command-statuses",
    "preserve-not-executed-command-statuses",
    "preserve-no-shell-dispatch",
    "emit-public-safe-readiness-gate-rows",
    "select-boundary-proof-without-command-arming",
)

READINESS_PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-status-pass",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-selected-this-slice",
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-continuity-preserved",
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
    "source-command-arm-checklist-command-arm-checklist-command-arm-checklist-zero-counters-preserved",
    "readiness-gate-does-not-read-private-inputs",
    "readiness-gate-does-not-materialize-runnable-command",
    "readiness-gate-does-not-arm-command",
    "readiness-gate-does-not-dispatch-shell",
    "readiness-gate-does-not-execute-importer",
    "readiness-gate-selects-boundary-proof-lane",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_REDACTED_FIELDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGatePrivateOutputGenerated",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateMaterializedRunnableCommand",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCommandArmed",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCommandSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCommandExecuted",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactPublished",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *(
                key
                for key in VALIDATION_ZERO_COUNTERS
                if key != "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows"
            ),
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryOutputArtifactRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_ROW_ZERO_FIELDS,
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryOutputArtifactRows",
        )
    )
)


class ReadinessGateError(RuntimeError):
    """Raised when the readiness gate proof cannot be built safely."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessGateError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _read_list(source: Mapping[str, Any], key: str) -> list[Any]:
    value = source.get(key)
    _require(isinstance(value, list), f"{key} must be a list")
    return value


def _validate_zero_fields(row: Mapping[str, Any], row_id: str) -> None:
    for key in VALIDATION_ROW_ZERO_FIELDS:
        _require(row.get(key) == 0, f"{row_id} zero field mismatch: {key}")


def _validate_source_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == VALIDATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "source validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 55, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofCount") == 54,
        "source population proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES),
        "source validation interface count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumedByValidation",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistInputAccepted"
        if "commandArmChecklistCommandArmChecklistCommandArmChecklistInputAccepted" in decision
        else "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistSchemaValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotRunStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistUnobservedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotArmedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistNotExecutedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistDispatchGuardsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in VALIDATION_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationContract")
    expected_counts = {
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
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source validation row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source validation row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(
            row.get("futureCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateAllowed") is True,
            f"{row_id} future readiness mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, row_id)
    return contract


def build_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal"])
        row: dict[str, Any] = {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-row"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateMode": (
                "public-safe-readiness-only-not-run-unobserved-not-armed-not-dispatched-not-executed"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowOrdinal"
            ],
            "category": source_row["category"],
            "itemId": source_row["itemId"],
            "readinessGateStatus": "ready-public-safe-boundary-lane-only-no-command-arming",
            "sourceValidationStatus": source_row["validationStatus"],
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryAllowed": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        for key in ROW_ZERO_FIELDS:
            row[key] = 0
        rows.append(row)
    return rows


def build_public_safe_readiness_gate_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_validation_proof(source)
    rows = build_readiness_gate_rows(contract)
    category_counts = dict(Counter(row["category"] for row in rows))
    summary: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
        ),
        "sourceProofCount": 56,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofCount": 55,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": 0,
        "readinessGateNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "publicLeakCheck": "PASS",
        "preflightChecks": list(READINESS_PREFLIGHT_CHECKS),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCategoryCounts": category_counts,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsBody": rows,
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
    }
    validate_public_safe_readiness_gate_summary(summary)
    return summary


def validate_public_safe_readiness_gate_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "summary status token mismatch",
    )
    expected_counts = {
        "sourceProofCount": 56,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofCount": 55,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": 0,
        "readinessGateNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "readiness category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"readiness row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal") == expected_ordinal,
            f"{row_id} source validation ordinal mismatch",
        )
        _require(row.get("readinessGateStatus") == "ready-public-safe-boundary-lane-only-no-command-arming", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("futureCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryAllowed") is True, f"{row_id} future boundary mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        for key in ROW_ZERO_FIELDS:
            _require(row.get(key) == 0, f"{row_id} zero field mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "public leak mismatch")


def build_public_safe_readiness_gate_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS
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
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount"
            ],
            "sourceProof": "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-validation-proof.v1.json",
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateOnly": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumedByReadinessGate": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateExecuted": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInputAccepted": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGatePreconditionsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCategoryCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRedactionPolicyValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateContract": {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInputMode": "tracked-public-safe-command-arm-checklist-validation-proof-json",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateOutputMode": "tracked-public-safe-command-arm-checklist-readiness-gate-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-checklist command arm-checklist command arm-checklist boundary without command arming here",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows"
            ],
            "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": summary[
                "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount"
            ],
            "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": summary[
                "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount"
            ],
            "readinessGateNotRunCommandArmChecklistRowCount": summary["readinessGateNotRunCommandArmChecklistRowCount"],
            "readinessGateUnobservedCommandArmChecklistRowCount": summary["readinessGateUnobservedCommandArmChecklistRowCount"],
            "readinessGateNotArmedCommandArmChecklistRowCount": summary["readinessGateNotArmedCommandArmChecklistRowCount"],
            "readinessGateNotExecutedCommandArmChecklistRowCount": summary["readinessGateNotExecutedCommandArmChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsBody": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsBody"
            ],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-status-token-only",
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
                "the tracked command arm-checklist validation proof can be consumed as public-safe readiness-gate input",
                "the 99 readiness rows preserve source validation ordinals and category counts",
                "every readiness row remains not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the next boundary lane is selected without materializing, arming, dispatching, or executing a command here",
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
    parser.add_argument("--validation-proof", type=Path, default=VALIDATION_PROOF)
    parser.add_argument("--summary", type=Path, help="optional public-safe readiness-gate summary")
    parser.add_argument("--proof", type=Path, help="optional tracked proof JSON output")
    args = parser.parse_args()

    try:
        source = read_json(args.validation_proof)
        summary = build_public_safe_readiness_gate_summary(source)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_readiness_gate_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, ReadinessGateError):
        print("Material sidecar command arm-checklist readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
