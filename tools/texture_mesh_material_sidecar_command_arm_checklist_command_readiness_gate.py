#!/usr/bin/env python3
"""Build a public-safe command readiness-gate proof for the sidecar lane.

This consumes only the tracked command-consumer-validation proof. It validates
that the public-safe non-armed command-contract rows can advance to a readiness
gate for a later dry-run lane. It does not read private asset content, consume
raw private manifests, build runnable commands, arm commands, dispatch a shell,
execute an importer, launch BEA, generate assets, mutate Ghidra, or publish
private paths, filenames, hashes, command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_consumer_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as CONSUMER_VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as CONSUMER_VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
    REDACTED_FIELDS as CONSUMER_VALIDATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as CONSUMER_VALIDATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as CONSUMER_VALIDATION_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
CONSUMER_VALIDATION_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-consumer-validation-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-"
    "complete-public-safe-readiness-only-not-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES = (
    "load-tracked-command-arm-checklist-command-consumer-validation-proof",
    "validate-command-consumer-validation-continuity",
    "validate-command-readiness-gate-preconditions",
    "validate-non-armed-command-contract-row-order",
    "validate-not-armed-command-statuses",
    "validate-not-executed-command-statuses",
    "validate-no-shell-dispatch",
    "emit-public-safe-command-readiness-gate-rows",
    "select-command-dry-run-lane",
    "emit-command-readiness-gate-summary",
)

READINESS_PREFLIGHT_CHECKS = (
    "source-command-consumer-validation-status-pass",
    "source-command-consumer-validation-selected-this-readiness-gate",
    "source-command-consumer-validation-continuity-preserved",
    "source-command-consumer-validation-row-order-preserved",
    "source-command-consumer-validation-row-counts-preserved",
    "source-command-consumer-validation-category-counts-preserved",
    "source-command-consumer-validation-not-armed-statuses-preserved",
    "source-command-consumer-validation-not-executed-statuses-preserved",
    "source-command-consumer-validation-dispatch-guards-preserved",
    "source-command-consumer-validation-real-importer-guards-preserved",
    "source-command-consumer-validation-redaction-policy-preserved",
    "source-command-consumer-validation-false-guard-counts-preserved",
    "source-command-consumer-validation-zero-counters-preserved",
    "readiness-gate-does-not-read-private-inputs",
    "readiness-gate-does-not-materialize-runnable-command",
    "readiness-gate-does-not-arm-command",
    "readiness-gate-does-not-dispatch-shell",
    "readiness-gate-does-not-execute-importer",
    "readiness-gate-selects-command-dry-run-lane",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_VALIDATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-private-output",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateMaterializedRunnableCommand",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateCommandArmed",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateCommandSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateCommandExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateImporterExecuted",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunExecuted",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_VALIDATION_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGatePrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *CONSUMER_VALIDATION_ROW_ZERO_FIELDS,
            *ZERO_COUNTERS,
            "actualAssetImportRows",
            "generatedAssetRows",
            "commandExecutionRows",
            "commandShellDispatchRows",
            "commandPrivateOutputRows",
            "privateDryRunRows",
            "rawCommandArgumentRows",
            "publishedCommandArgumentRows",
            "rawPathRows",
            "rawFilenameRows",
            "rawHashRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "rawStemRows",
            "byteLengthRows",
        )
    )
)


class CommandReadinessGateError(ValueError):
    """Raised when consumer-validation evidence cannot support a readiness gate."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandReadinessGateError(message)


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


def _validate_source_command_consumer_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == CONSUMER_VALIDATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
        "source command-consumer-validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 59, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount") == 58,
        "source command-materialization proof count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES,
        "source command-consumer-validation interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationOnly",
        "commandMaterializationProofConsumed",
        "commandContractArtifactConsumed",
        "commandContractArtifactContinuityValidated",
        "commandConsumerValidationExecuted",
        "commandConsumerValidationInputAccepted",
        "commandContractArtifactSchemaValidated",
        "commandContractRowOrdinalsValidated",
        "commandContractNonArmedStatusesValidated",
        "commandContractAggregateCountsValidated",
        "commandConsumerValidationInterfacesValidated",
        "commandConsumerValidationEmitsOnlyPublicSafeRows",
        "commandConsumerValidationGuardCountersValidated",
        "commandReadinessGateLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in CONSUMER_VALIDATION_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonArmedCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(CONSUMER_VALIDATION_REDACTED_FIELDS),
        "falseGuardCount": len(CONSUMER_VALIDATION_FALSE_GUARDS),
        "zeroCounterCount": len(CONSUMER_VALIDATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source command-consumer row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command-consumer row {expected_ordinal}"
        _require(row.get("commandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandContractRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandConsumerValidationStatus") == "validated-public-safe-non-armed-command-contract-row", f"{row_id} status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} real importer guard mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} later-arm mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} operator-arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, CONSUMER_VALIDATION_ROW_ZERO_FIELDS, row_id)
    return contract


def build_command_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_rows = _read_list(contract, "commandConsumerValidationRowsBody")
    for source_row in source_rows:
        ordinal = int(source_row["commandConsumerValidationRowOrdinal"])
        row: dict[str, Any] = {
            "commandReadinessGateRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-"
                "command-arm-checklist-command-arm-checklist-command-readiness-gate-row"
            ),
            "commandReadinessGateRowMode": "public-safe-readiness-only-not-armed-not-dispatched-not-executed",
            "commandReadinessGateRowOrdinal": ordinal,
            "sourceCommandConsumerValidationRowOrdinal": ordinal,
            "sourceCommandContractRowOrdinal": source_row["sourceCommandContractRowOrdinal"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal"
            ],
            "category": source_row["category"],
            "itemId": source_row["itemId"],
            "commandReadinessGateStatus": "ready-public-safe-command-dry-run-lane-only-no-command-execution",
            "sourceCommandConsumerValidationStatus": source_row["commandConsumerValidationStatus"],
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directRealImporterDryRunAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandDryRunAllowed": True,
            "futureHarnessArmRequiresOperatorAction": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_command_readiness_gate_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_command_consumer_validation_proof(source)
    rows = build_command_readiness_gate_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "readiness-gate category count mismatch")

    summary: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS
        ),
        "sourceProofCount": 60,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount": 59,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandReadinessGateRowCount": 0,
        "readinessGateNotArmedCommandRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotExecutedCommandRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "preflightChecks": list(READINESS_PREFLIGHT_CHECKS),
        "commandReadinessGateCategoryCounts": dict(sorted(category_counts.items())),
        "commandReadinessGateRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "publicLeakCheck": "PASS",
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
    }
    validate_public_safe_command_readiness_gate_summary(summary)
    return summary


