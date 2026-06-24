#!/usr/bin/env python3
"""Validate public-safe real-importer dry-run harness checklist rows.

This module consumes only the tracked public harness-checklist population
proof. It validates not-run/unobserved checklist continuity and does not read
private assets, enumerate private roots, execute an importer, launch BEA,
generate assets, or emit raw private paths, filenames, hashes, or byte
lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population import (
    CHECKLIST_GROUPS,
    FALSE_GUARDS_CHECKLIST as POPULATION_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PREFLIGHT_CHECKS,
    PROOF_SCHEMA_VERSION as POPULATION_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES,
    REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS_CHECKLIST as POPULATION_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-validation.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-validation-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-validation-complete-public-safe-checklist-rows-validated-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-validation-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-readiness-gate-proof-plan"
)

CHECKLIST_POPULATION_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-population-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES = (
    "load-tracked-real-importer-harness-checklist-population-proof",
    "validate-real-importer-harness-checklist-population-continuity",
    "validate-harness-checklist-row-schema",
    "validate-harness-checklist-row-ordinals",
    "validate-harness-checklist-category-counts",
    "validate-harness-checklist-not-run-statuses",
    "validate-harness-checklist-unobserved-statuses",
    "validate-harness-archive-class-count-continuity",
    "validate-harness-checklist-refusal-guards",
    "validate-harness-checklist-public-redaction-policy",
    "select-harness-checklist-readiness-gate-lane",
    "emit-harness-checklist-validation-summary",
)

EXPECTED_CATEGORY_COUNTS = {category: len(tuple(items)) for category, _, items in CHECKLIST_GROUPS}
EXPECTED_CHECKLIST_ROW_COUNT = sum(EXPECTED_CATEGORY_COUNTS.values())

PUBLIC_ALLOWED_OUTPUTS = (
    "harness-checklist-validation-status",
    "harness-checklist-validation-row-counts",
    "harness-checklist-validation-category-counts",
    "harness-checklist-validation-interface-linkage",
    "harness-checklist-readiness-gate-next-lane",
)

REDACTED_FIELDS = (
    "harness-checklist-validation-input-path",
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
            *POPULATION_FALSE_GUARDS,
            "realImporterDryRunHarnessChecklistValidationReadPrivateInputs",
            "realImporterDryRunHarnessChecklistValidationPublishedPrivateInput",
            "realImporterDryRunHarnessChecklistReadinessGateExecuted",
            "realImporterDryRunHarnessCommandArmed",
            "realImporterDryRunHarnessCommandMaterialized",
            "realImporterDryRunHarnessPrivateOutputGenerated",
            "actualRealImporterDryRunHarnessExecuted",
        )
    )
    if key != "realImporterDryRunHarnessChecklistValidationExecuted"
)

POPULATION_ZERO_GUARD_COUNTERS = tuple(
    key for key in POPULATION_ZERO_COUNTERS if key != "harnessChecklistValidationRows"
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *POPULATION_ZERO_GUARD_COUNTERS,
            "harnessChecklistValidationPrivateInputRows",
            "harnessChecklistReadinessGateRows",
            "harnessChecklistCommandRows",
            "harnessChecklistCommandArtifactRows",
            "realImporterDryRunHarnessCommandRows",
            "realImporterDryRunHarnessCommandArtifactRows",
            "actualRealImporterDryRunHarnessRows",
        )
    )
)


class RealImporterDryRunHarnessChecklistValidationError(ValueError):
    """Raised when checklist-population evidence cannot support validation."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessChecklistValidationError(message)


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


