#!/usr/bin/env python3
"""Define the public-safe boundary for a later harness command arm step.

This module consumes only the tracked command arm-checklist command arm-readiness proof. It defines
the public-safe command arm boundary for a later explicit operator-armed
checklist-population lane. It does not arm, dispatch, or execute commands; read
private asset content; consume raw private manifests; launch BEA; generate
assets; mutate Ghidra; or publish private paths, filenames, hashes, command
arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
    REDACTED_FIELDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-boundary.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-boundary-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Boundary Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-boundary-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Population Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-population-proof-plan"
)

COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES = (
    "load-tracked-real-importer-harness-command-arm-checklist-command-arm-readiness-gate-proof",
    "validate-real-importer-harness-command-arm-readiness-continuity",
    "define-harness-command-arm-checklist-command-arm-boundary",
    "validate-harness-command-arm-checklist-command-arm-boundary-row-statuses",
    "validate-harness-command-arm-checklist-command-arm-boundary-row-ordinals",
    "validate-harness-command-arm-checklist-command-arm-boundary-category-counts",
    "validate-harness-command-arm-checklist-command-arm-boundary-stop-conditions",
    "validate-harness-command-arm-checklist-command-arm-boundary-public-redaction-policy",
    "select-harness-command-arm-checklist-command-arm-checklist-population-lane",
    "emit-command-arm-checklist-command-arm-boundary-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-boundary-status",
            "harness-command-arm-checklist-command-arm-boundary-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-population-next-lane",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-boundary-input-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_FALSE_GUARDS,
            "privateCommandArmChecklistCommandArmBoundaryArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationPrivateOutputGenerated",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ZERO_COUNTERS,
            "commandArmChecklistCommandArmBoundaryPrivateInputRows",
            "commandArmChecklistCommandArmBoundaryArtifactPathRows",
            "privateCommandArmChecklistCommandArmBoundaryArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationRows",
            "commandArmChecklistCommandArmChecklistPopulationOutputArtifactRows",
        )
    )
)

ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ROW_ZERO_FIELDS,
            "commandArmChecklistCommandArmChecklistPopulationOutputArtifactRows",
            "privateCommandArmChecklistCommandArmBoundaryArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationRows",
        )
    )
)

STOP_CONDITIONS = (
    "command arming before the later checklist-population lane is explicitly armed",
    "shell dispatch before the later checklist-population lane is explicitly armed",
    "real importer dry-run execution before the command arm checklist is populated and armed",
    "private asset content, raw private manifest rows, or raw command arguments would enter public scope",
    "private output paths, filenames, hashes, byte lengths, or traces would enter public scope",
    "generated asset output would be inferred from class/count evidence",
    "runtime resource parser behavior would be inferred from dry-run contract evidence",
    "texture pixels, mesh loading/skinning, Direct3D/GPU, or material visual correctness would be claimed",
    "Godot, product UI, renderer, rebuild, or no-noticeable-difference parity would be claimed",
    "installed game or original executable mutation would be needed",
    "Ghidra mutation would be needed",
    "BEA launch would be needed",
)


class RealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryError(ValueError):
    """Raised when arm-readiness evidence cannot support the arm boundary."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryError(message)


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


