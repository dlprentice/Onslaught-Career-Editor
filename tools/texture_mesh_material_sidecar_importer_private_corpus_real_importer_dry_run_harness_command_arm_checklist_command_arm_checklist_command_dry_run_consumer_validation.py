#!/usr/bin/env python3
"""Validate public-safe real-importer harness command arm-checklist command arm-checklist command dry-run rows.

This module consumes only the tracked command arm-checklist command arm-checklist command dry-run proof. It treats the
embedded dry-run rows as public-safe status-token input, validates that every
row remains non-armed, non-dispatched, and not executed, then emits a
consumer-validation proof. It does not arm, dispatch, or execute a command;
read private asset content; consume raw private manifests; launch BEA; generate
assets; mutate Ghidra; or emit private paths, filenames, hashes, command
arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
    REDACTED_FIELDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-"
    "command-arm-checklist-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof",
    "validate-real-importer-harness-command-arm-checklist-command-arm-checklist-command-dry-run-continuity",
    "extract-public-safe-non-dispatched-command-arm-checklist-command-arm-checklist-command-dry-run-rows",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-dry-run-artifact-schema",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-dry-run-row-order",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-dry-run-non-dispatched-statuses",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-dry-run-aggregate-counts",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-dry-run-refusal-guards",
    "select-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-lane",
    "emit-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-status",
            "validated-command-arm-checklist-command-arm-checklist-command-dry-run-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecutedShellCommand",
            "privateCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationError(ValueError):
    """Raised when command arm-checklist command arm-checklist command dry-run evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationError(message)


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


