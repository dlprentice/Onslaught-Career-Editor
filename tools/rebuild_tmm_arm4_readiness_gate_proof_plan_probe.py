#!/usr/bin/env python3
"""Validate the public-safe TMM ARM4 readiness-gate proof-plan slot.

This checker consumes only tracked public-safe files: the Markdown proof plan,
the ARM4 validation proof JSON, and scoped active-slot front-door echoes that
link the plan slot. It does not validate entire historical ledger files for
public safety, discover private corpus paths, read private assets or manifests,
arm commands, dispatch shells, execute importers, launch BEA/CDB/Ghidra, or
write generated payloads.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md"
)
SOURCE_PROOF = (
    ROOT
    / "reverse-engineering"
    / "game-assets"
    / "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json"
)
CHAIN_MAP = ROOT / "roadmap" / "rebuild-front-door-chain-map.md"
STATIC_BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
ROADMAP_INDEX = ROOT / "roadmap" / "ROADMAP-INDEX.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"

ALIAS = "tmm-arm4-readiness-gate"
THIS_SLICE = (
    "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run "
    "Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan"
)
THIS_SCOPE = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan"
)
SOURCE_STATUS_KEY = (
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus"
)
SOURCE_STATUS = (
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-"
    "command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-"
    "validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming"
)
SOURCE_CONTRACT_KEY = (
    "realImporterHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationContract"
)
SOURCE_FILE_NAME = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json"
PLAN_FILE_NAME = "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md"
PREMATURE_RESULT_JSON_FILE_NAMES = (
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.v1.json",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof.v1.json",
)
WRONG_READINESS_GATE_ARTIFACT_FILE_NAMES = (
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-proof.md",
)

EXPECTED_CONTRACT_COUNTS = {
    "commandArmChecklistRowsConsumed": 99,
    "commandArmChecklistValidationRows": 99,
    "passedCommandArmChecklistValidationRowCount": 99,
    "failedCommandArmChecklistValidationRowCount": 0,
    "validatedNotRunCommandArmChecklistRowCount": 99,
    "validatedUnobservedCommandArmChecklistRowCount": 99,
    "validatedNotArmedCommandArmChecklistRowCount": 99,
    "validatedNotExecutedCommandArmChecklistRowCount": 99,
    "armedCommandRowCount": 0,
    "executedCommandRowCount": 0,
    "shellDispatchedCommandRowCount": 0,
    "consumerArchiveTotalCount": 301,
    "unknownAyaArchiveClassCount": 0,
}

EXPECTED_GUARDS = {
    "realImporterExecuted": False,
    "beLaunch": False,
    "ghidraMutation": False,
    "godotWork": False,
    "actualAssetImportRows": 0,
    "generatedAssetRows": 0,
    "rawPathRows": 0,
    "rawFilenameRows": 0,
    "rawHashRows": 0,
    "byteLengthRows": 0,
    "rawCommandArgumentRows": 0,
    "publishedCommandArgumentRows": 0,
    "rawCommandDryRunTraceRows": 0,
    "privateAssetContentRead": False,
    "privateArchiveBytesRead": False,
    "rawPrivateManifestConsumed": False,
    "rawPrivateManifestRows": 0,
    "commandExecutionRows": 0,
    "commandShellDispatchRows": 0,
    "outputArtifactRows": 0,
}

REQUIRED_PLAN_TOKENS = (
    ALIAS,
    THIS_SLICE,
    THIS_SCOPE,
    SOURCE_FILE_NAME,
    SOURCE_STATUS,
    "`selectedNextScope`",
    "`commandArmChecklistRowsConsumed`",
    "`commandArmChecklistValidationRows`",
    "`passedCommandArmChecklistValidationRowCount`",
    "`failedCommandArmChecklistValidationRowCount`",
    "`validatedNotRunCommandArmChecklistRowCount`",
    "`validatedUnobservedCommandArmChecklistRowCount`",
    "`validatedNotArmedCommandArmChecklistRowCount`",
    "`validatedNotExecutedCommandArmChecklistRowCount`",
    "`armedCommandRowCount`",
    "`executedCommandRowCount`",
    "`shellDispatchedCommandRowCount`",
    "`consumerArchiveTotalCount`",
    "`unknownAyaArchiveClassCount`",
    "`publicLeakCheck`",
    "`realImporterExecuted`",
    "`actualAssetImportRows`",
    "`generatedAssetRows`",
    "`rawPathRows`",
    "`rawFilenameRows`",
    "`rawHashRows`",
    "`byteLengthRows`",
    "`rawCommandArgumentRows`",
    "`publishedCommandArgumentRows`",
    "`rawCommandDryRunTraceRows`",
    "no private asset reads",
    "no raw private manifest reads",
    "no command arming",
    "no shell dispatch",
    "no command execution",
    "no importer execution",
    "no generated payloads",
    "no BEA launch",
    "no CDB",
    "no Ghidra mutation or read-back",
    "no installed game mutation",
    "no original BEA.exe mutation",
    "no runtime proof",
    "no runtime parity",
    "no visual parity",
    "no gameplay proof",
    "no rebuild parity",
    "no no-noticeable-difference parity",
    "does not complete a readiness-gate proof",
)

ACTIVE_SLOT_TOKENS = (
    ALIAS,
    THIS_SLICE,
    THIS_SCOPE,
    PLAN_FILE_NAME,
    SOURCE_FILE_NAME,
    "proof-plan",
    "continuity",
    "not readiness-gate execution",
    "no runtime proof",
    "no rebuild parity",
    "no no-noticeable-difference",
)

GAME_ASSETS_SLOT_TOKENS = (
    ALIAS,
    THIS_SLICE,
    PLAN_FILE_NAME,
    "proof-plan slot",
    "continuity guard only",
    "not readiness-gate execution",
    "no runtime proof",
    "no rebuild parity",
    "no no-noticeable-difference",
    "commandArmChecklistRowsConsumed=99",
    "armedCommandRowCount=0",
    "executedCommandRowCount=0",
    "shellDispatchedCommandRowCount=0",
)

ROUTING_INDEX_TOKENS = (
    "rebuild-front-door-chain-map.md",
    "static-to-proof-rebuild-transition-backlog.md",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{40}\b"), "raw digest-like value"),
    (re.compile(r"(?i)/(?:home|mnt|var|opt|tmp|users?)/"), "machine-local absolute path"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-)?game[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-)?media[\\/]"), "private media path"),
    (re.compile(r"(?i)\.(?:bes|aya|bea|wav|dds)\b"), "private payload-like file extension"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framebytelength"), "private frame locator field"),
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
    "readiness gate executed",
    "readiness-gate executed",
    "readiness-gate complete",
    "readinessgateexecuted=true",
    "complete public-safe readiness gate",
    "cleared to arm",
    "ready for execution",
    "import-ready",
    "asset import complete",
    "private asset import complete",
    "generated asset output complete",
    "runtime texture pixels proven",
    "runtime mesh loading proven",
    "runtime direct3d upload proven",
    "runtime proof complete",
    "runtime proof achieved",
    "material visual correctness proven",
    "asset format completeness proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild implementation complete",
    "rebuild parity proven",
    "rebuild parity is proven",
    "rebuild parity achieved",
    "no-noticeable-difference parity proven",
    "no-noticeable-difference parity achieved",
    "complete public-safe command-readiness gate",
    "complete public-safe command arm-checklist",
)

FORBIDDEN_OVERCLAIM_PATTERNS = (
    (re.compile(r"(?<!not a )\bcompleted readiness-gate proof\b", re.I), "completed readiness-gate proof claim"),
    (re.compile(r"\breadiness-gate proof complete\b", re.I), "completed readiness-gate proof claim"),
    (re.compile(r"\brebuild proof (?:complete|proven|achieved)\b", re.I), "rebuild proof claim"),
    (re.compile(r"\bruntime proof (?:complete|proven|achieved)\b", re.I), "runtime proof claim"),
)


class ReadinessPlanProbeError(ValueError):
    """Raised when the readiness-gate proof-plan slot is not public-safe."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise ReadinessPlanProbeError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ReadinessPlanProbeError(f"invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReadinessPlanProbeError(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessPlanProbeError(message)


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    require(isinstance(value, Mapping), f"{label} must be an object")
    return value


def check_forbidden_text(text: str, label: str) -> None:
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{label} leaks forbidden public category: {category}")
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{label} contains forbidden overclaim phrase: {phrase}")
    for pattern, category in FORBIDDEN_OVERCLAIM_PATTERNS:
        require(pattern.search(text) is None, f"{label} contains forbidden overclaim pattern: {category}")


def check_continuity_block(text: str, label: str, required_tokens: tuple[str, ...]) -> None:
    """Validate one active front-door continuity block."""
    require(text.strip() != "", f"{label} active block is empty")
    for token in required_tokens:
        require(token in text, f"{label} missing required token: {token}")
    for artifact_name in WRONG_READINESS_GATE_ARTIFACT_FILE_NAMES:
        require(artifact_name not in text, f"{label} promotes wrong readiness-gate artifact: {artifact_name}")
    for result_json_name in PREMATURE_RESULT_JSON_FILE_NAMES:
        require(result_json_name not in text, f"{label} references premature readiness-gate result JSON: {result_json_name}")
    require("proof file is not materialized yet" not in text, f"{label} still says proof file is not materialized")
    check_forbidden_text(text, label)


def section_after_heading(text: str, heading: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    require(match is not None, f"{label} missing heading: {heading}")
    tail_start = match.end()
    next_heading = re.search(r"(?m)^##\s+", text[tail_start:])
    tail_end = tail_start + next_heading.start() if next_heading else len(text)
    section = text[tail_start:tail_end].strip()
    require(section != "", f"{label} section is empty after {heading}")
    return section


def first_paragraph_after_heading(text: str, heading: str, label: str) -> str:
    section = section_after_heading(text, heading, label)
    match = re.match(r"(.+?)(?:\n\s*\n|$)", section, re.S)
    require(match is not None, f"{label} missing first paragraph after {heading}")
    return match.group(1)


def first_paragraph_with_token(text: str, token: str, label: str) -> str:
    for paragraph in re.split(r"\n\s*\n", text):
        if token in paragraph:
            return paragraph
    raise ReadinessPlanProbeError(f"{label} missing paragraph containing token: {token}")


def require_plan_link(block: str, base_path: Path, label: str) -> None:
    links = re.findall(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)", block)
    normalized_links = [(link, link.split("#", 1)[0]) for link in links]
    matching_links = [link for link, clean_link in normalized_links if Path(clean_link).name == PLAN_FILE_NAME]
    require(matching_links, f"{label} missing Markdown link to {PLAN_FILE_NAME}")
    for link, clean_link in normalized_links:
        name = Path(clean_link).name
        if "readiness-gate" in name and name.endswith(".md"):
            require(name == PLAN_FILE_NAME, f"{label} links wrong readiness-gate artifact: {link}")
    for link in matching_links:
        clean_link = link.split("#", 1)[0]
        target = (base_path.parent / clean_link).resolve()
        require(target == PLAN.resolve(), f"{label} plan link resolves to wrong target: {link}")


def check_source_proof(source: Mapping[str, Any]) -> None:
    check_forbidden_text(read_text(SOURCE_PROOF), str(SOURCE_PROOF.relative_to(ROOT)))
    require(
        source.get("schemaVersion")
        == "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1",
        "source schema mismatch",
    )
    require(source.get("status") == "PASS", "source status mismatch")
    require(source.get(SOURCE_STATUS_KEY) == SOURCE_STATUS, "source validation status mismatch")
    require(source.get("selectedNextSlice") == THIS_SLICE, "source selectedNextSlice mismatch")
    require(source.get("selectedNextScope") == THIS_SCOPE, "source selectedNextScope mismatch")

    contract = require_mapping(source.get(SOURCE_CONTRACT_KEY), SOURCE_CONTRACT_KEY)
    for key, expected in EXPECTED_CONTRACT_COUNTS.items():
        require(contract.get(key) == expected, f"source contract mismatch: {key}")

    rows = contract.get("commandArmChecklistValidationRowsBody")
    require(isinstance(rows, list), "source validation rows must be a list")
    require(len(rows) == 99, "source validation row count mismatch")
    for index, row_value in enumerate(rows, start=1):
        row = require_mapping(row_value, f"source validation row {index}")
        require(row.get("commandArmChecklistValidationRowOrdinal") == index, f"row {index} ordinal mismatch")
        require(row.get("rowStatus") == "not-run", f"row {index} rowStatus mismatch")
        require(row.get("observationStatus") == "unobserved", f"row {index} observation mismatch")
        require(row.get("commandArmStatus") == "not-armed", f"row {index} arm status mismatch")
        require(row.get("commandExecutionStatus") == "not-executed", f"row {index} execution status mismatch")
        require(row.get("commandDispatchAllowedHere") is False, f"row {index} dispatch guard mismatch")
        require(row.get("directCommandArmingAllowedHere") is False, f"row {index} direct arm guard mismatch")
        require(row.get("directCommandExecutionAllowedHere") is False, f"row {index} direct execution guard mismatch")
        require(row.get("privateValuePublished") is False, f"row {index} private value guard mismatch")

    guard = require_mapping(source.get("guardSummary"), "guardSummary")
    require(guard.get("publicLeakCheck") == "PASS", "source public leak check mismatch")
    for key, expected in EXPECTED_GUARDS.items():
        require(guard.get(key) == expected, f"source guard mismatch: {key}")


def check_plan_text(plan_text: str, source: Mapping[str, Any]) -> None:
    check_forbidden_text(plan_text, PLAN_FILE_NAME)
    for token in REQUIRED_PLAN_TOKENS:
        require(token in plan_text, f"plan missing required token: {token}")

    for key, expected in EXPECTED_CONTRACT_COUNTS.items():
        require(f"| `{key}` | `{expected}` |" in plan_text, f"plan missing source counter row: {key}")

    guard_table_checks = {
        "publicLeakCheck": "PASS",
        "realImporterExecuted": "false",
        "actualAssetImportRows": "0",
        "generatedAssetRows": "0",
        "rawPathRows": "0",
        "rawFilenameRows": "0",
        "rawHashRows": "0",
        "byteLengthRows": "0",
        "rawCommandArgumentRows": "0",
        "publishedCommandArgumentRows": "0",
        "rawCommandDryRunTraceRows": "0",
    }
    for key, expected in guard_table_checks.items():
        require(f"| `{key}` | `{expected}` |" in plan_text, f"plan missing guard row: {key}")

    require(
        f"| `{SOURCE_STATUS_KEY}` | `{source.get(SOURCE_STATUS_KEY)}` |" in plan_text,
        "plan missing source validation status row",
    )
    require(
        f"| `selectedNextScope` | `{source.get('selectedNextScope')}` |" in plan_text,
        "plan missing selectedNextScope row",
    )


def check_front_door_docs() -> None:
    chain = read_text(CHAIN_MAP)
    backlog = read_text(STATIC_BACKLOG)
    roadmap_index = read_text(ROADMAP_INDEX)
    re_index = read_text(RE_INDEX)
    index = read_text(GAME_ASSETS_INDEX)

    chain_block = section_after_heading(
        chain,
        "## Current Active Scope",
        str(CHAIN_MAP.relative_to(ROOT)),
    )
    check_continuity_block(chain_block, str(CHAIN_MAP.relative_to(ROOT)), ACTIVE_SLOT_TOKENS)
    require_plan_link(chain_block, CHAIN_MAP, str(CHAIN_MAP.relative_to(ROOT)))

    backlog_active = first_paragraph_after_heading(
        backlog,
        "## Active Proof Slice",
        str(STATIC_BACKLOG.relative_to(ROOT)),
    )
    require(
        backlog.count("The selected active static-to-proof slice is ") == 1,
        "static backlog must have exactly one selected active static-to-proof slice paragraph",
    )
    check_continuity_block(backlog_active, str(STATIC_BACKLOG.relative_to(ROOT)), ACTIVE_SLOT_TOKENS)
    require_plan_link(backlog_active, STATIC_BACKLOG, str(STATIC_BACKLOG.relative_to(ROOT)))

    re_index_block = first_paragraph_with_token(re_index, ALIAS, str(RE_INDEX.relative_to(ROOT)))
    check_continuity_block(re_index_block, str(RE_INDEX.relative_to(ROOT)), ACTIVE_SLOT_TOKENS)
    require_plan_link(re_index_block, RE_INDEX, str(RE_INDEX.relative_to(ROOT)))

    game_assets_block = first_paragraph_with_token(index, ALIAS, str(GAME_ASSETS_INDEX.relative_to(ROOT)))
    check_continuity_block(game_assets_block, str(GAME_ASSETS_INDEX.relative_to(ROOT)), GAME_ASSETS_SLOT_TOKENS)
    require_plan_link(game_assets_block, GAME_ASSETS_INDEX, str(GAME_ASSETS_INDEX.relative_to(ROOT)))

    for token in ROUTING_INDEX_TOKENS:
        require(token in roadmap_index, f"{ROADMAP_INDEX.relative_to(ROOT)} missing routing token: {token}")


def run_check() -> None:
    source = read_json(SOURCE_PROOF)
    check_source_proof(source)
    check_plan_text(read_text(PLAN), source)
    check_front_door_docs()


def run_self_test() -> None:
    check_forbidden_text("This has no command arming and no rebuild parity.", "self-test clean")
    check_forbidden_text("This does not complete a readiness-gate proof.", "self-test negative readiness-gate proof wording")
    try:
        check_forbidden_text(r"C:\\Users\\example\\secret", "self-test path")
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch absolute path")

    try:
        check_forbidden_text("rebuild parity proven", "self-test overclaim")
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch overclaim")

    check_forbidden_text("installed-game/original-executable mutation remains a non-claim.", "self-test hyphenated boundary")

    for bad_text, label in (
        ("game/BEA.exe", "self-test game mirror path"),
        ("local-game/BEA.exe", "self-test local game mirror path"),
        ("media/private.wav", "self-test media path"),
        ("local-media/private.wav", "self-test local media path"),
        ("a" * 64, "self-test raw digest"),
        ("a" * 40, "self-test sha1-like digest"),
        ("/home/user/private/file.txt", "self-test unix path"),
        ("asset.aya", "self-test payload extension"),
        ("runtime proof complete", "self-test runtime overclaim"),
        ("readiness-gate proof complete", "self-test readiness proof complete overclaim"),
        ("completed readiness-gate proof", "self-test completed readiness proof overclaim"),
        ("rebuild proof proven", "self-test rebuild proof overclaim"),
        ("rebuild parity achieved", "self-test parity overclaim"),
    ):
        try:
            check_forbidden_text(bad_text, label)
        except ReadinessPlanProbeError:
            pass
        else:
            raise ReadinessPlanProbeError(f"self-test failed to catch {label}")

    try:
        for token in REQUIRED_PLAN_TOKENS:
            require(token in "not enough context", f"plan missing required token: {token}")
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch missing token")

    try:
        check_continuity_block("Status: public-safe proof-plan slot only.", "self-test missing alias", (ALIAS,))
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch missing active alias")

    try:
        check_continuity_block(
            f"{ALIAS} {PLAN_FILE_NAME} {THIS_SCOPE} complete public-safe readiness gate",
            "self-test scoped overclaim",
            (ALIAS, PLAN_FILE_NAME, THIS_SCOPE),
        )
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch scoped overclaim")

    good_block = (
        f"{ALIAS} {THIS_SLICE} {THIS_SCOPE} {PLAN_FILE_NAME} {SOURCE_FILE_NAME} "
        "proof-plan continuity guard only; not readiness-gate execution; "
        "no runtime proof; no rebuild parity; no no-noticeable-difference parity."
    )
    check_continuity_block(good_block, "self-test good active block", ACTIVE_SLOT_TOKENS)

    try:
        check_continuity_block(
            f"{ALIAS} {THIS_SLICE} {THIS_SCOPE} {PLAN_FILE_NAME} {SOURCE_FILE_NAME} "
            "proof-plan continuity guard only; not readiness-gate execution; "
            "no runtime proof; rebuild parity achieved; no no-noticeable-difference parity.",
            "self-test positive parity",
            ACTIVE_SLOT_TOKENS,
        )
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch positive parity overclaim")

    try:
        check_continuity_block(
            f"{good_block} {WRONG_READINESS_GATE_ARTIFACT_FILE_NAMES[0]}",
            "self-test wrong readiness artifact",
            ACTIVE_SLOT_TOKENS,
        )
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch wrong readiness artifact")

    try:
        check_continuity_block(
            f"{good_block} {PREMATURE_RESULT_JSON_FILE_NAMES[1]}",
            "self-test premature result JSON",
            ACTIVE_SLOT_TOKENS,
        )
    except ReadinessPlanProbeError:
        pass
    else:
        raise ReadinessPlanProbeError("self-test failed to catch premature result JSON")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked readiness-gate proof-plan slot")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except ReadinessPlanProbeError as exc:
        print("TMM ARM4 readiness-gate proof-plan continuity probe: FAIL")
        print(f"- {exc}")
        return 1

    print("TMM ARM4 readiness-gate proof-plan continuity probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
