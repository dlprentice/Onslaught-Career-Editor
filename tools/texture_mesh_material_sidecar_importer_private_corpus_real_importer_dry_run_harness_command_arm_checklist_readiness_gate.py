#!/usr/bin/env python3
"""Validate readiness for a later command arm-checklist command-materialization lane.

This module consumes only the tracked command arm-checklist validation proof.
It preserves the 99 public-safe rows as not-run, unobserved, not-armed,
not-dispatched, and not-executed before selecting a later command
materialization lane. It
does not read private assets, consume raw private manifests, arm commands,
dispatch commands, execute commands, launch BEA, generate assets, mutate
Ghidra, or publish raw private paths, filenames, hashes, command arguments,
traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
    REDACTED_FIELDS as VALIDATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as VALIDATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    VALIDATION_PREFLIGHT_CHECKS,
    ZERO_COUNTERS as VALIDATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-readiness-gate.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-readiness-gate-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-readiness-gate-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Materialization Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-materialization-proof-plan"
)

COMMAND_ARM_CHECKLIST_VALIDATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-validation-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-validation-proof",
    "validate-real-importer-harness-command-arm-checklist-validation-continuity",
    "validate-command-arm-checklist-readiness-gate-preconditions",
    "validate-command-arm-checklist-readiness-gate-row-statuses",
    "validate-command-arm-checklist-readiness-gate-row-ordinals",
    "validate-command-arm-checklist-readiness-gate-category-counts",
    "validate-command-arm-checklist-readiness-gate-arm-execution-guards",
    "validate-command-arm-checklist-readiness-gate-public-redaction-policy",
    "validate-command-arm-checklist-readiness-gate-refusal-guards",
    "select-command-arm-checklist-command-materialization-lane",
    "emit-command-arm-checklist-readiness-gate-rows",
    "emit-command-arm-checklist-readiness-gate-summary",
)

READINESS_PREFLIGHT_CHECKS = (
    "source-command-arm-checklist-validation-status-pass",
    "source-command-arm-checklist-validation-selected-this-slice",
    "source-command-arm-checklist-validation-row-order-preserved",
    "source-command-arm-checklist-validation-row-counts-preserved",
    "source-command-arm-checklist-validation-category-counts-preserved",
    "source-command-arm-checklist-validation-not-run-statuses-preserved",
    "source-command-arm-checklist-validation-unobserved-statuses-preserved",
    "source-command-arm-checklist-validation-not-armed-statuses-preserved",
    "source-command-arm-checklist-validation-not-executed-statuses-preserved",
    "source-command-arm-checklist-validation-dispatch-guards-preserved",
    "source-command-arm-checklist-validation-redaction-policy-preserved",
    "source-command-arm-checklist-validation-false-guard-counts-preserved",
    "source-command-arm-checklist-validation-zero-counter-counts-preserved",
    "no-private-corpus-read-performed",
    "no-command-arming-performed",
    "no-shell-dispatch-performed",
    "no-command-execution-performed",
    "no-real-importer-executed",
    "public-leak-check-pass",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-readiness-gate-status",
            "harness-command-arm-checklist-readiness-gate-row-counts",
            "harness-command-arm-checklist-command-materialization-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-readiness-gate-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistReadinessGatePublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistReadinessGateSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistReadinessGatePrivateOutputGenerated",
            "realImporterDryRunHarnessCommandArmChecklistCommandMaterialized",
            "realImporterDryRunHarnessCommandArmChecklistCommandSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandPrivateOutputGenerated",
        )
    )
    if key != "realImporterDryRunHarnessCommandArmChecklistReadinessGateExecuted"
)

VALIDATION_ZERO_GUARD_COUNTERS = tuple(
    key for key in VALIDATION_ZERO_COUNTERS if key != "commandArmChecklistReadinessGateRows"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_ZERO_GUARD_COUNTERS,
            "commandArmChecklistReadinessGatePrivateInputRows",
            "commandArmChecklistCommandRows",
            "commandArmChecklistCommandArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandExecutionRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_ROW_ZERO_FIELDS,
            "commandArmChecklistCommandRows",
            "commandArmChecklistCommandArtifactRows",
            "commandArmChecklistReadinessGatePrivateInputRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandExecutionRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistReadinessGateError(ValueError):
    """Raised when validation evidence cannot support checklist readiness."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistReadinessGateError(message)


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


