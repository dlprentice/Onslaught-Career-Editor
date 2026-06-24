#!/usr/bin/env python3
"""Validate texture/mesh material-sidecar private-corpus checklist population."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_safety_boundary import (
    AUTHORIZATION_GATES,
    BOUNDARY_STATUS,
    PRIVATE_CORPUS_CLASSES,
    PUBLIC_ALLOWED_OUTPUTS,
    PUBLIC_SKELETON_STATUS,
    REDACTED_FIELD_IDS,
    SAFETY_PACKET_ITEMS,
    STOP_CONDITIONS,
)
from texture_mesh_material_sidecar_importer_private_corpus_safety_packet_checklist import (
    CHECKLIST_GROUPS,
    CHECKLIST_POPULATION_STATUS,
    CHECKLIST_SCHEMA_VERSION,
    FALSE_GUARDS_CHECKLIST,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREFLIGHT_CHECKS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS_CHECKLIST,
    build_public_safe_checklist_rows,
    emit_private_corpus_safety_packet_checklist_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_safety_packet_checklist_population_proof_plan_2026-06-10.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_safety_packet_checklist.py"

SOURCE_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md"
SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json"
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

PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan"
FOLLOWUP_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"

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
    "private corpus coverage",
    "full corpus pass",
    "private manifest materialized",
    "private rows observed",
    "real importer complete",
    "real importer implementation complete",
    "real importer execution complete",
    "dry-run succeeded on private corpus",
    "private output review complete",
    "all sidecars resolved",
    "asset import complete",
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
    "rebuild-ready",
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


def check_source_boundary(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_RESULT)
    require(source["status"] == "PASS", "source boundary status mismatch", failures)
    require(source["privateCorpusSafetyBoundaryStatus"] == BOUNDARY_STATUS, "source boundary token mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source selected next scope mismatch", failures)
    require(source["sourcePublicContractSkeletonStatus"] == PUBLIC_SKELETON_STATUS, "source public skeleton token mismatch", failures)
    decision = source["boundaryDecision"]
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
        require(decision[key] is False, f"source boundary false guard changed: {key}", failures)
    require(decision["privateCorpusSafetyBoundaryDefined"] is True, "source boundary not defined", failures)
    require(decision["futurePrivateCorpusReadRequiresExplicitArm"] is True, "source future arm rule missing", failures)
    require(decision["requiresCopiedOrAppOwnedCorpusRoot"] is True, "source copied/app-owned root rule missing", failures)
    require(decision["requiresAppOwnedArtifactRoot"] is True, "source app-owned output rule missing", failures)
    check_no_bad_public_content(SOURCE_PROOF, failures)
    return source


def check_result(source: dict[str, Any], failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["privateCorpusSafetyPacketChecklistPopulationStatus"] == CHECKLIST_POPULATION_STATUS, "checklist status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourcePrivateCorpusSafetyBoundaryStatus"] == BOUNDARY_STATUS, "source boundary status mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    require(result["sourceEvidence"]["sourceProofCount"] == 9, "source proof count mismatch", failures)
    continuity = result["sourceBoundaryContinuity"]
    for key, expected in {
        "safetyBoundaryOnly": True,
        "privateCorpusSafetyBoundaryDefined": True,
        "sourcePublicContractSkeletonStatus": PUBLIC_SKELETON_STATUS,
        "sourceProofCount": 8,
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

    decision = result["checklistPopulationDecision"]
    for key in (
        "checklistPopulationOnly",
        "safetyPacketChecklistPopulated",
        "futureReadOnlyPrivateCorpusSliceSelectable",
        "futureReadOnlyPrivateCorpusUseAllowedWhenSelected",
        "futurePrivateCorpusReadRequiresSelectedReadOnlySlice",
        "blockedByMissingExplicitPrivateCorpusArm",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"checklist decision should be true: {key}", failures)
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
        require(decision[key] is False, f"checklist decision should be false: {key}", failures)
    require(decision["defaultChecklistRowStatus"] == "not-run", "default row status mismatch", failures)
    require(decision["defaultObservationStatus"] == "unobserved", "default observation status mismatch", failures)

    summary = result["checklistSummary"]
    for key, expected in {
        "checklistSchemaVersion": CHECKLIST_SCHEMA_VERSION,
        "checklistModule": "tools/texture_mesh_material_sidecar_importer_private_corpus_safety_packet_checklist.py",
        "checklistGroupCount": len(CHECKLIST_GROUPS),
        "checklistRowCount": 53,
        "safetyPacketChecklistItemRowCount": len(SAFETY_PACKET_ITEMS),
        "passedChecklistRowCount": 53,
        "failedChecklistRowCount": 0,
        "notRunChecklistRowCount": 53,
        "unobservedChecklistRowCount": 53,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "safetyPacketItemCount": len(SAFETY_PACKET_ITEMS),
        "authorizationGateCount": len(AUTHORIZATION_GATES),
        "privateCorpusClassCount": len(PRIVATE_CORPUS_CLASSES),
        "redactedFieldCount": len(REDACTED_FIELD_IDS),
        "publicAllowedOutputClassCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "allowedCurrentAction": "public-safe-checklist-population-only",
        "allowedFutureActionWhenSelected": "read-only-private-corpus-inventory-preflight-only",
    }.items():
        require(summary[key] == expected, f"checklist summary mismatch: {key}", failures)
    require(tuple(summary["checklistFunctions"]) == ("build_public_safe_checklist_rows", "validate_private_corpus_safety_packet_checklist", "emit_private_corpus_safety_packet_checklist_summary"), "checklist functions mismatch", failures)

    group_counts = {row["groupId"]: row for row in result["checklistGroups"]}
    for category, status, items in CHECKLIST_GROUPS:
        row = group_counts.get(category)
        require(row is not None, f"missing checklist group: {category}", failures)
        if row is not None:
            require(row["rowCount"] == len(items), f"checklist group count mismatch: {category}", failures)
            require(row["status"] == status, f"checklist group status mismatch: {category}", failures)
    require(tuple(result["safetyPacketItems"]) == SAFETY_PACKET_ITEMS, "safety packet rows mismatch", failures)
    require(tuple(result["authorizationGates"]) == AUTHORIZATION_GATES, "authorization gate rows mismatch", failures)
    require(tuple(result["futurePrivateCorpusClasses"]) == PRIVATE_CORPUS_CLASSES, "private corpus class rows mismatch", failures)
    require(tuple(result["redactionPolicy"]["redactedFields"]) == REDACTED_FIELD_IDS, "redacted field rows mismatch", failures)
    require(tuple(result["redactionPolicy"]["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public allowed outputs mismatch", failures)
    require(tuple(result["preflightChecks"]) == PREFLIGHT_CHECKS, "preflight checks mismatch", failures)

    module_rows = build_public_safe_checklist_rows()
    require(len(module_rows) == 53, "module checklist row count mismatch", failures)
    require(all(row["rowStatus"] == "not-run" for row in module_rows), "module row status mismatch", failures)
    require(all(row["observationStatus"] == "unobserved" for row in module_rows), "module row observation mismatch", failures)
    require(all(row["blockedByMissingExplicitPrivateCorpusArm"] is True for row in module_rows), "module row blocker mismatch", failures)
    require(all(row["privateValuePublished"] is False for row in module_rows), "module private value publication mismatch", failures)
    require(result["checklistSummaryFromModule"] == emit_private_corpus_safety_packet_checklist_summary(source), "module checklist summary mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS_CHECKLIST), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS_CHECKLIST), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)
    for key in FALSE_GUARDS_CHECKLIST:
        require(guard["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS_CHECKLIST:
        require(guard["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the private-corpus safety packet is populated as public-safe checklist rows" in proves, "claim boundary missing checklist proof", failures)
    require("private corpus reads and real importer execution remain unperformed in this slice" in proves, "claim boundary missing no-read proof", failures)
    for token in (
        "private asset import",
        "private corpus manifest materialization",
        "private corpus inventory",
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
        "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_safety_packet_checklist.py",
        f"privateCorpusSafetyPacketChecklistPopulationStatus={CHECKLIST_POPULATION_STATUS}",
        f"sourcePrivateCorpusSafetyBoundaryStatus={BOUNDARY_STATUS}",
        "sourceProofCount=9",
        f"sourcePublicContractSkeletonStatus={PUBLIC_SKELETON_STATUS}",
        "sourceBoundaryProofCount=8",
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
        "checklistPopulationOnly=true",
        "safetyPacketChecklistPopulated=true",
        "futureReadOnlyPrivateCorpusSliceSelectable=true",
        "futureReadOnlyPrivateCorpusUseAllowedWhenSelected=true",
        "futurePrivateCorpusReadRequiresSelectedReadOnlySlice=true",
        "blockedByMissingExplicitPrivateCorpusArm=true",
        "defaultChecklistRowStatus=not-run",
        "defaultObservationStatus=unobserved",
        "privateCorpusReadAuthorizationPresent=false",
        "privateAssetRead=false",
        "privateCorpusReadPerformed=false",
        "privateCorpusEnumeration=false",
        "privateRootExistenceChecked=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "checklistGroupCount=6",
        "checklistRowCount=53",
        "safetyPacketChecklistItemRowCount=10",
        "passedChecklistRowCount=53",
        "failedChecklistRowCount=0",
        "notRunChecklistRowCount=53",
        "unobservedChecklistRowCount=53",
        "observedChecklistRowCount=0",
        "rowStatusChangedCount=0",
        "preflightCheckCount=14",
        "passedPreflightCheckCount=14",
        "failedPreflightCheckCount=0",
        "safetyPacketItemCount=10",
        "authorizationGateCount=8",
        "privateCorpusClassCount=5",
        "redactedFieldCount=12",
        "publicAllowedOutputClassCount=6",
        "stopConditionCount=12",
        "falseGuardCount=51",
        "zeroCounterCount=42",
        "publicLeakCheck=PASS",
        "NOT_RUN_PUBLIC_CHECKLIST_ONLY",
        "privateCorpusReadRows=0",
        "privateAssetReadRows=0",
        "privateManifestRows=0",
        "privateArtifactRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "readOnlyInventoryRows=0",
        "privateImporterDryRunRows=0",
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
        "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.v1.json",
        CHECKLIST_POPULATION_STATUS,
        "sourcePrivateCorpusSafetyBoundaryStatus=" + BOUNDARY_STATUS,
        "checklistPopulationOnly=true",
        "safetyPacketChecklistPopulated=true",
        "futureReadOnlyPrivateCorpusSliceSelectable=true",
        "futureReadOnlyPrivateCorpusUseAllowedWhenSelected=true",
        "futurePrivateCorpusReadRequiresSelectedReadOnlySlice=true",
        "blockedByMissingExplicitPrivateCorpusArm=true",
        "defaultChecklistRowStatus=not-run",
        "defaultObservationStatus=unobserved",
        "checklistGroupCount=6",
        "checklistRowCount=53",
        "notRunChecklistRowCount=53",
        "unobservedChecklistRowCount=53",
        "observedChecklistRowCount=0",
        "rowStatusChangedCount=0",
        "preflightCheckCount=14",
        "safetyPacketItemCount=10",
        "authorizationGateCount=8",
        "privateCorpusClassCount=5",
        "redactedFieldCount=12",
        "falseGuardCount=51",
        "zeroCounterCount=42",
        "readOnlyInventoryRows=0",
        "privateImporterDryRunRows=0",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed checklist population slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed read-only inventory preflight slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed private boundary slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks checklist population active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks read-only inventory preflight active", failures)
    require(f"Completed {FOLLOWUP_MANIFEST_DRY_RUN_SLICE}" in backlog, "backlog missing completed read-only manifest dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MANIFEST_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks read-only manifest dry-run active", failures)
    require(f"Completed {FOLLOWUP_MANIFEST_MATERIALIZATION_SLICE}" in backlog, "backlog missing completed read-only manifest materialization", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MANIFEST_MATERIALIZATION_SLICE}. Status: selected" not in active, "active block still marks read-only manifest materialization active", failures)
    require(f"Completed {FOLLOWUP_MANIFEST_CONSUMER_VALIDATION_SLICE}" in backlog, "backlog missing completed read-only manifest consumer validation", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MANIFEST_CONSUMER_VALIDATION_SLICE}. Status: selected" not in active, "active block still marks read-only manifest consumer validation active", failures)
    require(f"Completed {FOLLOWUP_MANIFEST_ADAPTER_SLICE}" in backlog, "backlog missing completed redacted manifest importer contract adapter", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MANIFEST_ADAPTER_SLICE}. Status: selected" not in active, "active block still marks redacted manifest importer contract adapter active", failures)
    require(f"Completed {FOLLOWUP_MANIFEST_ADAPTER_DRY_RUN_SLICE}" in backlog, "backlog missing completed redacted manifest importer contract adapter dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_MANIFEST_ADAPTER_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks redacted manifest importer contract adapter dry-run active", failures)
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
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_safety_packet_checklist_population_proof_plan_probe.py --check",
        "missing package private-corpus checklist population test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "private-corpus checklist module missing", failures)
    source = check_source_boundary(failures)
    check_result(source, failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after checklist population probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer private-corpus checklist-population probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer private-corpus checklist-population probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
