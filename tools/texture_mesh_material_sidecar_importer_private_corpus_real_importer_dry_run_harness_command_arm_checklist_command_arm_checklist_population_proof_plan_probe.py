#!/usr/bin/env python3
"""Validate command arm-checklist population public proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population import (
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREFLIGHT_CHECKS,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population_proof,
    build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population.py"
SOURCE_ARM_BOUNDARY_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-proof-plan.v1.json"
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
    (
        re.compile(r"(?i)textureRefSample|sampleRows|canonical_ref|canonicalRef|fbxTexturePath|exportFilePath"),
        "row-level private sample field",
    ),
    (re.compile(r"(?i)asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (
        re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"),
        "private frame locator/hash field",
    ),
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
    "command arming complete",
    "command execution complete",
    "shell dispatch complete",
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
        require(
            pattern.search(text) is None,
            f"{path.relative_to(ROOT)} leaks forbidden public category: {category}",
            failures,
        )
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    source_arm_boundary = read_json(SOURCE_ARM_BOUNDARY_RESULT)
    module_summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population_summary(
        source_arm_boundary
    )
    module_proof = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population_proof(
        module_summary
    )
    require(result == module_proof, "tracked command arm-checklist population proof differs from module rebuild", failures)

    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(
        result["privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationStatus"]
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "checklist-population status mismatch",
        failures,
    )
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(
        result["sourceCommandArmChecklistCommandArmBoundaryStatus"] == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "source arm-boundary continuity mismatch",
        failures,
    )

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["activeCurrentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    source = result["sourceEvidence"]
    require(source["sourceProofCount"] == 43, "source proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmBoundaryProofCount"] == 42, "source arm-boundary proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmBoundaryInterfaceCount"] == 10, "source arm-boundary interface count mismatch", failures)
    require(source["commandArmChecklistCommandArmChecklistPopulationInterfaceCount"] == 12, "checklist-population interface count mismatch", failures)
    require(
        tuple(source["sourceCommandArmChecklistCommandArmBoundaryInterfaces"]) == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
        "source command arm-checklist command arm-boundary interfaces mismatch",
        failures,
    )
    require(
        tuple(source["commandArmChecklistCommandArmChecklistPopulationInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_INTERFACES,
        "command arm-checklist population interfaces mismatch",
        failures,
    )

    decision = result["realImporterHarnessCommandArmChecklistCommandArmChecklistPopulationDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationOnly",
        "commandArmChecklistCommandArmBoundaryProofConsumed",
        "commandArmChecklistCommandArmBoundaryProofContinuityValidated",
        "commandArmChecklistCommandArmBoundaryRowsConsumedByChecklistPopulation",
        "commandArmChecklistCommandArmChecklistPopulationRowsPopulated",
        "commandArmChecklistCommandArmChecklistPopulationRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistPopulationRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistPopulationCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistPopulationInterfacesValidated",
        "commandArmChecklistCommandArmChecklistPopulationPreflightChecksPassed",
        "commandArmChecklistCommandArmChecklistPopulationEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistPopulationRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"decision should be true: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision[key] is False, f"decision should be false: {key}", failures)
    require(decision["defaultChecklistRowStatus"] == "not-run", "default row status mismatch", failures)
    require(decision["defaultObservationStatus"] == "unobserved", "default observation status mismatch", failures)

    contract = result["realImporterHarnessCommandArmChecklistCommandArmChecklistPopulationContract"]
    expected_counts = {
        "commandArmChecklistCommandArmBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistPopulationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "populatedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistPopulationRowCount": 0,
        "notRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "unobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistPopulationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract[key] == expected, f"checklist-population count mismatch: {key}", failures)
    require(
        contract["commandArmChecklistCommandArmChecklistPopulationCategoryCounts"] == dict(EXPECTED_CATEGORY_COUNTS),
        "checklist-population category count mismatch",
        failures,
    )
    rows = contract["commandArmChecklistCommandArmChecklistPopulationRowsBody"]
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "checklist row count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(
            row["commandArmChecklistCommandArmChecklistPopulationRowOrdinal"] == expected_ordinal,
            "checklist row order mismatch",
            failures,
        )
        require(row["sourceCommandArmChecklistCommandArmBoundaryRowOrdinal"] == expected_ordinal, "source row order mismatch", failures)
        require(row["rowStatus"] == "not-run", "checklist row status mismatch", failures)
        require(row["observationStatus"] == "unobserved", "checklist row observation mismatch", failures)
        require(row["commandArmStatus"] == "not-armed", "checklist row arm status mismatch", failures)
        require(row["commandExecutionStatus"] == "not-executed", "checklist row execution mismatch", failures)
        require(row["commandDispatchAllowedHere"] is False, "checklist row dispatch guard mismatch", failures)
        require(row["directCommandArmingAllowedHere"] is False, "checklist row direct-arm guard mismatch", failures)
        require(row["directCommandExecutionAllowedHere"] is False, "checklist row direct-exec guard mismatch", failures)
        require(row["privateValuePublished"] is False, "checklist row private guard mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row[key] == 0, f"checklist row zero mismatch: {key}", failures)

    redaction = result["redactionPolicy"]
    require(redaction["publicAllowedOutputCount"] == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction["redactedFieldCount"] == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public outputs mismatch", failures)
    require(tuple(redaction["redactedFields"]) == REDACTED_FIELDS, "redacted fields mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction public leak mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard[key] == 0, f"zero counter mismatch: {key}", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population.py",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationStatus=" + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "sourceCommandArmChecklistCommandArmBoundaryStatus=" + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "sourceProofCount=43",
        "sourceCommandArmChecklistCommandArmBoundaryProofCount=42",
        "sourceCommandArmChecklistCommandArmBoundaryInterfaceCount=10",
        "commandArmChecklistCommandArmChecklistPopulationInterfaceCount=12",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationOnly=true",
        "commandArmChecklistCommandArmBoundaryProofConsumed=true",
        "commandArmChecklistCommandArmBoundaryProofContinuityValidated=true",
        "commandArmChecklistCommandArmBoundaryRowsConsumedByChecklistPopulation=true",
        "commandArmChecklistCommandArmChecklistPopulationRowsPopulated=true",
        "commandArmChecklistCommandArmChecklistValidationLaneSelected=true",
        "futureCommandArmRequiresExplicitOperatorArm=true",
        "commandArmChecklistCommandArmBoundaryRowsConsumed=99",
        "commandArmChecklistCommandArmChecklistPopulationRows=99",
        "populatedCommandArmChecklistRowCount=99",
        "passedCommandArmChecklistCommandArmChecklistPopulationRowCount=99",
        "failedCommandArmChecklistCommandArmChecklistPopulationRowCount=0",
        "notRunCommandArmChecklistRowCount=99",
        "unobservedCommandArmChecklistRowCount=99",
        "observedChecklistRowCount=0",
        "rowStatusChangedCount=0",
        "armedCommandRowCount=0",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
        "readyForLaterCommandArmChecklistCommandArmChecklistValidationRowCount=99",
        "preflightCheckCount=17",
        "passedPreflightCheckCount=17",
        "failedPreflightCheckCount=0",
        "consumerArchiveTotalCount=301",
        "publicSafeCommandArmChecklistCommandArmChecklistPopulationArtifactRows=1",
        "publicAllowedOutputCount=58",
        "redactedFieldCount=32",
        "falseGuardCount=196",
        "zeroCounterCount=162",
        "rowStatus=not-run",
        "observationStatus=unobserved",
        "commandArmStatus=not-armed",
        "commandExecutionStatus=not-executed",
        "commandDispatchAllowedHere=false",
        "directCommandArmingAllowedHere=false",
        "directCommandExecutionAllowedHere=false",
        "futureCommandArmChecklistCommandArmChecklistValidationAllowed=true",
        "privateValuePublished=false",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistValidationRows=0",
        "commandArmChecklistDryRunRows=0",
        "commandArmChecklistPrivateOutputRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
        "rawCommandArgumentRows=0",
        "publishedCommandArgumentRows=0",
        "rawCommandDryRunTraceRows=0",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.v1.json",
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "sourceCommandArmChecklistCommandArmBoundaryStatus=" + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "sourceProofCount=43",
        "sourceCommandArmChecklistCommandArmBoundaryProofCount=42",
        "commandArmChecklistCommandArmChecklistPopulationRows=99",
        "notRunCommandArmChecklistRowCount=99",
        "unobservedCommandArmChecklistRowCount=99",
        "preflightCheckCount=17",
        "falseGuardCount=196",
        "zeroCounterCount=162",
        "commandArmChecklistCommandArmChecklistValidationLaneSelected=true",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed command arm-checklist population slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed command arm-checklist command arm-boundary slice", failures)
    require(f"Completed {NEXT_SLICE}" not in backlog, "backlog already marks command arm-checklist validation complete", failures)
    require(
        f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active,
        "active block still marks command arm-checklist population active",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in active,
        "active block missing command arm-checklist validation slice",
        failures,
    )
    require(
        NEXT_SCOPE in active,
        "active block missing command arm-checklist validation scope",
        failures,
    )
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
        scripts.get(
            "test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan"
        )
        == (
            r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_population_proof_plan_probe.py --check"
        ),
        "missing package real-importer harness command arm-checklist population test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "real importer harness command arm-checklist population module missing", failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after real importer harness command arm-checklist population probe", failures)

    if failures:
        print("Texture/mesh material sidecar real-importer harness command arm-checklist population probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness command arm-checklist population probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
