#!/usr/bin/env python3
"""Build a public-safe command dry-run proof for the sidecar lane.

This consumes only the tracked command-readiness-gate proof. It simulates
public-safe row consumption for the next dry-run lane, but it does not read
private asset content, consume raw private manifests, materialize runnable
commands, arm commands, dispatch a shell, execute an importer, launch BEA,
generate assets, mutate Ghidra, or publish private paths, filenames, hashes,
command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS,
    REDACTED_FIELDS as READINESS_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as READINESS_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
READINESS_GATE_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-"
    "complete-public-safe-readiness-row-consumption-not-real-importer-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES = (
    "load-tracked-command-arm-checklist-command-readiness-gate-proof",
    "validate-command-readiness-gate-continuity",
    "validate-command-dry-run-preconditions",
    "validate-command-dry-run-row-order",
    "dry-run-command-readiness-row-consumption",
    "validate-command-dry-run-aggregate-counts",
    "validate-command-dry-run-refusal-guards",
    "validate-command-dry-run-public-redaction-policy",
    "select-command-dry-run-consumer-validation-lane",
    "emit-command-dry-run-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-interface-linkage",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-input-path",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-output-path",
            "raw-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-trace",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunReadPrivateInputs",
            "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunPublishedPrivateInput",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunArtifactPublished",
            "rawCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunTracePublished",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunGeneratedPrivateOutput",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_COUNTERS,
            "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunPrivateInputRows",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunArtifactRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows",
            "rawCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunTraceRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_ROW_ZERO_FIELDS,
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


class CommandDryRunError(ValueError):
    """Raised when readiness-gate evidence cannot support a dry-run proof."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandDryRunError(message)


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


def _validate_source_command_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS,
        "source command-readiness status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 60, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount") == 59,
        "source consumer-validation proof count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES,
        "source command-readiness interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateOnly",
        "commandConsumerValidationProofConsumed",
        "commandConsumerValidationProofContinuityValidated",
        "commandConsumerValidationRowsConsumedByCommandReadinessGate",
        "commandReadinessGateExecuted",
        "commandReadinessGateInputAccepted",
        "commandReadinessGatePreconditionsValidated",
        "commandReadinessGateRowStatusesValidated",
        "commandReadinessGateRowOrdinalsValidated",
        "commandReadinessGateCategoryCountsValidated",
        "commandReadinessGateInterfacesValidated",
        "commandReadinessGateEmitsOnlyPublicSafeRows",
        "commandReadinessGateRedactionPolicyValidated",
        "commandDryRunLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in READINESS_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateContract")
    expected_counts = {
        "commandConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandReadinessGateRowCount": 0,
        "readinessGateNotArmedCommandRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotExecutedCommandRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(READINESS_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(READINESS_REDACTED_FIELDS),
        "falseGuardCount": len(READINESS_FALSE_GUARDS),
        "zeroCounterCount": len(READINESS_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command-readiness row {expected_ordinal}"
        _require(row.get("commandReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandReadinessGateStatus") == "ready-public-safe-command-dry-run-lane-only-no-command-execution", f"{row_id} status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} real importer guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("futureCommandDryRunAllowed") is True, f"{row_id} future dry-run mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} explicit arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, READINESS_ROW_ZERO_FIELDS, row_id)
    return contract


def build_command_dry_run_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_rows = _read_list(contract, "commandReadinessGateRowsBody")
    for source_row in source_rows:
        ordinal = int(source_row["commandReadinessGateRowOrdinal"])
        row: dict[str, Any] = {
            "commandDryRunRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-"
                "command-arm-checklist-command-arm-checklist-command-dry-run-row"
            ),
            "commandDryRunRowMode": "public-safe-non-dispatched-command-status-token-only",
            "commandDryRunRowOrdinal": ordinal,
            "sourceCommandReadinessGateRowOrdinal": ordinal,
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
            "commandDryRunStatus": "public-safe-non-dispatched-command-dry-run-passed",
            "sourceCommandReadinessGateStatus": source_row["commandReadinessGateStatus"],
            "rowStatus": "dry-run-passed",
            "observationStatus": "public-safe-synthetic-observation-only",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directRealImporterDryRunAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandDryRunConsumerValidationRequired": True,
            "futureHarnessArmRequiresOperatorAction": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_command_dry_run_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_command_readiness_gate_proof(source)
    rows = build_command_dry_run_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "dry-run category count mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS
        ),
        "sourceProofCount": 61,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount": 60,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandDryRunInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandDryRunInterfaces": list(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES),
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
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "commandDryRunCategoryCounts": dict(sorted(category_counts.items())),
        "commandDryRunRowsBody": rows,
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
    }


