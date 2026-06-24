#!/usr/bin/env python3
"""Validate the PhysicsScript explosion rebuild fixture proof-plan artifacts."""

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

import physics_script_explosion_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402
import physics_script_rebuild_fixture_selection as selection_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_explosion_rebuild_fixture_proof_plan_2026-06-10.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
SELECTION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.v1.json"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-explosion-rebuild-fixture-proof-plan.v1.json"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-explosion-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
NEXT_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-spawner-rebuild-fixture-proof-plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"
SELECTED_PATH = "explosion-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]

EXPECTED_VALUE_ROWS = {
    1: ("basedOn", {"owned_string_ascii_nul_shape_roundtrip": 14}),
    2: ("airEffect", {"owned_string_ascii_nul_shape_roundtrip": 111}),
    3: ("scalar34", {"scalar4_roundtrip": 104}),
    4: ("scalar38", {"scalar4_roundtrip": 94}),
    5: ("groundEffect", {"owned_string_ascii_nul_shape_roundtrip": 107}),
    6: ("waterEffect", {"owned_string_ascii_nul_shape_roundtrip": 107}),
    7: ("unitEffect", {"owned_string_ascii_nul_shape_roundtrip": 107}),
    8: ("scalar3C", {"scalar4_roundtrip": 17}),
    9: ("scalar40", {"scalar4_roundtrip": 14}),
    10: ("sound", {"owned_string_ascii_nul_shape_roundtrip": 79, "three_scalar4_roundtrip": 7}),
    11: ("scalar44", {"scalar4_roundtrip": 6}),
    12: ("scalar4C", {"scalar4_roundtrip": 80}),
    13: ("scalar48", {"scalar4_roundtrip": 15}),
    15: ("waterSound", {"owned_string_ascii_nul_shape_roundtrip": 7}),
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
    "runtime explosion behavior proven",
    "runtime explosion damage proven",
    "runtime explosion visual effect proven",
    "runtime explosion audio proven",
    "serialized physicsscript completeness proven",
    "exact explosion record layout proven",
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
    require(schema == fresh, "tracked schema differs from fresh explosion fixture report", failures)
    require(read_json(SELECTION_SCHEMA) == selection_tool.build_report(), "tracked fixture-selection schema differs from fresh selection report", failures)

    require(schema["schemaVersion"] == "physics-script-explosion-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "explosion", "selected family mismatch", failures)
    require(schema["selectedFixturePath"] == SELECTED_PATH, "selected path mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = schema["fixtureAccounting"]
    expected_counts = {
        "sourceProofCount": 5,
        "sourceSchemaCount": 4,
        "sourceMirrorPairCount": 10,
        "selectedCandidateRank": 1,
        "selectedSourceProofCount": 4,
        "selectedValueInterfaceRowCount": 14,
        "selectedValueIdCount": 14,
        "selectedObservedValueIdCount": 14,
        "selectedFactoryOnlyValueIdCount": 0,
        "selectedUnselectedObservedValueIdCount": 0,
        "selectedTopLevelRecordCount": 118,
        "selectedValueNodeCount": 869,
        "selectedRawValuePayloadBytesPreserved": 14616,
        "selectedDeclaredPayloadBytes": 27335,
        "selectedOwnedStringFieldCount": 7,
        "selectedScalarFieldCount": 7,
        "selectedFixtureRowCount": 14,
        "selectedPayloadShapeCaseCount": 15,
        "selectedObservedPayloadShapeClassCount": 3,
        "selectedScalar4ShapePayloadCount": 330,
        "selectedOwnedStringShapePayloadCount": 532,
        "selectedThreeScalarShapePayloadCount": 7,
        "selectedMixedPayloadShapeValueIdCount": 1,
        "selectedCrosswalkOwnedStringCorpusCount": 539,
        "selectedCrosswalkScalarCorpusCount": 330,
        "soundObservedOwnedStringShapeCount": 79,
        "soundObservedThreeScalarShapeCount": 7,
        "deferredFactoryValueIdCount": 1,
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
    require(accounting["selectedMixedPayloadShapeValueIds"] == [10], "mixed shape value ids mismatch", failures)
    require(accounting["deferredFactoryValueIds"] == [14], "deferred factory ids mismatch", failures)

    source = schema["sourceEvidence"]
    require(source["fixtureSelection"]["fixtureSelectionStatus"] == "physics-script-rebuild-fixture-selection-complete-explosion-selected", "source fixture-selection status mismatch", failures)
    require(source["valueIdCrosswalk"]["deferredFactoryValueIds"] == [14], "source deferred factory ids mismatch", failures)
    require(source["scalarStringFixture"]["observedExplosionPayloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 532,
        "scalar4_roundtrip": 330,
        "three_scalar4_roundtrip": 7,
    }, "source observed shape totals mismatch", failures)

    selected = schema["selectedFixture"]
    require(selected["family"] == "explosion", "selected fixture family mismatch", failures)
    require(selected["pathId"] == SELECTED_PATH, "selected fixture path mismatch", failures)
    require(selected["statementFamilyTypeId"] == 6, "statement family id mismatch", failures)
    require(selected["valueFactoryTypeId"] == 7, "value factory id mismatch", failures)
    require(selected["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType7", "nested factory mismatch", failures)
    require(selected["statementLoader"] == "CExplosionStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(selected["valueListLoader"] == "CPhysicsExplosionValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(selected["createAnchor"] == "CExplosionStatement__CreateExplosionAndRecurse", "create anchor mismatch", failures)
    require(selected["registryGlobal"] == "DAT_008553f8", "registry mismatch", failures)
    require(selected["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(selected["ownedStringFields"] == ["basedOn", "airEffect", "groundEffect", "waterEffect", "unitEffect", "sound", "waterSound"], "owned string fields mismatch", failures)
    require(selected["scalarFields"] == ["scalar34", "scalar38", "scalar3C", "scalar40", "scalar44", "scalar4C", "scalar48"], "scalar fields mismatch", failures)
    require(selected["payloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 532,
        "scalar4_roundtrip": 330,
        "three_scalar4_roundtrip": 7,
    }, "selected shape totals mismatch", failures)
    require(selected["deferredFactoryBoundary"]["valueIds"] == [14], "deferred boundary ids mismatch", failures)
    require(selected["deferredFactoryBoundary"]["runtimeMeaningProven"] is False, "deferred runtime boundary mismatch", failures)

    rows = {row["valueId"]: row for row in selected["fixtureRows"]}
    require(set(rows) == set(EXPECTED_VALUE_IDS), "fixture rows value-id set mismatch", failures)
    for value_id, (field_name, shapes) in EXPECTED_VALUE_ROWS.items():
        row = rows.get(value_id)
        require(row is not None, f"missing fixture row {value_id}", failures)
        if row is None:
            continue
        require(row["rebuildFacingFieldName"] == field_name, f"field mismatch for value id {value_id}", failures)
        require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value id {value_id}", failures)
        require(row["publicSafe"] is True, f"public-safe mismatch for value id {value_id}", failures)
        require(row["fixtureAssertion"] == "public-safe static selected value-id interface row; no raw payload publication", f"assertion mismatch for value id {value_id}", failures)
    require(rows[10]["mixedPayloadShapeBoundary"] is True, "sound mixed-shape boundary missing", failures)
    for value_id, row in rows.items():
        if value_id != 10:
            require(row["mixedPayloadShapeBoundary"] is False, f"unexpected mixed boundary for value id {value_id}", failures)

    requirement_rows = {row["row"]: row["status"] for row in schema["fixtureRequirementRows"]}
    require(requirement_rows == {
        "family-fixture": "satisfied-static",
        "loader-fixture": "satisfied-static",
        "value-interface-fixture": "satisfied-static",
        "payload-shape-fixture": "satisfied-public-safe",
        "based-on-fixture": "satisfied-static",
        "stop-fixture": "enforced",
    }, "fixture requirement rows mismatch", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"guard should be false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"counter should be zero: {key}", failures)
    require(schema["publicSafety"]["publicLeakCheck"] == "PASS", "public safety mismatch", failures)
    require(schema["publicSafety"]["rawBytesEmitted"] is False, "raw bytes emitted flag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "physics-script-explosion-rebuild-fixture-proof-plan.v1.json",
        f"explosionFixtureStatus={STATUS_TOKEN}",
        "fixtureStatus=physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof",
        "selectedFixtureFamily=explosion",
        f"selectedFixturePath={SELECTED_PATH}",
        "selectedNextSlice=PhysicsScript Spawner Rebuild Fixture Proof Plan",
        "selectedNextScope=physics-script-spawner-rebuild-fixture-proof-plan",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=4",
        "selectedValueInterfaceRowCount=14",
        "selectedValueIdCount=14",
        "selectedObservedValueIdCount=14",
        "selectedFactoryOnlyValueIdCount=0",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedTopLevelRecordCount=118",
        "selectedValueNodeCount=869",
        "selectedRawValuePayloadBytesPreserved=14616",
        "selectedDeclaredPayloadBytes=27335",
        "selectedOwnedStringFieldCount=7",
        "selectedScalarFieldCount=7",
        "selectedFixtureRowCount=14",
        "selectedPayloadShapeCaseCount=15",
        "selectedObservedPayloadShapeClassCount=3",
        "selectedScalar4ShapePayloadCount=330",
        "selectedOwnedStringShapePayloadCount=532",
        "selectedThreeScalarShapePayloadCount=7",
        "selectedMixedPayloadShapeValueIdCount=1",
        "selectedMixedPayloadShapeValueIds=10",
        "selectedCrosswalkOwnedStringCorpusCount=539",
        "selectedCrosswalkScalarCorpusCount=330",
        "soundObservedOwnedStringShapeCount=79",
        "soundObservedThreeScalarShapeCount=7",
        "deferredFactoryValueIdCount=1",
        "deferredFactoryValueIds=14",
        "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15",
        "ownedStringFields=basedOn/airEffect/groundEffect/waterEffect/unitEffect/sound/waterSound",
        "scalarFields=scalar34/scalar38/scalar3C/scalar40/scalar44/scalar4C/scalar48",
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
        "runtimeExplosionBehaviorProven=false",
        "runtimeExplosionDamageProven=false",
        "runtimeExplosionVisualEffectProven=false",
        "runtimeExplosionAudioProven=false",
        "serializedPhysicsScriptCompletenessProven=false",
        "completeValueIdSemanticsProven=false",
        "rawStringIdentityProven=false",
        "rawNumericMeaningProven=false",
        "runtimeObservationRows=0",
        "physicsScriptRuntimeEvidenceRows=0",
        "runtimePhysicsScriptRows=0",
        "runtimeExplosionRows=0",
        "CPhysicsScriptStatements__CreateStatementType7",
        "CExplosionStatement__LoadFromMemBuffer",
        "CPhysicsExplosionValueList__LoadFromMemBuffer",
        "CExplosionStatement__CreateExplosionAndRecurse",
        "CExplosionBasedOn__ApplyToExplosionByName",
        "CExplosionValue__ApplyToExplosionByName",
        "DAT_008553f8",
        "family-fixture",
        "loader-fixture",
        "value-interface-fixture",
        "payload-shape-fixture",
        "based-on-fixture",
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
        "physics-script-explosion-rebuild-fixture-proof-plan.md",
        "physics-script-explosion-rebuild-fixture-proof-plan.v1.json",
        "selectedNextSlice=PhysicsScript Spawner Rebuild Fixture Proof Plan",
        "selectedFixtureFamily=explosion",
        "selectedFixturePath=explosion-selected-value-id-interface-static-fixture",
        "selectedValueInterfaceRowCount=14",
        "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15",
        "selectedFactoryOnlyValueIdCount=0",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedPayloadShapeCaseCount=15",
        "selectedMixedPayloadShapeValueIds=10",
        "soundObservedOwnedStringShapeCount=79",
        "soundObservedThreeScalarShapeCount=7",
        "deferredFactoryValueIds=14",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, SELECTION_PLAN):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed explosion fixture lane", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks explosion fixture active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed spawner fixture lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks spawner fixture active", failures)
    require(f"Completed {COMPLETED_ROUND_SLICE}" in backlog, "backlog missing completed round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROUND_SLICE}. Status: selected" not in backlog, "backlog still marks round fixture active", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript fixture-family completion rollup lane", failures)

    for source, mirror in LORE_FILES:
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-explosion-rebuild-fixture-proof-plan")
        == r"py -3 tools\physics_script_explosion_rebuild_fixture_proof_plan_probe.py --check",
        "missing package explosion fixture probe script",
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
        require(no_bea_process_running(), "BEA.exe process is running after explosion fixture probe", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript explosion rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript explosion rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
