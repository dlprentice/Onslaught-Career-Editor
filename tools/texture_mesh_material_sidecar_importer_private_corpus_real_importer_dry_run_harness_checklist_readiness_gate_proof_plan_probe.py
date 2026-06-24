#!/usr/bin/env python3
"""Validate private-corpus real-importer dry-run harness checklist readiness gate."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_readiness_gate import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES,
    REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_proof,
    build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary,
    validate_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_validation import (
    NEXT_SCOPE as VALIDATION_NEXT_SCOPE,
    NEXT_SLICE as VALIDATION_NEXT_SLICE,
    PROOF_SCHEMA_VERSION as VALIDATION_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_readiness_gate_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_readiness_gate.py"

SOURCE_VALIDATION_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.v1.json"
SOURCE_VALIDATION_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.md"

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
    r"checklist_readiness_gate_proof_plan_probe.py --check"
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
    "harness command materialized",
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


def check_source_validation(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_VALIDATION_RESULT)
    require(source.get("schemaVersion") == VALIDATION_PROOF_SCHEMA_VERSION, "source validation schema mismatch", failures)
    require(source.get("status") == "PASS", "source validation status mismatch", failures)
    require(
        source.get("privateCorpusRealImporterDryRunHarnessChecklistValidationStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION_STATUS,
        "source validation token mismatch",
        failures,
    )
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch", failures)
    require(VALIDATION_NEXT_SLICE == THIS_SLICE, "source module next slice mismatch", failures)
    require(VALIDATION_NEXT_SCOPE == THIS_SCOPE, "source module next scope mismatch", failures)
    require(SOURCE_VALIDATION_PROOF.is_file(), "missing source validation proof doc", failures)
    return source


def check_result_and_mirror(source: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    summary = build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(source)
    validate_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_summary(summary)
    expected = build_public_safe_real_importer_dry_run_harness_checklist_readiness_gate_proof(summary)
    actual = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(actual == expected, "tracked readiness JSON does not match module rebuild", failures)
    require(lore == actual, "lore readiness JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore readiness markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "readiness proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "readiness proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessChecklistReadinessGateStatus")
        == REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
        "readiness status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    decision = result.get("realImporterHarnessChecklistReadinessGateDecision", {})
    contract = result.get("realImporterHarnessChecklistReadinessGateContract", {})
    guard = result.get("guardSummary", {})
    redaction = result.get("redactionPolicy", {})
    for key in (
        "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateOnly",
        "realImporterHarnessChecklistValidationProofConsumed",
        "realImporterHarnessChecklistValidationProofContinuityValidated",
        "realImporterHarnessChecklistValidationRowsConsumed",
        "realImporterDryRunHarnessChecklistReadinessGateExecuted",
        "realImporterDryRunHarnessChecklistReadinessGateInputAccepted",
        "harnessChecklistReadinessGatePreconditionsValidated",
        "harnessChecklistReadyRowStatusesValidated",
        "harnessChecklistReadinessGateRowOrdinalsValidated",
        "harnessChecklistReadinessGateCategoryCountsValidated",
        "harnessChecklistCommandPrerequisiteClassesValidated",
        "harnessChecklistReadinessGateEmitsOnlyPublicSafeRows",
        "harnessChecklistReadinessGateRedactionPolicyValidated",
        "harnessCommandMaterializationLaneSelected",
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
        "realImporterDryRunHarnessCommandMaterialized",
        "realImporterDryRunHarnessCommandPrivateOutputGenerated",
        "actualAssetImportExecuted",
        "generatedAssetOutputExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)
    require(contract.get("harnessChecklistValidationRowsConsumed") == EXPECTED_CHECKLIST_ROW_COUNT, "consumed validation count mismatch", failures)
    require(contract.get("harnessChecklistReadinessGateRows") == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row count mismatch", failures)
    require(contract.get("passedReadinessGateRowCount") == EXPECTED_CHECKLIST_ROW_COUNT, "passed row count mismatch", failures)
    require(contract.get("failedReadinessGateRowCount") == 0, "failed row count mismatch", failures)
    require(contract.get("readyForLaterCommandMaterializationRowCount") == EXPECTED_CHECKLIST_ROW_COUNT, "command-ready row count mismatch", failures)
    require(contract.get("readyForLaterHarnessArmRowCount") == EXPECTED_CHECKLIST_ROW_COUNT, "harness-arm row count mismatch", failures)
    require(contract.get("observedChecklistRowCount") == 0, "observed row count mismatch", failures)
    require(contract.get("rowStatusChangedCount") == 0, "row status changed count mismatch", failures)
    require(contract.get("preflightCheckCount") == 17, "preflight count mismatch", failures)
    require(contract.get("passedPreflightCheckCount") == 17, "passed preflight count mismatch", failures)
    require(contract.get("failedPreflightCheckCount") == 0, "failed preflight count mismatch", failures)
    require(contract.get("consumerArchiveTotalCount") == 301, "archive total mismatch", failures)
    require(contract.get("unknownAyaArchiveClassCount") == 0, "unknown archive class mismatch", failures)
    require(contract.get("publicSafeHarnessChecklistReadinessGateArtifactRows") == 1, "public-safe artifact count mismatch", failures)
    require(redaction.get("publicAllowedOutputCount") == 5, "public allowed output count mismatch", failures)
    require(redaction.get("redactedFieldCount") == 10, "redacted field count mismatch", failures)
    require(guard.get("falseGuardCount") == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard.get("zeroCounterCount") == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(guard.get("publicLeakCheck") == "PASS", "public leak guard mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard.get(key) == 0, f"zero counter mismatch: {key}", failures)

    rows = contract.get("harnessChecklistReadinessGateRowsBody", [])
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "readiness row body count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row-body category count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(row.get("harnessChecklistReadinessGateRowOrdinal") == expected_ordinal, f"readiness ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("sourceHarnessChecklistValidationRowOrdinal") == expected_ordinal, f"source validation ordinal mismatch: {expected_ordinal}", failures)
        require(row.get("readinessGateStatus") == "ready-for-later-explicit-harness-command-materialization", f"readiness status mismatch: {expected_ordinal}", failures)
        require(row.get("sourceValidationStatus") == "validated-public-safe-not-run-unobserved", f"source validation mismatch: {expected_ordinal}", failures)
        require(row.get("sourceRowStatus") == "not-run", f"source row status mismatch: {expected_ordinal}", failures)
        require(row.get("sourceObservationStatus") == "unobserved", f"source observation mismatch: {expected_ordinal}", failures)
        require(row.get("privateValuePublished") is False, f"private value flag mismatch: {expected_ordinal}", failures)
        require(row.get("directRealImporterDryRunAllowedHere") is False, f"direct importer flag mismatch: {expected_ordinal}", failures)
        require(row.get("futureHarnessCommandMaterializationRequiresLaterArm") is True, f"command later-arm flag mismatch: {expected_ordinal}", failures)
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


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_STATUS,
        NEXT_SLICE,
        NEXT_SCOPE,
        "sourceProofCount=25",
        "sourceChecklistValidationProofCount=24",
        "harnessChecklistReadinessGateRows=99",
        "readyForLaterCommandMaterializationRowCount=99",
        "falseGuardCount=100",
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
        require(THIS_SLICE in read_text(path), f"{path.relative_to(ROOT)} missing completed readiness-gate slice", failures)
    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan")
        == EXPECTED_SCRIPT,
        "missing package readiness-gate probe script",
        failures,
    )
    require(MODULE.is_file(), "missing readiness-gate generator module", failures)
    require(
        len(REAL_IMPORTER_HARNESS_CHECKLIST_READINESS_GATE_INTERFACES) == 12,
        "readiness-gate interface count mismatch",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    try:
        source = check_source_validation(failures)
        result = check_result_and_mirror(source, failures)
        check_contract(result, failures)
        check_docs(failures)
    except Exception as exc:  # pragma: no cover - probe output is user-facing.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture/mesh material sidecar real-importer harness checklist readiness-gate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness checklist readiness-gate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
