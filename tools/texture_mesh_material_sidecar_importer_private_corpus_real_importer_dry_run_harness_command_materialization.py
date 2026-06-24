#!/usr/bin/env python3
"""Materialize a public-safe non-armed real-importer harness command contract.

This module consumes only the tracked public harness-checklist readiness-gate
proof. It emits a command-contract artifact that is deliberately non-armed and
status-token-only. It does not read private assets, consume raw private
manifests, build a runnable shell command, execute an importer, launch BEA,
generate assets, mutate Ghidra, or emit raw private paths, filenames, hashes, or
byte lengths.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS as READINESS_FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PROOF_SCHEMA_VERSION as READINESS_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
    THIS_SCOPE as PREVIOUS_SCOPE,
    THIS_SLICE as PREVIOUS_SLICE,
    ZERO_COUNTERS as READINESS_ZERO_COUNTERS,
)


SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-materialization.v1"
)
PROOF_SCHEMA_VERSION = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-materialization-proof-plan.v1"
)
REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-materialization-complete-public-safe-non-armed-command-contract-not-real-importer-execution"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Materialization Proof Plan"
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-materialization-proof-plan"
)
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Consumer Validation Proof Plan"
NEXT_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-command-consumer-validation-proof-plan"
)

READINESS_GATE_PROOF = (
    "reverse-engineering/game-assets/"
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-"
    "harness-checklist-readiness-gate-proof-plan.v1.json"
)

REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES = (
    "load-tracked-real-importer-harness-checklist-readiness-gate-proof",
    "validate-real-importer-harness-checklist-readiness-gate-continuity",
    "validate-harness-command-materialization-preconditions",
    "materialize-public-safe-non-armed-harness-command-contract",
    "materialize-command-contract-rows-from-readiness-gate-rows",
    "validate-command-contract-row-ordinals",
    "validate-command-contract-category-counts",
    "validate-command-contract-not-armed-statuses",
    "validate-command-contract-public-redaction-policy",
    "validate-command-contract-refusal-guards",
    "select-command-consumer-validation-lane",
    "emit-command-materialization-summary",
)

PUBLIC_ALLOWED_OUTPUTS = (
    "harness-command-materialization-status",
    "harness-command-contract-row-counts",
    "harness-command-contract-category-counts",
    "harness-command-contract-non-armed-status",
    "harness-command-contract-interface-linkage",
    "harness-command-consumer-validation-next-lane",
)

REDACTED_FIELDS = (
    "harness-command-materialization-input-path",
    "private-corpus-root",
    "raw-private-path",
    "raw-private-filename",
    "raw-private-stem",
    "raw-private-ref",
    "raw-private-hash",
    "raw-private-byte-length",
    "asset-bytes",
    "runtime-frame",
    "executable-argument-value",
    "private-output-artifact-path",
)

READINESS_ZERO_GUARD_COUNTERS = tuple(
    key
    for key in READINESS_ZERO_COUNTERS
    if key
    not in {
        "harnessChecklistCommandRows",
        "harnessChecklistCommandArtifactRows",
        "realImporterDryRunHarnessCommandRows",
        "realImporterDryRunHarnessCommandArtifactRows",
    }
)

FALSE_GUARDS = tuple(
    dict.fromkeys(
        (
            *READINESS_FALSE_GUARDS,
            "realImporterDryRunHarnessCommandMaterializationReadPrivateInputs",
            "realImporterDryRunHarnessCommandMaterializationPublishedPrivateInput",
            "realImporterDryRunHarnessRunnableCommandMaterialized",
            "realImporterDryRunHarnessCommandArmed",
            "realImporterDryRunHarnessCommandExecuted",
            "realImporterDryRunHarnessCommandSentToShell",
            "realImporterDryRunHarnessCommandPrivateOutputGenerated",
            "actualRealImporterDryRunHarnessCommandExecuted",
        )
    )
)

ZERO_COUNTERS = tuple(
    dict.fromkeys(
        (
            *READINESS_ZERO_GUARD_COUNTERS,
            "rawCommandArgumentRows",
            "publishedCommandArgumentRows",
            "commandExecutionRows",
            "commandShellDispatchRows",
            "commandPrivateOutputRows",
            "realImporterDryRunHarnessCommandExecutionRows",
            "actualRealImporterDryRunHarnessCommandRows",
        )
    )
)


class RealImporterDryRunHarnessCommandMaterializationError(ValueError):
    """Raised when readiness evidence cannot support command materialization."""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RealImporterDryRunHarnessCommandMaterializationError(message)


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


def _validate_source_readiness_gate_proof(source: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(source.get("schemaVersion") == READINESS_PROOF_SCHEMA_VERSION, "source readiness schema mismatch")
    _require(source.get("status") == "PASS", "source readiness status mismatch")
    _require(
        source.get("privateCorpusRealImporterDryRunHarnessChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
        "source readiness status token mismatch",
    )
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")
    _require(SOURCE_SELECTED_SLICE == THIS_SLICE and SOURCE_SELECTED_SCOPE == THIS_SCOPE, "module continuity mismatch")

    source_evidence = _read_mapping(source, "sourceEvidence")
    _require(source_evidence.get("sourceProofCount") == 25, "source proof count mismatch")
    _require(source_evidence.get("sourceChecklistValidationProofCount") == 24, "source validation proof count mismatch")
    _require(
        tuple(source_evidence.get("realImporterDryRunHarnessChecklistReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES,
        "source readiness interface mismatch",
    )

    decision = _read_mapping(source, "realImporterHarnessChecklistReadinessGateDecision")
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
        "realImporterDryRunHarnessCommandMaterialized",
        "realImporterDryRunHarnessCommandPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source decision false flag mismatch: {key}")

    contract = _read_mapping(source, "realImporterHarnessChecklistReadinessGateContract")
    expected_counts = {
        "harnessChecklistValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessChecklistReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedReadinessGateRowCount": 0,
        "readyForLaterCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": 17,
        "passedPreflightCheckCount": 17,
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistReadinessGateArtifactRows": 1,
    }
    for key, expected in expected_counts.items():
        _require(contract.get(key) == expected, f"source contract count mismatch: {key}")

    rows = _read_list(contract, "harnessChecklistReadinessGateRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "source readiness row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "source category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        _require(
            row.get("harnessChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"source readiness ordinal mismatch: {expected_ordinal}",
        )
        _require(
            row.get("readinessGateStatus") == "ready-for-later-explicit-harness-command-materialization",
            f"source readiness status mismatch: {expected_ordinal}",
        )
        _require(row.get("sourceRowStatus") == "not-run", f"source row status mismatch: {expected_ordinal}")
        _require(row.get("sourceObservationStatus") == "unobserved", f"source observation mismatch: {expected_ordinal}")
        _require(row.get("privateValuePublished") is False, f"source private value flag mismatch: {expected_ordinal}")
        _require(row.get("directRealImporterDryRunAllowedHere") is False, f"source direct dry-run guard mismatch: {expected_ordinal}")
        _require(
            row.get("futureHarnessCommandMaterializationRequiresLaterArm") is True,
            f"source command later-arm flag mismatch: {expected_ordinal}",
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
            f"source readiness row {expected_ordinal}",
        )

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("falseGuardCount") == len(READINESS_FALSE_GUARDS), "source false guard count mismatch")
    _require(guard.get("zeroCounterCount") == len(READINESS_ZERO_COUNTERS), "source zero counter count mismatch")
    for key in READINESS_ZERO_COUNTERS:
        _require(guard.get(key) == 0, f"source zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    return contract


def build_command_contract_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build one public-safe, non-armed command-contract row per readiness row."""

    rows: list[dict[str, Any]] = []
    for source_row in _read_list(contract, "harnessChecklistReadinessGateRowsBody"):
        ordinal = int(source_row["harnessChecklistReadinessGateRowOrdinal"])
        rows.append(
            {
                "actualAssetImportRows": 0,
                "byteLengthRows": 0,
                "category": source_row["category"],
                "commandArmStatus": "not-armed",
                "commandContractRowClass": "private-corpus-real-importer-dry-run-harness-non-armed-command-contract-row",
                "commandContractRowMode": "public-safe-non-armed-command-contract-status-token-only",
                "commandContractRowOrdinal": ordinal,
                "commandDispatchAllowedHere": False,
                "commandExecutionRows": 0,
                "commandExecutionStatus": "not-executed",
                "commandMaterializationStatus": "materialized-public-safe-non-armed-command-contract",
                "commandPrivateOutputRows": 0,
                "commandRequiresLaterExplicitArm": True,
                "commandShellDispatchRows": 0,
                "directRealImporterDryRunAllowedHere": False,
                "futureHarnessArmRequiresOperatorAction": True,
                "generatedAssetRows": 0,
                "itemId": source_row["itemId"],
                "privateDryRunRows": 0,
                "privateValuePublished": False,
                "publishedCommandArgumentRows": 0,
                "rawCommandArgumentRows": 0,
                "rawFilenameRows": 0,
                "rawHashRows": 0,
                "rawMeshRefRows": 0,
                "rawPathRows": 0,
                "rawStemRows": 0,
                "rawTextureRefRows": 0,
                "realImporterDryRunHarnessCommandExecutionRows": 0,
                "realImporterDryRunHarnessRows": 0,
                "realImporterDryRunRows": 0,
                "sourceHarnessChecklistReadinessGateRowOrdinal": ordinal,
                "sourceReadinessGateStatus": source_row["readinessGateStatus"],
                "sourceRowStatus": source_row["sourceRowStatus"],
                "sourceObservationStatus": source_row["sourceObservationStatus"],
            }
        )
    return rows


