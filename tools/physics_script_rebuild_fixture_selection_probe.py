#!/usr/bin/env python3
"""Validate the PhysicsScript rebuild fixture-selection proof."""

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

import physics_script_rebuild_fixture_selection as selection_tool  # noqa: E402
import physics_script_rebuild_interface_rollup as rollup_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_rebuild_fixture_selection_2026-06-10.md"
ROLLUP_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.md"
ROLLUP_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.v1.json"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-fixture-selection.v1.json"),
    (ROLLUP_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.md"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
)

THIS_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
PREVIOUS_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
NEXT_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
COMPLETED_SPAWNER_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "physics-script-rebuild-fixture-selection-complete-explosion-selected"
SELECTED_PATH = "explosion-selected-value-id-interface-static-fixture"
ROLLUP_STATUS = "physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof"
EXPECTED_VALUE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]

FALSE_GUARDS = selection_tool.FALSE_GUARDS
ZERO_COUNTERS = selection_tool.ZERO_COUNTERS

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
    fresh = selection_tool.build_report()
    require(schema == fresh, "tracked schema differs from fresh fixture-selection report", failures)
    require(read_json(ROLLUP_SCHEMA) == rollup_tool.build_report(), "tracked rollup schema differs from fresh rollup report", failures)

    require(schema["schemaVersion"] == "physics-script-rebuild-fixture-selection.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["fixtureSelectionStatus"] == STATUS_TOKEN, "fixture selection status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(schema["selectedChildScope"] == "physics-script-explosion-rebuild-fixture-proof-plan", "selected scope mismatch", failures)
    require(schema["selectedFixtureFamily"] == "explosion", "selected family mismatch", failures)
    require(schema["selectedFixturePath"] == SELECTED_PATH, "selected path mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = schema["selectionAccounting"]
    expected_counts = {
        "candidateFamilyCount": 9,
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
        "selectedPayloadClassCount": 2,
        "sourceProofCount": 5,
        "sourceSchemaCount": 3,
        "sourceMirrorPairCount": 8,
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
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(accounting[key] == expected, f"selection accounting mismatch: {key}", failures)
    require(accounting["physicsScriptStreamHeader"] == "0x12", "stream header mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(accounting["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class accounting mismatch", failures)

    rollup = schema["sourceEvidence"]["rollup"]
    require(rollup["rollupStatus"] == ROLLUP_STATUS, "source rollup status mismatch", failures)
    require(rollup["recommendedNextFixtureFamily"] == "explosion", "source recommended fixture mismatch", failures)
    require(rollup["valueInterfaceRowCount"] == 87, "source value interface count mismatch", failures)
    require(rollup["unselectedObservedRowCount"] == 113, "source unselected count mismatch", failures)

    crosswalk = schema["sourceEvidence"]["valueIdCrosswalk"]
    require(crosswalk["observedValueIdCount"] == 14, "explosion observed coverage mismatch", failures)
    require(crosswalk["selectedCrosswalkRowCount"] == 14, "explosion selected coverage mismatch", failures)
    require(crosswalk["observedSelectedValueIdCount"] == 14, "explosion observed selected mismatch", failures)
    require(crosswalk["factoryOnlySelectedValueIdCount"] == 0, "explosion factory-only mismatch", failures)
    require(crosswalk["unselectedObservedValueIdCount"] == 0, "explosion unselected mismatch", failures)

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
    require(selected["valueIdHexes"] == ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7", "0x8", "0x9", "0xa", "0xb", "0xc", "0xd", "0xf"], "selected value hex ids mismatch", failures)
    require(len(selected["valueRows"]) == 14, "selected value row count mismatch", failures)
    require(selected["payloadClassBreakdown"]["owned_string_at_08"] == {"fieldCount": 7, "copiedCorpusCount": 539}, "owned-string breakdown mismatch", failures)
    require(selected["payloadClassBreakdown"]["scalar4"] == {"fieldCount": 7, "copiedCorpusCount": 330}, "scalar breakdown mismatch", failures)
    require(selected["ownedStringFields"] == ["basedOn", "airEffect", "groundEffect", "waterEffect", "unitEffect", "sound", "waterSound"], "owned string field list mismatch", failures)
    require(selected["scalarFields"] == ["scalar34", "scalar38", "scalar3C", "scalar40", "scalar44", "scalar4C", "scalar48"], "scalar field list mismatch", failures)
    for row in selected["valueRows"]:
        require(row["family"] == "explosion", f"non-explosion selected row: {row}", failures)
        require(row["corpusPresence"] == "copied_corpus_observed", f"non-observed selected row: {row}", failures)
        require(row["publicSafe"] is True, f"non-public-safe selected row: {row}", failures)

    ranking = schema["candidateRanking"]
    require(len(ranking) == 9, "candidate ranking count mismatch", failures)
    require(ranking[0]["family"] == "explosion" and ranking[0]["decision"] == "selected", "selected ranking mismatch", failures)
    require(ranking[-1]["family"] == "unit" and ranking[-1]["decision"] == "deferred", "unit deferral mismatch", failures)
    require(len(schema["futureEvidenceRequirements"]) == 6, "future evidence requirement count mismatch", failures)

    guards = schema["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)
    public = schema["publicSafety"]
    require(public["publicLeakCheck"] == "PASS", "public safety status mismatch", failures)
    for key in ("rawBytesEmitted", "rawCopiedStringsEmitted", "rawHashValuesEmitted", "rawNumericValuesEmitted", "absolutePrivatePathsEmitted", "privateArtifactLocatorsEmitted"):
        require(public[key] is False, f"public safety flag mismatch: {key}", failures)
    require("runtime explosion behavior" in schema["claimBoundary"]["doesNotProve"], "claim boundary missing runtime explosion behavior", failures)
    require("Explosion is the first selected PhysicsScript rebuild fixture family." in schema["claimBoundary"]["proves"], "claim boundary missing selection proof", failures)
    check_no_bad_public_content(SCHEMA, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "physics-script-rebuild-fixture-selection.v1.json",
        f"fixtureSelectionStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=explosion",
        f"selectedFixturePath={SELECTED_PATH}",
        "selectedChildLane=PhysicsScript Explosion Rebuild Fixture Proof Plan",
        "selectedCandidateRank=1",
        "candidateFamilyCount=9",
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
        "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15",
        "ownedStringFieldCorpusCount=539",
        "scalarFieldCorpusCount=330",
        "sourceProofCount=5",
        "sourceSchemaCount=3",
        "sourceMirrorPairCount=8",
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
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "runtimeExecution=false",
        "beLaunch=false",
        "screenshotCapture=false",
        "privateFrameReviewPerformed=false",
        "sourceSelectionProven=false",
        "godotWork=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "productUiWired=false",
        "rebuildImplementation=false",
        "completeValueIdSemanticsProven=false",
        "all185PairsSemanticallyNamed=false",
        "rawStringIdentityProven=false",
        "rawNumericMeaningProven=false",
        "runtimeExplosionBehaviorProven=false",
        "runtimeExplosionDamageProven=false",
        "runtimeExplosionVisualEffectProven=false",
        "runtimeExplosionAudioProven=false",
        "CPhysicsScriptStatements__CreateStatementType7",
        "CExplosionStatement__LoadFromMemBuffer",
        "CPhysicsExplosionValueList__LoadFromMemBuffer",
        "CExplosionStatement__CreateExplosionAndRecurse",
        "CExplosionBasedOn__ApplyToExplosionByName",
        "CExplosionValue__ApplyToExplosionByName",
        "DAT_008553f8",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physics-script-rebuild-fixture-selection.md",
        "physics-script-rebuild-fixture-selection.v1.json",
        "selectedFixtureFamily=explosion",
        "selectedChildLane=PhysicsScript Explosion Rebuild Fixture Proof Plan",
        "selectedValueInterfaceRowCount=14",
        "selectedFactoryOnlyValueIdCount=0",
        "selectedUnselectedObservedValueIdCount=0",
        "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15",
        f"falseGuardCount={len(FALSE_GUARDS)}",
        f"zeroCounterCount={len(ZERO_COUNTERS)}",
        "publicLeakCheck=PASS",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, ROLLUP_PLAN):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed fixture-selection slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks fixture-selection active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed explosion fixture lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks explosion fixture active", failures)
    require(f"Completed {COMPLETED_SPAWNER_SLICE}" in backlog, "backlog missing completed spawner fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_SPAWNER_SLICE}. Status: selected" not in backlog, "backlog still marks spawner fixture active", failures)
    require(f"Completed {COMPLETED_ROUND_SLICE}" in backlog, "backlog missing completed round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROUND_SLICE}. Status: selected" not in backlog, "backlog still marks round fixture active", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript fixture-family completion rollup lane", failures)

    for source, mirror in LORE_FILES:
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-rebuild-fixture-selection")
        == r"py -3 tools\physics_script_rebuild_fixture_selection_probe.py --check",
        "missing package fixture-selection probe script",
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
        require(no_bea_process_running(), "BEA.exe process is running after fixture selection", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript rebuild fixture-selection probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript rebuild fixture-selection probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
