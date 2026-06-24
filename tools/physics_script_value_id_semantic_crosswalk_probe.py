#!/usr/bin/env python3
"""Validate the PhysicsScript value-id semantic crosswalk proof."""

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

import physics_script_value_id_semantic_crosswalk as crosswalk_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_value_id_semantic_crosswalk_2026-06-10.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PHYSICS_PARSER = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
SCALAR_FIXTURE = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-scalar-string-value-decoder-fixture-proof-plan.md"
SEMANTIC_LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger-proof-plan.md"
FUNCTION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PACKAGE_JSON = ROOT / "package.json"

FACTORY_DECOMPILES = (
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "00431bb0_CPhysicsScriptStatements__CreateStatementType2.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "00434300_CPhysicsScriptStatements__CreateStatementType3.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "00435010_CPhysicsScriptStatements__CreateStatementType4.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "00437490_CPhysicsScriptStatements__CreateStatementType5.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "00439b40_CPhysicsScriptStatements__CreateStatementType6.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "0043a860_CPhysicsScriptStatements__CreateStatementType7.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "0043b990_CPhysicsScriptStatements__CreateStatementType8.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "0043c0b0_CPhysicsScriptStatements__CreateStatementType9.c",
    ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review" / "decompile" / "0043c500_CPhysicsScriptStatements__CreateStatementType10.c",
)

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk.v1.json"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
    (PHYSICS_PARSER, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"),
)

THIS_SLICE = "PhysicsScript Value-ID Semantic Crosswalk Proof Plan"
THIS_SCOPE = "physics-script-value-id-semantic-crosswalk-proof-plan"
STATUS_TOKEN = "physics-script-value-id-semantic-crosswalk-complete-bounded-static-crosswalk-not-runtime-proof"
NEXT_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
CURRENT_ACTIVE_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
COMPLETED_EXPLOSION_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
COMPLETED_SPAWNER_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"

EXPECTED_FAMILY_ROWS = {
    "component": (20, 20, 16, 4, 4),
    "explosion": (14, 14, 14, 0, 0),
    "feature": (5, 7, 5, 2, 0),
    "hazard": (3, 4, 3, 1, 0),
    "round": (33, 7, 7, 0, 26),
    "spawner": (10, 14, 10, 4, 0),
    "unit": (54, 8, 6, 2, 48),
    "weapon": (14, 4, 4, 0, 10),
    "weapon-mode": (32, 9, 7, 2, 25),
}

FALSE_GUARDS = (
    "runtimeExecution",
    "beLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsOutcomesProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "completeValueIdSemanticsProven",
    "completeNestedEnumSemanticsProven",
    "rawStringIdentityProven",
    "rawNumericMeaningProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "runtimeCommandEffectRows",
    "privateFrameRowsObserved",
    "ghidraMutationRows",
    "executablePatchRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterCrosswalk",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)framehash|framesha256|capturehash|capturepath|framepath"), "private frame locator/hash field"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime physics outcomes proven",
    "serialized physicsscript completeness proven",
    "serialized physics-script completeness proven",
    "exact concrete record layouts proven",
    "complete value-id semantics proven",
    "all 185 pairs semantically named",
    "complete nested enum semantics proven",
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


