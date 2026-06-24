#!/usr/bin/env python3
"""Validate the PhysicsScript fixture-family completion rollup artifacts."""

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

import physics_script_fixture_family_completion_rollup_proof_plan as rollup_tool  # noqa: E402


PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_fixture_family_completion_rollup_proof_plan_2026-06-10.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PROOF, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.v1.json"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)game[\\/]+data[\\/]"), "private game data path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framesha256"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime physics outcomes proven",
    "runtime explosion behavior proven",
    "runtime spawner behavior proven",
    "runtime hazard behavior proven",
    "runtime feature behavior proven",
    "runtime component behavior proven",
    "runtime weapon behavior proven",
    "runtime round behavior proven",
    "runtime weapon-mode behavior proven",
    "runtime unit behavior proven",
    "serialized physicsscript completeness proven",
    "exact record layout proven",
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
    fresh = rollup_tool.build_report()
    require(schema == fresh, "tracked schema differs from fresh PhysicsScript fixture-family rollup report", failures)
    lore_schema = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-fixture-family-completion-rollup-proof-plan.v1.json"
    require(read_json(lore_schema) == schema, "lore schema mirror mismatch", failures)

    require(schema["schemaVersion"] == "physics-script-fixture-family-completion-rollup-proof-plan.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "schema status mismatch", failures)
    require(schema["proofPlan"] == rollup_tool.THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == rollup_tool.THIS_SCOPE, "scope mismatch", failures)
    require(schema["physicsScriptFixtureFamilyCompletionRollupStatus"] == rollup_tool.STATUS_TOKEN, "status token mismatch", failures)
    require(schema["previousSlice"] == rollup_tool.PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == rollup_tool.NEXT_SLICE, "selected next slice mismatch", failures)
    require(schema["selectedNextScope"] == rollup_tool.NEXT_SCOPE, "selected next scope mismatch", failures)

    accounting = schema["fixtureCompletionAccounting"]
    expected_counts = {
        "expectedFixtureFamilyCount": 9,
        "completedFixtureFamilyCount": 9,
        "remainingFixtureFamilyCount": 0,
        "fixturePlanDocCount": 9,
        "fixturePlanSchemaCount": 9,
        "fixtureProofPlanProbeCount": 9,
        "packageScriptCount": 9,
        "sourceProofCount": 9,
        "sourceSchemaCount": 9,
        "sourceMirrorPairCount": 18,
        "selectedValueInterfaceRowCount": 87,
        "selectedObservedValueIdCount": 72,
        "selectedFactoryOnlyValueIdCount": 15,
        "selectedUnselectedObservedValueIdCount": 113,
        "selectedTopLevelRecordCount": 777,
        "selectedValueNodeCount": 6803,
        "selectedPayloadShapeCaseCount": 85,
        "selectedScalar4ShapePayloadCount": 1151,
        "selectedOwnedStringShapePayloadCount": 1186,
        "selectedTwoScalarShapePayloadCount": 13,
        "selectedThreeScalarShapePayloadCount": 101,
        "selectedRawPreservedOtherShapePayloadCount": 259,
        "selectedRawValuePayloadBytesPreserved": 73796,
        "selectedDeclaredPayloadBytes": 151149,
        "factoryOnlyBoundaryFamilyCount": 6,
        "unselectedObservedBoundaryFamilyCount": 5,
        "mixedPayloadBoundaryFamilyCount": 7,
        "runtimeFamilyProofCount": 0,
        "runtimeObservationReadyFamilyCount": 0,
    }
    for key, expected in expected_counts.items():
        require(accounting[key] == expected, f"fixture completion accounting mismatch: {key}", failures)
    require(accounting["allSourceMirrorsMatch"] is True, "source mirror accounting mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(accounting["selectedPayloadShapeTotals"] == {
        "owned_string_ascii_nul_shape_roundtrip": 1186,
        "raw_preserved_other": 259,
        "scalar4_roundtrip": 1151,
        "three_scalar4_roundtrip": 101,
        "two_scalar4_roundtrip": 13,
    }, "payload shape totals mismatch", failures)

    cross = schema["rollupCrossCheck"]
    cross_expected = {
        "topLevelFamilyCount": 9,
        "valueInterfaceRowCount": 87,
        "observedSelectedRowCount": 72,
        "factoryOnlySelectedRowCount": 15,
        "unselectedObservedRowCount": 113,
        "physicsScriptTopLevelStatementCount": 777,
        "physicsScriptValueListNodeCount": 6803,
        "physicsScriptStatementValuePairCount": 185,
        "physicsScriptRawValuePayloadBytesPreserved": 73796,
        "fixtureAggregateClassCount": 5,
        "semanticBucketCount": 10,
    }
    for key, expected in cross_expected.items():
        require(cross[key] == expected, f"rollup cross-check mismatch: {key}", failures)
    require(cross["completeValueIdSemanticsProven"] is False, "complete semantics guard mismatch", failures)
    require(cross["all185PairsSemanticallyNamed"] is False, "all-185 semantics guard mismatch", failures)

    expected_families = ["explosion", "spawner", "hazard", "feature", "component", "weapon", "round", "weapon-mode", "unit"]
    rows = schema["familyCompletionRows"]
    require([row["fixtureFamily"] for row in rows] == expected_families, "family row order mismatch", failures)
    for row in rows:
        require(row["fixtureStatus"].endswith("not-runtime-proof"), f"family status boundary mismatch: {row['fixtureFamily']}", failures)
        require(row["selectedNextSlice"] == row["expectedNextSlice"], f"next-slice chain mismatch: {row['fixtureFamily']}", failures)
        require(row["proofMirrorMatch"] is True, f"proof mirror mismatch in schema: {row['fixtureFamily']}", failures)
        require(row["schemaMirrorMatch"] is True, f"schema mirror mismatch in schema: {row['fixtureFamily']}", failures)
        require(row["runtimeExecution"] is False, f"runtime guard mismatch: {row['fixtureFamily']}", failures)
        require(row["godotWork"] is False, f"Godot guard mismatch: {row['fixtureFamily']}", failures)
        require(row["ghidraMutation"] is False, f"Ghidra guard mismatch: {row['fixtureFamily']}", failures)
        require(row["rebuildImplementation"] is False, f"rebuild guard mismatch: {row['fixtureFamily']}", failures)

    for key, value in schema["guardSummary"]["falseGuards"].items():
        require(value is False, f"false guard not false: {key}", failures)
    for key, value in schema["guardSummary"]["zeroCounters"].items():
        require(value == 0, f"zero counter not zero: {key}", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        rollup_tool.THIS_SLICE,
        rollup_tool.PREVIOUS_SLICE,
        rollup_tool.NEXT_SLICE,
        "physics-script-fixture-family-completion-rollup-proof-plan.v1.json",
        f"physicsScriptFixtureFamilyCompletionRollupStatus={rollup_tool.STATUS_TOKEN}",
        "expectedFixtureFamilyCount=9",
        "completedFixtureFamilyCount=9",
        "remainingFixtureFamilyCount=0",
        "fixturePlanDocCount=9",
        "fixturePlanSchemaCount=9",
        "fixtureProofPlanProbeCount=9",
        "sourceMirrorPairCount=18",
        "selectedValueInterfaceRowCount=87",
        "selectedObservedValueIdCount=72",
        "selectedFactoryOnlyValueIdCount=15",
        "selectedUnselectedObservedValueIdCount=113",
        "selectedTopLevelRecordCount=777",
        "selectedValueNodeCount=6803",
        "selectedPayloadShapeCaseCount=85",
        "selectedScalar4ShapePayloadCount=1151",
        "selectedOwnedStringShapePayloadCount=1186",
        "selectedTwoScalarShapePayloadCount=13",
        "selectedThreeScalarShapePayloadCount=101",
        "selectedRawPreservedOtherShapePayloadCount=259",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
        "factoryOnlyBoundaryFamilyCount=6",
        "unselectedObservedBoundaryFamilyCount=5",
        "mixedPayloadBoundaryFamilyCount=7",
        "publicLeakCheck=PASS",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "explosion, spawner, hazard, feature, component, weapon, round, weapon-mode, and unit",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)
    check_no_bad_public_content(SCHEMA, failures)

    front_tokens = (
        rollup_tool.THIS_SLICE,
        rollup_tool.NEXT_SLICE,
        "physics-script-fixture-family-completion-rollup-proof-plan.md",
        "physics-script-fixture-family-completion-rollup-proof-plan.v1.json",
        rollup_tool.STATUS_TOKEN,
        "completedFixtureFamilyCount=9",
        "remainingFixtureFamilyCount=0",
        "selectedValueInterfaceRowCount=87",
        "selectedObservedValueIdCount=72",
        "selectedFactoryOnlyValueIdCount=15",
        "selectedUnselectedObservedValueIdCount=113",
        "selectedPayloadShapeCaseCount=85",
        "physicsScriptTopLevelStatementCount=777",
        "physicsScriptValueListNodeCount=6803",
        "physicsScriptStatementValuePairCount=185",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT):
        text = read_text(path)
        for token in front_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {rollup_tool.THIS_SLICE}" in backlog, "backlog missing completed PhysicsScript fixture-family rollup", failures)
    require(f"The selected active static-to-proof slice is {rollup_tool.THIS_SLICE}. Status: selected" not in backlog, "backlog still marks rollup active", failures)
    require(f"Completed {rollup_tool.NEXT_SLICE}" in backlog, "backlog missing completed post-PhysicsScript selection refresh", failures)
    require(f"The selected active static-to-proof slice is {rollup_tool.NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks post-PhysicsScript selection refresh active", failures)
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan. Status: selected" in backlog,
        "backlog missing active texture/mesh material sidecar contract extension lane",
        failures,
    )

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-fixture-family-completion-rollup-proof-plan")
        == r"py -3 tools\physics_script_fixture_family_completion_rollup_proof_plan_probe.py --check",
        "missing package fixture-family rollup probe script",
        failures,
    )
    for row in rollup_tool.FAMILY_ROWS:
        require(row["script"] in package.get("scripts", {}), f"missing source family package script: {row['script']}", failures)

    for source, mirror in LORE_FILES:
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(source) == read_text(mirror), f"lore mirror differs: {mirror.relative_to(ROOT)}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        check_schema(failures)
        check_docs(failures)
        require(no_bea_process_running(), "BEA process is running after PhysicsScript fixture-family rollup", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript fixture-family completion rollup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript fixture-family completion rollup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
