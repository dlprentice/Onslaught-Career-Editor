#!/usr/bin/env python3
"""Validate the PhysicsScript feature rebuild fixture proof-plan artifacts."""

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

import physics_script_feature_rebuild_fixture_proof_plan as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-feature-rebuild-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-feature-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_feature_rebuild_fixture_proof_plan_2026-06-10.md"
HAZARD_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-hazard-rebuild-fixture-proof-plan.md"
SELECTION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-feature-rebuild-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-feature-rebuild-fixture-proof-plan.v1.json"),
    (HAZARD_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-hazard-rebuild-fixture-proof-plan.md"),
    (SELECTION_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Feature Rebuild Fixture Proof Plan"
THIS_SCOPE = "physics-script-feature-rebuild-fixture-proof-plan"
STATUS_TOKEN = "physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Hazard Rebuild Fixture Proof Plan"
NEXT_SLICE = "PhysicsScript Component Rebuild Fixture Proof Plan"
NEXT_SCOPE = "physics-script-component-rebuild-fixture-proof-plan"
ACTIVE_AFTER_COMPONENT_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
SELECTED_PATH = "feature-selected-value-id-interface-static-fixture"
EXPECTED_VALUE_IDS = [1, 2, 3, 4, 5, 6, 7]
EXPECTED_OBSERVED_VALUE_IDS = [1, 2, 3, 4, 6]
EXPECTED_FACTORY_ONLY_VALUE_IDS = [5, 7]

EXPECTED_VALUE_ROWS = {
    1: ("scalar18", {"scalar4_roundtrip": 25}, False, False),
    2: ("mesh", {"owned_string_ascii_nul_shape_roundtrip": 40, "three_scalar4_roundtrip": 2}, False, True),
    3: ("texture", {"owned_string_ascii_nul_shape_roundtrip": 26}, False, False),
    4: ("flag10", {"scalar4_roundtrip": 18}, False, False),
    5: ("noise", {}, True, False),
    6: ("flag14", {"scalar4_roundtrip": 2}, False, False),
    7: ("scalar1C", {}, True, False),
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
    "runtime feature behavior proven",
    "runtime feature mesh proven",
    "runtime feature texture proven",
    "runtime feature noise proven",
    "runtime feature flag behavior proven",
    "terrain/material behavior proven",
    "serialized physicsscript completeness proven",
    "exact feature record layout proven",
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
    require(schema == fresh, "tracked schema differs from fresh feature fixture report", failures)

    require(schema["schemaVersion"] == "physics-script-feature-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "feature", "selected family mismatch", failures)
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
        "selectedCandidateRank": 4,
        "selectedSourceProofCount": 5,
        "selectedValueInterfaceRowCount": 7,
        "selectedValueIdCount": 7,
        "selectedObservedValueIdCount": 5,
        "selectedFactoryOnlyValueIdCount": 2,
        "selectedUnselectedObservedValueIdCount": 0,
        "selectedTopLevelRecordCount": 43,
        "selectedValueNodeCount": 113,
        "selectedRawValuePayloadBytesPreserved": 1375,
        "selectedDeclaredPayloadBytes": 3319,
        "selectedOwnedStringFieldCount": 3,
        "selectedScalarFieldCount": 2,
        "selectedFlagConstantTrueFieldCount": 0,
        "selectedFlagFromScalarNonzeroFieldCount": 2,
        "selectedFixtureRowCount": 7,
        "selectedObservedFixtureRowCount": 5,
        "selectedFactoryOnlyFixtureRowCount": 2,
        "selectedPayloadShapeCaseCount": 6,
        "selectedObservedPayloadShapeClassCount": 3,
        "selectedScalar4ShapePayloadCount": 45,
        "selectedOwnedStringShapePayloadCount": 66,
        "selectedThreeScalarShapePayloadCount": 2,
        "selectedMixedPayloadShapeValueIdCount": 1,
        "selectedCrosswalkOwnedStringCorpusCount": 68,
        "selectedCrosswalkScalarCorpusCount": 25,
        "selectedCrosswalkFlagConstantTrueCorpusCount": 0,
        "selectedCrosswalkFlagFromScalarNonzeroCorpusCount": 20,
        "meshObservedOwnedStringShapeCount": 40,
        "meshObservedThreeScalarShapeCount": 2,
        "factoryOnlyValueIdCount": 2,
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
    require(accounting["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "factory-only value ids mismatch", failures)
    require(accounting["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "observed value ids mismatch", failures)
    require(accounting["selectedMixedPayloadShapeValueIds"] == [2], "mixed payload value ids mismatch", failures)
    require(accounting["physicsScriptStreamHeader"] == "0x12", "stream header mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    fixture = schema["selectedFixture"]
    require(fixture["statementFamilyTypeId"] == 8, "statement family type mismatch", failures)
    require(fixture["valueFactoryTypeId"] == 8, "value factory type mismatch", failures)
    require(fixture["nestedFactory"] == "CPhysicsScriptStatements__CreateStatementType8", "nested factory mismatch", failures)
    require(fixture["statementLoader"] == "CFeatureStatement__LoadFromMemBuffer", "statement loader mismatch", failures)
    require(fixture["valueListLoader"] == "CPhysicsFeatureValueList__LoadFromMemBuffer", "value-list loader mismatch", failures)
    require(fixture["createAnchor"] == "CFeatureStatement__CreateFeatureAndRecurse", "create anchor mismatch", failures)
    require(fixture["registryGlobal"] == "DAT_00855404", "registry global mismatch", failures)
    require(fixture["valueIds"] == EXPECTED_VALUE_IDS, "selected value ids mismatch", failures)
    require(fixture["observedValueIds"] == EXPECTED_OBSERVED_VALUE_IDS, "fixture observed ids mismatch", failures)
    require(fixture["factoryOnlyValueIds"] == EXPECTED_FACTORY_ONLY_VALUE_IDS, "fixture factory-only ids mismatch", failures)
    require(fixture["ownedStringFields"] == ["mesh", "texture", "noise"], "owned string fields mismatch", failures)
    require(fixture["scalarFields"] == ["scalar18", "scalar1C"], "scalar fields mismatch", failures)
    require(fixture["flagFromScalarNonzeroFields"] == ["flag10", "flag14"], "flag fields mismatch", failures)

    rows = {row["valueId"]: row for row in fixture["fixtureRows"]}
    for value_id, (field, shapes, factory_only, mixed) in EXPECTED_VALUE_ROWS.items():
        row = rows.get(value_id)
        require(row is not None, f"missing fixture row {value_id}", failures)
        if row is not None:
            require(row["rebuildFacingFieldName"] == field, f"field mismatch for value id {value_id}", failures)
            require(row["observedPayloadShapeClasses"] == shapes, f"shape mismatch for value id {value_id}", failures)
            require(row["factoryOnlyBoundary"] is factory_only, f"factory-only mismatch for value id {value_id}", failures)
            require(row["mixedPayloadShapeBoundary"] is mixed, f"mixed-shape mismatch for value id {value_id}", failures)
            require(row["publicSafe"] is True, f"public safe mismatch for value id {value_id}", failures)

    requirement_rows = {row["row"]: row["status"] for row in schema["fixtureRequirementRows"]}
    require(requirement_rows == {
        "family-fixture": "satisfied-static-with-factory-only-boundary",
        "loader-fixture": "satisfied-static",
        "value-interface-fixture": "satisfied-static",
        "factory-only-boundary-fixture": "satisfied-explicit-boundary",
        "payload-shape-fixture": "satisfied-public-safe",
        "mesh-texture-noise-fixture": "satisfied-static",
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
        "physics-script-feature-rebuild-fixture-proof-plan.v1.json",
        f"featureFixtureStatus={STATUS_TOKEN}",
        f"fixtureStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=feature",
        f"selectedFixturePath={SELECTED_PATH}",
        "selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan",
        "selectedNextScope=physics-script-component-rebuild-fixture-proof-plan",
        "selectedCandidateRank=4",
        "selectedSourceProofCount=5",
        "selectedValueInterfaceRowCount=7",
        "selectedValueIdCount=7",
        "selectedObservedValueIdCount=5",
        "selectedFactoryOnlyValueIdCount=2",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedTopLevelRecordCount=43",
        "selectedValueNodeCount=113",
        "selectedRawValuePayloadBytesPreserved=1375",
        "selectedDeclaredPayloadBytes=3319",
        "selectedOwnedStringFieldCount=3",
        "selectedScalarFieldCount=2",
        "selectedFlagConstantTrueFieldCount=0",
        "selectedFlagFromScalarNonzeroFieldCount=2",
        "selectedFixtureRowCount=7",
        "selectedObservedFixtureRowCount=5",
        "selectedFactoryOnlyFixtureRowCount=2",
        "selectedPayloadShapeCaseCount=6",
        "selectedObservedPayloadShapeClassCount=3",
        "selectedScalar4ShapePayloadCount=45",
        "selectedOwnedStringShapePayloadCount=66",
        "selectedThreeScalarShapePayloadCount=2",
        "selectedMixedPayloadShapeValueIdCount=1",
        "selectedMixedPayloadShapeValueIds=2",
        "selectedCrosswalkOwnedStringCorpusCount=68",
        "selectedCrosswalkScalarCorpusCount=25",
        "selectedCrosswalkFlagConstantTrueCorpusCount=0",
        "selectedCrosswalkFlagFromScalarNonzeroCorpusCount=20",
        "meshObservedOwnedStringShapeCount=40",
        "meshObservedThreeScalarShapeCount=2",
        "factoryOnlyValueIdCount=2",
        "factoryOnlyValueIds=5/7",
        "observedValueIds=1/2/3/4/6",
        "selectedValueIds=1/2/3/4/5/6/7",
        "ownedStringFields=mesh/texture/noise",
        "scalarFields=scalar18/scalar1C",
        "flagConstantTrueFields=",
        "flagFromScalarNonzeroFields=flag10/flag14",
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
        "runtimeFeatureBehaviorProven=false",
        "runtimeFeatureMeshProven=false",
        "runtimeFeatureTextureProven=false",
        "runtimeFeatureNoiseProven=false",
        "runtimeFeatureFlagBehaviorProven=false",
        "serializedPhysicsScriptCompletenessProven=false",
        "completeValueIdSemanticsProven=false",
        "rawStringIdentityProven=false",
        "rawNumericMeaningProven=false",
        "runtimeObservationRows=0",
        "physicsScriptRuntimeEvidenceRows=0",
        "runtimePhysicsScriptRows=0",
        "runtimeFeatureRows=0",
        "runtimeFeatureMeshRows=0",
        "runtimeFeatureTextureRows=0",
        "runtimeFeatureNoiseRows=0",
        "runtimeFeatureFlagRows=0",
        "CPhysicsScriptStatements__CreateStatementType8",
        "CFeatureStatement__LoadFromMemBuffer",
        "CPhysicsFeatureValueList__LoadFromMemBuffer",
        "CFeatureStatement__CreateFeatureAndRecurse",
        "CFeatureMesh__ApplyToFeatureByName",
        "CFeatureTexture__ApplyToFeatureByName",
        "CFeatureNoise__ApplyToFeatureByName",
        "CFeatureFlag10__ApplyToFeatureByName",
        "CFeatureFlag14__ApplyToFeatureByName",
        "DAT_00855404",
        "factory-only-boundary-fixture",
        "mesh-texture-noise-fixture",
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
        "physics-script-feature-rebuild-fixture-proof-plan.md",
        "physics-script-feature-rebuild-fixture-proof-plan.v1.json",
        "selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan",
        "selectedFixtureFamily=feature",
        "selectedFixturePath=feature-selected-value-id-interface-static-fixture",
        "selectedValueInterfaceRowCount=7",
        "selectedObservedValueIdCount=5",
        "selectedFactoryOnlyValueIdCount=2",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedPayloadShapeCaseCount=6",
        "selectedMixedPayloadShapeValueIds=2",
        "factoryOnlyValueIds=5/7",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, HAZARD_PLAN, SELECTION_PLAN):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed feature fixture lane", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks feature fixture active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed component fixture lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks component fixture active", failures)
    require("Completed PhysicsScript Round Rebuild Fixture Proof Plan" in backlog, "backlog missing completed round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_AFTER_COMPONENT_SLICE}. Status: selected" not in backlog, "backlog still marks round fixture active", failures)
    require("Completed PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan" in backlog, "backlog missing completed weapon-mode fixture lane", failures)
    require("The selected active static-to-proof slice is PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan. Status: selected" not in backlog, "backlog still marks weapon-mode fixture active", failures)
    require("The selected active static-to-proof slice is Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan. Status: selected" in backlog, "backlog missing active post-PhysicsScript selection refresh lane", failures)

    for source, mirror in LORE_FILES:
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-feature-rebuild-fixture-proof-plan")
        == r"py -3 tools\physics_script_feature_rebuild_fixture_proof_plan_probe.py --check",
        "missing package feature fixture probe script",
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
        require(no_bea_process_running(), "BEA.exe process is running after feature fixture probe", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript feature rebuild fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript feature rebuild fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
