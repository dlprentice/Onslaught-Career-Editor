#!/usr/bin/env python3
"""Validate the public-safe command arm-boundary proof."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_arm_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    STOP_CONDITIONS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_command_arm_boundary_proof,
    build_public_safe_command_arm_boundary_summary,
)
from texture_mesh_material_sidecar_command_arm_checklist_command_arm_readiness_gate import (
    PROOF_SCHEMA_VERSION as SOURCE_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_command_arm_checklist_command_arm_boundary_proof_2026-06-16.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_command_arm_checklist_command_arm_boundary.py"
SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.v1.json"
PACKAGE_JSON = ROOT / "package.json"

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

EXPECTED_SCRIPT = r"py -3 tools\texture_mesh_material_sidecar_command_arm_checklist_command_arm_boundary_proof_probe.py --check"
VALIDATION_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm "
    "Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan"
)
VALIDATION_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-"
    "checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan"
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


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_source(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_RESULT)
    require(source.get("schemaVersion") == SOURCE_PROOF_SCHEMA_VERSION, "source schema mismatch", failures)
    require(source.get("status") == "PASS", "source status mismatch", failures)
    require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "source status token mismatch",
        failures,
    )
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch", failures)
    return source


def check_result_and_mirror(source: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    expected = build_public_safe_command_arm_boundary_proof(build_public_safe_command_arm_boundary_summary(source))
    actual = read_json(RESULT)
    require(actual == expected, "tracked command arm-boundary JSON does not match module rebuild", failures)
    require(read_json(LORE_RESULT) == actual, "lore command arm-boundary JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore command arm-boundary markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "arm-boundary status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    decision = result.get("realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryDecision", {})
    contract = result.get("realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryContract", {})
    guard = result.get("guardSummary", {})
    redaction = result.get("redactionPolicy", {})
    source = result.get("sourceEvidence", {})

    expected_source = {
        "sourceProofCount": 64,
        "sourceCommandArmReadinessGateProofCount": 63,
        "sourceCommandArmReadinessGateInterfaceCount": 10,
        "commandArmBoundaryInterfaceCount": len(
            REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_INTERFACES
        ),
    }
    for key, expected in expected_source.items():
        require(source.get(key) == expected, f"source evidence mismatch: {key}", failures)

    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryOnly",
        "commandArmReadinessGateProofConsumed",
        "commandArmReadinessGateProofContinuityValidated",
        "commandArmReadinessGateRowsConsumedByArmBoundary",
        "commandArmBoundaryDefined",
        "commandArmBoundaryInputAccepted",
        "commandArmBoundaryRowStatusesValidated",
        "commandArmBoundaryRowOrdinalsValidated",
        "commandArmBoundaryCategoryCountsValidated",
        "commandArmBoundaryGuardCountersValidated",
        "commandArmBoundaryInterfacesValidated",
        "commandArmBoundaryStopConditionsValidated",
        "commandArmBoundaryEmitsOnlyPublicSafeRows",
        "commandArmBoundaryRedactionPolicyValidated",
        "commandArmChecklistPopulationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision.get(key) is True, f"decision true flag mismatch: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)

    expected_counts = {
        "commandArmReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistPopulationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)

    rows = contract.get("commandArmBoundaryRowsBody", [])
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "arm-boundary row count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "category count mismatch", failures)
    for ordinal, row in enumerate(rows, start=1):
        row_id = f"command arm-boundary row {ordinal}"
        require(row.get("commandArmBoundaryRowOrdinal") == ordinal, f"{row_id} ordinal mismatch", failures)
        require(row.get("sourceCommandArmReadinessGateRowOrdinal") == ordinal, f"{row_id} source ordinal mismatch", failures)
        require(row.get("commandArmStatus") == "not-armed", f"{row_id} arm status mismatch", failures)
        require(row.get("commandExecutionStatus") == "not-executed", f"{row_id} execution status mismatch", failures)
        require(row.get("commandDispatchAllowedHere") is False, f"{row_id} dispatch guard mismatch", failures)
        require(row.get("directCommandArmingAllowedHere") is False, f"{row_id} arm guard mismatch", failures)
        require(row.get("directCommandExecutionAllowedHere") is False, f"{row_id} execution guard mismatch", failures)
        require(row.get("futureCommandArmChecklistPopulationAllowed") is True, f"{row_id} population lane flag mismatch", failures)
        require(row.get("privateValuePublished") is False, f"{row_id} private flag mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row.get(key) == 0, f"{row_id} zero mismatch: {key}", failures)

    require(redaction.get("publicAllowedOutputCount") == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction.get("redactedFieldCount") == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction.get("publicAllowedOutputs", ())) == PUBLIC_ALLOWED_OUTPUTS, "public output list mismatch", failures)
    require(tuple(redaction.get("redactedFields", ())) == REDACTED_FIELDS, "redacted list mismatch", failures)
    require(guard.get("falseGuardCount") == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard.get("zeroCounterCount") == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"zero counter mismatch: {key}", failures)


def check_docs_and_package(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        PREVIOUS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "sourceCommandArmReadinessGateStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "sourceProofCount=64",
        "sourceCommandArmReadinessGateProofCount=63",
        "sourceCommandArmReadinessGateInterfaceCount=10",
        "commandArmBoundaryInterfaceCount=10",
        "commandArmReadinessGateRowsConsumed=99",
        "commandArmBoundaryRows=99",
        "definedCommandArmBoundaryRowCount=99",
        "passedCommandArmBoundaryRowCount=99",
        "failedCommandArmBoundaryRowCount=0",
        "readyForLaterCommandArmChecklistPopulationRowCount=99",
        "publicSafeCommandArmBoundaryArtifactRows=1",
        f"publicAllowedOutputCount={len(PUBLIC_ALLOWED_OUTPUTS)}",
        f"redactedFieldCount={len(REDACTED_FIELDS)}",
        f"stopConditionCount={len(STOP_CONDITIONS)}",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.md",
        "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json",
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_BOUNDARY_STATUS,
        "sourceProofCount=64",
        "sourceCommandArmReadinessGateProofCount=63",
        "commandArmReadinessGateRowsConsumed=99",
        "commandArmBoundaryRows=99",
        "passedCommandArmBoundaryRowCount=99",
        f"publicAllowedOutputCount={len(PUBLIC_ALLOWED_OUTPUTS)}",
        f"redactedFieldCount={len(REDACTED_FIELDS)}",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "commandArmChecklistPopulationLaneSelected=true",
        "realImporterExecuted=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "rawPathRows=0",
        "rawHashRows=0",
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

    text = read_text(BACKLOG)
    active = active_slice_block(text)
    require(f"Completed {THIS_SLICE}" in text, "backlog missing completed command arm-boundary slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in text, "backlog missing completed command arm-readiness slice", failures)
    require(f"Completed {NEXT_SLICE}" in text, "backlog missing completed command arm-checklist population slice", failures)
    require(f"The selected active static-to-proof slice is {VALIDATION_SLICE}. Status: selected" in active, "active slice not moved to command arm-checklist validation lane", failures)
    require(VALIDATION_SCOPE in active, "active scope not moved to command arm-checklist validation lane", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "command arm-boundary scope still active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "command arm-checklist population scope still active", failures)
    require(active.count("The selected active static-to-proof slice is ") == 1, "active block should have exactly one active slice sentence", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof") == EXPECTED_SCRIPT,
        "missing package command arm-boundary test script",
        failures,
    )
    require(MODULE.is_file(), "missing command arm-boundary generator module", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        source = check_source(failures)
        result = check_result_and_mirror(source, failures)
        check_contract(result, failures)
        check_docs_and_package(failures)
        check_no_bad_public_content(RESULT, failures)
    except Exception as exc:  # pragma: no cover - probe output is user-facing.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture mesh material sidecar command arm-boundary proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture mesh material sidecar command arm-boundary proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
