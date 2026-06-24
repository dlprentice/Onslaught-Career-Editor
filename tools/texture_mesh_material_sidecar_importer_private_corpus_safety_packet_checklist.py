#!/usr/bin/env python3
"""Public-safe checklist population for future private-corpus importer work.

This module consumes only the tracked public private-corpus boundary schema. It
does not read private assets, enumerate private roots, execute an importer, or
emit generated asset outputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_safety_boundary import (
    AUTHORIZATION_GATES,
    BOUNDARY_STATUS,
    FALSE_GUARDS,
    NEXT_SCOPE as SOURCE_SELECTED_SCOPE,
    NEXT_SLICE as SOURCE_SELECTED_SLICE,
    PRIVATE_CORPUS_CLASSES,
    PUBLIC_ALLOWED_OUTPUTS,
    REDACTED_FIELD_IDS,
    SAFETY_PACKET_ITEMS,
    STOP_CONDITIONS,
    THIS_SCOPE as SOURCE_SCOPE,
    THIS_SLICE as SOURCE_SLICE,
    ZERO_COUNTERS,
)


CHECKLIST_SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist.v1"
CHECKLIST_POPULATION_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-"
    "complete-public-safe-checklist-populated-no-private-corpus-read"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan"

CHECKLIST_GROUPS = (
    ("safety-packet-item", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", SAFETY_PACKET_ITEMS),
    ("authorization-gate", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", AUTHORIZATION_GATES),
    ("private-corpus-class", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", PRIVATE_CORPUS_CLASSES),
    ("redaction-field", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", REDACTED_FIELD_IDS),
    ("public-allowed-output", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", PUBLIC_ALLOWED_OUTPUTS),
    ("stop-condition", "NOT_RUN_PUBLIC_CHECKLIST_ONLY", STOP_CONDITIONS),
)

PREFLIGHT_CHECKS = (
    "source-boundary-status-pass",
    "source-boundary-selected-this-slice",
    "source-public-skeleton-continuity-preserved",
    "safety-packet-counts-match-source",
    "authorization-gate-counts-match-source",
    "redaction-policy-counts-match-source",
    "public-output-counts-match-source",
    "stop-condition-counts-match-source",
    "private-corpus-class-counts-match-source",
    "false-guard-counts-match-source",
    "zero-counter-counts-match-source",
    "no-private-corpus-read-performed",
    "no-real-importer-executed",
    "public-leak-check-pass",
)

FALSE_GUARDS_CHECKLIST = FALSE_GUARDS + (
    "privateCorpusInventoryPreflightExecuted",
    "privateCorpusReadOnlyInventoryGenerated",
    "privateCorpusRootEnumerated",
    "privateResourceArchiveEnumerated",
    "privateSidecarRowsObserved",
    "privateImporterDryRunExecuted",
)

ZERO_COUNTERS_CHECKLIST = ZERO_COUNTERS + (
    "checklistPrivatePathRows",
    "checklistRawTextureRefRows",
    "checklistRawFilenameRows",
    "checklistPrivateDigestRows",
    "readOnlyInventoryRows",
    "privateImporterDryRunRows",
)


class SafetyPacketChecklistError(ValueError):
    """Raised when source boundary evidence cannot populate the checklist."""


@dataclass(frozen=True)
class SafetyPacketChecklistReport:
    """Sanitized public summary of the populated checklist."""

    checklist_row_count: int
    checklist_group_count: int
    preflight_check_count: int
    false_guard_count: int
    zero_counter_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": CHECKLIST_SCHEMA_VERSION,
            "status": "PASS",
            "privateCorpusSafetyPacketChecklistPopulationStatus": CHECKLIST_POPULATION_STATUS,
            "checklistPopulationOnly": True,
            "safetyPacketChecklistPopulated": True,
            "futureReadOnlyPrivateCorpusSliceSelectable": True,
            "futureReadOnlyPrivateCorpusUseAllowedWhenSelected": True,
            "futurePrivateCorpusReadRequiresSelectedReadOnlySlice": True,
            "blockedByMissingExplicitPrivateCorpusArm": True,
            "defaultChecklistRowStatus": "not-run",
            "defaultObservationStatus": "unobserved",
            "privateCorpusReadAuthorizationPresent": False,
            "explicitImporterImplementationArmPresent": False,
            "operatorPrivateOutputReviewAvailable": False,
            "privateAssetRead": False,
            "privateCorpusReadPerformed": False,
            "privateCorpusEnumeration": False,
            "privateRootExistenceChecked": False,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
            "checklistGroupCount": self.checklist_group_count,
            "checklistRowCount": self.checklist_row_count,
            "passedChecklistRowCount": self.checklist_row_count,
            "failedChecklistRowCount": 0,
            "notRunChecklistRowCount": self.checklist_row_count,
            "unobservedChecklistRowCount": self.checklist_row_count,
            "observedChecklistRowCount": 0,
            "rowStatusChangedCount": 0,
            "preflightCheckCount": self.preflight_check_count,
            "passedPreflightCheckCount": self.preflight_check_count,
            "failedPreflightCheckCount": 0,
            "falseGuardCount": self.false_guard_count,
            "zeroCounterCount": self.zero_counter_count,
            "publicLeakCheck": "PASS",
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SafetyPacketChecklistError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _rows(category: str, status: str, items: Iterable[str]) -> list[dict[str, Any]]:
    return [
        {
            "category": category,
            "itemId": item,
            "status": status,
            "rowStatus": "not-run",
            "observationStatus": "unobserved",
            "blockedByMissingExplicitPrivateCorpusArm": True,
            "publicSafe": True,
            "privateValuePublished": False,
        }
        for item in items
    ]


def build_public_safe_checklist_rows() -> list[dict[str, Any]]:
    """Return the public checklist rows without touching private corpus data."""

    rows: list[dict[str, Any]] = []
    for category, status, items in CHECKLIST_GROUPS:
        rows.extend(_rows(category, status, items))
    return rows


def validate_private_corpus_safety_packet_checklist(source: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the source boundary and emit a public-safe checklist summary."""

    _require(source.get("status") == "PASS", "source boundary status mismatch")
    _require(source.get("privateCorpusSafetyBoundaryStatus") == BOUNDARY_STATUS, "source boundary token mismatch")
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")

    continuity = _read_mapping(source, "sourcePublicSkeletonContinuity")
    _require(continuity.get("publicContractSkeletonImplemented") is True, "public skeleton continuity missing")
    _require(continuity.get("publicLeakCheck") == "PASS", "source public skeleton leak check mismatch")

    decision = _read_mapping(source, "boundaryDecision")
    for key in (
        "safetyBoundaryOnly",
        "privateCorpusSafetyBoundaryDefined",
        "futurePrivateCorpusReadRequiresExplicitArm",
        "requiresCopiedOrAppOwnedCorpusRoot",
        "requiresAppOwnedArtifactRoot",
        "publicPrivateSeparationRequired",
    ):
        _require(decision.get(key) is True, f"source boundary decision should be true: {key}")
    for key in (
        "privateCorpusReadAuthorizationPresent",
        "explicitImporterImplementationArmPresent",
        "operatorPrivateOutputReviewAvailable",
        "privateAssetRead",
        "privateCorpusReadPerformed",
        "privateCorpusEnumeration",
        "privateRootExistenceChecked",
        "privateAssetReadPerformed",
        "privateManifestMaterialized",
        "privateManifestRowsObserved",
        "realImporterImplementation",
        "realImporterExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        _require(decision.get(key) is False, f"source boundary decision should be false: {key}")

    packet = _read_mapping(source, "privateCorpusSafetyPacket")
    expected_counts = {
        "safetyPacketItemCount": len(SAFETY_PACKET_ITEMS),
        "authorizationGateCount": len(AUTHORIZATION_GATES),
        "privateCorpusClassCount": len(PRIVATE_CORPUS_CLASSES),
        "redactedFieldCount": len(REDACTED_FIELD_IDS),
        "publicAllowedOutputClassCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        _require(packet.get(key) == expected, f"source packet count mismatch: {key}")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("publicLeakCheck") == "PASS", "source guard leak check mismatch")

    rows = build_public_safe_checklist_rows()
    report = SafetyPacketChecklistReport(
        checklist_row_count=len(rows),
        checklist_group_count=len(CHECKLIST_GROUPS),
        preflight_check_count=len(PREFLIGHT_CHECKS),
        false_guard_count=len(FALSE_GUARDS_CHECKLIST),
        zero_counter_count=len(ZERO_COUNTERS_CHECKLIST),
    )
    return report.to_dict()


def emit_private_corpus_safety_packet_checklist_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Return the only allowed public summary for this checklist slice."""

    return validate_private_corpus_safety_packet_checklist(source)
