#!/usr/bin/env python3
"""Validate the post-matrix static-to-proof next-safe-slice refresh."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection-refresh.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection-refresh.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection-refresh.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection-refresh.v1.json"
READINESS = ROOT / "release" / "readiness" / "static_to_proof_next_safe_slice_selection_refresh_2026-06-09.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

MATRIX = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-fixture-matrix.v1.json"
FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"
VECTOR_RANGE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json"
ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"

THIS_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan"
PREVIOUS_SLICE = "Save / Options Byte-Preservation AppCore Fixture Matrix Proof"
NEXT_SLICE = "MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan"
NEXT_SCOPE = "missionscript-vector-range-deterministic-helper-fixture-proof-plan"
GOODIE_FIXTURE_SLICE = "MissionScript Goodie State / Save Command-Effect Fixture Proof Plan"
POST_COMMAND_SELECTION_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
PHYSICS_SEMANTIC_SLICE = "PhysicsScript Semantic Value-Field Schema Ledger Proof Plan"
PHYSICS_SCALAR_STRING_SLICE = "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan"
PHYSICS_VALUE_ID_CROSSWALK_SLICE = "PhysicsScript Value-ID Semantic Crosswalk Proof Plan"
PHYSICS_REBUILD_INTERFACE_ROLLUP_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
COMPLETED_GOODIE_CLEAN_ROOM_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof"
COMPLETED_GOODIE_BOUNDARY_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
STATUS_TOKEN = "static-to-proof-next-safe-slice-selection-refresh-complete-vector-range-deterministic-helper-fixture-selected"

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
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeVectorRangeBehaviorProven",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactDatatypeLayoutProven",
    "exactVectorLayoutProven",
    "runtimeSaveLoadProof",
    "runtimeDefaultOptionsProof",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeVectorRangeRows",
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
    "runtime vector behavior proven",
    "runtime range behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact command arity proven",
    "exact argument type schema proven",
    "exact datatype layout proven",
    "exact vector layout proven",
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
    matrix = read_json(MATRIX)
    fixture = read_json(FIXTURE_SELECTION)
    vector = read_json(VECTOR_RANGE)
    rollup = read_json(ROLLUP)

    require(result["schemaVersion"] == "static-to-proof-next-safe-slice-selection-refresh.v1", "schema version mismatch", failures)
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
    require(accounting["completedSlotSaveChainCount"] == 8, "completed slot/save chain count mismatch", failures)
    require(accounting["selectionFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["selectionZeroCounterCount"] == len(ZERO_COUNTS), "zero count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    source = result["sourceEvidence"]
    require(matrix["saveOptionsBytePreservationAppCoreFixtureMatrixStatus"] == source["previousMatrix"]["statusToken"], "matrix status source mismatch", failures)
    require(matrix["matrix"]["fixtureFamilyCount"] == 8, "source matrix fixture family mismatch", failures)
    require(matrix["matrix"]["appCoreFixtureCaseCount"] == 36, "source matrix case count mismatch", failures)
    require(matrix["negativeGuards"]["runtimeExecution"] is False, "source matrix runtime guard mismatch", failures)
    require(matrix["negativeGuards"]["godotWork"] is False, "source matrix Godot guard mismatch", failures)

    require(fixture["selectionAccounting"]["candidateFamilyCount"] == 9, "source fixture candidate count mismatch", failures)
    require(fixture["selectedFixtureFamily"] == "slot-bitset-save", "source fixture selected family mismatch", failures)
    require(source["priorFixtureSelection"]["deferredRankForVectorRange"] == 2, "embedded deferred rank mismatch", failures)
    require(len(source["priorFixtureSelection"]["alreadySelectedFollowThrough"]) == 8, "embedded completed chain list mismatch", failures)

    require(len(vector["descriptorRecords"]) == 9, "source vector descriptor record count mismatch", failures)
    require(len(vector["vectorHandlers"]) == 5, "source vector handler count mismatch", failures)
    require(vector["evidenceCounts"]["wave581InstructionRows"] == 3545, "source vector instruction count mismatch", failures)
    require(vector["evidenceCounts"]["wave581VtableRows"] == 24, "source vector vtable count mismatch", failures)
    require(all(value == 0 for value in vector["looseMslUsage"]["directNonCommentCounts"].values()), "source vector loose-MSL absence mismatch", failures)
    require(vector["datatypeContext"]["floatVtable"] == "0x005e4ea4", "source vector float vtable mismatch", failures)
    require(vector["datatypeContext"]["boolVtable"] == "0x005e4d50", "source vector bool vtable mismatch", failures)
    require(vector["datatypeContext"]["vectorGetterSlot"] == "+0x44", "source vector getter slot mismatch", failures)
    require(vector["datatypeContext"]["floatGetterSlot"] == "+0x34", "source vector float getter slot mismatch", failures)

    require(rollup["rollupAccounting"]["commandFamilyCount"] == 9, "rollup command family count mismatch", failures)
    require(rollup["rollupAccounting"]["descriptorRecordCount"] == 52, "rollup descriptor record count mismatch", failures)
    require(rollup["rollupAccounting"]["uniqueDescriptorTokenCount"] == 48, "rollup unique descriptor token count mismatch", failures)

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
    require("the selected next child lane is a static, public-safe, deterministic MissionScript vector/range helper fixture plan" in result["claimBoundary"]["proves"], "claim boundary missing selected child proof", failures)
    require("runtime MissionScript execution" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime MissionScript execution", failures)
    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after selection-refresh probe", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore proof mirror mismatch", failures)
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "static-to-proof-next-safe-slice-selection-refresh.v1.json",
        f"selectionRefreshStatus={STATUS_TOKEN}",
        "selectedChildLane=MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan",
        "selectedChildScope=missionscript-vector-range-deterministic-helper-fixture-proof-plan",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=4",
        "completedSlotSaveChainCount=8",
        "selectionFalseGuardCount=31",
        "selectionZeroCounterCount=26",
        "publicLeakCheck=PASS",
        "fixtureFamilyCount=8",
        "appCoreFixtureCaseCount=36",
        "descriptorRecordCount=9",
        "vectorHandlerCount=5",
        "wave581InstructionRows=3545",
        "wave581VtableRows=24",
        "directNonCommentLooseMslRows=0",
        "0x005345d0 IScript__GetVectorLength",
        "0x005347b0 IScript__CheckValueInRange",
        "0x00534b80 IScript__GetVectorX",
        "0x00534c10 IScript__GetVectorY",
        "0x00534ca0 IScript__GetVectorZ",
        "vector getter slot `+0x44`",
        "float getter slot `+0x34`",
        "component offsets `+0/+4/+8`",
        "0x005e4ea4",
        "0x005e4d50",
        "runtimeExecution=false",
        "beLaunch=false",
        "screenshotCapture=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "runtimeVectorRangeBehaviorProven=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeVectorRangeRows=0",
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
        "static-to-proof-next-safe-slice-selection-refresh.md",
        "static-to-proof-next-safe-slice-selection-refresh.v1.json",
        STATUS_TOKEN,
        "complete post-matrix next safe slice selection",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=4",
        "completedSlotSaveChainCount=8",
        "selectionFalseGuardCount=31",
        "selectionZeroCounterCount=26",
        "publicLeakCheck=PASS",
        "Save / Options Byte-Preservation AppCore Fixture Matrix Proof",
        "MissionScript Vector/Range Command-Effect Static Proof",
        "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed selection refresh", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks selection refresh active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed vector/range fixture lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks vector/range fixture active", failures)
    require(f"Completed {GOODIE_FIXTURE_SLICE}" in backlog, "backlog missing completed Goodie State / Save fixture lane", failures)
    require(
        f"The selected active static-to-proof slice is {GOODIE_FIXTURE_SLICE}. Status: selected" not in backlog,
        "backlog still marks Goodie State / Save fixture active",
        failures,
    )
    require(
        f"Completed {COMPLETED_GOODIE_CLEAN_ROOM_SLICE}" in backlog,
        "backlog missing completed Goodie State / Save clean-room codec interface lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan. Status: selected" not in backlog,
        "backlog still marks Goodie State / Save clean-room codec interface active",
        failures,
    )
    require(
        f"Completed {COMPLETED_GOODIE_BOUNDARY_SLICE}" in backlog,
        "backlog missing completed Goodie State / Save copied-baseline boundary corpus harness lane",
        failures,
    )
    require(
        f"Completed {POST_GOODIE_SELECTION_SLICE}" in backlog,
        "backlog missing completed post-Goodie selection refresh lane",
        failures,
    )
    require(
        f"Completed {POST_COMMAND_SELECTION_SLICE}" in backlog,
        "backlog missing completed post-command-effect selection refresh lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {POST_COMMAND_SELECTION_SLICE}. Status: selected" not in backlog,
        "backlog still marks post-command-effect selection refresh active",
        failures,
    )
    require(
        f"Completed {PHYSICS_SEMANTIC_SLICE}" in backlog,
        "backlog missing completed PhysicsScript semantic value-field schema ledger lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {PHYSICS_SEMANTIC_SLICE}. Status: selected" not in backlog,
        "backlog still marks PhysicsScript semantic value-field schema ledger lane active",
        failures,
    )
    require(
        f"Completed {PHYSICS_SCALAR_STRING_SLICE}" in backlog,
        "backlog missing completed PhysicsScript scalar/string value decoder fixture lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {PHYSICS_SCALAR_STRING_SLICE}. Status: selected" not in backlog,
        "backlog still marks PhysicsScript scalar/string value decoder fixture lane active",
        failures,
    )
    require(
        f"Completed {PHYSICS_VALUE_ID_CROSSWALK_SLICE}" in backlog,
        "backlog missing completed PhysicsScript value-ID semantic crosswalk lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {PHYSICS_VALUE_ID_CROSSWALK_SLICE}. Status: selected" not in backlog,
        "backlog still marks PhysicsScript value-ID semantic crosswalk lane active",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {PHYSICS_REBUILD_INTERFACE_ROLLUP_SLICE}. Status: selected" in backlog,
        "backlog missing active PhysicsScript rebuild interface rollup lane",
        failures,
    )


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:static-to-proof-next-safe-slice-selection-refresh")
        == r"py -3 tools\static_to_proof_next_safe_slice_selection_refresh_probe.py --check",
        "missing package selection-refresh test script",
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
        print("Static-to-proof next safe slice selection refresh probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static-to-proof next safe slice selection refresh probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
