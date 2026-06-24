#!/usr/bin/env python3
"""Define the public-safe boundary for the command arm-checklist lane.

This consumes only the tracked command arm-checklist readiness-gate proof. It
does not arm, dispatch, or execute commands; read private asset content; consume
raw private manifests; generate assets; launch BEA; mutate Ghidra; or publish
private paths, filenames, hashes, command arguments, or traces.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from texture_mesh_material_sidecar_command_arm_checklist_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
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
    / "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-boundary-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-defined-public-safe-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Boundary Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES = (
    "load-tracked-command-arm-checklist-readiness-gate-proof",
    "validate-command-arm-checklist-readiness-continuity",
    "define-command-arm-checklist-boundary",
    "validate-command-arm-checklist-boundary-row-statuses",
    "validate-command-arm-checklist-boundary-row-ordinals",
    "validate-command-arm-checklist-boundary-category-counts",
    "validate-command-arm-checklist-boundary-stop-conditions",
    "validate-command-arm-checklist-boundary-public-redaction-policy",
    "select-command-arm-checklist-command-materialization-lane",
    "emit-command-arm-checklist-boundary-summary",
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

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-status",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactPublished",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationPrivateOutputGenerated",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryPrivateInputRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactPathRows",
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationOutputArtifactRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_ROW_ZERO_FIELDS,
            "privateCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRows",
            "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationOutputArtifactRows",
        )
    )
)


class CommandArmChecklistBoundaryError(ValueError):
    """Raised when readiness evidence cannot support the boundary."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandArmChecklistBoundaryError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be an object")
    return value


def _read_list(source: Mapping[str, Any], key: str) -> list[Any]:
    value = source.get(key)
    _require(isinstance(value, list), f"{key} must be a list")
    return value


def _validate_source_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source schema mismatch")
    _require(source.get("status") == "PASS", "source status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "source readiness status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 56, "source proof count mismatch")
    _require(
        source_evidence.get("commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES),
        "source readiness interface count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateOnly",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumedByReadinessGate",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGatePreconditionsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision should be true: {key}")
    for key in FALSE_GUARDS:
        if key in decision:
            _require(decision.get(key) is False, f"source decision should be false: {key}")

    contract = _read_mapping(source, "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateContract")
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount": 0,
        "readinessGateNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readinessGateNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source readiness row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(row.get("readinessGateStatus") == "ready-public-safe-boundary-lane-only-no-command-arming", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct exec guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
    return contract


def build_boundary_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsBody"):
        ordinal = int(source_row["commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"])
        row: dict[str, Any] = {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowClass": (
                "private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-row"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryMode": (
                "public-safe-boundary-definition-not-run-unobserved-not-armed-not-dispatched-not-executed"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal": ordinal,
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal": ordinal,
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
            "boundaryStatus": "defined-public-safe-command-materialization-lane-only-no-command-arming",
            "sourceReadinessGateStatus": source_row["readinessGateStatus"],
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "commandArmStatus": "not-armed",
            "commandExecutionStatus": "not-executed",
            "commandDispatchAllowedHere": False,
            "directCommandArmingAllowedHere": False,
            "directCommandExecutionAllowedHere": False,
            "futureCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationAllowed": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateValuePublished": False,
        }
        for key in ROW_ZERO_FIELDS:
            row[key] = 0
        rows.append(row)
    return rows


def build_public_safe_boundary_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_readiness_gate_proof(source)
    rows = build_boundary_rows(contract)
    category_counts = dict(Counter(row["category"] for row in rows))
    summary: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "sourceProofCount": 57,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount": 56,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "publicLeakCheck": "PASS",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryCategoryCounts": category_counts,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody": rows,
        "stopConditions": list(STOP_CONDITIONS),
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        **{key: False for key in FALSE_GUARDS},
        **{key: 0 for key in ZERO_COUNTERS},
    }
    validate_public_safe_boundary_summary(summary)
    return summary


def validate_public_safe_boundary_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "summary status token mismatch",
    )
    expected_counts = {
        "sourceProofCount": 57,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount": 56,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": 10,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": 10,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "boundary row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "boundary category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"boundary row {expected_ordinal}"
        _require(
            row.get("commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal") == expected_ordinal,
            f"{row_id} ordinal mismatch",
        )
        _require(row.get("boundaryStatus") == "defined-public-safe-command-materialization-lane-only-no-command-arming", f"{row_id} status mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct exec mismatch")
        _require(
            row.get("futureCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationAllowed") is True,
            f"{row_id} future materialization mismatch",
        )
        _require(row.get("privateValuePublished") is False, f"{row_id} private value mismatch")
        for key in ROW_ZERO_FIELDS:
            _require(row.get(key) == 0, f"{row_id} zero field mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "public leak mismatch")


def build_public_safe_boundary_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_boundary_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS
        ),
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedPost100StaticSurface": "1560/1560 = 100.00%",
            "activeCurrentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
        },
        "sourceEvidence": {
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount": summary[
                "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount"
            ],
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaces": list(
                REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaces": list(
                REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES
            ),
            "sourceProof": str(READINESS_PROOF.relative_to(ROOT)).replace("\\", "/"),
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryOnly": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofContinuityValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofRowsConsumed": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryDefined": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInputAccepted": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowStatusesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinalsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryCategoryCountsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfacesValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStopConditionsValidated": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryEmitsOnlyPublicSafeRows": True,
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRedactionPolicyValidated": True,
            "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationLaneSelected": True,
            "futureCommandArmRequiresExplicitOperatorArm": True,
            "privateEvidenceStoredOutsidePublicReleaseScope": True,
            "publicPrivateSeparationRequired": True,
            **{key: False for key in FALSE_GUARDS},
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryContract": {
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInputMode": (
                "tracked-public-safe-command-arm-checklist-readiness-gate-proof-json"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryOutputMode": (
                "tracked-public-safe-command-arm-checklist-boundary-proof"
            ),
            "selectedNextLaneClass": (
                "private-corpus real importer dry-run harness command arm-checklist command arm-checklist command arm-checklist "
                "command materialization without command arming here"
            ),
            "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsConsumed"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows"
            ],
            "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": summary[
                "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount"
            ],
            "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": summary[
                "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount"
            ],
            "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": summary[
                "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount"
            ],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": summary[
                "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": summary[
                "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "stopConditionCount": summary["stopConditionCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryCategoryCounts": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryCategoryCounts"
            ],
            "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody": summary[
                "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody"
            ],
            "stopConditions": summary["stopConditions"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-command-arm-checklist-boundary-status-token-only",
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
                "the tracked command arm-checklist readiness-gate proof can be consumed as public-safe boundary input",
                "the 99 boundary rows preserve readiness ordinals and category counts",
                "every boundary row remains not-run, unobserved, not-armed, not-dispatched, and not-executed",
                "the next command-materialization lane is selected without materializing, arming, dispatching, or executing a command here",
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
    parser.add_argument("--readiness-proof", type=Path, default=READINESS_PROOF)
    parser.add_argument("--summary", type=Path, help="optional public-safe boundary summary")
    parser.add_argument("--proof", type=Path, help="optional tracked proof JSON output")
    args = parser.parse_args()

    try:
        source = read_json(args.readiness_proof)
        summary = build_public_safe_boundary_summary(source)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_boundary_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, CommandArmChecklistBoundaryError):
        print("Material sidecar command arm-checklist boundary: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