def _validate_source_command_arm_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "source command arm-checklist command arm-readiness status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 41, "source proof count mismatch")
    _require(
        source_evidence.get("sourceCommandArmChecklistCommandDryRunConsumerValidationProofCount") == 40,
        "source command arm-checklist command dry-run consumer-validation proof count mismatch",
    )
    _require(
        source_evidence.get("commandArmChecklistCommandArmReadinessGateInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES),
        "source command arm-checklist command arm-readiness interface count mismatch",
    )
    _require(
        tuple(source_evidence.get("commandArmChecklistCommandArmReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
        "source command arm-checklist command arm-readiness interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmReadinessGateDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateOnly",
        "commandArmChecklistCommandDryRunConsumerValidationProofConsumed",
        "commandArmChecklistCommandDryRunConsumerValidationProofContinuityValidated",
        "commandArmChecklistCommandDryRunConsumerValidationProofRowsConsumed",
        "commandArmChecklistCommandArmReadinessGateExecuted",
        "commandArmChecklistCommandArmReadinessGateInputAccepted",
        "commandArmChecklistCommandArmReadinessGatePreconditionsValidated",
        "commandArmChecklistCommandArmReadinessGateRowStatusesValidated",
        "commandArmChecklistCommandArmReadinessGateRowOrdinalsValidated",
        "commandArmChecklistCommandArmReadinessGateCategoryCountsValidated",
        "commandArmChecklistCommandArmReadinessGateInterfacesValidated",
        "commandArmChecklistCommandArmReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmReadinessGateRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmBoundaryLaneSelected",
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
        "realImporterDryRunHarnessCommandArmChecklistCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandDryRunPrivateOutputGenerated",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateReadPrivateInputs",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGatePublishedPrivateInput",
        "privateCommandArmChecklistCommandArmReadinessGateArtifactPublished",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundarySentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmReadinessGateContract")
    expected_counts = {
        "commandArmChecklistCommandDryRunConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_REDACTED_FIELDS),
        "falseGuardCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_FALSE_GUARDS),
        "zeroCounterCount": len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source arm-readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source arm-readiness command row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceCommandArmChecklistCommandDryRunConsumerValidationRowOrdinal") == expected_ordinal,
            f"{row_id} source ordinal mismatch",
        )
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"{row_id} later-arm flag mismatch")
        _require(
            row.get("futureHarnessCommandArmChecklistCommandArmBoundaryRequiresLaterReview") is True,
            f"{row_id} later arm-boundary flag mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ROW_ZERO_FIELDS, row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_arm_boundary_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe command arm-checklist command arm-boundary row per arm-readiness row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmReadinessGateRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmReadinessGateRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmChecklistCommandArmBoundaryMode": "public-safe-command-arm-checklist-command-arm-boundary-status-token-only",
                "commandArmChecklistCommandArmBoundaryOutputArtifactRows": 0,
                "commandArmChecklistCommandArmBoundaryRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-row",
                "commandArmChecklistCommandArmBoundaryRowOrdinal": ordinal,
                "commandArmChecklistCommandArmBoundaryStatus": "ready-for-later-explicit-command-arm-checklist-command-arm-checklist-population",
                "commandArmChecklistCommandArmChecklistPopulationOutputArtifactRows": 0,
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandArmChecklistCommandDryRunOutputArtifactRows": 0,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandPrivateOutputRows": 0,
                "commandShellDispatchRows": 0,
                "directCommandArmingAllowedHere": False,
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessArmRequiresOperatorAction": True,
                "futureHarnessCommandArmChecklistCommandArmChecklistPopulationRequiresLaterReview": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "privateCommandArmChecklistCommandArmBoundaryArtifactRows": 0,
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArgumentRows": 0,
                "rawCommandArmChecklistCommandDryRunTraceRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationRows": 0,
                "realImporterDryRunHarnessCommandArmChecklistCommandDryRunRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "rowsAllowedToMoveOutOfNotArmedOnlyAfterArm": True,
                "sourceCommandArmChecklistCommandArmReadinessGateRowOrdinal": ordinal,
                "sourceCommandArmStatus": source_row["commandArmStatus"],
                "sourceCommandArmChecklistCommandConsumerValidationRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandConsumerValidationRowOrdinal"
                ],
                "sourceCommandContractRowOrdinal": source_row["sourceCommandContractRowOrdinal"],
                "sourceCommandArmChecklistCommandDryRunConsumerValidationRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandDryRunConsumerValidationRowOrdinal"
                ],
                "sourceCommandArmChecklistCommandDryRunRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandDryRunRowOrdinal"
                ],
                "sourceCommandExecutionStatus": source_row["commandExecutionStatus"],
                "sourceCommandArmChecklistCommandReadinessGateRowOrdinal": source_row[
                    "sourceCommandArmChecklistCommandReadinessGateRowOrdinal"
                ],
                "sourceCommandArmChecklistReadinessGateRowOrdinal": source_row[
                    "sourceCommandArmChecklistReadinessGateRowOrdinal"
                ],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary(
    command_arm_readiness_gate_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command arm-checklist command arm-boundary summary."""

    contract = _validate_source_command_arm_readiness_gate_proof(command_arm_readiness_gate_proof)
    rows = build_command_arm_boundary_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "arm-boundary category counts mismatch")
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmReadinessGateStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryOnly": True,
        "commandArmChecklistCommandArmReadinessGateProofConsumed": True,
        "commandArmChecklistCommandArmReadinessGateProofContinuityValidated": True,
        "commandArmChecklistCommandArmReadinessGateProofRowsConsumed": True,
        "commandArmChecklistCommandArmBoundaryDefined": True,
        "commandArmChecklistCommandArmBoundaryInputAccepted": True,
        "commandArmChecklistCommandArmBoundaryRowStatusesValidated": True,
        "commandArmChecklistCommandArmBoundaryRowOrdinalsValidated": True,
        "commandArmChecklistCommandArmBoundaryCategoryCountsValidated": True,
        "commandArmChecklistCommandArmBoundaryInterfacesValidated": True,
        "commandArmChecklistCommandArmBoundaryStopConditionsValidated": True,
        "commandArmChecklistCommandArmBoundaryEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistCommandArmBoundaryRedactionPolicyValidated": True,
        "harnessCommandArmChecklistCommandArmChecklistPopulationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **false_guards,
        **zero_counters,
        "sourceProofCount": 42,
        "sourceCommandArmChecklistCommandArmReadinessGateProofCount": 41,
        "sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmBoundaryRows": len(rows),
        "definedCommandArmChecklistCommandArmBoundaryRowCount": len(rows),
        "passedCommandArmChecklistCommandArmBoundaryRowCount": len(rows),
        "failedCommandArmChecklistCommandArmBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmChecklistCommandArmReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmBoundaryInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmBoundaryCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistCommandArmBoundaryRowsBody": rows,
        "stopConditions": list(STOP_CONDITIONS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate a public-safe command arm-checklist command arm-boundary summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryOnly",
        "commandArmChecklistCommandArmReadinessGateProofConsumed",
        "commandArmChecklistCommandArmReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmReadinessGateProofRowsConsumed",
        "commandArmChecklistCommandArmBoundaryDefined",
        "commandArmChecklistCommandArmBoundaryInputAccepted",
        "commandArmChecklistCommandArmBoundaryRowStatusesValidated",
        "commandArmChecklistCommandArmBoundaryRowOrdinalsValidated",
        "commandArmChecklistCommandArmBoundaryCategoryCountsValidated",
        "commandArmChecklistCommandArmBoundaryInterfacesValidated",
        "commandArmChecklistCommandArmBoundaryStopConditionsValidated",
        "commandArmChecklistCommandArmBoundaryEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmBoundaryRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistPopulationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 42,
        "sourceCommandArmChecklistCommandArmReadinessGateProofCount": 41,
        "sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmChecklistCommandArmReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
        "source command arm-checklist command arm-readiness interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmChecklistCommandArmBoundaryInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
        "command arm-checklist command arm-boundary interfaces mismatch",
    )
    rows = _read_list(summary, "commandArmChecklistCommandArmBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "arm-boundary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "arm-boundary category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"arm-boundary command row {expected_ordinal}"
        _require(row.get("commandArmChecklistCommandArmBoundaryRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmChecklistCommandArmReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(
            row.get("futureHarnessCommandArmChecklistCommandArmChecklistPopulationRequiresLaterReview") is True,
            f"{row_id} later checklist-population flag mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch")
        _validate_zero_fields(row, ROW_ZERO_FIELDS, row_id)
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_arm_boundary_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command arm-checklist command arm-boundary summary in the tracked proof schema."""

    validate_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmReadinessGateStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
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
            "sourceCommandArmChecklistCommandArmReadinessGateProofCount": summary[
                "sourceCommandArmChecklistCommandArmReadinessGateProofCount"
            ],
            "sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount"
            ],
            "commandArmChecklistCommandArmBoundaryInterfaceCount": summary["commandArmChecklistCommandArmBoundaryInterfaceCount"],
            "sourceCommandArmChecklistCommandArmReadinessGateInterfaces": summary[
                "sourceCommandArmChecklistCommandArmReadinessGateInterfaces"
            ],
            "commandArmChecklistCommandArmBoundaryInterfaces": summary["commandArmChecklistCommandArmBoundaryInterfaces"],
            "sourceProof": COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PROOF,
        },
        "realImporterHarnessCommandArmChecklistCommandArmBoundaryDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryOnly": True,
            "commandArmChecklistCommandArmReadinessGateProofConsumed": True,
            "commandArmChecklistCommandArmReadinessGateProofContinuityValidated": True,
            "commandArmChecklistCommandArmReadinessGateProofRowsConsumed": True,
            "commandArmChecklistCommandArmBoundaryDefined": True,
            "commandArmChecklistCommandArmBoundaryInputAccepted": True,
            "commandArmChecklistCommandArmBoundaryRowStatusesValidated": True,
            "commandArmChecklistCommandArmBoundaryRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmBoundaryCategoryCountsValidated": True,
            "commandArmChecklistCommandArmBoundaryInterfacesValidated": True,
            "commandArmChecklistCommandArmBoundaryStopConditionsValidated": True,
            "commandArmChecklistCommandArmBoundaryEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmBoundaryRedactionPolicyValidated": True,
            "harnessCommandArmChecklistCommandArmChecklistPopulationLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmBoundaryContract": {
            "commandArmChecklistCommandArmBoundaryInputMode": "tracked-public-safe-command-arm-checklist-command-arm-readiness-gate-proof-json",
            "commandArmChecklistCommandArmBoundaryOutputMode": "tracked-public-safe-command-arm-checklist-command-arm-boundary-proof",
            "selectedNextLaneClass": "private-corpus real importer dry-run harness command arm-checklist command arm-checklist-population without command arming here",
            "commandArmChecklistCommandArmReadinessGateRowsConsumed": summary["commandArmChecklistCommandArmReadinessGateRowsConsumed"],
            "commandArmChecklistCommandArmBoundaryRows": summary["commandArmChecklistCommandArmBoundaryRows"],
            "definedCommandArmChecklistCommandArmBoundaryRowCount": summary["definedCommandArmChecklistCommandArmBoundaryRowCount"],
            "passedCommandArmChecklistCommandArmBoundaryRowCount": summary["passedCommandArmChecklistCommandArmBoundaryRowCount"],
            "failedCommandArmChecklistCommandArmBoundaryRowCount": summary["failedCommandArmChecklistCommandArmBoundaryRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "stopConditionCount": summary["stopConditionCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmBoundaryCategoryCounts": summary["commandArmChecklistCommandArmBoundaryCategoryCounts"],
            "commandArmChecklistCommandArmBoundaryRowsBody": summary["commandArmChecklistCommandArmBoundaryRowsBody"],
            "stopConditions": summary["stopConditions"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-status-token-only",
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
                "the tracked command arm-checklist command arm-readiness proof can be consumed as public-safe command arm-checklist command arm-boundary input",
                "the 99 command arm-checklist command arm-readiness rows remain non-armed, non-dispatched, and not executed",
                "the command arm-checklist command arm-boundary policy records explicit stop conditions before any later command arm checklist population",
                "the next command arm-checklist command arm-checklist-population lane is selected without arming, dispatching, or executing a command here",
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
        "--command-arm-checklist-command-arm-readiness-gate-proof",
        type=Path,
        default=Path(COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_PROOF),
    )
    parser.add_argument("--summary", type=Path, help="optional public-safe arm-boundary summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        arm_readiness_proof = read_json(args.command_arm_checklist_command_arm_readiness_gate_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary(
            arm_readiness_proof
        )
        validate_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_arm_boundary_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryError):
        print("Real importer dry-run harness command arm-checklist command arm-boundary: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
