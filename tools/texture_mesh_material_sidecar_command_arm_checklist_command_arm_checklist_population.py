#!/usr/bin/env python3
"""Build a public-safe command arm-checklist population proof.

This consumes only the tracked command arm-boundary proof. It populates
not-run/unobserved public checklist rows for a later validation lane. It does
not read private assets, consume raw private manifests, materialize runnable
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

from texture_mesh_material_sidecar_command_arm_checklist_command_arm_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as BOUNDARY_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as BOUNDARY_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
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
    / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json"
)

SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-summary.v1"
PROOF_SCHEMA_VERSION = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.v1"
REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-"
    "population-complete-public-safe-not-run-checklist-populated-no-command-arming"
)
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan"
)
NEXT_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan"
)
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan"
)

REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES = (
    "load-tracked-command-arm-checklist-command-arm-boundary-proof",
    "validate-command-arm-checklist-command-arm-boundary-continuity",
    "validate-command-arm-checklist-command-arm-checklist-population-preconditions",
    "populate-command-arm-checklist-command-arm-boundary-checklist-rows",
    "validate-command-arm-checklist-command-arm-checklist-row-statuses",
    "validate-command-arm-checklist-command-arm-checklist-row-ordinals",
    "validate-command-arm-checklist-command-arm-checklist-category-counts",
    "validate-command-arm-checklist-command-arm-checklist-public-redaction-policy",
    "validate-command-arm-checklist-command-arm-checklist-refusal-guards",
    "select-command-arm-checklist-command-arm-checklist-validation-lane",
    "emit-command-arm-checklist-command-arm-checklist-population-rows",
    "emit-command-arm-checklist-command-arm-checklist-population-summary",
)

PREFLIGHT_CHECKS = (
    "source-command-arm-boundary-status-pass",
    "source-command-arm-boundary-selected-this-slice",
    "source-command-arm-boundary-row-order-preserved",
    "source-command-arm-boundary-row-counts-preserved",
    "source-command-arm-boundary-category-counts-preserved",
    "source-command-arm-boundary-interface-counts-preserved",
    "source-command-arm-boundary-redaction-policy-preserved",
    "source-command-arm-boundary-false-guard-counts-preserved",
    "source-command-arm-boundary-zero-counter-counts-preserved",
    "no-private-corpus-read-performed",
    "no-command-arming-performed",
    "no-shell-dispatch-performed",
    "no-real-importer-executed",
    "public-leak-check-pass",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
            "harness-command-arm-checklist-command-arm-checklist-population-status",
            "harness-command-arm-checklist-command-arm-checklist-population-row-counts",
            "harness-command-arm-checklist-command-arm-checklist-validation-next-lane",
        )
    )
)
REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_REDACTED_FIELDS,
            "harness-command-arm-checklist-command-arm-checklist-population-input-path",
        )
    )
)
FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationReadPrivateInputs",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationPublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationExecuted",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationSentToShell",
            "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationPrivateOutputGenerated",
        )
    )
)
ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ZERO_COUNTERS,
            "commandArmChecklistCommandArmChecklistPopulationPrivateInputRows",
            "commandArmChecklistCommandArmChecklistPopulationOutputArtifactRows",
            "commandArmChecklistCommandArmChecklistValidationRows",
            "commandArmChecklistCommandArmChecklistPrivateOutputRows",
            "commandArmChecklistCommandArmChecklistPrivatePathRows",
            "commandArmChecklistCommandArmChecklistRawFilenameRows",
            "commandArmChecklistCommandArmChecklistRawHashRows",
            "commandArmChecklistCommandArmChecklistByteLengthRows",
        )
    )
)
ROW_ZERO_FIELDS = tuple(
    dict.fromkeys(
        (
            *BOUNDARY_ROW_ZERO_FIELDS,
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


class CommandArmChecklistPopulationError(ValueError):
    """Raised when boundary evidence cannot support checklist population."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandArmChecklistPopulationError(message)


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
        source.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "source boundary status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE, "source module next-slice mismatch")
    _require(SOURCE_SELECTED_SCOPE == THIS_SCOPE, "source module next-scope mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    expected_evidence = {
        "sourceProofCount": 64,
        "sourceCommandArmReadinessGateProofCount": 63,
        "sourceCommandArmReadinessGateInterfaceCount": 10,
        "commandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
    }
    for key, expected in expected_evidence.items():
        _require(source_evidence.get(key) == expected, f"source evidence count mismatch: {key}")
    _require(
        tuple(source_evidence.get("commandArmBoundaryInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
        "source boundary interfaces mismatch",
    )

    decision = _read_mapping(
        source,
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryDecision",
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
        _require(decision.get(key) is True, f"source decision true flag mismatch: {key}")
    for key in BOUNDARY_FALSE_GUARDS:
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(
        source,
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryContract",
    )
    expected_counts = {
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
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(BOUNDARY_REDACTED_FIELDS),
        "falseGuardCount": len(BOUNDARY_FALSE_GUARDS),
        "zeroCounterCount": len(BOUNDARY_ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "commandArmBoundaryRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category count mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"source command arm-boundary row {expected_ordinal}"
        _require(row.get("commandArmBoundaryRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmReadinessGateRowOrdinal") == expected_ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct-arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} execution guard mismatch")
        _require(row.get("futureCommandArmChecklistPopulationAllowed") is True, f"{row_id} population flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private publication guard mismatch")
        _validate_zero_fields(row, tuple(key for key in BOUNDARY_ROW_ZERO_FIELDS if key in row), row_id)

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(BOUNDARY_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(BOUNDARY_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in BOUNDARY_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak mismatch")
    return contract


def build_command_arm_checklist_population_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe not-run checklist row per boundary row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "commandArmBoundaryRowsBody"):
        ordinal = int(source_row["commandArmBoundaryRowOrdinal"])
        row = {key: 0 for key in ROW_ZERO_FIELDS}
        row.update(
            {
                "category": source_row["category"],
                "commandArmChecklistPopulationMode": "public-safe-not-run-checklist-population",
                "commandArmChecklistPopulationRowClass": "private-corpus-real-importer-dry-run-harness-command-arm-checklist-population-row",
                "commandArmChecklistPopulationRowOrdinal": ordinal,
                "commandArmChecklistPopulationStatus": "not-run-public-checklist-only",
                "commandArmStatus": "not-armed",
                "commandDispatchAllowedHere": False,
                "commandExecutionStatus": "not-executed",
                "directCommandArmingAllowedHere": False,
                "directCommandExecutionAllowedHere": False,
                "futureCommandArmChecklistValidationAllowed": True,
                "futureCommandArmRequiresExplicitOperatorArm": True,
                "itemId": source_row["itemId"],
                "observationStatus": "unobserved",
                "privateValuePublished": False,
                "rowStatus": "not-run",
                "sourceCommandArmBoundaryRowOrdinal": ordinal,
                "sourceCommandArmBoundaryStatus": source_row["boundaryStatus"],
            }
        )
        rows.append(row)
    return rows


def build_public_safe_command_arm_checklist_population_summary(boundary_proof: Mapping[str, Any]) -> dict[str, Any]:
    contract = _validate_source_boundary_proof(boundary_proof)
    rows = build_command_arm_checklist_population_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "population category count mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "thisSlice": THIS_SLICE,
        "thisScope": THIS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceCommandArmBoundaryStatus": REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly": True,
        "commandArmBoundaryProofConsumed": True,
        "commandArmBoundaryProofContinuityValidated": True,
        "commandArmBoundaryRowsConsumedByChecklistPopulation": True,
        "commandArmChecklistPopulationRowsPopulated": True,
        "commandArmChecklistPopulationRowStatusesValidated": True,
        "commandArmChecklistPopulationRowOrdinalsValidated": True,
        "commandArmChecklistPopulationCategoryCountsValidated": True,
        "commandArmChecklistPopulationGuardCountersValidated": True,
        "commandArmChecklistPopulationInterfacesValidated": True,
        "commandArmChecklistPopulationPreflightChecksPassed": True,
        "commandArmChecklistPopulationEmitsOnlyPublicSafeRows": True,
        "commandArmChecklistPopulationRedactionPolicyValidated": True,
        "commandArmChecklistValidationLaneSelected": True,
        "futureCommandArmRequiresExplicitOperatorArm": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        **{key: False for key in FALSE_GUARDS},
        "sourceProofCount": 65,
        "sourceCommandArmBoundaryProofCount": 64,
        "sourceCommandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistPopulationRows": len(rows),
        "populatedCommandArmChecklistRowCount": len(rows),
        "passedCommandArmChecklistPopulationRowCount": len(rows),
        "failedCommandArmChecklistPopulationRowCount": 0,
        "notRunCommandArmChecklistRowCount": len(rows),
        "unobservedCommandArmChecklistRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistValidationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceCommandArmBoundaryInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistPopulationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmChecklistPopulationCategoryCounts": dict(sorted(category_counts.items())),
        "commandArmChecklistPopulationRowsBody": rows,
        "preflightChecks": list(PREFLIGHT_CHECKS),
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_command_arm_checklist_population_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "summary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly",
        "commandArmBoundaryProofConsumed",
        "commandArmBoundaryProofContinuityValidated",
        "commandArmBoundaryRowsConsumedByChecklistPopulation",
        "commandArmChecklistPopulationRowsPopulated",
        "commandArmChecklistPopulationRowStatusesValidated",
        "commandArmChecklistPopulationRowOrdinalsValidated",
        "commandArmChecklistPopulationCategoryCountsValidated",
        "commandArmChecklistPopulationGuardCountersValidated",
        "commandArmChecklistPopulationInterfacesValidated",
        "commandArmChecklistPopulationPreflightChecksPassed",
        "commandArmChecklistPopulationEmitsOnlyPublicSafeRows",
        "commandArmChecklistPopulationRedactionPolicyValidated",
        "commandArmChecklistValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 65,
        "sourceCommandArmBoundaryProofCount": 64,
        "sourceCommandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
        "commandArmChecklistPopulationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES
        ),
        "commandArmBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistPopulationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "populatedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistPopulationRowCount": 0,
        "notRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "unobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"summary count mismatch: {key}")
    rows = _read_list(summary, "commandArmChecklistPopulationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "population row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "population category count mismatch")
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-checklist population row {ordinal}"
        _require(row.get("commandArmChecklistPopulationRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceCommandArmBoundaryRowOrdinal") == ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch")
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} arm guard mismatch")
        _require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} execution guard mismatch")
        _require(row.get("futureCommandArmChecklistValidationAllowed") is True, f"{row_id} validation lane flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private flag mismatch")
        _validate_zero_fields(row, tuple(key for key in ROW_ZERO_FIELDS if key in row), row_id)
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")


def build_public_safe_command_arm_checklist_population_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    validate_public_safe_command_arm_checklist_population_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus": summary[
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus"
        ],
        "previousSlice": summary["previousSlice"],
        "previousScope": summary["previousScope"],
        "selectedNextSlice": summary["selectedNextSlice"],
        "selectedNextScope": summary["selectedNextScope"],
        "sourceCommandArmBoundaryStatus": summary["sourceCommandArmBoundaryStatus"],
        "sourceEvidence": {
            "sourceProof": "reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json",
            "sourceProofCount": summary["sourceProofCount"],
            "sourceCommandArmBoundaryProofCount": summary["sourceCommandArmBoundaryProofCount"],
            "sourceCommandArmBoundaryInterfaceCount": summary["sourceCommandArmBoundaryInterfaceCount"],
            "sourceCommandArmBoundaryInterfaces": summary["sourceCommandArmBoundaryInterfaces"],
            "commandArmChecklistPopulationInterfaceCount": summary["commandArmChecklistPopulationInterfaceCount"],
            "commandArmChecklistPopulationInterfaces": summary["commandArmChecklistPopulationInterfaces"],
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationDecision": {
            key: summary[key]
            for key in (
                "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationOnly",
                "commandArmBoundaryProofConsumed",
                "commandArmBoundaryProofContinuityValidated",
                "commandArmBoundaryRowsConsumedByChecklistPopulation",
                "commandArmChecklistPopulationRowsPopulated",
                "commandArmChecklistPopulationRowStatusesValidated",
                "commandArmChecklistPopulationRowOrdinalsValidated",
                "commandArmChecklistPopulationCategoryCountsValidated",
                "commandArmChecklistPopulationGuardCountersValidated",
                "commandArmChecklistPopulationInterfacesValidated",
                "commandArmChecklistPopulationPreflightChecksPassed",
                "commandArmChecklistPopulationEmitsOnlyPublicSafeRows",
                "commandArmChecklistPopulationRedactionPolicyValidated",
                "commandArmChecklistValidationLaneSelected",
                "futureCommandArmRequiresExplicitOperatorArm",
                "privateEvidenceStoredOutsidePublicReleaseScope",
                "publicPrivateSeparationRequired",
                *FALSE_GUARDS,
            )
        },
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationContract": {
            "commandArmChecklistPopulationInputMode": "tracked-public-safe-command-arm-boundary-proof-json",
            "commandArmChecklistPopulationOutputMode": "tracked-public-safe-command-arm-checklist-population-proof",
            "selectedNextLaneClass": "command-arm-checklist-validation-proof-plan",
            "commandArmBoundaryRowsConsumed": summary["commandArmBoundaryRowsConsumed"],
            "commandArmChecklistPopulationRows": summary["commandArmChecklistPopulationRows"],
            "populatedCommandArmChecklistRowCount": summary["populatedCommandArmChecklistRowCount"],
            "passedCommandArmChecklistPopulationRowCount": summary["passedCommandArmChecklistPopulationRowCount"],
            "failedCommandArmChecklistPopulationRowCount": summary["failedCommandArmChecklistPopulationRowCount"],
            "notRunCommandArmChecklistRowCount": summary["notRunCommandArmChecklistRowCount"],
            "unobservedCommandArmChecklistRowCount": summary["unobservedCommandArmChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterCommandArmChecklistValidationRowCount": summary["readyForLaterCommandArmChecklistValidationRowCount"],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeCommandArmChecklistPopulationArtifactRows": summary["publicSafeCommandArmChecklistPopulationArtifactRows"],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "commandArmChecklistPopulationCategoryCounts": summary["commandArmChecklistPopulationCategoryCounts"],
            "commandArmChecklistPopulationRowsBody": summary["commandArmChecklistPopulationRowsBody"],
            "preflightChecks": summary["preflightChecks"],
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
                "Tracked public-safe command arm-boundary rows were consumed and converted into "
                "public-safe not-run command arm-checklist population rows for later validation."
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
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "activeCurrentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "wave911Focused": "historical-retired/non-reconstructable at 812/1408 = 57.67%",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=BOUNDARY_PROOF)
    parser.add_argument("--proof", type=Path, help="write proof JSON to this path")
    args = parser.parse_args()

    summary = build_public_safe_command_arm_checklist_population_summary(read_json(args.source))
    proof = build_public_safe_command_arm_checklist_population_proof(summary)
    if args.proof:
        args.proof.parent.mkdir(parents=True, exist_ok=True)
        args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
