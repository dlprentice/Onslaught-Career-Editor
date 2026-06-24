#!/usr/bin/env python3
"""Validate private-corpus real-importer harness command arm-checklist command arm-checklist boundary proof."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    STOP_CONDITIONS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_command_arm_boundary_proof,
    build_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_readiness_gate import (
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / PROOF.name
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / RESULT.name
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary.py"
SOURCE_READINESS_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.v1.json"
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
    "runnable command materialization complete",
    "command arming complete",
    "command execution complete",
    "shell dispatch complete",
    "real importer complete",
    "real importer execution complete",
    "private importer dry-run complete",
    "real importer dry-run complete",
    "asset import complete",
    "generated asset output complete",
    "runtime resource archive parser behavior proven",
    "runtime texture parser behavior proven",
    "runtime mesh loading proven",
    "runtime direct3d upload proven",
    "native textured 3d rendering proven",
    "material visual correctness proven",
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
    module_summary = build_public_safe_real_importer_dry_run_harness_command_arm_boundary_summary(source_readiness)
    module_proof = build_public_safe_real_importer_dry_run_harness_command_arm_boundary_proof(module_summary)
    require(result == module_proof, "tracked command arm-checklist command arm-checklist boundary proof differs from module rebuild", failures)

    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(
        result["privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryStatus"]
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "boundary status mismatch",
        failures,
    )
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(
        result["sourceCommandArmChecklistCommandArmChecklistReadinessGateStatus"]
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "source readiness-gate continuity mismatch",
        failures,
    )

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["activeCurrentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    source = result["sourceEvidence"]
    require(source["sourceProofCount"] == 46, "source proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistReadinessGateProofCount"] == 45, "source readiness proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount"] == 10, "source readiness interface count mismatch", failures)
    require(source["commandArmChecklistCommandArmChecklistBoundaryInterfaceCount"] == 10, "boundary interface count mismatch", failures)
    require(
        tuple(source["sourceCommandArmChecklistCommandArmChecklistReadinessGateInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
        "source readiness interfaces mismatch",
        failures,
    )
    require(
        tuple(source["commandArmChecklistCommandArmChecklistBoundaryInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
        "boundary interfaces mismatch",
        failures,
    )

    decision = result["realImporterHarnessCommandArmChecklistCommandArmChecklistBoundaryDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryOnly",
        "commandArmChecklistCommandArmChecklistReadinessGateProofConsumed",
        "commandArmChecklistCommandArmChecklistReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistReadinessGateProofRowsConsumed",
        "commandArmChecklistCommandArmChecklistBoundaryDefined",
        "commandArmChecklistCommandArmChecklistBoundaryInputAccepted",
        "commandArmChecklistCommandArmChecklistBoundaryRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistBoundaryRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistBoundaryCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistBoundaryInterfacesValidated",
        "commandArmChecklistCommandArmChecklistBoundaryStopConditionsValidated",
        "commandArmChecklistCommandArmChecklistBoundaryEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistBoundaryRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandMaterializationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"decision should be true: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision[key] is False, f"decision should be false: {key}", failures)

    contract = result["realImporterHarnessCommandArmChecklistCommandArmChecklistBoundaryContract"]
    expected_counts = {
        "commandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract[key] == expected, f"boundary count mismatch: {key}", failures)
    require(contract["commandArmChecklistCommandArmChecklistBoundaryCategoryCounts"] == dict(EXPECTED_CATEGORY_COUNTS), "boundary category count mismatch", failures)

    rows = contract["commandArmChecklistCommandArmChecklistBoundaryRowsBody"]
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "boundary row count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(row["commandArmChecklistCommandArmChecklistBoundaryRowOrdinal"] == expected_ordinal, "boundary row order mismatch", failures)
        require(row["sourceCommandArmChecklistCommandArmChecklistReadinessGateRowOrdinal"] == expected_ordinal, "boundary source row order mismatch", failures)
        require(row["rowStatus"] == "not-run", "boundary row status mismatch", failures)
        require(row["commandArmStatus"] == "not-armed", "boundary row arm status mismatch", failures)
        require(row["commandExecutionStatus"] == "not-executed", "boundary row execution status mismatch", failures)
        require(row["commandDispatchAllowedHere"] is False, "boundary row dispatch guard mismatch", failures)
        require(row["directCommandArmingAllowedHere"] is False, "boundary row direct-arm guard mismatch", failures)
        require(row["privateValuePublished"] is False, "boundary row private value guard mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row[key] == 0, f"boundary row zero mismatch: {key}", failures)

    require(result["redactionPolicy"]["publicAllowedOutputCount"] == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(result["redactionPolicy"]["redactedFieldCount"] == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(result["redactionPolicy"]["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public outputs mismatch", failures)
    require(tuple(result["redactionPolicy"]["redactedFields"]) == REDACTED_FIELDS, "redacted fields mismatch", failures)
    require(result["redactionPolicy"]["publicLeakCheck"] == "PASS", "redaction public leak mismatch", failures)

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
        RESULT.name,
        "tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary.py",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryStatus=" + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "sourceCommandArmChecklistCommandArmChecklistReadinessGateStatus=" + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "sourceProofCount=46",
        "sourceCommandArmChecklistCommandArmChecklistReadinessGateProofCount=45",
        "commandArmChecklistCommandArmChecklistBoundaryInterfaceCount=10",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryOnly=true",
        "commandArmChecklistCommandArmChecklistReadinessGateProofConsumed=true",
        "commandArmChecklistCommandArmChecklistBoundaryDefined=true",
        "harnessCommandArmChecklistCommandArmChecklistCommandMaterializationLaneSelected=true",
        "futureCommandArmRequiresExplicitOperatorArm=true",
        "commandArmChecklistCommandArmChecklistReadinessGateRowsConsumed=99",
        "commandArmChecklistCommandArmChecklistBoundaryRows=99",
        "definedCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
        "passedCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
        "failedCommandArmChecklistCommandArmChecklistBoundaryRowCount=0",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount=99",
        "publicSafeCommandArmChecklistCommandArmChecklistBoundaryArtifactRows=1",
        "publicAllowedOutputCount=67",
        "redactedFieldCount=35",
        "stopConditionCount=12",
        "falseGuardCount=212",
        "zeroCounterCount=174",
        "privateAssetContentRead=false",
        "rawPrivateManifestConsumed=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationExecuted=false",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
        "rawCommandArgumentRows=0",
        "publishedCommandArgumentRows=0",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "outputArtifactRows=0",
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
        PROOF.name,
        RESULT.name,
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "sourceCommandArmChecklistCommandArmChecklistReadinessGateStatus=" + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryOnly=true",
        "commandArmChecklistCommandArmChecklistBoundaryDefined=true",
        "commandArmChecklistCommandArmChecklistReadinessGateRowsConsumed=99",
        "commandArmChecklistCommandArmChecklistBoundaryRows=99",
        "passedCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount=99",
        "consumerArchiveTotalCount=301",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationRows=0",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed command arm-checklist command arm-checklist boundary slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed command arm-checklist command arm-checklist readiness slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks command arm-checklist command arm-checklist boundary active", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in active,
        "active block missing command-materialization slice",
        failures,
    )
    require(NEXT_SCOPE in active, "active block missing command-materialization scope", failures)
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
            "test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan"
        )
        == (
            r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary_proof_plan_probe.py --check"
        ),
        "missing package real-importer harness command arm-checklist command arm-checklist boundary test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "real importer harness command arm-checklist command arm-checklist boundary module missing", failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors_and_package(failures)

    if failures:
        print("Texture/mesh material sidecar real-importer harness command arm-checklist command arm-checklist boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness command arm-checklist command arm-checklist boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
