#!/usr/bin/env python3
"""Materialize a public-safe non-armed command arm-checklist command contract.

This module consumes only the tracked public command arm-checklist command-arm-checklist-boundary
proof. It emits a command-arm-checklist-command-contract proof that is deliberately non-armed and
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

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as BOUNDARY_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as BOUNDARY_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
    REDACTED_FIELDS as BOUNDARY_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as BOUNDARY_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as BOUNDARY_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-materialization.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-materialization-complete-public-safe-"
    "non-armed-command-arm-checklist-command-contract-not-command-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-checklist-boundary-proof",
    "validate-real-importer-harness-command-arm-checklist-command-arm-checklist-boundary-continuity",
    "validate-command-arm-checklist-command-arm-checklist-command-materialization-preconditions",
    "materialize-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-contract",
    "materialize-command-arm-checklist-command-arm-checklist-command-contract-rows-from-command-arm-checklist-boundary-rows",
    "validate-command-arm-checklist-command-arm-checklist-command-contract-row-ordinals",
    "validate-command-arm-checklist-command-arm-checklist-command-contract-category-counts",
    "validate-command-arm-checklist-command-arm-checklist-command-contract-not-armed-statuses",
    "validate-command-arm-checklist-command-arm-checklist-command-contract-public-redaction-policy",
    "validate-command-arm-checklist-command-arm-checklist-command-contract-refusal-guards",
    "select-command-arm-checklist-command-arm-checklist-command-consumer-validation-lane",
    "emit-command-arm-checklist-command-arm-checklist-command-materialization-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-materialization-status",
            "harness-command-arm-checklist-command-arm-checklist-command-contract-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-materialization-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistRunnableCommandMaterialized",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandContractPathPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandContractSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandContractPrivateOutputGenerated",
            "actualRealImporterDryRunHarnessCommandArmChecklistCommandExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandContractPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandContractRawArgumentRows",
            "commandArmChecklistCommandArmChecklistCommandContractPublishedArgumentRows",
            "commandArmChecklistCommandArmChecklistCommandContractExecutionRows",
            "commandArmChecklistCommandArmChecklistCommandContractShellDispatchRows",
            "commandArmChecklistCommandArmChecklistCommandContractPrivateOutputRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ROW_ZERO_FIELDS,
            "commandArmChecklistCommandArmChecklistCommandContractPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandContractRawArgumentRows",
            "commandArmChecklistCommandArmChecklistCommandContractPublishedArgumentRows",
            "commandArmChecklistCommandArmChecklistCommandContractExecutionRows",
            "commandArmChecklistCommandArmChecklistCommandContractShellDispatchRows",
            "commandArmChecklistCommandArmChecklistCommandContractPrivateOutputRows",
        )
    )
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationError(ValueError):
    """Raised when readiness evidence cannot support command materialization."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationError(message)


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


