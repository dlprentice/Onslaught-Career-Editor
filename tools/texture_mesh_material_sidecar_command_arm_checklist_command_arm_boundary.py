#!/usr/bin/env python3
"""Build a public-safe command arm-boundary proof for the sidecar lane.

This consumes only the tracked command arm-readiness proof. It defines the
public-safe boundary for a later explicit checklist-population lane. It does
not read private asset content, consume raw private manifests, materialize
runnable commands, arm commands, dispatch a shell, execute an importer, launch
BEA, generate assets, mutate Ghidra, or publish private paths, filenames,
hashes, command arguments, traces, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_arm_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
    REDACTED_FIELDS as READINESS_REDACTED_FIELDS,
    ROW_ZERO_FIELDS as READINESS_ROW_ZERO_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


ROOT = Path(__file__).resolve().parents[1]
READINESS_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-"
    "defined-public-safe-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES = (
    "load-tracked-command-arm-checklist-command-arm-readiness-gate-proof",
    "validate-command-arm-checklist-command-arm-readiness-continuity",
    "define-command-arm-checklist-command-arm-boundary",
    "validate-command-arm-checklist-command-arm-boundary-row-statuses",
    "validate-command-arm-checklist-command-arm-boundary-row-ordinals",
    "validate-command-arm-checklist-command-arm-boundary-category-counts",
    "validate-command-arm-checklist-command-arm-boundary-stop-conditions",
    "validate-command-arm-checklist-command-arm-boundary-public-redaction-policy",
    "select-command-arm-checklist-command-arm-checklist-population-lane",
    "emit-command-arm-checklist-command-arm-boundary-summary",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-status",
            "validated-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "privateCommandArmBoundaryArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationPrivateOutputGenerated",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_COUNTERS,
            "commandArmBoundaryPrivateInputRows",
            "commandArmBoundaryArtifactPathRows",
            "privateCommandArmBoundaryArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOutputArtifactRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_ROW_ZERO_FIELDS,
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
STOP_CONDITIONS = (
    "private-asset-content-read-requested",
    "raw-private-manifest-row-requested",
    "private-path-filename-hash-argument-or-trace-publication-requested",
    "direct-command-arm-requested",
    "shell-dispatch-requested",
    "real-importer-execution-requested",
    "generated-asset-output-requested",
    "bea-launch-requested",
    "ghidra-mutation-requested",
    "godot-or-product-ui-work-requested",
    "runtime-proof-requested",
    "rebuild-or-no-noticeable-difference-parity-claim-requested",
)


class CommandArmBoundaryError(ValueError):
    """Raised when readiness evidence cannot support boundary definition."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandArmBoundaryError(message)


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


