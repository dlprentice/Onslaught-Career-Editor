#!/usr/bin/env python3
"""Validate the material sidecar command arm-checklist boundary proof."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_boundary import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    STOP_CONDITIONS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_boundary_proof,
    build_public_safe_boundary_summary,
)
from texture_mesh_material_sidecar_command_arm_checklist_readiness_gate import (
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_command_arm_checklist_boundary_proof_2026-06-16.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_command_arm_checklist_boundary.py"
SOURCE_READINESS_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-proof.v1.json"
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

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)\bgame[\\/]"), "repo-private game path"),
    (re.compile(r"(?i)\bmedia[\\/]"), "repo-private media path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
)

FORBIDDEN_OVERCLAIMS = (
    "private asset content parsed",
    "private corpus manifest consumed",
    "command armed successfully",
    "shell dispatched successfully",
    "importer executed successfully",
    "asset outputs generated",
    "runtime proof complete",
    "rebuild parity proven",
    "no-noticeable-difference proven",
)


def read_text(path: Path) -> str:
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
    next_marker = text.find("\n## ", start + len(marker))
    return text[start:] if next_marker < 0 else text[start:next_marker]


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
    module_summary = build_public_safe_boundary_summary(source_readiness)
    module_proof = build_public_safe_boundary_proof(module_summary)
    require(result == module_proof, "tracked boundary proof differs from module rebuild", failures)

    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "proof status mismatch", failures)
    require(
        result["privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus"]
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "boundary status token mismatch",
        failures,
    )
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "next scope mismatch", failures)
    require(
        result["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus"]
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "source readiness status token mismatch",
        failures,
    )

    source = result["sourceEvidence"]
    require(source["sourceProofCount"] == 57, "source proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount"] == 56, "source readiness proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount"] == 10, "source readiness interface count mismatch", failures)
    require(source["commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount"] == 10, "boundary interface count mismatch", failures)
    require(
        tuple(source["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_INTERFACES,
        "source readiness interfaces mismatch",
        failures,
    )
    require(
        tuple(source["commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
        "boundary interfaces mismatch",
        failures,
    )

    decision = result["realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryOnly",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofRowsConsumed",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryDefined",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInputAccepted",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinalsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryCategoryCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStopConditionsValidated",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"decision should be true: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision[key] is False, f"decision should be false: {key}", failures)

    contract = result["realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryContract"]
    expected_counts = {
        "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "stopConditionCount": len(STOP_CONDITIONS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)

    rows = contract["commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowsBody"]
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "boundary row count mismatch", failures)
    require(Counter(row["category"] for row in rows) == EXPECTED_CATEGORY_COUNTS, "boundary category counts mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"boundary row {expected_ordinal}"
        require(
            row["commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal"] == expected_ordinal,
            f"{row_id} ordinal mismatch",
            failures,
        )
        require(row["boundaryStatus"] == "defined-public-safe-command-materialization-lane-only-no-command-arming", f"{row_id} status mismatch", failures)
        require(row["rowStatus"] == "not-run", f"{row_id} row status mismatch", failures)
        require(row["observationStatus"] == "unobserved", f"{row_id} observation mismatch", failures)
        require(row["commandArmStatus"] == "not-armed", f"{row_id} arm status mismatch", failures)
        require(row["commandExecutionStatus"] == "not-executed", f"{row_id} execution status mismatch", failures)
        require(row["commandDispatchAllowedHere"] is False, f"{row_id} dispatch guard mismatch", failures)
        require(row["directCommandArmingAllowedHere"] is False, f"{row_id} direct arm guard mismatch", failures)
        require(row["directCommandExecutionAllowedHere"] is False, f"{row_id} direct exec guard mismatch", failures)
        require(
            row["futureCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationAllowed"] is True,
            f"{row_id} future command materialization mismatch",
            failures,
        )
        require(row["privateValuePublished"] is False, f"{row_id} private value mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row.get(key) == 0, f"{row_id} zero field mismatch: {key}", failures)

    require(result["redactionPolicy"]["publicLeakCheck"] == "PASS", "redaction public leak mismatch", failures)
    require(tuple(result["redactionPolicy"]["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public outputs mismatch", failures)
    require(tuple(result["redactionPolicy"]["redactedFields"]) == REDACTED_FIELDS, "redacted fields mismatch", failures)
    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"guard zero mismatch: {key}", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak mismatch", failures)
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
        "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1.json",
        "tools/texture_mesh_material_sidecar_command_arm_checklist_boundary.py",
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "sourceProofCount=57",
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount=56",
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount=10",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount=10",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows=99",
        "definedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
        "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=0",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount=99",
        "publicAllowedOutputCount=100",
        "redactedFieldCount=47",
        "falseGuardCount=266",
        "zeroCounterCount=220",
        "publicLeakCheck=PASS",
        "no command arming",
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
        "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.md",
        "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1.json",
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_READINESS_GATE_STATUS,
        "sourceProofCount=57",
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount=56",
        "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows=99",
        "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount=99",
        "consumerArchiveTotalCount=301",
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
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks boundary slice active", failures)
    require(f"Completed {THIS_SLICE}" in text, "backlog missing completed boundary slice", failures)
    require(NEXT_SLICE in text, "backlog missing boundary-selected command materialization slice", failures)
    require(NEXT_SCOPE in text, "backlog missing boundary-selected command materialization scope", failures)
    require(active.count("The selected active static-to-proof slice is ") == 1, "active block should have exactly one active slice sentence", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-command-arm-checklist-boundary-proof")
        == r"py -3 tools\texture_mesh_material_sidecar_command_arm_checklist_boundary_proof_probe.py --check",
        "missing package boundary proof test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "boundary module missing", failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    if failures:
        print("Texture mesh material sidecar command arm-checklist boundary proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture mesh material sidecar command arm-checklist boundary proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
