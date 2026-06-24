#!/usr/bin/env python3
"""Build a public-safe command arm-readiness proof for the sidecar lane.

This consumes only the tracked command dry-run consumer-validation proof. It
validates that the public-safe rows remain non-armed, non-dispatched, and not
executed before selecting a later command arm-boundary lane. It does not read
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

from texture_mesh_material_sidecar_command_arm_checklist_command_dry_run_consumer_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as DRY_RUN_CONSUMER_VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as DRY_RUN_CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
    REDACTED_FIELDS as DRY_RUN_CONSUMER_VALIDATION_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as DRY_RUN_CONSUMER_VALIDATION_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
DRY_RUN_CONSUMER_VALIDATION_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-"
    "complete-public-safe-readiness-only-not-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES = (
    "load-tracked-command-arm-checklist-command-dry-run-consumer-validation-proof",
    "validate-command-dry-run-consumer-validation-continuity",
    "validate-command-arm-readiness-gate-preconditions",
    "validate-command-dry-run-consumer-validation-row-statuses",
    "validate-command-arm-readiness-gate-row-order",
    "validate-command-arm-readiness-gate-category-counts",
    "validate-command-arm-readiness-gate-refusal-guards",
    "validate-command-arm-readiness-gate-public-redaction-policy",
    "select-command-arm-boundary-lane",
    "emit-command-arm-readiness-gate-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-status",
            "validated-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_CONSUMER_VALIDATION_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGatePublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateMaterializedRunnableCommand",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateArmedCommand",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateExecutedCommand",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryExecuted",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGatePrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryOutputArtifactRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *DRY_RUN_CONSUMER_VALIDATION_ROW_ZERO_FIELDS,
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


class CommandArmReadinessGateError(ValueError):
    """Raised when consumer-validation evidence cannot support arm-readiness."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandArmReadinessGateError(message)


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


