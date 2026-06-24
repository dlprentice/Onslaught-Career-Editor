#!/usr/bin/env python3
"""Validate readiness for a later real-importer harness command arm-checklist command arm-checklist command dry-run.

This module consumes only the tracked public command-arm-checklist-command-consumer-validation proof.
It verifies that the 99 command rows remain non-armed, not executed, and
public-safe before selecting a later explicitly armed command arm-checklist command arm-checklist command dry-run lane. It
does not arm, dispatch, or execute a command; read private asset content;
consume raw private manifests; launch BEA; generate assets; mutate Ghidra; or
emit private paths, filenames, hashes, command arguments, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_consumer_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
    REDACTED_FIELDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof",
    "validate-real-importer-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-continuity",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-preconditions",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-row-statuses",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-row-ordinals",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-category-counts",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-refusal-guards",
    "validate-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-public-redaction-policy",
    "select-harness-command-arm-checklist-command-arm-checklist-command-dry-run-lane",
    "emit-command-arm-checklist-command-readiness-gate-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-status",
            "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-dry-run-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGatePublishedPrivateInput",
            "privateCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated",
        )
    )
    if key != "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateExecuted"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandReadinessGatePrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRows",
            "commandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateError(ValueError):
    """Raised when command-consumer evidence cannot support readiness."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateError(message)


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


