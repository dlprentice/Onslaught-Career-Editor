#!/usr/bin/env python3
"""Validate the PhysicsScript unit rebuild fixture proof-plan artifacts."""

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

import physics_script_unit_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-unit-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-unit-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_unit_rebuild_fixture_proof_plan_2026-06-10.md"
WEAPON_MODE_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-mode-rebuild-fixture-proof-plan.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-unit-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-unit-rebuild-fixture-proof-plan.v1.json"),
    (WEAPON_MODE_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-mode-rebuild-fixture-proof-plan.md"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Unit Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-unit-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-unit-rebuild-fixture-proof-plan-complete-static-unit-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Fixture Family Completion Rollup Proof Plan"
NEXT_SCOPE = "physics-script-fixture-family-completion-rollup-proof-plan"
SELECTED_PATH = "unit-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [7, 8, 20, 21, 22, 25, 60, 61]
EXPECTED_OBSERVED_VALUE_IDS = [
    1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18, 21, 22, 23, 27, 28, 29, 30, 31, 32, 33, 36, 38, 39,
    40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 61, 62, 63, 65, 66,
    67, 68, 70
]
EXPECTED_FACTORY_ONLY_VALUE_IDS = [20, 25]
EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS = [
    1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 18, 23, 27, 28, 29, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42,
    43, 44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 62, 63, 65, 66, 67, 68, 70
]

EXPECTED_VALUE_ROWS = {
    7: ("use", {"raw_preserved_other": 118}, False),
    8: ("behaviour", {"scalar4_roundtrip": 160}, False),
    20: ("importance", {}, True),
    21: ("soundMaterial", {"scalar4_roundtrip": 123}, False),
    22: ("strafeChange", {"scalar4_roundtrip": 2}, False),
    25: ("navMap", {}, True),
    60: ("standingLegPlacementArea", {"scalar4_roundtrip": 3}, False),
    61: ("maxLegsLifted", {"scalar4_roundtrip": 4}, False),
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
    "runtime unit behavior proven",
    "runtime unit ai behavior proven",
    "runtime unit movement behavior proven",
    "runtime unit sound-material behavior proven",
    "runtime unit navigation behavior proven",
    "runtime unit leg-placement behavior proven",
    "serialized physicsscript completeness proven",
    "exact unit record layout proven",
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
    require(schema == fixture_tool.build_report(), "tracked schema differs from fresh unit fixture report", failures)
    require(schema["schemaVersion"] == "physics-script-unit-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "unit", "selected family mismatch", failures)
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
        "selectedCandidateRank": 9,
        "selectedSourceProofCount": 5,
        "selectedValueInterfaceRowCount": 8,
        "selectedValueIdCount": 8,
        "selectedObservedValueIdCount": 6,
        "selectedFactoryOnlyValueIdCount": 2,
        "selectedUnselectedObservedValueIdCount": 48,
        "selectedTopLevelRecordCount": 160,
        "selectedValueNodeCount": 2338,
        "selectedRawValuePayloadBytesPreserved": 28840,
        "selectedDeclaredPayloadBytes": 50284,
        "selectedCompoundOwnedStringFieldCount": 1,
        "selectedNestedEnumChildFieldCount": 2,
        "selectedScalarFieldCount": 3,
        "selectedRoundedScalarFieldCount": 2,
        "selectedFixtureRowCount": 8,
        "selectedObservedFixtureRowCount": 6,
        "selectedFactoryOnlyFixtureRowCount": 2,
        "selectedPayloadShapeCaseCount": 6,
        "selectedObservedPayloadShapeClassCount": 2,
        "selectedScalar4ShapePayloadCount": 292,
        "selectedRawPreservedOtherShapePayloadCount": 118,
        "selectedOwnedStringShapePayloadCount": 0,
        "selectedTwoScalarShapePayloadCount": 0,
        "selectedThreeScalarShapePayloadCount": 0,
        "selectedMixedPayloadShapeValueIdCount": 0,
        "selectedCrosswalkCompoundOwnedStringCorpusCount": 118,
        "selectedCrosswalkNestedEnumChildCorpusCount": 160,
        "selectedCrosswalkScalarCorpusCount": 5,
        "selectedCrosswalkRoundedScalarCorpusCount": 127,
        "useObservedRawPreservedOtherShapeCount": 118,
        "behaviourObservedScalar4ShapeCount": 160,
        "soundMaterialObservedScalar4ShapeCount": 123,
        "strafeChangeObservedScalar4ShapeCount": 2,
        "standingLegPlacementAreaObservedScalar4ShapeCount": 3,
        "maxLegsLiftedObservedScalar4ShapeCount": 4,
        "factoryOnlyValueIdCount": 2,
        "unselectedObservedValueIdCount": 48,
        "unselectedObservedScalar4PayloadCount": 912,
        "unselectedObservedTwoScalarPayloadCount": 123,
        "unselectedObservedThreeScalarPayloadCount": 31,
        "unselectedObservedOwnedStringShapePayloadCount": 511,
        "unselectedObservedRawPreservedOtherPayloadCount": 351,
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
    require(evidence["previousFixture"]["fixtureStatus"].startswith("physics-script-weapon-mode-"), "previous fixture mismatch", failures)
    require(evidence["valueIdCrosswalk"]["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "crosswalk unselected ids mismatch", failures)

    fixture = schema["selectedFixture"]
    require(fixture["statementFamilyTypeId"] == 1, "statement family type mismatch", failures)
    require(fixture["valueFactoryTypeId"] == 2, "value factory type mismatch", failures)
    require(fixture["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType2", "nested factory mismatch", failures)
    require(fixture["statementLoader"] == "CUnitStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(fixture["valueListLoader"] == "CPhysicsUnitValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(fixture["createAnchor"] == "CUnitStatement__CreateUnitAndRecurse", "create anchor mismatch", failures)
    require(fixture["registryGlobal"] == "DAT_008553fc", "registry global mismatch", failures)
    require(fixture["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(fixture["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "fixture observed ids mismatch", failures)
    require(fixture["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "fixture factory-only ids mismatch", failures)
    require(fixture["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "fixture unselected observed ids mismatch", failures)
    require(fixture["compoundOwnedStringFields"] == ["use"], "compound owned string fields mismatch", failures)
    require(fixture["nestedEnumChildFields"] == ["behaviour", "navMap"], "nested enum fields mismatch", failures)
    require(fixture["scalarFields"] == ["importance", "strafeChange", "standingLegPlacementArea"], "scalar fields mismatch", failures)
    require(fixture["roundedScalarFields"] == ["soundMaterial", "maxLegsLifted"], "rounded scalar fields mismatch", failures)
    require(fixture["payloadShapeTotals"] == {"raw_preserved_other": 118, "scalar4_roundtrip": 292}, "payload totals mismatch", failures)

    rows = {row["valueId"]: row for row in fixture["fixtureRows"]}
    require(sorted(rows) == EXPECTED_VALUE_IDS, "fixture row ids mismatch", failures)
    for value_id, (field, shapes, factory_only) in EXPECTED_VALUE_ROWS.items():
        row = rows[value_id]
        require(row["rebuildFacingFieldName"] == field, f"field mismatch for value {value_id}", failures)
        require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value {value_id}", failures)
        require(row["mixedPayloadShapeBoundary"] is False, f"mixed-shape boundary mismatch for value {value_id}", failures)
        require(row["factoryOnlyBoundary"] is factory_only, f"factory-only boundary mismatch for value {value_id}", failures)
        require(sum(row["observedPayloadShapeClasses"].values()) == row["copiedCorpusCount"], f"shape sum mismatch for value {value_id}", failures)
        require(row["publicSafe"] is True, f"public-safe false for value {value_id}", failures)

    require(rows[20]["observedPayloadShapeClasses"] == {}, "factory-only importance row has shape evidence", failures)
    require(rows[25]["observedPayloadShapeClasses"] == {}, "factory-only navMap row has shape evidence", failures)
    require(fixture["factoryOnlyBoundary"]["valueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "factory-only boundary ids mismatch", failures)
    require(fixture["compoundRawPreservedBoundary"]["valueIds"] == [7], "compound boundary ids mismatch", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"false guard not false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"zero counter not zero: {key}", failures)
    for key in ("runtimeExecution", "godotWork", "ghidraMutation", "executablePatching", "rebuildImplementation"):
        require(schema["guardSummary"]["falseGuards"][key] is False, f"critical guard not false: {key}", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PLAN, READINESS, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT]
    required = (
        THIS_SLICE,
        THIS_SCOPE,
        STATUS_TOKEN,
        NEXT_SLICE,
        NEXT_SCOPE,
        SELECTED_PATH,
        "selectedValueIds=7/8/20/21/22/25/60/61",
        "factoryOnlyValueIds=20/25",
        "unselectedObservedValueIds=1/2/3/5/6/9/10/11/12/13/14/18/23/27/28/29/30/31/32/33/36/38/39/40/41/42/43/44/45/46/47/48/50/51/52/53/54/55/56/57/58/62/63/65/66/67/68/70",
        "selectedMixedPayloadShapeValueIds=none",
        "CUnitStatement__LoadFromMemBuffer",
        "CPhysicsUnitValueList__LoadFromMemBuffer",
        "CUnitStatement__CreateUnitAndRecurse",
        "CUnitAI__CreateAndRegisterByName",
        "DAT_008553fc",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in docs:
        text = read_text(path)
        for token in required:
            require(token in text, f"missing token in {path.relative_to(ROOT)}: {token}", failures)
    for path in (PLAN, READINESS):
        check_no_bad_public_content(path, failures)

    schema = read_json(SCHEMA)
    require(schema["publicSafety"]["publicLeakCheck"] == "PASS", "schema public leak check mismatch", failures)
    require(schema["publicSafety"]["rawBytesEmitted"] is False, "schema emits raw bytes", failures)

    for src, dst in LORE_FILES:
        require(dst.is_file(), f"missing lore mirror: {dst.relative_to(ROOT)}", failures)
        if dst.is_file():
            require(read_text(src) == read_text(dst), f"lore mirror differs: {dst.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\physics_script_unit_rebuild_fixture_proof_plan_probe.py --check"
    require(
        package.get("scripts", {}).get("test:physics-script-unit-rebuild-fixture-proof-plan") == expected_script,
        "missing package script",
        failures,
    )


def check_runtime_boundary(failures: list[str]) -> None:
    require(no_bea_process_running(), "BEA process is running during static unit fixture proof", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_runtime_boundary(failures)
    if failures:
        print("PhysicsScript unit rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript unit rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
