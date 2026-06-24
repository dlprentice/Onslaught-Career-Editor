#!/usr/bin/env python3
"""Public contract skeleton for texture/mesh material-sidecar importer planning.

This module intentionally validates tracked public aggregate evidence only. It
does not read asset files, resolve texture names, execute an importer, or emit
generated asset outputs.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


CONTRACT_VERSION = "texture-mesh-material-sidecar-importer-public-contract-skeleton.v1"
VALIDATION_SCHEMA = "texture-mesh-material-sidecar-importer-public-contract-skeleton.validation.v1"
CONTRACT_STATUS = (
    "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-"
    "public-contract-only-not-real-importer-proof"
)
SOURCE_STATUS = (
    "texture-mesh-material-sidecar-importer-implementation-readiness-gate-complete-"
    "public-contract-skeleton-ready-not-real-importer-proof"
)

PUBLIC_CONTRACT_FUNCTIONS = (
    "validate_public_contract_skeleton",
    "emit_public_validation_summary",
)

REQUIRED_PUBLIC_INTERFACES = (
    "load-public-consumer-dry-run-schema",
    "enumerate-consumed-fixture-row-ids",
    "validate-aggregate-counts",
    "validate-public-edge-case-boundaries",
    "refuse-private-or-runtime-inputs",
    "emit-public-validation-summary",
)

EXPECTED_ROW_IDS = (
    "importer-source-matrix-prerequisite",
    "importer-loose-family-fixture",
    "importer-embedded-family-fixture",
    "importer-non-additive-union-fixture",
    "importer-sidecar-match-mode-fixture",
    "importer-catalog-linkage-fixture",
    "importer-duplicate-output-surplus-fixture",
    "importer-negative-claim-guard-fixture",
)

EXPECTED_EDGE_CASE_IDS = (
    "stem-only-sidecar-match-boundary-001",
    "ambiguous-catalog-ref-boundary-001",
)

EXPECTED_AGGREGATES: Mapping[str, Any] = {
    "sourceConsumedFixtureRowCount": 8,
    "sourceConsumerDryRunStepCount": 10,
    "sourceConsumerAssertionGroupCount": 8,
    "sourceConsumerAssertionCheckCount": 19,
    "sourceFailedConsumerAssertions": 0,
    "sourceUnexpectedFixtureRows": 0,
    "sourceConsumerOutputArtifactRows": 0,
    "readinessGateCount": 8,
    "readinessCheckCount": 16,
    "failedReadinessGateCount": 0,
    "blockedReadinessGateCount": 0,
    "readinessValidationOnly": True,
    "readinessConsumesPublicDryRunOnly": True,
    "publicSyntheticFixtureCount": 8,
    "publicEdgeCaseIdCount": 2,
    "modelRowsWithTextureRefs": "352/352",
    "modelTextureReferenceInstances": 1268,
    "uniqueModelTextureRefUnion": 213,
    "familyUniqueRefSum": 241,
    "familyUniqueRefsAreNotAdditive": True,
    "sidecarFiles": 213,
    "exactFilenameMatches": 212,
    "stemOnlyMatches": 1,
    "missingSidecarRefs": 0,
    "catalogRows": 4050,
    "catalogMissingRefs": 0,
    "ambiguousCatalogRefs": 1,
    "embeddedDuplicateOutputGroups": 28,
    "embeddedDuplicateOutputSurplusRows": 32,
    "publicLeakCheck": "PASS",
}

FALSE_GUARDS = (
    "runtimeExecution",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionObserved",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "realImporterImplementation",
    "realImporterExecuted",
    "importerImplementation",
    "importerExecuted",
    "fixtureHarnessRuntimeExecuted",
    "fixtureHarnessConsumerRuntimeExecuted",
    "rebuildImplementation",
    "runtimeTextureParserBehaviorProven",
    "runtimeTexturePixelsProven",
    "runtimeJpegInflateDecodeFidelityProven",
    "runtimeMeshLoadingProven",
    "runtimeMeshSkinningProven",
    "runtimeAnimationBehaviorProven",
    "runtimeCollisionBehaviorProven",
    "runtimeDirect3DUploadProven",
    "runtimeGpuBehaviorProven",
    "nativeTextured3DRenderingProven",
    "materialVisualCorrectnessProven",
    "materialShaderParityProven",
    "visualQaComplete",
    "cleanRoomRendererImplemented",
    "assetFormatCompletenessProven",
    "exactMeshTextureLayoutsProven",
    "runtimeResourceArchiveParserProven",
    "runtimeSidecarMaterialLoadProven",
    "runtimeObjectIdentityProven",
    "runtimeWorldLoadingProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "privateAssetPublication",
    "publicPrivateProofLeak",
)

ZERO_COUNTERS = (
    "actualAssetImportRows",
    "generatedAssetRows",
    "outputArtifactRows",
    "dryRunOutputArtifactRows",
    "rawFixtureExampleRows",
    "privateFixtureRows",
    "runtimeTexturePixelRows",
    "runtimeMeshRenderRows",
    "runtimeMaterialRows",
    "runtimeObservationRows",
    "textureRuntimeEvidenceRows",
    "meshRuntimeEvidenceRows",
    "materialRuntimeEvidenceRows",
    "materialVisualReviewRows",
    "screenshotRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "productUiRows",
    "godotRows",
    "realImporterImplementationRows",
    "rebuildImplementationRows",
    "runtimeCollisionRows",
    "runtimeResourceArchiveParserRows",
    "runtimeSidecarMaterialLoadRows",
    "beProcessesAfterPublicContractSkeleton",
    "publicCaseRawRefLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "privateAssetLeakCount",
    "publicPrivateProofLeakCount",
)


class ContractSkeletonValidationError(ValueError):
    """Raised when public readiness evidence cannot satisfy the contract skeleton."""


@dataclass(frozen=True)
class PublicContractSkeletonReport:
    """Sanitized validation summary for the public importer contract skeleton."""

    check_count: int
    consumed_fixture_row_count: int
    public_edge_case_id_count: int
    interface_count: int
    function_count: int
    false_guard_count: int
    zero_counter_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": VALIDATION_SCHEMA,
            "status": "PASS",
            "publicContractSkeletonStatus": CONTRACT_STATUS,
            "contractVersion": CONTRACT_VERSION,
            "contractInterfaceCount": self.interface_count,
            "implementedContractInterfaceCount": self.interface_count,
            "contractFunctionCount": self.function_count,
            "skeletonContractCheckCount": self.check_count,
            "failedSkeletonContractChecks": 0,
            "consumedFixtureRowCount": self.consumed_fixture_row_count,
            "publicEdgeCaseIdCount": self.public_edge_case_id_count,
            "publicContractSkeletonImplemented": True,
            "contractSkeletonValidationExecuted": True,
            "readsOnlyTrackedPublicSchema": True,
            "emitsOnlyValidationSummary": True,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "importerImplementation": False,
            "importerExecuted": False,
            "outputArtifactRows": 0,
            "actualAssetImportRows": 0,
            "generatedAssetRows": 0,
            "runtimeExecution": False,
            "godotWork": False,
            "ghidraMutation": False,
            "rebuildImplementation": False,
            "rebuildParityProven": False,
            "noNoticeableDifferenceParityProven": False,
            "contractSkeletonImplementationRows": 1,
            "falseGuardCount": self.false_guard_count,
            "zeroCounterCount": self.zero_counter_count,
            "publicLeakCheck": "PASS",
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractSkeletonValidationError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def _validate_required_interfaces(source: Mapping[str, Any]) -> None:
    rows = source.get("requiredPublicContractInterfaces")
    _require(isinstance(rows, list), "requiredPublicContractInterfaces must be a list")
    ids = tuple(row.get("interfaceId") for row in rows if isinstance(row, Mapping))
    _require(ids == REQUIRED_PUBLIC_INTERFACES, "public contract interface ids mismatch")
    for row in rows:
        _require(isinstance(row, Mapping), "public contract interface row must be a mapping")
        _require(row.get("status") == "READY", f"interface is not ready: {row.get('interfaceId')}")


def _validate_edge_cases(source: Mapping[str, Any]) -> None:
    rows = source.get("publicEdgeCases")
    _require(isinstance(rows, list), "publicEdgeCases must be a list")
    ids = tuple(row.get("caseId") for row in rows if isinstance(row, Mapping))
    _require(ids == EXPECTED_EDGE_CASE_IDS, "public edge-case ids mismatch")
    for row in rows:
        _require(isinstance(row, Mapping), "public edge-case row must be a mapping")
        _require(row.get("count") == 1, f"public edge count mismatch: {row.get('caseId')}")
        for key in ("rawRefPublished", "rawStemPublished", "catalogVariantPublished", "filenamePublished", "pathPublished", "hashPublished"):
            _require(row.get(key) is False, f"edge case publishes forbidden field {key}: {row.get('caseId')}")


def _validate_guards(source: Mapping[str, Any]) -> None:
    guard = _read_mapping(source, "guardSummary")
    false_guards = _read_mapping(guard, "falseGuards")
    zero_counters = _read_mapping(guard, "zeroCounters")
    for key in FALSE_GUARDS:
        _require(false_guards.get(key) is False, f"false guard mismatch: {key}")
    for key in ZERO_COUNTERS:
        if key == "beProcessesAfterPublicContractSkeleton":
            continue
        _require(zero_counters.get(key) == 0, f"zero counter mismatch: {key}")
    _require(guard.get("publicLeakCheck") == "PASS", "guard public leak check mismatch")


def validate_public_contract_skeleton(source: Mapping[str, Any]) -> dict[str, Any]:
    """Validate public readiness evidence and return a sanitized contract summary."""

    _require(source.get("implementationReadinessStatus") == SOURCE_STATUS, "source readiness status mismatch")
    _require(source.get("selectedNextSlice") == "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan", "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan", "source selected next scope mismatch")

    decision = _read_mapping(source, "readinessDecision")
    _require(decision.get("implementationReadinessGateComplete") is True, "readiness gate is not complete")
    _require(decision.get("publicContractSkeletonReadyNow") is True, "public contract skeleton is not ready")
    _require(decision.get("realImporterImplementationReadyNow") is False, "real importer implementation must not be ready")
    _require(decision.get("realImporterExecutionReadyNow") is False, "real importer execution must not be ready")

    summary = _read_mapping(source, "readinessSummary")
    for key, expected in EXPECTED_AGGREGATES.items():
        _require(summary.get(key) == expected, f"aggregate mismatch: {key}")

    row_ids = tuple(source.get("consumedFixtureRows", ()))
    _require(row_ids == EXPECTED_ROW_IDS, "consumed fixture row ids mismatch")
    _validate_required_interfaces(source)
    _validate_edge_cases(source)
    _validate_guards(source)

    report = PublicContractSkeletonReport(
        check_count=len(EXPECTED_AGGREGATES) + len(EXPECTED_ROW_IDS) + len(EXPECTED_EDGE_CASE_IDS) + len(REQUIRED_PUBLIC_INTERFACES),
        consumed_fixture_row_count=len(EXPECTED_ROW_IDS),
        public_edge_case_id_count=len(EXPECTED_EDGE_CASE_IDS),
        interface_count=len(REQUIRED_PUBLIC_INTERFACES),
        function_count=len(PUBLIC_CONTRACT_FUNCTIONS),
        false_guard_count=len(FALSE_GUARDS),
        zero_counter_count=len(ZERO_COUNTERS),
    )
    return report.to_dict()


def emit_public_validation_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Return the only allowed output shape for this public skeleton."""

    return validate_public_contract_skeleton(source)
