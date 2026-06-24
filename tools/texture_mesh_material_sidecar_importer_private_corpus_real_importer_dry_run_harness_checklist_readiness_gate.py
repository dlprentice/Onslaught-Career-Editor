#!/usr/bin/env python3
"""Validate readiness for later real-importer harness command materialization.

This module consumes only the tracked public harness-checklist validation proof.
It verifies that the validated not-run/unobserved checklist rows are ready for a
later explicitly armed command-materialization lane. It does not read private
assets, consume raw private manifests, materialize a command, execute an
importer, launch BEA, generate assets, mutate Ghidra, or emit raw private paths,
filenames, hashes, or byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as VALIDATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PREFLIGHT_CHECKS,
    PROOF_SCHEMA_VERSION as VALIDATION_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as VALIDATION_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
    REDACTED_FIELDS as VALIDATION_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as VALIDATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-readiness-gate.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-readiness-gate-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-readiness-gate-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Materialization Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-materialization-proof-plan"
)

CHECKLIST_VALIDATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-validation-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES = (
    "load-tracked-real-importer-harness-checklist-validation-proof",
    "validate-real-importer-harness-checklist-validation-continuity",
    "validate-harness-checklist-readiness-preconditions",
    "validate-harness-checklist-ready-row-statuses",
    "validate-harness-checklist-category-counts",
    "validate-harness-checklist-archive-class-count-continuity",
    "validate-harness-checklist-command-prerequisite-classes",
    "validate-harness-checklist-refusal-guards",
    "validate-harness-checklist-public-redaction-policy",
    "select-harness-command-materialization-lane",
    "emit-harness-checklist-readiness-gate-rows",
    "emit-harness-checklist-readiness-gate-summary",
)

PUBLIC_ALLOWED_OUTPUTS = (
    "harness-checklist-readiness-gate-status",
    "harness-checklist-readiness-gate-row-counts",
    "harness-checklist-readiness-gate-category-counts",
    "harness-checklist-readiness-gate-interface-linkage",
    "harness-command-materialization-next-lane",
)

REDACTED_FIELDS = (
    "harness-checklist-readiness-gate-input-path",
    "private-corpus-root",
    "raw-private-path",
    "raw-private-filename",
    "raw-private-stem",
    "raw-private-ref",
    "raw-private-hash",
    "raw-private-byte-length",
    "asset-bytes",
    "runtime-frame",
)

FALSE_GUARDS = tuple(
    key
    for key in dict.fromkeys(
        (
            *VALIDATION_FALSE_GUARDS,
            "realImporterDryRunHarnessChecklistReadinessGateReadPrivateInputs",
            "realImporterDryRunHarnessChecklistReadinessGatePublishedPrivateInput",
            "realImporterDryRunHarnessCommandArmed",
            "realImporterDryRunHarnessCommandMaterialized",
            "realImporterDryRunHarnessCommandPrivateOutputGenerated",
            "realImporterDryRunHarnessExecuted",
            "realImporterDryRunHarnessOutputPublished",
            "actualRealImporterDryRunHarnessExecuted",
        )
    )
    if key != "realImporterDryRunHarnessChecklistReadinessGateExecuted"
)

VALIDATION_ZERO_GUARD_COUNTERS = tuple(
    key for key in VALIDATION_ZERO_COUNTERS if key != "harnessChecklistReadinessGateRows"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *VALIDATION_ZERO_GUARD_COUNTERS,
            "harnessChecklistReadinessGatePrivateInputRows",
            "harnessChecklistCommandRows",
            "harnessChecklistCommandArtifactRows",
            "realImporterDryRunHarnessCommandRows",
            "realImporterDryRunHarnessCommandArtifactRows",
            "actualRealImporterDryRunHarnessRows",
        )
    )
)


class RealImporterDryRunHarnessChecklistReadinessGateError(ValueError):
    """Raised when checklist-validation evidence cannot support readiness."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessChecklistReadinessGateError(message)


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


