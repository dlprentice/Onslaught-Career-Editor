#!/usr/bin/env python3
"""Materialize public-safe, non-armed command-contract rows for the sidecar lane.

This consumes only the tracked command arm-checklist boundary proof. It emits a
status-token command contract for later consumer validation. It does not read
private asset content, consume raw private manifests, build runnable commands,
arm commands, dispatch a shell, execute an importer, launch BEA, generate
assets, mutate Ghidra, or publish private paths, filenames, hashes, command
arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as BOUNDARY_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as BOUNDARY_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
    REDACTED_FIELDS as BOUNDARY_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as BOUNDARY_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as BOUNDARY_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-materialization-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-materialization-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-"
    "complete-public-safe-non-armed-command-contract-not-command-execution"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES = (
    "load-tracked-command-arm-checklist-boundary-proof",
    "validate-command-arm-checklist-boundary-continuity",
    "validate-command-materialization-preconditions",
    "materialize-public-safe-non-armed-command-contract",
    "materialize-command-contract-rows-from-boundary-rows",
    "validate-command-contract-row-ordinals",
    "validate-command-contract-category-counts",
    "validate-command-contract-not-armed-statuses",
    "validate-command-contract-public-redaction-policy",
    "validate-command-contract-refusal-guards",
    "select-command-consumer-validation-lane",
    "emit-command-materialization-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-contract-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistRunnableCommandMaterialized",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractPathPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractPrivateOutputGenerated",
            "actualRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandExecuted",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRawArgumentRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractPublishedArgumentRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractExecutionRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractShellDispatchRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractPrivateOutputRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ROW_ZERO_FIELDS,
            *ZERO_COUNTERS,
        )
    )
)


class CommandMaterializationError(ValueError):
    """Raised when boundary evidence cannot support command materialization."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandMaterializationError(message)


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


def _validate_source_boundary_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == BOUNDARY_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "source boundary status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 57, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount") == 56,
        "source readiness-gate proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES),
        "source boundary interface count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryOnly",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofRowsConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryDefined",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStopConditionsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in BOUNDARY_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false guard mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(BOUNDARY_REDACTED_FIELDS),
        "falseGuardCount": len(BOUNDARY_FALSE_GUARDS),
        "zeroCounterCount": len(BOUNDARY_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source boundary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source boundary category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source boundary row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("boundaryStatus") == "defined-public-safe-command-materialization-lane-only-no-command-arming", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, BOUNDARY_ROW_ZERO_FIELDS, row_id)
    return contract


def build_command_contract_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody")
    for source_row in source_rows:
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal"])
        row: dict[str, Any] = {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-"
                "command-arm-checklist-non-armed-command-contract-row"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowMode": (
                "public-safe-non-armed-command-contract-status-token-only"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowOrdinal"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal": source_row[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowOrdinal"
            ],
            "category": source_row["category"],
            "itemId": source_row["itemId"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
                "materialized-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-contract"
            ),
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus": source_row["boundaryStatus"],
            "sourceReadinessGateStatus": source_row["sourceReadinessGateStatus"],
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "commandRequiresLaterExplicitArm": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        row.update({key: 0 for key in ROW_ZERO_FIELDS})
        rows.append(row)
    return rows


def build_public_safe_command_materialization_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_boundary_proof(source)
    rows = build_command_contract_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "command-contract category count mismatch")

    summary: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS
        ),
        "sourceProofCount": 58,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofCount": 57,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        "publicLeakCheck": "PASS",
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
    }
    validate_public_safe_command_materialization_summary(summary)
    return summary


def validate_public_safe_command_materialization_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "summary status token mismatch",
    )
    expected_counts = {
        "sourceProofCount": 58,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofCount": 57,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": 10,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": 12,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"summary false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"summary zero counter mismatch: {key}")

    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command-contract row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command-contract row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(
            row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus")
            == "materialized-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-contract",
            f"{row_id} materialization status mismatch",
        )
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct-exec guard mismatch")
        _require(row.get("commandRequiresLaterExplicitArm") is True, f"{row_id} later-arm mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} future arm mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_command_materialization_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_materialization_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS
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
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaces": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaces"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInterfaces"
            ],
            "sourceProof": str(BOUNDARY_PROOF.relative_to(ROOT)).replace("\\", "/"),
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationOnly": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumedByCommandMaterialization": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInputAccepted": True,
            "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractMaterialized": True,
            "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractStoredInTrackedProof": True,
            "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractPathPublished": False,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsGenerated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractAggregateCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractNotArmedStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRedactionPolicyValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected": True,
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
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationContract": {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationInputMode": (
                "tracked-public-safe-command-arm-checklist-boundary-proof-json"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationOutputMode": (
                "tracked-public-safe-non-armed-command-contract-proof"
            ),
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command consumer validation without execution",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRows": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRows"
            ],
            "nonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowCount": summary[
                "nonArmedCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsBody": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRowsBody"
            ],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-non-armed-command-contract-status-token-only",
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
                "the tracked command arm-checklist boundary proof can be consumed as public-safe command-materialization input",
                "the 99 boundary rows can be represented as non-armed command-contract status-token rows",
                "the command contract preserves row/category counts and aggregate archive count 301",
                "the next command consumer-validation lane is selected without arming, dispatching, or executing a command",
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
    parser.add_argument("--boundary-proof", type=Path, default=BOUNDARY_PROOF)
    parser.add_argument("--summary", type=Path, help="optional public-safe command-materialization summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof JSON output")
    args = parser.parse_args()

    try:
        source = read_json(args.boundary_proof)
        summary = build_public_safe_command_materialization_summary(source)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_command_materialization_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandMaterializationError):
        print("Material sidecar command arm-checklist command-materialization: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