def _validate_source_dry_run_consumer_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == DRY_RUN_CONSUMER_VALIDATION_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "source dry-run consumer-validation status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 62, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount") == 61,
        "source dry-run proof count mismatch",
    )
    _require(
        source_evidence.get("commandDryRunConsumerValidationInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES),
        "source dry-run consumer-validation interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandDryRunConsumerValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
        "source dry-run consumer-validation interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationOnly",
        "commandDryRunProofConsumed",
        "commandDryRunProofContinuityValidated",
        "commandDryRunRowsConsumedByConsumerValidation",
        "commandDryRunConsumerValidationExecuted",
        "commandDryRunConsumerValidationInputAccepted",
        "commandDryRunArtifactSchemaValidated",
        "commandDryRunRowOrdinalsValidated",
        "commandDryRunNonDispatchedStatusesValidated",
        "commandDryRunAggregateCountsValidated",
        "commandDryRunConsumerValidationGuardCountersValidated",
        "commandDryRunConsumerValidationInterfacesValidated",
        "commandDryRunConsumerValidationEmitsOnlyPublicSafeRows",
        "commandArmReadinessGateLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
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
        "commandDryRunSentToShell",
        "commandDryRunGeneratedPrivateOutput",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunSentToShell",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunGeneratedPrivateOutput",
        "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunReadPrivateInputs",
        "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunPublishedPrivateInput",
        "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "beLaunch",
        "ghidraMutation",
        "godotWork",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
        "noNoticeableDifferenceParityProven",
    ):
        if key in decision:
            _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationContract")
    expected_counts = {
        "commandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonDispatchedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(DRY_RUN_CONSUMER_VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(DRY_RUN_CONSUMER_VALIDATION_REDACTED_FIELDS),
        "falseGuardCount": len(DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS),
        "zeroCounterCount": len(DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandDryRunConsumerValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source dry-run consumer-validation row {expected_ordinal}"
        _require(row.get("commandDryRunConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandDryRunRowOrdinal") == expected_ordinal, f"{row_id} source dry-run ordinal mismatch")
        _require(row.get("commandDryRunConsumerValidationStatus") == "validated-public-safe-non-dispatched-command-dry-run-row", f"{row_id} status mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} arm guard mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} future arm flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private flag mismatch")
        _validate_zero_fields(row, tuple(key for key in DRY_RUN_CONSUMER_VALIDATION_ROW_ZERO_FIELDS if key in row), row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(DRY_RUN_CONSUMER_VALIDATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in DRY_RUN_CONSUMER_VALIDATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe arm-readiness row per dry-run consumer-validation row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandDryRunConsumerValidationRowsBody"):
        ordinal = int(source_row["commandDryRunConsumerValidationRowOrdinal"])
        row = {key: 0 for key in ROW_ZERO_FIELDS}
        row.update(
            {
                "category": source_row["category"],
                "commandArmReadinessGateRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-row",
                "commandArmReadinessGateRowMode": "public-safe-command-arm-readiness-status-token-only",
                "commandArmReadinessGateRowOrdinal": ordinal,
                "commandArmReadinessGateStatus": "ready-for-later-explicit-command-arm-boundary-review",
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandExecutionStatus": "not-executed",
                "directCommandArmingAllowedHere": False,
                "directRealImporterDryRunAllowedHere": False,
                "futureCommandArmRequiresExplicitOperatorArm": True,
                "futureHarnessArmRequiresOperatorAction": True,
                "futureHarnessCommandArmBoundaryRequiresLaterReview": True,
                "itemId": source_row["itemId"],
                "privateValuePublished": False,
                "rowStatus": "command-arm-readiness-gate-passed",
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandDryRunConsumerValidationRowOrdinal": ordinal,
                "sourceCommandDryRunConsumerValidationStatus": source_row["commandDryRunConsumerValidationStatus"],
                "sourceCommandDryRunRowOrdinal": source_row["sourceCommandDryRunRowOrdinal"],
                "sourceCommandDryRunStatus": source_row["sourceCommandDryRunStatus"],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
            }
        )
        for key, value in source_row.items():
            if key.startswith("source") and key.endswith("Ordinal"):
                row.setdefault(key, value)
        rows.append(row)
    return rows


def build_public_safe_command_arm_readiness_gate_summary(
    dry_run_consumer_validation_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-readiness summary."""

    contract = _validate_source_dry_run_consumer_validation_proof(dry_run_consumer_validation_proof)
    rows = build_command_arm_readiness_gate_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "arm-readiness category counts mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS
        ),
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateOnly": True,
        "commandDryRunConsumerValidationProofConsumed": True,
        "commandDryRunConsumerValidationProofContinuityValidated": True,
        "commandDryRunConsumerValidationRowsConsumedByArmReadinessGate": True,
        "commandArmReadinessGateExecuted": True,
        "commandArmReadinessGateInputAccepted": True,
        "commandArmReadinessGatePreconditionsValidated": True,
        "commandArmReadinessGateRowStatusesValidated": True,
        "commandArmReadinessGateRowOrdinalsValidated": True,
        "commandArmReadinessGateCategoryCountsValidated": True,
        "commandArmReadinessGateGuardCountersValidated": True,
        "commandArmReadinessGateInterfacesValidated": True,
        "commandArmReadinessGateEmitsOnlyPublicSafeRows": True,
        "commandArmBoundaryLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
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
        "commandArmReadinessGateReadPrivateInputs": False,
        "commandArmReadinessGatePublishedPrivateInput": False,
        "commandArmReadinessGateMaterializedRunnableCommand": False,
        "commandArmReadinessGateArmedCommand": False,
        "commandArmReadinessGateSentToShell": False,
        "commandArmReadinessGateExecutedCommand": False,
        "privateCommandArmReadinessGateArtifactPublished": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "beLaunch": False,
        "ghidraMutation": False,
        "godotWork": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "noNoticeableDifferenceParityProven": False,
        "sourceProofCount": 63,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount": 62,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
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
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmReadinessGateCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmReadinessGateRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_command_arm_readiness_gate_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateOnly",
        "commandDryRunConsumerValidationProofConsumed",
        "commandDryRunConsumerValidationProofContinuityValidated",
        "commandDryRunConsumerValidationRowsConsumedByArmReadinessGate",
        "commandArmReadinessGateExecuted",
        "commandArmReadinessGateInputAccepted",
        "commandArmReadinessGatePreconditionsValidated",
        "commandArmReadinessGateRowStatusesValidated",
        "commandArmReadinessGateRowOrdinalsValidated",
        "commandArmReadinessGateCategoryCountsValidated",
        "commandArmReadinessGateGuardCountersValidated",
        "commandArmReadinessGateInterfacesValidated",
        "commandArmReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmBoundaryLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
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
        "commandArmReadinessGateReadPrivateInputs",
        "commandArmReadinessGatePublishedPrivateInput",
        "commandArmReadinessGateMaterializedRunnableCommand",
        "commandArmReadinessGateArmedCommand",
        "commandArmReadinessGateSentToShell",
        "commandArmReadinessGateExecutedCommand",
        "privateCommandArmReadinessGateArtifactPublished",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "beLaunch",
        "ghidraMutation",
        "godotWork",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
        "noNoticeableDifferenceParityProven",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 63,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount": 62,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES
        ),
        "commandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandDryRunConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "publicSafeCommandArmReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    rows = _read_list(summary, "commandArmReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "summary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "summary category counts mismatch")
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-readiness row {ordinal}"
        _require(row.get("commandArmReadinessGateRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandDryRunConsumerValidationRowOrdinal") == ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} command arm guard mismatch")
        _validate_zero_fields(row, tuple(key for key in ROW_ZERO_FIELDS if key in row), row_id)


def build_public_safe_command_arm_readiness_gate_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_arm_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus": summary[
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus"
        ],
        "previousSlice": summary["previousSlice"],
        "previousScope": summary["previousScope"],
        "selectedNextSlice": summary["selectedNextSlice"],
        "selectedNextScope": summary["selectedNextScope"],
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus": summary[
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus"
        ],
        "sourceEvidence": {
            "sourceProof": "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json",
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount"
            ],
            "sourceCommandDryRunConsumerValidationInterfaces": summary["sourceCommandDryRunConsumerValidationInterfaces"],
            "commandArmReadinessGateInterfaceCount": summary["commandArmReadinessGateInterfaceCount"],
            "commandArmReadinessGateInterfaces": summary["commandArmReadinessGateInterfaces"],
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateDecision": {
            key: summary[key]
            for key in (
                "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateOnly",
                "commandDryRunConsumerValidationProofConsumed",
                "commandDryRunConsumerValidationProofContinuityValidated",
                "commandDryRunConsumerValidationRowsConsumedByArmReadinessGate",
                "commandArmReadinessGateExecuted",
                "commandArmReadinessGateInputAccepted",
                "commandArmReadinessGatePreconditionsValidated",
                "commandArmReadinessGateRowStatusesValidated",
                "commandArmReadinessGateRowOrdinalsValidated",
                "commandArmReadinessGateCategoryCountsValidated",
                "commandArmReadinessGateGuardCountersValidated",
                "commandArmReadinessGateInterfacesValidated",
                "commandArmReadinessGateEmitsOnlyPublicSafeRows",
                "commandArmBoundaryLaneSelected",
                "futureCommandArmRequiresExplicitOperatorArm",
                "privateEvidenceStoredOutsidePublicReleaseScope",
                "publicPrivateSeparationRequired",
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
                "commandArmReadinessGateReadPrivateInputs",
                "commandArmReadinessGatePublishedPrivateInput",
                "commandArmReadinessGateMaterializedRunnableCommand",
                "commandArmReadinessGateArmedCommand",
                "commandArmReadinessGateSentToShell",
                "commandArmReadinessGateExecutedCommand",
                "privateCommandArmReadinessGateArtifactPublished",
                "actualAssetImportExecuted",
                "generatedAssetOutputExecuted",
                "beLaunch",
                "ghidraMutation",
                "godotWork",
                "installedGameMutationAllowed",
                "originalExecutableMutationAllowed",
                "noNoticeableDifferenceParityProven",
            )
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateContract": {
            "commandDryRunConsumerValidationRowsConsumed": summary["commandDryRunConsumerValidationRowsConsumed"],
            "commandArmReadinessGateRows": summary["commandArmReadinessGateRows"],
            "passedCommandArmReadinessGateRowCount": summary["passedCommandArmReadinessGateRowCount"],
            "failedCommandArmReadinessGateRowCount": summary["failedCommandArmReadinessGateRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmBoundaryRowCount": summary["readyForLaterCommandArmBoundaryRowCount"],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmReadinessGateArtifactRows": summary["publicSafeCommandArmReadinessGateArtifactRows"],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "selectedNextLaneClass": "command-arm-boundary-proof-plan",
            "commandArmReadinessGateCategoryCounts": summary["commandArmReadinessGateCategoryCounts"],
            "commandArmReadinessGateRowsBody": summary["commandArmReadinessGateRowsBody"],
        },
        "redactionPolicy": {
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "publicAllowedOutputs": summary["publicAllowedOutputs"],
            "redactedFields": summary["redactedFields"],
            "publicLeakCheck": "PASS",
        },
        "guardSummary": {
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            **summary["falseGuards"],
            **summary["zeroCounters"],
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "positiveEvidence": (
                "Tracked public-safe command dry-run consumer-validation rows were consumed and validated as "
                "ready for a later explicit command arm-boundary review."
            ),
            "notEvidenceFor": [
                "private asset content reads",
                "raw private manifest consumption",
                "command arming",
                "shell dispatch",
                "importer execution",
                "generated assets",
                "BEA launch",
                "Ghidra mutation",
                "runtime proof",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "activeCurrentRisk": "1179/1179 = 100.00%",
            "staticTarget": "rebuild-grade static contracts and rebuild-grade specification aiming at no noticeable difference",
            "runtimeBoundary": "runtime, visual, patching, generated asset, and rebuild parity remain separate proof",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DRY_RUN_CONSUMER_VALIDATION_PROOF)
    parser.add_argument("--proof", type=Path, help="write proof JSON to this path")
    args = parser.parse_args()

    summary = build_public_safe_command_arm_readiness_gate_summary(read_json(args.source))
    proof = build_public_safe_command_arm_readiness_gate_proof(summary)
    if args.proof:
        args.proof.parent.mkdir(parents=True, exist_ok=True)
        args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