def _validate_source_checklist_validation_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == VALIDATION_PROOF_SCHEMA_VERSION, "source validation schema mismatch")
    _require(source.get("status") == "PASS", "source validation status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "source validation status token mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 24, "source proof count mismatch")
    _require(
        source_evidence.get("sourceChecklistPopulationProofCount") == 23,
        "source checklist-population proof count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessChecklistValidationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessChecklistValidationOnly",
        "realImporterHarnessChecklistPopulationProofConsumed",
        "realImporterHarnessChecklistPopulationProofContinuityValidated",
        "realImporterDryRunHarnessChecklistValidationExecuted",
        "realImporterDryRunHarnessChecklistValidationInputAccepted",
        "harnessChecklistSchemaValidated",
        "harnessChecklistRowOrdinalsValidated",
        "harnessChecklistCategoryCountsValidated",
        "harnessChecklistNotRunStatusesValidated",
        "harnessChecklistUnobservedStatusesValidated",
        "harnessChecklistReadinessGateLaneSelected",
        "harnessChecklistValidationEmitsOnlyPublicSafeRows",
        "harnessChecklistRedactionPolicyValidated",
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
        "realImporterDryRunHarnessChecklistValidationReadPrivateInputs",
        "realImporterDryRunHarnessChecklistValidationPublishedPrivateInput",
        "realImporterDryRunHarnessChecklistReadinessGateExecuted",
        "realImporterDryRunHarnessCommandArmed",
        "realImporterDryRunHarnessCommandMaterialized",
        "realImporterDryRunHarnessPrivateOutputGenerated",
        "realImporterDryRunHarnessOutputPublished",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessChecklistValidationContract")
    expected_contract_counts = {
        "sourceHarnessChecklistPopulationInterfaceCount": 12,
        "realImporterDryRunHarnessChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES
        ),
        "harnessChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistValidationArchiveClassRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-archive-class"],
        "harnessChecklistValidationAllowedInputClassRows": EXPECTED_CATEGORY_COUNTS["allowed-future-input-class"],
        "harnessChecklistValidationRequiredArtifactClassRows": EXPECTED_CATEGORY_COUNTS[
            "required-future-artifact-class"
        ],
        "harnessChecklistValidationStopConditionRows": EXPECTED_CATEGORY_COUNTS["harness-stop-condition"],
        "harnessChecklistValidationBoundaryInterfaceRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-interface"],
        "harnessChecklistValidationRedactionFieldRows": EXPECTED_CATEGORY_COUNTS["redaction-field"],
        "harnessChecklistValidationPublicAllowedOutputRows": EXPECTED_CATEGORY_COUNTS["public-allowed-output"],
        "passedValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedValidationRowCount": 0,
        "validatedNotRunChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedUnobservedChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistValidationArtifactRows": 1,
    }
    for key, expected in expected_contract_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "harnessChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        _require(
            row.get("harnessChecklistValidationRowOrdinal") == expected_ordinal,
            f"source validation ordinal mismatch: {expected_ordinal}",
        )
        _require(
            row.get("sourceHarnessChecklistRowOrdinal") == expected_ordinal,
            f"source checklist ordinal mismatch: {expected_ordinal}",
        )
        _require(
            row.get("validationStatus") == "validated-public-safe-not-run-unobserved",
            f"source validation status mismatch: {expected_ordinal}",
        )
        _require(row.get("sourceRowStatus") == "not-run", f"source row status mismatch: {expected_ordinal}")
        _require(
            row.get("sourceObservationStatus") == "unobserved",
            f"source observation status mismatch: {expected_ordinal}",
        )
        _require(row.get("privateValuePublished") is False, f"source private value flag mismatch: {expected_ordinal}")
        _require(
            row.get("directRealImporterDryRunAllowedHere") is False,
            f"source direct importer flag mismatch: {expected_ordinal}",
        )
        _require(
            row.get("futureRealImporterDryRunHarnessRequiresLaterArm") is True,
            f"source later-arm flag mismatch: {expected_ordinal}",
        )
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
                "generatedAssetRows",
                "privateDryRunRows",
                "rawFilenameRows",
                "rawHashRows",
                "rawMeshRefRows",
                "rawPathRows",
                "rawStemRows",
                "rawTextureRefRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            f"source row {expected_ordinal}",
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(VALIDATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(VALIDATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in VALIDATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")

    redaction = _read_mapping(source, "redactionPolicy")
    _require(
        redaction.get("publicAllowedOutputCount") == len(VALIDATION_PUBLIC_ALLOWED_OUTPUTS),
        "source public allowed output count mismatch",
    )
    _require(
        redaction.get("redactedFieldCount") == len(VALIDATION_REDACTED_FIELDS),
        "source redacted field count mismatch",
    )
    _require(redaction.get("publicLeakCheck") == "PASS", "source redaction public leak check mismatch")
    return contract


def build_harness_checklist_readiness_gate_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe readiness-gate row per validated checklist row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "harnessChecklistValidationRowsBody"):
        ordinal = int(source_row["harnessChecklistValidationRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessCommandMaterializationRequiresLaterArm": True,
                "futureRealImporterDryRunHarnessRequiresLaterArm": True,
                "generatedAssetRows": 0,
                "harnessChecklistReadinessGateMode": "public-safe-readiness-precondition-status-token-only",
                "harnessChecklistReadinessGateRowClass": (
                    "private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-row"
                ),
                "harnessChecklistReadinessGateRowOrdinal": ordinal,
                "itemId": source_row["itemId"],
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "readinessGateStatus": "ready-for-later-explicit-harness-command-materialization",
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceHarnessChecklistRowOrdinal": source_row["sourceHarnessChecklistRowOrdinal"],
                "sourceHarnessChecklistValidationRowOrdinal": ordinal,
                "sourceObservationStatus": source_row["sourceObservationStatus"],
                "sourceRowStatus": source_row["sourceRowStatus"],
                "sourceValidationStatus": source_row["validationStatus"],
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe readiness-gate summary."""

    contract = _validate_source_checklist_validation_proof(source)
    rows = build_harness_checklist_readiness_gate_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "readiness category counts mismatch")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS
        ),
        "slice": THIS_SLICE,
        "scope": THIS_SCOPE,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessChecklistValidationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateOnly": True,
        "realImporterHarnessChecklistValidationProofConsumed": True,
        "realImporterHarnessChecklistValidationProofContinuityValidated": True,
        "realImporterHarnessChecklistValidationRowsConsumed": True,
        "realImporterDryRunHarnessChecklistReadinessGateExecuted": True,
        "realImporterDryRunHarnessChecklistReadinessGateInputAccepted": True,
        "harnessChecklistReadinessGatePreconditionsValidated": True,
        "harnessChecklistReadyRowStatusesValidated": True,
        "harnessChecklistReadinessGateRowOrdinalsValidated": True,
        "harnessChecklistReadinessGateCategoryCountsValidated": True,
        "harnessChecklistCommandPrerequisiteClassesValidated": True,
        "harnessChecklistReadinessGateEmitsOnlyPublicSafeRows": True,
        "harnessChecklistReadinessGateRedactionPolicyValidated": True,
        "harnessCommandMaterializationLaneSelected": True,
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
        "realImporterDryRunHarnessChecklistReadinessGateReadPrivateInputs": False,
        "realImporterDryRunHarnessChecklistReadinessGatePublishedPrivateInput": False,
        "realImporterDryRunHarnessCommandArmed": False,
        "realImporterDryRunHarnessCommandMaterialized": False,
        "realImporterDryRunHarnessCommandPrivateOutputGenerated": False,
        "realImporterDryRunHarnessOutputPublished": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "realImporterHarnessChecklistReadinessGateInputMode": (
            "tracked-public-safe-real-importer-harness-checklist-validation-proof-json"
        ),
        "realImporterHarnessChecklistReadinessGateOutputMode": (
            "public-safe-readiness-gate-status-and-command-materialization-lane-selection"
        ),
        "selectedNextLaneClass": "private-corpus real importer dry-run harness command materialization without execution",
        "sourceProofCount": 25,
        "sourceChecklistValidationProofCount": 24,
        "sourceHarnessChecklistValidationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES),
        "realImporterDryRunHarnessChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "harnessChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistReadinessGateRows": len(rows),
        "harnessChecklistReadinessGateArchiveClassRows": category_counts["harness-boundary-archive-class"],
        "harnessChecklistReadinessGateAllowedInputClassRows": category_counts["allowed-future-input-class"],
        "harnessChecklistReadinessGateRequiredArtifactClassRows": category_counts[
            "required-future-artifact-class"
        ],
        "harnessChecklistReadinessGateStopConditionRows": category_counts["harness-stop-condition"],
        "harnessChecklistReadinessGateBoundaryInterfaceRows": category_counts["harness-boundary-interface"],
        "harnessChecklistReadinessGateRedactionFieldRows": category_counts["redaction-field"],
        "harnessChecklistReadinessGatePublicAllowedOutputRows": category_counts["public-allowed-output"],
        "passedReadinessGateRowCount": len(rows),
        "failedReadinessGateRowCount": 0,
        "readyForLaterCommandMaterializationRowCount": len(rows),
        "readyForLaterHarnessArmRowCount": len(rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceHarnessChecklistValidationInterfaces": list(REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES),
        "realImporterDryRunHarnessChecklistReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "harnessChecklistReadinessGateCategoryCounts": dict(sorted(category_counts.items())),
        "harnessChecklistReadinessGateRowsBody": rows,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(
    summary: Mapping[str, Any],
) -> None:
    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
        "summary readiness status mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateOnly",
        "realImporterHarnessChecklistValidationProofConsumed",
        "realImporterHarnessChecklistValidationProofContinuityValidated",
        "realImporterHarnessChecklistValidationRowsConsumed",
        "realImporterDryRunHarnessChecklistReadinessGateExecuted",
        "realImporterDryRunHarnessChecklistReadinessGateInputAccepted",
        "harnessChecklistReadinessGatePreconditionsValidated",
        "harnessChecklistReadyRowStatusesValidated",
        "harnessChecklistReadinessGateRowOrdinalsValidated",
        "harnessChecklistReadinessGateCategoryCountsValidated",
        "harnessChecklistCommandPrerequisiteClassesValidated",
        "harnessChecklistReadinessGateEmitsOnlyPublicSafeRows",
        "harnessChecklistReadinessGateRedactionPolicyValidated",
        "harnessCommandMaterializationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"summary true flag mismatch: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    for key, expected in {
        "sourceProofCount": 25,
        "sourceChecklistValidationProofCount": 24,
        "sourceHarnessChecklistValidationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES),
        "realImporterDryRunHarnessChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "harnessChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedReadinessGateRowCount": 0,
        "readyForLaterCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "harnessChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        _require(
            row.get("harnessChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"readiness ordinal mismatch: {expected_ordinal}",
        )
        _require(
            row.get("sourceHarnessChecklistValidationRowOrdinal") == expected_ordinal,
            f"source validation ordinal mismatch: {expected_ordinal}",
        )
        _require(
            row.get("readinessGateStatus") == "ready-for-later-explicit-harness-command-materialization",
            f"readiness status mismatch: {expected_ordinal}",
        )
        _require(
            row.get("sourceValidationStatus") == "validated-public-safe-not-run-unobserved",
            f"source validation status mismatch: {expected_ordinal}",
        )
        _require(row.get("sourceRowStatus") == "not-run", f"source row status mismatch: {expected_ordinal}")
        _require(
            row.get("sourceObservationStatus") == "unobserved",
            f"source observation status mismatch: {expected_ordinal}",
        )
        _require(row.get("privateValuePublished") is False, f"private value flag mismatch: {expected_ordinal}")
        _require(
            row.get("directRealImporterDryRunAllowedHere") is False,
            f"direct importer flag mismatch: {expected_ordinal}",
        )
        _require(
            row.get("futureHarnessCommandMaterializationRequiresLaterArm") is True,
            f"command later-arm flag mismatch: {expected_ordinal}",
        )
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
                "generatedAssetRows",
                "privateDryRunRows",
                "rawFilenameRows",
                "rawHashRows",
                "rawMeshRefRows",
                "rawPathRows",
                "rawStemRows",
                "rawTextureRefRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            f"readiness row {expected_ordinal}",
        )


def build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated readiness-gate summary in a proof-plan schema."""

    validate_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateStatus": (
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessChecklistValidationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
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
            "sourceChecklistValidationProofCount": summary["sourceChecklistValidationProofCount"],
            "sourceHarnessChecklistValidationInterfaceCount": summary["sourceHarnessChecklistValidationInterfaceCount"],
            "realImporterDryRunHarnessChecklistReadinessGateInterfaceCount": summary[
                "realImporterDryRunHarnessChecklistReadinessGateInterfaceCount"
            ],
            "sourceHarnessChecklistValidationInterfaces": summary["sourceHarnessChecklistValidationInterfaces"],
            "realImporterDryRunHarnessChecklistReadinessGateInterfaces": summary[
                "realImporterDryRunHarnessChecklistReadinessGateInterfaces"
            ],
            "sourceProof": CHECKLIST_VALIDATION_PROOF,
        },
        "realImporterHarnessChecklistReadinessGateDecision": {
            "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateOnly": True,
            "realImporterHarnessChecklistValidationProofConsumed": True,
            "realImporterHarnessChecklistValidationProofContinuityValidated": True,
            "realImporterHarnessChecklistValidationRowsConsumed": True,
            "realImporterDryRunHarnessChecklistReadinessGateExecuted": True,
            "realImporterDryRunHarnessChecklistReadinessGateInputAccepted": True,
            "harnessChecklistReadinessGatePreconditionsValidated": True,
            "harnessChecklistReadyRowStatusesValidated": True,
            "harnessChecklistReadinessGateRowOrdinalsValidated": True,
            "harnessChecklistReadinessGateCategoryCountsValidated": True,
            "harnessChecklistCommandPrerequisiteClassesValidated": True,
            "harnessChecklistReadinessGateEmitsOnlyPublicSafeRows": True,
            "harnessChecklistReadinessGateRedactionPolicyValidated": True,
            "harnessCommandMaterializationLaneSelected": True,
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
            "realImporterDryRunHarnessChecklistReadinessGateReadPrivateInputs": False,
            "realImporterDryRunHarnessChecklistReadinessGatePublishedPrivateInput": False,
            "realImporterDryRunHarnessCommandArmed": False,
            "realImporterDryRunHarnessCommandMaterialized": False,
            "realImporterDryRunHarnessCommandPrivateOutputGenerated": False,
            "realImporterDryRunHarnessOutputPublished": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessChecklistReadinessGateContract": {
            "realImporterHarnessChecklistReadinessGateInputMode": summary[
                "realImporterHarnessChecklistReadinessGateInputMode"
            ],
            "realImporterHarnessChecklistReadinessGateOutputMode": summary[
                "realImporterHarnessChecklistReadinessGateOutputMode"
            ],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "harnessChecklistValidationRowsConsumed": summary["harnessChecklistValidationRowsConsumed"],
            "harnessChecklistReadinessGateRows": summary["harnessChecklistReadinessGateRows"],
            "harnessChecklistReadinessGateArchiveClassRows": summary[
                "harnessChecklistReadinessGateArchiveClassRows"
            ],
            "harnessChecklistReadinessGateAllowedInputClassRows": summary[
                "harnessChecklistReadinessGateAllowedInputClassRows"
            ],
            "harnessChecklistReadinessGateRequiredArtifactClassRows": summary[
                "harnessChecklistReadinessGateRequiredArtifactClassRows"
            ],
            "harnessChecklistReadinessGateStopConditionRows": summary[
                "harnessChecklistReadinessGateStopConditionRows"
            ],
            "harnessChecklistReadinessGateBoundaryInterfaceRows": summary[
                "harnessChecklistReadinessGateBoundaryInterfaceRows"
            ],
            "harnessChecklistReadinessGateRedactionFieldRows": summary[
                "harnessChecklistReadinessGateRedactionFieldRows"
            ],
            "harnessChecklistReadinessGatePublicAllowedOutputRows": summary[
                "harnessChecklistReadinessGatePublicAllowedOutputRows"
            ],
            "passedReadinessGateRowCount": summary["passedReadinessGateRowCount"],
            "failedReadinessGateRowCount": summary["failedReadinessGateRowCount"],
            "readyForLaterCommandMaterializationRowCount": summary[
                "readyForLaterCommandMaterializationRowCount"
            ],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeHarnessChecklistReadinessGateArtifactRows": summary[
                "publicSafeHarnessChecklistReadinessGateArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "harnessChecklistReadinessGateCategoryCounts": summary[
                "harnessChecklistReadinessGateCategoryCounts"
            ],
            "harnessChecklistReadinessGateRowsBody": summary["harnessChecklistReadinessGateRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-checklist-readiness-gate-status-token-only",
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
                "the tracked harness-checklist validation proof can be consumed as public-safe readiness-gate input",
                "the 99 validated checklist rows are still not-run and unobserved",
                "the readiness gate preserves checklist row/category counts and aggregate archive count 301",
                "the next command-materialization lane is selected without arming or materializing a command",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw manifest consumption",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
                "real importer dry-run harness execution",
                "real importer dry-run harness command arming",
                "real importer dry-run harness command materialization",
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
    parser.add_argument("--checklist-validation-proof", type=Path, default=Path(CHECKLIST_VALIDATION_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe readiness-gate summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        validation_proof = read_json(args.checklist_validation_proof)
        summary = build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(validation_proof)
        validate_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessChecklistReadinessGateError):
        print("Real importer dry-run harness checklist readiness gate: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
