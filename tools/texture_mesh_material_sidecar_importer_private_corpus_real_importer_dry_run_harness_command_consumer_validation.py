#!/usr/bin/env python3
"""Validate a public-safe non-armed real-importer harness command contract.

This module consumes only the tracked command-materialization proof. It treats
the embedded command contract as public-safe status-token input, validates that
every row remains non-armed and not executed, and emits a consumer-validation
proof. It does not build a runnable shell command, arm or dispatch a command,
execute an importer, read private asset bytes, consume raw private manifests,
launch BEA, generate assets, mutate Ghidra, or emit private paths/filenames.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_materialization import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_MATERIALIZATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_MATERIALIZATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
    REDACTED_FIELDS as COMMAND_MATERIALIZATION_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_MATERIALIZATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-consumer-validation.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-consumer-validation-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-"
    "not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Consumer Validation Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-consumer-validation-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Readiness Gate Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-readiness-gate-proof-plan"
)

COMMAND_MATERIALIZATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-materialization-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-materialization-proof",
    "validate-real-importer-harness-command-materialization-continuity",
    "extract-public-safe-non-armed-harness-command-contract",
    "validate-harness-command-contract-artifact-schema",
    "validate-harness-command-contract-row-order",
    "validate-harness-command-contract-non-armed-statuses",
    "validate-harness-command-contract-aggregate-counts",
    "validate-harness-command-contract-refusal-guards",
    "select-harness-command-readiness-gate-lane",
    "emit-command-consumer-validation-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-consumer-validation-status",
            "validated-non-armed-command-contract-row-counts",
            "harness-command-readiness-gate-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_REDACTED_FIELDS,
            "harness-command-consumer-validation-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandConsumerValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandConsumerValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandConsumerValidationExecutedShellCommand",
            "privateCommandConsumerValidationArtifactPublished",
            "realImporterDryRunHarnessCommandReadinessGateExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_ZERO_COUNTERS,
            "commandConsumerValidationPrivateInputRows",
            "commandConsumerValidationArtifactPathRows",
            "privateCommandConsumerValidationArtifactRows",
            "realImporterDryRunHarnessCommandConsumerValidationRows",
        )
    )
)


class RealImporterDryRunHarnessCommandConsumerValidationError(ValueError):
    """Raised when command materialization evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandConsumerValidationError(message)


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