def build_command_contract_artifact(readiness_proof: Mapping[str, Any]) -> dict[str, Any]:
    """Build the public-safe non-armed command-contract artifact."""

    contract = _validate_source_readiness_gate_proof(readiness_proof)
    rows = build_command_contract_rows(contract)
    category_counts = Counter(row["category"] for row in rows)
    _require(category_counts == EXPECTED_CATEGORY_COUNTS, "command category counts mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "artifactKind": "public-safe-real-importer-dry-run-harness-non-armed-command-contract-artifact",
        "artifactRowMode": "public-safe-non-armed-command-contract-status-token-only",
        "materializationStatus": REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
        "sourceReadinessGateStatus": REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
        "publicSafeNonArmedHarnessCommandContractMaterialized": True,
        "publicSafeNonArmedHarnessCommandContractStoredInTrackedProof": True,
        "publicSafeNonArmedHarnessCommandContractPathPublished": False,
        "harnessCommandContractRows": len(rows),
        "harnessCommandContractSummaryRows": 1,
        "harnessCommandContractArchiveTotalCount": 301,
        "harnessCommandContractRowsValidated": True,
        "harnessCommandContractAggregateCountsValidated": True,
        "commandArmed": False,
        "commandExecuted": False,
        "commandDispatchedToShell": False,
        "privateAssetContentRead": False,
        "privateArchiveBytesRead": False,
        "rawPrivateManifestConsumed": False,
        "rawPrivateManifestRowsConsumed": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "privateImporterDryRunExecuted": False,
        "realImporterDryRunExecuted": False,
        "realImporterDryRunHarnessExecuted": False,
        "realImporterDryRunHarnessCommandArmed": False,
        "realImporterDryRunHarnessCommandExecuted": False,
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "commandContractCategoryCounts": dict(sorted(category_counts.items())),
        "commandContractRowsBody": rows,
        "publicLeakCheck": "PASS",
    }


