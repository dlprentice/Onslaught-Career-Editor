#!/usr/bin/env python3
"""Validate texture/mesh material sidecar importer implementation readiness gate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_implementation_readiness_gate_proof_plan_2026-06-10.md"

SOURCE_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md"
SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json"
MATERIALIZATION_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md"
HARNESS_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md"
MATRIX_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md"
CONTRACT_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
LORE_GAME_ASSETS_INDEX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan"
FOLLOWUP_PRIVATE_SAFETY_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
FOLLOWUP_PRIVATE_CHECKLIST_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"
STATUS_TOKEN = "texture-mesh-material-sidecar-importer-implementation-readiness-gate-complete-public-contract-skeleton-ready-not-real-importer-proof"
SOURCE_STATUS = "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan-complete-public-safe-consumer-dry-run-not-importer-execution-proof"

ROW_IDS = (
    "importer-source-matrix-prerequisite",
    "importer-loose-family-fixture",
    "importer-embedded-family-fixture",
    "importer-non-additive-union-fixture",
    "importer-sidecar-match-mode-fixture",
    "importer-catalog-linkage-fixture",
    "importer-duplicate-output-surplus-fixture",
    "importer-negative-claim-guard-fixture",
)

PUBLIC_EDGE_IDS = (
    "stem-only-sidecar-match-boundary-001",
    "ambiguous-catalog-ref-boundary-001",
)

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

ZERO_COUNTS = (
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
    "publicContractSkeletonImplementationRows",
    "beProcessesAfterReadinessGate",
    "publicCaseRawRefLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "privateAssetLeakCount",
    "publicPrivateProofLeakCount",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "ignored artifact path"),
    (re.compile(r"(?i)\bgame[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)\bmedia[\\/]"), "private media path"),
    (re.compile(r"(?i)textureRefSample|sampleRows|canonical_ref|canonicalRef|fbxTexturePath|exportFilePath"), "row-level private sample field"),
    (re.compile(r"(?i)asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "real importer implementation complete",
    "real importer execution complete",
    "private asset import complete",
    "runtime resource archive parser behavior proven",
    "runtime texture parser behavior proven",
    "runtime texture pixels proven",
    "runtime mesh loading proven",
    "runtime mesh skinning proven",
    "runtime direct3d upload proven",
    "gpu behavior proven",
    "native textured 3d rendering proven",
    "material visual correctness proven",
    "material/shader parity proven",
    "asset format completeness proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild implementation complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def no_bea_process_running() -> bool:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-Process -Name BEA -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_source_consumer(failures: list[str]) -> None:
    source = read_json(SOURCE_RESULT)
    require(source["consumerDryRunStatus"] == SOURCE_STATUS, "source consumer dry-run status mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source consumer selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source consumer selected next scope mismatch", failures)
    summary = source["consumerDryRunSummary"]
    require(summary["consumedFixtureRowCount"] == 8, "source consumed fixture row count mismatch", failures)
    require(summary["consumerDryRunStepCount"] == 10, "source consumer dry-run step count mismatch", failures)
    require(summary["consumerAssertionGroupCount"] == 8, "source assertion group count mismatch", failures)
    require(summary["consumerAssertionCheckCount"] == 19, "source assertion check count mismatch", failures)
    require(summary["failedConsumerAssertions"] == 0, "source failed assertion count mismatch", failures)
    require(summary["unexpectedFixtureRows"] == 0, "source unexpected row count mismatch", failures)
    require(summary["consumerOutputArtifactRows"] == 0, "source output artifact count mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "source public leak check mismatch", failures)
    require(tuple(source["consumedFixtureRows"]) == ROW_IDS, "source consumed fixture row ids mismatch", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["implementationReadinessStatus"] == STATUS_TOKEN, "implementation readiness status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceConsumerDryRunStatus"] == SOURCE_STATUS, "source consumer status mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    evidence = result["sourceEvidence"]
    require(evidence["sourceProofCount"] == 6, "source proof count mismatch", failures)
    for key in ("consumerDryRunProof", "consumerDryRunSchema", "materializationProof", "importerFixtureHarnessProof", "fixtureMatrixProof", "contractExtensionProof"):
        require(key in evidence and evidence[key], f"source evidence missing {key}", failures)

    decision = result["readinessDecision"]
    expected_decision = {
        "implementationReadinessGateComplete": True,
        "publicContractSkeletonReadyNow": True,
        "realImporterImplementationReadyNow": False,
        "realImporterExecutionReadyNow": False,
        "implementationDeferred": True,
        "nextLaneClass": "non-runtime public contract skeleton implementation proof",
        "explicitImporterImplementationArmPresent": False,
        "privateAssetReadAuthorizationPresent": False,
        "operatorPrivateOutputReviewAvailable": False,
        "selectedNextImplementationSliceCount": 1,
    }
    for key, expected in expected_decision.items():
        require(decision[key] == expected, f"readiness decision mismatch: {key}", failures)

    summary = result["readinessSummary"]
    expected_summary = {
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
        "allowedInputMode": "tracked-public-sanitized-consumer-dry-run-schema",
        "allowedOutputMode": "public-contract-skeleton-validation-report-only",
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
    for key, expected in expected_summary.items():
        require(summary[key] == expected, f"readiness summary mismatch: {key}", failures)

    require(tuple(result["consumedFixtureRows"]) == ROW_IDS, "consumed fixture row ids mismatch", failures)
    require(len(result["requiredPublicContractInterfaces"]) == 6, "required interface count mismatch", failures)
    require(len(result["readinessGates"]) == 8, "readiness gate row count mismatch", failures)
    require(all(row["status"] == "PASS" for row in result["readinessGates"]), "readiness gate status mismatch", failures)
    require(len(result["readinessChecks"]) == 16, "readiness check row count mismatch", failures)
    require(all(row["status"] == "PASS" for row in result["readinessChecks"]), "readiness check status mismatch", failures)

    expressions = {row["checkId"]: row.get("expression") for row in result["readinessChecks"] if "expression" in row}
    require(expressions["row-sum-arithmetic"] == "213 + 139 = 352", "row arithmetic expression mismatch", failures)
    require(expressions["ref-instance-arithmetic"] == "602 + 666 = 1268", "ref arithmetic expression mismatch", failures)
    require(expressions["family-unique-ref-sum"] == "213 + 28 = 241", "family unique expression mismatch", failures)
    require(expressions["unique-ref-union-non-additive"] == "uniqueModelTextureRefUnion = 213", "union expression mismatch", failures)
    require(expressions["sidecar-match-mode-boundary"] == "212 + 1 = 213", "sidecar expression mismatch", failures)
    require(expressions["embedded-duplicate-output-surplus"] == "139 - 107 = 32", "duplicate surplus expression mismatch", failures)

    edge_ids = [row["caseId"] for row in result["publicEdgeCases"]]
    require(tuple(edge_ids) == PUBLIC_EDGE_IDS, "public edge ids mismatch", failures)
    for row in result["publicEdgeCases"]:
        require(row["count"] == 1, f"public edge case count mismatch: {row['caseId']}", failures)
        for key in ("rawRefPublished", "rawStemPublished", "catalogVariantPublished", "filenamePublished", "pathPublished", "hashPublished"):
            require(row.get(key) is False, f"public edge publishes forbidden field {key}: {row['caseId']}", failures)

    guard = result["guardSummary"]
    require(guard["implementationReadinessFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["implementationReadinessZeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)

    require("the importer implementation path has a public-safe readiness gate" in result["claimBoundary"]["proves"], "claim boundary missing readiness proof", failures)
    require("real importer implementation" in result["claimBoundary"]["doesNotProve"], "claim boundary missing importer implementation non-proof", failures)
    require("real importer execution" in result["claimBoundary"]["doesNotProve"], "claim boundary missing importer execution non-proof", failures)
    require("no-noticeable-difference parity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing parity non-proof", failures)
    require(len(result["stopConditions"]) == 6, "stop condition count mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json",
        f"implementationReadinessStatus={STATUS_TOKEN}",
        f"sourceConsumerDryRunStatus={SOURCE_STATUS}",
        "sourceConsumedFixtureRowCount=8",
        "sourceConsumerDryRunStepCount=10",
        "sourceConsumerAssertionGroupCount=8",
        "sourceConsumerAssertionCheckCount=19",
        "sourceFailedConsumerAssertions=0",
        "sourceUnexpectedFixtureRows=0",
        "sourceConsumerOutputArtifactRows=0",
        "readinessGateCount=8",
        "readinessCheckCount=16",
        "failedReadinessGateCount=0",
        "blockedReadinessGateCount=0",
        "readinessValidationOnly=true",
        "readinessConsumesPublicDryRunOnly=true",
        "implementationReadinessGateComplete=true",
        "publicContractSkeletonReadyNow=true",
        "realImporterImplementationReadyNow=false",
        "realImporterExecutionReadyNow=false",
        "implementationDeferred=true",
        "explicitImporterImplementationArmPresent=false",
        "privateAssetReadAuthorizationPresent=false",
        "operatorPrivateOutputReviewAvailable=false",
        "selectedNextImplementationSliceCount=1",
        "publicSyntheticFixtureCount=8",
        "publicEdgeCaseIdCount=2",
        "modelRowsWithTextureRefs=352/352",
        "modelTextureReferenceInstances=1268",
        "uniqueModelTextureRefUnion=213",
        "familyUniqueRefSum=241",
        "familyUniqueRefsAreNotAdditive=true",
        "sidecarFiles=213",
        "exactFilenameMatches=212",
        "stemOnlyMatches=1",
        "missingSidecarRefs=0",
        "catalogRows=4050",
        "catalogMissingRefs=0",
        "ambiguousCatalogRefs=1",
        "embeddedDuplicateOutputGroups=28",
        "embeddedDuplicateOutputSurplusRows=32",
        "publicLeakCheck=PASS",
        "importer-source-matrix-prerequisite",
        "importer-loose-family-fixture",
        "importer-embedded-family-fixture",
        "importer-non-additive-union-fixture",
        "importer-sidecar-match-mode-fixture",
        "importer-catalog-linkage-fixture",
        "importer-duplicate-output-surplus-fixture",
        "importer-negative-claim-guard-fixture",
        "stem-only-sidecar-match-boundary-001",
        "ambiguous-catalog-ref-boundary-001",
        "213 + 139 = 352",
        "602 + 666 = 1268",
        "213 + 28 = 241",
        "212 + 1 = 213",
        "139 - 107 = 32",
        "rawRefPublished=false",
        "rawStemPublished=false",
        "catalogVariantPublished=false",
        "filenamePublished=false",
        "pathPublished=false",
        "hashPublished=false",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "importerImplementation=false",
        "rebuildImplementation=false",
        "runtimeTexturePixelsProven=false",
        "materialVisualCorrectnessProven=false",
        "materialShaderParityProven=false",
        "implementationReadinessFalseGuardCount=45",
        "implementationReadinessZeroCounterCount=38",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "outputArtifactRows=0",
        "dryRunOutputArtifactRows=0",
        "realImporterImplementationRows=0",
        "publicContractSkeletonImplementationRows=0",
        "beProcessesAfterReadinessGate=0",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in common_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)


def check_front_doors(failures: list[str]) -> None:
    front_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md",
        "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json",
        STATUS_TOKEN,
        "sourceConsumerDryRunStatus=" + SOURCE_STATUS,
        "readinessGateCount=8",
        "readinessCheckCount=16",
        "failedReadinessGateCount=0",
        "blockedReadinessGateCount=0",
        "readinessValidationOnly=true",
        "readinessConsumesPublicDryRunOnly=true",
        "publicContractSkeletonReadyNow=true",
        "realImporterImplementationReadyNow=false",
        "realImporterExecutionReadyNow=false",
        "selectedNextImplementationSliceCount=1",
        "uniqueModelTextureRefUnion=213",
        "familyUniqueRefsAreNotAdditive=true",
        "embeddedDuplicateOutputSurplusRows=32",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, GAME_ASSETS_INDEX):
        text = read_text(path)
        for token in front_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (GAME_ASSETS_INDEX, LORE_GAME_ASSETS_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed readiness gate slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed consumer dry-run source slice", failures)
    require(f"The selected active static-to-proof slice is {PREVIOUS_SLICE}. Status: selected" not in backlog, "backlog still marks consumer dry-run active", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks readiness gate active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed public contract skeleton slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks public contract skeleton active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_SAFETY_SLICE}" in backlog, "backlog missing completed private corpus safety boundary", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_SAFETY_SLICE}. Status: selected" not in backlog, "backlog still marks private corpus safety boundary active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_CHECKLIST_SLICE}" in backlog, "backlog missing completed private corpus safety packet checklist population", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_CHECKLIST_SLICE}. Status: selected" not in backlog, "backlog still marks private corpus safety packet checklist population active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE}" in backlog, "backlog missing completed private corpus read-only inventory preflight", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE}. Status: selected" not in backlog, "backlog still marks private corpus read-only inventory preflight active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE}. Status: selected" not in backlog, "active block still marks private corpus read-only manifest dry-run active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest materialization", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE}. Status: selected" not in backlog, "active block still marks private corpus read-only manifest materialization active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest consumer validation", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE}. Status: selected" not in backlog, "active block still marks private corpus read-only manifest consumer validation active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE}" in backlog, "backlog missing completed private corpus redacted manifest importer contract adapter", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE}. Status: selected" not in backlog, "active block still marks private corpus redacted manifest importer contract adapter active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE}" in backlog, "backlog missing completed private corpus redacted manifest importer contract adapter dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE}. Status: selected" not in backlog, "active block still marks private corpus redacted manifest importer contract adapter dry-run active", failures)
    require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in backlog, "active block missing private corpus real importer dry-run command consumer validation", failures)
    require(backlog.count("The selected active static-to-proof slice is ") == 1, "backlog should have exactly one active slice sentence", failures)


def check_source_docs_and_package(failures: list[str]) -> None:
    source_tokens = {
        SOURCE_PROOF: (
            f"consumerDryRunStatus={SOURCE_STATUS}",
            f"selectedNextSlice={THIS_SLICE}",
            "consumedFixtureRowCount=8",
            "consumerDryRunStepCount=10",
            "consumerAssertionCheckCount=19",
        ),
        MATERIALIZATION_PROOF: (
            "materializationStatus=texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan-complete-public-safe-deterministic-fixture-row-materialization-not-runtime-proof",
            f"selectedNextSlice={PREVIOUS_SLICE}",
            "materializedFixtureRowCount=8",
        ),
        HARNESS_PROOF: (
            "importerFixtureHarnessStatus=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof",
            "harnessCaseCount=8",
        ),
        MATRIX_PROOF: (
            "fixtureMatrixStatus=texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof",
            "fixtureCaseCount=8",
        ),
        CONTRACT_PROOF: (
            "contractExtensionStatus=texture-mesh-material-sidecar-rebuild-contract-extension-complete-static-contract-extension-not-runtime-proof",
            "materialSidecarUniqueRefs=213",
        ),
    }
    for path, tokens in source_tokens.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing source token: {token}", failures)

    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_implementation_readiness_gate_proof_plan_probe.py --check",
        "missing package readiness-gate test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_source_consumer(failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors(failures)
    check_source_docs_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after readiness-gate probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer implementation readiness-gate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer implementation readiness-gate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