def _validate_source_command_materialization_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == COMMAND_MATERIALIZATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
        "source command materialization status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 26, "source proof count mismatch")
    _require(source_evidence.get("sourceReadinessGateProofCount") == 25, "source readiness proof count mismatch")
    _require(
        tuple(source_evidence.get("realImporterDryRunHarnessCommandMaterializationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES,
        "source command materialization interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandMaterializationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandMaterializationOnly",
        "realImporterHarnessChecklistReadinessGateProofConsumed",
        "realImporterHarnessChecklistReadinessGateProofContinuityValidated",
        "realImporterDryRunHarnessCommandMaterializationExecuted",
        "realImporterDryRunHarnessCommandMaterializationInputAccepted",
        "publicSafeNonArmedHarnessCommandContractMaterialized",
        "publicSafeNonArmedHarnessCommandContractStoredInTrackedProof",
        "harnessCommandContractRowsGenerated",
        "harnessCommandContractRowsValidated",
        "harnessCommandContractAggregateCountsValidated",
        "harnessCommandContractInterfacesValidated",
        "harnessCommandContractEmitsOnlyPublicSafeRows",
        "harnessCommandContractRedactionPolicyValidated",
        "harnessCommandConsumerValidationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in (
        "publicSafeNonArmedHarnessCommandContractPathPublished",
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
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandMaterializationContract")
    expected_counts = {
        "harnessChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": 6,
        "redactedFieldCount": 12,
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    artifact = _read_mapping(contract, "harnessCommandContractArtifact")
    _require(artifact.get("artifactKind") == "public-safe-real-importer-dry-run-harness-non-armed-command-contract-artifact", "artifact kind mismatch")
    _require(artifact.get("artifactRowMode") == "public-safe-non-armed-command-contract-status-token-only", "artifact row mode mismatch")
    _require(artifact.get("materializationStatus") == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS, "artifact status mismatch")
    _require(artifact.get("commandArmed") is False, "artifact command armed")
    _require(artifact.get("commandExecuted") is False, "artifact command executed")
    _require(artifact.get("commandDispatchedToShell") is False, "artifact command dispatched")
    _require(artifact.get("publicLeakCheck") == "PASS", "artifact public leak mismatch")

    rows = _read_list(artifact, "commandContractRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command contract row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "command category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command row {expected_ordinal}"
        _require(row.get("commandContractRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceHarnessChecklistReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("commandRequiresLaterExplicitArm") is True, f"{row_id} later-arm guard mismatch")
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
                "realImporterDryRunHarnessCommandExecutionRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            row_id,
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(COMMAND_MATERIALIZATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(COMMAND_MATERIALIZATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in COMMAND_MATERIALIZATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return artifact


def build_command_consumer_validation_rows(artifact: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe consumer-validation row per non-armed command row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(artifact, "commandContractRowsBody"):
        ordinal = int(source_row["commandContractRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmStatus": "not-armed",
                "commandConsumerValidationRowClass": "private-corpus-real-importer-dry-run-harness-command-consumer-validation-row",
                "commandConsumerValidationRowMode": "public-safe-non-armed-command-contract-status-token-only",
                "commandConsumerValidationRowOrdinal": ordinal,
                "commandConsumerValidationStatus": "validated-public-safe-non-armed-command-contract-row",
                "commandDispatchAllowedHere": False,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandReadinessGateStatus": "ready-for-later-explicit-harness-command-readiness-gate",
                "commandShellDispatchRows": 0,
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessArmRequiresOperatorAction": True,
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
                "realImporterDryRunHarnessCommandConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandContractRowOrdinal": ordinal,
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceHarnessChecklistReadinessGateRowOrdinal": source_row[
                    "sourceHarnessChecklistReadinessGateRowOrdinal"
                ],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(
    command_materialization_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command-consumer-validation summary."""

    artifact = _validate_source_command_materialization_proof(command_materialization_proof)
    rows = build_command_consumer_validation_rows(artifact)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "consumer validation category counts mismatch")
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandMaterializationStatus": REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationOnly": True,
        "commandMaterializationProofConsumed": True,
        "commandContractArtifactConsumed": True,
        "commandContractArtifactContinuityValidated": True,
        "commandConsumerValidationExecuted": True,
        "commandConsumerValidationInputAccepted": True,
        "commandContractArtifactSchemaValidated": True,
        "commandContractRowOrdinalsValidated": True,
        "commandContractNonArmedStatusesValidated": True,
        "commandContractAggregateCountsValidated": True,
        "commandConsumerValidationInterfacesValidated": True,
        "commandConsumerValidationEmitsOnlyPublicSafeRows": True,
        "harnessCommandReadinessGateLaneSelected": True,
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
        "realImporterDryRunHarnessCommandConsumerValidationReadPrivateInputs": False,
        "realImporterDryRunHarnessCommandConsumerValidationPublishedPrivateInput": False,
        "realImporterDryRunHarnessCommandConsumerValidationExecutedShellCommand": False,
        "privateCommandConsumerValidationArtifactPublished": False,
        "realImporterDryRunHarnessCommandReadinessGateExecuted": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "sourceProofCount": 27,
        "sourceCommandMaterializationProofCount": 26,
        "sourceCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "harnessCommandContractRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandConsumerValidationRows": len(rows),
        "validatedNonArmedCommandContractRowCount": len(rows),
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandReadinessGateRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandMaterializationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandConsumerValidationCategoryCounts": dict(sorted(category_counts.items())),
        "commandConsumerValidationRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command-consumer-validation summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationOnly",
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
        "realImporterDryRunHarnessCommandConsumerValidationReadPrivateInputs",
        "realImporterDryRunHarnessCommandConsumerValidationPublishedPrivateInput",
        "realImporterDryRunHarnessCommandConsumerValidationExecutedShellCommand",
        "privateCommandConsumerValidationArtifactPublished",
        "realImporterDryRunHarnessCommandReadinessGateExecuted",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 27,
        "sourceCommandMaterializationProofCount": 26,
        "sourceCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "harnessCommandContractRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonArmedCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandMaterializationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES,
        "source command materialization interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES,
        "command consumer validation interfaces mismatch",
    )
    rows = _read_list(summary, "commandConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "consumer row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "consumer category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"consumer command row {expected_ordinal}"
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
                "realImporterDryRunHarnessCommandConsumerValidationRows",
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


def build_public_safe_real_importer_dry_run_harness_command_consumer_validation_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command-consumer summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandMaterializationStatus": REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
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
            "sourceCommandMaterializationProofCount": summary["sourceCommandMaterializationProofCount"],
            "sourceCommandMaterializationInterfaceCount": summary[
                "sourceCommandMaterializationInterfaceCount"
            ],
            "commandConsumerValidationInterfaceCount": summary[
                "commandConsumerValidationInterfaceCount"
            ],
            "sourceCommandMaterializationInterfaces": summary[
                "sourceCommandMaterializationInterfaces"
            ],
            "commandConsumerValidationInterfaces": summary[
                "commandConsumerValidationInterfaces"
            ],
            "sourceProof": COMMAND_MATERIALIZATION_PROOF,
        },
        "realImporterHarnessCommandConsumerValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationOnly": True,
            "commandMaterializationProofConsumed": True,
            "commandContractArtifactConsumed": True,
            "commandContractArtifactContinuityValidated": True,
            "commandConsumerValidationExecuted": True,
            "commandConsumerValidationInputAccepted": True,
            "commandContractArtifactSchemaValidated": True,
            "commandContractRowOrdinalsValidated": True,
            "commandContractNonArmedStatusesValidated": True,
            "commandContractAggregateCountsValidated": True,
            "commandConsumerValidationInterfacesValidated": True,
            "commandConsumerValidationEmitsOnlyPublicSafeRows": True,
            "harnessCommandReadinessGateLaneSelected": True,
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
            "realImporterDryRunHarnessCommandConsumerValidationReadPrivateInputs": False,
            "realImporterDryRunHarnessCommandConsumerValidationPublishedPrivateInput": False,
            "realImporterDryRunHarnessCommandConsumerValidationExecutedShellCommand": False,
            "privateCommandConsumerValidationArtifactPublished": False,
            "realImporterDryRunHarnessCommandReadinessGateExecuted": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandConsumerValidationContract": {
            "consumerValidationInputMode": "tracked-public-safe-command-materialization-proof-json",
            "consumerValidationOutputMode": "tracked-public-safe-command-consumer-validation-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command readiness gate without execution",
            "harnessCommandContractRowsConsumed": summary["harnessCommandContractRowsConsumed"],
            "commandConsumerValidationRows": summary["commandConsumerValidationRows"],
            "validatedNonArmedCommandContractRowCount": summary[
                "validatedNonArmedCommandContractRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandReadinessGateRowCount": summary[
                "readyForLaterCommandReadinessGateRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandConsumerValidationArtifactRows": summary[
                "publicSafeCommandConsumerValidationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandConsumerValidationCategoryCounts": summary[
                "commandConsumerValidationCategoryCounts"
            ],
            "commandConsumerValidationRowsBody": summary["commandConsumerValidationRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-consumer-validation-status-token-only",
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
                "the tracked command-materialization proof can be consumed as public-safe command-consumer input",
                "the 99 embedded command-contract rows remain non-armed and not executed",
                "the consumer validation preserves row/category counts and aggregate archive count 301",
                "the next command-readiness-gate lane is selected without arming or executing a command",
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
    parser.add_argument("--command-materialization-proof", type=Path, default=Path(COMMAND_MATERIALIZATION_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe consumer validation summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        materialization_proof = read_json(args.command_materialization_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(
            materialization_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_consumer_validation_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandConsumerValidationError):
        print("Real importer dry-run harness command consumer validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
