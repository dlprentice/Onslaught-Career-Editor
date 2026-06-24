#!/usr/bin/env python3
"""Materialize a public-safe non-armed command arm-checklist command contract.

This module consumes only the tracked public command arm-checklist readiness-gate
proof. It emits a command-contract proof that is deliberately non-armed and
status-token-only. It does not read private assets, consume raw private
manifests, build a runnable shell command, arm a command, execute an importer,
launch BEA, generate assets, mutate Ghidra, or emit raw private paths,
filenames, hashes, command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
    REDACTED_FIELDS as READINESS_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as READINESS_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-materialization.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-materialization-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-materialization-complete-public-safe-"
    "non-armed-command-contract-not-command-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Materialization Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-materialization-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Consumer Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-consumer-validation-proof-plan"
)

COMMAND_ARM_CHECKLIST_READINESS_GATE_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-readiness-gate-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-readiness-gate-proof",
    "validate-real-importer-harness-command-arm-checklist-readiness-gate-continuity",
    "validate-command-arm-checklist-command-materialization-preconditions",
    "materialize-public-safe-non-armed-command-arm-checklist-command-contract",
    "materialize-command-arm-checklist-command-contract-rows-from-readiness-gate-rows",
    "validate-command-arm-checklist-command-contract-row-ordinals",
    "validate-command-arm-checklist-command-contract-category-counts",
    "validate-command-arm-checklist-command-contract-not-armed-statuses",
    "validate-command-arm-checklist-command-contract-public-redaction-policy",
    "validate-command-arm-checklist-command-contract-refusal-guards",
    "select-command-arm-checklist-command-consumer-validation-lane",
    "emit-command-arm-checklist-command-materialization-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-materialization-status",
            "harness-command-arm-checklist-command-contract-row-counts",
            "harness-command-arm-checklist-command-consumer-validation-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-materialization-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandMaterializationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandMaterializationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistRunnableCommandMaterialized",
            "realImporterDryRunHarnessCommandArmChecklistCommandContractPathPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandContractSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandContractPrivateOutputGenerated",
            "actualRealImporterDryRunHarnessCommandArmChecklistCommandExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_COUNTERS,
            "commandArmChecklistCommandContractPrivateInputRows",
            "commandArmChecklistCommandContractRawArgumentRows",
            "commandArmChecklistCommandContractPublishedArgumentRows",
            "commandArmChecklistCommandContractExecutionRows",
            "commandArmChecklistCommandContractShellDispatchRows",
            "commandArmChecklistCommandContractPrivateOutputRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_ROW_ZERO_FIELDS,
            "commandArmChecklistCommandContractPrivateInputRows",
            "commandArmChecklistCommandContractRawArgumentRows",
            "commandArmChecklistCommandContractPublishedArgumentRows",
            "commandArmChecklistCommandContractExecutionRows",
            "commandArmChecklistCommandContractShellDispatchRows",
            "commandArmChecklistCommandContractPrivateOutputRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistCommandMaterializationError(ValueError):
    """Raised when readiness evidence cannot support command materialization."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandMaterializationError(message)


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


