#!/usr/bin/env python3
"""Validate the PhysicsScript weapon rebuild fixture proof-plan artifacts."""

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

import physics_script_weapon_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_weapon_rebuild_fixture_proof_plan_2026-06-10.md"
COMPONENT_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-component-rebuild-fixture-proof-plan.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-rebuild-fixture-proof-plan.v1.json"),
    (COMPONENT_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-component-rebuild-fixture-proof-plan.md"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Weapon Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-weapon-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Component Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-round-rebuild-fixture-proof-plan"
SELECTED_PATH = "weapon-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [1, 4, 5, 14]
EXPECTED_OBSERVED_VALUE_IDS = list(range(1, 15))
EXPECTED_FACTORY_ONLY_VALUE_IDS: list[int] = []
EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS = [2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
EXPECTED_MIXED_SHAPE_VALUE_IDS = [1]

EXPECTED_VALUE_ROWS = {
    1: ("chargeLevel", {"raw_preserved_other": 141, "three_scalar4_roundtrip": 1}, True),
    4: ("consumption", {"scalar4_roundtrip": 15}, False),
    5: ("iconName", {"owned_string_ascii_nul_shape_roundtrip": 15}, False),
    14: ("versusAir", {"scalar4_roundtrip": 12}, False),
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
    "runtime weapon behavior proven",
    "runtime weapon charge behavior proven",
    "runtime weapon firing behavior proven",
    "runtime weapon damage behavior proven",
    "serialized physicsscript completeness proven",
    "exact weapon record layout proven",
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
    require(schema == fixture_tool.build_report(), "tracked schema differs from fresh weapon fixture report", failures)
    require(schema["schemaVersion"] == "physics-script-weapon-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "weapon", "selected family mismatch", failures)
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
        "selectedCandidateRank": 6,
        "selectedSourceProofCount": 5,
        "selectedValueInterfaceRowCount": 4,
        "selectedValueIdCount": 4,
        "selectedObservedValueIdCount": 4,
        "selectedFactoryOnlyValueIdCount": 0,
        "selectedUnselectedObservedValueIdCount": 10,
        "selectedTopLevelRecordCount": 139,
        "selectedValueNodeCount": 286,
        "selectedRawValuePayloadBytesPreserved": 4082,
        "selectedDeclaredPayloadBytes": 8894,
        "selectedOwnedStringFieldCount": 1,
        "selectedScalarFieldCount": 2,
        "selectedCompoundChargeFieldCount": 1,
        "selectedFixtureRowCount": 4,
        "selectedObservedFixtureRowCount": 4,
        "selectedFactoryOnlyFixtureRowCount": 0,
        "selectedPayloadShapeCaseCount": 5,
        "selectedObservedPayloadShapeClassCount": 4,
        "selectedScalar4ShapePayloadCount": 27,
        "selectedOwnedStringShapePayloadCount": 15,
        "selectedTwoScalarShapePayloadCount": 0,
        "selectedThreeScalarShapePayloadCount": 1,
        "selectedRawPreservedOtherShapePayloadCount": 141,
        "selectedMixedPayloadShapeValueIdCount": 1,
        "selectedCrosswalkChargeLevelCorpusCount": 142,
        "selectedCrosswalkScalarCorpusCount": 27,
        "selectedCrosswalkOwnedStringCorpusCount": 15,
        "factoryOnlyValueIdCount": 0,
        "unselectedObservedValueIdCount": 10,
        "unselectedObservedScalar4PayloadCount": 102,
        "unselectedObservedRawPreservedOtherPayloadCount": 0,
        "unselectedObservedOwnedStringShapePayloadCount": 0,
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
    require(accounting["selectedMixedPayloadShapeValueIds"] == EXPECTED_MIXED_SHAPE_VALUE_IDS, "mixed payload ids mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    evidence = schema["sourceEvidence"]
    require(evidence["previousFixture"]["fixtureStatus"].startswith("physics-script-component-"), "previous fixture mismatch", failures)
    require(evidence["valueIdCrosswalk"]["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "crosswalk unselected ids mismatch", failures)

    fixture = schema["selectedFixture"]
    require(fixture["statementFamilyTypeId"] == 2, "statement family type mismatch", failures)
    require(fixture["valueFactoryTypeId"] == 3, "value factory type mismatch", failures)
    require(fixture["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType3", "nested factory mismatch", failures)
    require(fixture["statementLoader"] == "CWeaponStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(fixture["valueListLoader"] == "CPhysicsWeaponValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(fixture["createAnchor"] == "CWeaponStatement__CreateWeaponAndRecurse", "create anchor mismatch", failures)
    require(fixture["registryGlobal"] == "DAT_008553e8", "registry global mismatch", failures)
    require(fixture["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(fixture["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "fixture observed ids mismatch", failures)
    require(fixture["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "fixture factory-only ids mismatch", failures)
    require(fixture["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "fixture unselected observed ids mismatch", failures)
    require(fixture["ownedStringFields"] == ["iconName"], "owned string fields mismatch", failures)
    require(fixture["scalarFields"] == ["consumption", "versusAir"], "scalar fields mismatch", failures)
    require(fixture["compoundChargeFields"] == ["chargeLevel"], "compound charge fields mismatch", failures)
    require(fixture["payloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 15,
        "raw_preserved_other": 141,
        "scalar4_roundtrip": 27,
        "three_scalar4_roundtrip": 1,
    }, "payload totals mismatch", failures)

    rows = {row["valueId"]: row for row in fixture["fixtureRows"]}
    require(sorted(rows) == EXPECTED_VALUE_IDS, "fixture row ids mismatch", failures)
    for value_id, (field, shapes, mixed) in EXPECTED_VALUE_ROWS.items():
        row = rows[value_id]
        require(row["rebuildFacingFieldName"] == field, f"field mismatch for value {value_id}", failures)
        require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value {value_id}", failures)
        require(row["mixedPayloadShapeBoundary"] is mixed, f"mixed-shape boundary mismatch for value {value_id}", failures)
        require(row["publicSafe"] is True, f"public-safe false for value {value_id}", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"false guard not false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"zero counter not zero: {key}", failures)
    for key in ("runtimeExecution", "godotWork", "ghidraMutation", "executablePatching", "rebuildImplementation"):
        require(schema["guardSummary"]["falseGuards"][key] is False, f"critical guard not false: {key}", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PLAN, READINESS, COMPONENT_PLAN, SELECTION_PLAN, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT]
    required = (
        THIS_SLICE,
        THIS_SCOPE,
        STATUS_TOKEN,
        NEXT_SLICE,
        NEXT_SCOPE,
        SELECTED_PATH,
        "selectedValueIds=1/4/5/14",
        "unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13",
        "selectedMixedPayloadShapeValueIds=1",
        "CWeaponStatement__LoadFromMemBuffer",
        "CPhysicsWeaponValueList__LoadFromMemBuffer",
        "CWeaponStatement__CreateWeaponAndRecurse",
        "DAT_008553e8",
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
    expected_script = r"py -3 tools\physics_script_weapon_rebuild_fixture_proof_plan_probe.py --check"
    require(
        package.get("scripts", {}).get("test:physics-script-weapon-rebuild-fixture-proof-plan") == expected_script,
        "missing package script",
        failures,
    )


def check_runtime_boundary(failures: list[str]) -> None:
    require(no_bea_process_running(), "BEA process is running during static weapon fixture proof", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_runtime_boundary(failures)
    if failures:
        print("PhysicsScript weapon rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript weapon rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