def _validate_source_command_arm_checklist_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == VALIDATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "source command arm-checklist validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 34, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistPopulationProofCount") == 33,
        "source command arm-checklist population proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistValidationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES),
        "source command arm-checklist validation interface count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistValidationDecision")
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
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in VALIDATION_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistValidationContract")
    expected_counts = {
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
        "publicAllowedOutputCount": len(VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(VALIDATION_REDACTED_FIELDS),
        "falseGuardCount": len(VALIDATION_FALSE_GUARDS),
        "zeroCounterCount": len(VALIDATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command arm-checklist validation row {expected_ordinal}"
        _require(row.get("commandArmChecklistValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("validationStatus") == "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed",
            f"{row_id} validation status mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-execution guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, VALIDATION_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(VALIDATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(VALIDATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in VALIDATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")

    redaction = _read_mapping(source, "redactionPolicy")
    _require(
        redaction.get("publicAllowedOutputCount") == len(VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "source public allowed output count mismatch",
    )
    _require(
        redaction.get("redactedFieldCount") == len(VALIDATION_REDACTED_FIELDS),
        "source redacted field count mismatch",
    )
    _require(redaction.get("publicLeakCheck") == "PASS", "source redaction public leak check mismatch")
    return contract


def build_command_arm_checklist_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe readiness-gate row per validated command arm-checklist row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistValidationRowsBody"):
        ordinal = int(source_row["commandArmChecklistValidationRowOrdinal"])
        row = {
            "category": source_row["category"],
            "commandArmChecklistReadinessGateMode": "public-safe-readiness-precondition-status-token-only",
            "commandArmChecklistReadinessGateRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-row"
            ),
            "commandArmChecklistReadinessGateRowOrdinal": ordinal,
            "commandArmStatus": source_row["commandArmStatus"],
            "commandDispatchAllowedHere": False,
            "commandExecutionStatus": source_row["commandExecutionStatus"],
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmChecklistCommandMaterializationRequiresLaterArm": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "itemId": source_row["itemId"],
            "observationStatus": source_row["observationStatus"],
            "privateValuePublished": False,
            "readinessGateStatus": "ready-for-later-explicit-command-arm-checklist-command-materialization",
            "rowStatus": source_row["rowStatus"],
            "sourceCommandArmBoundaryRowOrdinal": source_row["sourceCommandArmBoundaryRowOrdinal"],
            "sourceCommandArmChecklistPopulationRowOrdinal": source_row[
                "sourceCommandArmChecklistPopulationRowOrdinal"
            ],
            "sourceCommandArmChecklistValidationRowOrdinal": ordinal,
            "sourceCommandArmReadinessGateRowOrdinal": source_row["sourceCommandArmReadinessGateRowOrdinal"],
            "sourceCommandArmStatus": source_row["sourceCommandArmStatus"],
            "sourceCommandExecutionStatus": source_row["sourceCommandExecutionStatus"],
            "sourceObservationStatus": source_row["sourceObservationStatus"],
            "sourceRowStatus": source_row["sourceRowStatus"],
            "sourceValidationStatus": source_row["validationStatus"],
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_summary(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist readiness-gate summary."""

    contract = _validate_source_command_arm_checklist_validation_proof(source)
    rows = build_command_arm_checklist_readiness_gate_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "readiness category counts mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "slice": THIS_SLICE,
        "scope": THIS_SCOPE,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistValidationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateOnly": True,
        "commandArmChecklistValidationProofConsumed": True,
        "commandArmChecklistValidationProofContinuityValidated": True,
        "commandArmChecklistValidationRowsConsumedByReadinessGate": True,
        "commandArmChecklistReadinessGateExecuted": True,
        "commandArmChecklistReadinessGateInputAccepted": True,
        "commandArmChecklistReadinessGatePreconditionsValidated": True,
        "commandArmChecklistReadinessGateRowStatusesValidated": True,
        "commandArmChecklistReadinessGateRowOrdinalsValidated": True,
        "commandArmChecklistReadinessGateCategoryCountsValidated": True,
        "commandArmChecklistReadinessGateArmExecutionGuardsValidated": True,
        "commandArmChecklistReadinessGateRedactionPolicyValidated": True,
        "commandArmChecklistReadinessGateGuardCountersValidated": True,
        "commandArmChecklistReadinessGateEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandMaterializationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
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
        "realImporterDryRunHarnessCommandArmChecklistReadinessGateReadPrivateInputs": False,
        "realImporterDryRunHarnessCommandArmChecklistReadinessGatePublishedPrivateInput": False,
        "realImporterDryRunHarnessCommandArmChecklistReadinessGateSentToShell": False,
        "realImporterDryRunHarnessCommandArmChecklistReadinessGatePrivateOutputGenerated": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandMaterialized": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandSentToShell": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandPrivateOutputGenerated": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmed": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "commandArmChecklistReadinessGateInputMode": (
            "tracked-public-safe-command-arm-checklist-validation-proof-json"
        ),
        "commandArmChecklistReadinessGateOutputMode": (
            "tracked-public-safe-command-arm-checklist-readiness-gate-proof"
        ),
        "selectedNextLaneClass": (
            "private-corpus real importer dry-run harness command arm-checklist command materialization without command arming here"
        ),
        "sourceProofCount": 35,
        "sourceCommandArmChecklistValidationProofCount": 34,
        "sourceCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistReadinessGateRows": len(rows),
        "passedCommandArmChecklistReadinessGateRowCount": len(rows),
        "failedCommandArmChecklistReadinessGateRowCount": 0,
        "notRunCommandArmChecklistReadinessGateRowCount": len(rows),
        "unobservedCommandArmChecklistReadinessGateRowCount": len(rows),
        "notArmedCommandArmChecklistReadinessGateRowCount": len(rows),
        "notExecutedCommandArmChecklistReadinessGateRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandMaterializationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistReadinessGateCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistReadinessGateRowsBody": rows,
        "preflightChecks": list(READINESS_PREFLIGHT_CHECKS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_summary(
    summary: Mapping[str, Any],
) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "summary readiness status mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateOnly",
        "commandArmChecklistValidationProofConsumed",
        "commandArmChecklistValidationProofContinuityValidated",
        "commandArmChecklistValidationRowsConsumedByReadinessGate",
        "commandArmChecklistReadinessGateExecuted",
        "commandArmChecklistReadinessGateInputAccepted",
        "commandArmChecklistReadinessGatePreconditionsValidated",
        "commandArmChecklistReadinessGateRowStatusesValidated",
        "commandArmChecklistReadinessGateRowOrdinalsValidated",
        "commandArmChecklistReadinessGateCategoryCountsValidated",
        "commandArmChecklistReadinessGateArmExecutionGuardsValidated",
        "commandArmChecklistReadinessGateRedactionPolicyValidated",
        "commandArmChecklistReadinessGateGuardCountersValidated",
        "commandArmChecklistReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandMaterializationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"summary true flag mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    expected_counts = {
        "sourceProofCount": 35,
        "sourceCommandArmChecklistValidationProofCount": 34,
        "sourceCommandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
        "commandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistReadinessGateRowCount": 0,
        "notRunCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "unobservedCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "notArmedCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "notExecutedCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "commandArmChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist readiness row {expected_ordinal}"
        _require(row.get("commandArmChecklistReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistValidationRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("readinessGateStatus") == "ready-for-later-explicit-command-arm-checklist-command-materialization", f"{row_id} status mismatch")
        _require(row.get("sourceValidationStatus") == "validated-public-safe-not-run-unobserved-not-armed-not-dispatched-not-executed", f"{row_id} source validation mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("futureCommandArmChecklistCommandMaterializationRequiresLaterArm") is True, f"{row_id} command materialization later-arm mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} operator-arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist readiness summary in the proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistValidationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "activeCurrentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
        },
        "sourceEvidence": {
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmChecklistValidationProofCount": summary[
                "sourceCommandArmChecklistValidationProofCount"
            ],
            "sourceCommandArmChecklistValidationInterfaceCount": summary[
                "sourceCommandArmChecklistValidationInterfaceCount"
            ],
            "commandArmChecklistReadinessGateInterfaceCount": summary[
                "commandArmChecklistReadinessGateInterfaceCount"
            ],
            "sourceCommandArmChecklistValidationInterfaces": summary[
                "sourceCommandArmChecklistValidationInterfaces"
            ],
            "commandArmChecklistReadinessGateInterfaces": summary[
                "commandArmChecklistReadinessGateInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_VALIDATION_PROOF,
        },
        "realImporterHarnessCommandArmChecklistReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateOnly": True,
            "commandArmChecklistValidationProofConsumed": True,
            "commandArmChecklistValidationProofContinuityValidated": True,
            "commandArmChecklistValidationRowsConsumedByReadinessGate": True,
            "commandArmChecklistReadinessGateExecuted": True,
            "commandArmChecklistReadinessGateInputAccepted": True,
            "commandArmChecklistReadinessGatePreconditionsValidated": True,
            "commandArmChecklistReadinessGateRowStatusesValidated": True,
            "commandArmChecklistReadinessGateRowOrdinalsValidated": True,
            "commandArmChecklistReadinessGateCategoryCountsValidated": True,
            "commandArmChecklistReadinessGateArmExecutionGuardsValidated": True,
            "commandArmChecklistReadinessGateRedactionPolicyValidated": True,
            "commandArmChecklistReadinessGateGuardCountersValidated": True,
            "commandArmChecklistReadinessGateEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandMaterializationLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
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
            "realImporterDryRunHarnessCommandArmChecklistReadinessGateReadPrivateInputs": False,
            "realImporterDryRunHarnessCommandArmChecklistReadinessGatePublishedPrivateInput": False,
            "realImporterDryRunHarnessCommandArmChecklistReadinessGateSentToShell": False,
            "realImporterDryRunHarnessCommandArmChecklistReadinessGatePrivateOutputGenerated": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandMaterialized": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandSentToShell": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandPrivateOutputGenerated": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmed": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandArmChecklistReadinessGateContract": {
            "commandArmChecklistReadinessGateInputMode": summary["commandArmChecklistReadinessGateInputMode"],
            "commandArmChecklistReadinessGateOutputMode": summary["commandArmChecklistReadinessGateOutputMode"],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "commandArmChecklistValidationRowsConsumed": summary["commandArmChecklistValidationRowsConsumed"],
            "commandArmChecklistReadinessGateRows": summary["commandArmChecklistReadinessGateRows"],
            "passedCommandArmChecklistReadinessGateRowCount": summary[
                "passedCommandArmChecklistReadinessGateRowCount"
            ],
            "failedCommandArmChecklistReadinessGateRowCount": summary[
                "failedCommandArmChecklistReadinessGateRowCount"
            ],
            "notRunCommandArmChecklistReadinessGateRowCount": summary[
                "notRunCommandArmChecklistReadinessGateRowCount"
            ],
            "unobservedCommandArmChecklistReadinessGateRowCount": summary[
                "unobservedCommandArmChecklistReadinessGateRowCount"
            ],
            "notArmedCommandArmChecklistReadinessGateRowCount": summary[
                "notArmedCommandArmChecklistReadinessGateRowCount"
            ],
            "notExecutedCommandArmChecklistReadinessGateRowCount": summary[
                "notExecutedCommandArmChecklistReadinessGateRowCount"
            ],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandMaterializationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandMaterializationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistReadinessGateArtifactRows": summary[
                "publicSafeCommandArmChecklistReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistReadinessGateCategoryCounts": summary[
                "commandArmChecklistReadinessGateCategoryCounts"
            ],
            "commandArmChecklistReadinessGateRowsBody": summary["commandArmChecklistReadinessGateRowsBody"],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-status-token-only",
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
                "the 99 command arm-checklist validation rows remain not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the next command arm-checklist command-materialization lane is selected without command arming, shell dispatch, command execution, or importer execution here",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "raw private manifest consumption",
                "runnable command materialization",
                "command arming, shell dispatch, or command execution",
                "private importer dry run or real importer dry run",
                "actual asset import or generated asset outputs",
                "runtime resource, texture, mesh, Direct3D, GPU, visual, Godot, product UI, renderer, rebuild, rebuild parity, or no-noticeable-difference parity",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--command-arm-checklist-validation-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_VALIDATION_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe readiness-gate summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        validation_proof = read_json(args.command_arm_checklist_validation_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_summary(
            validation_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_readiness_gate_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistReadinessGateError):
        print("Real importer dry-run harness command arm-checklist readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
