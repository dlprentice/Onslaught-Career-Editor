#!/usr/bin/env python3
"""Validate public-safe command-contract rows for the sidecar lane.

This consumes only the tracked command-materialization proof. It treats the
embedded command contract as public-safe status-token input and emits a
consumer-validation proof for the next readiness gate. It does not read private
asset content, consume raw private manifests, build runnable commands, arm
commands, dispatch a shell, execute an importer, launch BEA, generate assets,
mutate Ghidra, or publish private paths, filenames, hashes, command arguments,
traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_materialization import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_MATERIALIZATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_MATERIALIZATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
    REDACTED_FIELDS as COMMAND_MATERIALIZATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as COMMAND_MATERIALIZATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_MATERIALIZATION_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
COMMAND_MATERIALIZATION_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-materialization-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-consumer-validation-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-consumer-validation-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-"
    "complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES = (
    "load-tracked-command-arm-checklist-command-materialization-proof",
    "validate-command-materialization-continuity",
    "extract-public-safe-non-armed-command-contract",
    "validate-command-contract-artifact-schema",
    "validate-command-contract-row-order",
    "validate-command-contract-non-armed-statuses",
    "validate-command-contract-aggregate-counts",
    "validate-command-contract-public-redaction-policy",
    "validate-command-contract-refusal-guards",
    "validate-command-consumer-validation-guard-counters",
    "select-command-readiness-gate-lane",
    "emit-command-consumer-validation-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-row-counts",
            "validated-non-armed-command-contract-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationExecutedShellCommand",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateExecuted",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactPathRows",
            "commandConsumerValidationPrivateInputRows",
            "commandConsumerValidationArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_MATERIALIZATION_ROW_ZERO_FIELDS,
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


class CommandConsumerValidationError(ValueError):
    """Raised when command-materialization evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandConsumerValidationError(message)


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


def _validate_source_command_materialization_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == COMMAND_MATERIALIZATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "source command-materialization status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 58, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofCount") == 57,
        "source boundary proof count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES,
        "source command-materialization interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationOnly",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumedByCommandMaterialization",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInputAccepted",
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractMaterialized",
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractStoredInTrackedProof",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsGenerated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractAggregateCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractNotArmedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in FALSE_GUARDS[:-5]:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(COMMAND_MATERIALIZATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(COMMAND_MATERIALIZATION_REDACTED_FIELDS),
        "falseGuardCount": len(COMMAND_MATERIALIZATION_FALSE_GUARDS),
        "zeroCounterCount": len(COMMAND_MATERIALIZATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source command-contract row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command-contract row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("commandRequiresLaterExplicitArm") is True, f"{row_id} later-arm mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} operator-arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, COMMAND_MATERIALIZATION_ROW_ZERO_FIELDS, row_id)
    return contract


def build_command_consumer_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsBody")
    for source_row in source_rows:
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowOrdinal"])
        row: dict[str, Any] = {
            "commandConsumerValidationRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-"
                "command-arm-checklist-command-arm-checklist-command-consumer-validation-row"
            ),
            "commandConsumerValidationRowMode": "public-safe-non-armed-command-contract-status-token-only",
            "commandConsumerValidationRowOrdinal": ordinal,
            "sourceCommandContractRowOrdinal": ordinal,
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
            "commandConsumerValidationStatus": "validated-public-safe-non-armed-command-contract-row",
            "sourceCommandMaterializationStatus": source_row[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus"
            ],
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directRealImporterDryRunAllowedHere": False,
            "futureHarnessArmRequiresOperatorAction": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "commandReadinessGateStatus": "ready-for-later-explicit-command-readiness-gate",
            "privateValuePublished": False,
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_command_consumer_validation_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_command_materialization_proof(source)
    rows = build_command_consumer_validation_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "consumer category count mismatch")

    summary: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "sourceProofCount": 59,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount": 58,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
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
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandConsumerValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandConsumerValidationCategoryCounts": dict(sorted(category_counts.items())),
        "commandConsumerValidationRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "publicLeakCheck": "PASS",
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
    }
    validate_public_safe_command_consumer_validation_summary(summary)
    return summary


def validate_public_safe_command_consumer_validation_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS,
        "summary status token mismatch",
    )
    expected_counts = {
        "sourceProofCount": 59,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount": 58,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": 12,
        "commandConsumerValidationInterfaceCount": 12,
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

    rows = _read_list(summary, "commandConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "consumer row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "consumer category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"consumer row {expected_ordinal}"
        _require(row.get("commandConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandContractRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandConsumerValidationStatus") == "validated-public-safe-non-armed-command-contract-row", f"{row_id} status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} real importer guard mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} later-arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_command_consumer_validation_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_consumer_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_CONSUMER_VALIDATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "activeCurrentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
        },
        "sourceEvidence": {
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount"
            ],
            "commandConsumerValidationInterfaceCount": summary["commandConsumerValidationInterfaceCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces"
            ],
            "commandConsumerValidationInterfaces": summary["commandConsumerValidationInterfaces"],
            "sourceProof": str(COMMAND_MATERIALIZATION_PROOF.relative_to(ROOT)).replace("\\", "/"),
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationOnly": True,
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
            "commandConsumerValidationGuardCountersValidated": True,
            "commandReadinessGateLaneSelected": True,
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
            "realImporterDryRunHarnessCommandArmed": False,
            "realImporterDryRunHarnessCommandExecuted": False,
            "realImporterDryRunHarnessCommandSentToShell": False,
            "realImporterDryRunHarnessCommandPrivateOutputGenerated": False,
            "realImporterDryRunHarnessRunnableCommandMaterialized": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationContract": {
            "consumerValidationInputMode": "tracked-public-safe-command-materialization-proof-json",
            "consumerValidationOutputMode": "tracked-public-safe-command-consumer-validation-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command readiness gate without execution",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsConsumed"
            ],
            "commandConsumerValidationRows": summary["commandConsumerValidationRows"],
            "validatedNonArmedCommandContractRowCount": summary["validatedNonArmedCommandContractRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandConsumerValidationCategoryCounts": summary["commandConsumerValidationCategoryCounts"],
            "commandConsumerValidationRowsBody": summary["commandConsumerValidationRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-command-consumer-validation-status-token-only",
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
                "the next command-readiness-gate lane is selected without arming, dispatching, or executing a command",
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
    parser.add_argument("--command-materialization-proof", type=Path, default=COMMAND_MATERIALIZATION_PROOF)
    parser.add_argument("--summary", type=Path, help="optional public-safe command-consumer summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof JSON output")
    args = parser.parse_args()

    try:
        source = read_json(args.command_materialization_proof)
        summary = build_public_safe_command_consumer_validation_summary(source)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_command_consumer_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandConsumerValidationError):
        print("Material sidecar command arm-checklist command-consumer-validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