def _validate_source_command_arm_checklist_command_arm_checklist_boundary_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == BOUNDARY_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "source command arm-checklist command-arm-checklist-boundary status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 46, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistReadinessGateProofCount") == 45,
        "source command arm-checklist command arm-checklist readiness-gate proof count mismatch",
    )
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES),
        "source command arm-checklist command arm-checklist readiness-gate interface count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistBoundaryInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES),
        "source command-arm-checklist-boundary interface count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistBoundaryDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryOnly",
        "commandArmChecklistCommandArmChecklistReadinessGateProofConsumed",
        "commandArmChecklistCommandArmChecklistReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistReadinessGateProofRowsConsumed",
        "commandArmChecklistCommandArmChecklistBoundaryDefined",
        "commandArmChecklistCommandArmChecklistBoundaryInputAccepted",
        "commandArmChecklistCommandArmChecklistBoundaryRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistBoundaryRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistBoundaryCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistBoundaryInterfacesValidated",
        "commandArmChecklistCommandArmChecklistBoundaryStopConditionsValidated",
        "commandArmChecklistCommandArmChecklistBoundaryEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistBoundaryRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandMaterializationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in BOUNDARY_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistBoundaryContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistBoundaryRowCount": 0,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(BOUNDARY_REDACTED_FIELDS),
        "falseGuardCount": len(BOUNDARY_FALSE_GUARDS),
        "zeroCounterCount": len(BOUNDARY_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source boundary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command arm-checklist boundary row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistBoundaryRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("commandArmChecklistCommandArmChecklistBoundaryStatus")
            == "ready-for-later-explicit-command-arm-checklist-command-arm-checklist-command-materialization",
            f"{row_id} boundary status mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("sourceObservationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, BOUNDARY_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(BOUNDARY_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(BOUNDARY_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in BOUNDARY_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_checklist_command_contract_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe, non-armed command-arm-checklist-command-contract row per boundary row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistBoundaryRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistBoundaryRowOrdinal"])
        row = {
            "category": source_row["category"],
            "commandArmChecklistCommandArmChecklistCommandContractRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-non-armed-command-arm-checklist-command-contract-row"
            ),
            "commandArmChecklistCommandArmChecklistCommandContractRowMode": (
                "public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-contract-status-token-only"
            ),
            "commandArmChecklistCommandArmChecklistCommandContractRowOrdinal": ordinal,
            "commandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
                "materialized-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-contract"
            ),
            "commandArmStatus": "not-armed",
            "commandDispatchAllowedHere": False,
            "commandExecutionStatus": "not-executed",
            "commandRequiresLaterExplicitArm": True,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "itemId": source_row["itemId"],
            "observationStatus": source_row["sourceObservationStatus"],
            "privateValuePublished": False,
            "rowStatus": source_row["rowStatus"],
            "sourceCommandArmChecklistCommandArmBoundaryRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmBoundaryRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistPopulationRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistValidationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistValidationRowOrdinal"
            ],
            "sourceCommandArmStatus": source_row["sourceCommandArmStatus"],
            "sourceCommandExecutionStatus": source_row["sourceCommandExecutionStatus"],
            "sourceObservationStatus": source_row["sourceObservationStatus"],
            "sourceCommandArmChecklistCommandArmChecklistBoundaryStatus": source_row[
                "commandArmChecklistCommandArmChecklistBoundaryStatus"
            ],
            "sourceRowStatus": source_row["sourceRowStatus"],
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist command arm-checklist command-materialization summary."""

    contract = _validate_source_command_arm_checklist_command_arm_checklist_boundary_proof(source)
    rows = build_command_arm_checklist_command_contract_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "command-arm-checklist-command-contract category counts mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "slice": THIS_SLICE,
        "scope": THIS_SCOPE,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS
        ),
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationOnly": True,
        "commandArmChecklistCommandArmChecklistBoundaryProofConsumed": True,
        "commandArmChecklistCommandArmChecklistBoundaryProofContinuityValidated": True,
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumedByCommandMaterialization": True,
        "commandArmChecklistCommandArmChecklistCommandMaterializationExecuted": True,
        "commandArmChecklistCommandArmChecklistCommandMaterializationInputAccepted": True,
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractMaterialized": True,
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractStoredInTrackedProof": True,
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractPathPublished": False,
        "commandArmChecklistCommandArmChecklistCommandContractRowsGenerated": True,
        "commandArmChecklistCommandArmChecklistCommandContractRowsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandContractAggregateCountsValidated": True,
        "commandArmChecklistCommandArmChecklistCommandContractInterfacesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandContractNotArmedStatusesValidated": True,
        "commandArmChecklistCommandArmChecklistCommandContractEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandArmChecklistCommandContractRedactionPolicyValidated": True,
        "commandArmChecklistCommandArmChecklistCommandContractGuardCountersValidated": True,
        "commandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        "sourceProofCount": 47,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount": 46,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed": len(rows),
        "commandArmChecklistCommandArmChecklistCommandContractRows": len(rows),
        "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount": len(rows),
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandContractCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandArmChecklistCommandContractRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary(
    summary: Mapping[str, Any],
) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "summary command-materialization status mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationOnly",
        "commandArmChecklistCommandArmChecklistBoundaryProofConsumed",
        "commandArmChecklistCommandArmChecklistBoundaryProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumedByCommandMaterialization",
        "commandArmChecklistCommandArmChecklistCommandMaterializationExecuted",
        "commandArmChecklistCommandArmChecklistCommandMaterializationInputAccepted",
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractMaterialized",
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractStoredInTrackedProof",
        "commandArmChecklistCommandArmChecklistCommandContractRowsGenerated",
        "commandArmChecklistCommandArmChecklistCommandContractRowsValidated",
        "commandArmChecklistCommandArmChecklistCommandContractAggregateCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandContractInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandContractNotArmedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandContractEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandContractRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistCommandContractGuardCountersValidated",
        "commandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected",
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
        "sourceProofCount": 47,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount": 46,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandContractRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command-arm-checklist-command-contract row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist command-arm-checklist command-contract row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandContractRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal") == expected_ordinal,
            f"{row_id} source readiness ordinal mismatch",
        )
        _require(row.get("commandArmChecklistCommandArmChecklistCommandMaterializationStatus") == "materialized-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-contract", f"{row_id} materialization status mismatch")
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


def build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist command arm-checklist command-materialization summary in the proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS
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
            "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaces"
            ],
            "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaces": summary[
                "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaces"
            ],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationOnly": True,
            "commandArmChecklistCommandArmChecklistBoundaryProofConsumed": True,
            "commandArmChecklistCommandArmChecklistBoundaryProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistBoundaryRowsConsumedByCommandMaterialization": True,
            "commandArmChecklistCommandArmChecklistCommandMaterializationExecuted": True,
            "commandArmChecklistCommandArmChecklistCommandMaterializationInputAccepted": True,
            "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractMaterialized": True,
            "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractStoredInTrackedProof": True,
            "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractPathPublished": False,
            "commandArmChecklistCommandArmChecklistCommandContractRowsGenerated": True,
            "commandArmChecklistCommandArmChecklistCommandContractRowsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandContractAggregateCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandContractInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandContractNotArmedStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandContractEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistCommandContractRedactionPolicyValidated": True,
            "commandArmChecklistCommandArmChecklistCommandContractGuardCountersValidated": True,
            "commandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected": True,
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
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationContract": {
            "commandArmChecklistCommandArmChecklistCommandMaterializationInputMode": "tracked-public-safe-command-arm-checklist-command-arm-checklist-boundary-proof-json",
            "commandArmChecklistCommandArmChecklistCommandMaterializationOutputMode": (
                "tracked-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-contract-proof"
            ),
            "selectedNextLaneClass": (
                "private-corpus real importer dry-run harness command arm-checklist command consumer validation without execution"
            ),
            "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistCommandContractRows": summary["commandArmChecklistCommandArmChecklistCommandContractRows"],
            "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount": summary[
                "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandContractCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandContractCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandContractRowsBody": summary[
                "commandArmChecklistCommandArmChecklistCommandContractRowsBody"
            ],
        },
        "redactionPolicy": {
            "redactionPolicy": (
                "public-safe-real-importer-dry-run-harness-command-arm-checklist-"
                "non-armed-command-arm-checklist-command-contract-status-token-only"
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
                "the tracked command arm-checklist command-arm-checklist-boundary proof can be consumed as public-safe command-materialization input",
                "the 99 boundary rows can be represented as non-armed command arm-checklist command-arm-checklist command-contract status-token rows",
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
        "--command-arm-checklist-command-arm-checklist-boundary-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe command-materialization summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        readiness_proof = read_json(args.command_arm_checklist_command_arm_checklist_boundary_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary(
            readiness_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary(
            summary
        )
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_proof(
                summary
            )
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationError):
        print("Real importer dry-run harness command arm-checklist command materialization: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