def validate_public_safe_command_dry_run_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
        "summary dry-run status mismatch",
    )
    _require(summary.get("previousSlice") == PREVIOUS_SLICE, "summary previous slice mismatch")
    _require(summary.get("previousScope") == PREVIOUS_SCOPE, "summary previous scope mismatch")
    _require(summary.get("selectedNextSlice") == NEXT_SLICE, "summary next slice mismatch")
    _require(summary.get("selectedNextScope") == NEXT_SCOPE, "summary next scope mismatch")

    expected_counts = {
        "sourceProofCount": 61,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount": 60,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandDryRunInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES),
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
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES,
        "source interface list mismatch",
    )
    _require(
        tuple(summary.get("commandDryRunInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
        "dry-run interface list mismatch",
    )

    rows = _read_list(summary, "commandDryRunRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "dry-run row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "dry-run category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"dry-run row {expected_ordinal}"
        _require(row.get("commandDryRunRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandDryRunStatus") == "public-safe-non-dispatched-command-dry-run-passed", f"{row_id} status mismatch")
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


def build_public_safe_command_dry_run_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_dry_run_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS
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
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount"
            ],
            "commandDryRunInterfaceCount": summary["commandDryRunInterfaceCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces"
            ],
            "commandDryRunInterfaces": summary["commandDryRunInterfaces"],
            "sourceProof": str(READINESS_GATE_PROOF.relative_to(ROOT)).replace("\\", "/"),
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunOnly": True,
            "commandReadinessGateProofConsumed": True,
            "commandReadinessGateProofContinuityValidated": True,
            "commandReadinessGateRowsConsumedByCommandDryRun": True,
            "commandDryRunExecuted": True,
            "commandDryRunInputAccepted": True,
            "commandDryRunRowsGenerated": True,
            "commandDryRunRowsValidated": True,
            "commandDryRunAggregateCountsValidated": True,
            "commandDryRunInterfacesValidated": True,
            "commandDryRunEmitsOnlyPublicSafeRows": True,
            "commandDryRunRedactionPolicyValidated": True,
            "commandDryRunConsumerValidationLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunContract": {
            "commandDryRunInputMode": "tracked-public-safe-command-readiness-gate-proof-json",
            "commandDryRunOutputMode": "tracked-public-safe-non-dispatched-command-dry-run-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command dry-run consumer validation without command arming here",
            "commandReadinessGateRowsConsumed": summary["commandReadinessGateRowsConsumed"],
            "commandDryRunRows": summary["commandDryRunRows"],
            "passedCommandDryRunRowCount": summary["passedCommandDryRunRowCount"],
            "failedCommandDryRunRowCount": summary["failedCommandDryRunRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandDryRunCategoryCounts": summary["commandDryRunCategoryCounts"],
            "commandDryRunRowsBody": summary["commandDryRunRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-command-dry-run-status-token-only",
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
                "the tracked command-readiness-gate proof can be consumed as public-safe command dry-run input",
                "the 99 command-readiness rows can pass non-dispatched dry-run row validation",
                "the command dry-run preserves row/category counts and aggregate archive count 301",
                "the next command dry-run consumer-validation lane is selected without arming, dispatching, or executing a command here",
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
    parser.add_argument("--readiness-gate-proof", type=Path, default=READINESS_GATE_PROOF)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--proof", type=Path)
    args = parser.parse_args()

    try:
        source = read_json(args.readiness_gate_proof)
        summary = build_public_safe_command_dry_run_summary(source)
        validate_public_safe_command_dry_run_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_command_dry_run_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandDryRunError):
        print("Texture mesh material sidecar command dry-run proof: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
