#!/usr/bin/env python3
"""Validate the public-safe command arm-checklist validation proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_population import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    PROOF_SCHEMA_VERSION as SOURCE_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
)
from texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_validation import (
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    THIS_SCOPE,
    THIS_SLICE,
    VALIDATION_PREFLIGHT_CHECKS,
    ZERO_COUNTERS,
    build_public_safe_command_arm_checklist_validation_proof,
    build_public_safe_command_arm_checklist_validation_summary,
)


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_validation_proof_2026-06-16.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_validation.py"
SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.v1.json"
PACKAGE_JSON = ROOT / "package.json"
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

EXPECTED_SCRIPT = (
    r"py -3 tools\texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_validation_proof_probe.py --check"
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
    (re.compile(r"(?i)asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "private asset content parsed",
    "raw private corpus manifest consumed",
    "private raw manifest rows consumed",
    "runnable command materialized",
    "command armed successfully",
    "shell dispatched successfully",
    "importer executed successfully",
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
    "runtime texture pixels proven",
    "runtime mesh loading proven",
    "runtime direct3d upload proven",
    "material visual correctness proven",
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


def active_slice_block(text: str) -> str:
    marker = "## Active Proof Slice"
    start = text.find(marker)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + len(marker))
    return text[start:] if next_heading < 0 else text[start:next_heading]


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


def check_result(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_RESULT)
    require(source.get("schemaVersion") == SOURCE_PROOF_SCHEMA_VERSION, "source schema mismatch", failures)
    require(source.get("status") == "PASS", "source status mismatch", failures)
    require(
        source.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "source population status mismatch",
        failures,
    )
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch", failures)

    expected = build_public_safe_command_arm_checklist_validation_proof(
        build_public_safe_command_arm_checklist_validation_summary(source)
    )
    actual = read_json(RESULT)
    require(actual == expected, "tracked validation JSON does not match module rebuild", failures)
    require(read_json(LORE_RESULT) == actual, "lore validation JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore validation markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "proof status mismatch", failures)
    require(
        actual.get(
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus"
        )
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "validation status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    check_no_bad_public_content(RESULT, failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    source = result.get("sourceEvidence", {})
    contract = result.get(
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationContract",
        {},
    )
    decision = result.get(
        "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationDecision",
        {},
    )
    guard = result.get("guardSummary", {})
    redaction = result.get("redactionPolicy", {})

    expected_source = {
        "sourceProofCount": 66,
        "sourceCommandArmChecklistPopulationProofCount": 65,
        "sourceCommandArmChecklistPopulationInterfaceCount": 12,
        "commandArmChecklistValidationInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES
        ),
    }
    for key, expected in expected_source.items():
        require(source.get(key) == expected, f"source evidence mismatch: {key}", failures)
    require(
        tuple(source.get("commandArmChecklistValidationInterfaces", ()))
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_INTERFACES,
        "validation interface list mismatch",
        failures,
    )

    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationOnly",
        "commandArmChecklistPopulationProofConsumed",
        "commandArmChecklistPopulationProofContinuityValidated",
        "commandArmChecklistRowsConsumedByValidation",
        "commandArmChecklistValidationExecuted",
        "commandArmChecklistValidationInputAccepted",
        "commandArmChecklistValidationSchemaValidated",
        "commandArmChecklistValidationRowOrdinalsValidated",
        "commandArmChecklistValidationCategoryCountsValidated",
        "commandArmChecklistValidationNotRunStatusesValidated",
        "commandArmChecklistValidationUnobservedStatusesValidated",
        "commandArmChecklistValidationNotArmedStatusesValidated",
        "commandArmChecklistValidationNotExecutedStatusesValidated",
        "commandArmChecklistValidationDispatchGuardsValidated",
        "commandArmChecklistValidationRedactionPolicyValidated",
        "commandArmChecklistValidationGuardCountersValidated",
        "commandArmChecklistValidationEmitsOnlyPublicSafeRows",
        "commandArmChecklistReadinessGateLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision.get(key) is True, f"decision true flag mismatch: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)

    expected_counts = {
        "commandArmChecklistRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistValidationRowCount": 0,
        "validatedNotRunCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedUnobservedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotArmedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNotExecutedCommandArmChecklistRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "preflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "passedPreflightCheckCount": len(VALIDATION_PREFLIGHT_CHECKS),
        "failedPreflightCheckCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)
    require(Counter(contract.get("commandArmChecklistValidationCategoryCounts", {})) == EXPECTED_CATEGORY_COUNTS, "category count mismatch", failures)
    require(tuple(contract.get("preflightChecks", ())) == VALIDATION_PREFLIGHT_CHECKS, "preflight list mismatch", failures)

    rows = contract.get("commandArmChecklistValidationRowsBody", [])
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "validation row count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "validation row category mismatch", failures)
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"validation row {ordinal}"
        require(row.get("commandArmChecklistValidationRowOrdinal") == ordinal, f"{row_id} ordinal mismatch", failures)
        require(row.get("sourceCommandArmChecklistPopulationRowOrdinal") == ordinal, f"{row_id} source population ordinal mismatch", failures)
        require(row.get("sourceCommandArmBoundaryRowOrdinal") == ordinal, f"{row_id} source boundary ordinal mismatch", failures)
        require(row.get("rowStatus") == "not-run", f"{row_id} row status mismatch", failures)
        require(row.get("observationStatus") == "unobserved", f"{row_id} observation mismatch", failures)
        require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch", failures)
        require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch", failures)
        require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch", failures)
        require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} direct arm guard mismatch", failures)
        require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} direct execution guard mismatch", failures)
        require(row.get("futureCommandArmChecklistReadinessGateAllowed") is True, f"{row_id} future readiness flag mismatch", failures)
        require(row.get("privateValuePublished") is False, f"{row_id} private value flag mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row.get(key) == 0, f"{row_id} zero field mismatch: {key}", failures)

    require(redaction.get("publicAllowedOutputCount") == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction.get("redactedFieldCount") == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction.get("publicAllowedOutputs", ())) == PUBLIC_ALLOWED_OUTPUTS, "public outputs mismatch", failures)
    require(tuple(redaction.get("redactedFields", ())) == REDACTED_FIELDS, "redacted fields mismatch", failures)
    require(redaction.get("publicLeakCheck") == "PASS", "redaction public leak mismatch", failures)
    require(guard.get("falseGuardCount") == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard.get("zeroCounterCount") == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"zero counter mismatch: {key}", failures)
    require(guard.get("publicLeakCheck") == "PASS", "guard public leak mismatch", failures)


def check_docs(failures: list[str]) -> None:
    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        PREVIOUS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json",
        "tools/texture_mesh_material_sidecar_command_arm_checklist_command_arm_checklist_validation.py",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "sourceCommandArmChecklistPopulationStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "sourceProofCount=66",
        "sourceCommandArmChecklistPopulationProofCount=65",
        "sourceCommandArmChecklistPopulationInterfaceCount=12",
        "commandArmChecklistValidationInterfaceCount=16",
        "commandArmChecklistRowsConsumed=99",
        "commandArmChecklistValidationRows=99",
        "passedCommandArmChecklistValidationRowCount=99",
        "failedCommandArmChecklistValidationRowCount=0",
        "validatedNotRunCommandArmChecklistRowCount=99",
        "validatedUnobservedCommandArmChecklistRowCount=99",
        "validatedNotArmedCommandArmChecklistRowCount=99",
        "validatedNotExecutedCommandArmChecklistRowCount=99",
        "armedCommandRowCount=0",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
        "readyForLaterCommandArmChecklistReadinessGateRowCount=99",
        "consumerArchiveTotalCount=301",
        "unknownAyaArchiveClassCount=0",
        "publicSafeCommandArmChecklistValidationArtifactRows=1",
        f"publicAllowedOutputCount={len(PUBLIC_ALLOWED_OUTPUTS)}",
        f"redactedFieldCount={len(REDACTED_FIELDS)}",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "realImporterExecuted=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "rawPathRows=0",
        "rawHashRows=0",
        "no private asset reads",
        "no private asset bytes",
        "not command arming",
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
        "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md",
        "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json",
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_VALIDATION_STATUS,
        "sourceCommandArmChecklistPopulationStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_POPULATION_STATUS,
        "sourceProofCount=66",
        "sourceCommandArmChecklistPopulationProofCount=65",
        "commandArmChecklistValidationRows=99",
        "readyForLaterCommandArmChecklistReadinessGateRowCount=99",
        "consumerArchiveTotalCount=301",
        "realImporterExecuted=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
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

    active = active_slice_block(read_text(BACKLOG))
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks validation slice active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in active, "active block does not mark readiness-gate slice active", failures)
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
        scripts.get("test:texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof")
        == EXPECTED_SCRIPT,
        "missing package validation proof test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "validation module missing", failures)
    result = check_result(failures)
    check_contract(result, failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after command arm-checklist validation probe", failures)

    if failures:
        print("Texture/mesh material sidecar command arm-checklist command arm-checklist validation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar command arm-checklist command arm-checklist validation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
