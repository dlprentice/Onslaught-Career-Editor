#!/usr/bin/env python3
"""Validate the post-PhysicsScript static-to-proof next-safe-slice refresh."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json"
READINESS = ROOT / "release" / "readiness" / "static_to_proof_post_physics_script_fixture_next_safe_slice_selection_refresh_2026-06-10.md"

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

ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.v1.json"
ASSET_PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
COPIED_CORPUS = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
MATERIAL_LEDGER = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"

THIS_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"
PREVIOUS_SLICE = "PhysicsScript Fixture Family Completion Rollup Proof Plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan"
FOLLOWUP_SLICE = "Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan"
FOLLOWUP_NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan"
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
STATUS_TOKEN = "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh-complete-texture-mesh-material-sidecar-contract-extension-selected"

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
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "completeValueIdSemanticsProven",
    "all185PairsSemanticallyNamed",
    "rawStringIdentityProven",
    "rawNumericMeaningProven",
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
    "runtimeObjectIdentityProven",
    "runtimeWorldLoadingProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "privateAssetPublication",
    "publicPrivateProofLeak",
)

ZERO_COUNTS = (
    "runtimeObservationRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeWeaponRows",
    "runtimeRoundRows",
    "runtimeProjectileRows",
    "textureRuntimeEvidenceRows",
    "meshRuntimeEvidenceRows",
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
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime physicsscript behavior proven",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    rollup = read_json(ROLLUP)

    require(result["schemaVersion"] == "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["selectionRefreshStatus"] == STATUS_TOKEN, "selection refresh status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedChildScope"] == NEXT_SCOPE, "selected child scope mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk focused mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["selectionAccounting"]
    require(accounting["consultCount"] == 2, "consult count mismatch", failures)
    require(accounting["candidateCount"] == 4, "candidate count mismatch", failures)
    require(accounting["selectedCandidateRank"] == 1, "selected rank mismatch", failures)
    require(accounting["selectedSourceProofCount"] == 5, "selected source proof count mismatch", failures)
    require(accounting["completedPhysicsScriptFixtureFamilyCount"] == 9, "completed PhysicsScript fixture family count mismatch", failures)
    require(accounting["remainingPhysicsScriptFixtureFamilyCount"] == 0, "remaining PhysicsScript fixture family count mismatch", failures)
    require(accounting["fixturePlanDocCount"] == 9, "fixture doc count mismatch", failures)
    require(accounting["fixturePlanSchemaCount"] == 9, "fixture schema count mismatch", failures)
    require(accounting["fixtureProofPlanProbeCount"] == 9, "fixture probe count mismatch", failures)
    require(accounting["sourceMirrorPairCount"] == 18, "source mirror pair count mismatch", failures)
    require(accounting["selectedValueInterfaceRowCount"] == 87, "selected value row count mismatch", failures)
    require(accounting["selectedObservedValueIdCount"] == 72, "observed value id count mismatch", failures)
    require(accounting["selectedFactoryOnlyValueIdCount"] == 15, "factory-only value id count mismatch", failures)
    require(accounting["selectedUnselectedObservedValueIdCount"] == 113, "unselected observed value id count mismatch", failures)
    require(accounting["selectedTopLevelRecordCount"] == 777, "top-level count mismatch", failures)
    require(accounting["selectedValueNodeCount"] == 6803, "value node count mismatch", failures)
    require(accounting["physicsScriptStatementValuePairCount"] == 185, "statement/value pair count mismatch", failures)
    require(accounting["physicsScriptRawValuePayloadBytesPreserved"] == 73796, "raw value bytes mismatch", failures)
    require(accounting["selectedPayloadShapeCaseCount"] == 85, "payload shape count mismatch", failures)
    require(accounting["selectedScalar4ShapePayloadCount"] == 1151, "scalar4 payload count mismatch", failures)
    require(accounting["selectedOwnedStringShapePayloadCount"] == 1186, "owned string payload count mismatch", failures)
    require(accounting["selectedTwoScalarShapePayloadCount"] == 13, "two-scalar payload count mismatch", failures)
    require(accounting["selectedThreeScalarShapePayloadCount"] == 101, "three-scalar payload count mismatch", failures)
    require(accounting["selectedRawPreservedOtherShapePayloadCount"] == 259, "raw-preserved payload count mismatch", failures)
    require(accounting["factoryOnlyBoundaryFamilyCount"] == 6, "factory-only boundary family count mismatch", failures)
    require(accounting["unselectedObservedBoundaryFamilyCount"] == 5, "unselected observed boundary family count mismatch", failures)
    require(accounting["mixedPayloadBoundaryFamilyCount"] == 7, "mixed payload boundary family count mismatch", failures)
    require(accounting["materialSidecarModelRowsWithRefs"] == "352/352", "material sidecar model rows mismatch", failures)
    require(accounting["materialSidecarUniqueRefs"] == 213, "material sidecar unique refs mismatch", failures)
    require(accounting["materialSidecarFiles"] == 213, "material sidecar file count mismatch", failures)
    require(accounting["materialSidecarMissingRefs"] == 0, "material sidecar missing refs mismatch", failures)
    require(accounting["catalogMissingRefs"] == 0, "catalog missing refs mismatch", failures)
    require(accounting["selectionFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["selectionZeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    require(rollup["physicsScriptFixtureFamilyCompletionRollupStatus"] == result["sourceEvidence"]["physicsScriptFixtureFamilyCompletionRollup"]["statusToken"], "rollup source status mismatch", failures)
    require(rollup["selectedNextSlice"] == THIS_SLICE, "rollup selected next slice mismatch", failures)
    rollup_counts = rollup["fixtureCompletionAccounting"]
    require(rollup_counts["completedFixtureFamilyCount"] == 9, "rollup completed family count mismatch", failures)
    require(rollup_counts["remainingFixtureFamilyCount"] == 0, "rollup remaining family count mismatch", failures)
    require(rollup_counts["sourceMirrorPairCount"] == 18, "rollup mirror count mismatch", failures)
    require(rollup_counts["selectedValueInterfaceRowCount"] == 87, "rollup selected value count mismatch", failures)
    require(rollup_counts["selectedPayloadShapeCaseCount"] == 85, "rollup payload shape count mismatch", failures)
    require(rollup_counts["selectedScalar4ShapePayloadCount"] == 1151, "rollup scalar4 count mismatch", failures)
    require(rollup_counts["selectedOwnedStringShapePayloadCount"] == 1186, "rollup owned string count mismatch", failures)
    require(rollup_counts["selectedRawValuePayloadBytesPreserved"] == 73796, "rollup raw payload bytes mismatch", failures)

    ranks = result["candidateRanking"]
    require(len(ranks) == 4, "candidate ranking length mismatch", failures)
    require(ranks[0]["rank"] == 1 and ranks[0]["decision"] == "selected", "selected candidate row mismatch", failures)
    require(ranks[0]["lane"] == NEXT_SLICE, "selected lane mismatch", failures)

    not_reselected = set(result["notReselectedCompletedPhysicsScriptFixtureFamilies"])
    for token in ("explosion", "spawner", "hazard", "feature", "component", "weapon", "round", "weapon-mode", "unit", PREVIOUS_SLICE):
        require(token in not_reselected, f"missing not-reselected token: {token}", failures)

    guard = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard["zeroCounters"][key] == 0, f"guard count must be zero: {key}", failures)

    require(len(result["futureEvidenceRequirements"]) == 5, "future requirement count mismatch", failures)
    require(len(result["stopConditions"]) == 5, "stop condition count mismatch", failures)
    require("the selected next child lane is the Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan" in result["claimBoundary"]["proves"], "claim boundary missing selected child proof", failures)
    require("runtime texture parser behavior" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime texture parser non-proof", failures)
    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)
    require(no_bea_process_running(), "BEA process is running after selection-refresh probe", failures)


def check_source_docs(failures: list[str]) -> None:
    source_requirements = {
        ASSET_PLAN: (
            "Scope: texture/resource/decode plus mesh asset bridge",
            "Material/sidecar ledger schema",
            "847/847",
            "213/213",
            "139/139",
            "352/352",
        ),
        COPIED_CORPUS: (
            "301",
            "232",
            "Top-level archive chunks | `TEXT 18857`, `MESH 3492`, `GDIE 232`",
            "Loose texture export lane | `847` attempted, `847` succeeded, `0` failed, `0` skipped",
            "Loose mesh export lane | `213` attempted, `213` succeeded, `0` failed, `0` skipped",
            "Embedded mesh export lane | `139` attempted, `139` succeeded, `0` failed, `0` skipped",
            "Catalog totals | `828` textures, `213` loose meshes, `139` embedded meshes, `66` videos, `2571` language rows, `233` goodies, `4050` total rows",
        ),
        MATERIAL_LEDGER: (
            "Status: generated material/sidecar ledger proof complete, not runtime proof",
            "Model rows with texture refs | `352/352`",
            "Unique model texture refs | `213`",
            "Mesh texture sidecar files | `213`",
            "Rows with missing sidecar refs | `0` missing sidecar rows",
            "Unique refs missing catalog rows | `0` catalog-missing refs",
            "Ambiguous catalog refs | `1` ambiguous catalog ref",
            "Embedded mesh duplicate-output caveat | `107` unique output files from `139` rows, `28` duplicate-output groups, `32` duplicate rows",
        ),
        MESH_CONTRACT: (
            "## Asset Bridge Counts",
            "Model rows with material/texture-binding metadata | `352/352`",
            "Model texture sidecar refs covered | `213/213`",
            "Runtime texture decode pixels or GPU upload results.",
            "Native textured/animated WinUI rendering.",
            "material visual parity",
        ),
    }
    for path, tokens in source_requirements.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing source token: {token}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore proof mirror mismatch", failures)
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json",
        f"selectionRefreshStatus={STATUS_TOKEN}",
        "selectedChildLane=Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan",
        "selectedChildScope=texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=5",
        "completedPhysicsScriptFixtureFamilyCount=9",
        "remainingPhysicsScriptFixtureFamilyCount=0",
        "fixturePlanDocCount=9",
        "fixturePlanSchemaCount=9",
        "fixtureProofPlanProbeCount=9",
        "sourceMirrorPairCount=18",
        "selectedValueInterfaceRowCount=87",
        "selectedObservedValueIdCount=72",
        "selectedFactoryOnlyValueIdCount=15",
        "selectedUnselectedObservedValueIdCount=113",
        "selectedPayloadShapeCaseCount=85",
        "selectedScalar4ShapePayloadCount=1151",
        "selectedOwnedStringShapePayloadCount=1186",
        "selectedTwoScalarShapePayloadCount=13",
        "selectedThreeScalarShapePayloadCount=101",
        "selectedRawPreservedOtherShapePayloadCount=259",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
        "factoryOnlyBoundaryFamilyCount=6",
        "unselectedObservedBoundaryFamilyCount=5",
        "mixedPayloadBoundaryFamilyCount=7",
        "materialSidecarModelRowsWithRefs=352/352",
        "materialSidecarUniqueRefs=213",
        "materialSidecarFiles=213",
        "materialSidecarMissingRefs=0",
        "catalogMissingRefs=0",
        "selectionFalseGuardCount=45",
        "selectionZeroCounterCount=35",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "runtimeExecution=false",
        "beLaunch=false",
        "screenshotCapture=false",
        "privateFrameReviewPerformed=false",
        "sourceSelectionProven=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "runtimePhysicsScriptBehaviorProven=false",
        "serializedPhysicsScriptCompletenessProven=false",
        "runtimeTextureParserBehaviorProven=false",
        "runtimeTexturePixelsProven=false",
        "runtimeMeshLoadingProven=false",
        "runtimeDirect3DUploadProven=false",
        "materialVisualCorrectnessProven=false",
        "materialShaderParityProven=false",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "runtimeObservationRows=0",
        "physicsScriptRuntimeEvidenceRows=0",
        "textureRuntimeEvidenceRows=0",
        "meshRuntimeEvidenceRows=0",
        "materialVisualReviewRows=0",
        "ghidraMutationRows=0",
        "executablePatchRows=0",
        "godotRows=0",
        "rebuildImplementationRows=0",
        "beProcessesAfterSelection=0",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.md",
        "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json",
        STATUS_TOKEN,
        "complete post-PhysicsScript fixture next safe slice selection",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=5",
        "completedPhysicsScriptFixtureFamilyCount=9",
        "remainingPhysicsScriptFixtureFamilyCount=0",
        "materialSidecarModelRowsWithRefs=352/352",
        "materialSidecarUniqueRefs=213",
        "materialSidecarFiles=213",
        "materialSidecarMissingRefs=0",
        "catalogMissingRefs=0",
        "selectionFalseGuardCount=45",
        "selectionZeroCounterCount=35",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "Texture/Mesh Material Sidecar Ledger Proof",
        "Texture/Mesh Asset Bridge Copied-Corpus Proof",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed post-PhysicsScript selection refresh", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks post-PhysicsScript selection refresh active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed texture/material sidecar contract extension lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks texture/material sidecar contract extension lane active", failures)
    require(f"Completed {FOLLOWUP_SLICE}" in backlog, "backlog missing completed texture/material fixture matrix lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}. Status: selected" not in backlog, "backlog still marks texture/material fixture matrix lane active", failures)
    require(f"Completed {FOLLOWUP_NEXT_SLICE}" in backlog, "backlog missing completed texture/material importer fixture harness lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks texture/material importer fixture harness lane active", failures)
    require(f"Completed {FOLLOWUP_MATERIALIZATION_SLICE}" in backlog, "backlog missing completed texture/material importer fixture harness materialization lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MATERIALIZATION_SLICE}. Status: selected" not in backlog, "backlog still marks texture/material importer fixture harness materialization lane active", failures)
    require(f"Completed {FOLLOWUP_CONSUMER_SLICE}" in backlog, "backlog missing completed texture/material importer fixture harness consumer dry-run lane", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_CONSUMER_SLICE}. Status: selected" not in backlog, "backlog still marks texture/material importer fixture harness consumer dry-run lane active", failures)
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
    require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Readiness Gate Proof Plan. Status: selected" in backlog, "active block missing private corpus redacted manifest importer contract adapter materialization consumer validation", failures)
    require("next selected child lane is Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan" in backlog, "backlog missing fixture matrix next selected child lane", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh")
        == r"py -3 tools\static_to_proof_post_physics_script_fixture_next_safe_slice_selection_refresh_probe.py --check",
        "missing package post-PhysicsScript selection-refresh test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_source_docs(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("Static-to-proof post-PhysicsScript fixture next safe slice selection refresh probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static-to-proof post-PhysicsScript fixture next safe slice selection refresh probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
