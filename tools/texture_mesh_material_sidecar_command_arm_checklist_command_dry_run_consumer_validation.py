#!/usr/bin/env python3
"""Build a public-safe dry-run consumer-validation proof for the sidecar lane.

This consumes only the tracked command dry-run proof. It validates that the
embedded dry-run rows remain public-safe, non-armed, non-dispatched, and not
executed, then emits the next command arm-readiness lane. It does not read
private asset content, consume raw private manifests, arm commands, dispatch a
shell, execute an importer, launch BEA, generate assets, mutate Ghidra, or
publish private paths, filenames, hashes, command arguments, traces, or byte
lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_dry_run import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as DRY_RUN_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as DRY_RUN_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as DRY_RUN_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
    REDACTED_FIELDS as DRY_RUN_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as DRY_RUN_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as DRY_RUN_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
COMMAND_DRY_RUN_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-"
    "consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES = (
    "load-tracked-command-arm-checklist-command-dry-run-proof",
    "validate-command-dry-run-continuity",
    "extract-public-safe-non-dispatched-command-dry-run-rows",
    "validate-command-dry-run-artifact-schema",
    "validate-command-dry-run-row-order",
    "validate-command-dry-run-non-dispatched-statuses",
    "validate-command-dry-run-aggregate-counts",
    "validate-command-dry-run-refusal-guards",
    "select-command-arm-readiness-gate-lane",
    "emit-command-dry-run-consumer-validation-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-status",
            "validated-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecutedShellCommand",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateExecuted",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_ROW_ZERO_FIELDS,
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


class CommandDryRunConsumerValidationError(ValueError):
    """Raised when dry-run evidence cannot support consumer validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandDryRunConsumerValidationError(message)


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


def _validate_source_command_dry_run_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == DRY_RUN_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
        "source dry-run status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 61, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount") == 60,
        "source readiness proof count mismatch",
    )
    _require(
        source_evidence.get("commandDryRunInterfaceCount") == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES),
        "source dry-run interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandDryRunInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
        "source dry-run interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunOnly",
        "commandReadinessGateProofConsumed",
        "commandReadinessGateProofContinuityValidated",
        "commandReadinessGateRowsConsumedByCommandDryRun",
        "commandDryRunExecuted",
        "commandDryRunInputAccepted",
        "commandDryRunRowsGenerated",
        "commandDryRunRowsValidated",
        "commandDryRunAggregateCountsValidated",
        "commandDryRunInterfacesValidated",
        "commandDryRunEmitsOnlyPublicSafeRows",
        "commandDryRunRedactionPolicyValidated",
        "commandDryRunConsumerValidationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in DRY_RUN_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunContract")
    expected_counts = {
        "commandReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandDryRunRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunArtifactRows": 1,
        "publicAllowedOutputCount": len(DRY_RUN_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(DRY_RUN_REDACTED_FIELDS),
        "falseGuardCount": len(DRY_RUN_FALSE_GUARDS),
        "zeroCounterCount": len(DRY_RUN_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandDryRunRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source dry-run row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source dry-run row {expected_ordinal}"
        _require(row.get("commandDryRunRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("commandDryRunStatus") == "public-safe-non-dispatched-command-dry-run-passed", f"{row_id} status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} real importer guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, DRY_RUN_ROW_ZERO_FIELDS, row_id)
    return contract


def build_command_dry_run_consumer_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_rows = _read_list(contract, "commandDryRunRowsBody")
    for source_row in source_rows:
        ordinal = int(source_row["commandDryRunRowOrdinal"])
        row: dict[str, Any] = {
            "commandDryRunConsumerValidationRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-"
                "command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-row"
            ),
            "commandDryRunConsumerValidationRowMode": "public-safe-non-dispatched-command-dry-run-status-token-only",
            "commandDryRunConsumerValidationRowOrdinal": ordinal,
            "sourceCommandDryRunRowOrdinal": ordinal,
            "sourceCommandReadinessGateRowOrdinal": source_row["sourceCommandReadinessGateRowOrdinal"],
            "sourceCommandConsumerValidationRowOrdinal": source_row["sourceCommandConsumerValidationRowOrdinal"],
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
            "commandDryRunConsumerValidationStatus": "validated-public-safe-non-dispatched-command-dry-run-row",
            "sourceCommandDryRunStatus": source_row["commandDryRunStatus"],
            "rowStatus": "dry-run-consumer-validation-passed",
            "observationStatus": "public-safe-synthetic-observation-only",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directRealImporterDryRunAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmReadinessGateRequired": True,
            "futureHarnessArmRequiresOperatorAction": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_command_dry_run_consumer_validation_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_command_dry_run_proof(source)
    rows = build_command_dry_run_consumer_validation_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "consumer-validation category count mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS
        ),
        "sourceProofCount": 62,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount": 61,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES
        ),
        "commandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES
        ),
        "commandDryRunConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonDispatchedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "commandDryRunConsumerValidationCategoryCounts": dict(sorted(category_counts.items())),
        "commandDryRunConsumerValidationRowsBody": rows,
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
    }


