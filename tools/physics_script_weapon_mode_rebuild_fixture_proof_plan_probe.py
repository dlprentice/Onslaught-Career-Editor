#!/usr/bin/env python3
"""Validate the PhysicsScript weapon-mode rebuild fixture proof-plan artifacts."""

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

import physics_script_weapon_mode_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-mode-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_weapon_mode_rebuild_fixture_proof_plan_2026-06-10.md"
ROUND_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-round-rebuild-fixture-proof-plan.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-mode-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json"),
    (ROUND_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-round-rebuild-fixture-proof-plan.md"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-weapon-mode-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-weapon-mode-rebuild-fixture-proof-plan-complete-static-weapon-mode-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Unit Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-unit-rebuild-fixture-proof-plan"
SELECTED_PATH = "weapon-mode-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [2, 6, 15, 18, 24, 28, 31, 34, 36]
EXPECTED_OBSERVED_VALUE_IDS = [
    1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35
]
EXPECTED_FACTORY_ONLY_VALUE_IDS = [15, 36]
EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS = [
    1, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 20, 21, 22, 23, 26, 27, 29, 30, 32, 33, 35
]
EXPECTED_MIXED_SHAPE_VALUE_IDS = [2, 24]

EXPECTED_VALUE_ROWS = {
    2: ("roundNameOrRoundRef", {"owned_string_ascii_nul_shape_roundtrip": 112, "three_scalar4_roundtrip": 23, "two_scalar4_roundtrip": 9}, True, False),
    6: ("muzzleEffect", {"owned_string_ascii_nul_shape_roundtrip": 118}, False, False),
    15: ("clip", {}, False, True),
    18: ("preFireEffect", {"owned_string_ascii_nul_shape_roundtrip": 15}, False, False),
    24: ("launchSound", {"owned_string_ascii_nul_shape_roundtrip": 87, "scalar4_roundtrip": 4, "three_scalar4_roundtrip": 13}, True, False),
    28: ("volleySize", {"scalar4_roundtrip": 39}, False, False),
    31: ("launchAngle3", {"three_scalar4_roundtrip": 40}, False, False),
    34: ("preFireSound", {"owned_string_ascii_nul_shape_roundtrip": 2}, False, False),
    36: ("postFireSound", {}, False, True),
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
    "runtime weapon-mode behavior proven",
    "runtime weapon-mode round selection proven",
    "runtime weapon-mode effect behavior proven",
    "runtime weapon-mode audio behavior proven",
    "runtime weapon-mode volley behavior proven",
    "runtime weapon-mode launch-angle behavior proven",
    "runtime weapon firing cadence proven",
    "runtime projectile spawn proven",
    "runtime projectile outcomes proven",
    "serialized physicsscript completeness proven",
    "exact weapon-mode record layout proven",
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
    require(schema == fixture_tool.build_report(), "tracked schema differs from fresh weapon-mode fixture report", failures)
    require(schema["schemaVersion"] == "physics-script-weapon-mode-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "weapon-mode", "selected family mismatch", failures)
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
        "selectedCandidateRank": 8,
        "selectedSourceProofCount": 5,
        "selectedValueInterfaceRowCount": 9,
        "selectedValueIdCount": 9,
        "selectedObservedValueIdCount": 7,
        "selectedFactoryOnlyValueIdCount": 2,
        "selectedUnselectedObservedValueIdCount": 25,
        "selectedTopLevelRecordCount": 145,
        "selectedValueNodeCount": 1934,
        "selectedRawValuePayloadBytesPreserved": 15007,
        "selectedDeclaredPayloadBytes": 33261,
        "selectedOwnedStringFieldCount": 7,
        "selectedRoundedScalarFieldCount": 1,
        "selectedThreeScalarFieldCount": 1,
        "selectedFixtureRowCount": 9,
        "selectedObservedFixtureRowCount": 7,
        "selectedFactoryOnlyFixtureRowCount": 2,
        "selectedPayloadShapeCaseCount": 11,
        "selectedObservedPayloadShapeClassCount": 4,
        "selectedScalar4ShapePayloadCount": 43,
        "selectedOwnedStringShapePayloadCount": 334,
        "selectedTwoScalarShapePayloadCount": 9,
        "selectedThreeScalarShapePayloadCount": 76,
        "selectedRawPreservedOtherShapePayloadCount": 0,
        "selectedMixedPayloadShapeValueIdCount": 2,
        "selectedCrosswalkOwnedStringCorpusCount": 383,
        "selectedCrosswalkRoundedScalarCorpusCount": 39,
        "selectedCrosswalkThreeScalarCorpusCount": 40,
        "roundNameOrRoundRefObservedOwnedStringShapeCount": 112,
        "roundNameOrRoundRefObservedTwoScalarShapeCount": 9,
        "roundNameOrRoundRefObservedThreeScalarShapeCount": 23,
        "launchSoundObservedOwnedStringShapeCount": 87,
        "launchSoundObservedScalar4ShapeCount": 4,
        "launchSoundObservedThreeScalarShapeCount": 13,
        "factoryOnlyValueIdCount": 2,
        "unselectedObservedValueIdCount": 25,
        "unselectedObservedScalar4PayloadCount": 1247,
        "unselectedObservedTwoScalarPayloadCount": 225,
        "unselectedObservedOwnedStringShapePayloadCount": 0,
        "unselectedObservedRawPreservedOtherPayloadCount": 0,
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
    require(evidence["previousFixture"]["fixtureStatus"].startswith("physics-script-round-"), "previous fixture mismatch", failures)
    require(evidence["valueIdCrosswalk"]["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "crosswalk unselected ids mismatch", failures)

    fixture = schema["selectedFixture"]
    require(fixture["statementFamilyTypeId"] == 3, "statement family type mismatch", failures)
    require(fixture["valueFactoryTypeId"] == 4, "value factory type mismatch", failures)
    require(fixture["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType4", "nested factory mismatch", failures)
    require(fixture["statementLoader"] == "CWeaponModeStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(fixture["valueListLoader"] == "CPhysicsWeaponModeValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(fixture["createAnchor"] == "CWeaponModeStatement__CreateWeaponModeAndRecurse", "create anchor mismatch", failures)
    require(fixture["registryGlobal"] == "DAT_008553ec", "registry global mismatch", failures)
    require(fixture["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(fixture["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "fixture observed ids mismatch", failures)
    require(fixture["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "fixture factory-only ids mismatch", failures)
    require(fixture["unselectedObservedValueIds"] == EXPECTED_UNSELECTED_OBSERVED_VALUE_IDS, "fixture unselected observed ids mismatch", failures)
    require(
        fixture["ownedStringFields"] == ["roundNameOrRoundRef", "muzzleEffect", "clip", "preFireEffect", "launchSound", "preFireSound", "postFireSound"],
        "owned string fields mismatch",
        failures,
    )
    require(fixture["roundedScalarFields"] == ["volleySize"], "rounded scalar fields mismatch", failures)
    require(fixture["threeScalarFields"] == ["launchAngle3"], "three scalar fields mismatch", failures)
    require(
        fixture["payloadShapeTotals"]
        == {
            "owned_string_ascii_nul_shape_roundtrip": 334,
            "scalar4_roundtrip": 43,
            "three_scalar4_roundtrip": 76,
            "two_scalar4_roundtrip": 9,
        },
        "payload totals mismatch",
        failures,
    )

    rows = {row["valueId"]: row for row in fixture["fixtureRows"]}
    require(sorted(rows) == EXPECTED_VALUE_IDS, "fixture row ids mismatch", failures)
    for value_id, (field, shapes, mixed, factory_only) in EXPECTED_VALUE_ROWS.items():
        row = rows[value_id]
        require(row["rebuildFacingFieldName"] == field, f"field mismatch for value {value_id}", failures)
        require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value {value_id}", failures)
        require(row["mixedPayloadShapeBoundary"] is mixed, f"mixed-shape boundary mismatch for value {value_id}", failures)
        require(row["factoryOnlyBoundary"] is factory_only, f"factory-only boundary mismatch for value {value_id}", failures)
        require(sum(row["observedPayloadShapeClasses"].values()) == row["copiedCorpusCount"], f"shape sum mismatch for value {value_id}", failures)
        require(row["publicSafe"] is True, f"public-safe false for value {value_id}", failures)

    require(rows[15]["observedPayloadShapeClasses"] == {}, "factory-only clip row has shape evidence", failures)
    require(rows[36]["observedPayloadShapeClasses"] == {}, "factory-only postFireSound row has shape evidence", failures)
    require(fixture["factoryOnlyBoundary"]["valueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "factory-only boundary ids mismatch", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"false guard not false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"zero counter not zero: {key}", failures)
    for key in ("runtimeExecution", "godotWork", "ghidraMutation", "executablePatching", "rebuildImplementation"):
        require(schema["guardSummary"]["falseGuards"][key] is False, f"critical guard not false: {key}", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PLAN, READINESS, ROUND_PLAN, SELECTION_PLAN, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT]
    required = (
        THIS_SLICE,
        THIS_SCOPE,
        STATUS_TOKEN,
        NEXT_SLICE,
        NEXT_SCOPE,
        SELECTED_PATH,
        "selectedValueIds=2/6/15/18/24/28/31/34/36",
        "factoryOnlyValueIds=15/36",
        "unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35",
        "selectedMixedPayloadShapeValueIds=2/24",
        "CWeaponModeStatement__LoadFromMemBuffer",
        "CPhysicsWeaponModeValueList__LoadFromMemBuffer",
        "CWeaponModeStatement__CreateWeaponModeAndRecurse",
        "DAT_008553ec",
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
    expected_script = r"py -3 tools\physics_script_weapon_mode_rebuild_fixture_proof_plan_probe.py --check"
    require(
        package.get("scripts", {}).get("test:physics-script-weapon-mode-rebuild-fixture-proof-plan") == expected_script,
        "missing package script",
        failures,
    )


def check_runtime_boundary(failures: list[str]) -> None:
    require(no_bea_process_running(), "BEA process is running during static weapon-mode fixture proof", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_runtime_boundary(failures)
    if failures:
        print("PhysicsScript weapon-mode rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript weapon-mode rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
