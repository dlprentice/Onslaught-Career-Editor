#!/usr/bin/env python3
"""Validate the texture/mesh material sidecar rebuild-contract extension."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_rebuild_contract_extension_proof_plan_2026-06-10.md"

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

SOURCE_LEDGER = ROOT / "subagents" / "texture_mesh_material_sidecar_ledger_2026-06-08" / "asset-material-sidecar-ledger.json"
SOURCE_LEDGER_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
COPIED_CORPUS_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
ASSET_BRIDGE_PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
TEXTURE_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"

THIS_SLICE = "Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-rebuild-fixture-matrix-proof-plan"
FOLLOWUP_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan"
FOLLOWUP_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan"
FOLLOWUP_CONSUMER_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan"
FOLLOWUP_IMPLEMENTATION_READINESS_SLICE = "Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan"
FOLLOWUP_PUBLIC_SKELETON_SLICE = "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan"
FOLLOWUP_PRIVATE_SAFETY_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
FOLLOWUP_PRIVATE_CHECKLIST_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"
STATUS_TOKEN = "texture-mesh-material-sidecar-rebuild-contract-extension-complete-static-contract-extension-not-runtime-proof"

VOCABULARY_TERMS = (
    "model row",
    "row family",
    "model texture reference instance",
    "unique model texture ref",
    "mesh texture sidecar file",
    "exact filename match",
    "stem-only match",
    "catalog-mapped ref",
    "catalog-missing ref",
    "missing sidecar ref",
    "ambiguous catalog ref",
    "duplicate-output group",
    "duplicate row",
    "unique output file",
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
    "rebuildImplementationRows",
    "runtimeTexturePixelRows",
    "runtimeMeshRenderRows",
    "runtimeMaterialRows",
    "runtimeCollisionRows",
    "cleanRoomRendererRows",
    "runtimeResourceArchiveParserRows",
    "runtimeSidecarMaterialLoadRows",
    "beProcessesAfterSelection",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
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
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)textureRefSample|sampleRows|canonical_ref|canonicalRef|fbxTexturePath|exportFilePath"), "row-level private sample field"),
    (re.compile(r"(?i)aya_asset_manifest\.json|asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
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


def check_source_ledger(failures: list[str]) -> None:
    if not SOURCE_LEDGER.is_file():
        return
    ledger = read_json(SOURCE_LEDGER)
    require(ledger["schema"] == "asset-material-sidecar-ledger.v1", "source ledger schema mismatch", failures)
    require(ledger["status"] == "PASS", "source ledger status mismatch", failures)
    require(ledger["failures"] == [], "source ledger reports failures", failures)

    counts = ledger["countAnchors"]
    require(counts["archives"] == 301, "source archive count mismatch", failures)
    require(counts["goodieArchives"] == 232, "source goodie count mismatch", failures)
    require(counts["topLevelChunks"]["TEXT"] == 18857, "source TEXT count mismatch", failures)
    require(counts["topLevelChunks"]["MESH"] == 3492, "source MESH count mismatch", failures)
    require(counts["topLevelChunks"]["GDIE"] == 232, "source GDIE count mismatch", failures)
    require(counts["packedRefs"]["textTextures"] == "601/601", "source TEXT ref mismatch", failures)
    require(counts["packedRefs"]["referenceMeshes"] == "209/209", "source MESH ref mismatch", failures)
    require(counts["packedRefs"]["gdieTextures"] == "206/206", "source GDIE texture ref mismatch", failures)
    require(counts["packedRefs"]["gdieMeshes"] == "42/42", "source GDIE mesh ref mismatch", failures)

    exports = ledger["exportLanes"]
    require(exports["looseTextures"]["rows"] == 847 and exports["looseTextures"]["succeeded"] == 847, "source loose texture export mismatch", failures)
    require(exports["looseMeshes"]["rows"] == 213 and exports["looseMeshes"]["succeeded"] == 213, "source loose mesh export mismatch", failures)
    require(exports["embeddedMeshes"]["rows"] == 139 and exports["embeddedMeshes"]["succeeded"] == 139, "source embedded mesh export mismatch", failures)
    require(exports["embeddedMeshes"]["uniqueOutputFiles"] == 107, "source embedded unique output mismatch", failures)
    require(exports["embeddedMeshes"]["duplicateOutputGroups"] == 28, "source embedded duplicate group mismatch", failures)
    require(exports["embeddedMeshes"]["duplicateOutputRows"] == 32, "source embedded duplicate row mismatch", failures)

    coverage = ledger["modelCoverage"]
    require(coverage["modelRows"] == 352, "source model row mismatch", failures)
    require(coverage["modelRowsWithTextureRefs"] == 352, "source model rows with refs mismatch", failures)
    require(coverage["modelTextureReferenceInstances"] == 1268, "source ref instance mismatch", failures)
    require(coverage["uniqueModelTextureRefs"] == 213, "source unique ref mismatch", failures)
    require(coverage["sidecarTextureFiles"] == 213, "source sidecar file mismatch", failures)
    require(coverage["uniqueTextureRefsWithExactSidecarName"] == 212, "source exact sidecar mismatch", failures)
    require(coverage["uniqueTextureRefsWithSidecarStemOnly"] == 1, "source stem-only sidecar mismatch", failures)
    require(coverage["modelRowsWithAllTextureRefsCatalogMapped"] == 352, "source catalog-mapped row mismatch", failures)
    require(coverage["modelRowsWithAnyCatalogMissingTextureRef"] == 0, "source catalog gap mismatch", failures)
    require(coverage["modelRowsWithAnyMissingSidecarTextureRef"] == 0, "source sidecar gap row mismatch", failures)
    require(coverage["uniqueTextureRefsMissingSidecar"] == 0, "source missing sidecar ref mismatch", failures)
    require(coverage["uniqueTextureRefsMissingCatalogRows"] == 0, "source missing catalog ref mismatch", failures)
    require(coverage["uniqueTextureRefsAmbiguousInCatalog"] == 1, "source ambiguous catalog mismatch", failures)
    require(coverage["byKind"]["loose"]["rows"] == 213, "source loose rows mismatch", failures)
    require(coverage["byKind"]["loose"]["textureRefInstances"] == 602, "source loose ref instances mismatch", failures)
    require(coverage["byKind"]["embedded"]["rows"] == 139, "source embedded rows mismatch", failures)
    require(coverage["byKind"]["embedded"]["textureRefInstances"] == 666, "source embedded ref instances mismatch", failures)
    require(coverage["byKind"]["embedded"]["uniqueTextureRefs"] == 28, "source embedded unique refs mismatch", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["contractExtensionStatus"] == STATUS_TOKEN, "contract extension status mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    source = result["sourceEvidence"]
    require(source["sourceProofCount"] == 5, "source proof count mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["archiveRows"] == 301, "result archive count mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["goodieArchiveRows"] == 232, "result goodie count mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["topLevelChunks"]["TEXT"] == 18857, "result TEXT count mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["topLevelChunks"]["MESH"] == 3492, "result MESH count mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["topLevelChunks"]["GDIE"] == 232, "result GDIE count mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["packedRefs"]["textTextures"] == "601/601", "result TEXT refs mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["packedRefs"]["referenceMeshes"] == "209/209", "result MESH refs mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["packedRefs"]["gdieTextures"] == "206/206", "result GDIE texture refs mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["packedRefs"]["gdieMeshes"] == "42/42", "result GDIE mesh refs mismatch", failures)
    require(source["textureMeshCopiedCorpusProof"]["catalogRows"] == 4050, "result catalog rows mismatch", failures)

    sidecar = source["textureMeshMaterialSidecarLedgerProof"]
    require(sidecar["ledgerSchema"] == "asset-material-sidecar-ledger.v1", "result ledger schema mismatch", failures)
    require(sidecar["copiedCorpusFileCount"] == 8574, "result copied-corpus files mismatch", failures)
    require(sidecar["copiedCorpusByteCount"] == 250335133, "result copied-corpus bytes mismatch", failures)
    require(sidecar["modelRowsWithTextureRefs"] == "352/352", "result model rows mismatch", failures)
    require(sidecar["modelTextureReferenceInstances"] == 1268, "result ref instances mismatch", failures)
    require(sidecar["uniqueModelTextureRefs"] == 213, "result unique refs mismatch", failures)
    require(sidecar["meshTextureSidecarFiles"] == 213, "result sidecar files mismatch", failures)
    require(sidecar["uniqueTextureRefsWithExactSidecarName"] == 212, "result exact sidecar mismatch", failures)
    require(sidecar["uniqueTextureRefsWithSidecarStemOnly"] == 1, "result stem-only mismatch", failures)
    require(sidecar["modelRowsWithAllTextureRefsCatalogMapped"] == "352/352", "result catalog-mapped rows mismatch", failures)
    require(sidecar["missingSidecarRows"] == 0, "result missing sidecar row mismatch", failures)
    require(sidecar["uniqueTextureRefsMissingSidecar"] == 0, "result missing sidecar refs mismatch", failures)
    require(sidecar["uniqueTextureRefsMissingCatalogRows"] == 0, "result missing catalog refs mismatch", failures)
    require(sidecar["uniqueTextureRefsAmbiguousInCatalog"] == 1, "result ambiguous catalog refs mismatch", failures)
    require(sidecar["looseRows"] == 213, "result loose rows mismatch", failures)
    require(sidecar["looseTextureRefInstances"] == 602, "result loose ref instances mismatch", failures)
    require(sidecar["embeddedRows"] == 139, "result embedded rows mismatch", failures)
    require(sidecar["embeddedTextureRefInstances"] == 666, "result embedded ref instances mismatch", failures)
    require(sidecar["embeddedUniqueTextureRefs"] == 28, "result embedded unique refs mismatch", failures)
    require(sidecar["embeddedUniqueOutputFiles"] == 107, "result embedded unique output mismatch", failures)
    require(sidecar["embeddedDuplicateOutputGroups"] == 28, "result embedded duplicate groups mismatch", failures)
    require(sidecar["embeddedDuplicateOutputRows"] == 32, "result embedded duplicate rows mismatch", failures)

    require(result["contractVocabulary"]["termCount"] == len(VOCABULARY_TERMS), "vocabulary term count mismatch", failures)
    require(tuple(result["contractVocabulary"]["terms"]) == VOCABULARY_TERMS, "vocabulary terms mismatch", failures)

    contract = result["rebuildContract"]
    require(contract["modelRowsWithTextureRefs"] == "352/352", "contract model row mismatch", failures)
    require(contract["rowFamilies"]["loose"]["rows"] == 213, "contract loose rows mismatch", failures)
    require(contract["rowFamilies"]["loose"]["uniqueOutputFiles"] == 213, "contract loose output mismatch", failures)
    require(contract["rowFamilies"]["embedded"]["rows"] == 139, "contract embedded rows mismatch", failures)
    require(contract["rowFamilies"]["embedded"]["uniqueOutputFiles"] == 107, "contract embedded output mismatch", failures)
    require(contract["rowFamilies"]["embedded"]["duplicateOutputGroups"] == 28, "contract embedded duplicate group mismatch", failures)
    require(contract["rowFamilies"]["embedded"]["duplicateRows"] == 32, "contract embedded duplicate rows mismatch", failures)
    require(contract["sidecarCoverage"]["uniqueModelTextureRefs"] == 213, "contract unique refs mismatch", failures)
    require(contract["sidecarCoverage"]["missingSidecarRefs"] == 0, "contract sidecar gap mismatch", failures)
    require(contract["catalogCoverage"]["catalogRows"] == 4050, "contract catalog rows mismatch", failures)
    require(contract["catalogCoverage"]["catalogMissingRefs"] == 0, "contract catalog gap mismatch", failures)
    require(contract["catalogCoverage"]["ambiguousCatalogRefs"] == 1, "contract ambiguous refs mismatch", failures)
    require("row coverage and unique output-file coverage are separate dimensions" in contract["contractRules"], "contract rule missing row/output split", failures)

    guard = result["guardSummary"]
    require(guard["contractFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["contractZeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"guard should be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard["zeroCounters"][key] == 0, f"guard count should be zero: {key}", failures)

    require("the next static child lane can build a fixture matrix without runtime, Godot, Ghidra mutation, or renderer implementation" in result["claimBoundary"]["proves"], "claim boundary missing fixture matrix proof", failures)
    require("runtime texture pixels" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime texture pixel non-proof", failures)
    require("rebuild parity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing rebuild parity non-proof", failures)
    require(len(result["stopConditions"]) == 5, "stop condition count mismatch", failures)
    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore proof mirror mismatch", failures)

    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json",
        f"contractExtensionStatus={STATUS_TOKEN}",
        "sourceProofCount=5",
        "contractVocabularyTermCount=14",
        "modelRowsWithTextureRefs=352/352",
        "materialSidecarUniqueRefs=213",
        "materialSidecarFiles=213",
        "materialSidecarMissingRefs=0",
        "catalogMissingRefs=0",
        "ambiguousCatalogRefs=1",
        "embeddedDuplicateOutputBoundaryRows=32",
        "contractFalseGuardCount=39",
        "contractZeroCounterCount=33",
        "publicLeakCheck=PASS",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "runtimeTexturePixelsProven=false",
        "materialVisualCorrectnessProven=false",
        "materialShaderParityProven=false",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "runtimeObservationRows=0",
        "textureRuntimeEvidenceRows=0",
        "meshRuntimeEvidenceRows=0",
        "materialRuntimeEvidenceRows=0",
        "ghidraMutationRows=0",
        "executablePatchRows=0",
        "godotRows=0",
        "rebuildImplementationRows=0",
        "beProcessesAfterSelection=0",
    )
    plan_only_tokens = (
        "301",
        "232",
        "TEXT 18857",
        "MESH 3492",
        "GDIE 232",
        "601/601",
        "209/209",
        "206/206",
        "42/42",
        "847/847",
        "213/213",
        "139/139",
        "4050",
        "asset-material-sidecar-ledger.v1",
        "8574",
        "250335133",
        "1268",
        "212",
        "1` stem-only",
        "0` catalog-missing refs",
        "107",
        "28",
        "32",
        "model row",
        "row family",
        "model texture reference instance",
        "unique model texture ref",
        "mesh texture sidecar file",
        "exact filename match",
        "stem-only match",
        "catalog-mapped ref",
        "catalog-missing ref",
        "missing sidecar ref",
        "ambiguous catalog ref",
        "duplicate-output group",
        "duplicate row",
        "unique output file",
        "JPEG Huffman separate from inflate Huffman",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in common_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)
    plan_text = read_text(PLAN)
    for token in plan_only_tokens:
        require(token in plan_text, f"{PLAN.relative_to(ROOT)} missing token: {token}", failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md",
        "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json",
        STATUS_TOKEN,
        "contractVocabularyTermCount=14",
        "modelRowsWithTextureRefs=352/352",
        "materialSidecarUniqueRefs=213",
        "materialSidecarFiles=213",
        "materialSidecarMissingRefs=0",
        "catalogMissingRefs=0",
        "ambiguousCatalogRefs=1",
        "embeddedDuplicateOutputBoundaryRows=32",
        "contractFalseGuardCount=39",
        "contractZeroCounterCount=33",
        "publicLeakCheck=PASS",
        "Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, GAME_ASSETS_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed contract extension slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks contract extension active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed fixture matrix lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks fixture matrix active", failures)
    require(f"Completed {FOLLOWUP_SLICE}" in backlog, "backlog missing completed importer fixture harness lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}. Status: selected" not in backlog, "backlog still marks importer fixture harness lane active", failures)
    require(f"Completed {FOLLOWUP_MATERIALIZATION_SLICE}" in backlog, "backlog missing completed importer fixture harness materialization lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MATERIALIZATION_SLICE}. Status: selected" not in backlog, "backlog still marks importer fixture harness materialization lane active", failures)
    require(f"Completed {FOLLOWUP_CONSUMER_SLICE}" in backlog, "backlog missing completed importer fixture harness consumer dry-run lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_CONSUMER_SLICE}. Status: selected" not in backlog, "backlog still marks importer fixture harness consumer dry-run lane active", failures)
    require(f"Completed {FOLLOWUP_IMPLEMENTATION_READINESS_SLICE}" in backlog, "backlog missing completed implementation-readiness gate", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_IMPLEMENTATION_READINESS_SLICE}. Status: selected" not in backlog, "backlog still marks implementation-readiness gate active", failures)
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
        SOURCE_LEDGER_PROOF: (
            "Status: generated material/sidecar ledger proof complete, not runtime proof",
            "asset-material-sidecar-ledger.v1",
            "352/352",
            "1268",
            "213",
            "0` catalog-missing refs",
            "Embedded mesh duplicate-output caveat",
        ),
        COPIED_CORPUS_PROOF: (
            "301",
            "232",
            "TEXT 18857",
            "MESH 3492",
            "GDIE 232",
            "601/601",
            "209/209",
            "206/206",
            "42/42",
            "4050",
        ),
        ASSET_BRIDGE_PLAN: (
            "Material/sidecar ledger schema",
            "847/847",
            "213/213",
            "139/139",
            "352/352",
        ),
        MESH_CONTRACT: (
            "Model rows with material/texture-binding metadata | `352/352`",
            "Model texture sidecar refs covered | `213/213`",
        ),
        TEXTURE_CONTRACT: (
            "Wave1163",
            "17 CFastVB/CTexture/CDXTexture current-risk rows",
            "68 xref rows",
            "2779 instruction rows",
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
        scripts.get("test:texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_rebuild_contract_extension_proof_plan_probe.py --check",
        "missing package contract extension test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_source_ledger(failures)
    check_result(failures)
    check_docs(failures)
    check_source_docs(failures)
    check_progress_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after contract-extension probe", failures)

    if failures:
        print("Texture/mesh material sidecar rebuild-contract extension probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar rebuild-contract extension probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
