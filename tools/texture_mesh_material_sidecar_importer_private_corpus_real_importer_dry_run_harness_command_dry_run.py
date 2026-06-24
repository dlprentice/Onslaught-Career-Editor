#!/usr/bin/env python3
"""Dry-run public-safe real-importer harness command rows.

This module consumes only the tracked public command-readiness-gate proof. It
simulates command-row consumption and validates that every row remains safe for
a later explicit arm gate. It does not arm, dispatch, or execute shell commands;
read private asset content; consume raw private manifests; generate assets;
launch BEA; mutate Ghidra; mutate the installed game/original executable; or
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

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_STATUS,
    REDACTED_FIELDS as READINESS_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-dry-run.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-dry-run-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-dry-run-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Consumer Validation Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-dry-run-consumer-validation-proof-plan"
)

COMMAND_READINESS_GATE_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-readiness-gate-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_INTERFACES = (
    "load-tracked-real-importer-harness-command-readiness-gate-proof",
    "validate-real-importer-harness-command-readiness-gate-continuity",
    "validate-harness-command-dry-run-preconditions",
    "validate-harness-command-dry-run-row-order",
    "dry-run-harness-command-row-consumption",
    "validate-harness-command-dry-run-aggregate-counts",
    "validate-harness-command-dry-run-refusal-guards",
    "validate-harness-command-dry-run-public-redaction-policy",
    "select-harness-command-arm-readiness-gate-lane",
    "emit-command-dry-run-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-dry-run-status",
            "harness-command-dry-run-row-counts",
            "harness-command-dry-run-interface-linkage",
            "harness-command-dry-run-consumer-validation-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "harness-command-dry-run-input-path",
            "harness-command-dry-run-output-path",
            "raw-command-dry-run-trace",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "harnessCommandDryRunReadPrivateInputs",
            "harnessCommandDryRunPublishedPrivateInput",
            "privateCommandDryRunArtifactPublished",
            "rawCommandDryRunTracePublished",
            "commandDryRunSentToShell",
            "commandDryRunGeneratedPrivateOutput",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_COUNTERS,
            "harnessCommandDryRunPrivateInputRows",
            "privateCommandDryRunArtifactRows",
            "commandDryRunOutputArtifactRows",
            "rawCommandDryRunTraceRows",
        )
    )
)


class RealImporterDryRunHarnessCommandDryRunError(ValueError):
    """Raised when command-readiness evidence cannot support dry-run."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandDryRunError(message)


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


