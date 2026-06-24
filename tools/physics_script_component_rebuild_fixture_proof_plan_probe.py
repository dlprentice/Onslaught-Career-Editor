#!/usr/bin/env python3
"""Validate the PhysicsScript component rebuild fixture proof-plan artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import physics_script_component_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-component-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-component-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_component_rebuild_fixture_proof_plan_2026-06-10.md"
FEATURE_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-feature-rebuild-fixture-proof-plan.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-component-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-component-rebuild-fixture-proof-plan.v1.json"),
    (FEATURE_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-feature-rebuild-fixture-proof-plan.md"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Component Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-component-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-component-rebuild-fixture-proof-plan-complete-static-component-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Feature Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Weapon Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-weapon-rebuild-fixture-proof-plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
ACTIVE_AFTER_ROUND_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"
SELECTED_PATH = "component-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25]
EXPECTED_OBSERVED_VALUE_IDS = [1, 3, 6, 7, 8, 9, 11, 12, 13, 15, 18, 20, 21, 22, 23, 25]
EXPECTED_FACTORY_ONLY_VALUE_IDS = [10, 16, 17, 24]
EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS = [2, 4, 14, 19]

EXPECTED_VALUE_ROWS = {
    1: ("scalarC0", {"scalar4_roundtrip": 39}, False),
    3: ("mesh", {"owned_string_ascii_nul_shape_roundtrip": 39}, False),
    6: ("scalar158", {"scalar4_roundtrip": 25}, False),
    7: ("scalarDC", {"scalar4_roundtrip": 9}, False),
    8: ("scalarD8", {"scalar4_roundtrip": 6}, False),
    9: ("scalarB8", {"scalar4_roundtrip": 7}, False),
    10: ("basedOn", {}, True),
    11: ("scalarBC", {"scalar4_roundtrip": 8}, False),
    12: ("noise", {"owned_string_ascii_nul_shape_roundtrip": 1}, False),
    13: ("flag124", {"scalar4_roundtrip": 2}, False),
    15: ("flag128", {"scalar4_roundtrip": 2}, False),
    16: ("flag108", {}, True),
    17: ("scalar160", {}, True),
    18: ("flag12C", {"scalar4_roundtrip": 2}, False),
    20: ("indexedScalar164", {"two_scalar4_roundtrip": 1}, False),
    21: ("flag198", {"scalar4_roundtrip": 2}, False),
    22: ("flag114", {"scalar4_roundtrip": 10}, False),
    23: ("flag19C", {"scalar4_roundtrip": 4}, False),
    24: ("flag134", {}, True),
    25: ("vent", {"owned_string_ascii_nul_shape_roundtrip": 1}, False),
}

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
    (re.compile(r"(?i)capturepath|framepath|capturehash|framesha256"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime component behavior proven",
    "runtime component mesh proven",
    "runtime component noise proven",
    "runtime component vent proven",
    "runtime component flag behavior proven",
    "runtime component indexed-scalar behavior proven",
    "serialized physicsscript completeness proven",
    "exact component record layout proven",
    "complete value-id semantics proven",
    "all 185 pairs semantically named",
    "raw string identity proven",
    "raw numeric value meaning proven",
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


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


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


def check_schema(failures: list[str]) -> None:
    schema = read_json(SCHEMA)
    require(schema == fixture_tool.build_report(), "tracked schema differs from fresh component fixture report", failures)
    require(schema["schemaVersion"] == "physics-script-component-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "component", "selected family mismatch", failures)
    require(schema["selectedFixturePath"] == SELECTED_PATH, "selected path mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)

    accounting = schema["fixtureAccounting"]
    expected_counts = {
        "sourceProofCount": 6,
        "sourceSchemaCount": 5,
        "sourceMirrorPairCount": len(LORE_FILES),
        "selectedCandidateRank": 5,
        "selectedSourceProofCount": 5,
        "selectedValueInterfaceRowCount": 20,
        "selectedValueIdCount": 20,
        "selectedObservedValueIdCount": 16,
        "selectedFactoryOnlyValueIdCount": 4,
        "selectedUnselectedObservedValueIdCount": 4,
        "selectedTopLevelRecordCount": 39,
        "selectedValueNodeCount": 225,
        "selectedRawValuePayloadBytesPreserved": 2921,
        "selectedDeclaredPayloadBytes": 6337,
        "selectedOwnedStringFieldCount": 4,
        "selectedScalarFieldCount": 7,
        "selectedFlagConstantTrueFieldCount": 0,
        "selectedFlagFromScalarNonzeroFieldCount": 8,
        "selectedIndexedScalarFieldCount": 1,
        "selectedFixtureRowCount": 20,
        "selectedObservedFixtureRowCount": 16,
        "selectedFactoryOnlyFixtureRowCount": 4,
        "selectedPayloadShapeCaseCount": 16,
        "selectedObservedPayloadShapeClassCount": 3,
        "selectedScalar4ShapePayloadCount": 116,
        "selectedOwnedStringShapePayloadCount": 41,
        "selectedTwoScalarShapePayloadCount": 1,
        "selectedThreeScalarShapePayloadCount": 0,
        "selectedMixedPayloadShapeValueIdCount": 0,
        "selectedCrosswalkOwnedStringCorpusCount": 41,
        "selectedCrosswalkScalarCorpusCount": 94,
        "selectedCrosswalkFlagConstantTrueCorpusCount": 0,
        "selectedCrosswalkFlagFromScalarNonzeroCorpusCount": 22,
        "selectedCrosswalkIndexedScalarCorpusCount": 1,
        "meshObservedOwnedStringShapeCount": 39,
        "noiseObservedOwnedStringShapeCount": 1,
        "ventObservedOwnedStringShapeCount": 1,
        "indexedScalar164ObservedTwoScalarShapeCount": 1,
        "factoryOnlyValueIdCount": 4,
        "unselectedObservedValueIdCount": 4,
        "unselectedObservedRawPreservedOtherPayloadCount": 27,
        "unselectedObservedOwnedStringShapePayloadCount": 40,
        "topLevelFamilyCount": 9,
        "valueInterfaceRowCount": 87,
        "observedSelectedRowCount": 72,
        "factoryOnlySelectedRowCount": 15,
        "unselectedObservedRowCount": 113,
        "physicsScriptCorpusByteCount": 175603,
        "physicsScriptTopLevelStatementCount": 777,
        "physicsScriptValueListNodeCount": 6803,
        "physicsScriptStatementValuePairCount": 185,
        "physicsScriptRawValuePayloadBytesPreserved": 73796,
        "falseGuardCount": len(fixture_tool.FALSE_GUARDS),
        "zeroCounterCount": len(fixture_tool.ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(accounting[key] == expected, f"fixture accounting mismatch: {key}", failures)
    require(accounting["physicsScriptStreamHeader"] == "0x12", "stream header mismatch", failures)
    require(accounting["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "factory-only ids mismatch", failures)
    require(accounting["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "observed ids mismatch", failures)
    require(accounting["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "unselected observed ids mismatch", failures)
    require(accounting["selectedMixedPayloadShapeValueIds"] == [], "mixed payload ids mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    evidence = schema["sourceEvidence"]
    require(evidence["previousFixture"]["fixtureStatus"].startswith("physics-script-feature-"), "previous fixture mismatch", failures)
    require(evidence["valueIdCrosswalk"]["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "crosswalk unselected ids mismatch", failures)

    fixture = schema["selectedFixture"]
    require(fixture["statementFamilyTypeId"] == 7, "statement family type mismatch", failures)
    require(fixture["valueFactoryTypeId"] == 10, "value factory type mismatch", failures)
    require(fixture["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType10", "nested factory mismatch", failures)
    require(fixture["statementLoader"] == "CComponentStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(fixture["valueListLoader"] == "CPhysicsComponentValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(fixture["createAnchor"] == "CComponentStatement__CreateComponentAndRecurse", "create anchor mismatch", failures)
    require(fixture["registryGlobal"] == "DAT_00855400", "registry global mismatch", failures)
    require(fixture["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(fixture["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "fixture observed ids mismatch", failures)
    require(fixture["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "fixture factory-only ids mismatch", failures)
    require(fixture["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "fixture unselected observed ids mismatch", failures)
    require(fixture["ownedStringFields"] == ["mesh", "basedOn", "noise", "vent"], "owned string fields mismatch", failures)
    require(fixture["scalarFields"] == ["scalarC0", "scalar158", "scalarDC", "scalarD8", "scalarB8", "scalarBC", "scalar160"], "scalar fields mismatch", failures)
    require(fixture["flagConstantTrueFields"] == [], "flag constant fields mismatch", failures)
    require(
        fixture["flagFromScalarNonzeroFields"]
        == ["flag124", "flag128", "flag108", "flag12C", "flag198", "flag114", "flag19C", "flag134"],
        "flag fields mismatch",
        failures,
    )
    require(fixture["indexedScalarFields"] == ["indexedScalar164"], "indexed scalar fields mismatch", failures)
    require(fixture["payloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 41,
        "scalar4_roundtrip": 116,
        "two_scalar4_roundtrip": 1,
    }, "payload shape totals mismatch", failures)

    rows = {row["valueId"]: row for row in fixture["fixtureRows"]}
    for value_id, (field, shapes, factory_only) in EXPECTED_VALUE_ROWS.items():
        row = rows.get(value_id)
        require(row is not None, f"missing fixture row {value_id}", failures)
        if row is not None:
            require(row["rebuildFacingFieldName"] == field, f"field mismatch for value id {value_id}", failures)
            require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value id {value_id}", failures)
            require(row["factoryOnlyBoundary"] is factory_only, f"factory-only mismatch for value id {value_id}", failures)
            require(row["mixedPayloadShapeBoundary"] is False, f"mixed-shape mismatch for value id {value_id}", failures)
            require(row["publicSafe"] is True, f"public safe mismatch for value id {value_id}", failures)

    requirement_rows = {row["row"]: row["status"] for row in schema["fixtureRequirementRows"]}
    require(requirement_rows == {
        "family-fixture": "satisfied-static-with-factory-only-boundary",
        "loader-fixture": "satisfied-static",
        "value-interface-fixture": "satisfied-static",
        "factory-only-boundary-fixture": "satisfied-explicit-boundary",
        "unselected-observed-boundary-fixture": "satisfied-explicit-boundary",
        "payload-shape-fixture": "satisfied-public-safe",
        "mesh-noise-vent-fixture": "satisfied-static",
        "indexed-scalar-fixture": "satisfied-public-safe",
        "stop-fixture": "enforced",
    }, "fixture requirement rows mismatch", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"guard should be false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"counter should be zero: {key}", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "physics-script-component-rebuild-fixture-proof-plan.v1.json",
        f"componentFixtureStatus={STATUS_TOKEN}",
        f"fixtureStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=component",
        f"selectedFixturePath={SELECTED_PATH}",
        "selectedNextSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan",
        "selectedNextScope=physics-script-weapon-rebuild-fixture-proof-plan",
        "selectedCandidateRank=5",
        "selectedValueInterfaceRowCount=20",
        "selectedValueIdCount=20",
        "selectedObservedValueIdCount=16",
        "selectedFactoryOnlyValueIdCount=4",
        "selectedUnselectedObservedValueIdCount=4",
        "selectedTopLevelRecordCount=39",
        "selectedValueNodeCount=225",
        "selectedRawValuePayloadBytesPreserved=2921",
        "selectedDeclaredPayloadBytes=6337",
        "selectedOwnedStringFieldCount=4",
        "selectedScalarFieldCount=7",
        "selectedFlagConstantTrueFieldCount=0",
        "selectedFlagFromScalarNonzeroFieldCount=8",
        "selectedIndexedScalarFieldCount=1",
        "selectedFixtureRowCount=20",
        "selectedObservedFixtureRowCount=16",
        "selectedFactoryOnlyFixtureRowCount=4",
        "selectedPayloadShapeCaseCount=16",
        "selectedObservedPayloadShapeClassCount=3",
        "selectedScalar4ShapePayloadCount=116",
        "selectedOwnedStringShapePayloadCount=41",
        "selectedTwoScalarShapePayloadCount=1",
        "selectedThreeScalarShapePayloadCount=0",
        "selectedMixedPayloadShapeValueIdCount=0",
        "selectedMixedPayloadShapeValueIds=",
        "selectedCrosswalkOwnedStringCorpusCount=41",
        "selectedCrosswalkScalarCorpusCount=94",
        "selectedCrosswalkFlagFromScalarNonzeroCorpusCount=22",
        "selectedCrosswalkIndexedScalarCorpusCount=1",
        "meshObservedOwnedStringShapeCount=39",
        "noiseObservedOwnedStringShapeCount=1",
        "ventObservedOwnedStringShapeCount=1",
        "indexedScalar164ObservedTwoScalarShapeCount=1",
        "factoryOnlyValueIdCount=4",
        "factoryOnlyValueIds=10/16/17/24",
        "observedValueIds=1/3/6/7/8/9/11/12/13/15/18/20/21/22/23/25",
        "unselectedObservedValueIds=2/4/14/19",
        "unselectedObservedRawPreservedOtherPayloadCount=27",
        "unselectedObservedOwnedStringShapePayloadCount=40",
        "selectedValueIds=1/3/6/7/8/9/10/11/12/13/15/16/17/18/20/21/22/23/24/25",
        "ownedStringFields=mesh/basedOn/noise/vent",
        "scalarFields=scalarC0/scalar158/scalarDC/scalarD8/scalarB8/scalarBC/scalar160",
        "flagFromScalarNonzeroFields=flag124/flag128/flag108/flag12C/flag198/flag114/flag19C/flag134",
        "indexedScalarFields=indexedScalar164",
        "sourceProofCount=6",
        "sourceSchemaCount=5",
        f"sourceMirrorPairCount={len(LORE_FILES)}",
        "topLevelFamilyCount=9",
        "valueInterfaceRowCount=87",
        "observedSelectedRowCount=72",
        "factoryOnlySelectedRowCount=15",
        "unselectedObservedRowCount=113",
        "physicsScriptCorpusByteCount=175603",
        "physicsScriptStreamHeader=0x12",
        "physicsScriptTopLevelStatementCount=777",
        "physicsScriptValueListNodeCount=6803",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
        f"falseGuardCount={len(fixture_tool.FALSE_GUARDS)}",
        f"zeroCounterCount={len(fixture_tool.ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "runtimeExecution=false",
        "beLaunch=false",
        "godotWork=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "productUiWired=false",
        "rebuildImplementation=false",
        "runtimePhysicsScriptBehaviorProven=false",
        "runtimeComponentBehaviorProven=false",
        "serializedPhysicsScriptCompletenessProven=false",
        "completeValueIdSemanticsProven=false",
        "rawStringIdentityProven=false",
        "rawNumericMeaningProven=false",
        "runtimeObservationRows=0",
        "physicsScriptRuntimeEvidenceRows=0",
        "runtimePhysicsScriptRows=0",
        "runtimeComponentRows=0",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CComponentStatement__LoadFromMemBuffer",
        "CPhysicsComponentValueList__LoadFromMemBuffer",
        "CComponentStatement__CreateComponentAndRecurse",
        "CComponentMesh__ApplyToComponentByName",
        "CComponentNoise__ApplyToComponentByName",
        "CComponentBasedOn__ApplyToComponentByName",
        "CComponentVent__ApplyToComponentByName",
        "CComponentIndexedScalar164__ApplyToComponentByName",
        "DAT_00855400",
        "factory-only-boundary-fixture",
        "unselected-observed-boundary-fixture",
        "mesh-noise-vent-fixture",
        "indexed-scalar-fixture",
        "stop-fixture",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)
    check_no_bad_public_content(SCHEMA, failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physics-script-component-rebuild-fixture-proof-plan.md",
        "physics-script-component-rebuild-fixture-proof-plan.v1.json",
        "selectedNextSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan",
        "selectedFixtureFamily=component",
        "selectedFixturePath=component-selected-value-id-interface-static-fixture",
        "selectedValueInterfaceRowCount=20",
        "selectedObservedValueIdCount=16",
        "selectedFactoryOnlyValueIdCount=4",
        "selectedUnselectedObservedValueIdCount=4",
        "selectedPayloadShapeCaseCount=16",
        "factoryOnlyValueIds=10/16/17/24",
        "unselectedObservedValueIds=2/4/14/19",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, FEATURE_PLAN, SELECTION_PLAN):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed component fixture lane", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks component fixture active", failures)
    require(f"Completed {COMPLETED_ROUND_SLICE}" in backlog, "backlog missing completed round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROUND_SLICE}. Status: selected" not in backlog, "backlog still marks round fixture active", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_AFTER_ROUND_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript fixture-family completion rollup lane", failures)

    for source, mirror in LORE_FILES:
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-component-rebuild-fixture-proof-plan")
        == r"py -3 tools\physics_script_component_rebuild_fixture_proof_plan_probe.py --check",
        "missing package component fixture probe script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        check_schema(failures)
        check_docs(failures)
        require(no_bea_process_running(), "BEA.exe process is running after component fixture probe", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript component rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript component rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