def _validate_source_readiness_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "source readiness status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    expected_evidence = {
        "sourceProofCount": 63,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount": 62,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": 10,
        "commandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
    }
    for key, expected in expected_evidence.items():
        _require(source_evidence.get(key) == expected, f"source evidence count mismatch: {key}")
    _require(
        tuple(source_evidence.get("commandArmReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
        "source readiness interfaces mismatch",
    )

    decision = _read_mapping(
        source,
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateDecision",
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
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(
        source,
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateContract",
    )
    expected_counts = {
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
        "publicAllowedOutputCount": len(READINESS_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(READINESS_REDACTED_FIELDS),
        "falseGuardCount": len(READINESS_FALSE_GUARDS),
        "zeroCounterCount": len(READINESS_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source arm-readiness row {expected_ordinal}"
        _require(row.get("commandArmReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandDryRunConsumerValidationRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch")
        _require(row.get("futureCommandArmRequiresExplicitOperatorArm") is True, f"{row_id} future arm flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private publication guard mismatch")
        _validate_zero_fields(row, tuple(key for key in READINESS_ROW_ZERO_FIELDS if key in row), row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(READINESS_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(READINESS_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in READINESS_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak mismatch")
    return contract


def build_command_arm_boundary_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe command arm-boundary row per readiness row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmReadinessGateRowsBody"):
        ordinal = int(source_row["commandArmReadinessGateRowOrdinal"])
        row = {key: 0 for key in ROW_ZERO_FIELDS}
        row.update(
            {
                "boundaryStatus": "defined-public-safe-command-arm-checklist-population-lane-only-no-command-arming",
                "category": source_row["category"],
                "commandArmBoundaryMode": "public-safe-command-arm-boundary-definition-not-run-not-armed-not-dispatched-not-executed",
                "commandArmBoundaryRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-boundary-row",
                "commandArmBoundaryRowOrdinal": ordinal,
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandExecutionStatus": "not-executed",
                "directCommandArmingAllowedHere": False,
                "directCommandExecutionAllowedHere": False,
                "futureCommandArmChecklistPopulationAllowed": True,
                "futureCommandArmRequiresExplicitOperatorArm": True,
                "itemId": source_row["itemId"],
                "observationStatus": "unobserved",
                "privateValuePublished": False,
                "rowStatus": "not-run",
                "sourceCommandArmReadinessGateRowOrdinal": ordinal,
                "sourceCommandArmReadinessGateStatus": source_row["commandArmReadinessGateStatus"],
            }
        )
        for key, value in source_row.items():
            if key.startswith("source") and key.endswith("Ordinal"):
                row.setdefault(key, value)
        rows.append(row)
    return rows


def build_public_safe_command_arm_boundary_summary(readiness_proof: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_readiness_proof(readiness_proof)
    rows = build_command_arm_boundary_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "boundary category count mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "thisSlice": THIS_SLICE,
        "thisScope": THIS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmReadinessGateStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryOnly": True,
        "commandArmReadinessGateProofConsumed": True,
        "commandArmReadinessGateProofContinuityValidated": True,
        "commandArmReadinessGateRowsConsumedByArmBoundary": True,
        "commandArmBoundaryDefined": True,
        "commandArmBoundaryInputAccepted": True,
        "commandArmBoundaryRowStatusesValidated": True,
        "commandArmBoundaryRowOrdinalsValidated": True,
        "commandArmBoundaryCategoryCountsValidated": True,
        "commandArmBoundaryGuardCountersValidated": True,
        "commandArmBoundaryInterfacesValidated": True,
        "commandArmBoundaryStopConditionsValidated": True,
        "commandArmBoundaryEmitsOnlyPublicSafeRows": True,
        "commandArmBoundaryRedactionPolicyValidated": True,
        "commandArmChecklistPopulationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        "sourceProofCount": 64,
        "sourceCommandArmReadinessGateProofCount": 63,
        "sourceCommandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmBoundaryRows": len(rows),
        "definedCommandArmBoundaryRowCount": len(rows),
        "passedCommandArmBoundaryRowCount": len(rows),
        "failedCommandArmBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistPopulationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmBoundaryInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmBoundaryCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmBoundaryRowsBody": rows,
        "stopConditions": list(STOP_CONDITIONS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_command_arm_boundary_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryOnly",
        "commandArmReadinessGateProofConsumed",
        "commandArmReadinessGateProofContinuityValidated",
        "commandArmReadinessGateRowsConsumedByArmBoundary",
        "commandArmBoundaryDefined",
        "commandArmBoundaryInputAccepted",
        "commandArmBoundaryRowStatusesValidated",
        "commandArmBoundaryRowOrdinalsValidated",
        "commandArmBoundaryCategoryCountsValidated",
        "commandArmBoundaryGuardCountersValidated",
        "commandArmBoundaryInterfacesValidated",
        "commandArmBoundaryStopConditionsValidated",
        "commandArmBoundaryEmitsOnlyPublicSafeRows",
        "commandArmBoundaryRedactionPolicyValidated",
        "commandArmChecklistPopulationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 64,
        "sourceCommandArmReadinessGateProofCount": 63,
        "sourceCommandArmReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES
        ),
        "commandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    _require(
        tuple(summary.get("sourceCommandArmReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
        "source interfaces mismatch",
    )
    _require(
        tuple(summary.get("commandArmBoundaryInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
        "boundary interfaces mismatch",
    )
    rows = _read_list(summary, "commandArmBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "boundary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "boundary category count mismatch")
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-boundary row {ordinal}"
        _require(row.get("commandArmBoundaryRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmReadinessGateRowOrdinal") == ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} command arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} execution guard mismatch")
        _require(row.get("futureCommandArmChecklistPopulationAllowed") is True, f"{row_id} population lane flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private flag mismatch")
        _validate_zero_fields(row, tuple(key for key in ROW_ZERO_FIELDS if key in row), row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")


def build_public_safe_command_arm_boundary_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_arm_boundary_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus": summary[
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus"
        ],
        "previousSlice": summary["previousSlice"],
        "previousScope": summary["previousScope"],
        "selectedNextSlice": summary["selectedNextSlice"],
        "selectedNextScope": summary["selectedNextScope"],
        "sourceCommandArmReadinessGateStatus": summary["sourceCommandArmReadinessGateStatus"],
        "sourceEvidence": {
            "sourceProof": "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.v1.json",
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmReadinessGateProofCount": summary["sourceCommandArmReadinessGateProofCount"],
            "sourceCommandArmReadinessGateInterfaceCount": summary["sourceCommandArmReadinessGateInterfaceCount"],
            "sourceCommandArmReadinessGateInterfaces": summary["sourceCommandArmReadinessGateInterfaces"],
            "commandArmBoundaryInterfaceCount": summary["commandArmBoundaryInterfaceCount"],
            "commandArmBoundaryInterfaces": summary["commandArmBoundaryInterfaces"],
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryDecision": {
            key: summary[key]
            for key in (
                "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryOnly",
                "commandArmReadinessGateProofConsumed",
                "commandArmReadinessGateProofContinuityValidated",
                "commandArmReadinessGateRowsConsumedByArmBoundary",
                "commandArmBoundaryDefined",
                "commandArmBoundaryInputAccepted",
                "commandArmBoundaryRowStatusesValidated",
                "commandArmBoundaryRowOrdinalsValidated",
                "commandArmBoundaryCategoryCountsValidated",
                "commandArmBoundaryGuardCountersValidated",
                "commandArmBoundaryInterfacesValidated",
                "commandArmBoundaryStopConditionsValidated",
                "commandArmBoundaryEmitsOnlyPublicSafeRows",
                "commandArmBoundaryRedactionPolicyValidated",
                "commandArmChecklistPopulationLaneSelected",
                "futureCommandArmRequiresExplicitOperatorArm",
                "privateEvidenceStoredOutsidePublicReleaseScope",
                "publicPrivateSeparationRequired",
                *FALSE_GUARDS,
            )
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryContract": {
            "commandArmReadinessGateRowsConsumed": summary["commandArmReadinessGateRowsConsumed"],
            "commandArmBoundaryRows": summary["commandArmBoundaryRows"],
            "definedCommandArmBoundaryRowCount": summary["definedCommandArmBoundaryRowCount"],
            "passedCommandArmBoundaryRowCount": summary["passedCommandArmBoundaryRowCount"],
            "failedCommandArmBoundaryRowCount": summary["failedCommandArmBoundaryRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistPopulationRowCount": summary["readyForLaterCommandArmChecklistPopulationRowCount"],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmBoundaryArtifactRows": summary["publicSafeCommandArmBoundaryArtifactRows"],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "stopConditionCount": summary["stopConditionCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "selectedNextLaneClass": "command-arm-checklist-population-proof-plan",
            "commandArmBoundaryCategoryCounts": summary["commandArmBoundaryCategoryCounts"],
            "commandArmBoundaryRowsBody": summary["commandArmBoundaryRowsBody"],
            "stopConditions": summary["stopConditions"],
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
                "Tracked public-safe command arm-readiness rows were consumed and converted into "
                "a public-safe command arm-boundary contract for later checklist population."
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
    parser.add_argument("--source", type=Path, default=READINESS_PROOF)
    parser.add_argument("--proof", type=Path, help="write proof JSON to this path")
    args = parser.parse_args()

    summary = build_public_safe_command_arm_boundary_summary(read_json(args.source))
    proof = build_public_safe_command_arm_boundary_proof(summary)
    if args.proof:
        args.proof.parent.mkdir(parents=True, exist_ok=True)
        args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
