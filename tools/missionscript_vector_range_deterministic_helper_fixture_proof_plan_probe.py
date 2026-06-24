#!/usr/bin/env python3
"""Validate MissionScript vector/range deterministic helper fixture proof-plan artifacts."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_vector_range_deterministic_helper_fixture_proof_plan_2026-06-09.md"

SELECTION_REFRESH = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection-refresh.v1.json"
VECTOR_RANGE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json"
ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
ISCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_ISCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan"
PREVIOUS_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan"
NEXT_SLICE = "MissionScript Goodie State / Save Command-Effect Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
COMPLETED_GOODIE_CLEAN_ROOM_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof"
COMPLETED_GOODIE_BOUNDARY_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-vector-range-deterministic-helper-fixture-proof-plan-complete-pure-helper-fixture-not-runtime-proof"
REFRESH_STATUS = "static-to-proof-next-safe-slice-selection-refresh-complete-vector-range-deterministic-helper-fixture-selected"

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "originalExecutableMutation",
    "copiedFileMutation",
    "sourceBaselineRead",
    "privateArtifactMaterialized",
    "saveSynthesis",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeVectorRangeBehaviorProven",
    "runtimeVectorBehaviorProven",
    "runtimeRangeBehaviorProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "rebuildImplementation",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactDatatypeLayoutProven",
    "exactVectorLayoutProven",
    "exactHelperAbiProven",
    "nanInfinityBehaviorProven",
    "signedZeroBehaviorProven",
    "subnormalBehaviorProven",
    "overflowBehaviorProven",
    "exactX87OrCrtRoundingParityProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeVectorRangeRows",
    "runtimeVectorRows",
    "runtimeRangeRows",
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
    "copiedFileMutationRows",
    "sourceBaselineReadRows",
    "privateArtifactRows",
    "rebuildImplementationRows",
    "godotProjectRows",
    "beProcessesAfterFixture",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

VECTOR_HANDLERS = (
    "0x005345d0 IScript__GetVectorLength",
    "0x005347b0 IScript__CheckValueInRange",
    "0x00534b80 IScript__GetVectorX",
    "0x00534c10 IScript__GetVectorY",
    "0x00534ca0 IScript__GetVectorZ",
)

DESCRIPTOR_INDICES = (56, 57, 58, 59, 60, 61, 104, 105, 108)

DESCRIPTOR_ROWS = (
    "0x0064dc50",
    "0x0064dc90",
    "0x0064dcd0",
    "0x0064dd10",
    "0x0064dd50",
    "0x0064dd90",
    "0x0064e850",
    "0x0064e890",
    "0x0064e950",
)

VECTOR_FIXTURES = (
    ("zero-vector", [0.0, 0.0, 0.0]),
    ("three-four-zero", [3.0, 4.0, 0.0]),
    ("two-three-six", [2.0, 3.0, 6.0]),
    ("negative-three-four-twelve", [-3.0, -4.0, -12.0]),
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime vector/range behavior proven",
    "runtime vector behavior proven",
    "runtime range behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact datatype layout proven",
    "exact vector layout proven",
    "nan/infinity behavior proven",
    "signed-zero behavior proven",
    "subnormal behavior proven",
    "overflow behavior proven",
    "allocator failure behavior proven",
    "exact x87/crt rounding parity proven",
    "exact result-object layout proven",
    "exact source identity proven",
    "private-frame review complete",
    "source-selection observation complete",
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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


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


def vector_length(vector: list[float]) -> float:
    return math.sqrt(sum(component * component for component in vector))


def range_check(value: float, bound_a: float, bound_b: float) -> bool:
    return (bound_a <= value <= bound_b) or (bound_b <= value <= bound_a)


def finite_case_values(values: list[float]) -> bool:
    return all(math.isfinite(value) for value in values)


def length_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": case_id,
            "handler": "IScript__GetVectorLength",
            "vector": vector,
            "expected": vector_length(vector),
            "formula": "sqrt(x*x+y*y+z*z)",
            "finiteOnly": finite_case_values(vector),
        }
        for case_id, vector in VECTOR_FIXTURES
    ]


def component_cases() -> list[dict[str, Any]]:
    components = [("x", "+0", 0), ("y", "+4", 1), ("z", "+8", 2)]
    return [
        {
            "id": f"{case_id}-component-{axis}",
            "handler": f"IScript__GetVector{axis.upper()}",
            "vector": vector,
            "component": axis,
            "componentOffset": offset,
            "expected": vector[index],
            "finiteOnly": finite_case_values(vector),
        }
        for case_id, vector in VECTOR_FIXTURES
        for axis, offset, index in components
    ]


def range_cases() -> list[dict[str, Any]]:
    raw_cases = [
        ("ascending-middle", 5.0, 1.0, 10.0),
        ("ascending-low-bound", 1.0, 1.0, 10.0),
        ("ascending-high-bound", 10.0, 1.0, 10.0),
        ("ascending-below", 0.0, 1.0, 10.0),
        ("ascending-above", 11.0, 1.0, 10.0),
        ("descending-middle", 5.0, 10.0, 1.0),
        ("descending-low-bound", 1.0, 10.0, 1.0),
        ("descending-high-bound", 10.0, 10.0, 1.0),
        ("descending-below", 0.0, 10.0, 1.0),
        ("descending-above", 11.0, 10.0, 1.0),
        ("equal-bound", 3.0, 3.0, 3.0),
        ("equal-bound-outside", 2.0, 3.0, 3.0),
    ]
    return [
        {
            "id": case_id,
            "handler": "IScript__CheckValueInRange",
            "value": value,
            "boundA": bound_a,
            "boundB": bound_b,
            "expected": range_check(value, bound_a, bound_b),
            "comparison": "(a <= value <= b) or (b <= value <= a)",
            "finiteOnly": finite_case_values([value, bound_a, bound_b]),
        }
        for case_id, value, bound_a, bound_b in raw_cases
    ]


def build_schema() -> dict[str, Any]:
    selection = read_json(SELECTION_REFRESH)
    vector = read_json(VECTOR_RANGE_SCHEMA)
    rollup = read_json(ROLLUP)
    fixture = read_json(FIXTURE_SELECTION)

    length = length_cases()
    components = component_cases()
    ranges = range_cases()
    vector_assertion_count = len(length) + len(components)
    deterministic_case_count = vector_assertion_count + len(ranges)
    return {
        "schemaVersion": "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1",
        "status": "PASS",
        "missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus": STATUS_TOKEN,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "vector-range-helpers",
        "selectedFixturePath": "vector-range-finite-helper-math",
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "fixtureAccounting": {
            "sourceProofCount": 4,
            "helperFamilyCount": 3,
            "descriptorIndices": list(DESCRIPTOR_INDICES),
            "descriptorRecordCount": len(vector["descriptorRecords"]),
            "handlerAnchorCount": len(vector["vectorHandlers"]),
            "vectorHandlerCount": len(vector["vectorHandlers"]),
            "wave581MetadataRows": vector["evidenceCounts"]["wave581MetadataRows"],
            "wave581TagRows": vector["evidenceCounts"]["wave581TagRows"],
            "wave581XrefRows": vector["evidenceCounts"]["wave581XrefRows"],
            "wave581DecompileRows": vector["evidenceCounts"]["wave581DecompileRows"],
            "wave581InstructionRows": vector["evidenceCounts"]["wave581InstructionRows"],
            "wave581VtableRows": vector["evidenceCounts"]["wave581VtableRows"],
            "directNonCommentLooseMslRows": sum(vector["looseMslUsage"]["directNonCommentCounts"].values()),
            "plannedVectorInputCount": len(VECTOR_FIXTURES),
            "plannedVectorAssertionCount": vector_assertion_count,
            "lengthCaseCount": len(length),
            "componentVectorCount": len(VECTOR_FIXTURES),
            "componentCaseCount": len(components),
            "plannedRangeCaseCount": len(ranges),
            "rangeCaseCount": len(ranges),
            "plannedHelperAssertionCount": deterministic_case_count,
            "deterministicHelperCaseCount": deterministic_case_count,
            "finiteOnlyCaseCount": deterministic_case_count,
            "nonFiniteFloatCaseCount": 0,
            "nonFiniteFloatBehaviorDeferred": True,
            "selectionConsultCount": selection["selectionAccounting"]["consultCount"],
            "selectionSelectedCandidateRank": selection["selectionAccounting"]["selectedCandidateRank"],
            "rollupCommandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
            "fixtureSelectionDeferredRank": next(row["rank"] for row in fixture["candidateRanking"] if row["family"] == "vector-range-helpers"),
            "falseGuardCount": len(FALSE_GUARDS),
            "zeroCounterCount": len(ZERO_COUNTERS),
            "publicLeakCheck": "PASS",
        },
        "sourceEvidence": {
            "selectionRefresh": {
                "schema": "reverse-engineering/binary-analysis/static-to-proof-next-safe-slice-selection-refresh.v1.json",
                "status": selection["selectionRefreshStatus"],
                "selectedChildLane": selection["selectedChildLane"],
                "selectedChildScope": selection["selectedChildScope"],
            },
            "vectorRangeStaticProof": {
                "schema": "reverse-engineering/binary-analysis/missionscript-vector-range-command-effect.v1.json",
                "descriptorRecords": list(DESCRIPTOR_ROWS),
                "descriptorIndices": list(DESCRIPTOR_INDICES),
                "vectorHandlers": list(VECTOR_HANDLERS),
                "datatypeContext": {
                    "vectorGetterSlot": vector["datatypeContext"]["vectorGetterSlot"],
                    "floatGetterSlot": vector["datatypeContext"]["floatGetterSlot"],
                    "componentOffsets": vector["datatypeContext"]["componentOffsets"],
                    "floatVtable": vector["datatypeContext"]["floatVtable"],
                    "boolVtable": vector["datatypeContext"]["boolVtable"],
                },
                "descriptorBoundary": "raw static descriptor context only; exact descriptor layout, exact arity, and exact argument type schema remain unproven",
            },
            "rollup": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-rebuild-interface-rollup.v1.json",
                "commandFamilyCount": rollup["rollupAccounting"]["commandFamilyCount"],
                "descriptorRecordCount": rollup["rollupAccounting"]["descriptorRecordCount"],
                "uniqueDescriptorTokenCount": rollup["rollupAccounting"]["uniqueDescriptorTokenCount"],
            },
            "fixtureSelection": {
                "schema": "reverse-engineering/binary-analysis/missionscript-command-effect-fixture-selection.v1.json",
                "candidateFamilyCount": fixture["selectionAccounting"]["candidateFamilyCount"],
                "priorDeferredRank": next(row["rank"] for row in fixture["candidateRanking"] if row["family"] == "vector-range-helpers"),
            },
        },
        "helperModel": {
            "vectorLengthFormula": "sqrt(x*x+y*y+z*z)",
            "componentOffsets": {"x": "+0", "y": "+4", "z": "+8"},
            "rangeComparison": "(boundA <= value <= boundB) or (boundB <= value <= boundA)",
            "resultContext": {
                "floatResultVtable": "0x005e4ea4",
                "boolResultVtableContext": "0x005e4d50",
            },
            "finiteOnly": True,
            "excludedNumericCases": [
                "NaN",
                "infinity",
                "signed zero parity",
                "subnormal values",
                "overflow",
                "exact x87/CRT rounding parity",
                "allocator failure behavior",
            ],
        },
        "deterministicLengthCases": length,
        "deterministicComponentCases": components,
        "deterministicRangeCases": ranges,
        "deferredProofGate": {
            "selectedNextSlice": NEXT_SLICE,
            "runtimeExecution": False,
            "beLaunch": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "copiedFileMutation": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
            "requiresNewSelectionIfRuntimeNeeded": True,
            "requiresSeparateProofForNaNInfinitySignedZeroSubnormalOverflow": True,
        },
        "guardSummary": {
            "falseGuards": {key: False for key in FALSE_GUARDS},
            "zeroCounters": {key: 0 for key in ZERO_COUNTERS},
        },
        "claimBoundary": {
            "proves": [
                "pure deterministic vector length plus component helper math for four finite vectors",
                "pure deterministic component extraction across offsets +0, +4, and +8",
                "pure deterministic inclusive order-insensitive range helper behavior for twelve finite cases",
                "the static source anchors for the vector/range helper fixture are consolidated without runtime or Ghidra mutation",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime vector/range behavior",
                "live loose-MSL loading",
                "packed-resource script selection",
                "exact descriptor layout",
                "exact command arity",
                "exact argument type schema",
                "exact datatype layout",
                "exact vector layout",
                "NaN/infinity behavior",
                "signed-zero behavior",
                "subnormal behavior",
                "overflow behavior",
                "allocator failure behavior",
                "exact x87/CRT rounding parity",
                "exact result-object layout",
                "exact helper ABI",
                "exact source identity",
                "source-selection observation",
                "private-frame review",
                "visual QA",
                "Godot parity",
                "Ghidra mutation",
                "executable patching",
                "product UI behavior",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def assert_schema(actual: dict[str, Any], failures: list[str]) -> None:
    expected = build_schema()
    require(actual == expected, "schema is not regenerated from current evidence and fixture formulas", failures)
    accounting = actual["fixtureAccounting"]
    require(accounting["descriptorIndices"] == list(DESCRIPTOR_INDICES), "descriptor index list mismatch", failures)
    require(accounting["descriptorRecordCount"] == 9, "descriptor record count mismatch", failures)
    require(accounting["handlerAnchorCount"] == 5, "handler anchor count mismatch", failures)
    require(accounting["vectorHandlerCount"] == 5, "vector handler count mismatch", failures)
    require(accounting["wave581MetadataRows"] == 5, "Wave581 metadata count mismatch", failures)
    require(accounting["wave581TagRows"] == 5, "Wave581 tag count mismatch", failures)
    require(accounting["wave581XrefRows"] == 5, "Wave581 xref count mismatch", failures)
    require(accounting["wave581DecompileRows"] == 5, "Wave581 decompile count mismatch", failures)
    require(accounting["wave581InstructionRows"] == 3545, "Wave581 instruction count mismatch", failures)
    require(accounting["wave581VtableRows"] == 24, "Wave581 vtable count mismatch", failures)
    require(accounting["directNonCommentLooseMslRows"] == 0, "direct loose-MSL count mismatch", failures)
    require(accounting["helperFamilyCount"] == 3, "helper family count mismatch", failures)
    require(accounting["plannedVectorInputCount"] == 4, "planned vector input count mismatch", failures)
    require(accounting["plannedVectorAssertionCount"] == 16, "planned vector assertion count mismatch", failures)
    require(accounting["lengthCaseCount"] == 4, "length case count mismatch", failures)
    require(accounting["componentVectorCount"] == 4, "component vector count mismatch", failures)
    require(accounting["componentCaseCount"] == 12, "component case count mismatch", failures)
    require(accounting["plannedRangeCaseCount"] == 12, "planned range case count mismatch", failures)
    require(accounting["rangeCaseCount"] == 12, "range case count mismatch", failures)
    require(accounting["plannedHelperAssertionCount"] == 28, "planned helper assertion count mismatch", failures)
    require(accounting["deterministicHelperCaseCount"] == 28, "deterministic helper case count mismatch", failures)
    require(accounting["finiteOnlyCaseCount"] == 28, "finite case count mismatch", failures)
    require(accounting["nonFiniteFloatCaseCount"] == 0, "non-finite case count mismatch", failures)
    require(accounting["nonFiniteFloatBehaviorDeferred"] is True, "non-finite deferral mismatch", failures)
    require(accounting["selectionConsultCount"] == 2, "selection consult count mismatch", failures)
    require(accounting["selectionSelectedCandidateRank"] == 1, "selection rank mismatch", failures)
    require(accounting["fixtureSelectionDeferredRank"] == 2, "prior fixture deferred rank mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    for case in actual["deterministicLengthCases"]:
        require(case["finiteOnly"] is True, f"length case not finite-only: {case['id']}", failures)
        require(math.isclose(case["expected"], vector_length(case["vector"]), rel_tol=0.0, abs_tol=1e-12), f"length case formula mismatch: {case['id']}", failures)
    for case in actual["deterministicComponentCases"]:
        offsets = {"+0": 0, "+4": 1, "+8": 2}
        require(case["finiteOnly"] is True, f"component case not finite-only: {case['id']}", failures)
        require(case["expected"] == case["vector"][offsets[case["componentOffset"]]], f"component case mismatch: {case['id']}", failures)
    for case in actual["deterministicRangeCases"]:
        require(case["finiteOnly"] is True, f"range case not finite-only: {case['id']}", failures)
        require(case["expected"] == range_check(case["value"], case["boundA"], case["boundB"]), f"range case mismatch: {case['id']}", failures)

    guards = actual["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    assert_schema(result, failures)
    require(lore == result, "lore schema mirror mismatch", failures)
    check_no_bad_public_content(RESULT, failures)


def check_source_prerequisites(failures: list[str]) -> None:
    selection = read_json(SELECTION_REFRESH)
    vector = read_json(VECTOR_RANGE_SCHEMA)
    rollup = read_json(ROLLUP)
    fixture = read_json(FIXTURE_SELECTION)

    require(selection["selectionRefreshStatus"] == REFRESH_STATUS, "selection refresh status mismatch", failures)
    require(selection["selectedChildLane"] == THIS_SLICE, "selection refresh selected lane mismatch", failures)
    require(selection["selectionAccounting"]["consultCount"] == 2, "selection refresh consult count mismatch", failures)
    require(selection["selectionAccounting"]["selectedCandidateRank"] == 1, "selection refresh rank mismatch", failures)

    require(len(vector["descriptorRecords"]) == 9, "vector static descriptor count mismatch", failures)
    require(
        [record["index"] for record in vector["descriptorRecords"]] == list(DESCRIPTOR_INDICES),
        "vector static descriptor indices mismatch",
        failures,
    )
    require(len(vector["vectorHandlers"]) == 5, "vector static handler count mismatch", failures)
    require(vector["evidenceCounts"]["wave581MetadataRows"] == 5, "vector static metadata count mismatch", failures)
    require(vector["evidenceCounts"]["wave581TagRows"] == 5, "vector static tag count mismatch", failures)
    require(vector["evidenceCounts"]["wave581XrefRows"] == 5, "vector static xref count mismatch", failures)
    require(vector["evidenceCounts"]["wave581DecompileRows"] == 5, "vector static decompile count mismatch", failures)
    require(vector["evidenceCounts"]["wave581InstructionRows"] == 3545, "vector static instruction count mismatch", failures)
    require(vector["evidenceCounts"]["wave581VtableRows"] == 24, "vector static vtable count mismatch", failures)
    require(sum(vector["looseMslUsage"]["directNonCommentCounts"].values()) == 0, "vector static loose-MSL count mismatch", failures)
    require(vector["datatypeContext"]["vectorGetterSlot"] == "+0x44", "vector getter slot mismatch", failures)
    require(vector["datatypeContext"]["floatGetterSlot"] == "+0x34", "float getter slot mismatch", failures)
    require(vector["datatypeContext"]["componentOffsets"] == {"x": "+0", "y": "+4", "z": "+8"}, "component offsets mismatch", failures)
    require(vector["datatypeContext"]["floatVtable"] == "0x005e4ea4", "float vtable mismatch", failures)
    require(vector["datatypeContext"]["boolVtable"] == "0x005e4d50", "bool vtable mismatch", failures)

    require(rollup["rollupAccounting"]["commandFamilyCount"] == 9, "rollup family count mismatch", failures)
    require(rollup["rollupAccounting"]["descriptorRecordCount"] == 52, "rollup descriptor count mismatch", failures)
    require(rollup["rollupAccounting"]["uniqueDescriptorTokenCount"] == 48, "rollup token count mismatch", failures)
    require(next(row["rank"] for row in fixture["candidateRanking"] if row["family"] == "vector-range-helpers") == 2, "prior fixture deferred rank mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json",
        f"missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=vector-range-helpers",
        "selectedFixturePath=vector-range-finite-helper-math",
        "selectedNextSlice=MissionScript Goodie State / Save Command-Effect Fixture Proof Plan",
        "sourceProofCount=4",
        "helperFamilyCount=3",
        "descriptorIndices=56/57/58/59/60/61/104/105/108",
        "descriptorRecordCount=9",
        "handlerAnchorCount=5",
        "vectorHandlerCount=5",
        "wave581MetadataRows=5",
        "wave581TagRows=5",
        "wave581XrefRows=5",
        "wave581DecompileRows=5",
        "wave581InstructionRows=3545",
        "wave581VtableRows=24",
        "directNonCommentLooseMslRows=0",
        "plannedVectorInputCount=4",
        "plannedVectorAssertionCount=16",
        "lengthCaseCount=4",
        "componentVectorCount=4",
        "componentCaseCount=12",
        "plannedRangeCaseCount=12",
        "rangeCaseCount=12",
        "plannedHelperAssertionCount=28",
        "deterministicHelperCaseCount=28",
        "finiteOnlyCaseCount=28",
        "nonFiniteFloatCaseCount=0",
        "nonFiniteFloatBehaviorDeferred=true",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "0x005345d0 IScript__GetVectorLength",
        "0x005347b0 IScript__CheckValueInRange",
        "0x00534b80 IScript__GetVectorX",
        "0x00534c10 IScript__GetVectorY",
        "0x00534ca0 IScript__GetVectorZ",
        "0x0064dc50",
        "0x0064e950",
        "vector getter slot `+0x44`",
        "float getter slot `+0x34`",
        "component offsets `+0/+4/+8`",
        "0x005e4ea4",
        "0x005e4d50",
        "sqrt(x*x+y*y+z*z)",
        "(boundA <= value <= boundB) or (boundB <= value <= boundA)",
        "NaN",
        "infinity",
        "signed zero",
        "subnormal",
        "overflow",
        "exact x87/CRT rounding parity",
        "runtimeExecution=false",
        "beLaunch=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        "copiedFileMutation=false",
        "ghidraMutation=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeVectorRangeRows=0",
        "beProcessesAfterFixture=0",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-vector-range-deterministic-helper-fixture-proof-plan.md",
        "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json",
        f"missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=vector-range-helpers",
        "selectedNextSlice=MissionScript Goodie State / Save Command-Effect Fixture Proof Plan",
        "plannedVectorAssertionCount=16",
        "plannedHelperAssertionCount=28",
        "deterministicHelperCaseCount=28",
        "lengthCaseCount=4",
        "componentCaseCount=12",
        "rangeCaseCount=12",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, ISCRIPT_CONTRACT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks vector/range fixture active",
            failures,
        )
    backlog = read_text(BACKLOG)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed Goodie State / Save fixture lane", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog,
        "backlog still marks Goodie State / Save fixture lane active",
        failures,
    )
    require(
        f"Completed {COMPLETED_GOODIE_CLEAN_ROOM_SLICE}" in backlog,
        "backlog missing completed Goodie State / Save clean-room codec interface lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan. Status: selected" not in backlog,
        "backlog still marks Goodie State / Save clean-room codec interface lane active",
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
        f"Completed {NEXT_ACTIVE_SLICE}" in backlog,
        "backlog missing completed cutscene pan-camera/position fixture lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" not in backlog,
        "backlog still marks cutscene pan-camera/position fixture lane active",
        failures,
    )
    require(
        f"Completed {COMPLETION_ROLLUP_SLICE}" in backlog,
        "backlog missing completed fixture-family completion rollup lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in backlog,
        "backlog missing active post-rollup selection refresh lane",
        failures,
    )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (ISCRIPT_CONTRACT, LORE_ISCRIPT_CONTRACT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-vector-range-deterministic-helper-fixture-proof-plan")
        == r"py -3 tools\missionscript_vector_range_deterministic_helper_fixture_proof_plan_probe.py --check",
        "missing package vector/range deterministic helper fixture proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-vector-range-command-effect-static",
        "test:static-to-proof-next-safe-slice-selection-refresh",
        "test:static-to-proof-transition-backlog",
    ):
        require(script in scripts, f"missing source package script: {script}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_schema:
        schema = build_schema()
        write_json(RESULT, schema)
        write_json(LORE_RESULT, schema)
        print(f"Wrote {RESULT.relative_to(ROOT)}")
        print(f"Wrote {LORE_RESULT.relative_to(ROOT)}")

    if args.check or not args.write_schema:
        failures: list[str] = []
        check_source_prerequisites(failures)
        check_result(failures)
        check_docs(failures)
        check_package(failures)
        require(no_bea_process_running(), "BEA.exe process is running after vector/range helper fixture proof", failures)
        if failures:
            print("MissionScript vector/range deterministic helper fixture proof-plan probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript vector/range deterministic helper fixture proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
