#!/usr/bin/env python3
"""Validate the PhysicsScript rebuild-interface rollup proof."""

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

import physics_script_rebuild_interface_rollup as rollup_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_rebuild_interface_rollup_2026-06-10.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
VALUE_CROSSWALK_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk-proof-plan.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-rebuild-interface-rollup.v1.json"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
    (VALUE_CROSSWALK_PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-value-id-semantic-crosswalk-proof-plan.md"),
)

THIS_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
THIS_SCOPE = "physics-script-rebuild-interface-rollup"
STATUS_TOKEN = "physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof"
PREVIOUS_SLICE = "PhysicsScript Value-ID Semantic Crosswalk Proof Plan"
NEXT_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
COMPLETED_EXPLOSION_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
COMPLETED_SPAWNER_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"

EXPECTED_FAMILY_COVERAGE = {
    "unit": (54, 8, 6, 2, 48),
    "weapon": (14, 4, 4, 0, 10),
    "weapon-mode": (32, 9, 7, 2, 25),
    "round": (33, 7, 7, 0, 26),
    "spawner": (10, 14, 10, 4, 0),
    "explosion": (14, 14, 14, 0, 0),
    "component": (20, 20, 16, 4, 4),
    "feature": (5, 7, 5, 2, 0),
    "hazard": (3, 4, 3, 1, 0),
}

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "livePhysicsScriptRuntimeLoading",
    "runtimeExecution",
    "runtimePhysicsScriptBehaviorProven",
    "runtimePhysicsScriptOutcomesProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "completeValueIdSemanticsProven",
    "all185PairsSemanticallyNamed",
    "completeNestedEnumSemanticsProven",
    "rawStringIdentityProven",
    "rawNumericMeaningProven",
    "rawCopiedStringsEmitted",
    "rawPayloadBytesPublished",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "sourceSelectionObserved",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "productUiWired",
    "rebuildImplementation",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "exactSourceBodyIdentityProven",
    "exactRecordLayoutProven",
    "exactRegistryContainerLayoutProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "runtimeCommandEffectRows",
    "physicsScriptRuntimeEvidenceRows",
    "runtimePhysicsScriptRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "godotRows",
    "rebuildImplementationRows",
    "beProcessesAfterRollup",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawCopiedStringRows",
    "rawNumericRowsPublished",
    "serializedCompletenessRows",
    "exactLayoutRows",
)

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
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256"), "private frame locator/hash field"),
)