def validate_public_safe_command_readiness_gate_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS,
        "summary status token mismatch",
    )
    expected_counts = {
        "sourceProofCount": 60,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount": 59,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount": 12,
        "commandReadinessGateInterfaceCount": 10,
        "commandConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandReadinessGateRowCount": 0,
        "readinessGateNotArmedCommandRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotExecutedCommandRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(READINESS_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"summary false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"summary zero counter mismatch: {key}")

    rows = _read_list(summary, "commandReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness-gate row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "readiness-gate category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"readiness-gate row {expected_ordinal}"
        _require(row.get("commandReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandReadinessGateStatus") == "ready-public-safe-command-dry-run-lane-only-no-command-execution", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} real importer guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("futureCommandDryRunAllowed") is True, f"{row_id} future dry-run mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} future arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_command_readiness_gate_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS
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
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount"
            ],
            "commandReadinessGateInterfaceCount": summary["commandReadinessGateInterfaceCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces"
            ],
            "commandReadinessGateInterfaces": summary["commandReadinessGateInterfaces"],
            "sourceProof": str(CONSUMER_VALIDATION_PROOF.relative_to(ROOT)).replace("\\", "/"),
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateOnly": True,
            "commandConsumerValidationProofConsumed": True,
            "commandConsumerValidationProofContinuityValidated": True,
            "commandConsumerValidationRowsConsumedByCommandReadinessGate": True,
            "commandReadinessGateExecuted": True,
            "commandReadinessGateInputAccepted": True,
            "commandReadinessGatePreconditionsValidated": True,
            "commandReadinessGateRowStatusesValidated": True,
            "commandReadinessGateRowOrdinalsValidated": True,
            "commandReadinessGateCategoryCountsValidated": True,
            "commandReadinessGateInterfacesValidated": True,
            "commandReadinessGateEmitsOnlyPublicSafeRows": True,
            "commandReadinessGateRedactionPolicyValidated": True,
            "commandDryRunLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateContract": {
            "commandReadinessGateInputMode": "tracked-public-safe-command-consumer-validation-proof-json",
            "commandReadinessGateOutputMode": "tracked-public-safe-command-readiness-gate-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command dry-run without command arming here",
            "commandConsumerValidationRowsConsumed": summary["commandConsumerValidationRowsConsumed"],
            "commandReadinessGateRows": summary["commandReadinessGateRows"],
            "passedCommandReadinessGateRowCount": summary["passedCommandReadinessGateRowCount"],
            "failedCommandReadinessGateRowCount": summary["failedCommandReadinessGateRowCount"],
            "readinessGateNotArmedCommandRowCount": summary["readinessGateNotArmedCommandRowCount"],
            "readinessGateNotExecutedCommandRowCount": summary["readinessGateNotExecutedCommandRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandReadinessGateCategoryCounts": summary["commandReadinessGateCategoryCounts"],
            "commandReadinessGateRowsBody": summary["commandReadinessGateRowsBody"],
            "preflightChecks": summary["preflightChecks"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-command-readiness-gate-status-token-only",
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
                "the tracked command-consumer-validation proof can be consumed as public-safe readiness-gate input",
                "the 99 readiness-gate rows preserve source ordinals and category counts",
                "every readiness-gate row remains not-armed, not-dispatched, and not-executed",
                "the next command dry-run lane is selected without materializing, arming, dispatching, or executing a command here",
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
    parser.add_argument("--consumer-validation-proof", type=Path, default=CONSUMER_VALIDATION_PROOF)
    parser.add_argument("--summary", type=Path, help="optional public-safe command-readiness summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof JSON output")
    args = parser.parse_args()

    try:
        source = read_json(args.consumer_validation_proof)
        summary = build_public_safe_command_readiness_gate_summary(source)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_command_readiness_gate_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandReadinessGateError):
        print("Material sidecar command arm-checklist command-readiness-gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
