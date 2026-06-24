#!/usr/bin/env python3
"""Private-corpus safety boundary for texture/mesh material-sidecar importer work.

This module validates only public contract-skeleton evidence and emits a
public-safe boundary summary. It does not read private assets, list private
paths, execute a real importer, or create imported outputs.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


BOUNDARY_SCHEMA_VERSION = "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary.v1"
BOUNDARY_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-defined-"
    "no-private-corpus-read"
)
PUBLIC_SKELETON_STATUS = (
    "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-"
    "public-contract-only-not-real-importer-proof"
)
THIS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan"

SAFETY_PACKET_ITEMS = (
    "copied-or-app-owned-private-corpus-root-required",
    "installed-game-remains-read-only",
    "original-executable-remains-read-only",
    "app-owned-output-root-required",
    "public-private-separation-manifest-required",
    "no-public-raw-texture-ref-publication",
    "no-public-private-path-publication",
    "dry-run-before-importer-execution",
    "leak-check-before-public-docs",
    "stop-on-missing-explicit-private-corpus-arm",
)

AUTHORIZATION_GATES = (
    "explicit-private-corpus-read-arm-required",
    "operator-private-output-review-required",
    "copied-or-app-owned-corpus-root-required",
    "app-owned-artifact-root-required",
    "installed-game-mutation-forbidden",
    "original-executable-mutation-forbidden",
    "public-redaction-policy-required",
    "dry-run-before-output-materialization",
)

PRIVATE_CORPUS_CLASSES = (
    "loose-texture-sidecar-private-corpus",
    "loose-mesh-sidecar-private-corpus",
    "embedded-mesh-output-private-corpus",
    "asset-catalog-linkage-private-corpus",
    "importer-generated-output-private-corpus",
)

REDACTED_FIELD_IDS = (
    "private-corpus-root",
    "concrete-resource-archive-path",
    "concrete-sidecar-path",
    "concrete-output-path",
    "raw-texture-reference",
    "raw-filename-or-stem",
    "private-digest",
    "private-byte-length",
    "operator-profile-identifier",
    "process-or-window-identifier",
    "raw-importer-stdout-or-stderr",
    "screenshot-or-frame-locator",
)

PUBLIC_ALLOWED_OUTPUTS = (
    "class-counts",
    "status-tokens",
    "claim-boundary",
    "redaction-field-counts",
    "no-private-paths",
    "no-raw-texture-refs",
)

STOP_CONDITIONS = (
    "a private corpus path would be written to public docs",
    "a raw texture reference, stem, filename, digest, or byte count would be published",
    "private asset reads are required before an explicit private-corpus arm",
    "real importer execution is required before a dry-run safety-packet checklist exists",
    "generated/imported assets would be written outside an app-owned artifact root",
    "installed game files or the original executable would be mutated",
    "runtime parser, pixel, mesh-loading, Direct3D, GPU, or material visual behavior would be inferred",
    "Godot, product UI, renderer, rebuild, or no-noticeable-difference parity would be inferred",
    "public and private proof artifacts cannot be separated",
    "operator private-output review is unavailable when private outputs would be produced",
    "a leak check cannot distinguish class/count summaries from raw private evidence",
    "the public contract skeleton source no longer selects this private-corpus boundary",
)

FALSE_GUARDS = (
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
    "importerImplementation",
    "importerExecuted",
    "actualAssetImport",
    "generatedAssetOutputs",
    "privateAssetPublication",
    "runtimeExecution",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rendererImplementation",
    "rebuildImplementation",
    "runtimeResourceArchiveParserProven",
    "runtimeTextureParserBehaviorProven",
    "runtimeTexturePixelsProven",
    "runtimeMeshLoadingProven",
    "runtimeMeshSkinningProven",
    "runtimeDirect3DUploadProven",
    "runtimeGpuBehaviorProven",
    "nativeTextured3DRenderingProven",
    "materialVisualCorrectnessProven",
    "materialShaderParityProven",
    "visualQaComplete",
    "assetFormatCompletenessProven",
    "exactMeshTextureLayoutsProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "publicPrivateProofLeak",
)

ZERO_COUNTERS = (
    "privateCorpusReadRows",
    "privateAssetReadRows",
    "privateManifestRows",
    "actualAssetImportRows",
    "generatedAssetRows",
    "outputArtifactRows",
    "dryRunOutputArtifactRows",
    "rawFixtureExampleRows",
    "privateFixtureRows",
    "privateArtifactRows",
    "privatePathRows",
    "rawPathRows",
    "rawFilenameRows",
    "rawHashRows",
    "privateHashRows",
    "rawTextureRefRows",
    "publishedPrivatePathRows",
    "publishedRawRefRows",
    "publicCaseRawRefLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "privateAssetLeakCount",
    "publicPrivateProofLeakCount",
    "runtimeObservationRows",
    "runtimeTexturePixelRows",
    "runtimeMeshRenderRows",
    "runtimeMaterialRows",
    "screenshotRows",
    "captureRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "productUiRows",
    "godotRows",
    "realImporterImplementationRows",
    "rebuildImplementationRows",
    "beProcessesAfterPrivateCorpusBoundary",
)


class PrivateCorpusBoundaryError(ValueError):
    """Raised when public skeleton evidence does not satisfy the boundary."""


@dataclass(frozen=True)
class PrivateCorpusBoundaryReport:
    """Sanitized public summary of the private-corpus safety boundary."""

    safety_packet_item_count: int
    authorization_gate_count: int
    private_corpus_class_count: int
    redacted_field_count: int
    public_allowed_output_count: int
    stop_condition_count: int
    false_guard_count: int
    zero_counter_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": BOUNDARY_SCHEMA_VERSION,
            "status": "PASS",
            "privateCorpusSafetyBoundaryStatus": BOUNDARY_STATUS,
            "safetyBoundaryOnly": True,
            "privateCorpusSafetyBoundaryDefined": True,
            "privateCorpusReadAuthorizationPresent": False,
            "explicitImporterImplementationArmPresent": False,
            "operatorPrivateOutputReviewAvailable": False,
            "privateAssetRead": False,
            "privateCorpusReadPerformed": False,
            "privateCorpusEnumeration": False,
            "privateRootExistenceChecked": False,
            "privateAssetReadPerformed": False,
            "realImporterImplementation": False,
            "realImporterExecuted": False,
            "futurePrivateCorpusReadRequiresExplicitArm": True,
            "requiresCopiedOrAppOwnedCorpusRoot": True,
            "requiresAppOwnedArtifactRoot": True,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "publicPrivateSeparationRequired": True,
            "safetyPacketItemCount": self.safety_packet_item_count,
            "authorizationGateCount": self.authorization_gate_count,
            "privateCorpusClassCount": self.private_corpus_class_count,
            "redactedFieldCount": self.redacted_field_count,
            "publicAllowedOutputClassCount": self.public_allowed_output_count,
            "stopConditionCount": self.stop_condition_count,
            "falseGuardCount": self.false_guard_count,
            "zeroCounterCount": self.zero_counter_count,
            "publicLeakCheck": "PASS",
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateCorpusBoundaryError(message)


def _read_mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    _require(isinstance(value, Mapping), f"{key} must be a mapping")
    return value


def validate_private_corpus_safety_boundary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Validate prior public skeleton evidence and emit a boundary summary."""

    _require(source.get("status") == "PASS", "source public skeleton status mismatch")
    _require(source.get("publicContractSkeletonStatus") == PUBLIC_SKELETON_STATUS, "public skeleton token mismatch")
    _require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch")
    _require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch")

    skeleton = _read_mapping(source, "publicContractSkeleton")
    _require(skeleton.get("contractInterfaceCount") == 6, "public skeleton interface count mismatch")
    _require(skeleton.get("implementedContractInterfaceCount") == 6, "public skeleton implemented interface count mismatch")
    _require(skeleton.get("contractFunctionCount") == 2, "public skeleton function count mismatch")
    _require(skeleton.get("publicContractSkeletonImplementationRows") == 1, "public skeleton row count mismatch")
    _require(skeleton.get("failedSkeletonContractChecks") == 0, "public skeleton failed check count mismatch")

    decision = _read_mapping(source, "skeletonDecision")
    _require(decision.get("publicContractSkeletonImplemented") is True, "public skeleton not implemented")
    _require(decision.get("realImporterImplementation") is False, "real importer implementation should be false")
    _require(decision.get("realImporterExecuted") is False, "real importer execution should be false")
    _require(decision.get("privateAssetReadAuthorizationPresent") is False, "private asset authorization should be absent")
    _require(decision.get("operatorPrivateOutputReviewAvailable") is False, "operator private output review should be absent")

    guard = _read_mapping(source, "guardSummary")
    _require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")

    report = PrivateCorpusBoundaryReport(
        safety_packet_item_count=len(SAFETY_PACKET_ITEMS),
        authorization_gate_count=len(AUTHORIZATION_GATES),
        private_corpus_class_count=len(PRIVATE_CORPUS_CLASSES),
        redacted_field_count=len(REDACTED_FIELD_IDS),
        public_allowed_output_count=len(PUBLIC_ALLOWED_OUTPUTS),
        stop_condition_count=len(STOP_CONDITIONS),
        false_guard_count=len(FALSE_GUARDS),
        zero_counter_count=len(ZERO_COUNTERS),
    )
    return report.to_dict()


def emit_private_corpus_safety_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    """Return the only allowed public summary for this boundary slice."""

    return validate_private_corpus_safety_boundary(source)
