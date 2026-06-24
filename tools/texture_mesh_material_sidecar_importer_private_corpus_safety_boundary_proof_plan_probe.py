#!/usr/bin/env python3
"""Validate texture/mesh material-sidecar private-corpus safety boundary."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_safety_boundary import (
    AUTHORIZATION_GATES,
    BOUNDARY_SCHEMA_VERSION,
    BOUNDARY_STATUS,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PRIVATE_CORPUS_CLASSES,
    PUBLIC_ALLOWED_OUTPUTS,
    PUBLIC_SKELETON_STATUS,
    REDACTED_FIELD_IDS,
    SAFETY_PACKET_ITEMS,
    STOP_CONDITIONS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    emit_private_corpus_safety_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_safety_boundary_proof_plan_2026-06-10.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_safety_boundary.py"

SOURCE_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md"
SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1.json"
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

FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"

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
    (re.compile(r"(?i)asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "private corpus validated",
    "private asset import complete",
    "private corpus manifest materialization complete",
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


def active_slice_block(text: str) -> str:
    marker = "## Active Proof Slice"
    start = text.find(marker)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + len(marker))
    return text[start:] if next_heading < 0 else text[start:next_heading]


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_source_public_skeleton(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_RESULT)
    require(source["status"] == "PASS", "source public skeleton status mismatch", failures)
    require(source["publicContractSkeletonStatus"] == PUBLIC_SKELETON_STATUS, "source public skeleton token mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source selected next scope mismatch", failures)
    decision = source["skeletonDecision"]
    require(decision["publicContractSkeletonImplemented"] is True, "source skeleton not implemented", failures)
    require(decision["realImporterImplementation"] is False, "source real importer implementation flag changed", failures)
    require(decision["realImporterExecuted"] is False, "source real importer execution flag changed", failures)
    require(decision["privateAssetReadAuthorizationPresent"] is False, "source private asset authorization flag changed", failures)
    require(decision["operatorPrivateOutputReviewAvailable"] is False, "source operator private review flag changed", failures)
    skeleton = source["publicContractSkeleton"]
    require(skeleton["contractInterfaceCount"] == 6, "source contract interface count mismatch", failures)
    require(skeleton["implementedContractInterfaceCount"] == 6, "source implemented contract interface count mismatch", failures)
    require(skeleton["contractFunctionCount"] == 2, "source contract function count mismatch", failures)
    require(skeleton["publicContractSkeletonImplementationRows"] == 1, "source public skeleton row count mismatch", failures)
    require(skeleton["failedSkeletonContractChecks"] == 0, "source failed skeleton check mismatch", failures)
    check_no_bad_public_content(SOURCE_PROOF, failures)
    return source


def check_result(source: dict[str, Any], failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["privateCorpusSafetyBoundaryStatus"] == BOUNDARY_STATUS, "boundary status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourcePublicContractSkeletonStatus"] == PUBLIC_SKELETON_STATUS, "source public skeleton status mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    require(result["sourceEvidence"]["sourceProofCount"] == 8, "source proof count mismatch", failures)
    continuity = result["sourcePublicSkeletonContinuity"]
    for key, expected in {
        "publicContractSkeletonImplemented": True,
        "contractSkeletonValidationExecuted": True,
        "contractInterfaceCount": 6,
        "implementedContractInterfaceCount": 6,
        "contractFunctionCount": 2,
        "publicContractSkeletonImplementationRows": 1,
        "validationSummaryRows": 1,
        "skeletonContractCheckCount": 46,
        "failedSkeletonContractChecks": 0,
        "sourceConsumedFixtureRowCount": 8,
        "publicEdgeCaseIdCount": 2,
        "uniqueModelTextureRefUnion": 213,
        "familyUniqueRefsAreNotAdditive": True,
        "embeddedDuplicateOutputSurplusRows": 32,
        "publicLeakCheck": "PASS",
    }.items():
        require(continuity[key] == expected, f"source continuity mismatch: {key}", failures)

    decision = result["boundaryDecision"]
    for key, expected in {
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
        "privateManifestMaterialized": False,
        "privateManifestRowsObserved": False,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "futurePrivateCorpusReadRequiresExplicitArm": True,
        "requiresCopiedOrAppOwnedCorpusRoot": True,
        "requiresAppOwnedArtifactRoot": True,
        "installedGameMutationAllowed": False,
        "originalExecutableMutationAllowed": False,
        "publicPrivateSeparationRequired": True,
        "selectedNextImplementationSliceCount": 1,
    }.items():
        require(decision[key] == expected, f"boundary decision mismatch: {key}", failures)

    packet = result["privateCorpusSafetyPacket"]
    require(packet["boundarySchemaVersion"] == BOUNDARY_SCHEMA_VERSION, "boundary schema mismatch", failures)
    require(packet["boundaryModule"] == "tools/texture_mesh_material_sidecar_importer_private_corpus_safety_boundary.py", "boundary module path mismatch", failures)
    require(tuple(packet["boundaryFunctions"]) == ("validate_private_corpus_safety_boundary", "emit_private_corpus_safety_summary"), "boundary functions mismatch", failures)
    for key, expected in {
        "safetyPacketItemCount": len(SAFETY_PACKET_ITEMS),
        "authorizationGateCount": len(AUTHORIZATION_GATES),
        "privateCorpusClassCount": len(PRIVATE_CORPUS_CLASSES),
        "redactedFieldCount": len(REDACTED_FIELD_IDS),
        "publicAllowedOutputClassCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
        "allowedCurrentAction": "public-safe-private-corpus-boundary-definition-only",
        "allowedFutureActionAfterArm": "private-corpus-safety-packet-checklist-population-only",
    }.items():
        require(packet[key] == expected, f"safety packet mismatch: {key}", failures)

    require(tuple(result["safetyPacketItems"]) == SAFETY_PACKET_ITEMS, "safety packet item ids mismatch", failures)
    require(tuple(result["authorizationGates"]) == AUTHORIZATION_GATES, "authorization gate ids mismatch", failures)
    require(tuple(result["futurePrivateCorpusClasses"]) == PRIVATE_CORPUS_CLASSES, "private corpus class ids mismatch", failures)

    redaction = result["redactionPolicy"]
    require(redaction["redactionPolicy"] == "public-safe-class-count-status-token-only", "redaction policy mismatch", failures)
    require(redaction["redactedFieldCount"] == len(REDACTED_FIELD_IDS), "redacted field count mismatch", failures)
    require(tuple(redaction["redactedFields"]) == REDACTED_FIELD_IDS, "redacted field ids mismatch", failures)
    require(tuple(redaction["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "allowed public outputs mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction leak check mismatch", failures)

    require(result["boundarySummary"] == emit_private_corpus_safety_summary(source), "module boundary summary mismatch", failures)
    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guard["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)

    require(tuple(result["stopConditions"]) == STOP_CONDITIONS, "stop condition ids mismatch", failures)
    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the completed public contract skeleton has an explicit private-corpus safety boundary" in proves, "claim boundary missing boundary proof", failures)
    require("private corpus reads and real importer execution remain unperformed in this slice" in proves, "claim boundary missing no-read proof", failures)
    for token in (
        "private asset import",
        "private corpus manifest materialization",
        "real importer implementation",
        "real importer execution",
        "runtime texture parser behavior",
        "runtime texture pixels",
        "runtime mesh loading or skinning",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in unproven, f"claim boundary missing unproven token: {token}", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        PREVIOUS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_safety_boundary.py",
        f"privateCorpusSafetyBoundaryStatus={BOUNDARY_STATUS}",
        f"sourcePublicContractSkeletonStatus={PUBLIC_SKELETON_STATUS}",
        "sourceProofCount=8",
        "publicContractSkeletonImplemented=true",
        "contractSkeletonValidationExecuted=true",
        "contractInterfaceCount=6",
        "implementedContractInterfaceCount=6",
        "contractFunctionCount=2",
        "publicContractSkeletonImplementationRows=1",
        "validationSummaryRows=1",
        "skeletonContractCheckCount=46",
        "failedSkeletonContractChecks=0",
        "sourceConsumedFixtureRowCount=8",
        "publicEdgeCaseIdCount=2",
        "uniqueModelTextureRefUnion=213",
        "familyUniqueRefsAreNotAdditive=true",
        "embeddedDuplicateOutputSurplusRows=32",
        "safetyBoundaryOnly=true",
        "privateCorpusSafetyBoundaryDefined=true",
        "privateCorpusReadAuthorizationPresent=false",
        "explicitImporterImplementationArmPresent=false",
        "operatorPrivateOutputReviewAvailable=false",
        "privateAssetRead=false",
        "privateCorpusReadPerformed=false",
        "privateCorpusEnumeration=false",
        "privateRootExistenceChecked=false",
        "privateAssetReadPerformed=false",
        "privateManifestMaterialized=false",
        "privateManifestRowsObserved=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "futurePrivateCorpusReadRequiresExplicitArm=true",
        "requiresCopiedOrAppOwnedCorpusRoot=true",
        "requiresAppOwnedArtifactRoot=true",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "publicPrivateSeparationRequired=true",
        "safetyPacketItemCount=10",
        "authorizationGateCount=8",
        "privateCorpusClassCount=5",
        "redactedFieldCount=12",
        "publicAllowedOutputClassCount=6",
        "stopConditionCount=12",
        "falseGuardCount=45",
        "zeroCounterCount=36",
        "publicLeakCheck=PASS",
        "privateCorpusReadRows=0",
        "privateAssetReadRows=0",
        "privateManifestRows=0",
        "privateArtifactRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "beProcessesAfterPrivateCorpusBoundary=0",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in common_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)


def check_front_doors_and_package(failures: list[str]) -> None:
    front_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json",
        BOUNDARY_STATUS,
        "sourcePublicContractSkeletonStatus=" + PUBLIC_SKELETON_STATUS,
        "privateCorpusSafetyBoundaryDefined=true",
        "futurePrivateCorpusReadRequiresExplicitArm=true",
        "requiresCopiedOrAppOwnedCorpusRoot=true",
        "requiresAppOwnedArtifactRoot=true",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "safetyPacketItemCount=10",
        "authorizationGateCount=8",
        "privateCorpusClassCount=5",
        "redactedFieldCount=12",
        "falseGuardCount=45",
        "zeroCounterCount=36",
        "privateCorpusReadRows=0",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
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
    active = active_slice_block(backlog)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed private-corpus boundary slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed public skeleton slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed safety packet checklist population slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks private boundary active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks safety packet checklist population active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE}" in backlog, "backlog missing completed private corpus read-only inventory preflight", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only inventory preflight active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only manifest dry-run active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest materialization", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only manifest materialization active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest consumer validation", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only manifest consumer validation active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE}" in backlog, "backlog missing completed private corpus redacted manifest importer contract adapter", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE}. Status: selected" not in active, "active block still marks private corpus redacted manifest importer contract adapter active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE}" in backlog, "backlog missing completed private corpus redacted manifest importer contract adapter dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks private corpus redacted manifest importer contract adapter dry-run active", failures)
    require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active, "active block missing private corpus real importer dry-run harness checklist population", failures)
    require(active.count("The selected active static-to-proof slice is ") == 1, "active block should have exactly one active slice sentence", failures)

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
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_safety_boundary_proof_plan_probe.py --check",
        "missing package private-corpus safety boundary test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "private-corpus safety boundary module missing", failures)
    source = check_source_public_skeleton(failures)
    check_result(source, failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after private boundary probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer private-corpus safety-boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer private-corpus safety-boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