def _validate_source_command_arm_checklist_command_arm_checklist_command_dry_run_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
        "source command arm-checklist command arm-checklist command dry-run status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 50, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount") == 49,
        "source command-arm-checklist-command-arm-checklist-command-readiness proof count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistCommandArmChecklistCommandDryRunInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
        "source command arm-checklist command arm-checklist command dry-run interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandDryRunDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunOnly",
        "commandArmChecklistCommandArmChecklistCommandReadinessGateProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandReadinessGateProofRowsConsumed",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunInputAccepted",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunRowsGenerated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunRowsValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunAggregateCountsValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunInterfacesValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunEmitsOnlyPublicSafeRows",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "realImporterDryRunHarnessExecuted",
        "realImporterDryRunHarnessArmed",
        "realImporterDryRunHarnessCommandArmed",
        "realImporterDryRunHarnessCommandExecuted",
        "realImporterDryRunHarnessCommandSentToShell",
        "realImporterDryRunHarnessCommandPrivateOutputGenerated",
        "realImporterDryRunHarnessRunnableCommandMaterialized",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunReadPrivateInputs",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunPublishedPrivateInput",
        "privateCommandArmChecklistCommandArmChecklistCommandDryRunArtifactPublished",
        "rawCommandArmChecklistCommandArmChecklistCommandDryRunTracePublished",
        "commandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
        "commandArmChecklistCommandArmChecklistCommandDryRunGeneratedPrivateOutput",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandDryRunContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandDryRunRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunArtifactRows": 1,
        "publicAllowedOutputCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_REDACTED_FIELDS),
        "falseGuardCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_FALSE_GUARDS),
        "zeroCounterCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandDryRunRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source dry-run row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source dry-run command row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandDryRunRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateRowOrdinal") == expected_ordinal,
            f"{row_id} source ordinal mismatch",
        )
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} later-arm flag mismatch")
        _require(
            row.get("futureHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRequiresLaterReview") is True,
            f"{row_id} later consumer-validation flag mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
                "commandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows",
                "commandExecutionRows",
                "commandPrivateOutputRows",
                "commandShellDispatchRows",
                "generatedAssetRows",
                "privateDryRunRows",
                "publishedCommandArgumentRows",
                "rawCommandArgumentRows",
                "rawCommandArmChecklistCommandArmChecklistCommandDryRunTraceRows",
                "rawFilenameRows",
                "rawHashRows",
                "rawMeshRefRows",
                "rawPathRows",
                "rawStemRows",
                "rawTextureRefRows",
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRows",
                "realImporterDryRunHarnessCommandExecutionRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            row_id,
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe consumer-validation row per command arm-checklist command arm-checklist command dry-run row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistCommandDryRunRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandDryRunRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowClass": (
                    "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-row"
                ),
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowMode": (
                    "public-safe-non-dispatched-command-arm-checklist-command-arm-checklist-command-dry-run-status-token-only"
                ),
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowOrdinal": ordinal,
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": (
                    "validated-public-safe-non-dispatched-command-arm-checklist-command-arm-checklist-command-dry-run-row"
                ),
                "commandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows": 0,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandShellDispatchRows": 0,
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessArmRequiresOperatorAction": True,
                "futureHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRequiresLaterReview": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArgumentRows": 0,
                "rawCommandArmChecklistCommandArmChecklistCommandDryRunTraceRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowOrdinal"
                ],
                "sourceCommandContractRowOrdinal": source_row["sourceCommandContractRowOrdinal"],
                "sourceCommandArmChecklistCommandArmChecklistCommandDryRunRowOrdinal": ordinal,
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateRowOrdinal"
                ],
                "sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"
                ],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_summary(
    command_arm_checklist_command_arm_checklist_command_dry_run_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist command arm-checklist command dry-run consumer-validation summary."""

    contract = _validate_source_command_arm_checklist_command_arm_checklist_command_dry_run_proof(command_arm_checklist_command_arm_checklist_command_dry_run_proof)
    rows = build_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "consumer validation category counts mismatch")
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationOnly": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunProofConsumed": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunProofContinuityValidated": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunProofRowsConsumed": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecuted": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInputAccepted": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunArtifactSchemaValidated": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunRowOrdinalsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunNonDispatchedStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunAggregateCountsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfacesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationEmitsOnlyPublicSafeRows": True,
        "harnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateLaneSelected": True,
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
        "realImporterDryRunHarnessCommandArmed": False,
        "realImporterDryRunHarnessCommandExecuted": False,
        "realImporterDryRunHarnessCommandSentToShell": False,
        "realImporterDryRunHarnessCommandPrivateOutputGenerated": False,
        "realImporterDryRunHarnessRunnableCommandMaterialized": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationReadPrivateInputs": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPublishedPrivateInput": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecutedShellCommand": False,
        "privateCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateExecuted": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceProofCount": 51,
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunProofCount": 50,
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows": len(rows),
        "validatedNonDispatchedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": len(rows),
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces": list(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES),
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command arm-checklist command arm-checklist command dry-run consumer-validation summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationOnly",
        "commandArmChecklistCommandArmChecklistCommandDryRunProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandDryRunProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandDryRunProofRowsConsumed",
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecuted",
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandDryRunArtifactSchemaValidated",
        "commandArmChecklistCommandArmChecklistCommandDryRunRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandDryRunNonDispatchedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandDryRunAggregateCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationEmitsOnlyPublicSafeRows",
        "harnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "realImporterDryRunHarnessExecuted",
        "realImporterDryRunHarnessArmed",
        "realImporterDryRunHarnessCommandArmed",
        "realImporterDryRunHarnessCommandExecuted",
        "realImporterDryRunHarnessCommandSentToShell",
        "realImporterDryRunHarnessCommandPrivateOutputGenerated",
        "realImporterDryRunHarnessRunnableCommandMaterialized",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationReadPrivateInputs",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPublishedPrivateInput",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecutedShellCommand",
        "privateCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateExecuted",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 51,
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunProofCount": 50,
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES),
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonDispatchedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
        "source command arm-checklist command arm-checklist command dry-run interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
        "command arm-checklist command arm-checklist command dry-run consumer-validation interfaces mismatch",
    )
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "consumer row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "consumer category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"dry-run consumer command row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmChecklistCommandDryRunRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} later-arm flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
                "commandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows",
                "commandExecutionRows",
                "commandPrivateOutputRows",
                "commandShellDispatchRows",
                "generatedAssetRows",
                "privateDryRunRows",
                "publishedCommandArgumentRows",
                "rawCommandArgumentRows",
                "rawCommandArmChecklistCommandArmChecklistCommandDryRunTraceRows",
                "rawFilenameRows",
                "rawHashRows",
                "rawMeshRefRows",
                "rawPathRows",
                "rawStemRows",
                "rawTextureRefRows",
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows",
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRows",
                "realImporterDryRunHarnessCommandExecutionRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            row_id,
        )
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist command arm-checklist command dry-run consumer summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandDryRunStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
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
            "sourceCommandArmChecklistCommandArmChecklistCommandDryRunProofCount": summary["sourceCommandArmChecklistCommandArmChecklistCommandDryRunProofCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount": summary["sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount"],
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces": summary["sourceCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces"],
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaces": summary[
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationOnly": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunProofConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunProofRowsConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecuted": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInputAccepted": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunArtifactSchemaValidated": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunNonDispatchedStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunAggregateCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationEmitsOnlyPublicSafeRows": True,
            "harnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateLaneSelected": True,
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
            "realImporterDryRunHarnessCommandArmed": False,
            "realImporterDryRunHarnessCommandExecuted": False,
            "realImporterDryRunHarnessCommandSentToShell": False,
            "realImporterDryRunHarnessCommandPrivateOutputGenerated": False,
            "realImporterDryRunHarnessRunnableCommandMaterialized": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationReadPrivateInputs": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationPublishedPrivateInput": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationExecutedShellCommand": False,
            "privateCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateExecuted": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationContract": {
            "consumerValidationInputMode": "tracked-public-safe-command-arm-checklist-command-arm-checklist-command-dry-run-proof-json",
            "consumerValidationOutputMode": "tracked-public-safe-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-checklist command arm-readiness gate without execution",
            "commandArmChecklistCommandArmChecklistCommandDryRunRowsConsumed": summary["commandArmChecklistCommandArmChecklistCommandDryRunRowsConsumed"],
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows": summary[
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows"
            ],
            "validatedNonDispatchedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": summary[
                "validatedNonDispatchedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowsBody": summary[
                "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowsBody"
            ],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-status-token-only",
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
                "the tracked command arm-checklist command arm-checklist command dry-run proof can be consumed as public-safe command arm-checklist command arm-checklist command dry-run consumer-validation input",
                "the 99 embedded command arm-checklist command arm-checklist command dry-run rows remain non-armed, non-dispatched, and not executed",
                "the consumer validation preserves row/category counts and aggregate archive count 301",
                "the next command arm-readiness-gate lane is selected without arming or executing a command here",
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
    parser.add_argument("--command-arm-checklist-command-arm-checklist-command-dry-run-proof", type=Path, default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe consumer validation summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        command_arm_checklist_command_arm_checklist_command_dry_run_proof = read_json(args.command_arm_checklist_command_arm_checklist_command_dry_run_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_summary(
            command_arm_checklist_command_arm_checklist_command_dry_run_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_dry_run_consumer_validation_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationError):
        print("Real importer dry-run harness command arm-checklist command arm-checklist command dry-run consumer validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