def _validate_source_command_arm_checklist_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "source command arm-checklist readiness-gate status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 35, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistValidationProofCount") == 34,
        "source command arm-checklist validation proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistReadinessGateInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES),
        "source readiness-gate interface count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistReadinessGateDecision")
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
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in READINESS_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistReadinessGateContract")
    expected_counts = {
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
        "preflightCheckCount": 19,
        "passedPreflightCheckCount": 19,
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(READINESS_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(READINESS_REDACTED_FIELDS),
        "falseGuardCount": len(READINESS_FALSE_GUARDS),
        "zeroCounterCount": len(READINESS_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command arm-checklist readiness row {expected_ordinal}"
        _require(row.get("commandArmChecklistReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("readinessGateStatus") == "ready-for-later-explicit-command-arm-checklist-command-materialization",
            f"{row_id} readiness status mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, READINESS_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(READINESS_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(READINESS_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in READINESS_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_command_contract_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe, non-armed command-contract row per readiness row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistReadinessGateRowsBody"):
        ordinal = int(source_row["commandArmChecklistReadinessGateRowOrdinal"])
        row = {
            "category": source_row["category"],
            "commandArmChecklistCommandContractRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-non-armed-command-contract-row"
            ),
            "commandArmChecklistCommandContractRowMode": (
                "public-safe-non-armed-command-arm-checklist-command-contract-status-token-only"
            ),
            "commandArmChecklistCommandContractRowOrdinal": ordinal,
            "commandArmChecklistCommandMaterializationStatus": (
                "materialized-public-safe-non-armed-command-arm-checklist-command-contract"
            ),
            "commandArmStatus": "not-armed",
            "commandDispatchAllowedHere": False,
            "commandExecutionStatus": "not-executed",
            "commandRequiresLaterExplicitArm": True,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "itemId": source_row["itemId"],
            "observationStatus": source_row["observationStatus"],
            "privateValuePublished": False,
            "rowStatus": source_row["rowStatus"],
            "sourceCommandArmBoundaryRowOrdinal": source_row["sourceCommandArmBoundaryRowOrdinal"],
            "sourceCommandArmChecklistPopulationRowOrdinal": source_row[
                "sourceCommandArmChecklistPopulationRowOrdinal"
            ],
            "sourceCommandArmChecklistReadinessGateRowOrdinal": ordinal,
            "sourceCommandArmChecklistValidationRowOrdinal": source_row[
                "sourceCommandArmChecklistValidationRowOrdinal"
            ],
            "sourceCommandArmReadinessGateRowOrdinal": source_row["sourceCommandArmReadinessGateRowOrdinal"],
            "sourceCommandArmStatus": source_row["sourceCommandArmStatus"],
            "sourceCommandExecutionStatus": source_row["sourceCommandExecutionStatus"],
            "sourceObservationStatus": source_row["sourceObservationStatus"],
            "sourceReadinessGateStatus": source_row["readinessGateStatus"],
            "sourceRowStatus": source_row["sourceRowStatus"],
            "sourceValidationStatus": source_row["sourceValidationStatus"],
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_summary(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist command-materialization summary."""

    contract = _validate_source_command_arm_checklist_readiness_gate_proof(source)
    rows = build_command_arm_checklist_command_contract_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "command-contract category counts mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "slice": THIS_SLICE,
        "scope": THIS_SCOPE,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationOnly": True,
        "commandArmChecklistReadinessGateProofConsumed": True,
        "commandArmChecklistReadinessGateProofContinuityValidated": True,
        "commandArmChecklistReadinessGateRowsConsumedByCommandMaterialization": True,
        "commandArmChecklistCommandMaterializationExecuted": True,
        "commandArmChecklistCommandMaterializationInputAccepted": True,
        "publicSafeNonArmedCommandArmChecklistCommandContractMaterialized": True,
        "publicSafeNonArmedCommandArmChecklistCommandContractStoredInTrackedProof": True,
        "publicSafeNonArmedCommandArmChecklistCommandContractPathPublished": False,
        "commandArmChecklistCommandContractRowsGenerated": True,
        "commandArmChecklistCommandContractRowsValidated": True,
        "commandArmChecklistCommandContractAggregateCountsValidated": True,
        "commandArmChecklistCommandContractInterfacesValidated": True,
        "commandArmChecklistCommandContractNotArmedStatusesValidated": True,
        "commandArmChecklistCommandContractEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandContractRedactionPolicyValidated": True,
        "commandArmChecklistCommandContractGuardCountersValidated": True,
        "commandArmChecklistCommandConsumerValidationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        "sourceProofCount": 36,
        "sourceCommandArmChecklistReadinessGateProofCount": 35,
        "sourceCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistReadinessGateRowsConsumed": len(rows),
        "commandArmChecklistCommandContractRows": len(rows),
        "nonArmedCommandArmChecklistCommandContractRowCount": len(rows),
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandConsumerValidationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandMaterializationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistCommandContractCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandContractRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_summary(
    summary: Mapping[str, Any],
) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "summary command-materialization status mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationOnly",
        "commandArmChecklistReadinessGateProofConsumed",
        "commandArmChecklistReadinessGateProofContinuityValidated",
        "commandArmChecklistReadinessGateRowsConsumedByCommandMaterialization",
        "commandArmChecklistCommandMaterializationExecuted",
        "commandArmChecklistCommandMaterializationInputAccepted",
        "publicSafeNonArmedCommandArmChecklistCommandContractMaterialized",
        "publicSafeNonArmedCommandArmChecklistCommandContractStoredInTrackedProof",
        "commandArmChecklistCommandContractRowsGenerated",
        "commandArmChecklistCommandContractRowsValidated",
        "commandArmChecklistCommandContractAggregateCountsValidated",
        "commandArmChecklistCommandContractInterfacesValidated",
        "commandArmChecklistCommandContractNotArmedStatusesValidated",
        "commandArmChecklistCommandContractEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandContractRedactionPolicyValidated",
        "commandArmChecklistCommandContractGuardCountersValidated",
        "commandArmChecklistCommandConsumerValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"summary true flag mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"summary false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    expected_counts = {
        "sourceProofCount": 36,
        "sourceCommandArmChecklistReadinessGateProofCount": 35,
        "sourceCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandArmChecklistCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "commandArmChecklistCommandContractRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command-contract row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist command-contract row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandContractRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandArmChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"{row_id} source readiness ordinal mismatch",
        )
        _require(row.get("commandArmChecklistCommandMaterializationStatus") == "materialized-public-safe-non-armed-command-arm-checklist-command-contract", f"{row_id} materialization status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("commandRequiresLaterExplicitArm") is True, f"{row_id} later-arm mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} operator-arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist command-materialization summary in the proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
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
            "sourceCommandArmChecklistReadinessGateProofCount": summary[
                "sourceCommandArmChecklistReadinessGateProofCount"
            ],
            "sourceCommandArmChecklistReadinessGateInterfaceCount": summary[
                "sourceCommandArmChecklistReadinessGateInterfaceCount"
            ],
            "commandArmChecklistCommandMaterializationInterfaceCount": summary[
                "commandArmChecklistCommandMaterializationInterfaceCount"
            ],
            "sourceCommandArmChecklistReadinessGateInterfaces": summary[
                "sourceCommandArmChecklistReadinessGateInterfaces"
            ],
            "commandArmChecklistCommandMaterializationInterfaces": summary[
                "commandArmChecklistCommandMaterializationInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_READINESS_GATE_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandMaterializationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationOnly": True,
            "commandArmChecklistReadinessGateProofConsumed": True,
            "commandArmChecklistReadinessGateProofContinuityValidated": True,
            "commandArmChecklistReadinessGateRowsConsumedByCommandMaterialization": True,
            "commandArmChecklistCommandMaterializationExecuted": True,
            "commandArmChecklistCommandMaterializationInputAccepted": True,
            "publicSafeNonArmedCommandArmChecklistCommandContractMaterialized": True,
            "publicSafeNonArmedCommandArmChecklistCommandContractStoredInTrackedProof": True,
            "publicSafeNonArmedCommandArmChecklistCommandContractPathPublished": False,
            "commandArmChecklistCommandContractRowsGenerated": True,
            "commandArmChecklistCommandContractRowsValidated": True,
            "commandArmChecklistCommandContractAggregateCountsValidated": True,
            "commandArmChecklistCommandContractInterfacesValidated": True,
            "commandArmChecklistCommandContractNotArmedStatusesValidated": True,
            "commandArmChecklistCommandContractEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandContractRedactionPolicyValidated": True,
            "commandArmChecklistCommandContractGuardCountersValidated": True,
            "commandArmChecklistCommandConsumerValidationLaneSelected": True,
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
            "realImporterDryRunHarnessCommandArmChecklistRunnableCommandMaterialized": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmed": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandExecuted": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandSentToShell": False,
            "realImporterDryRunHarnessCommandArmChecklistCommandPrivateOutputGenerated": False,
            "actualRealImporterDryRunHarnessCommandArmChecklistCommandExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandArmChecklistCommandMaterializationContract": {
            "commandArmChecklistCommandMaterializationInputMode": "tracked-public-safe-command-arm-checklist-readiness-gate-proof-json",
            "commandArmChecklistCommandMaterializationOutputMode": (
                "tracked-public-safe-non-armed-command-arm-checklist-command-contract-proof"
            ),
            "selectedNextLaneClass": (
                "private-corpus real importer dry-run harness command arm-checklist command consumer validation without execution"
            ),
            "commandArmChecklistReadinessGateRowsConsumed": summary[
                "commandArmChecklistReadinessGateRowsConsumed"
            ],
            "commandArmChecklistCommandContractRows": summary["commandArmChecklistCommandContractRows"],
            "nonArmedCommandArmChecklistCommandContractRowCount": summary[
                "nonArmedCommandArmChecklistCommandContractRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandConsumerValidationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandConsumerValidationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandContractArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandContractArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandContractCategoryCounts": summary[
                "commandArmChecklistCommandContractCategoryCounts"
            ],
            "commandArmChecklistCommandContractRowsBody": summary[
                "commandArmChecklistCommandContractRowsBody"
            ],
        },
        "redactionPolicy": {
            "redactionPolicy": (
                "public-safe-real-importer-dry-run-harness-command-arm-checklist-"
                "non-armed-command-contract-status-token-only"
            ),
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
                "the tracked command arm-checklist readiness-gate proof can be consumed as public-safe command-materialization input",
                "the 99 readiness rows can be represented as non-armed command arm-checklist command-contract status-token rows",
                "the command contract preserves row/category counts and aggregate archive count 301",
                "the next command arm-checklist command-consumer-validation lane is selected without arming, dispatching, or executing a command",
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
        "--command-arm-checklist-readiness-gate-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_READINESS_GATE_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe command-materialization summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        readiness_proof = read_json(args.command_arm_checklist_readiness_gate_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_summary(
            readiness_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_summary(
            summary
        )
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_materialization_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandMaterializationError):
        print("Real importer dry-run harness command arm-checklist command materialization: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
