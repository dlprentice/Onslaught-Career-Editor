#!/usr/bin/env python3
"""Validate the post-command-effect static-to-proof next-safe-slice refresh."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.v1.json"
READINESS = ROOT / "release" / "readiness" / "static_to_proof_post_command_effect_fixture_next_safe_slice_selection_refresh_2026-06-10.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
LORE_PHYSICS_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1.json"
PHYSICS_PARSER = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"

THIS_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
PREVIOUS_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
NEXT_SLICE = "PhysicsScript Semantic Value-Field Schema Ledger Proof Plan"
NEXT_SCOPE = "physics-script-semantic-value-field-schema-ledger-proof-plan"
COMPLETED_SCALAR_STRING_SLICE = "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan"
COMPLETED_VALUE_ID_CROSSWALK_SLICE = "PhysicsScript Value-ID Semantic Crosswalk Proof Plan"
CURRENT_ACTIVE_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
STATUS_TOKEN = "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh-complete-physics-script-semantic-value-field-schema-ledger-selected"

FALSE_GUARDS = (
    "runtimeExecution",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "sourceSelectionObserved",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "runtimeSaveLoadProof",
    "runtimeDefaultOptionsProof",
    "runtimeVectorRangeBehaviorProven",
    "runtimeObjectIdentityProven",
    "runtimeWorldLoadingProven",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimePhysicsScriptRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "productUiRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterSelection",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime physicsscript behavior proven",
    "runtime physics outcomes proven",
    "serialized physics-script format completeness proven",
    "exact statement/value-list/concrete record layouts proven",
    "source-selection observation complete",
    "private-frame review complete",
    "visual qa complete",
    "godot parity proven",
    "ghidra mutation complete",
    "executable patching behavior proven",
    "product ui behavior proven",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    rollup = read_json(ROLLUP)
    parser_text = read_text(PHYSICS_PARSER)
    contract_text = read_text(PHYSICS_CONTRACT)

    require(result["schemaVersion"] == "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["selectionRefreshStatus"] == STATUS_TOKEN, "selection status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedChildScope"] == NEXT_SCOPE, "selected child scope mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk focused mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active focused work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["selectionAccounting"]
    require(accounting["consultCount"] == 2, "consult count mismatch", failures)
    require(accounting["candidateCount"] == 4, "candidate count mismatch", failures)
    require(accounting["selectedCandidateRank"] == 1, "selected candidate rank mismatch", failures)
    require(accounting["selectedSourceProofCount"] == 4, "selected source proof count mismatch", failures)
    require(accounting["completedMissionScriptFixtureFamilyCount"] == 9, "completed MissionScript family count mismatch", failures)
    require(accounting["remainingMissionScriptFixtureFamilyCount"] == 0, "remaining MissionScript family count mismatch", failures)
    require(accounting["duplicateDescriptorBoundaryCount"] == 4, "duplicate descriptor boundary count mismatch", failures)
    require(accounting["heterogeneousFixtureCaseCount"] == 114, "heterogeneous fixture case count mismatch", failures)
    require(accounting["selectionFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["selectionZeroCounterCount"] == len(ZERO_COUNTS), "zero count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    source = result["sourceEvidence"]
    require(rollup["missionScriptCommandEffectFixtureFamilyCompletionRollupProofPlanStatus"] == source["missionScriptCommandEffectCompletionRollup"]["statusToken"], "rollup status source mismatch", failures)
    require(rollup["fixtureCompletionAccounting"]["expectedFixtureFamilyCount"] == 9, "rollup expected family count mismatch", failures)
    require(rollup["fixtureCompletionAccounting"]["completedFixtureFamilyCount"] == 9, "rollup completed family count mismatch", failures)
    require(rollup["fixtureCompletionAccounting"]["remainingFixtureFamilyCount"] == 0, "rollup remaining family count mismatch", failures)
    require(rollup["fixtureCompletionAccounting"]["heterogeneousFixtureCaseCount"] == 114, "rollup heterogeneous case count mismatch", failures)
    require(rollup["descriptorIndexAccounting"]["descriptorRecordCount"] == 52, "rollup descriptor count mismatch", failures)
    require(rollup["descriptorIndexAccounting"]["uniqueDescriptorIndexCount"] == 48, "rollup unique descriptor count mismatch", failures)
    require(rollup["descriptorIndexAccounting"]["duplicateDescriptorIndexCount"] == 4, "rollup duplicate index count mismatch", failures)
    require(rollup["descriptorIndexAccounting"]["duplicateDescriptorBoundaryCount"] == 4, "rollup duplicate boundary count mismatch", failures)
    require(rollup["staticToProofBacklogAccounting"]["selectedNextSlice"] == THIS_SLICE, "rollup selected next slice mismatch", failures)
    require(rollup["guardSummary"]["falseGuards"]["runtimeExecution"] is False, "rollup runtime guard mismatch", failures)
    require(rollup["guardSummary"]["falseGuards"]["godotWork"] is False, "rollup Godot guard mismatch", failures)
    require(rollup["guardSummary"]["falseGuards"]["rebuildImplementation"] is False, "rollup rebuild guard mismatch", failures)

    physics = source["physicsScriptCopiedCorpusParser"]
    require(physics["byteCount"] == 175603, "PhysicsScript byte count mismatch", failures)
    require(physics["streamHeader"] == "0x12", "PhysicsScript stream header mismatch", failures)
    require(physics["topLevelStatementCount"] == 777, "PhysicsScript top-level statement count mismatch", failures)
    require(physics["valueListNodeCount"] == 6803, "PhysicsScript value-list node count mismatch", failures)
    require(physics["statementValuePairCount"] == 185, "PhysicsScript statement/value pair count mismatch", failures)
    require(physics["rawValuePayloadBytesPreserved"] == 73796, "PhysicsScript raw payload byte count mismatch", failures)
    require(physics["unknownTopLevelIdCount"] == 0, "PhysicsScript unknown top-level id count mismatch", failures)
    for token in (
        "Parsed byte count | `175603`",
        "Stream header | `0x12`",
        "Top-level statements | `777`",
        "Value-list nodes | `6803`",
        "Unique statement/value id pairs | `185`",
        "Raw value payload bytes preserved | `73796`",
        "Unknown top-level ids | `0`",
        "semantic schema ledger for selected high-confidence value families",
    ):
        require(token in parser_text, f"PhysicsScript parser proof missing token: {token}", failures)

    for token in (
        "CPhysicsScript__Load",
        "CPhysicsScript__CreateStatement",
        "CPhysicsScriptStatements__CreateStatementType2",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CPhysicsScriptStatement__dtor",
        "Runtime PhysicsScript behavior.",
        "Serialized physics-script file-format completeness.",
        "Exact statement/value-list/concrete record layouts.",
    ):
        require(token in contract_text, f"PhysicsScript static contract missing token: {token}", failures)

    ranks = result["candidateRanking"]
    require(len(ranks) == 4, "candidate ranking length mismatch", failures)
    require(ranks[0]["rank"] == 1 and ranks[0]["decision"] == "selected", "selected rank mismatch", failures)
    require(ranks[0]["lane"] == NEXT_SLICE, "selected lane row mismatch", failures)

    guard = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard["zeroCounters"][key] == 0, f"guard count must be zero: {key}", failures)

    require(len(result["futureEvidenceRequirements"]) == 5, "future requirement count mismatch", failures)
    require(len(result["stopConditions"]) == 5, "stop condition count mismatch", failures)
    require("the selected next child lane is a static, public-safe PhysicsScript semantic value-field schema ledger plan" in result["claimBoundary"]["proves"], "claim boundary missing selected child proof", failures)
    require("runtime PhysicsScript behavior" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime PhysicsScript behavior", failures)
    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)
    require(no_bea_process_running(), "BEA process still running after selection-refresh probe", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore proof mirror mismatch", failures)
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.v1.json",
        f"selectionRefreshStatus={STATUS_TOKEN}",
        "selectedChildLane=PhysicsScript Semantic Value-Field Schema Ledger Proof Plan",
        "selectedChildScope=physics-script-semantic-value-field-schema-ledger-proof-plan",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=4",
        "completedMissionScriptFixtureFamilyCount=9",
        "remainingMissionScriptFixtureFamilyCount=0",
        "duplicateDescriptorBoundaryCount=4",
        "heterogeneousFixtureCaseCount=114",
        "selectionFalseGuardCount=33",
        "selectionZeroCounterCount=27",
        "publicLeakCheck=PASS",
        "physicsScriptCorpusByteCount=175603",
        "physicsScriptStreamHeader=0x12",
        "physicsScriptTopLevelStatementCount=777",
        "physicsScriptValueListNodeCount=6803",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
        "physicsScriptUnknownTopLevelIdCount=0",
        "CPhysicsScript__Load",
        "CPhysicsScript__CreateStatement",
        "CPhysicsScriptStatements__CreateStatementType2",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CPhysicsScriptStatement__dtor",
        "runtimeExecution=false",
        "beLaunch=false",
        "screenshotCapture=false",
        "sourceSelectionProven=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "runtimePhysicsScriptBehaviorProven=false",
        "serializedPhysicsScriptCompletenessProven=false",
        "exactPhysicsScriptLayoutProven=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "physicsScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimePhysicsScriptRows=0",
        "beProcessesAfterSelection=0",
        "latestGhidraBackupClass=verified-static-backup-redacted",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.md",
        "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.v1.json",
        STATUS_TOKEN,
        "complete post-command-effect fixture next safe slice selection",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=4",
        "completedMissionScriptFixtureFamilyCount=9",
        "remainingMissionScriptFixtureFamilyCount=0",
        "selectionFalseGuardCount=33",
        "selectionZeroCounterCount=27",
        "publicLeakCheck=PASS",
        "PhysicsScript Copied-Corpus Parser Proof",
        "PhysicsScript Static Contract",
        "physicsScriptTopLevelStatementCount=777",
        "physicsScriptValueListNodeCount=6803",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, MISSIONSCRIPT_CONTRACT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (PHYSICS_CONTRACT, LORE_PHYSICS_CONTRACT),
        (MISSIONSCRIPT_CONTRACT, LORE_MISSIONSCRIPT_CONTRACT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed post-command-effect selection refresh", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks post-command-effect selection refresh active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed PhysicsScript semantic value-field schema ledger lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript semantic value-field schema ledger active", failures)
    require(f"Completed {COMPLETED_SCALAR_STRING_SLICE}" in backlog, "backlog missing completed PhysicsScript scalar/string value decoder fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_SCALAR_STRING_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript scalar/string value decoder fixture lane active", failures)
    require(f"Completed {COMPLETED_VALUE_ID_CROSSWALK_SLICE}" in backlog, "backlog missing completed PhysicsScript value-ID semantic crosswalk lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_VALUE_ID_CROSSWALK_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript value-ID semantic crosswalk lane active", failures)
    require(f"The selected active static-to-proof slice is {CURRENT_ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript rebuild interface rollup lane", failures)
    require("runtimeExecution=false" in backlog, "backlog missing runtime execution guard", failures)
    require("godotWork=false" in backlog, "backlog missing Godot guard", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh")
        == r"py -3 tools\static_to_proof_post_command_effect_fixture_next_safe_slice_selection_refresh_probe.py --check",
        "missing package post-command-effect selection-refresh test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("Static-to-proof post-command-effect fixture next safe slice selection refresh probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static-to-proof post-command-effect fixture next safe slice selection refresh probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
