#!/usr/bin/env python3
"""Validate the PhysicsScript spawner rebuild fixture proof-plan artifacts."""

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

import physics_script_spawner_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-spawner-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-spawner-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_spawner_rebuild_fixture_proof_plan_2026-06-10.md"
EXPLOSION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-spawner-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-spawner-rebuild-fixture-proof-plan.v1.json"),
    (EXPLOSION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.md"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-spawner-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Hazard Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-hazard-rebuild-fixture-proof-plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"
SELECTED_PATH = "spawner-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
EXPECTED_OBSERVED_VALUE_IDS = [1, 2, 3, 6, 7, 8, 9, 11, 12, 14]
EXPECTED_FACTORY_ONLY_VALUE_IDS = [4, 5, 10, 13]

EXPECTED_VALUE_ROWS = {
    1: ("unitName", {"owned_string_ascii_nul_shape_roundtrip": 34, "three_scalar4_roundtrip": 4}, False, True),
    2: ("delay", {"scalar4_roundtrip": 38}, False, False),
    3: ("amount", {"scalar4_roundtrip": 38}, False, False),
    4: ("seekDelay", {}, True, False),
    5: ("recallEnabled", {}, True, False),
    6: ("minRange", {"scalar4_roundtrip": 2}, False, False),
    7: ("maxRange", {"scalar4_roundtrip": 38}, False, False),
    8: ("preSpawnDelay", {"scalar4_roundtrip": 5}, False, False),
    9: ("postSpawnDelay", {"scalar4_roundtrip": 5}, False, False),
    10: ("basedOn", {}, True, False),
    11: ("squadSize", {"scalar4_roundtrip": 37}, False, False),
    12: ("squadDelay", {"scalar4_roundtrip": 34}, False, False),
    13: ("infinite", {}, True, False),
    14: ("conditions", {"scalar4_roundtrip": 9}, False, False),
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
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime spawner behavior proven",
    "runtime spawned-unit identity proven",
    "runtime spawn timing proven",
    "runtime spawner ai behavior proven",
    "runtime range behavior proven",
    "serialized physicsscript completeness proven",
    "exact spawner record layout proven",
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
    fresh = fixture_tool.build_report()
    require(schema == fresh, "tracked schema differs from fresh spawner fixture report", failures)

    require(schema["schemaVersion"] == "physics-script-spawner-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "spawner", "selected family mismatch", failures)
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
        "selectedCandidateRank": 2,
        "selectedSourceProofCount": 5,
        "selectedValueInterfaceRowCount": 14,
        "selectedValueIdCount": 14,
        "selectedObservedValueIdCount": 10,
        "selectedFactoryOnlyValueIdCount": 4,
        "selectedUnselectedObservedValueIdCount": 0,
        "selectedTopLevelRecordCount": 38,
        "selectedValueNodeCount": 244,
        "selectedRawValuePayloadBytesPreserved": 1441,
        "selectedDeclaredPayloadBytes": 5279,
        "selectedOwnedStringFieldCount": 2,
        "selectedScalarFieldCount": 11,
        "selectedFlagConstantTrueFieldCount": 1,
        "selectedFixtureRowCount": 14,
        "selectedObservedFixtureRowCount": 10,
        "selectedFactoryOnlyFixtureRowCount": 4,
        "selectedPayloadShapeCaseCount": 11,
        "selectedObservedPayloadShapeClassCount": 3,
        "selectedScalar4ShapePayloadCount": 206,
        "selectedOwnedStringShapePayloadCount": 34,
        "selectedThreeScalarShapePayloadCount": 4,
        "selectedMixedPayloadShapeValueIdCount": 1,
        "selectedCrosswalkOwnedStringCorpusCount": 38,
        "selectedCrosswalkScalarCorpusCount": 206,
        "selectedCrosswalkFlagConstantTrueCorpusCount": 0,
        "unitNameObservedOwnedStringShapeCount": 34,
        "unitNameObservedThreeScalarShapeCount": 4,
        "factoryOnlyValueIdCount": 4,
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
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(accounting["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)
    require(accounting["selectedMixedPayloadShapeValueIds"] == [1], "mixed shape value ids mismatch", failures)
    require(accounting["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "factory-only ids mismatch", failures)
    require(accounting["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "observed ids mismatch", failures)

    source = schema["sourceEvidence"]
    require(source["previousFixture"]["fixtureStatus"] == "physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof", "previous fixture status mismatch", failures)
    require(source["valueIdCrosswalk"]["deferredFactoryValueIds"] == [], "source deferred factory ids mismatch", failures)
    require(source["scalarStringFixture"]["observedSpawnerPayloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 34,
        "scalar4_roundtrip": 206,
        "three_scalar4_roundtrip": 4,
    }, "source observed shape totals mismatch", failures)

    selected = schema["selectedFixture"]
    require(selected["family"] == "spawner", "selected fixture family mismatch", failures)
    require(selected["pathId"] == SELECTED_PATH, "selected fixture path mismatch", failures)
    require(selected["statementFamilyTypeId"] == 5, "statement family id mismatch", failures)
    require(selected["valueFactoryTypeId"] == 6, "value factory id mismatch", failures)
    require(selected["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType6", "nested factory mismatch", failures)
    require(selected["statementLoader"] == "CSpawnerStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(selected["valueListLoader"] == "CPhysicsSpawnerValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(selected["createAnchor"] == "CSpawnerStatement__CreateSpawnerAndRecurse", "create anchor mismatch", failures)
    require(selected["registryGlobal"] == "DAT_008553f4", "registry mismatch", failures)
    require(selected["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(selected["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "selected observed ids mismatch", failures)
    require(selected["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "selected factory-only ids mismatch", failures)
    require(selected["ownedStringFields"] == ["unitName", "basedOn"], "owned string fields mismatch", failures)
    require(selected["scalarFields"] == ["delay", "amount", "seekDelay", "minRange", "maxRange", "preSpawnDelay", "postSpawnDelay", "squadSize", "squadDelay", "infinite", "conditions"], "scalar fields mismatch", failures)
    require(selected["flagConstantTrueFields"] == ["recallEnabled"], "flag fields mismatch", failures)
    require(selected["payloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 34,
        "scalar4_roundtrip": 206,
        "three_scalar4_roundtrip": 4,
    }, "selected shape totals mismatch", failures)
    require(selected["factoryOnlyBoundary"]["valueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "factory-only boundary ids mismatch", failures)
    require(selected["factoryOnlyBoundary"]["runtimeMeaningProven"] is False, "factory-only runtime boundary mismatch", failures)

    rows = {row["valueId"]: row for row in selected["fixtureRows"]}
    require(set(rows) == set(EXPECTED_VALUE_IDS), "fixture rows value-id set mismatch", failures)
    for value_id, (field_name, shapes, factory_only, mixed) in EXPECTED_VALUE_ROWS.items():
        row = rows.get(value_id)
        require(row is not None, f"missing fixture row {value_id}", failures)
        if row is None:
            continue
        require(row["rebuildFacingFieldName"] == field_name, f"field mismatch for value id {value_id}", failures)
        require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value id {value_id}", failures)
        require(row["factoryOnlyBoundary"] is factory_only, f"factory-only mismatch for value id {value_id}", failures)
        require(row["mixedPayloadShapeBoundary"] is mixed, f"mixed-shape mismatch for value id {value_id}", failures)
        require(row["publicSafe"] is True, f"public-safe mismatch for value id {value_id}", failures)

    requirement_rows = {row["row"]: row["status"] for row in schema["fixtureRequirementRows"]}
    require(requirement_rows == {
        "family-fixture": "satisfied-static-with-factory-only-boundary",
        "loader-fixture": "satisfied-static",
        "value-interface-fixture": "satisfied-static",
        "factory-only-boundary-fixture": "satisfied-explicit-boundary",
        "payload-shape-fixture": "satisfied-public-safe",
        "unit-name-fixture": "satisfied-static",
        "stop-fixture": "enforced",
    }, "fixture requirement rows mismatch", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"guard should be false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"counter should be zero: {key}", failures)
    require(schema["publicSafety"]["publicLeakCheck"] == "PASS", "public safety mismatch", failures)
    require(schema["publicSafety"]["rawCopiedStringsEmitted"] is False, "raw strings emitted flag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "physics-script-spawner-rebuild-fixture-proof-plan.v1.json",
        f"spawnerFixtureStatus={STATUS_TOKEN}",
        f"fixtureStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=spawner",
        f"selectedFixturePath={SELECTED_PATH}",
        "selectedNextSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan",
        "selectedNextScope=physics-script-hazard-rebuild-fixture-proof-plan",
        "selectedCandidateRank=2",
        "selectedSourceProofCount=5",
        "selectedValueInterfaceRowCount=14",
        "selectedValueIdCount=14",
        "selectedObservedValueIdCount=10",
        "selectedFactoryOnlyValueIdCount=4",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedTopLevelRecordCount=38",
        "selectedValueNodeCount=244",
        "selectedRawValuePayloadBytesPreserved=1441",
        "selectedDeclaredPayloadBytes=5279",
        "selectedOwnedStringFieldCount=2",
        "selectedScalarFieldCount=11",
        "selectedFlagConstantTrueFieldCount=1",
        "selectedFixtureRowCount=14",
        "selectedObservedFixtureRowCount=10",
        "selectedFactoryOnlyFixtureRowCount=4",
        "selectedPayloadShapeCaseCount=11",
        "selectedObservedPayloadShapeClassCount=3",
        "selectedScalar4ShapePayloadCount=206",
        "selectedOwnedStringShapePayloadCount=34",
        "selectedThreeScalarShapePayloadCount=4",
        "selectedMixedPayloadShapeValueIdCount=1",
        "selectedMixedPayloadShapeValueIds=1",
        "selectedCrosswalkOwnedStringCorpusCount=38",
        "selectedCrosswalkScalarCorpusCount=206",
        "selectedCrosswalkFlagConstantTrueCorpusCount=0",
        "unitNameObservedOwnedStringShapeCount=34",
        "unitNameObservedThreeScalarShapeCount=4",
        "factoryOnlyValueIdCount=4",
        "factoryOnlyValueIds=4/5/10/13",
        "observedValueIds=1/2/3/6/7/8/9/11/12/14",
        "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/14",
        "ownedStringFields=unitName/basedOn",
        "scalarFields=delay/amount/seekDelay/minRange/maxRange/preSpawnDelay/postSpawnDelay/squadSize/squadDelay/infinite/conditions",
        "flagConstantTrueFields=recallEnabled",
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
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "runtimeExecution=false",
        "beLaunch=false",
        "newLaunch=false",
        "screenshotCapture=false",
        "privateFrameReviewPerformed=false",
        "rowObservation=false",
        "sourceSelectionObserved=false",
        "sourceSelectionProven=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "productUiWired=false",
        "rebuildImplementation=false",
        "runtimePhysicsScriptBehaviorProven=false",
        "runtimeSpawnerBehaviorProven=false",
        "runtimeSpawnerUnitSpawnProven=false",
        "runtimeSpawnerTimingProven=false",
        "runtimeSpawnerAiBehaviorProven=false",
        "runtimeSpawnerRangeBehaviorProven=false",
        "serializedPhysicsScriptCompletenessProven=false",
        "completeValueIdSemanticsProven=false",
        "rawStringIdentityProven=false",
        "rawNumericMeaningProven=false",
        "runtimeObservationRows=0",
        "physicsScriptRuntimeEvidenceRows=0",
        "runtimePhysicsScriptRows=0",
        "runtimeSpawnerRows=0",
        "runtimeSpawnerUnitSpawnRows=0",
        "runtimeSpawnerTimingRows=0",
        "runtimeSpawnerAiRows=0",
        "runtimeSpawnerRangeRows=0",
        "CPhysicsScriptStatements__CreateStatementType6",
        "CSpawnerStatement__LoadFromMemBuffer",
        "CPhysicsSpawnerValueList__LoadFromMemBuffer",
        "CSpawnerStatement__CreateSpawnerAndRecurse",
        "CSpawnerData__CreateAndRegisterByName",
        "CSpawnerBasedOn__ApplyToSpawnerByName",
        "CSpawnerUnit__ApplyToSpawnerByName",
        "DAT_008553f4",
        "factory-only-boundary-fixture",
        "unit-name-fixture",
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
        "physics-script-spawner-rebuild-fixture-proof-plan.md",
        "physics-script-spawner-rebuild-fixture-proof-plan.v1.json",
        "selectedNextSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan",
        "selectedFixtureFamily=spawner",
        "selectedFixturePath=spawner-selected-value-id-interface-static-fixture",
        "selectedValueInterfaceRowCount=14",
        "selectedObservedValueIdCount=10",
        "selectedFactoryOnlyValueIdCount=4",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedPayloadShapeCaseCount=11",
        "selectedMixedPayloadShapeValueIds=1",
        "factoryOnlyValueIds=4/5/10/13",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, EXPLOSION_PLAN, SELECTION_PLAN):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed spawner fixture lane", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks spawner fixture active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed hazard fixture lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks hazard fixture active", failures)
    require(f"Completed {COMPLETED_ROUND_SLICE}" in backlog, "backlog missing completed round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROUND_SLICE}. Status: selected" not in backlog, "backlog still marks round fixture active", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript fixture-family completion rollup lane", failures)

    for source, mirror in LORE_FILES:
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-spawner-rebuild-fixture-proof-plan")
        == r"py -3 tools\physics_script_spawner_rebuild_fixture_proof_plan_probe.py --check",
        "missing package spawner fixture probe script",
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
        require(no_bea_process_running(), "BEA.exe process is running after spawner fixture probe", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript spawner rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript spawner rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
