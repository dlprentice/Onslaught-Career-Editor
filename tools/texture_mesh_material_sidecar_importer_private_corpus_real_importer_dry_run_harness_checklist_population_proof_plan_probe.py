#!/usr/bin/env python3
"""Validate private-corpus real-importer dry-run harness checklist population."""

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
    HARNESS_STOP_CONDITIONS,
    PROOF_SCHEMA_VERSION as SOURCE_BOUNDARY_PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS as BOUNDARY_PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
    REDACTED_FIELDS as BOUNDARY_REDACTED_FIELDS,
    REQUIRED_FUTURE_ARTIFACT_CLASSES,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population import (
    CHECKLIST_GROUPS,
    FALSE_GUARDS_CHECKLIST,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREFLIGHT_CHECKS,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
    REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS_CHECKLIST,
    build_public_safe_harness_checklist_rows,
    build_public_safe_real_importer_dry_run_harness_checklist_population_proof,
    build_public_safe_real_importer_dry_run_harness_checklist_population_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_readiness_gate import (
    REAL_IMPORTER_READINESS_INTERFACES,
    REAL_IMPORTER_READINESS_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population.py"

SOURCE_BOUNDARY_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md"
SOURCE_BOUNDARY_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json"
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

FOLLOWUP_CHECKLIST_READINESS_GATE_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan"
)
FOLLOWUP_CHECKLIST_READINESS_GATE_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan"
)

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
    "real importer dry-run harness complete",
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


def check_source_boundary(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_BOUNDARY_RESULT)
    require(source["schemaVersion"] == SOURCE_BOUNDARY_PROOF_SCHEMA_VERSION, "source boundary schema mismatch", failures)
    require(source["status"] == "PASS", "source boundary status mismatch", failures)
    require(source["privateCorpusRealImporterDryRunHarnessBoundaryStatus"] == REAL_IMPORTER_HARNESS_BOUNDARY_STATUS, "source boundary token mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source selected next scope mismatch", failures)
    require(source["sourceEvidence"]["sourceProofCount"] == 22, "source proof count mismatch", failures)
    decision = source["realImporterHarnessBoundaryDecision"]
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
        require(decision[key] is False, f"source boundary false guard changed: {key}", failures)
    require(decision["harnessChecklistPopulationLaneSelected"] is True, "source boundary did not select checklist lane", failures)
    check_no_bad_public_content(SOURCE_BOUNDARY_PROOF, failures)
    return source