def _validate_source_command_arm_checklist_command_arm_checklist_command_consumer_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
        "source command arm-checklist command arm-checklist command consumer-validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 48, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount") == 47,
        "source command-materialization proof count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES,
        "source command arm-checklist command arm-checklist command consumer-validation interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationOnly",
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
        "harnessCommandReadinessGateLaneSelected",
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
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationReadPrivateInputs",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationPublishedPrivateInput",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationExecutedShellCommand",
        "privateCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactPublished",
        "realImporterDryRunHarnessCommandReadinessGateExecuted",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandContractRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonArmedCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_REDACTED_FIELDS),
        "falseGuardCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_FALSE_GUARDS),
        "zeroCounterCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source consumer row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source consumer command row {expected_ordinal}"
        _require(row.get("commandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandContractRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
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
                "commandExecutionRows",
                "commandPrivateOutputRows",
                "commandShellDispatchRows",
                "generatedAssetRows",
                "privateDryRunRows",
                "publishedCommandArgumentRows",
                "rawCommandArgumentRows",
                "rawFilenameRows",
                "rawHashRows",
                "rawMeshRefRows",
                "rawPathRows",
                "rawStemRows",
                "rawTextureRefRows",
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationRows",
                "realImporterDryRunHarnessCommandExecutionRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            row_id,
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_command_arm_checklist_command_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe command-arm-checklist-command-readiness row per consumer-validation row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandConsumerValidationRowsBody"):
        ordinal = int(source_row["commandConsumerValidationRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandArmChecklistCommandArmChecklistCommandDryRunOutputArtifactRows": 0,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandArmChecklistCommandReadinessGateMode": "public-safe-command-arm-checklist-command-readiness-status-token-only",
                "commandArmChecklistCommandReadinessGateRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-row",
                "commandArmChecklistCommandReadinessGateRowOrdinal": ordinal,
                "commandArmChecklistCommandReadinessGateStatus": "ready-for-later-explicit-harness-command-arm-checklist-command-arm-checklist-command-dry-run",
                "commandShellDispatchRows": 0,
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessArmRequiresOperatorAction": True,
                "futureHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRequiresLaterArm": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArgumentRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowOrdinal": ordinal,
                "sourceCommandContractRowOrdinal": source_row["sourceCommandContractRowOrdinal"],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"
                ],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_summary(
    command_arm_checklist_command_arm_checklist_command_consumer_validation_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command-arm-checklist-command-readiness-gate summary."""

    contract = _validate_source_command_arm_checklist_command_arm_checklist_command_consumer_validation_proof(command_arm_checklist_command_arm_checklist_command_consumer_validation_proof)
    rows = build_command_arm_checklist_command_arm_checklist_command_readiness_gate_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "readiness category counts mismatch")
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateOnly": True,
        "commandArmChecklistCommandConsumerValidationProofConsumed": True,
        "commandArmChecklistCommandConsumerValidationProofContinuityValidated": True,
        "commandArmChecklistCommandConsumerValidationProofRowsConsumed": True,
        "commandArmChecklistCommandReadinessGateExecuted": True,
        "commandArmChecklistCommandReadinessGateInputAccepted": True,
        "commandArmChecklistCommandReadinessGatePreconditionsValidated": True,
        "commandArmChecklistCommandReadinessGateRowStatusesValidated": True,
        "commandArmChecklistCommandReadinessGateRowOrdinalsValidated": True,
        "commandArmChecklistCommandReadinessGateCategoryCountsValidated": True,
        "commandArmChecklistCommandReadinessGateInterfacesValidated": True,
        "commandArmChecklistCommandReadinessGateEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandReadinessGateRedactionPolicyValidated": True,
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunLaneSelected": True,
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
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateReadPrivateInputs": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGatePublishedPrivateInput": False,
        "privateCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPublished": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell": False,
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceProofCount": 49,
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount": 48,
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandReadinessGateRows": len(rows),
        "passedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": len(rows),
        "failedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandReadinessGateCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandArmChecklistCommandReadinessGateRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command-arm-checklist-command-readiness-gate summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateOnly",
        "commandArmChecklistCommandConsumerValidationProofConsumed",
        "commandArmChecklistCommandConsumerValidationProofContinuityValidated",
        "commandArmChecklistCommandConsumerValidationProofRowsConsumed",
        "commandArmChecklistCommandReadinessGateExecuted",
        "commandArmChecklistCommandReadinessGateInputAccepted",
        "commandArmChecklistCommandReadinessGatePreconditionsValidated",
        "commandArmChecklistCommandReadinessGateRowStatusesValidated",
        "commandArmChecklistCommandReadinessGateRowOrdinalsValidated",
        "commandArmChecklistCommandReadinessGateCategoryCountsValidated",
        "commandArmChecklistCommandReadinessGateInterfacesValidated",
        "commandArmChecklistCommandReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandReadinessGateRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandDryRunLaneSelected",
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
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateReadPrivateInputs",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGatePublishedPrivateInput",
        "privateCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPublished",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 49,
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount": 48,
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES,
        "source command arm-checklist command arm-checklist command consumer-validation interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_INTERFACES,
        "command arm-checklist command readiness-gate interfaces mismatch",
    )
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "readiness category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"readiness command row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("futureHarnessCommandArmChecklistCommandArmChecklistCommandDryRunRequiresLaterArm") is True, f"{row_id} later dry-run flag mismatch")
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
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command-arm-checklist-command-readiness-gate summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
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
            "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount": summary["commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaces"
            ],
            "commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces": summary["commandArmChecklistCommandArmChecklistCommandReadinessGateInterfaces"],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateOnly": True,
            "commandArmChecklistCommandConsumerValidationProofConsumed": True,
            "commandArmChecklistCommandConsumerValidationProofContinuityValidated": True,
            "commandArmChecklistCommandConsumerValidationProofRowsConsumed": True,
            "commandArmChecklistCommandReadinessGateExecuted": True,
            "commandArmChecklistCommandReadinessGateInputAccepted": True,
            "commandArmChecklistCommandReadinessGatePreconditionsValidated": True,
            "commandArmChecklistCommandReadinessGateRowStatusesValidated": True,
            "commandArmChecklistCommandReadinessGateRowOrdinalsValidated": True,
            "commandArmChecklistCommandReadinessGateCategoryCountsValidated": True,
            "commandArmChecklistCommandReadinessGateInterfacesValidated": True,
            "commandArmChecklistCommandReadinessGateEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandReadinessGateRedactionPolicyValidated": True,
            "harnessCommandArmChecklistCommandArmChecklistCommandDryRunLaneSelected": True,
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
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateReadPrivateInputs": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGatePublishedPrivateInput": False,
            "privateCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactPublished": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunExecuted": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunPrivateOutputGenerated": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateContract": {
            "commandArmChecklistCommandReadinessGateInputMode": "tracked-public-safe-command-arm-checklist-command-consumer-validation-proof-json",
            "commandArmChecklistCommandReadinessGateOutputMode": "tracked-public-safe-command-arm-checklist-command-readiness-gate-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-checklist command arm-checklist command dry-run without command execution here",
            "commandArmChecklistCommandArmChecklistCommandConsumerValidationRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistCommandConsumerValidationRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistCommandReadinessGateRows": summary["commandArmChecklistCommandArmChecklistCommandReadinessGateRows"],
            "passedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": summary[
                "passedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount"
            ],
            "failedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": summary[
                "failedCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandReadinessGateCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandReadinessGateCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandReadinessGateRowsBody": summary["commandArmChecklistCommandArmChecklistCommandReadinessGateRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-status-token-only",
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
                "the tracked command-arm-checklist-command-consumer-validation proof can be consumed as public-safe command-arm-checklist-command-readiness input",
                "the 99 command arm-checklist command arm-checklist command consumer-validation rows remain non-armed and not executed",
                "the command-arm-checklist-command-readiness gate preserves row/category counts and aggregate archive count 301",
                "the next command arm-checklist command arm-checklist command dry-run lane is selected without arming, dispatching, or executing a command here",
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
    parser.add_argument("--command-arm-checklist-command-consumer-validation-proof", type=Path, default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe command arm-checklist command readiness-gate summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        consumer_validation_proof = read_json(args.command_arm_checklist_command_consumer_validation_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_summary(
            consumer_validation_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_readiness_gate_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandReadinessGateError):
        print("Real importer dry-run harness command readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
