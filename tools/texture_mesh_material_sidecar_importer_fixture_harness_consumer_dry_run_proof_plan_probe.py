#!/usr/bin/env python3
"""Validate texture/mesh material sidecar importer fixture consumer dry-run."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_fixture_harness_consumer_dry_run_proof_plan_2026-06-10.md"

MATERIALIZATION_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md"
MATERIALIZATION_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.v1.json"
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

THIS_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan"
FOLLOWUP_NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan"
FOLLOWUP_PRIVATE_SAFETY_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
FOLLOWUP_PRIVATE_CHECKLIST_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"
STATUS_TOKEN = "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan-complete-public-safe-consumer-dry-run-not-importer-execution-proof"
SOURCE_STATUS = "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan-complete-public-safe-deterministic-fixture-row-materialization-not-runtime-proof"

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
    "importerImplementationRows",
    "rebuildImplementationRows",
    "runtimeCollisionRows",
    "cleanRoomRendererRows",
    "runtimeResourceArchiveParserRows",
    "runtimeSidecarMaterialLoadRows",
    "beProcessesAfterConsumerDryRun",
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


def check_source_materialization(failures: list[str]) -> None:
    source = read_json(MATERIALIZATION_RESULT)
    require(source["materializationStatus"] == SOURCE_STATUS, "source materialization status mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source materialization selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source materialization selected next scope mismatch", failures)
    summary = source["materializationSummary"]
    require(summary["materializedFixtureRowCount"] == 8, "source materialized row count mismatch", failures)
    require(summary["publicSyntheticFixtureCount"] == 8, "source public synthetic count mismatch", failures)
    require(summary["publicEdgeCaseIdCount"] == 2, "source public edge count mismatch", failures)
    require(summary["derivedAssertionCount"] == 6, "source derived assertion count mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "source public leak check mismatch", failures)
    require(tuple(row["fixtureRowId"] for row in source["materializedFixtureRows"]) == ROW_IDS, "source materialized row ids mismatch", failures)


def check_result(failures: list[str]) -> None:
    source = read_json(MATERIALIZATION_RESULT)
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["consumerDryRunStatus"] == STATUS_TOKEN, "consumer dry-run status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceMaterializationStatus"] == SOURCE_STATUS, "source status mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    summary = result["consumerDryRunSummary"]
    expected_summary = {
        "sourceMaterializedFixtureRowCount": 8,
        "consumedFixtureRowCount": 8,
        "consumerDryRunStepCount": 10,
        "consumerAssertionGroupCount": 8,
        "consumerAssertionCheckCount": 19,
        "failedConsumerAssertions": 0,
        "unexpectedFixtureRows": 0,
        "publicSyntheticFixtureCount": 8,
        "publicEdgeCaseIdCount": 2,
        "derivedAssertionCount": 6,
        "dryRunOnly": True,
        "dryRunValidationOnly": True,
        "consumerInputMode": "tracked-public-sanitized-materialization-schema",
        "consumerOutputMode": "dry-run-summary-only",
        "consumerDryRunExecuted": True,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "consumerOutputArtifactRows": 0,
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
        require(summary[key] == expected, f"consumer summary mismatch: {key}", failures)

    source_rows = tuple(row["fixtureRowId"] for row in source["materializedFixtureRows"])
    require(tuple(result["consumedFixtureRows"]) == source_rows, "consumed fixture rows do not match source", failures)
    require(tuple(result["consumedFixtureRows"]) == ROW_IDS, "consumed fixture row ids mismatch", failures)
    require(len(result["consumerDryRunSteps"]) == 10, "consumer dry-run step count mismatch", failures)
    require(all(row["status"] == "PASS" for row in result["consumerDryRunSteps"]), "consumer step status mismatch", failures)
    require(len(result["consumerChecks"]) == 19, "consumer check count mismatch", failures)
    require(all(row["status"] == "PASS" for row in result["consumerChecks"]), "consumer check status mismatch", failures)
    expressions = {row["checkId"]: row.get("expression") for row in result["consumerChecks"] if "expression" in row}
    require(expressions["row-sum-arithmetic"] == "213 + 139 = 352", "row arithmetic expression mismatch", failures)
    require(expressions["ref-instance-arithmetic"] == "602 + 666 = 1268", "ref arithmetic expression mismatch", failures)
    require(expressions["family-unique-ref-sum"] == "213 + 28 = 241", "family unique expression mismatch", failures)
    require(expressions["unique-ref-union-non-additive"] == "uniqueModelTextureRefUnion = 213", "union expression mismatch", failures)
    require(expressions["sidecar-match-mode-boundary"] == "212 + 1 = 213", "sidecar expression mismatch", failures)
    require(expressions["embedded-duplicate-output-surplus"] == "139 - 107 = 32", "duplicate surplus expression mismatch", failures)

    # Re-derive the public aggregate relations from the source materialization.
    families = source["familyFixtures"]
    require(families["loose"]["rows"] + families["embedded"]["rows"] == 352, "source row sum arithmetic mismatch", failures)
    require(families["loose"]["textureRefInstances"] + families["embedded"]["textureRefInstances"] == 1268, "source ref instance arithmetic mismatch", failures)
    require(families["loose"]["uniqueTextureRefs"] + families["embedded"]["uniqueTextureRefs"] == 241, "source family unique arithmetic mismatch", failures)
    require(source["materializationSummary"]["uniqueModelTextureRefUnion"] == 213, "source unique union mismatch", failures)
    require(families["loose"]["exactFilenameMatches"] + families["loose"]["stemOnlyMatches"] == 213, "source sidecar arithmetic mismatch", failures)
    require(families["embedded"]["rows"] - families["embedded"]["uniqueOutputFiles"] == 32, "source duplicate surplus arithmetic mismatch", failures)

    edge_ids = [row["caseId"] for row in result["publicEdgeCases"]]
    require(tuple(edge_ids) == PUBLIC_EDGE_IDS, "public edge ids mismatch", failures)
    for row in result["publicEdgeCases"]:
        require(row["count"] == 1, f"edge case count mismatch: {row['caseId']}", failures)
        for key in ("rawRefPublished", "rawStemPublished", "catalogVariantPublished", "filenamePublished", "pathPublished", "hashPublished"):
            require(row.get(key) is False, f"public edge publishes forbidden field {key}: {row['caseId']}", failures)

    guard = result["guardSummary"]
    require(guard["consumerDryRunFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["consumerDryRunZeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)

    require("the eight public-safe materialized fixture rows can be consumed by a dry-run importer-facing contract" in result["claimBoundary"]["proves"], "claim boundary missing consumer proof", failures)
    require("real importer implementation" in result["claimBoundary"]["doesNotProve"], "claim boundary missing importer implementation non-proof", failures)
    require("real importer execution" in result["claimBoundary"]["doesNotProve"], "claim boundary missing importer execution non-proof", failures)
    require("no-noticeable-difference parity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing parity non-proof", failures)
    require(len(result["stopConditions"]) == 5, "stop condition count mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json",
        f"consumerDryRunStatus={STATUS_TOKEN}",
        f"sourceMaterializationStatus={SOURCE_STATUS}",
        "sourceMaterializedFixtureRowCount=8",
        "consumedFixtureRowCount=8",
        "consumerDryRunStepCount=10",
        "consumerAssertionGroupCount=8",
        "consumerAssertionCheckCount=19",
        "failedConsumerAssertions=0",
        "unexpectedFixtureRows=0",
        "publicSyntheticFixtureCount=8",
        "publicEdgeCaseIdCount=2",
        "derivedAssertionCount=6",
        "dryRunOnly=true",
        "dryRunValidationOnly=true",
        "consumerInputMode=tracked-public-sanitized-materialization-schema",
        "consumerOutputMode=dry-run-summary-only",
        "consumerDryRunExecuted=true",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "consumerOutputArtifactRows=0",
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
        "fixtureHarnessConsumerRuntimeExecuted=false",
        "rebuildImplementation=false",
        "runtimeTexturePixelsProven=false",
        "materialVisualCorrectnessProven=false",
        "materialShaderParityProven=false",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "outputArtifactRows=0",
        "dryRunOutputArtifactRows=0",
        "importerImplementationRows=0",
        "beProcessesAfterConsumerDryRun=0",
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
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md",
        "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json",
        STATUS_TOKEN,
        "consumedFixtureRowCount=8",
        "consumerDryRunStepCount=10",
        "consumerAssertionGroupCount=8",
        "consumerAssertionCheckCount=19",
        "dryRunOnly=true",
        "dryRunValidationOnly=true",
        "consumerOutputArtifactRows=0",
        "failedConsumerAssertions=0",
        "unexpectedFixtureRows=0",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed consumer dry-run slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed implementation-readiness gate", failures)
    require(f"The selected active static-to-proof slice is {PREVIOUS_SLICE}. Status: selected" not in backlog, "backlog still marks materialization active", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks consumer dry-run active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks implementation-readiness gate active", failures)
    require(f"Completed {FOLLOWUP_NEXT_SLICE}" in backlog, "backlog missing completed public contract skeleton", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks public contract skeleton active", failures)
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
        MATERIALIZATION_PROOF: (
            f"materializationStatus={SOURCE_STATUS}",
            f"selectedNextSlice={THIS_SLICE}",
            "materializedFixtureRowCount=8",
            "publicSyntheticFixtureCount=8",
            "publicEdgeCaseIdCount=2",
            "derivedAssertionCount=6",
        ),
        HARNESS_PROOF: (
            "importerFixtureHarnessStatus=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof",
            f"selectedNextSlice={PREVIOUS_SLICE}",
            "harnessCaseCount=8",
        ),
        MATRIX_PROOF: (
            "fixtureMatrixStatus=texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof",
            "fixtureCaseCount=8",
            "familyUniqueRefsAreNotAdditive=true",
        ),
        CONTRACT_PROOF: (
            "contractExtensionStatus=texture-mesh-material-sidecar-rebuild-contract-extension-complete-static-contract-extension-not-runtime-proof",
            "modelRowsWithTextureRefs=352/352",
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
        scripts.get("test:texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_fixture_harness_consumer_dry_run_proof_plan_probe.py --check",
        "missing package consumer dry-run test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_source_materialization(failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors(failures)
    check_source_docs_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after consumer dry-run probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer fixture-harness consumer dry-run probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer fixture-harness consumer dry-run probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