FORBIDDEN_OVERCLAIMS = (
    "complete physicsscript interface",
    "complete physicsscript semantics",
    "complete value-id semantics proven",
    "all 185 pairs semantically named",
    "serialized physicsscript completeness proven",
    "exact concrete record layouts proven",
    "raw string identity proven",
    "raw numeric value meaning proven",
    "runtime physicsscript behavior proven",
    "runtime physics outcomes proven",
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
    require(schema == fresh, "tracked schema differs from fresh rollup report", failures)

    require(schema["schemaVersion"] == "physics-script-rebuild-interface-rollup.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["rollupStatus"] == STATUS_TOKEN, "rollup status mismatch", failures)
    require(schema["physicsScriptRebuildInterfaceRollupStatus"] == STATUS_TOKEN, "named status mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = schema["rollupAccounting"]
    expected_counts = {
        "selectedSourceProofCount": 5,
        "sourceProofCount": 5,
        "sourceSchemaCount": 3,
        "sourceMirrorPairCount": 8,
        "topLevelFamilyCount": 9,
        "semanticBucketCount": 10,
        "fixtureAggregateClassCount": 5,
        "fixtureClassDefinitionCount": 6,
        "syntheticFixtureCaseCount": 13,
        "interfaceRowCount": 9,
        "valueInterfaceRowCount": 87,
        "boundedCrosswalkRowCount": 87,
        "observedSelectedRowCount": 72,
        "factoryOnlySelectedRowCount": 15,
        "unselectedObservedRowCount": 113,
        "physicsScriptTopLevelStatementCount": 777,
        "physicsScriptValueListNodeCount": 6803,
        "physicsScriptStatementValuePairCount": 185,
        "physicsScriptRawValuePayloadBytesPreserved": 73796,
        "rollupTrueGuardCount": 7,
        "falseGuardCount": len(FALSE_GUARDS),
        "zeroCounterCount": len(ZERO_COUNTERS),
    }
    for key, expected in expected_counts.items():
        require(accounting[key] == expected, f"rollup accounting mismatch: {key}", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    source_accounting = schema["sourceSchemaAccounting"]
    require(source_accounting["sourceProofCount"] == 5, "source proof count mismatch", failures)
    require(source_accounting["sourceSchemaCount"] == 3, "source schema count mismatch", failures)
    require(source_accounting["sourceMirrorPairCount"] == 8, "source mirror count mismatch", failures)
    require(source_accounting["allSourceMirrorsMatch"] is True, "source mirror status mismatch", failures)

    corpus = schema["corpusCounts"]
    require(corpus["parsedCopiedCorpusFiles"] == 1, "parsed file count mismatch", failures)
    require(corpus["parsedCopiedFileName"] == "data/default physics.dat", "parsed file name mismatch", failures)
    require(corpus["parsedByteCount"] == 175603, "parsed byte count mismatch", failures)
    require(corpus["streamHeader"] == "0x12", "stream header mismatch", failures)
    require(corpus["topLevelStatementCount"] == 777, "top-level count mismatch", failures)
    require(corpus["valueListNodeCount"] == 6803, "value-list node count mismatch", failures)
    require(corpus["uniqueStatementValuePairCount"] == 185, "unique statement/value count mismatch", failures)
    require(corpus["rawValuePayloadBytesPreserved"] == 73796, "raw payload count mismatch", failures)
    require(corpus["continueMarkerCount"] == 6026, "continue marker count mismatch", failures)
    require(corpus["terminatingMarkerCount"] == 777, "terminating marker count mismatch", failures)

    family_rows = {row["family"]: row for row in schema["topLevelInterfaceRows"]}
    require(len(family_rows) == 9, "top-level interface row count mismatch", failures)
    for family, (observed, selected, observed_selected, factory_only, unselected) in EXPECTED_FAMILY_COVERAGE.items():
        row = family_rows[family]
        require(row["uniqueObservedValueIds"] == observed, f"{family} observed mismatch", failures)
        require(row["selectedCrosswalkRows"] == selected, f"{family} selected mismatch", failures)
        require(row["observedSelectedRows"] == observed_selected, f"{family} observed selected mismatch", failures)
        require(row["factoryOnlySelectedRows"] == factory_only, f"{family} factory-only mismatch", failures)
        require(row["unselectedObservedValueIdCount"] == unselected, f"{family} unselected mismatch", failures)
        for key in ("nestedFactory", "statementLoader", "valueListLoader", "createAnchor", "registryGlobal", "rebuildObligation"):
            require(row.get(key) not in (None, ""), f"{family} missing interface field: {key}", failures)

    fixture_counts = schema["payloadInterface"]["fixtureClassCounts"]
    require(fixture_counts["scalar4_roundtrip"] == 3912, "scalar4 fixture count mismatch", failures)
    require(fixture_counts["owned_string_ascii_nul_shape_roundtrip"] == 1737, "string fixture count mismatch", failures)
    require(fixture_counts["two_scalar4_roundtrip"] == 361, "two-scalar fixture count mismatch", failures)
    require(fixture_counts["three_scalar4_roundtrip"] == 132, "three-scalar fixture count mismatch", failures)
    require(fixture_counts["raw_preserved_other"] == 661, "raw-preserved fixture count mismatch", failures)
    require(len(schema["semanticBuckets"]) == 10, "semantic bucket count mismatch", failures)

    value_rows = schema["valueInterfaceRows"]
    require(len(value_rows) == 87, "value interface row count mismatch", failures)
    require(sum(1 for row in value_rows if row["copiedCorpusCount"] > 0) == 72, "observed value row count mismatch", failures)
    require(sum(1 for row in value_rows if row["copiedCorpusCount"] == 0) == 15, "factory-only value row count mismatch", failures)
    for row in value_rows:
        for key in ("family", "valueId", "rebuildFacingFieldName", "payloadClass", "semanticState", "factoryAnchor", "applyAnchor", "registryGlobal", "destinationField", "claimBoundary"):
            require(row.get(key) not in (None, ""), f"value row missing {key}: {row}", failures)
        require(row["publicSafe"] is True, f"value row not public-safe: {row}", failures)

    recommendation = schema["recommendedNextFixtureFamily"]
    require(recommendation["family"] == "explosion", "recommended next fixture family mismatch", failures)
    require(recommendation["observedValueIdCount"] == 14, "explosion observed mismatch", failures)
    require(recommendation["selectedCrosswalkRowCount"] == 14, "explosion selected mismatch", failures)
    require(recommendation["factoryOnlySelectedValueIdCount"] == 0, "explosion factory-only mismatch", failures)
    require(recommendation["unselectedObservedValueIdCount"] == 0, "explosion unselected mismatch", failures)

    guards = schema["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"counter must be zero: {key}", failures)
    public = schema["publicSafety"]
    require(public["publicLeakCheck"] == "PASS", "public safety status mismatch", failures)
    for key in ("rawBytesEmitted", "rawCopiedStringsEmitted", "rawHashValuesEmitted", "rawNumericValuesEmitted", "absolutePrivatePathsEmitted", "privateArtifactLocatorsEmitted"):
        require(public[key] is False, f"public safety flag mismatch: {key}", failures)
    check_no_bad_public_content(SCHEMA, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physicsScriptRebuildInterfaceRollupStatus=physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof",
        "physics-script-rebuild-interface-rollup.v1.json",
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1179/1179 = 100.00%",
        "selectedSourceProofCount=5",
        "sourceProofCount=5",
        "sourceSchemaCount=3",
        "sourceMirrorPairCount=8",
        "topLevelFamilyCount=9",
        "semanticBucketCount=10",
        "fixtureAggregateClassCount=5",
        "fixtureClassDefinitionCount=6",
        "syntheticFixtureCaseCount=13",
        "interfaceRowCount=9",
        "valueInterfaceRowCount=87",
        "boundedCrosswalkRowCount=87",
        "observedSelectedRowCount=72",
        "factoryOnlySelectedRowCount=15",
        "unselectedObservedRowCount=113",
        "physicsScriptTopLevelStatementCount=777",
        "physicsScriptValueListNodeCount=6803",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
        "falseGuardCount=34",
        "zeroCounterCount=19",
        "publicLeakCheck=PASS",
        "runtimeExecution=false",
        "beLaunch=false",
        "newLaunch=false",
        "godotWork=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "productUiWired=false",
        "rebuildImplementation=false",
        "completeValueIdSemanticsProven=false",
        "all185PairsSemanticallyNamed=false",
        "rawStringIdentityProven=false",
        "rawNumericMeaningProven=false",
        "CPhysicsScriptStatements__CreateStatementType7",
        "CExplosionStatement__LoadFromMemBuffer",
        "CExplosionBasedOn__ApplyToExplosionByName",
        "recommendedNextFixtureFamily=explosion",
        "observedValueIdCount=14",
        "selectedCrosswalkRowCount=14",
        "factoryOnlySelectedValueIdCount=0",
        "unselectedObservedValueIdCount=0",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physics-script-rebuild-interface-rollup.md",
        "physics-script-rebuild-interface-rollup.v1.json",
        "selectedNextSlice=PhysicsScript Rebuild Fixture Selection Proof Plan",
        "recommendedNextFixtureFamily=explosion",
        "valueInterfaceRowCount=87",
        "unselectedObservedRowCount=113",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, VALUE_CROSSWALK_PLAN):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed rollup slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks rollup active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed fixture selection lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks fixture selection active", failures)
    require(f"Completed {COMPLETED_EXPLOSION_SLICE}" in backlog, "backlog missing completed explosion fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_EXPLOSION_SLICE}. Status: selected" not in backlog, "backlog still marks explosion fixture active", failures)
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
        package.get("scripts", {}).get("test:physics-script-rebuild-interface-rollup")
        == r"py -3 tools\physics_script_rebuild_interface_rollup_probe.py --check",
        "missing package rollup probe script",
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
        require(no_bea_process_running(), "BEA.exe process is running after rollup probe", failures)
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("PhysicsScript rebuild-interface rollup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript rebuild-interface rollup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
