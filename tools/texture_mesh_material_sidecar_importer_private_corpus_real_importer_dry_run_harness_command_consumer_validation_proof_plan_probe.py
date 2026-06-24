#!/usr/bin/env python3
"""Validate private-corpus real-importer harness command consumer-validation proof."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_consumer_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_command_consumer_validation_proof,
    build_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary,
    validate_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_materialization import (
    NEXT_SCOPE as COMMAND_MATERIALIZATION_NEXT_SCOPE,
    NEXT_SLICE as COMMAND_MATERIALIZATION_NEXT_SLICE,
    PROOF_SCHEMA_VERSION as COMMAND_MATERIALIZATION_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_consumer_validation_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_consumer_validation.py"

SOURCE_COMMAND_MATERIALIZATION_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-proof-plan.v1.json"
SOURCE_COMMAND_MATERIALIZATION_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-proof-plan.md"

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

EXPECTED_SCRIPT = (
    r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_"
    r"command_consumer_validation_proof_plan_probe.py --check"
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
    "real importer complete",
    "real importer implementation complete",
    "real importer execution complete",
    "private importer dry-run complete",
    "real importer dry-run complete",
    "real importer dry-run harness complete",
    "harness command armed",
    "harness command executed",
    "shell command dispatched",
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


def check_source_command_materialization(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_COMMAND_MATERIALIZATION_RESULT)
    require(source.get("schemaVersion") == COMMAND_MATERIALIZATION_PROOF_SCHEMA_VERSION, "source schema mismatch", failures)
    require(source.get("status") == "PASS", "source status mismatch", failures)
    require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_STATUS,
        "source command materialization status token mismatch",
        failures,
    )
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch", failures)
    require(COMMAND_MATERIALIZATION_NEXT_SLICE == THIS_SLICE, "source module next slice mismatch", failures)
    require(COMMAND_MATERIALIZATION_NEXT_SCOPE == THIS_SCOPE, "source module next scope mismatch", failures)
    require(SOURCE_COMMAND_MATERIALIZATION_PROOF.is_file(), "missing source command materialization proof doc", failures)
    return source


def check_result_and_mirror(source: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    summary = build_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(source)
    validate_public_safe_real_importer_dry_run_harness_command_consumer_validation_summary(summary)
    expected = build_public_safe_real_importer_dry_run_harness_command_consumer_validation_proof(summary)
    actual = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(actual == expected, "tracked command consumer-validation JSON does not match module rebuild", failures)
    require(lore == actual, "lore command consumer-validation JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore command consumer-validation markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "command consumer-validation proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "command consumer-validation proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessCommandConsumerValidationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS,
        "command consumer-validation status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    decision = result.get("realImporterHarnessCommandConsumerValidationDecision", {})
    contract = result.get("realImporterHarnessCommandConsumerValidationContract", {})
    guard = result.get("guardSummary", {})
    redaction = result.get("redactionPolicy", {})
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationOnly",
        "commandMaterializationProofConsumed",
        "commandContractArtifactConsumed",
        "commandContractArtifactContinuityValidated",
        "commandConsumerValidationExecuted",
        "commandConsumerValidationInputAccepted",
        "commandContractArtifactSchemaValidated",
        "commandContractRowOrdinalsValidated",
        "commandContractNonArmedStatusesValidated",
        "commandContractAggregateCountsValidated",
        "commandConsumerValidationInterfacesValidated",
        "commandConsumerValidationEmitsOnlyPublicSafeRows",
        "harnessCommandReadinessGateLaneSelected",
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
        "realImporterDryRunHarnessCommandConsumerValidationReadPrivateInputs",
        "realImporterDryRunHarnessCommandConsumerValidationPublishedPrivateInput",
        "realImporterDryRunHarnessCommandConsumerValidationExecutedShellCommand",
        "privateCommandConsumerValidationArtifactPublished",
        "realImporterDryRunHarnessCommandReadinessGateExecuted",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)

    expected_counts = {
        "harnessCommandContractRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandConsumerValidationRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "validatedNonArmedCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandReadinessGateRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandConsumerValidationArtifactRows": 1,
        "publicAllowedOutputCount": 9,
        "redactedFieldCount": 13,
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)
    require(redaction.get("publicAllowedOutputCount") == 9, "public allowed output count mismatch", failures)
    require(redaction.get("redactedFieldCount") == 13, "redacted field count mismatch", failures)
    require(guard.get("falseGuardCount") == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard.get("zeroCounterCount") == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(guard.get("publicLeakCheck") == "PASS", "public leak guard mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"zero counter mismatch: {key}", failures)

    rows = contract.get("commandConsumerValidationRowsBody", [])
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command consumer row body count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row-body category count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(row.get("commandConsumerValidationRowOrdinal") == expected_ordinal, f"consumer ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("sourceCommandContractRowOrdinal") == expected_ordinal, f"source command ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("commandArmStatus") == "not-armed", f"command arm status mismatch: {expected_ordinal}", failures)
        require(row.get("commandExecutionStatus") == "not-executed", f"command execution status mismatch: {expected_ordinal}", failures)
        require(row.get("commandDispatchAllowedHere") is False, f"command dispatch guard mismatch: {expected_ordinal}", failures)
        require(row.get("futureHarnessArmRequiresOperatorAction") is True, f"future harness arm guard mismatch: {expected_ordinal}", failures)
        require(row.get("privateValuePublished") is False, f"private value flag mismatch: {expected_ordinal}", failures)
        for counter in (
            "actualAssetImportRows",
            "byteLengthRows",
            "commandExecutionRows",
            "commandPrivateOutputRows",
            "commandShellDispatchRows",
            "generatedAssetRows",
            "privateDryRunRows",
            "publishedCommandArgumentRows",
            "rawCommandArgumentRows",
            "rawFilenameRows",
            "rawHashRows",
            "rawMeshRefRows",
            "rawPathRows",
            "rawStemRows",
            "rawTextureRefRows",
            "realImporterDryRunHarnessCommandConsumerValidationRows",
            "realImporterDryRunHarnessCommandExecutionRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunRows",
        ):
            require(row.get(counter) == 0, f"row zero counter mismatch {expected_ordinal}: {counter}", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_STATUS,
        NEXT_SLICE,
        NEXT_SCOPE,
        "sourceProofCount=27",
        "sourceCommandMaterializationProofCount=26",
        "harnessCommandContractRowsConsumed=99",
        "commandConsumerValidationRows=99",
        "validatedNonArmedCommandContractRowCount=99",
        "armedCommandRowCount=0",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
        "falseGuardCount=111",
        "zeroCounterCount=92",
        "publicLeakCheck=PASS",
    )
    for path in (PROOF, READINESS, GAME_ASSETS_INDEX, LORE_GAME_ASSETS_INDEX, RE_INDEX, LORE_RE_INDEX, BIN_INDEX, LORE_BIN_INDEX, MAPPED, LORE_MAPPED, BACKLOG, LORE_BACKLOG):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
    for path in (PROOF, LORE_PROOF, READINESS):
        check_no_bad_public_content(path, failures)
    for path in (BACKLOG, LORE_BACKLOG):
        active = active_slice_block(read_text(path))
        require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active, f"{path.relative_to(ROOT)} active slice not moved to command dry-run", failures)
        require("texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan" in active, f"{path.relative_to(ROOT)} active scope not moved to command arm-checklist-population", failures)
        require(THIS_SLICE in read_text(path), f"{path.relative_to(ROOT)} missing completed command consumer-validation slice", failures)
        require(active.count("The selected active static-to-proof slice is ") == 1, f"{path.relative_to(ROOT)} active block should have exactly one active slice sentence", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan")
        == EXPECTED_SCRIPT,
        "missing package command consumer-validation probe script",
        failures,
    )
    require(MODULE.is_file(), "missing command consumer-validation generator module", failures)
    require(
        len(REAL_IMPORTER_HARNESS_COMMAND_MATERIALIZATION_INTERFACES) == 12,
        "source command materialization interface count mismatch",
        failures,
    )
    require(
        len(REAL_IMPORTER_HARNESS_COMMAND_CONSUMER_VALIDATION_INTERFACES) == 10,
        "command consumer-validation interface count mismatch",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    try:
        source = check_source_command_materialization(failures)
        result = check_result_and_mirror(source, failures)
        check_contract(result, failures)
        check_docs(failures)
    except Exception as exc:  # pragma: no cover - probe output is user-facing.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture/mesh material sidecar real-importer harness command consumer-validation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness command consumer-validation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
