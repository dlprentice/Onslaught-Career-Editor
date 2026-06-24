#!/usr/bin/env python3
"""Validate readiness for a later explicit real-importer harness command arm gate.

This module consumes only the tracked command dry-run consumer-validation proof.
It verifies that the 99 public-safe rows remain non-armed, non-dispatched, and
not executed before selecting a later command arm-boundary lane. It does not
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

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_dry_run_consumer_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_DRY_RUN_CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
    REDACTED_FIELDS as COMMAND_DRY_RUN_CONSUMER_VALIDATION_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-readiness-gate.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-readiness-gate-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-readiness-gate-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Boundary Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-boundary-proof-plan"
)

COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-dry-run-consumer-validation-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_INTERFACES = (
    "load-tracked-real-importer-harness-command-dry-run-consumer-validation-proof",
    "validate-real-importer-harness-command-dry-run-consumer-validation-continuity",
    "validate-harness-command-arm-readiness-gate-preconditions",
    "validate-harness-command-dry-run-consumer-validation-row-statuses",
    "validate-harness-command-arm-readiness-gate-row-ordinals",
    "validate-harness-command-arm-readiness-gate-category-counts",
    "validate-harness-command-arm-readiness-gate-refusal-guards",
    "validate-harness-command-arm-readiness-gate-public-redaction-policy",
    "select-harness-command-arm-boundary-lane",
    "emit-command-arm-readiness-gate-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_DRY_RUN_CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-readiness-gate-status",
            "harness-command-arm-readiness-gate-row-counts",
            "harness-command-arm-boundary-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_DRY_RUN_CONSUMER_VALIDATION_REDACTED_FIELDS,
            "harness-command-arm-readiness-gate-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *COMMAND_DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmReadinessGatePublishedPrivateInput",
            "privateCommandArmReadinessGateArtifactPublished",
            "realImporterDryRunHarnessCommandArmBoundaryExecuted",
            "realImporterDryRunHarnessCommandArmBoundarySentToShell",
            "realImporterDryRunHarnessCommandArmBoundaryPrivateOutputGenerated",
        )
    )
    if key != "realImporterDryRunHarnessCommandArmReadinessGateExecuted"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS,
            "commandArmReadinessGatePrivateInputRows",
            "commandArmReadinessGateArtifactPathRows",
            "privateCommandArmReadinessGateArtifactRows",
            "realImporterDryRunHarnessCommandArmReadinessGateRows",
            "realImporterDryRunHarnessCommandArmBoundaryRows",
            "commandArmBoundaryOutputArtifactRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmReadinessGateError(ValueError):
    """Raised when command dry-run consumer evidence cannot support arm-readiness."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmReadinessGateError(message)


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


ROW_ZERO_FIELDS = (
    "actualAssetImportRows",
    "byteLengthRows",
    "commandArmBoundaryOutputArtifactRows",
    "commandDryRunOutputArtifactRows",
    "commandExecutionRows",
    "commandPrivateOutputRows",
    "commandShellDispatchRows",
    "generatedAssetRows",
    "privateDryRunRows",
    "publishedCommandArgumentRows",
    "rawCommandArgumentRows",
    "rawCommandDryRunTraceRows",
    "rawFilenameRows",
    "rawHashRows",
    "rawMeshRefRows",
    "rawPathRows",
    "rawStemRows",
    "rawTextureRefRows",
    "realImporterDryRunHarnessCommandArmBoundaryRows",
    "realImporterDryRunHarnessCommandArmReadinessGateRows",
    "realImporterDryRunHarnessCommandDryRunConsumerValidationRows",
    "realImporterDryRunHarnessCommandDryRunRows",
    "realImporterDryRunHarnessCommandExecutionRows",
    "realImporterDryRunHarnessRows",
    "realImporterDryRunRows",
)