def check_schema(failures: list[str]) -> None:
    schema = read_json(SCHEMA)
    fresh = crosswalk_tool.build_report()
    require(schema == fresh, "tracked schema differs from fresh crosswalk report", failures)

    require(schema["schemaVersion"] == "physics-script-value-id-semantic-crosswalk.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "schema status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["crosswalkStatus"] == STATUS_TOKEN, "crosswalk status mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)

    coverage = schema["coverageSummary"]
    require(coverage["familyCount"] == 9, "family count mismatch", failures)
    require(coverage["copiedCorpusUniqueStatementValuePairCount"] == 185, "unique statement/value pair count mismatch", failures)
    require(coverage["boundedCrosswalkRowCount"] == 87, "bounded crosswalk row count mismatch", failures)
    require(coverage["copiedCorpusObservedSelectedRowCount"] == 72, "observed selected row count mismatch", failures)
    require(coverage["factoryOnlySelectedRowCount"] == 15, "factory-only selected row count mismatch", failures)
    for key in ("allObservedPairsAccountedByCountMap", "allSelectedRowsHaveFactoryAnchors", "allSelectedRowsHaveApplyAnchors"):
        require(coverage[key] is True, f"coverage true flag mismatch: {key}", failures)
    for key in ("completeValueIdSemanticsProven", "all185PairsSemanticallyNamed", "runtimeBehaviorProven", "rebuildImplementationComplete"):
        require(coverage[key] is False, f"coverage false flag mismatch: {key}", failures)

    family_summary = schema["familyCoverageSummary"]
    for family, (observed, selected, selected_observed, factory_only, unselected) in EXPECTED_FAMILY_ROWS.items():
        row = family_summary[family]
        require(row["observedValueIdCount"] == observed, f"{family} observed count mismatch", failures)
        require(row["selectedCrosswalkRowCount"] == selected, f"{family} selected count mismatch", failures)
        require(row["observedSelectedValueIdCount"] == selected_observed, f"{family} selected observed count mismatch", failures)
        require(row["factoryOnlySelectedValueIdCount"] == factory_only, f"{family} factory-only count mismatch", failures)
        require(row["unselectedObservedValueIdCount"] == unselected, f"{family} unselected observed count mismatch", failures)

    rows = schema["crosswalkRows"]
    require(len(rows) == 87, "crosswalk row list length mismatch", failures)
    require(sum(1 for row in rows if row["copiedCorpusCount"] > 0) == 72, "observed row tally mismatch", failures)
    require(sum(1 for row in rows if row["copiedCorpusCount"] == 0) == 15, "factory-only row tally mismatch", failures)
    for row in rows:
        for key in ("family", "statementFamilyTypeId", "valueFactoryTypeId", "valueId", "valueIdHex", "rebuildFacingFieldName", "factoryAnchor", "applyAnchor", "registryGlobal", "claimBoundary"):
            require(row.get(key) not in (None, ""), f"row missing field {key}: {row}", failures)
        require(row["publicSafe"] is True, f"row not public-safe: {row}", failures)

    expected_rows = {
        ("spawner", 1, "unitName"),
        ("spawner", 10, "basedOn"),
        ("explosion", 2, "airEffect"),
        ("explosion", 15, "waterSound"),
        ("feature", 3, "texture"),
        ("hazard", 4, "noise"),
        ("component", 20, "indexedScalar164"),
        ("component", 25, "vent"),
        ("round", 24, "gridOfFear"),
        ("round", 36, "mesh"),
        ("weapon-mode", 31, "launchAngle3"),
        ("weapon-mode", 36, "postFireSound"),
        ("weapon", 5, "iconName"),
        ("unit", 8, "behaviour"),
        ("unit", 61, "maxLegsLifted"),
    }
    actual_rows = {(row["family"], row["valueId"], row["rebuildFacingFieldName"]) for row in rows}
    require(expected_rows.issubset(actual_rows), f"missing expected crosswalk rows: {expected_rows - actual_rows}", failures)

    guards = schema["guardSummary"]
    require(guards["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guards["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"counter must be zero: {key}", failures)

    public = schema["publicSafety"]
    require(public["publicLeakCheck"] == "PASS", "public leak status mismatch", failures)
    for key in ("rawBytesEmitted", "rawNamesOrStringsEmitted", "rawHashValuesEmitted", "rawNumericValuesEmitted", "absolutePrivatePathsEmitted", "privateArtifactLocatorsEmitted"):
        require(public[key] is False, f"public safety must be false: {key}", failures)
    require("runtime PhysicsScript behavior" in schema["claimBoundary"]["doesNotProve"], "claim boundary missing runtime PhysicsScript behavior", failures)
    check_no_bad_public_content(SCHEMA, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        STATUS_TOKEN,
        "physics-script-value-id-semantic-crosswalk.v1.json",
        "PhysicsScript Rebuild Interface Rollup Proof Plan",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1179/1179 = 100.00%",
        "175603",
        "0x12",
        "777",
        "6803",
        "185",
        "87",
        "72",
        "15",
        "all185PairsSemanticallyNamed=false",
        "completeValueIdSemanticsProven=false",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "rawCopiedStringsEmitted=false",
        "rawNumericValuesEmitted=false",
        "CPhysicsScriptStatements__CreateStatementType6",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CSpawnerUnit__ApplyToSpawnerByName",
        "CExplosionBasedOn__ApplyToExplosionByName",
        "CComponentIndexedScalar164__ApplyToComponentByName",
        "CRoundGridOfFear__ApplyToRoundByName",
        "CWeaponVolleySize__ApplyToWeaponModeByName",
        "CUnitBehaviour__ApplyToUnitData",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physics-script-value-id-semantic-crosswalk-proof-plan.md",
        "physics-script-value-id-semantic-crosswalk.v1.json",
        "boundedCrosswalkRowCount=87",
        "observedSelectedRowCount=72",
        "factoryOnlySelectedRowCount=15",
        "all185PairsSemanticallyNamed=false",
        "completeValueIdSemanticsProven=false",
        "selectedNextSlice=PhysicsScript Rebuild Interface Rollup Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, PHYSICS_PARSER, SCALAR_FIXTURE):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed value-id crosswalk slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks value-id crosswalk active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed rebuild interface rollup lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks rebuild interface rollup active", failures)
    require(f"Completed {CURRENT_ACTIVE_SLICE}" in backlog, "backlog missing completed rebuild fixture selection lane", failures)
    require(f"The selected active static-to-proof slice is {CURRENT_ACTIVE_SLICE}. Status: selected" not in backlog, "backlog still marks rebuild fixture selection active", failures)
    require(f"Completed {COMPLETED_EXPLOSION_SLICE}" in backlog, "backlog missing completed explosion fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_EXPLOSION_SLICE}. Status: selected" not in backlog, "backlog still marks explosion fixture active", failures)
    require(f"Completed {COMPLETED_SPAWNER_SLICE}" in backlog, "backlog missing completed spawner fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_SPAWNER_SLICE}. Status: selected" not in backlog, "backlog still marks spawner fixture active", failures)
    require(f"Completed {COMPLETED_ROUND_SLICE}" in backlog, "backlog missing completed round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROUND_SLICE}. Status: selected" not in backlog, "backlog still marks round fixture active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript fixture-family completion rollup lane", failures)

    for source, mirror in LORE_FILES:
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-value-id-semantic-crosswalk")
        == r"py -3 tools\physics_script_value_id_semantic_crosswalk_probe.py --check",
        "missing package value-id crosswalk probe script",
        failures,
    )


def check_source_anchors(failures: list[str]) -> None:
    combined_public = "\n".join(read_text(path) for path in (PHYSICS_CONTRACT, PHYSICS_PARSER, SCALAR_FIXTURE, SEMANTIC_LEDGER, FUNCTION_DOC))
    for token in (
        "CPhysicsScriptStatements__CreateStatementType2",
        "CPhysicsScriptStatements__CreateStatementType3",
        "CPhysicsScriptStatements__CreateStatementType4",
        "CPhysicsScriptStatements__CreateStatementType5",
        "CPhysicsScriptStatements__CreateStatementType6",
        "CPhysicsScriptStatements__CreateStatementType7",
        "CPhysicsScriptStatements__CreateStatementType8",
        "CPhysicsScriptStatements__CreateStatementType9",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CSpawnerBasedOn__ApplyToSpawnerByName",
        "CSpawnerUnit__ApplyToSpawnerByName",
        "CExplosionBasedOn__ApplyToExplosionByName",
        "CFeatureTexture__ApplyToFeatureByName",
        "CHazardEffect__ApplyToHazardByName",
        "CComponentBasedOn__ApplyToComponentByName",
        "CComponentIndexedScalar164__ApplyToComponentByName",
        "CRoundGridOfFear__ApplyToRoundByName",
        "CWeaponVolleySize__ApplyToWeaponModeByName",
        "CUnitBehaviour__ApplyToUnitData",
        "Value-list nodes | `6803`",
        "Unique statement/value id pairs | `185`",
    ):
        require(token in combined_public, f"missing source/static anchor: {token}", failures)

    combined_decompiles = "\n".join(read_text(path) for path in FACTORY_DECOMPILES)
    for token in (
        "switch(valueType)",
        "case 0xe:",
        "case 0x19:",
        "case 0x24:",
        "case 0x3d:",
        "CPhysicsScriptStatements__CreateStatementType6",
        "CPhysicsScriptStatements__CreateStatementType10",
    ):
        require(token in combined_decompiles, f"missing factory decompile anchor: {token}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        check_schema(failures)
        check_docs(failures)
        check_source_anchors(failures)
        require(no_bea_process_running(), "BEA process still running after value-id crosswalk probe", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript value-id semantic crosswalk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript value-id semantic crosswalk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