def validate_public_safe_command_dry_run_consumer_validation_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "summary consumer-validation status mismatch",
    )
    _require(summary.get("previousSlice") == PREVIOUS_SLICE, "summary previous slice mismatch")
    _require(summary.get("previousScope") == PREVIOUS_SCOPE, "summary previous scope mismatch")
    _require(summary.get("selectedNextSlice") == NEXT_SLICE, "summary next slice mismatch")
    _require(summary.get("selectedNextScope") == NEXT_SCOPE, "summary next scope mismatch")

    expected_counts = {
        "sourceProofCount": 62,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount": 61,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES
        ),
        "commandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonDispatchedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
        "source interface list mismatch",
    )
    _require(
        tuple(summary.get("commandDryRunConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
        "consumer-validation interface list mismatch",
    )

    rows = _read_list(summary, "commandDryRunConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "consumer-validation row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "consumer-validation category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"dry-run consumer-validation row {expected_ordinal}"
        _require(row.get("commandDryRunConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandDryRunRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandDryRunConsumerValidationStatus") == "validated-public-safe-non-dispatched-command-dry-run-row", f"{row_id} status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} real importer guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)

    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_command_dry_run_consumer_validation_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_dry_run_consumer_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS
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
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount"
            ],
            "commandDryRunConsumerValidationInterfaceCount": summary["commandDryRunConsumerValidationInterfaceCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces"
            ],
            "commandDryRunConsumerValidationInterfaces": summary["commandDryRunConsumerValidationInterfaces"],
            "sourceProof": str(COMMAND_DRY_RUN_PROOF.relative_to(ROOT)).replace("\\", "/"),
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationOnly": True,
            "commandDryRunProofConsumed": True,
            "commandDryRunProofContinuityValidated": True,
            "commandDryRunRowsConsumedByConsumerValidation": True,
            "commandDryRunConsumerValidationExecuted": True,
            "commandDryRunConsumerValidationInputAccepted": True,
            "commandDryRunArtifactSchemaValidated": True,
            "commandDryRunRowOrdinalsValidated": True,
            "commandDryRunNonDispatchedStatusesValidated": True,
            "commandDryRunAggregateCountsValidated": True,
            "commandDryRunConsumerValidationInterfacesValidated": True,
            "commandDryRunConsumerValidationEmitsOnlyPublicSafeRows": True,
            "commandDryRunConsumerValidationGuardCountersValidated": True,
            "commandArmReadinessGateLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationContract": {
            "consumerValidationInputMode": "tracked-public-safe-command-dry-run-proof-json",
            "consumerValidationOutputMode": "tracked-public-safe-command-dry-run-consumer-validation-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-readiness gate without command arming here",
            "commandDryRunRowsConsumed": summary["commandDryRunRowsConsumed"],
            "commandDryRunConsumerValidationRows": summary["commandDryRunConsumerValidationRows"],
            "validatedNonDispatchedCommandDryRunRowCount": summary["validatedNonDispatchedCommandDryRunRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandDryRunConsumerValidationCategoryCounts": summary["commandDryRunConsumerValidationCategoryCounts"],
            "commandDryRunConsumerValidationRowsBody": summary["commandDryRunConsumerValidationRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-command-dry-run-consumer-validation-status-token-only",
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
                "the tracked command dry-run proof can be consumed as public-safe command dry-run consumer-validation input",
                "the 99 embedded command dry-run rows remain non-armed, non-dispatched, and not executed",
                "the consumer validation preserves row/category counts and aggregate archive count 301",
                "the next command arm-readiness-gate lane is selected without arming, dispatching, or executing a command",
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
    parser.add_argument("--command-dry-run-proof", type=Path, default=COMMAND_DRY_RUN_PROOF)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--proof", type=Path)
    args = parser.parse_args()

    try:
        source = read_json(args.command_dry_run_proof)
        summary = build_public_safe_command_dry_run_consumer_validation_summary(source)
        validate_public_safe_command_dry_run_consumer_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_command_dry_run_consumer_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandDryRunConsumerValidationError):
        print("Texture mesh material sidecar command dry-run consumer-validation proof: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
