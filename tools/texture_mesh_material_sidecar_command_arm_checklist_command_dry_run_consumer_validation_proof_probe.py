#!/usr/bin/env python3
"""Validate the public-safe command dry-run consumer-validation proof."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_command_arm_checklist_command_dry_run import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    PROOF_SCHEMA_VERSION as DRY_RUN_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
)
from texture_mesh_material_sidecar_command_arm_checklist_command_dry_run_consumer_validation import (
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_command_dry_run_consumer_validation_proof,
    build_public_safe_command_dry_run_consumer_validation_summary,
)


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_command_arm_checklist_command_dry_run_consumer_validation_proof_2026-06-16.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_command_arm_checklist_command_dry_run_consumer_validation.py"
SOURCE_DRY_RUN_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.v1.json"
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

EXPECTED_SCRIPT = r"py -3 tools\texture_mesh_material_sidecar_command_arm_checklist_command_dry_run_consumer_validation_proof_probe.py --check"
ADVANCED_ACTIVE_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan"
)
ADVANCED_ACTIVE_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-proof-plan"
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


def check_source_dry_run(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_DRY_RUN_RESULT)
    require(source.get("schemaVersion") == DRY_RUN_PROOF_SCHEMA_VERSION, "source schema mismatch", failures)
    require(source.get("status") == "PASS", "source status mismatch", failures)
    require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
        "source dry-run status mismatch",
        failures,
    )
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected-next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected-next scope mismatch", failures)
    return source


def check_result_and_mirror(source: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    summary = build_public_safe_command_dry_run_consumer_validation_summary(source)
    expected = build_public_safe_command_dry_run_consumer_validation_proof(summary)
    actual = read_json(RESULT)
    require(actual == expected, "tracked dry-run consumer-validation JSON does not match module rebuild", failures)
    require(read_json(LORE_RESULT) == actual, "lore dry-run consumer-validation JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore dry-run consumer-validation markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "consumer-validation status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    source = result["sourceEvidence"]
    require(source["sourceProofCount"] == 62, "source proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount"] == 61, "source dry-run proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount"] == 10, "source dry-run interface count mismatch", failures)
    require(source["commandDryRunConsumerValidationInterfaceCount"] == 10, "consumer-validation interface count mismatch", failures)
    require(
        tuple(source["sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_INTERFACES,
        "source dry-run interfaces mismatch",
        failures,
    )
    require(
        tuple(source["commandDryRunConsumerValidationInterfaces"])
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_INTERFACES,
        "consumer-validation interfaces mismatch",
        failures,
    )

    decision = result["realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationOnly",
        "commandDryRunProofConsumed",
        "commandDryRunProofContinuityValidated",
        "commandDryRunRowsConsumedByConsumerValidation",
        "commandDryRunConsumerValidationExecuted",
        "commandDryRunConsumerValidationInputAccepted",
        "commandDryRunArtifactSchemaValidated",
        "commandDryRunRowOrdinalsValidated",
        "commandDryRunNonDispatchedStatusesValidated",
        "commandDryRunAggregateCountsValidated",
        "commandDryRunConsumerValidationInterfacesValidated",
        "commandDryRunConsumerValidationEmitsOnlyPublicSafeRows",
        "commandDryRunConsumerValidationGuardCountersValidated",
        "commandArmReadinessGateLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision.get(key) is True, f"decision true flag mismatch: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)

    contract = result["realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationContract"]
    expected_counts = {
        "commandDryRunRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandDryRunConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonDispatchedCommandDryRunRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)

    rows = contract["commandDryRunConsumerValidationRowsBody"]
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "consumer-validation row count mismatch", failures)
    require(Counter(row["category"] for row in rows) == EXPECTED_CATEGORY_COUNTS, "consumer-validation category count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        row_id = f"dry-run consumer-validation row {expected_ordinal}"
        require(row["commandDryRunConsumerValidationRowOrdinal"] == expected_ordinal, f"{row_id} ordinal mismatch", failures)
        require(row["sourceCommandDryRunRowOrdinal"] == expected_ordinal, f"{row_id} source ordinal mismatch", failures)
        require(row["commandDryRunConsumerValidationStatus"] == "validated-public-safe-non-dispatched-command-dry-run-row", f"{row_id} status mismatch", failures)
        require(row["commandArmStatus"] == "not-armed", f"{row_id} arm status mismatch", failures)
        require(row["commandExecutionStatus"] == "not-executed", f"{row_id} execution mismatch", failures)
        require(row["commandDispatchAllowedHere"] is False, f"{row_id} dispatch guard mismatch", failures)
        require(row["directRealImporterDryRunAllowedHere"] is False, f"{row_id} real importer guard mismatch", failures)
        require(row["privateValuePublished"] is False, f"{row_id} private value flag mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row[key] == 0, f"{row_id} zero mismatch: {key}", failures)

    redaction = result["redactionPolicy"]
    require(redaction["publicAllowedOutputCount"] == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction["redactedFieldCount"] == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public output list mismatch", failures)
    require(tuple(redaction["redactedFields"]) == REDACTED_FIELDS, "redacted field list mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction public leak mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard[key] == 0, f"zero counter mismatch: {key}", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)


def check_docs_and_package(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        PREVIOUS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_STATUS,
        "sourceProofCount=62",
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount=61",
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount=10",
        "commandDryRunConsumerValidationInterfaceCount=10",
        "commandDryRunRowsConsumed=99",
        "commandDryRunConsumerValidationRows=99",
        "validatedNonDispatchedCommandDryRunRowCount=99",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=99",
        "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=1",
        f"publicAllowedOutputCount={len(PUBLIC_ALLOWED_OUTPUTS)}",
        f"redactedFieldCount={len(REDACTED_FIELDS)}",
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
        "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.md",
        "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json",
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_STATUS,
        "sourceProofCount=62",
        "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount=61",
        "commandDryRunRowsConsumed=99",
        "commandDryRunConsumerValidationRows=99",
        "validatedNonDispatchedCommandDryRunRowCount=99",
        f"publicAllowedOutputCount={len(PUBLIC_ALLOWED_OUTPUTS)}",
        f"redactedFieldCount={len(REDACTED_FIELDS)}",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "commandArmReadinessGateLaneSelected=true",
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
    require(f"Completed {THIS_SLICE}" in text, "backlog missing completed dry-run consumer-validation slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in text, "backlog missing completed command dry-run slice", failures)
    require(f"The selected active static-to-proof slice is {ADVANCED_ACTIVE_SLICE}. Status: selected" in active, "active slice not moved past command arm-readiness lane", failures)
    require(ADVANCED_ACTIVE_SCOPE in active, "active scope not moved past command arm-readiness lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "command arm-readiness scope still active", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "dry-run consumer-validation scope still active", failures)
    require(active.count("The selected active static-to-proof slice is ") == 1, "active block should have exactly one active slice sentence", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof") == EXPECTED_SCRIPT,
        "missing package dry-run consumer-validation test script",
        failures,
    )
    require(MODULE.is_file(), "missing dry-run consumer-validation generator module", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        source = check_source_dry_run(failures)
        result = check_result_and_mirror(source, failures)
        check_contract(result, failures)
        check_docs_and_package(failures)
        check_no_bad_public_content(RESULT, failures)
    except Exception as exc:  # pragma: no cover - probe output is user-facing.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture mesh material sidecar command dry-run consumer-validation proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture mesh material sidecar command dry-run consumer-validation proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