def check_result(source: dict[str, Any], failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    module_summary = build_public_safe_real_importer_dry_run_harness_checklist_population_summary(source)
    module_proof = build_public_safe_real_importer_dry_run_harness_checklist_population_proof(module_summary)
    require(result == module_proof, "tracked harness checklist proof differs from module rebuild", failures)

    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(
        result["privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus"]
        == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "checklist status mismatch",
        failures,
    )
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceRealImporterHarnessBoundaryStatus"] == REAL_IMPORTER_HARNESS_BOUNDARY_STATUS, "source boundary continuity mismatch", failures)
    require(result["sourceRealImporterReadinessGateStatus"] == REAL_IMPORTER_READINESS_STATUS, "source readiness continuity mismatch", failures)
    require(result["sourceEvidence"]["sourceProofCount"] == 23, "source proof count mismatch", failures)
    require(result["sourceEvidence"]["sourceHarnessBoundaryProofCount"] == 22, "source boundary proof count mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    decision = result["realImporterHarnessChecklistPopulationDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly",
        "realImporterHarnessBoundaryProofConsumed",
        "realImporterHarnessBoundaryProofContinuityValidated",
        "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation",
        "realImporterDryRunHarnessChecklistPopulated",
        "harnessChecklistRowsPopulated",
        "harnessChecklistArchiveClassRowsPopulated",
        "harnessChecklistInputClassRowsPopulated",
        "harnessChecklistRequiredArtifactRowsPopulated",
        "harnessChecklistStopConditionRowsPopulated",
        "harnessChecklistInterfaceRowsPopulated",
        "harnessChecklistRedactionRowsPopulated",
        "harnessChecklistPublicOutputRowsPopulated",
        "harnessChecklistRefusalGuardsValidated",
        "harnessChecklistArchiveClassOrderValidated",
        "harnessChecklistArchiveClassCountsValidated",
        "harnessChecklistInterfacesValidated",
        "harnessChecklistEmitsOnlyPublicSafeRows",
        "harnessChecklistValidationLaneSelected",
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
        "realImporterDryRunHarnessExecutedInChecklistPopulationSlice",
        "realImporterDryRunHarnessOutputPublished",
        "realImporterDryRunHarnessChecklistPopulationReadPrivateInputs",
        "realImporterDryRunHarnessChecklistPublishedPrivateInput",
        "realImporterDryRunHarnessChecklistPrivateValuesPublished",
        "realImporterDryRunHarnessChecklistValidationExecuted",
        "realImporterDryRunHarnessChecklistDryRunExecuted",
        "realImporterDryRunHarnessCommandMaterialized",
        "realImporterDryRunHarnessPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision[key] is False, f"decision should be false: {key}", failures)
    require(decision["defaultChecklistRowStatus"] == "not-run", "default checklist row status mismatch", failures)
    require(decision["defaultObservationStatus"] == "unobserved", "default observation status mismatch", failures)

    contract = result["realImporterHarnessChecklistPopulationContract"]
    expected_counts = {
        "sourceRealImporterReadinessInterfaceCount": len(REAL_IMPORTER_READINESS_INTERFACES),
        "sourceRealImporterHarnessBoundaryInterfaceCount": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "realImporterDryRunHarnessChecklistPopulationInterfaceCount": len(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES),
        "realImporterHarnessBoundaryRowsConsumed": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessChecklistGroupCount": len(CHECKLIST_GROUPS),
        "harnessChecklistRows": 99,
        "harnessChecklistArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "harnessChecklistAllowedInputClassRows": len(ALLOWED_FUTURE_INPUT_CLASSES),
        "harnessChecklistRequiredArtifactClassRows": len(REQUIRED_FUTURE_ARTIFACT_CLASSES),
        "harnessChecklistStopConditionRows": len(HARNESS_STOP_CONDITIONS),
        "harnessChecklistBoundaryInterfaceRows": len(REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES),
        "harnessChecklistRedactionFieldRows": len(BOUNDARY_REDACTED_FIELDS),
        "harnessChecklistPublicAllowedOutputRows": len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS),
        "passedChecklistRowCount": 99,
        "failedChecklistRowCount": 0,
        "notRunChecklistRowCount": 99,
        "unobservedChecklistRowCount": 99,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "baseArchiveClassCount": 1,
        "frontendArchiveClassCount": 1,
        "loadingArchiveClassCount": 1,
        "numericLevelArchiveClassCount": 66,
        "goodieArchiveClassCount": 232,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeHarnessChecklistArtifactRows": 1,
    }
    for key, expected in expected_counts.items():
        require(contract[key] == expected, f"contract count mismatch: {key}", failures)
    require(tuple(contract["sourceRealImporterReadinessInterfaces"]) == REAL_IMPORTER_READINESS_INTERFACES, "source readiness interface mismatch", failures)
    require(tuple(contract["sourceRealImporterHarnessBoundaryInterfaces"]) == REAL_IMPORTER_HARNESS_BOUNDARY_INTERFACES, "source boundary interface mismatch", failures)
    require(tuple(contract["realImporterDryRunHarnessChecklistPopulationInterfaces"]) == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_INTERFACES, "checklist interface mismatch", failures)
    require(tuple(contract["allowedFutureInputClasses"]) == ALLOWED_FUTURE_INPUT_CLASSES, "allowed future inputs mismatch", failures)
    require(tuple(contract["requiredFutureArtifactClasses"]) == REQUIRED_FUTURE_ARTIFACT_CLASSES, "required future artifacts mismatch", failures)
    require(tuple(contract["harnessStopConditions"]) == HARNESS_STOP_CONDITIONS, "stop conditions mismatch", failures)

    group_counts = {row["groupId"]: row for row in contract["checklistGroups"]}
    for category, status, items in CHECKLIST_GROUPS:
        row = group_counts.get(category)
        require(row is not None, f"missing checklist group: {category}", failures)
        if row is not None:
            require(row["rowCount"] == len(items), f"checklist group count mismatch: {category}", failures)
            require(row["status"] == status, f"checklist group status mismatch: {category}", failures)
    archive_rows = contract["harnessArchiveClassChecklistRowsBody"]
    require([row["sourceArchiveClass"] for row in archive_rows] == list(REQUIRED_ARCHIVE_CLASSES), "archive checklist row order mismatch", failures)
    require(all(row["rowStatus"] == "not-run" for row in archive_rows), "archive row status mismatch", failures)
    require(all(row["observationStatus"] == "unobserved" for row in archive_rows), "archive row observation mismatch", failures)
    require(all(row["harnessChecklistPrivateIdentifiersPresent"] is False for row in archive_rows), "archive private identifier guard mismatch", failures)
    rows = contract["harnessChecklistRowsBody"]
    require(rows == build_public_safe_harness_checklist_rows(), "module checklist row body mismatch", failures)
    require(all(row["rowStatus"] == "not-run" for row in rows), "checklist row status mismatch", failures)
    require(all(row["observationStatus"] == "unobserved" for row in rows), "checklist row observation mismatch", failures)
    require(all(row["privateValuePublished"] is False for row in rows), "checklist private value publication mismatch", failures)

    redaction = result["redactionPolicy"]
    require(redaction["publicAllowedOutputCount"] == len(BOUNDARY_PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction["redactedFieldCount"] == len(BOUNDARY_REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction["publicAllowedOutputs"]) == BOUNDARY_PUBLIC_ALLOWED_OUTPUTS, "public output list mismatch", failures)
    require(tuple(redaction["redactedFields"]) == BOUNDARY_REDACTED_FIELDS, "redacted field list mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS_CHECKLIST), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS_CHECKLIST), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)
    require("harnessChecklistRows" not in guard, "guard should not shadow public checklist row count", failures)
    for key in ZERO_COUNTERS_CHECKLIST:
        require(guard[key] == 0, f"zero counter mismatch: {key}", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the tracked harness-boundary proof can support public-safe not-run/unobserved checklist rows" in proves, "claim boundary missing checklist proof", failures)
    require("private reads and real/private importer execution remain unperformed in this slice" in proves, "claim boundary missing no-execution proof", failures)
    for token in (
        "private asset content parsing",
        "private raw manifest consumption",
        "real importer implementation",
        "real importer execution",
        "real importer dry-run harness execution",
        "real importer dry-run harness checklist validation",
        "actual asset import",
        "generated asset outputs",
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population.py",
        f"privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus={REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS}",
        f"sourceRealImporterHarnessBoundaryStatus={REAL_IMPORTER_HARNESS_BOUNDARY_STATUS}",
        f"sourceRealImporterReadinessGateStatus={REAL_IMPORTER_READINESS_STATUS}",
        "sourceProofCount=23",
        "sourceHarnessBoundaryProofCount=22",
        "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly=true",
        "realImporterHarnessBoundaryProofConsumed=true",
        "realImporterHarnessBoundaryProofContinuityValidated=true",
        "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation=true",
        "realImporterDryRunHarnessChecklistPopulated=true",
        "harnessChecklistRowsPopulated=true",
        "harnessChecklistArchiveClassRowsPopulated=true",
        "harnessChecklistInputClassRowsPopulated=true",
        "harnessChecklistRequiredArtifactRowsPopulated=true",
        "harnessChecklistStopConditionRowsPopulated=true",
        "harnessChecklistValidationLaneSelected=true",
        "defaultChecklistRowStatus=not-run",
        "defaultObservationStatus=unobserved",
        "sourceRealImporterReadinessInterfaceCount=8",
        "sourceRealImporterHarnessBoundaryInterfaceCount=10",
        "realImporterDryRunHarnessChecklistPopulationInterfaceCount=12",
        "realImporterHarnessBoundaryRowsConsumed=5",
        "harnessChecklistGroupCount=7",
        "harnessChecklistRows=99",
        "harnessChecklistArchiveClassRows=5",
        "harnessChecklistAllowedInputClassRows=5",
        "harnessChecklistRequiredArtifactClassRows=6",
        "harnessChecklistStopConditionRows=12",
        "harnessChecklistBoundaryInterfaceRows=10",
        "harnessChecklistRedactionFieldRows=28",
        "harnessChecklistPublicAllowedOutputRows=33",
        "notRunChecklistRowCount=99",
        "unobservedChecklistRowCount=99",
        "observedChecklistRowCount=0",
        "rowStatusChangedCount=0",
        "preflightCheckCount=17",
        "consumerArchiveTotalCount=301",
        "publicSafeHarnessChecklistArtifactRows=1",
        "publicAllowedOutputCount=33",
        "redactedFieldCount=28",
        "falseGuardCount=94",
        "zeroCounterCount=79",
        "NOT_RUN_PUBLIC_CHECKLIST_ONLY",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "realImporterDryRunHarnessExecuted=false",
        "realImporterDryRunHarnessArmed=false",
        "realImporterDryRunHarnessChecklistValidationExecuted=false",
        "realImporterDryRunHarnessChecklistDryRunExecuted=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "generatedDryRunOutputRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json",
        REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "sourceRealImporterHarnessBoundaryStatus=" + REAL_IMPORTER_HARNESS_BOUNDARY_STATUS,
        "sourceProofCount=23",
        "sourceHarnessBoundaryProofCount=22",
        "harnessChecklistRows=99",
        "notRunChecklistRowCount=99",
        "unobservedChecklistRowCount=99",
        "preflightCheckCount=17",
        "falseGuardCount=94",
        "zeroCounterCount=79",
        "realImporterDryRunHarnessChecklistValidationExecuted=false",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed harness checklist population slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed harness boundary slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed harness checklist validation slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks harness checklist population active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks harness checklist validation active", failures)
    require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active, "active block missing harness checklist readiness gate slice", failures)
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
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population_proof_plan_probe.py --check",
        "missing package harness checklist population test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "harness checklist population module missing", failures)
    source = check_source_boundary(failures)
    check_result(source, failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after harness checklist population probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer private-corpus real-importer harness checklist-population probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer private-corpus real-importer harness checklist-population probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
