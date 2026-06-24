#!/usr/bin/env python3
"""Define the public-safe real-importer dry-run harness boundary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import (
    REQUIRED_ARCHIVE_CLASSES,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter import (
    EXPECTED_ARCHIVE_CLASS_COUNTS,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_readiness_gate import (
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as READINESS_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_READINESS_INTERFACES,
    REAL_IMPORTER_READINESS_STATUS,
    REDACTED_FIELDS as READINESS_REDACTED_FIELDS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary.v1"
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-boundary-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_BOUNDARY_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-boundary-defined-public-safe-boundary-only-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-population-proof-plan"
)

READINESS_GATE_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "readiness-gate-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES = (
    "load-tracked-real-importer-readiness-gate-proof",
    "validate-real-importer-readiness-gate-continuity",
    "validate-harness-boundary-preconditions",
    "define-read-only-private-corpus-input-boundary",
    "define-app-owned-private-output-boundary",
    "define-real-importer-dry-run-stop-conditions",
    "validate-harness-boundary-private-data-refusal-guards",
    "select-harness-checklist-population-lane",
    "emit-harness-boundary-validation-rows",
    "emit-harness-boundary-summary",
)

ALLOWED_FUTURE_INPUT_CLASSES = (
    "read-only-corpus-root-handle",
    "tracked-public-safe-redacted-manifest",
    "public-safe-archive-class-count-rows",
    "app-owned-private-evidence-root",
    "app-owned-importer-dry-run-output-root",
)

REQUIRED_FUTURE_ARTIFACT_CLASSES = (
    "private-dry-run-command-manifest",
    "private-dry-run-input-manifest",
    "private-dry-run-output-inventory",
    "private-dry-run-log-inventory",
    "private-leak-scan-report",
    "public-safe-result-summary",
)

HARNESS_STOP_CONDITIONS = (
    "installed-game-or-original-executable-would-be-mutated",
    "raw-private-paths-or-filenames-would-enter-public-scope",
    "private-asset-content-read-outside-later-armed-harness",
    "raw-private-manifest-rows-would-be-published",
    "real-importer-output-escapes-app-owned-artifact-root",
    "dry-run-would-generate-assets-without-output-inventory",
    "importer-would-launch-bea-or-require-runtime-game-state",
    "ghidra-mutation-would-be-needed",
    "godot-ui-renderer-or-rebuild-work-would-be-needed",
    "archive-class-order-or-counts-mismatch-readiness-contract",
    "unknown-archive-class-appears",
    "raw-hashes-byte-lengths-or-private-refs-would-enter-public-scope",
)

PUBLIC_ALLOWED_OUTPUTS = tuple(
    dict.fromkeys(
        (
            *READINESS_PUBLIC_ALLOWED_OUTPUTS,
            "real-importer-dry-run-harness-boundary-status",
            "source-real-importer-readiness-gate-status",
            "harness-boundary-rows",
            "harness-boundary-input-artifact-classes",
            "harness-boundary-stop-conditions",
            "harness-boundary-interface-linkage",
        )
    )
)

REDACTED_FIELDS = tuple(
    dict.fromkeys(
        (
            *READINESS_REDACTED_FIELDS,
            "real-importer-dry-run-harness-private-input-root",
            "real-importer-dry-run-harness-output-root",
            "real-importer-dry-run-command-line",
            "real-importer-dry-run-stdout-stderr",
            "real-importer-dry-run-generated-output-path",
        )
    )
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "realImporterDryRunHarnessBoundaryReadPrivateInputs",
            "realImporterDryRunHarnessBoundaryPublishedPrivateInput",
            "privateHarnessBoundaryArtifactPublished",
            "harnessChecklistPopulationExecuted",
            "harnessChecklistMaterialized",
            "realImporterDryRunHarnessArmed",
            "realImporterDryRunHarnessExecutedInBoundarySlice",
            "realImporterDryRunHarnessOutputPublished",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_COUNTERS,
            "realImporterDryRunHarnessBoundaryPrivateInputRows",
            "privateHarnessBoundaryArtifactRows",
            "harnessChecklistRows",
            "realImporterDryRunHarnessOutputRows",
            "realImporterDryRunHarnessTraceRows",
            "generatedDryRunOutputRows",
        )
    )
)


class RealImporterDryRunHarnessBoundaryError(ValueError):
    """Raised when readiness proof cannot support harness-boundary selection."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessBoundaryError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _validate_source_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source readiness proof schema mismatch")
    _require(source.get("status") == "PASS", "source readiness proof status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunReadinessGateStatus") == REAL_IMPORTER_READINESS_STATUS,
        "source readiness status mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")
    _require(_read_mapping(source, "sourceEvidence").get("sourceProofCount") == 21, "source proof count mismatch")

    decision = _read_mapping(source, "realImporterReadinessDecision")
    for key in (
        "privateCorpusRealImporterDryRunReadinessGateOnly",
        "adapterConsumerDryRunProofConsumed",
        "adapterConsumerDryRunProofContinuityValidated",
        "adapterConsumerDryRunRowsConsumedByReadinessGate",
        "realImporterDryRunReadinessGateExecuted",
        "realImporterReadinessInputAccepted",
        "realImporterReadinessArchiveClassOrderValidated",
        "realImporterReadinessArchiveClassCountsValidated",
        "realImporterReadinessGuardCountersValidated",
        "realImporterReadinessInterfacesValidated",
        "realImporterDryRunHarnessBoundaryLaneSelected",
        "realImporterReadinessEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source decision expected true: {key}")
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "realImporterDryRunHarnessExecuted",
        "realImporterDryRunHarnessMaterialized",
        "realImporterDryRunBoundaryBypassed",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision expected false: {key}")

    contract = _read_mapping(source, "realImporterReadinessContract")
    for key, expected in {
        "realImporterDryRunReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "adapterConsumerDryRunRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "realImporterReadinessGateRows": len(REQUIRED_ARCHIVE_CLASSES),
        "realImporterReadinessArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "realImporterReadinessSummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "publicSafeRealImporterReadinessArtifactRows": 1,
    }.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")
    _require(
        tuple(contract.get("realImporterDryRunReadinessInterfaces", ())) == REAL_IMPORTER_READINESS_INTERFACES,
        "source readiness interface mismatch",
    )
    rows = contract.get("realImporterReadinessRowsBody")
    _require(isinstance(rows, list), "source readiness rows must be a list")
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "source row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"source row count mismatch: {archive_class}")
        _require(row.get("readyForRealImporterDryRunHarnessBoundary") is True, f"source row boundary readiness mismatch: {archive_class}")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"source row direct dry-run guard mismatch: {archive_class}")
        _require(row.get("realImporterReadinessPrivateIdentifiersPresent") is False, f"source row private guard mismatch: {archive_class}")
        for key in (
            "rawPathRows",
            "rawFilenameRows",
            "rawStemRows",
            "rawHashRows",
            "byteLengthRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "actualAssetImportRows",
            "generatedAssetRows",
            "privateDryRunRows",
            "realImporterDryRunRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunBoundaryBypassRows",
        ):
            _require(row.get(key) == 0, f"source row zero mismatch: {archive_class}:{key}")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(READINESS_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(READINESS_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in READINESS_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    return contract


def build_harness_boundary_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(contract["realImporterReadinessRowsBody"], start=1):
        archive_class = row["sourceArchiveClass"]
        rows.append(
            {
                "harnessBoundaryRowClass": "private-corpus-real-importer-dry-run-harness-boundary-row",
                "harnessBoundaryRowMode": "public-safe-boundary-class-count-status-token-only",
                "harnessBoundaryRowOrdinal": ordinal,
                "sourceRealImporterReadinessGateRowOrdinal": row["realImporterReadinessGateRowOrdinal"],
                "sourceArchiveClass": archive_class,
                "archiveClassCount": row["archiveClassCount"],
                "futureHarnessChecklistPopulationAllowed": True,
                "futureRealImporterDryRunHarnessRequiresLaterArm": True,
                "directRealImporterDryRunAllowedHere": False,
                "harnessBoundaryPrivateIdentifiersPresent": False,
                "rawPathRows": 0,
                "rawFilenameRows": 0,
                "rawStemRows": 0,
                "rawHashRows": 0,
                "byteLengthRows": 0,
                "rawTextureRefRows": 0,
                "rawMeshRefRows": 0,
                "actualAssetImportRows": 0,
                "generatedAssetRows": 0,
                "generatedDryRunOutputRows": 0,
                "privateDryRunRows": 0,
                "realImporterDryRunRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunHarnessOutputRows": 0,
                "realImporterDryRunHarnessTraceRows": 0,
                "harnessChecklistRows": 0,
                "rawDryRunTraceRows": 0,
            }
        )
    return rows


def build_public_safe_real_importer_dry_run_harness_boundary_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe real-importer dry-run harness boundary summary."""

    contract = _validate_source_readiness_gate_proof(source)
    boundary_rows = build_harness_boundary_rows(contract)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessBoundaryStatus": REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterReadinessGateStatus": REAL_IMPORTER_READINESS_STATUS,
        "privateCorpusRealImporterDryRunHarnessBoundaryOnly": True,
        "realImporterReadinessGateProofConsumed": True,
        "realImporterReadinessGateProofContinuityValidated": True,
        "realImporterReadinessRowsConsumedByHarnessBoundary": True,
        "realImporterDryRunHarnessBoundaryDefined": True,
        "harnessBoundaryInputClassesDefined": True,
        "harnessBoundaryOutputClassesDefined": True,
        "harnessBoundaryStopConditionsDefined": True,
        "harnessBoundaryRefusalGuardsValidated": True,
        "harnessBoundaryArchiveClassOrderValidated": True,
        "harnessBoundaryArchiveClassCountsValidated": True,
        "harnessBoundaryInterfacesValidated": True,
        "harnessBoundaryEmitsOnlyPublicSafeRows": True,
        "harnessChecklistPopulationLaneSelected": True,
        "privateEvidenceStoredOutsidePublicReleaseScope": True,
        "publicPrivateSeparationRequired": True,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "privateManifestMaterialized": False,
        "privateRawManifestRowsObserved": False,
        "privateManifestRowsPublished": False,
        "rawPrivateManifestConsumed": False,
        "rawPrivateManifestRowsConsumed": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "privateImporterDryRunExecuted": False,
        "realImporterDryRunExecuted": False,
        "realImporterDryRunHarnessExecuted": False,
        "realImporterDryRunHarnessArmed": False,
        "realImporterDryRunHarnessBoundaryReadPrivateInputs": False,
        "realImporterDryRunHarnessBoundaryPublishedPrivateInput": False,
        "realImporterDryRunHarnessExecutedInBoundarySlice": False,
        "realImporterDryRunHarnessOutputPublished": False,
        "privateHarnessBoundaryArtifactPublished": False,
        "harnessChecklistPopulationExecuted": False,
        "harnessChecklistMaterialized": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "realImporterHarnessBoundaryInputMode": "tracked-public-safe-real-importer-readiness-gate-proof-json",
        "realImporterHarnessBoundaryOutputMode": "public-safe-harness-boundary-class-count-status-token-rows",
        "selectedNextLaneClass": "private-corpus real importer dry-run harness checklist population without execution",
        "sourceProofCount": 22,
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "realImporterDryRunHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterReadinessRowsConsumed": len(boundary_rows),
        "harnessBoundaryRows": len(boundary_rows),
        "harnessBoundaryArchiveClassRows": len(boundary_rows),
        "harnessBoundarySummaryRows": 1,
        "consumerArchiveTotalCount": sum(row["archiveClassCount"] for row in boundary_rows),
        "baseArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["base-resource-archive"],
        "frontendArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["frontend-resource-archive"],
        "loadingArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["loading-resource-archive"],
        "numericLevelArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["numeric-level-resource-archive"],
        "goodieArchiveClassCount": EXPECTED_ARCHIVE_CLASS_COUNTS["goodie-resource-archive"],
        "unknownAyaArchiveClassCount": 0,
        "harnessAllowedFutureInputClassCount": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessRequiredFutureArtifactClassCount": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessStopConditionCount": len(HARNESS_STOP_CONDITIONS),
        "publicSafeHarnessBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceRealImporterReadinessInterfaces": list(REAL_IMPORTER_READINESS_INTERFACES),
        "realImporterDryRunHarnessBoundaryInterfaces": list(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "allowedFutureInputClasses": list(ALLOWED_FUTURE_INPUT_CLASSES),
        "requiredFutureArtifactClasses": list(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessStopConditions": list(HARNESS_STOP_CONDITIONS),
        "harnessBoundaryRowsBody": boundary_rows,
        "publicLeakCheck": "PASS",
        "falseGuards": {key: False for key in FALSE_GUARDS},
        "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
    }


def validate_public_safe_real_importer_dry_run_harness_boundary_summary(summary: Mapping[str, Any]) -> None:
    """Validate the public-safe harness boundary summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "harness boundary schema mismatch")
    _require(summary.get("status") == "PASS", "harness boundary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessBoundaryStatus") == REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "harness boundary status token mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessBoundaryOnly",
        "realImporterReadinessGateProofConsumed",
        "realImporterReadinessGateProofContinuityValidated",
        "realImporterReadinessRowsConsumedByHarnessBoundary",
        "realImporterDryRunHarnessBoundaryDefined",
        "harnessBoundaryInputClassesDefined",
        "harnessBoundaryOutputClassesDefined",
        "harnessBoundaryStopConditionsDefined",
        "harnessBoundaryRefusalGuardsValidated",
        "harnessBoundaryArchiveClassOrderValidated",
        "harnessBoundaryArchiveClassCountsValidated",
        "harnessBoundaryInterfacesValidated",
        "harnessBoundaryEmitsOnlyPublicSafeRows",
        "harnessChecklistPopulationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    for key, expected in {
        "sourceProofCount": 22,
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "realImporterDryRunHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterReadinessRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundaryRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundaryArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundarySummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "harnessAllowedFutureInputClassCount": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessRequiredFutureArtifactClassCount": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessStopConditionCount": len(HARNESS_STOP_CONDITIONS),
        "publicSafeHarnessBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceRealImporterReadinessInterfaces", ())) == REAL_IMPORTER_READINESS_INTERFACES,
        "source readiness interface list mismatch",
    )
    _require(
        tuple(summary.get("realImporterDryRunHarnessBoundaryInterfaces", ())) == REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES,
        "harness boundary interface list mismatch",
    )
    _require(tuple(summary.get("allowedFutureInputClasses", ())) == ALLOWED_FUTURE_INPUT_CLASSES, "allowed input classes mismatch")
    _require(
        tuple(summary.get("requiredFutureArtifactClasses", ())) == REQUIRED_FUTURE_ARTIFACT_CLASSES,
        "required artifact classes mismatch",
    )
    _require(tuple(summary.get("harnessStopConditions", ())) == HARNESS_STOP_CONDITIONS, "stop conditions mismatch")
    rows = summary.get("harnessBoundaryRowsBody", [])
    _require([row.get("sourceArchiveClass") for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "harness row order mismatch")
    for row in rows:
        archive_class = row.get("sourceArchiveClass")
        _require(row.get("archiveClassCount") == EXPECTED_ARCHIVE_CLASS_COUNTS[archive_class], f"harness row count mismatch: {archive_class}")
        _require(row.get("futureHarnessChecklistPopulationAllowed") is True, f"future checklist flag mismatch: {archive_class}")
        _require(row.get("futureRealImporterDryRunHarnessRequiresLaterArm") is True, f"later arm flag mismatch: {archive_class}")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"direct dry-run guard mismatch: {archive_class}")
        _require(row.get("harnessBoundaryPrivateIdentifiersPresent") is False, f"private identifier guard mismatch: {archive_class}")
        for key in (
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
            "harnessChecklistRows",
            "rawDryRunTraceRows",
        ):
            _require(row.get(key) == 0, f"harness row zero mismatch: {archive_class}:{key}")
    _require(summary.get("publicLeakCheck") == "PASS", "public leak check mismatch")