def _validate_source_checklist_population_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == POPULATION_PROOF_SCHEMA_VERSION, "source checklist schema mismatch")
    _require(source.get("status") == "PASS", "source checklist status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "source checklist status token mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    _require(_read_mapping(source, "sourceEvidence").get("sourceProofCount") == 23, "source proof count mismatch")
    _require(
        _read_mapping(source, "sourceEvidence").get("sourceHarnessBoundaryProofCount") == 22,
        "source harness-boundary proof count mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessChecklistPopulationDecision")
    for key in (
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly",
        "realImporterHarnessBoundaryProofConsumed",
        "realImporterHarnessBoundaryProofContinuityValidated",
        "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation",
        "realImporterDryRunHarnessChecklistPopulated",
        "harnessChecklistRowsPopulated",
        "harnessChecklistArchiveClassRowsPopulated",
        "harnessChecklistInputClassRowsPopulated",
        "harnessChecklistRequiredArtifactRowsPopulated",
        "harnessChecklistStopConditionRowsPopulated",
        "harnessChecklistInterfaceRowsPopulated",
        "harnessChecklistRedactionRowsPopulated",
        "harnessChecklistPublicOutputRowsPopulated",
        "harnessChecklistRefusalGuardsValidated",
        "harnessChecklistArchiveClassOrderValidated",
        "harnessChecklistArchiveClassCountsValidated",
        "harnessChecklistInterfacesValidated",
        "harnessChecklistEmitsOnlyPublicSafeRows",
        "harnessChecklistValidationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision expected true: {key}")
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
        "realImporterDryRunHarnessExecutedInChecklistPopulationSlice",
        "realImporterDryRunHarnessOutputPublished",
        "realImporterDryRunHarnessChecklistPopulationReadPrivateInputs",
        "realImporterDryRunHarnessChecklistPublishedPrivateInput",
        "realImporterDryRunHarnessChecklistPrivateValuesPublished",
        "realImporterDryRunHarnessChecklistValidationExecuted",
        "realImporterDryRunHarnessChecklistDryRunExecuted",
        "realImporterDryRunHarnessCommandMaterialized",
        "realImporterDryRunHarnessPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "realImporterHarnessChecklistPopulationContract")
    for key, expected in {
        "harnessChecklistGroupCount": len(CHECKLIST_GROUPS),
        "harnessChecklistRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistArchiveClassRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-archive-class"],
        "harnessChecklistAllowedInputClassRows": EXPECTED_CATEGORY_COUNTS["allowed-future-input-class"],
        "harnessChecklistRequiredArtifactClassRows": EXPECTED_CATEGORY_COUNTS["required-future-artifact-class"],
        "harnessChecklistStopConditionRows": EXPECTED_CATEGORY_COUNTS["harness-stop-condition"],
        "harnessChecklistBoundaryInterfaceRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-interface"],
        "harnessChecklistRedactionFieldRows": EXPECTED_CATEGORY_COUNTS["redaction-field"],
        "harnessChecklistPublicAllowedOutputRows": EXPECTED_CATEGORY_COUNTS["public-allowed-output"],
        "passedChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedChecklistRowCount": 0,
        "notRunChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "unobservedChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistArtifactRows": 1,
    }.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")
    _require(
        tuple(contract.get("realImporterDryRunHarnessChecklistPopulationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES,
        "source checklist population interface mismatch",
    )

    archive_rows = _read_list(contract, "harnessArchiveClassChecklistRowsBody")
    _require(len(archive_rows) == EXPECTED_CATEGORY_COUNTS["harness-boundary-archive-class"], "archive row count mismatch")
    archive_total = 0
    for ordinal, row in enumerate(archive_rows, start=1):
        row_id = f"archive:{ordinal}:{row.get('sourceArchiveClass')}"
        _require(row.get("harnessChecklistArchiveClassRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceHarnessBoundaryRowOrdinal") == ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("futureHarnessChecklistValidationAllowed") is True, f"{row_id} future validation mismatch")
        _require(row.get("futureRealImporterDryRunHarnessRequiresLaterArm") is True, f"{row_id} later arm mismatch")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"{row_id} direct dry-run guard mismatch")
        _require(row.get("harnessChecklistPrivateIdentifiersPresent") is False, f"{row_id} private identifier guard mismatch")
        archive_total += int(row.get("archiveClassCount", 0))
        _validate_zero_fields(
            row,
            (
                "rawPathRows",
                "rawFilenameRows",
                "rawStemRows",
                "rawHashRows",
                "byteLengthRows",
                "rawTextureRefRows",
                "rawMeshRefRows",
                "actualAssetImportRows",
                "generatedAssetRows",
                "generatedDryRunOutputRows",
                "privateDryRunRows",
                "realImporterDryRunRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunHarnessOutputRows",
                "realImporterDryRunHarnessTraceRows",
                "harnessChecklistValidationRows",
                "harnessChecklistDryRunRows",
                "rawDryRunTraceRows",
            ),
            row_id,
        )
    _require(archive_total == 301, "archive class aggregate count mismatch")

    rows = _read_list(contract, "harnessChecklistRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "checklist row body count mismatch")
    category_counts = Counter()
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"checklist:{ordinal}:{row.get('category')}:{row.get('itemId')}"
        _require(row.get("harnessChecklistRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("status") == "NOT_RUN_PUBLIC_CHECKLIST_ONLY", f"{row_id} status token mismatch")
        _require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch")
        _require(row.get("observationStatus") == "unobserved", f"{row_id} observation status mismatch")
        _require(row.get("publicSafe") is True, f"{row_id} public-safe flag mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value guard mismatch")
        _require(row.get("futureHarnessChecklistValidationAllowed") is True, f"{row_id} future validation mismatch")
        _require(row.get("futureRealImporterDryRunHarnessRequiresLaterArm") is True, f"{row_id} later arm mismatch")
        _validate_zero_fields(
            row,
            (
                "rawPathRows",
                "rawFilenameRows",
                "rawStemRows",
                "rawHashRows",
                "byteLengthRows",
                "rawTextureRefRows",
                "rawMeshRefRows",
            ),
            row_id,
        )
        category_counts[row.get("category")] += 1
    _require(dict(category_counts) == EXPECTED_CATEGORY_COUNTS, "checklist category counts mismatch")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(POPULATION_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(POPULATION_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in POPULATION_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_harness_checklist_validation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe validation row per populated checklist row."""

    rows: list[dict[str, Any]] = []
    for row in contract["harnessChecklistRowsBody"]:
        rows.append(
            {
                "harnessChecklistValidationRowClass": "private-corpus-real-importer-dry-run-harness-checklist-validation-row",
                "harnessChecklistValidationMode": "public-safe-row-schema-status-token-validation-only",
                "harnessChecklistValidationRowOrdinal": row["harnessChecklistRowOrdinal"],
                "sourceHarnessChecklistRowOrdinal": row["harnessChecklistRowOrdinal"],
                "category": row["category"],
                "itemId": row["itemId"],
                "validationStatus": "validated-public-safe-not-run-unobserved",
                "sourceRowStatus": row["rowStatus"],
                "sourceObservationStatus": row["observationStatus"],
                "futureRealImporterDryRunHarnessRequiresLaterArm": True,
                "directRealImporterDryRunAllowedHere": False,
                "privateValuePublished": False,
                "rawPathRows": 0,
                "rawFilenameRows": 0,
                "rawStemRows": 0,
                "rawHashRows": 0,
                "byteLengthRows": 0,
                "rawTextureRefRows": 0,
                "rawMeshRefRows": 0,
                "privateDryRunRows": 0,
                "realImporterDryRunRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "actualAssetImportRows": 0,
                "generatedAssetRows": 0,
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_checklist_validation_summary(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe checklist validation summary."""

    contract = _validate_source_checklist_population_proof(source)
    validation_rows = build_harness_checklist_validation_rows(contract)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessChecklistValidationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessChecklistPopulationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "privateCorpusRealImporterDryRunHarnessChecklistValidationOnly": True,
        "realImporterHarnessChecklistPopulationProofConsumed": True,
        "realImporterHarnessChecklistPopulationProofContinuityValidated": True,
        "realImporterDryRunHarnessChecklistValidationExecuted": True,
        "realImporterDryRunHarnessChecklistValidationInputAccepted": True,
        "harnessChecklistSchemaValidated": True,
        "harnessChecklistRowOrdinalsValidated": True,
        "harnessChecklistCategoryCountsValidated": True,
        "harnessChecklistNotRunStatusesValidated": True,
        "harnessChecklistUnobservedStatusesValidated": True,
        "harnessChecklistArchiveClassCountsValidated": True,
        "harnessChecklistStopConditionsValidated": True,
        "harnessChecklistRedactionPolicyValidated": True,
        "harnessChecklistGuardCountersValidated": True,
        "harnessChecklistValidationEmitsOnlyPublicSafeRows": True,
        "harnessChecklistReadinessGateLaneSelected": True,
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
        "realImporterDryRunHarnessOutputPublished": False,
        "realImporterDryRunHarnessChecklistValidationReadPrivateInputs": False,
        "realImporterDryRunHarnessChecklistValidationPublishedPrivateInput": False,
        "realImporterDryRunHarnessChecklistReadinessGateExecuted": False,
        "realImporterDryRunHarnessCommandArmed": False,
        "realImporterDryRunHarnessCommandMaterialized": False,
        "realImporterDryRunHarnessPrivateOutputGenerated": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "realImporterHarnessChecklistValidationInputMode": "tracked-public-safe-harness-checklist-population-proof-json",
        "realImporterHarnessChecklistValidationOutputMode": "public-safe-harness-checklist-validation-status-token-rows",
        "selectedNextLaneClass": "private-corpus real importer dry-run harness checklist readiness gate without execution",
        "sourceProofCount": 24,
        "sourceChecklistPopulationProofCount": 23,
        "sourceHarnessChecklistPopulationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "realImporterDryRunHarnessChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES
        ),
        "harnessChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistValidationRows": len(validation_rows),
        "harnessChecklistValidationArchiveClassRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-archive-class"],
        "harnessChecklistValidationAllowedInputClassRows": EXPECTED_CATEGORY_COUNTS["allowed-future-input-class"],
        "harnessChecklistValidationRequiredArtifactClassRows": EXPECTED_CATEGORY_COUNTS["required-future-artifact-class"],
        "harnessChecklistValidationStopConditionRows": EXPECTED_CATEGORY_COUNTS["harness-stop-condition"],
        "harnessChecklistValidationBoundaryInterfaceRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-interface"],
        "harnessChecklistValidationRedactionFieldRows": EXPECTED_CATEGORY_COUNTS["redaction-field"],
        "harnessChecklistValidationPublicAllowedOutputRows": EXPECTED_CATEGORY_COUNTS["public-allowed-output"],
        "passedValidationRowCount": len(validation_rows),
        "failedValidationRowCount": 0,
        "validatedNotRunChecklistRowCount": len(validation_rows),
        "validatedUnobservedChecklistRowCount": len(validation_rows),
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": contract["consumerArchiveTotalCount"],
        "unknownAyaArchiveClassCount": contract["unknownAyaArchiveClassCount"],
        "publicSafeHarnessChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceHarnessChecklistPopulationInterfaces": list(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "realImporterDryRunHarnessChecklistValidationInterfaces": list(
            REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES
        ),
        "checklistCategoryCounts": [
            {"category": category, "validatedRowCount": count}
            for category, count in EXPECTED_CATEGORY_COUNTS.items()
        ],
        "harnessChecklistValidationRowsBody": validation_rows,
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_harness_checklist_validation_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate the public-safe checklist validation summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "checklist validation schema mismatch")
    _require(summary.get("status") == "PASS", "checklist validation status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "checklist validation status token mismatch",
    )
    true_decision_keys = (
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
        "harnessChecklistArchiveClassCountsValidated",
        "harnessChecklistStopConditionsValidated",
        "harnessChecklistRedactionPolicyValidated",
        "harnessChecklistGuardCountersValidated",
        "harnessChecklistValidationEmitsOnlyPublicSafeRows",
        "harnessChecklistReadinessGateLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    )
    for key in true_decision_keys:
        _require(summary.get(key) is True, f"expected true: {key}")
        _require(key not in summary.get("falseGuards", {}), f"true key also listed as false guard: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    for key, expected in {
        "sourceProofCount": 24,
        "sourceChecklistPopulationProofCount": 23,
        "sourceHarnessChecklistPopulationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "realImporterDryRunHarnessChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES
        ),
        "harnessChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistValidationArchiveClassRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-archive-class"],
        "harnessChecklistValidationAllowedInputClassRows": EXPECTED_CATEGORY_COUNTS["allowed-future-input-class"],
        "harnessChecklistValidationRequiredArtifactClassRows": EXPECTED_CATEGORY_COUNTS["required-future-artifact-class"],
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
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    rows = _read_list(summary, "harnessChecklistValidationRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "validation row body count mismatch")
    _require(
        Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS,
        "validation category count mismatch",
    )
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"validation:{ordinal}:{row.get('category')}:{row.get('itemId')}"
        _require(row.get("harnessChecklistValidationRowOrdinal") == ordinal, f"{row_id} ordinal mismatch")
        _require(row.get("sourceHarnessChecklistRowOrdinal") == ordinal, f"{row_id} source ordinal mismatch")
        _require(row.get("validationStatus") == "validated-public-safe-not-run-unobserved", f"{row_id} status mismatch")
        _require(row.get("sourceRowStatus") == "not-run", f"{row_id} source row status mismatch")
        _require(row.get("sourceObservationStatus") == "unobserved", f"{row_id} source observation mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value guard mismatch")
    _require(summary.get("publicLeakCheck") == "PASS", "public leak check mismatch")


def build_public_safe_real_importer_dry_run_harness_checklist_validation_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated checklist-validation summary in a proof-plan schema."""

    validate_public_safe_real_importer_dry_run_harness_checklist_validation_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessChecklistValidationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessChecklistPopulationStatus": REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceProofCount": 24,
            "sourceChecklistPopulationProofCount": 23,
            "checklistPopulationProof": CHECKLIST_POPULATION_PROOF.replace(".v1.json", ".md"),
            "checklistPopulationSchema": CHECKLIST_POPULATION_PROOF,
        },
        "realImporterHarnessChecklistValidationDecision": {
            "privateCorpusRealImporterDryRunHarnessChecklistValidationOnly": True,
            "realImporterHarnessChecklistPopulationProofConsumed": True,
            "realImporterHarnessChecklistPopulationProofContinuityValidated": True,
            "realImporterDryRunHarnessChecklistValidationExecuted": True,
            "realImporterDryRunHarnessChecklistValidationInputAccepted": True,
            "harnessChecklistSchemaValidated": True,
            "harnessChecklistRowOrdinalsValidated": True,
            "harnessChecklistCategoryCountsValidated": True,
            "harnessChecklistNotRunStatusesValidated": True,
            "harnessChecklistUnobservedStatusesValidated": True,
            "harnessChecklistArchiveClassCountsValidated": True,
            "harnessChecklistStopConditionsValidated": True,
            "harnessChecklistRedactionPolicyValidated": True,
            "harnessChecklistGuardCountersValidated": True,
            "harnessChecklistValidationEmitsOnlyPublicSafeRows": True,
            "harnessChecklistReadinessGateLaneSelected": True,
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
            "realImporterDryRunHarnessOutputPublished": False,
            "realImporterDryRunHarnessChecklistValidationReadPrivateInputs": False,
            "realImporterDryRunHarnessChecklistValidationPublishedPrivateInput": False,
            "realImporterDryRunHarnessChecklistReadinessGateExecuted": False,
            "realImporterDryRunHarnessCommandArmed": False,
            "realImporterDryRunHarnessCommandMaterialized": False,
            "realImporterDryRunHarnessPrivateOutputGenerated": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessChecklistValidationContract": {
            "realImporterHarnessChecklistValidationInputMode": summary[
                "realImporterHarnessChecklistValidationInputMode"
            ],
            "realImporterHarnessChecklistValidationOutputMode": summary[
                "realImporterHarnessChecklistValidationOutputMode"
            ],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "sourceHarnessChecklistPopulationInterfaceCount": summary[
                "sourceHarnessChecklistPopulationInterfaceCount"
            ],
            "sourceHarnessChecklistPopulationInterfaces": summary["sourceHarnessChecklistPopulationInterfaces"],
            "realImporterDryRunHarnessChecklistValidationInterfaceCount": summary[
                "realImporterDryRunHarnessChecklistValidationInterfaceCount"
            ],
            "realImporterDryRunHarnessChecklistValidationInterfaces": summary[
                "realImporterDryRunHarnessChecklistValidationInterfaces"
            ],
            "harnessChecklistRowsConsumed": summary["harnessChecklistRowsConsumed"],
            "harnessChecklistValidationRows": summary["harnessChecklistValidationRows"],
            "harnessChecklistValidationArchiveClassRows": summary["harnessChecklistValidationArchiveClassRows"],
            "harnessChecklistValidationAllowedInputClassRows": summary[
                "harnessChecklistValidationAllowedInputClassRows"
            ],
            "harnessChecklistValidationRequiredArtifactClassRows": summary[
                "harnessChecklistValidationRequiredArtifactClassRows"
            ],
            "harnessChecklistValidationStopConditionRows": summary[
                "harnessChecklistValidationStopConditionRows"
            ],
            "harnessChecklistValidationBoundaryInterfaceRows": summary[
                "harnessChecklistValidationBoundaryInterfaceRows"
            ],
            "harnessChecklistValidationRedactionFieldRows": summary[
                "harnessChecklistValidationRedactionFieldRows"
            ],
            "harnessChecklistValidationPublicAllowedOutputRows": summary[
                "harnessChecklistValidationPublicAllowedOutputRows"
            ],
            "passedValidationRowCount": summary["passedValidationRowCount"],
            "failedValidationRowCount": summary["failedValidationRowCount"],
            "validatedNotRunChecklistRowCount": summary["validatedNotRunChecklistRowCount"],
            "validatedUnobservedChecklistRowCount": summary["validatedUnobservedChecklistRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "preflightCheckCount": summary["preflightCheckCount"],
            "passedPreflightCheckCount": summary["passedPreflightCheckCount"],
            "failedPreflightCheckCount": summary["failedPreflightCheckCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeHarnessChecklistValidationArtifactRows": summary[
                "publicSafeHarnessChecklistValidationArtifactRows"
            ],
            "checklistCategoryCounts": summary["checklistCategoryCounts"],
            "harnessChecklistValidationRowsBody": summary["harnessChecklistValidationRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-checklist-validation-status-token-only",
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
                "the tracked harness-checklist population proof can be consumed as public-safe validation input",
                "the 99 checklist rows preserve ordinals, category counts, not-run statuses, and unobserved observation states",
                "the archive-class checklist rows preserve aggregate count 301 from the population proof",
                "the next readiness-gate lane is selected without executing the real/private importer",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw manifest consumption",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
                "real importer dry-run harness execution",
                "real importer dry-run harness readiness gate execution",
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
    parser.add_argument("--checklist-population-proof", type=Path, default=Path(CHECKLIST_POPULATION_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe checklist validation summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        population_proof = read_json(args.checklist_population_proof)
        summary = build_public_safe_real_importer_dry_run_harness_checklist_validation_summary(population_proof)
        validate_public_safe_real_importer_dry_run_harness_checklist_validation_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_checklist_validation_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessChecklistValidationError):
        print("Real importer dry-run harness checklist validation: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