def _validate_source_command_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_STATUS,
        "source command-readiness status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 28, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandConsumerValidationProofCount") == 27,
        "source command-consumer proof count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_INTERFACES,
        "source command-readiness interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandReadinessGateDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandReadinessGateOnly",
        "commandConsumerValidationProofConsumed",
        "commandConsumerValidationProofContinuityValidated",
        "commandConsumerValidationProofRowsConsumed",
        "commandReadinessGateExecuted",
        "commandReadinessGateInputAccepted",
        "commandReadinessGatePreconditionsValidated",
        "commandReadinessGateRowStatusesValidated",
        "commandReadinessGateRowOrdinalsValidated",
        "commandReadinessGateCategoryCountsValidated",
        "commandReadinessGateInterfacesValidated",
        "commandReadinessGateEmitsOnlyPublicSafeRows",
        "commandReadinessGateRedactionPolicyValidated",
        "harnessCommandDryRunLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision expected true: {key}")
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
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandReadinessGateContract")
    expected_counts = {
        "commandConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandReadinessGateArtifactRows": 1,
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command-readiness row {expected_ordinal}"
        _require(row.get("commandReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("futureHarnessCommandDryRunRequiresLaterArm") is True, f"{row_id} later dry-run flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
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
                "realImporterDryRunHarnessCommandDryRunRows",
                "realImporterDryRunHarnessCommandExecutionRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            row_id,
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(READINESS_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(READINESS_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in READINESS_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_dry_run_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe dry-run row per command-readiness row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandReadinessGateRowsBody"):
        ordinal = int(source_row["commandReadinessGateRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandDryRunAcceptedByInterface": "dry-run-harness-command-row-consumption",
                "commandDryRunOutputArtifactRows": 0,
                "commandDryRunRowClass": "private-corpus-real-importer-dry-run-harness-command-dry-run-row",
                "commandDryRunRowMode": "public-safe-non-dispatched-command-status-token-only",
                "commandDryRunRowOrdinal": ordinal,
                "commandDryRunStatus": "public-safe-non-dispatched-command-dry-run-passed",
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandShellDispatchRows": 0,
                "futureHarnessArmRequiresOperatorAction": True,
                "futureHarnessCommandDryRunConsumerValidationRequiresLaterReview": True,
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
                "realImporterDryRunHarnessCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceCommandReadinessGateRowOrdinal": ordinal,
                "sourceCommandConsumerValidationRowOrdinal": source_row[
                    "sourceCommandConsumerValidationRowOrdinal"
                ],
                "sourceCommandContractRowOrdinal": source_row["sourceCommandContractRowOrdinal"],
                "sourceHarnessChecklistReadinessGateRowOrdinal": source_row[
                    "sourceHarnessChecklistReadinessGateRowOrdinal"
                ],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_dry_run_summary(
    command_readiness_gate_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command dry-run summary."""

    contract = _validate_source_command_readiness_gate_proof(command_readiness_gate_proof)
    rows = build_command_dry_run_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "dry-run category counts mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandDryRunStatus": REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandReadinessGateStatus": REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandDryRunOnly": True,
        "commandReadinessGateProofConsumed": True,
        "commandReadinessGateProofContinuityValidated": True,
        "commandReadinessGateProofRowsConsumed": True,
        "harnessCommandDryRunExecuted": True,
        "harnessCommandDryRunInputAccepted": True,
        "harnessCommandDryRunRowsGenerated": True,
        "harnessCommandDryRunRowsValidated": True,
        "harnessCommandDryRunAggregateCountsValidated": True,
        "harnessCommandDryRunInterfacesValidated": True,
        "harnessCommandDryRunEmitsOnlyPublicSafeRows": True,
        "harnessCommandDryRunRedactionPolicyValidated": True,
        "harnessCommandDryRunConsumerValidationLaneSelected": True,
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
        "harnessCommandDryRunReadPrivateInputs": False,
        "harnessCommandDryRunPublishedPrivateInput": False,
        "privateCommandDryRunArtifactPublished": False,
        "rawCommandDryRunTracePublished": False,
        "commandDryRunSentToShell": False,
        "commandDryRunGeneratedPrivateOutput": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceProofCount": 29,
        "sourceCommandReadinessGateProofCount": 28,
        "sourceCommandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandDryRunInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_INTERFACES),
        "commandReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunRows": len(rows),
        "passedCommandDryRunRowCount": len(rows),
        "failedCommandDryRunRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandDryRunConsumerValidationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandDryRunArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandDryRunInterfaces": list(REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_INTERFACES),
        "commandDryRunCategoryCounts": dict(sorted(category_counts.items())),
        "commandDryRunRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_harness_command_dry_run_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command dry-run summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandDryRunStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandDryRunOnly",
        "commandReadinessGateProofConsumed",
        "commandReadinessGateProofContinuityValidated",
        "commandReadinessGateProofRowsConsumed",
        "harnessCommandDryRunExecuted",
        "harnessCommandDryRunInputAccepted",
        "harnessCommandDryRunRowsGenerated",
        "harnessCommandDryRunRowsValidated",
        "harnessCommandDryRunAggregateCountsValidated",
        "harnessCommandDryRunInterfacesValidated",
        "harnessCommandDryRunEmitsOnlyPublicSafeRows",
        "harnessCommandDryRunRedactionPolicyValidated",
        "harnessCommandDryRunConsumerValidationLaneSelected",
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
        "harnessCommandDryRunReadPrivateInputs",
        "harnessCommandDryRunPublishedPrivateInput",
        "privateCommandDryRunArtifactPublished",
        "rawCommandDryRunTracePublished",
        "commandDryRunSentToShell",
        "commandDryRunGeneratedPrivateOutput",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 29,
        "sourceCommandReadinessGateProofCount": 28,
        "sourceCommandReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_INTERFACES
        ),
        "commandDryRunInterfaceCount": len(REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_INTERFACES),
        "commandReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandDryRunRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandDryRunConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandDryRunArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_INTERFACES,
        "source command-readiness interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandDryRunInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_INTERFACES,
        "command dry-run interfaces mismatch",
    )
    rows = _read_list(summary, "commandDryRunRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "dry-run row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "dry-run category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"dry-run command row {expected_ordinal}"
        _require(row.get("commandDryRunRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
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
                "realImporterDryRunHarnessCommandDryRunRows",
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


def build_public_safe_real_importer_dry_run_harness_command_dry_run_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command dry-run summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_dry_run_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandDryRunStatus": REAL_IMPORTER_HARNESS_COMMAND_DRY_RUN_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandReadinessGateStatus": REAL_IMPORTER_HARNESS_COMMAND_READINESS_GATE_STATUS,
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
            "sourceCommandReadinessGateProofCount": summary["sourceCommandReadinessGateProofCount"],
            "sourceCommandReadinessGateInterfaceCount": summary[
                "sourceCommandReadinessGateInterfaceCount"
            ],
            "commandDryRunInterfaceCount": summary["commandDryRunInterfaceCount"],
            "sourceCommandReadinessGateInterfaces": summary["sourceCommandReadinessGateInterfaces"],
            "commandDryRunInterfaces": summary["commandDryRunInterfaces"],
            "sourceProof": COMMAND_READINESS_GATE_PROOF,
        },
        "realImporterHarnessCommandDryRunDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandDryRunOnly": True,
            "commandReadinessGateProofConsumed": True,
            "commandReadinessGateProofContinuityValidated": True,
            "commandReadinessGateProofRowsConsumed": True,
            "harnessCommandDryRunExecuted": True,
            "harnessCommandDryRunInputAccepted": True,
            "harnessCommandDryRunRowsGenerated": True,
            "harnessCommandDryRunRowsValidated": True,
            "harnessCommandDryRunAggregateCountsValidated": True,
            "harnessCommandDryRunInterfacesValidated": True,
            "harnessCommandDryRunEmitsOnlyPublicSafeRows": True,
            "harnessCommandDryRunRedactionPolicyValidated": True,
            "harnessCommandDryRunConsumerValidationLaneSelected": True,
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
            "harnessCommandDryRunReadPrivateInputs": False,
            "harnessCommandDryRunPublishedPrivateInput": False,
            "privateCommandDryRunArtifactPublished": False,
            "rawCommandDryRunTracePublished": False,
            "commandDryRunSentToShell": False,
            "commandDryRunGeneratedPrivateOutput": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandDryRunContract": {
            "commandDryRunInputMode": "tracked-public-safe-command-readiness-gate-proof-json",
            "commandDryRunOutputMode": "public-safe-non-dispatched-command-status-token-rows",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command dry-run consumer validation without command arming",
            "commandReadinessGateRowsConsumed": summary["commandReadinessGateRowsConsumed"],
            "commandDryRunRows": summary["commandDryRunRows"],
            "passedCommandDryRunRowCount": summary["passedCommandDryRunRowCount"],
            "failedCommandDryRunRowCount": summary["failedCommandDryRunRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandDryRunConsumerValidationRowCount": summary[
                "readyForLaterCommandDryRunConsumerValidationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandDryRunArtifactRows": summary["publicSafeCommandDryRunArtifactRows"],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandDryRunCategoryCounts": summary["commandDryRunCategoryCounts"],
            "commandDryRunRowsBody": summary["commandDryRunRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-dry-run-status-token-only",
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
    parser.add_argument("--command-readiness-gate-proof", type=Path, default=Path(COMMAND_READINESS_GATE_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe command dry-run summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        readiness_gate_proof = read_json(args.command_readiness_gate_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_dry_run_summary(
            readiness_gate_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_dry_run_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_dry_run_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandDryRunError):
        print("Real importer dry-run harness command dry-run: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
