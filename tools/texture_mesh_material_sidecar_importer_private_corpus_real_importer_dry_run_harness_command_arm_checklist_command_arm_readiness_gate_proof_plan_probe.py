#!/usr/bin/env python3
"""Validate private-corpus real-importer harness command arm-checklist command arm-readiness proof."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate import (
    COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF,
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
    REDACTED_FIELDS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_proof,
    build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_summary,
    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate.py"
SOURCE_RESULT = ROOT / COMMAND_ARM_CHECKLIST_COMMAND_DRY_RUN_CONSUMER_VALIDATION_PROOF

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

ACTIVE_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan"
ACTIVE_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-validation-proof-plan"
EXPECTED_SCRIPT = (
    r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_"
    r"command_arm_checklist_command_arm_readiness_gate_proof_plan_probe.py --check"
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "ignored artifact path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)textureRefSample|sampleRows|canonical_ref|canonicalRef|fbxTexturePath|exportFilePath"), "row-level private sample field"),
    (re.compile(r"(?i)asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "private asset content parsed",
    "raw private corpus manifest consumed",
    "private raw manifest rows consumed",
    "runnable real-importer harness command materialized",
    "command armed",
    "harness command armed",
    "harness command executed",
    "shell command dispatched",
    "real importer complete",
    "real importer execution complete",
    "asset import complete",
    "generated asset output complete",
    "runtime texture pixels proven",
    "runtime mesh loading proven",
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


def check_result_and_mirror(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_RESULT)
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch", failures)

    summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_summary(source)
    validate_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_summary(summary)
    expected = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_readiness_gate_proof(summary)
    actual = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(actual == expected, "tracked command arm-checklist command arm-readiness JSON does not match module rebuild", failures)
    require(lore == actual, "lore command arm-checklist command arm-readiness JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore command arm-checklist command arm-readiness markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        "command arm-checklist command arm-readiness status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    decision = result.get("realImporterHarnessCommandArmChecklistCommandArmReadinessGateDecision", {})
    contract = result.get("realImporterHarnessCommandArmChecklistCommandArmReadinessGateContract", {})
    guard = result.get("guardSummary", {})
    redaction = result.get("redactionPolicy", {})
    source = result.get("sourceEvidence", {})

    expected_counts = {
        "sourceProofCount": 41,
        "sourceCommandArmChecklistCommandDryRunConsumerValidationProofCount": 40,
        "sourceCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount": 10,
        "commandArmChecklistCommandArmReadinessGateInterfaceCount": 10,
    }
    for key, expected in expected_counts.items():
        require(source.get(key) == expected, f"source evidence mismatch: {key}", failures)

    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateOnly",
        "commandArmChecklistCommandDryRunConsumerValidationProofConsumed",
        "commandArmChecklistCommandDryRunConsumerValidationProofContinuityValidated",
        "commandArmChecklistCommandDryRunConsumerValidationProofRowsConsumed",
        "commandArmChecklistCommandArmReadinessGateExecuted",
        "commandArmChecklistCommandArmReadinessGateInputAccepted",
        "commandArmChecklistCommandArmReadinessGatePreconditionsValidated",
        "commandArmChecklistCommandArmReadinessGateRowStatusesValidated",
        "commandArmChecklistCommandArmReadinessGateRowOrdinalsValidated",
        "commandArmChecklistCommandArmReadinessGateCategoryCountsValidated",
        "commandArmChecklistCommandArmReadinessGateInterfacesValidated",
        "commandArmChecklistCommandArmReadinessGateEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmReadinessGateRedactionPolicyValidated",
        "harnessCommandArmChecklistCommandArmBoundaryLaneSelected",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision.get(key) is True, f"decision true flag mismatch: {key}", failures)
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
        "realImporterDryRunHarnessCommandArmed",
        "realImporterDryRunHarnessCommandExecuted",
        "realImporterDryRunHarnessCommandSentToShell",
        "realImporterDryRunHarnessCommandPrivateOutputGenerated",
        "realImporterDryRunHarnessRunnableCommandMaterialized",
        "realImporterDryRunHarnessCommandArmChecklistCommandDryRunExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandDryRunSentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandDryRunPrivateOutputGenerated",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateReadPrivateInputs",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGatePublishedPrivateInput",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryExecuted",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundarySentToShell",
        "realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryPrivateOutputGenerated",
        "privateCommandArmChecklistCommandArmReadinessGateArtifactPublished",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)

    expected_contract_counts = {
        "commandArmChecklistCommandDryRunConsumerValidationRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmReadinessGateRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "passedCommandArmChecklistCommandArmReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "failedCommandArmChecklistCommandArmReadinessGateRowCount": 0,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmBoundaryRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmReadinessGateArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_contract_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)
    require(redaction.get("publicAllowedOutputCount") == len(PUBLIC_ALLOWED_OUTPUTS), "public allowed output count mismatch", failures)
    require(redaction.get("redactedFieldCount") == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(guard.get("falseGuardCount") == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard.get("zeroCounterCount") == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(guard.get("publicLeakCheck") == "PASS", "public leak guard mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"zero counter mismatch: {key}", failures)

    rows = contract.get("commandArmChecklistCommandArmReadinessGateRowsBody", [])
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "arm-readiness row body count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row-body category count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(row.get("commandArmChecklistCommandArmReadinessGateRowOrdinal") == expected_ordinal, f"arm-readiness ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("sourceCommandArmChecklistCommandDryRunConsumerValidationRowOrdinal") == expected_ordinal, f"source dry-run consumer-validation ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("commandArmStatus") == "not-armed", f"command arm status mismatch: {expected_ordinal}", failures)
        require(row.get("commandExecutionStatus") == "not-executed", f"command execution status mismatch: {expected_ordinal}", failures)
        require(row.get("commandDispatchAllowedHere") is False, f"command dispatch guard mismatch: {expected_ordinal}", failures)
        require(row.get("futureHarnessCommandArmChecklistCommandArmBoundaryRequiresLaterReview") is True, f"future arm-boundary guard mismatch: {expected_ordinal}", failures)
        require(row.get("privateValuePublished") is False, f"private value flag mismatch: {expected_ordinal}", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_STATUS,
        NEXT_SLICE,
        NEXT_SCOPE,
        "sourceProofCount=41",
        "sourceCommandArmChecklistCommandDryRunConsumerValidationProofCount=40",
        "commandArmChecklistCommandDryRunConsumerValidationRowsConsumed=99",
        "commandArmChecklistCommandArmReadinessGateRows=99",
        "passedCommandArmChecklistCommandArmReadinessGateRowCount=99",
        "failedCommandArmChecklistCommandArmReadinessGateRowCount=0",
        "armedCommandRowCount=0",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
        "readyForLaterCommandArmChecklistCommandArmBoundaryRowCount=99",
        f"publicAllowedOutputCount={len(PUBLIC_ALLOWED_OUTPUTS)}",
        f"redactedFieldCount={len(REDACTED_FIELDS)}",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
    )
    docs = (PROOF, READINESS, GAME_ASSETS_INDEX, LORE_GAME_ASSETS_INDEX, RE_INDEX, LORE_RE_INDEX, BIN_INDEX, LORE_BIN_INDEX, MAPPED, LORE_MAPPED, BACKLOG, LORE_BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
    for path in (PROOF, LORE_PROOF, READINESS):
        check_no_bad_public_content(path, failures)
    for path in (BACKLOG, LORE_BACKLOG):
        active = active_slice_block(read_text(path))
        require(ACTIVE_SLICE in active, f"{path.relative_to(ROOT)} active slice not moved to command arm boundary", failures)
        require(ACTIVE_SCOPE in active, f"{path.relative_to(ROOT)} active scope not moved to command arm boundary", failures)
        require(THIS_SLICE in read_text(path), f"{path.relative_to(ROOT)} missing completed command arm-readiness slice", failures)
        require(active.count("The selected active static-to-proof slice is ") == 1, f"{path.relative_to(ROOT)} active block should have exactly one active slice sentence", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan")
        == EXPECTED_SCRIPT,
        "missing package command arm-checklist command arm-readiness probe script",
        failures,
    )
    require(MODULE.is_file(), "missing command arm-checklist command arm-readiness generator module", failures)
    require(len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_READINESS_GATE_INTERFACES) == 10, "arm-readiness interface count mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    try:
        result = check_result_and_mirror(failures)
        check_contract(result, failures)
        check_docs(failures)
    except Exception as exc:  # pragma: no cover - probe output is user-facing.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture/mesh material sidecar real-importer harness command arm-checklist command arm-readiness probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness command arm-checklist command arm-readiness probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
