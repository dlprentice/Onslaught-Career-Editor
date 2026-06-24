#!/usr/bin/env python3
"""Validate private-corpus real-importer dry-run harness boundary proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import REQUIRED_ARCHIVE_CLASSES
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary import (
    ALLOWED_FUTURE_INPUT_CLASSES,
    FALSE_GUARDS,
    HARNESS_STOP_CONDITIONS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
    REDACTED_FIELDS,
    REQUIRED_FUTURE_ARTIFACT_CLASSES,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_boundary_proof,
    build_public_safe_real_importer_dry_run_harness_boundary_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_readiness_gate import (
    REAL_IMPORTER_READINESS_INTERFACES,
    REAL_IMPORTER_READINESS_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary.py"

FOLLOWUP_CHECKLIST_VALIDATION_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan"
)
FOLLOWUP_CHECKLIST_READINESS_GATE_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan"
)
FOLLOWUP_CHECKLIST_READINESS_GATE_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan"
)

SOURCE_READINESS_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan.v1.json"
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

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
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
    "private asset content parsed",
    "raw private corpus manifest consumed",
    "private raw manifest rows consumed",
    "real importer complete",
    "real importer implementation complete",
    "real importer execution complete",
    "private importer dry-run complete",
    "real importer dry-run complete",
    "dry-run succeeded on private corpus assets",
    "asset import complete",
    "private asset import complete",
    "generated asset output complete",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    source_readiness = read_json(SOURCE_READINESS_RESULT)
    module_summary = build_public_safe_real_importer_dry_run_harness_boundary_summary(source_readiness)
    module_proof = build_public_safe_real_importer_dry_run_harness_boundary_proof(module_summary)
    require(result == module_proof, "tracked harness-boundary proof differs from module rebuild", failures)

    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["privateCorpusRealImporterDryRunHarnessBoundaryStatus"] == REAL_IMPORTER_HARNESS_BOUNDARY_STATUS, "harness status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceRealImporterReadinessGateStatus"] == REAL_IMPORTER_READINESS_STATUS, "source readiness continuity mismatch", failures)
    require(result["sourceEvidence"]["sourceProofCount"] == 22, "source proof count mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    decision = result["realImporterHarnessBoundaryDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessBoundaryOnly",
        "realImporterReadinessGateProofConsumed",
        "realImporterReadinessGateProofContinuityValidated",
        "realImporterReadinessRowsConsumedByHarnessBoundary",
        "realImporterDryRunHarnessBoundaryDefined",
        "harnessBoundaryInputClassesDefined",
        "harnessBoundaryOutputClassesDefined",
        "harnessBoundaryStopConditionsDefined",
        "harnessBoundaryRefusalGuardsValidated",
        "harnessBoundaryArchiveClassOrderValidated",
        "harnessBoundaryArchiveClassCountsValidated",
        "harnessBoundaryInterfacesValidated",
        "harnessBoundaryEmitsOnlyPublicSafeRows",
        "harnessChecklistPopulationLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"decision should be true: {key}", failures)
    for key in (
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "realImporterDryRunHarnessExecuted",
        "realImporterDryRunHarnessArmed",
        "realImporterDryRunHarnessExecutedInBoundarySlice",
        "realImporterDryRunHarnessOutputPublished",
        "realImporterDryRunHarnessBoundaryReadPrivateInputs",
        "realImporterDryRunHarnessBoundaryPublishedPrivateInput",
        "privateHarnessBoundaryArtifactPublished",
        "harnessChecklistPopulationExecuted",
        "harnessChecklistMaterialized",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision[key] is False, f"decision should be false: {key}", failures)

    contract = result["realImporterHarnessBoundaryContract"]
    expected_counts = {
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "realImporterDryRunHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterReadinessRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundaryRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundaryArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessBoundarySummaryRows": 1,
        "consumerArchiveTotalCount": 301,
        "baseArchiveClassCount": 1,
        "frontendArchiveClassCount": 1,
        "loadingArchiveClassCount": 1,
        "numericLevelArchiveClassCount": 66,
        "goodieArchiveClassCount": 232,
        "unknownAyaArchiveClassCount": 0,
        "harnessAllowedFutureInputClassCount": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessRequiredFutureArtifactClassCount": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessStopConditionCount": len(HARNESS_STOP_CONDITIONS),
        "publicSafeHarnessBoundaryArtifactRows": 1,
    }
    for key, expected in expected_counts.items():
        require(contract[key] == expected, f"harness boundary count mismatch: {key}", failures)
    require(tuple(contract["sourceRealImporterReadinessInterfaces"]) == REAL_IMPORTER_READINESS_INTERFACES, "source readiness interface list mismatch", failures)
    require(tuple(contract["realImporterDryRunHarnessBoundaryInterfaces"]) == REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES, "harness boundary interface list mismatch", failures)
    require(tuple(contract["allowedFutureInputClasses"]) == ALLOWED_FUTURE_INPUT_CLASSES, "allowed future input list mismatch", failures)
    require(tuple(contract["requiredFutureArtifactClasses"]) == REQUIRED_FUTURE_ARTIFACT_CLASSES, "required future artifact list mismatch", failures)
    require(tuple(contract["harnessStopConditions"]) == HARNESS_STOP_CONDITIONS, "stop condition list mismatch", failures)
    rows = contract["harnessBoundaryRowsBody"]
    require([row["sourceArchiveClass"] for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "harness boundary row order mismatch", failures)
    for row in rows:
        require(row["futureHarnessChecklistPopulationAllowed"] is True, "future checklist row flag mismatch", failures)
        require(row["futureRealImporterDryRunHarnessRequiresLaterArm"] is True, "future arm row flag mismatch", failures)
        require(row["directRealImporterDryRunAllowedHere"] is False, "direct dry-run allowance row mismatch", failures)
        require(row["harnessBoundaryPrivateIdentifiersPresent"] is False, "private identifier row guard mismatch", failures)
        for key in (
            "rawPathRows",
            "rawFilenameRows",
            "rawStemRows",
            "rawHashRows",
            "byteLengthRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "actualAssetImportRows",
            "generatedAssetRows",
            "generatedDryRunOutputRows",
            "privateDryRunRows",
            "realImporterDryRunRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunHarnessOutputRows",
            "realImporterDryRunHarnessTraceRows",
            "harnessChecklistRows",
            "rawDryRunTraceRows",
        ):
            require(row[key] == 0, f"harness row zero counter mismatch: {key}", failures)

    redaction = result["redactionPolicy"]
    require(redaction["publicAllowedOutputCount"] == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction["redactedFieldCount"] == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public outputs mismatch", failures)
    require(tuple(redaction["redactedFields"]) == REDACTED_FIELDS, "redacted fields mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction public leak check mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard[key] == 0, f"zero counter mismatch: {key}", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)

    unproven = result["claimBoundary"]["doesNotProve"]
    for token in (
        "private asset content parsing",
        "private raw manifest consumption",
        "real importer implementation",
        "real importer execution",
        "private importer dry run",
        "real importer dry run",
        "real importer dry-run harness execution",
        "harness checklist population",
        "actual asset import",
        "generated asset outputs",
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary.py",
        f"privateCorpusRealImporterDryRunHarnessBoundaryStatus={REAL_IMPORTER_HARNESS_BOUNDARY_STATUS}",
        f"sourceRealImporterReadinessGateStatus={REAL_IMPORTER_READINESS_STATUS}",
        "sourceProofCount=22",
        "privateCorpusRealImporterDryRunHarnessBoundaryOnly=true",
        "realImporterReadinessGateProofConsumed=true",
        "realImporterReadinessGateProofContinuityValidated=true",
        "realImporterReadinessRowsConsumedByHarnessBoundary=true",
        "realImporterDryRunHarnessBoundaryDefined=true",
        "harnessBoundaryInputClassesDefined=true",
        "harnessBoundaryOutputClassesDefined=true",
        "harnessBoundaryStopConditionsDefined=true",
        "harnessBoundaryRefusalGuardsValidated=true",
        "harnessBoundaryArchiveClassOrderValidated=true",
        "harnessBoundaryArchiveClassCountsValidated=true",
        "harnessBoundaryInterfacesValidated=true",
        "harnessBoundaryEmitsOnlyPublicSafeRows=true",
        "harnessChecklistPopulationLaneSelected=true",
        "realImporterHarnessBoundaryInputMode=tracked-public-safe-real-importer-readiness-gate-proof-json",
        "realImporterHarnessBoundaryOutputMode=public-safe-harness-boundary-class-count-status-token-rows",
        "selectedNextLaneClass=private-corpus real importer dry-run harness checklist population without execution",
        "sourceRealImporterReadinessInterfaceCount=8",
        "realImporterDryRunHarnessBoundaryInterfaceCount=10",
        "realImporterReadinessRowsConsumed=5",
        "harnessBoundaryRows=5",
        "harnessBoundaryArchiveClassRows=5",
        "harnessBoundarySummaryRows=1",
        "consumerArchiveTotalCount=301",
        "harnessAllowedFutureInputClassCount=5",
        "harnessRequiredFutureArtifactClassCount=6",
        "harnessStopConditionCount=12",
        "publicSafeHarnessBoundaryArtifactRows=1",
        "publicAllowedOutputCount=33",
        "redactedFieldCount=28",
        "falseGuardCount=85",
        "zeroCounterCount=69",
        "privateAssetContentRead=false",
        "privateArchiveBytesRead=false",
        "rawPrivateManifestConsumed=false",
        "rawPrivateManifestRowsConsumed=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "realImporterDryRunHarnessExecuted=false",
        "realImporterDryRunHarnessArmed=false",
        "realImporterDryRunHarnessExecutedInBoundarySlice=false",
        "realImporterDryRunHarnessOutputPublished=false",
        "realImporterDryRunHarnessBoundaryReadPrivateInputs=false",
        "realImporterDryRunHarnessBoundaryPublishedPrivateInput=false",
        "privateHarnessBoundaryArtifactPublished=false",
        "harnessChecklistPopulationExecuted=false",
        "harnessChecklistMaterialized=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "generatedDryRunOutputRows=0",
        "outputArtifactRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
        "rawTextureRefRows=0",
        "rawMeshRefRows=0",
        "realImporterDryRunRows=0",
        "realImporterDryRunHarnessRows=0",
        "realImporterDryRunHarnessOutputRows=0",
        "realImporterDryRunHarnessTraceRows=0",
        "harnessChecklistRows=0",
        "publicLeakCheck=PASS",
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json",
        REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "sourceRealImporterReadinessGateStatus=" + REAL_IMPORTER_READINESS_STATUS,
        "privateCorpusRealImporterDryRunHarnessBoundaryOnly=true",
        "realImporterDryRunHarnessBoundaryDefined=true",
        "harnessBoundaryRows=5",
        "consumerArchiveTotalCount=301",
        "realImporterDryRunHarnessBoundaryInterfaceCount=10",
        "harnessAllowedFutureInputClassCount=5",
        "harnessRequiredFutureArtifactClassCount=6",
        "harnessStopConditionCount=12",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "realImporterDryRunHarnessExecuted=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "outputArtifactRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed harness-boundary slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed readiness gate slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed harness checklist population slice", failures)
    require(f"Completed {FOLLOWUP_CHECKLIST_VALIDATION_SLICE}" in backlog, "backlog missing completed harness checklist validation slice", failures)
    require(f"The selected active static-to-proof slice is {PREVIOUS_SLICE}. Status: selected" not in active, "active block still marks readiness gate active", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks harness boundary active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks harness checklist population active", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_CHECKLIST_VALIDATION_SLICE}. Status: selected" not in active, "active block still marks harness checklist validation active", failures)
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active,
        "active block missing harness checklist command consumer validation next slice",
        failures,
    )
    require("texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan" in active, "active block missing current command arm-checklist-population scope", failures)
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
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_boundary_proof_plan_probe.py --check",
        "missing package private-corpus real importer dry-run harness boundary test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "real importer dry-run harness boundary module missing", failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after real importer dry-run harness boundary probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer private-corpus real importer dry-run harness boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer private-corpus real importer dry-run harness boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