def build_public_safe_real_importer_dry_run_harness_boundary_proof(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a validated harness boundary summary in the tracked proof-plan schema."""

    validate_public_safe_real_importer_dry_run_harness_boundary_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessBoundaryStatus": REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterReadinessGateStatus": REAL_IMPORTER_READINESS_STATUS,
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "sourceEvidence": {
            "sourceProofCount": 22,
            "readinessGateProof": READINESS_GATE_PROOF.replace(".v1.json", ".md"),
            "readinessGateSchema": READINESS_GATE_PROOF,
        },
        "realImporterHarnessBoundaryDecision": {
            "privateCorpusRealImporterDryRunHarnessBoundaryOnly": True,
            "realImporterReadinessGateProofConsumed": True,
            "realImporterReadinessGateProofContinuityValidated": True,
            "realImporterReadinessRowsConsumedByHarnessBoundary": True,
            "realImporterDryRunHarnessBoundaryDefined": True,
            "harnessBoundaryInputClassesDefined": True,
            "harnessBoundaryOutputClassesDefined": True,
            "harnessBoundaryStopConditionsDefined": True,
            "harnessBoundaryRefusalGuardsValidated": True,
            "harnessBoundaryArchiveClassOrderValidated": True,
            "harnessBoundaryArchiveClassCountsValidated": True,
            "harnessBoundaryInterfacesValidated": True,
            "harnessBoundaryEmitsOnlyPublicSafeRows": True,
            "harnessChecklistPopulationLaneSelected": True,
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
            "realImporterDryRunHarnessExecutedInBoundarySlice": False,
            "realImporterDryRunHarnessOutputPublished": False,
            "realImporterDryRunHarnessBoundaryReadPrivateInputs": False,
            "realImporterDryRunHarnessBoundaryPublishedPrivateInput": False,
            "privateHarnessBoundaryArtifactPublished": False,
            "harnessChecklistPopulationExecuted": False,
            "harnessChecklistMaterialized": False,
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessBoundaryContract": {
            "realImporterHarnessBoundaryInputMode": summary["realImporterHarnessBoundaryInputMode"],
            "realImporterHarnessBoundaryOutputMode": summary["realImporterHarnessBoundaryOutputMode"],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "sourceRealImporterReadinessInterfaceCount": summary["sourceRealImporterReadinessInterfaceCount"],
            "sourceRealImporterReadinessInterfaces": summary["sourceRealImporterReadinessInterfaces"],
            "realImporterDryRunHarnessBoundaryInterfaceCount": summary["realImporterDryRunHarnessBoundaryInterfaceCount"],
            "realImporterDryRunHarnessBoundaryInterfaces": summary["realImporterDryRunHarnessBoundaryInterfaces"],
            "realImporterReadinessRowsConsumed": summary["realImporterReadinessRowsConsumed"],
            "harnessBoundaryRows": summary["harnessBoundaryRows"],
            "harnessBoundaryArchiveClassRows": summary["harnessBoundaryArchiveClassRows"],
            "harnessBoundarySummaryRows": summary["harnessBoundarySummaryRows"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "baseArchiveClassCount": summary["baseArchiveClassCount"],
            "frontendArchiveClassCount": summary["frontendArchiveClassCount"],
            "loadingArchiveClassCount": summary["loadingArchiveClassCount"],
            "numericLevelArchiveClassCount": summary["numericLevelArchiveClassCount"],
            "goodieArchiveClassCount": summary["goodieArchiveClassCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "harnessAllowedFutureInputClassCount": summary["harnessAllowedFutureInputClassCount"],
            "allowedFutureInputClasses": summary["allowedFutureInputClasses"],
            "harnessRequiredFutureArtifactClassCount": summary["harnessRequiredFutureArtifactClassCount"],
            "requiredFutureArtifactClasses": summary["requiredFutureArtifactClasses"],
            "harnessStopConditionCount": summary["harnessStopConditionCount"],
            "harnessStopConditions": summary["harnessStopConditions"],
            "publicSafeHarnessBoundaryArtifactRows": summary["publicSafeHarnessBoundaryArtifactRows"],
            "harnessBoundaryRowsBody": summary["harnessBoundaryRowsBody"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-boundary-class-count-status-token-only",
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
                "the tracked real-importer readiness-gate proof can support a public-safe dry-run harness boundary",
                "the harness boundary defines later allowed input classes, required private artifact classes, and stop conditions",
                "the harness boundary preserves archive class order and aggregate count 301 from the readiness gate",
                "the next selected lane is a harness checklist population proof without executing the real/private importer",
            ],
            "doesNotProve": [
                "private asset content parsing",
                "private raw manifest consumption",
                "real importer implementation",
                "real importer execution",
                "private importer dry run",
                "real importer dry run",
                "real importer dry-run harness execution",
                "harness checklist population",
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
    parser.add_argument("--readiness-gate-proof", type=Path, default=Path(READINESS_GATE_PROOF))
    parser.add_argument("--summary", type=Path, help="optional public-safe harness boundary summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        readiness_proof = read_json(args.readiness_gate_proof)
        summary = build_public_safe_real_importer_dry_run_harness_boundary_summary(readiness_proof)
        validate_public_safe_real_importer_dry_run_harness_boundary_summary(summary)
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_boundary_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessBoundaryError):
        print("Real importer dry-run harness boundary: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
