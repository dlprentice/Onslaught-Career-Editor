#!/usr/bin/env python3
"""Validate private-corpus real-importer dry-run harness checklist validation."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_validation import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES,
    REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_checklist_validation_proof,
    build_public_safe_real_importer_dry_run_harness_checklist_validation_summary,
    validate_public_safe_real_importer_dry_run_harness_checklist_validation_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population import (
    NEXT_SCOPE as POPULATION_NEXT_SCOPE,
    NEXT_SLICE as POPULATION_NEXT_SLICE,
    PROOF_SCHEMA_VERSION as POPULATION_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_validation_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_validation.py"

SOURCE_POPULATION_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json"
SOURCE_POPULATION_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md"
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

EXPECTED_SCRIPT = (
    r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_"
    r"checklist_validation_proof_plan_probe.py --check"
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


def check_source_population(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_POPULATION_RESULT)
    require(source.get("schemaVersion") == POPULATION_PROOF_SCHEMA_VERSION, "source population schema mismatch", failures)
    require(source.get("status") == "PASS", "source population status mismatch", failures)
    require(
        source.get("privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS,
        "source population token mismatch",
        failures,
    )
    require(POPULATION_NEXT_SLICE == THIS_SLICE, "module population next-slice import mismatch", failures)
    require(POPULATION_NEXT_SCOPE == THIS_SCOPE, "module population next-scope import mismatch", failures)
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch", failures)
    require(REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION_STATUS in read_text(SOURCE_POPULATION_PROOF), "source population markdown missing token", failures)
    return source


def check_result_and_mirror(source: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    summary = build_public_safe_real_importer_dry_run_harness_checklist_validation_summary(source)
    validate_public_safe_real_importer_dry_run_harness_checklist_validation_summary(summary)
    expected = build_public_safe_real_importer_dry_run_harness_checklist_validation_proof(summary)
    actual = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(actual == expected, "tracked validation JSON does not match module rebuild", failures)
    require(lore == actual, "lore validation JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore validation markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "validation proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "validation proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "validation status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "selected next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "selected next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    decision = result.get("realImporterHarnessChecklistValidationDecision", {})
    contract = result.get("realImporterHarnessChecklistValidationContract", {})
    guard = result.get("guardSummary", {})
    require(decision.get("realImporterDryRunHarnessChecklistValidationExecuted") is True, "validation execution flag mismatch", failures)
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
        "realImporterDryRunHarnessChecklistValidationReadPrivateInputs",
        "realImporterDryRunHarnessChecklistValidationPublishedPrivateInput",
        "realImporterDryRunHarnessChecklistReadinessGateExecuted",
        "realImporterDryRunHarnessCommandArmed",
        "realImporterDryRunHarnessCommandMaterialized",
        "realImporterDryRunHarnessPrivateOutputGenerated",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
    ):
        require(decision.get(key) is False, f"decision false guard mismatch: {key}", failures)
    require(contract.get("harnessChecklistRowsConsumed") == EXPECTED_CHECKLIST_ROW_COUNT, "consumed checklist count mismatch", failures)
    require(contract.get("harnessChecklistValidationRows") == EXPECTED_CHECKLIST_ROW_COUNT, "validation row count mismatch", failures)
    require(contract.get("passedValidationRowCount") == EXPECTED_CHECKLIST_ROW_COUNT, "passed row count mismatch", failures)
    require(contract.get("failedValidationRowCount") == 0, "failed row count mismatch", failures)
    require(contract.get("validatedNotRunChecklistRowCount") == EXPECTED_CHECKLIST_ROW_COUNT, "not-run row count mismatch", failures)
    require(contract.get("validatedUnobservedChecklistRowCount") == EXPECTED_CHECKLIST_ROW_COUNT, "unobserved row count mismatch", failures)
    require(contract.get("observedChecklistRowCount") == 0, "observed row count mismatch", failures)
    require(contract.get("rowStatusChangedCount") == 0, "row status changed count mismatch", failures)
    require(contract.get("preflightCheckCount") == 17, "preflight count mismatch", failures)
    require(contract.get("consumerArchiveTotalCount") == 301, "archive total count mismatch", failures)
    require(contract.get("unknownAyaArchiveClassCount") == 0, "unknown archive class mismatch", failures)
    require(contract.get("realImporterDryRunHarnessChecklistValidationInterfaceCount") == len(REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_INTERFACES), "interface count mismatch", failures)
    category_counts = {row["category"]: row["validatedRowCount"] for row in contract.get("checklistCategoryCounts", [])}
    require(category_counts == EXPECTED_CATEGORY_COUNTS, "validation category count mismatch", failures)
    rows = contract.get("harnessChecklistValidationRowsBody", [])
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "validation row body count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row-body category count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(row.get("harnessChecklistValidationRowOrdinal") == expected_ordinal, f"validation ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("sourceHarnessChecklistRowOrdinal") == expected_ordinal, f"source ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("validationStatus") == "validated-public-safe-not-run-unobserved", f"validation status mismatch: {expected_ordinal}", failures)
        require(row.get("sourceRowStatus") == "not-run", f"source row status mismatch: {expected_ordinal}", failures)
        require(row.get("sourceObservationStatus") == "unobserved", f"source observation mismatch: {expected_ordinal}", failures)
        require(row.get("privateValuePublished") is False, f"private value flag mismatch: {expected_ordinal}", failures)
        require(row.get("directRealImporterDryRunAllowedHere") is False, f"direct importer flag mismatch: {expected_ordinal}", failures)
        for counter in (
            "actualAssetImportRows",
            "byteLengthRows",
            "generatedAssetRows",
            "privateDryRunRows",
            "rawFilenameRows",
            "rawHashRows",
            "rawMeshRefRows",
            "rawPathRows",
            "rawStemRows",
            "rawTextureRefRows",
            "realImporterDryRunHarnessRows",
            "realImporterDryRunRows",
        ):
            require(row.get(counter) == 0, f"row zero counter mismatch {expected_ordinal}: {counter}", failures)
    require(guard.get("falseGuardCount") == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard.get("zeroCounterCount") == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(guard.get("publicLeakCheck") == "PASS", "public leak guard mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"guard zero counter mismatch: {key}", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "sourceRealImporterHarnessChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-complete-public-safe-checklist-populated-not-real-importer-execution",
        "harnessChecklistValidationRows=99",
        "validatedNotRunChecklistRowCount=99",
        "validatedUnobservedChecklistRowCount=99",
        "consumerArchiveTotalCount=301",
        "falseGuardCount=98",
        "zeroCounterCount=85",
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
        require(
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Consumer Validation Proof Plan" in active,
            f"{path.relative_to(ROOT)} active slice not moved to command consumer validation",
            failures,
        )
        require(
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan" in active,
            f"{path.relative_to(ROOT)} active scope not moved to command consumer validation",
            failures,
        )
        require(THIS_SLICE in read_text(path), f"{path.relative_to(ROOT)} missing completed validation slice", failures)
    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan")
        == EXPECTED_SCRIPT,
        "missing package validation probe script",
        failures,
    )
    progress = read_json(PROGRESS)
    quality = progress.get("functionQuality", {})
    require(quality.get("totalFunctions") == 6411, "static progress total mismatch", failures)
    require(quality.get("commentedFunctions") == 6411, "static progress commented mismatch", failures)
    require(quality.get("commentlessFunctions") == 0, "static progress commentless mismatch", failures)
    require(quality.get("undefinedSignatures") == 0, "static progress undefined mismatch", failures)
    require(quality.get("paramSignatures") == 0, "static progress param_N mismatch", failures)
    require(MODULE.is_file(), "validation module missing", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    try:
        source = check_source_population(failures)
        result = check_result_and_mirror(source, failures)
        check_contract(result, failures)
        check_docs(failures)
        check_no_bad_public_content(RESULT, failures)
        require(no_bea_process_running(), "BEA.exe process is running", failures)
    except Exception as exc:  # pragma: no cover - probe reports exact failure text.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture/mesh material sidecar real-importer harness checklist validation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness checklist validation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