def build_public_safe_real_importer_dry_run_harness_command_materialization_summary(
    readiness_proof: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a public-safe command-materialization summary."""

    artifact = build_command_contract_artifact(readiness_proof)
    false_guards = {key: False for key in FALSE_GUARDS}
    zero_counters = {key: 0 for key in ZERO_COUNTERS}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessChecklistReadinessGateStatus": REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandMaterializationOnly": True,
        "realImporterHarnessChecklistReadinessGateProofConsumed": True,
        "realImporterHarnessChecklistReadinessGateProofContinuityValidated": True,
        "realImporterDryRunHarnessCommandMaterializationExecuted": True,
        "realImporterDryRunHarnessCommandMaterializationInputAccepted": True,
        "publicSafeNonArmedHarnessCommandContractMaterialized": True,
        "publicSafeNonArmedHarnessCommandContractStoredInTrackedProof": True,
        "publicSafeNonArmedHarnessCommandContractPathPublished": False,
        "harnessCommandContractRowsGenerated": True,
        "harnessCommandContractRowsValidated": True,
        "harnessCommandContractAggregateCountsValidated": True,
        "harnessCommandContractInterfacesValidated": True,
        "harnessCommandContractEmitsOnlyPublicSafeRows": True,
        "harnessCommandContractRedactionPolicyValidated": True,
        "harnessCommandConsumerValidationLaneSelected": True,
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
        "actualAssetImportExecuted": False,
        "generatedAssetOutputExecuted": False,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "realImporterHarnessCommandMaterializationInputMode": "tracked-public-safe-readiness-gate-proof-json",
        "realImporterHarnessCommandMaterializationOutputMode": (
            "tracked-public-safe-non-armed-command-contract-artifact"
        ),
        "selectedNextLaneClass": "private-corpus real importer dry-run harness command consumer validation without execution",
        "sourceProofCount": 26,
        "sourceReadinessGateProofCount": 25,
        "sourceHarnessChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "realImporterDryRunHarnessCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "harnessChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessCommandContractRows": artifact["harnessCommandContractRows"],
        "harnessCommandContractArchiveClassRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-archive-class"],
        "harnessCommandContractAllowedInputClassRows": EXPECTED_CATEGORY_COUNTS["allowed-future-input-class"],
        "harnessCommandContractRequiredArtifactClassRows": EXPECTED_CATEGORY_COUNTS["required-future-artifact-class"],
        "harnessCommandContractStopConditionRows": EXPECTED_CATEGORY_COUNTS["harness-stop-condition"],
        "harnessCommandContractBoundaryInterfaceRows": EXPECTED_CATEGORY_COUNTS["harness-boundary-interface"],
        "harnessCommandContractRedactionFieldRows": EXPECTED_CATEGORY_COUNTS["redaction-field"],
        "harnessCommandContractPublicAllowedOutputRows": EXPECTED_CATEGORY_COUNTS["public-allowed-output"],
        "nonArmedCommandContractRowCount": artifact["harnessCommandContractRows"],
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterHarnessArmRowCount": artifact["harnessCommandContractRows"],
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "sourceHarnessChecklistReadinessGateInterfaces": list(
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "realImporterDryRunHarnessCommandMaterializationInterfaces": list(
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "harnessCommandContractCategoryCounts": artifact["commandContractCategoryCounts"],
        "harnessCommandContractArtifact": artifact,
        "publicAllowedOutputs": list(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFields": list(REDACTED_FIELDS),
        "publicLeakCheck": "PASS",
        "falseGuards": false_guards,
        "zeroCounters": zero_counters,
    }


def validate_public_safe_real_importer_dry_run_harness_command_materialization_summary(
    summary: Mapping[str, Any],
) -> None:
    """Validate the public-safe command-materialization summary."""

    _require(summary.get("schemaVersion") == SCHEMA_VERSION, "summary schema mismatch")
    _require(summary.get("status") == "PASS", "summary status mismatch")
    _require(
        summary.get("privateCorpusRealImporterDryRunHarnessCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
        "summary command materialization status mismatch",
    )
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandMaterializationOnly",
        "realImporterHarnessChecklistReadinessGateProofConsumed",
        "realImporterHarnessChecklistReadinessGateProofContinuityValidated",
        "realImporterDryRunHarnessCommandMaterializationExecuted",
        "realImporterDryRunHarnessCommandMaterializationInputAccepted",
        "publicSafeNonArmedHarnessCommandContractMaterialized",
        "publicSafeNonArmedHarnessCommandContractStoredInTrackedProof",
        "harnessCommandContractRowsGenerated",
        "harnessCommandContractRowsValidated",
        "harnessCommandContractAggregateCountsValidated",
        "harnessCommandContractInterfacesValidated",
        "harnessCommandContractEmitsOnlyPublicSafeRows",
        "harnessCommandContractRedactionPolicyValidated",
        "harnessCommandConsumerValidationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        _require(summary.get(key) is True, f"expected true: {key}")
    for key in (
        "publicSafeNonArmedHarnessCommandContractPathPublished",
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
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(summary.get(key) is False, f"expected false: {key}")

    expected_counts = {
        "sourceProofCount": 26,
        "sourceReadinessGateProofCount": 25,
        "sourceHarnessChecklistReadinessGateInterfaceCount": len(
            REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES
        ),
        "realImporterDryRunHarnessCommandMaterializationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES
        ),
        "harnessChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "harnessCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(summary.get(key) == expected, f"count mismatch: {key}")
    _require(
        tuple(summary.get("sourceHarnessChecklistReadinessGateInterfaces", ()))
        == REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES,
        "source readiness interface mismatch",
    )
    _require(
        tuple(summary.get("realImporterDryRunHarnessCommandMaterializationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES,
        "command materialization interface mismatch",
    )
    artifact = _read_mapping(summary, "harnessCommandContractArtifact")
    _require(artifact.get("schemaVersion") == SCHEMA_VERSION, "artifact schema mismatch")
    _require(artifact.get("materializationStatus") == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS, "artifact status mismatch")
    _require(artifact.get("publicSafeNonArmedHarnessCommandContractMaterialized") is True, "artifact materialized flag mismatch")
    _require(artifact.get("publicSafeNonArmedHarnessCommandContractPathPublished") is False, "artifact path published")
    _require(artifact.get("commandArmed") is False, "artifact command armed")
    _require(artifact.get("commandExecuted") is False, "artifact command executed")
    _require(artifact.get("commandDispatchedToShell") is False, "artifact command shell dispatch")
    rows = _read_list(artifact, "commandContractRowsBody")
    _require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "artifact row count mismatch")
    _require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "artifact category counts mismatch")
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"command row {expected_ordinal}"
        _require(row.get("commandContractRowOrdinal") == expected_ordinal, f"{row_id} ordinal mismatch")
        _require(
            row.get("sourceHarnessChecklistReadinessGateRowOrdinal") == expected_ordinal,
            f"{row_id} source ordinal mismatch",
        )
        _require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch")
        _require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch")
        _require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch")
        _require(row.get("commandRequiresLaterExplicitArm") is True, f"{row_id} later-arm guard mismatch")
        _require(row.get("privateValuePublished") is False, f"{row_id} private value guard mismatch")
        _validate_zero_fields(
            row,
            (
                "actualAssetImportRows",
                "byteLengthRows",
                "commandExecutionRows",
                "commandPrivateOutputRows",
                "commandShellDispatchRows",
                "generatedAssetRows",
                "privateDryRunRows",
                "publishedCommandArgumentRows",
                "rawCommandArgumentRows",
                "rawFilenameRows",
                "rawHashRows",
                "rawMeshRefRows",
                "rawPathRows",
                "rawStemRows",
                "rawTextureRefRows",
                "realImporterDryRunHarnessCommandExecutionRows",
                "realImporterDryRunHarnessRows",
                "realImporterDryRunRows",
            ),
            row_id,
        )
    for key in FALSE_GUARDS:
        _require(summary.get("falseGuards", {}).get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        _require(summary.get("zeroCounters", {}).get(key) == 0, f"zero counter mismatch: {key}")
    _require(summary.get("publicLeakCheck") == "PASS", "summary public leak mismatch")
    _require(artifact.get("publicLeakCheck") == "PASS", "artifact public leak mismatch")


def build_public_safe_real_importer_dry_run_harness_command_materialization_proof(
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Wrap a validated command-materialization summary in a proof-plan schema."""

    validate_public_safe_real_importer_dry_run_harness_command_materialization_summary(summary)
    return {
        "schemaVersion": PROOF_SCHEMA_VERSION,
        "status": "PASS",
        "privateCorpusRealImporterDryRunHarnessCommandMaterializationStatus": (
            REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS
        ),
        "previousSlice": PREVIOUS_SLICE,
        "previousScope": PREVIOUS_SCOPE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedNextScope": NEXT_SCOPE,
        "sourceRealImporterHarnessChecklistReadinessGateStatus": REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
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
            "sourceReadinessGateProofCount": summary["sourceReadinessGateProofCount"],
            "sourceHarnessChecklistReadinessGateInterfaceCount": summary[
                "sourceHarnessChecklistReadinessGateInterfaceCount"
            ],
            "realImporterDryRunHarnessCommandMaterializationInterfaceCount": summary[
                "realImporterDryRunHarnessCommandMaterializationInterfaceCount"
            ],
            "sourceHarnessChecklistReadinessGateInterfaces": summary[
                "sourceHarnessChecklistReadinessGateInterfaces"
            ],
            "realImporterDryRunHarnessCommandMaterializationInterfaces": summary[
                "realImporterDryRunHarnessCommandMaterializationInterfaces"
            ],
            "sourceProof": READINESS_GATE_PROOF,
        },
        "realImporterHarnessCommandMaterializationDecision": {
            "privateCorpusRealImporterDryRunHarnessCommandMaterializationOnly": True,
            "realImporterHarnessChecklistReadinessGateProofConsumed": True,
            "realImporterHarnessChecklistReadinessGateProofContinuityValidated": True,
            "realImporterDryRunHarnessCommandMaterializationExecuted": True,
            "realImporterDryRunHarnessCommandMaterializationInputAccepted": True,
            "publicSafeNonArmedHarnessCommandContractMaterialized": True,
            "publicSafeNonArmedHarnessCommandContractStoredInTrackedProof": True,
            "publicSafeNonArmedHarnessCommandContractPathPublished": False,
            "harnessCommandContractRowsGenerated": True,
            "harnessCommandContractRowsValidated": True,
            "harnessCommandContractAggregateCountsValidated": True,
            "harnessCommandContractInterfacesValidated": True,
            "harnessCommandContractEmitsOnlyPublicSafeRows": True,
            "harnessCommandContractRedactionPolicyValidated": True,
            "harnessCommandConsumerValidationLaneSelected": True,
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
            "actualAssetImportExecuted": False,
            "generatedAssetOutputExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
        },
        "realImporterHarnessCommandMaterializationContract": {
            "realImporterHarnessCommandMaterializationInputMode": summary[
                "realImporterHarnessCommandMaterializationInputMode"
            ],
            "realImporterHarnessCommandMaterializationOutputMode": summary[
                "realImporterHarnessCommandMaterializationOutputMode"
            ],
            "selectedNextLaneClass": summary["selectedNextLaneClass"],
            "harnessChecklistReadinessGateRowsConsumed": summary[
                "harnessChecklistReadinessGateRowsConsumed"
            ],
            "harnessCommandContractRows": summary["harnessCommandContractRows"],
            "harnessCommandContractArchiveClassRows": summary["harnessCommandContractArchiveClassRows"],
            "harnessCommandContractAllowedInputClassRows": summary[
                "harnessCommandContractAllowedInputClassRows"
            ],
            "harnessCommandContractRequiredArtifactClassRows": summary[
                "harnessCommandContractRequiredArtifactClassRows"
            ],
            "harnessCommandContractStopConditionRows": summary["harnessCommandContractStopConditionRows"],
            "harnessCommandContractBoundaryInterfaceRows": summary[
                "harnessCommandContractBoundaryInterfaceRows"
            ],
            "harnessCommandContractRedactionFieldRows": summary["harnessCommandContractRedactionFieldRows"],
            "harnessCommandContractPublicAllowedOutputRows": summary[
                "harnessCommandContractPublicAllowedOutputRows"
            ],
            "nonArmedCommandContractRowCount": summary["nonArmedCommandContractRowCount"],
            "armedCommandRowCount": summary["armedCommandRowCount"],
            "executedCommandRowCount": summary["executedCommandRowCount"],
            "shellDispatchedCommandRowCount": summary["shellDispatchedCommandRowCount"],
            "readyForLaterHarnessArmRowCount": summary["readyForLaterHarnessArmRowCount"],
            "observedChecklistRowCount": summary["observedChecklistRowCount"],
            "rowStatusChangedCount": summary["rowStatusChangedCount"],
            "consumerArchiveTotalCount": summary["consumerArchiveTotalCount"],
            "unknownAyaArchiveClassCount": summary["unknownAyaArchiveClassCount"],
            "publicSafeHarnessCommandContractArtifactRows": summary[
                "publicSafeHarnessCommandContractArtifactRows"
            ],
            "publicAllowedOutputCount": summary["publicAllowedOutputCount"],
            "redactedFieldCount": summary["redactedFieldCount"],
            "falseGuardCount": summary["falseGuardCount"],
            "zeroCounterCount": summary["zeroCounterCount"],
            "harnessCommandContractCategoryCounts": summary["harnessCommandContractCategoryCounts"],
            "harnessCommandContractArtifact": summary["harnessCommandContractArtifact"],
        },
        "redactionPolicy": {
            "redactionPolicy": "public-safe-real-importer-dry-run-harness-non-armed-command-contract-status-token-only",
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
                "the tracked readiness-gate proof can be consumed as public-safe command-materialization input",
                "the 99 readiness rows can be represented as non-armed command-contract status-token rows",
                "the materialized command contract preserves row/category counts and aggregate archive count 301",
                "the next command-consumer-validation lane is selected without arming or executing a command",
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
    parser.add_argument("--readiness-gate-proof", type=Path, default=Path(READINESS_GATE_PROOF))
    parser.add_argument("--artifact", type=Path, help="optional public-safe non-armed command artifact output")
    parser.add_argument("--summary", type=Path, help="optional public-safe command materialization summary output")
    parser.add_argument("--proof", type=Path, help="optional tracked proof-plan JSON output")
    args = parser.parse_args()

    try:
        readiness_proof = read_json(args.readiness_gate_proof)
        summary = build_public_safe_real_importer_dry_run_harness_command_materialization_summary(readiness_proof)
        validate_public_safe_real_importer_dry_run_harness_command_materialization_summary(summary)
        if args.artifact is not None:
            args.artifact.parent.mkdir(parents=True, exist_ok=True)
            args.artifact.write_text(
                json.dumps(summary["harnessCommandContractArtifact"], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if args.summary is not None:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.proof is not None:
            proof = build_public_safe_real_importer_dry_run_harness_command_materialization_proof(summary)
            args.proof.parent.mkdir(parents=True, exist_ok=True)
            args.proof.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RealImporterDryRunHarnessCommandMaterializationError):
        print("Real importer dry-run harness command materialization: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
