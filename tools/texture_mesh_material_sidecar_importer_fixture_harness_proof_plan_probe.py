#!/usr/bin/env python3
"""Validate the texture/mesh material sidecar importer fixture harness contract."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_fixture_harness_proof_plan_2026-06-10.md"

MATRIX_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md"
MATRIX_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-fixture-matrix.v1.json"
CONTRACT_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md"
LEDGER_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
COPIED_CORPUS_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
TEXTURE_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
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

THIS_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan"
FOLLOWUP_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan"
FOLLOWUP_SCOPE = "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan"
FOLLOWUP_NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan"
FOLLOWUP_PUBLIC_SKELETON_SLICE = "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan"
FOLLOWUP_PRIVATE_SAFETY_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
FOLLOWUP_PRIVATE_CHECKLIST_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"
STATUS_TOKEN = "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof"
MATRIX_STATUS = "texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof"

CASE_IDS = (
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
    "importerImplementation",
    "importerExecuted",
    "fixtureHarnessExecuted",
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
    "actualAssetImportRows",
    "privateFixtureRows",
    "rawFixtureExampleRows",
    "generatedAssetRows",
    "outputArtifactRows",
    "rebuildImplementationRows",
    "runtimeTexturePixelRows",
    "runtimeMeshRenderRows",
    "runtimeMaterialRows",
    "runtimeCollisionRows",
    "cleanRoomRendererRows",
    "runtimeResourceArchiveParserRows",
    "runtimeSidecarMaterialLoadRows",
    "beProcessesAfterSelection",
    "publicCaseRawRefLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "privateAssetLeakCount",
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
    "importer implementation complete",
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


def check_public_case_ids(result: dict[str, Any], failures: list[str]) -> None:
    ids = [row["caseId"] for row in result["publicEdgeCases"]]
    require(tuple(ids) == PUBLIC_EDGE_IDS, "public edge case ids mismatch", failures)
    for case_id in ids:
        require("/" not in case_id and "\\" not in case_id, f"public case id contains path separator: {case_id}", failures)
        require("." not in case_id, f"public case id contains file extension-like dot: {case_id}", failures)
        require(re.search(r"\b[a-fA-F0-9]{16,}\b", case_id) is None, f"public case id contains hash-like token: {case_id}", failures)
    for row in result["publicEdgeCases"]:
        for key in ("rawRefPublished", "filenamePublished", "pathPublished", "hashPublished"):
            require(row.get(key) is False, f"public edge case publishes forbidden field {key}: {row['caseId']}", failures)
        require(row["count"] == 1, f"public edge case count mismatch: {row['caseId']}", failures)


def check_matrix_prerequisite(failures: list[str]) -> None:
    matrix = read_json(MATRIX_RESULT)
    require(matrix["fixtureMatrixStatus"] == MATRIX_STATUS, "fixture matrix status mismatch", failures)
    require(matrix["selectedNextSlice"] == THIS_SLICE, "fixture matrix next-slice mismatch", failures)
    require(matrix["matrixSummary"]["fixtureCaseCount"] == 8, "fixture matrix case count mismatch", failures)
    require(matrix["matrixSummary"]["uniqueModelTextureRefUnion"] == 213, "matrix unique-ref mismatch", failures)
    require(matrix["matrixSummary"]["familyUniqueRefSum"] == 241, "matrix family sum mismatch", failures)
    require(matrix["matrixSummary"]["familyUniqueRefsAreNotAdditive"] is True, "matrix non-additive mismatch", failures)
    require(matrix["matrixSummary"]["stemOnlyMatches"] == 1, "matrix stem-only mismatch", failures)
    require(matrix["matrixSummary"]["ambiguousCatalogRefs"] == 1, "matrix ambiguous ref mismatch", failures)
    require(matrix["familyCoverage"]["embedded"]["duplicateOutputSurplusRows"] == 32, "matrix duplicate surplus mismatch", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["importerFixtureHarnessStatus"] == STATUS_TOKEN, "harness status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceFixtureMatrixStatus"] == MATRIX_STATUS, "source matrix status mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)

    summary = result["harnessSummary"]
    expected_summary = {
        "harnessDimensionCount": 7,
        "harnessCaseCount": 8,
        "importerAssertionGroupCount": 8,
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
        require(summary[key] == expected, f"harness summary mismatch: {key}", failures)

    families = result["familyFixtures"]
    require(families["loose"]["rows"] == 213, "loose row mismatch", failures)
    require(families["loose"]["textureRefInstances"] == 602, "loose ref instance mismatch", failures)
    require(families["loose"]["uniqueTextureRefs"] == 213, "loose unique ref mismatch", failures)
    require(families["loose"]["uniqueOutputFiles"] == 213, "loose output mismatch", failures)
    require(families["loose"]["exactFilenameMatches"] == 212, "loose exact match mismatch", failures)
    require(families["loose"]["stemOnlyMatches"] == 1, "loose stem-only mismatch", failures)
    require(families["loose"]["duplicateOutputSurplusRows"] == 0, "loose duplicate surplus mismatch", failures)
    require(families["embedded"]["rows"] == 139, "embedded row mismatch", failures)
    require(families["embedded"]["textureRefInstances"] == 666, "embedded ref instance mismatch", failures)
    require(families["embedded"]["uniqueTextureRefs"] == 28, "embedded unique ref mismatch", failures)
    require(families["embedded"]["uniqueOutputFiles"] == 107, "embedded output mismatch", failures)
    require(families["embedded"]["duplicateOutputGroups"] == 28, "embedded duplicate group mismatch", failures)
    require(families["embedded"]["duplicateOutputSurplusRows"] == 32, "embedded duplicate surplus mismatch", failures)

    cases = result["harnessCases"]
    require(tuple(row["caseId"] for row in cases) == CASE_IDS, "harness case ids mismatch", failures)
    require(all(row["status"] == "PASS" for row in cases), "harness case status mismatch", failures)
    union_case = next(row for row in cases if row["caseId"] == "importer-non-additive-union-fixture")
    require(union_case["uniqueModelTextureRefUnion"] == 213, "union case unique ref mismatch", failures)
    require(union_case["familyUniqueRefSum"] == 241, "union case family sum mismatch", failures)
    require(union_case["familyUniqueRefsAreNotAdditive"] is True, "union case non-additive mismatch", failures)
    duplicate_case = next(row for row in cases if row["caseId"] == "importer-duplicate-output-surplus-fixture")
    require(duplicate_case["duplicateOutputSurplusRows"] == 32, "duplicate case surplus row mismatch", failures)
    require(duplicate_case["dedupeToUniqueOutputsAllowed"] is False, "duplicate case dedupe guard mismatch", failures)
    check_public_case_ids(result, failures)

    for rule in (
        "the importer fixture harness is deterministic from public aggregate schema rows only",
        "unique model texture refs are a corpus union, not an additive sum of family unique refs",
        "embedded duplicate-output accounting uses surplus rows and must not collapse row coverage to unique output-file coverage",
    ):
        require(rule in result["harnessRules"], f"harness rule missing: {rule}", failures)

    guard = result["guardSummary"]
    require(guard["harnessFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["harnessZeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)

    require("the material sidecar matrix has a deterministic importer harness contract" in result["claimBoundary"]["proves"], "claim boundary missing harness proof", failures)
    require("importer implementation" in result["claimBoundary"]["doesNotProve"], "claim boundary missing importer implementation non-proof", failures)
    require("rebuild parity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing rebuild parity non-proof", failures)
    require(len(result["stopConditions"]) == 5, "stop condition count mismatch", failures)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json",
        f"importerFixtureHarnessStatus={STATUS_TOKEN}",
        f"sourceFixtureMatrixStatus={MATRIX_STATUS}",
        "harnessDimensionCount=7",
        "harnessCaseCount=8",
        "importerAssertionGroupCount=8",
        "publicSyntheticFixtureCount=8",
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
        "publicEdgeCaseIdCount=2",
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
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "importerImplementation=false",
        "importerExecuted=false",
        "fixtureHarnessExecuted=false",
        "rebuildImplementation=false",
        "runtimeTexturePixelsProven=false",
        "materialVisualCorrectnessProven=false",
        "materialShaderParityProven=false",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "actualAssetImportRows=0",
        "rawFixtureExampleRows=0",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in common_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md",
        "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json",
        STATUS_TOKEN,
        "harnessCaseCount=8",
        "uniqueModelTextureRefUnion=213",
        "familyUniqueRefsAreNotAdditive=true",
        "embeddedDuplicateOutputSurplusRows=32",
        "publicEdgeCaseIdCount=2",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed importer harness slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks importer harness active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed materialization lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks materialization lane active", failures)
    require(f"Completed {FOLLOWUP_SLICE}" in backlog, "backlog missing completed consumer dry-run lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}. Status: selected" not in backlog, "backlog still marks consumer dry-run lane active", failures)
    require(f"Completed {FOLLOWUP_NEXT_SLICE}" in backlog, "backlog missing completed implementation-readiness gate", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks implementation-readiness gate active", failures)
    require(f"Completed {FOLLOWUP_PUBLIC_SKELETON_SLICE}" in backlog, "backlog missing completed public contract skeleton", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PUBLIC_SKELETON_SLICE}. Status: selected" not in backlog, "backlog still marks public contract skeleton active", failures)
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


def check_source_docs(failures: list[str]) -> None:
    source_tokens = {
        MATRIX_PROOF: (
            f"fixtureMatrixStatus={MATRIX_STATUS}",
            "selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan",
            "matrixDimensionCount=7",
            "fixtureCaseCount=8",
            "uniqueModelTextureRefUnion=213",
            "familyUniqueRefsAreNotAdditive=true",
            "embeddedDuplicateOutputSurplusRows=32",
        ),
        CONTRACT_PROOF: (
            "contractExtensionStatus=texture-mesh-material-sidecar-rebuild-contract-extension-complete-static-contract-extension-not-runtime-proof",
            "selectedNextSlice=Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan",
            "modelRowsWithTextureRefs=352/352",
            "materialSidecarUniqueRefs=213",
            "ambiguousCatalogRefs=1",
            "embeddedDuplicateOutputBoundaryRows=32",
        ),
        LEDGER_PROOF: (
            "352/352",
            "1268",
            "213",
            "0` catalog-missing refs",
            "Embedded mesh duplicate-output caveat",
        ),
        COPIED_CORPUS_PROOF: (
            "Loose texture export lane | `847` attempted, `847` succeeded, `0` failed, `0` skipped",
            "Loose mesh export lane | `213` attempted, `213` succeeded, `0` failed, `0` skipped",
            "Embedded mesh export lane | `139` attempted, `139` succeeded, `0` failed, `0` skipped",
            "4050",
        ),
        MESH_CONTRACT: (
            "Model rows with material/texture-binding metadata | `352/352`",
            "Model texture sidecar refs covered | `213/213`",
        ),
        TEXTURE_CONTRACT: (
            "Wave1163",
            "17 CFastVB/CTexture/CDXTexture current-risk rows",
            "JPEG Huffman separate from inflate Huffman",
        ),
    }
    for path, tokens in source_tokens.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing source token: {token}", failures)


def check_progress_and_package(failures: list[str]) -> None:
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
        scripts.get("test:texture-mesh-material-sidecar-importer-fixture-harness-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_fixture_harness_proof_plan_probe.py --check",
        "missing package importer harness test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_matrix_prerequisite(failures)
    check_result(failures)
    check_docs(failures)
    check_source_docs(failures)
    check_progress_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after importer harness probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer fixture-harness probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer fixture-harness probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
