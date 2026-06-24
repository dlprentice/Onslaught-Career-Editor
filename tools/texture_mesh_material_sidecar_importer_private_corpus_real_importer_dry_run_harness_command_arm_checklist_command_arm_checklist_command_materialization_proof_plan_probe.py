#!/usr/bin/env python3
"""Validate command arm-checklist command arm-checklist materialization artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_boundary import (
    PROOF_SCHEMA_VERSION as BOUNDARY_PROOF_SCHEMA_VERSION,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
)
from texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_CHECKLIST_ROW_COUNT,
    FALSE_GUARDS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES,
    REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
    REDACTED_FIELDS,
    ROW_ZERO_FIELDS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_proof,
    build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization.py"

SOURCE_BOUNDARY_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan.v1.json"

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
    r"command_arm_checklist_command_arm_checklist_command_materialization_proof_plan_probe.py --check"
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
    "runnable command materialized",
    "runnable command materialization complete",
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


def check_source_boundary(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_BOUNDARY_RESULT)
    require(source.get("schemaVersion") == BOUNDARY_PROOF_SCHEMA_VERSION, "source boundary schema mismatch", failures)
    require(source.get("status") == "PASS", "source boundary status mismatch", failures)
    require(
        source.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "source boundary token mismatch",
        failures,
    )
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selected next scope mismatch", failures)

    evidence = source.get("sourceEvidence", {})
    require(evidence.get("sourceProofCount") == 46, "source proof count mismatch", failures)
    require(
        evidence.get("sourceCommandArmChecklistCommandArmChecklistReadinessGateProofCount") == 45,
        "source readiness proof count mismatch",
        failures,
    )
    require(
        evidence.get("sourceCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount") == 10,
        "source readiness interface count mismatch",
        failures,
    )
    require(
        evidence.get("commandArmChecklistCommandArmChecklistBoundaryInterfaceCount")
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_INTERFACES),
        "source boundary interface count mismatch",
        failures,
    )
    return source


def check_result_and_mirror(source: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    summary = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_summary(
        source
    )
    expected = build_public_safe_real_importer_dry_run_harness_command_arm_checklist_command_arm_checklist_command_materialization_proof(
        summary
    )
    actual = read_json(RESULT)
    require(actual == expected, "tracked command materialization JSON does not match module rebuild", failures)
    require(read_json(LORE_RESULT) == actual, "lore command materialization JSON mirror mismatch", failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore command materialization markdown mirror mismatch", failures)
    require(actual.get("schemaVersion") == PROOF_SCHEMA_VERSION, "command materialization proof schema mismatch", failures)
    require(actual.get("status") == "PASS", "command materialization proof status mismatch", failures)
    require(
        actual.get("privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationStatus")
        == REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "command materialization status token mismatch",
        failures,
    )
    require(actual.get("previousSlice") == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(actual.get("previousScope") == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(actual.get("selectedNextSlice") == NEXT_SLICE, "next slice mismatch", failures)
    require(actual.get("selectedNextScope") == NEXT_SCOPE, "next scope mismatch", failures)
    return actual


def check_contract(result: dict[str, Any], failures: list[str]) -> None:
    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["activeCurrentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    source = result["sourceEvidence"]
    require(source["sourceProofCount"] == 47, "source proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount"] == 46, "source boundary proof count mismatch", failures)
    require(source["sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount"] == 10, "source boundary interface count mismatch", failures)
    require(
        source["commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount"]
        == len(REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_INTERFACES),
        "command materialization interface count mismatch",
        failures,
    )

    decision = result["realImporterHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationDecision"]
    for key in (
        "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationOnly",
        "commandArmChecklistCommandArmChecklistBoundaryProofConsumed",
        "commandArmChecklistCommandArmChecklistBoundaryProofContinuityValidated",
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumedByCommandMaterialization",
        "commandArmChecklistCommandArmChecklistCommandMaterializationExecuted",
        "commandArmChecklistCommandArmChecklistCommandMaterializationInputAccepted",
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractMaterialized",
        "publicSafeNonArmedCommandArmChecklistCommandArmChecklistCommandContractStoredInTrackedProof",
        "commandArmChecklistCommandArmChecklistCommandContractRowsGenerated",
        "commandArmChecklistCommandArmChecklistCommandContractRowsValidated",
        "commandArmChecklistCommandArmChecklistCommandContractAggregateCountsValidated",
        "commandArmChecklistCommandArmChecklistCommandContractInterfacesValidated",
        "commandArmChecklistCommandArmChecklistCommandContractNotArmedStatusesValidated",
        "commandArmChecklistCommandArmChecklistCommandContractEmitsOnlyPublicSafeRows",
        "commandArmChecklistCommandArmChecklistCommandContractRedactionPolicyValidated",
        "commandArmChecklistCommandArmChecklistCommandContractGuardCountersValidated",
        "commandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected",
        "futureCommandArmRequiresExplicitOperatorArm",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision.get(key) is True, f"decision true flag mismatch: {key}", failures)
    for key in FALSE_GUARDS:
        require(decision.get(key) is False, f"decision false flag mismatch: {key}", failures)

    contract = result["realImporterHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationContract"]
    expected_counts = {
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed": EXPECTED_CHECKLIST_ROW_COUNT,
        "commandArmChecklistCommandArmChecklistCommandContractRows": EXPECTED_CHECKLIST_ROW_COUNT,
        "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "armedCommandRowCount": 0,
        "executedCommandRowCount": 0,
        "shellDispatchedCommandRowCount": 0,
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "readyForLaterHarnessArmRowCount": EXPECTED_CHECKLIST_ROW_COUNT,
        "observedChecklistRowCount": 0,
        "rowStatusChangedCount": 0,
        "consumerArchiveTotalCount": 301,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows": 1,
        "publicAllowedOutputCount": len(PUBLIC_ALLOWED_OUTPUTS),
        "redactedFieldCount": len(REDACTED_FIELDS),
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(contract.get(key) == expected, f"contract count mismatch: {key}", failures)

    rows = contract["commandArmChecklistCommandArmChecklistCommandContractRowsBody"]
    require(len(rows) == EXPECTED_CHECKLIST_ROW_COUNT, "command contract row count mismatch", failures)
    require(Counter(row.get("category") for row in rows) == EXPECTED_CATEGORY_COUNTS, "row category count mismatch", failures)
    for expected_ordinal, row in enumerate(rows, start=1):
        require(
            row["commandArmChecklistCommandArmChecklistCommandContractRowOrdinal"] == expected_ordinal,
            "command row order mismatch",
            failures,
        )
        require(
            row["sourceCommandArmChecklistCommandArmChecklistBoundaryRowOrdinal"] == expected_ordinal,
            "source boundary row order mismatch",
            failures,
        )
        require(
            row["commandArmChecklistCommandArmChecklistCommandMaterializationStatus"]
            == "materialized-public-safe-non-armed-command-arm-checklist-command-arm-checklist-command-contract",
            "command materialization status mismatch",
            failures,
        )
        require(row["rowStatus"] == "not-run", "command row status mismatch", failures)
        require(row["observationStatus"] == "unobserved", "command observation mismatch", failures)
        require(row["commandArmStatus"] == "not-armed", "command arm status mismatch", failures)
        require(row["commandExecutionStatus"] == "not-executed", "command execution status mismatch", failures)
        require(row["commandDispatchAllowedHere"] is False, "command dispatch guard mismatch", failures)
        require(row["directCommandArmingAllowedHere"] is False, "command direct-arm guard mismatch", failures)
        require(row["directCommandExecutionAllowedHere"] is False, "command direct-exec guard mismatch", failures)
        require(row["commandRequiresLaterExplicitArm"] is True, "later-arm mismatch", failures)
        require(row["futureCommandArmRequiresExplicitOperatorArm"] is True, "operator-arm mismatch", failures)
        require(row["privateValuePublished"] is False, "private value flag mismatch", failures)
        for key in ROW_ZERO_FIELDS:
            require(row[key] == 0, f"command row zero mismatch: {key}", failures)

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
        NEXT_SLICE,
        NEXT_SCOPE,
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "sourceCommandArmChecklistCommandArmChecklistBoundaryStatus="
        + REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_BOUNDARY_STATUS,
        "sourceProofCount=47",
        "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount=46",
        "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount=10",
        "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount=12",
        "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed=99",
        "commandArmChecklistCommandArmChecklistCommandContractRows=99",
        "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount=99",
        "armedCommandRowCount=0",
        "executedCommandRowCount=0",
        "shellDispatchedCommandRowCount=0",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount=99",
        "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows=1",
        "publicAllowedOutputCount=70",
        "redactedFieldCount=36",
        "falseGuardCount=217",
        "zeroCounterCount=180",
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
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.v1.json",
        REAL_IMPORTER_HARNESS_COMMAND_ARM_CHECKLIST_COMMAND_ARM_CHECKLIST_COMMAND_MATERIALIZATION_STATUS,
        "sourceProofCount=47",
        "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount=46",
        "commandArmChecklistCommandArmChecklistCommandContractRows=99",
        "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount=99",
        "publicAllowedOutputCount=70",
        "redactedFieldCount=36",
        "falseGuardCount=217",
        "zeroCounterCount=180",
        "commandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected=true",
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

    for path in (BACKLOG, LORE_BACKLOG):
        text = read_text(path)
        active = active_slice_block(text)
        require(f"Completed {THIS_SLICE}" in text, f"{path.relative_to(ROOT)} missing completed command materialization slice", failures)
        require(
            f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in active,
            f"{path.relative_to(ROOT)} active slice not moved to command consumer validation",
            failures,
        )
        require(NEXT_SCOPE in active, f"{path.relative_to(ROOT)} active scope not moved to command consumer validation", failures)
        require(
            f"Scope: {THIS_SCOPE}" not in active,
            f"{path.relative_to(ROOT)} still has command materialization scope active",
            failures,
        )
        require(active.count("The selected active static-to-proof slice is ") == 1, "active block should have one active slice sentence", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get(
            "test:texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan"
        )
        == EXPECTED_SCRIPT,
        "missing package command arm-checklist command arm-checklist command-materialization test script",
        failures,
    )
    require(MODULE.is_file(), "missing command-materialization generator module", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        source = check_source_boundary(failures)
        result = check_result_and_mirror(source, failures)
        check_contract(result, failures)
        check_docs_and_package(failures)
        check_no_bad_public_content(RESULT, failures)
    except Exception as exc:  # pragma: no cover - probe output is user-facing.
        failures.append(f"unexpected probe exception: {exc}")

    if failures:
        print("Texture/mesh material sidecar real-importer harness command arm-checklist command arm-checklist command-materialization probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar real-importer harness command arm-checklist command arm-checklist command-materialization probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