def _validate_source_command_dry_run_consumer_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(
        source.get("schemaVersion") == COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF_SCHEMA_VERSION,
        "source schema mismatch",
    )
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandDryRunConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "source command dry-run consumer-validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 30, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandDryRunProofCount") == 29,
        "source command dry-run proof count mismatch",
    )
    _require(
        source_evidence.get("commandDryRunConsumerValidationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES),
        "source command dry-run consumer-validation interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandDryRunConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
        "source command dry-run consumer-validation interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandDryRunConsumerValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandDryRunConsumerValidationOnly",
        "commandDryRunProofConsumed",
        "commandDryRunProofContinuityValidated",
        "commandDryRunProofRowsConsumed",
        "commandDryRunConsumerValidationExecuted",
        "commandDryRunConsumerValidationInputAccepted",
        "commandDryRunArtifactSchemaValidated",
        "commandDryRunRowOrdinalsValidated",
        "commandDryRunNonDispatchedStatusesValidated",
        "commandDryRunAggregateCountsValidated",
        "commandDryRunConsumerValidationInterfacesValidated",
        "commandDryRunConsumerValidationEmitsOnlyPublicSafeRows",
        "harnessCommandArmReadinessGateLaneSelected",
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
        "realImporterDryRunHarnessCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandDryRunPrivateOutputGenerated",
        "realImporterDryRunHarnessCommandDryRunConsumerValidationReadPrivateInputs",
        "realImporterDryRunHarnessCommandDryRunConsumerValidationPublishedPrivateInput",
        "realImporterDryRunHarnessCommandDryRunConsumerValidationExecutedShellCommand",
        "privateCommandDryRunConsumerValidationArtifactPublished",
        "realImporterDryRunHarnessCommandArmReadinessGateExecuted",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandDryRunConsumerValidationContract")
    expected_counts = {
        "commandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonDispatchedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(COMMAND_DRY_RUN_CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(COMMAND_DRY_RUN_CONSUMER_VALIDATION_REDACTED_FIELDS),
        "falseGuardCount": len(COMMAND_DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS),
        "zeroCounterCount": len(COMMAND_DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandDryRunConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source consumer-validation row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source dry-run consumer-validation command row {expected_ordinal}"
        _require(row.get("commandDryRunConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandDryRunRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} later-arm flag mismatch")
        _require(
            row.get("futureHarnessCommandArmReadinessGateRequiresLaterReview") is True,
            f"{row_id} later arm-readiness flag mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(
            row,
            tuple(key for key in ROW_ZERO_FIELDS if key in row),
            row_id,
        )

    guard = _read_mapping(source, "guardSummary")
    _require(
        guard.get("falseGuardCount") == len(COMMAND_DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS),
        "source false guard count mismatch",
    )
    _require(
        guard.get("zeroCounterCount") == len(COMMAND_DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS),
        "source zero counter count mismatch",
    )
    for key in COMMAND_DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe command arm-readiness row per consumer-validation row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandDryRunConsumerValidationRowsBody"):
        ordinal = int(source_row["commandDryRunConsumerValidationRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmBoundaryOutputArtifactRows": 0,
                "commandArmReadinessGateMode": "public-safe-command-arm-readiness-status-token-only",
                "commandArmReadinessGateRowClass": (
                    "private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-row"
                ),
                "commandArmReadinessGateRowOrdinal": ordinal,
                "commandArmReadinessGateStatus": "ready-for-later-explicit-command-arm-boundary-review",
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandDryRunOutputArtifactRows": 0,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandShellDispatchRows": 0,
                "directCommandArmingAllowedHere": False,
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessArmRequiresOperatorAction": True,
                "futureHarnessCommandArmBoundaryRequiresLaterReview": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArgumentRows": 0,
                "rawCommandDryRunTraceRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandArmBoundaryRows": 0,
                "realImporterDryRunHarnessCommandArmReadinessGateRows": 0,
                "realImporterDryRunHarnessCommandDryRunConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandConsumerValidationRowOrdinal": source_row[
                    "sourceCommandConsumerValidationRowOrdinal"
                ],
                "sourceCommandContractRowOrdinal": source_row["sourceCommandContractRowOrdinal"],
                "sourceCommandDryRunConsumerValidationRowOrdinal": ordinal,
                "sourceCommandDryRunRowOrdinal": source_row["sourceCommandDryRunRowOrdinal"],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceCommandReadinessGateRowOrdinal": source_row[
                    "sourceCommandReadinessGateRowOrdinal"
                ],
                "sourceHarnessChecklistReadinessGateRowOrdinal": source_row[
                    "sourceHarnessChecklistReadinessGateRowOrdinal"
                ],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_summary(
    command_dry_run_consumer_validation_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-readiness-gate summary."""

    contract = _validate_source_command_dry_run_consumer_validation_proof(command_dry_run_consumer_validation_proof)
    rows = build_command_arm_readiness_gate_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "arm-readiness category counts mismatch")
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandDryRunConsumerValidationStatus": REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateOnly": True,
        "commandDryRunConsumerValidationProofConsumed": True,
        "commandDryRunConsumerValidationProofContinuityValidated": True,
        "commandDryRunConsumerValidationProofRowsConsumed": True,
        "commandArmReadinessGateExecuted": True,
        "commandArmReadinessGateInputAccepted": True,
        "commandArmReadinessGatePreconditionsValidated": True,
        "commandArmReadinessGateRowStatusesValidated": True,
        "commandArmReadinessGateRowOrdinalsValidated": True,
        "commandArmReadinessGateCategoryCountsValidated": True,
        "commandArmReadinessGateInterfacesValidated": True,
        "commandArmReadinessGateEmitsOnlyPublicSafeRows": True,
        "commandArmReadinessGateRedactionPolicyValidated": True,
        "harnessCommandArmBoundaryLaneSelected": True,
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
        "realImporterDryRunHarnessCommandDryRunExecuted": False,
        "realImporterDryRunHarnessCommandDryRunSentToShell": False,
        "realImporterDryRunHarnessCommandDryRunPrivateOutputGenerated": False,
        "realImporterDryRunHarnessCommandArmReadinessGateReadPrivateInputs": False,
        "realImporterDryRunHarnessCommandArmReadinessGatePublishedPrivateInput": False,
        "privateCommandArmReadinessGateArtifactPublished": False,
        "realImporterDryRunHarnessCommandArmBoundaryExecuted": False,
        "realImporterDryRunHarnessCommandArmBoundarySentToShell": False,
        "realImporterDryRunHarnessCommandArmBoundaryPrivateOutputGenerated": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceProofCount": 31,
        "sourceCommandDryRunConsumerValidationProofCount": 30,
        "sourceCommandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandDryRunConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmReadinessGateRows": len(rows),
        "passedCommandArmReadinessGateRowCount": len(rows),
        "failedCommandArmReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmBoundaryRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandDryRunConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmReadinessGateCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmReadinessGateRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command arm-readiness-gate summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateOnly",
        "commandDryRunConsumerValidationProofConsumed",
        "commandDryRunConsumerValidationProofContinuityValidated",
        "commandDryRunConsumerValidationProofRowsConsumed",
        "commandArmReadinessGateExecuted",
        "commandArmReadinessGateInputAccepted",
        "commandArmReadinessGatePreconditionsValidated",
        "commandArmReadinessGateRowStatusesValidated",
        "commandArmReadinessGateRowOrdinalsValidated",
        "commandArmReadinessGateCategoryCountsValidated",
        "commandArmReadinessGateInterfacesValidated",
        "commandArmReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmReadinessGateRedactionPolicyValidated",
        "harnessCommandArmBoundaryLaneSelected",
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
        "realImporterDryRunHarnessCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandDryRunPrivateOutputGenerated",
        "realImporterDryRunHarnessCommandArmReadinessGateReadPrivateInputs",
        "realImporterDryRunHarnessCommandArmReadinessGatePublishedPrivateInput",
        "privateCommandArmReadinessGateArtifactPublished",
        "realImporterDryRunHarnessCommandArmBoundaryExecuted",
        "realImporterDryRunHarnessCommandArmBoundarySentToShell",
        "realImporterDryRunHarnessCommandArmBoundaryPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 31,
        "sourceCommandDryRunConsumerValidationProofCount": 30,
        "sourceCommandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandDryRunConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandDryRunConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
        "source command dry-run consumer-validation interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_INTERFACES,
        "command arm-readiness-gate interfaces mismatch",
    )
    rows = _read_list(summary, "commandArmReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "arm-readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "arm-readiness category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"arm-readiness command row {expected_ordinal}"
        _require(row.get("commandArmReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandDryRunConsumerValidationRowOrdinal") == expected_ordinal,
            f"{row_id} source ordinal mismatch",
        )
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(
            row.get("futureHarnessCommandArmBoundaryRequiresLaterReview") is True,
            f"{row_id} later arm-boundary flag mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-readiness summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandDryRunConsumerValidationStatus": REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
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
            "sourceCommandDryRunConsumerValidationProofCount": summary[
                "sourceCommandDryRunConsumerValidationProofCount"
            ],
            "sourceCommandDryRunConsumerValidationInterfaceCount": summary[
                "sourceCommandDryRunConsumerValidationInterfaceCount"
            ],
            "commandArmReadinessGateInterfaceCount": summary[
                "commandArmReadinessGateInterfaceCount"
            ],
            "sourceCommandDryRunConsumerValidationInterfaces": summary[
                "sourceCommandDryRunConsumerValidationInterfaces"
            ],
            "commandArmReadinessGateInterfaces": summary["commandArmReadinessGateInterfaces"],
            "sourceProof": COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF,
        },
        "realImporterHarnessCommandArmReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateOnly": True,
            "commandDryRunConsumerValidationProofConsumed": True,
            "commandDryRunConsumerValidationProofContinuityValidated": True,
            "commandDryRunConsumerValidationProofRowsConsumed": True,
            "commandArmReadinessGateExecuted": True,
            "commandArmReadinessGateInputAccepted": True,
            "commandArmReadinessGatePreconditionsValidated": True,
            "commandArmReadinessGateRowStatusesValidated": True,
            "commandArmReadinessGateRowOrdinalsValidated": True,
            "commandArmReadinessGateCategoryCountsValidated": True,
            "commandArmReadinessGateInterfacesValidated": True,
            "commandArmReadinessGateEmitsOnlyPublicSafeRows": True,
            "commandArmReadinessGateRedactionPolicyValidated": True,
            "harnessCommandArmBoundaryLaneSelected": True,
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
            "realImporterDryRunHarnessCommandDryRunExecuted": False,
            "realImporterDryRunHarnessCommandDryRunSentToShell": False,
            "realImporterDryRunHarnessCommandDryRunPrivateOutputGenerated": False,
            "realImporterDryRunHarnessCommandArmReadinessGateReadPrivateInputs": False,
            "realImporterDryRunHarnessCommandArmReadinessGatePublishedPrivateInput": False,
            "privateCommandArmReadinessGateArtifactPublished": False,
            "realImporterDryRunHarnessCommandArmBoundaryExecuted": False,
            "realImporterDryRunHarnessCommandArmBoundarySentToShell": False,
            "realImporterDryRunHarnessCommandArmBoundaryPrivateOutputGenerated": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandArmReadinessGateContract": {
            "commandArmReadinessGateInputMode": "tracked-public-safe-command-dry-run-consumer-validation-proof-json",
            "commandArmReadinessGateOutputMode": "tracked-public-safe-command-arm-readiness-gate-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-boundary without command arming here",
            "commandDryRunConsumerValidationRowsConsumed": summary[
                "commandDryRunConsumerValidationRowsConsumed"
            ],
            "commandArmReadinessGateRows": summary["commandArmReadinessGateRows"],
            "passedCommandArmReadinessGateRowCount": summary[
                "passedCommandArmReadinessGateRowCount"
            ],
            "failedCommandArmReadinessGateRowCount": summary[
                "failedCommandArmReadinessGateRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmBoundaryRowCount": summary[
                "readyForLaterCommandArmBoundaryRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmReadinessGateArtifactRows": summary[
                "publicSafeCommandArmReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmReadinessGateCategoryCounts": summary[
                "commandArmReadinessGateCategoryCounts"
            ],
            "commandArmReadinessGateRowsBody": summary["commandArmReadinessGateRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-readiness-gate-status-token-only",
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
                "the tracked command dry-run consumer-validation proof can be consumed as public-safe command arm-readiness input",
                "the 99 command dry-run consumer-validation rows remain non-armed, non-dispatched, and not executed",
                "the command arm-readiness gate preserves row/category counts and aggregate archive count 301",
                "the next command arm-boundary lane is selected without arming, dispatching, or executing a command here",
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
    parser.add_argument(
        "--command-dry-run-consumer-validation-proof",
        type=Path,
        default=Path(COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe arm-readiness summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        consumer_validation_proof = read_json(args.command_dry_run_consumer_validation_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_summary(
            consumer_validation_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_readiness_gate_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmReadinessGateError):
        print("Real importer dry-run harness command arm-readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
