#!/usr/bin/env python3
"""Validate the PhysicsScript scalar/string value decoder fixture proof."""

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

import physics_script_scalar_string_decoder_fixture as fixture_tool  # noqa: E402


PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-scalar-string-value-decoder-fixture-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_scalar_string_value_decoder_fixture_proof_plan_2026-06-10.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PHYSICS_PARSER = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
SEMANTIC_LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger-proof-plan.md"
FUNCTION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-scalar-string-value-decoder-fixture-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
    (PHYSICS_PARSER, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"),
)

THIS_SLICE = "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan"
THIS_SCOPE = "physics-script-scalar-string-value-decoder-fixture-proof-plan"
STATUS_TOKEN = "physics-script-scalar-string-value-decoder-fixture-complete-static-decode-roundtrip-not-runtime-proof"
NEXT_SLICE = "PhysicsScript Value-ID Semantic Crosswalk Proof Plan"
COMPLETED_ROLLUP_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
CURRENT_ACTIVE_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
COMPLETED_EXPLOSION_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
COMPLETED_SPAWNER_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"

EXPECTED_CLASS_COUNTS = {
    "scalar4_roundtrip": 3912,
    "owned_string_ascii_nul_shape_roundtrip": 1737,
    "two_scalar4_roundtrip": 361,
    "three_scalar4_roundtrip": 132,
    "raw_preserved_other": 661,
}

EXPECTED_FAMILY_CLASS_COUNTS = {
    "component": {"owned_string_ascii_nul_shape_roundtrip": 81, "raw_preserved_other": 27, "scalar4_roundtrip": 116, "two_scalar4_roundtrip": 1},
    "explosion": {"owned_string_ascii_nul_shape_roundtrip": 532, "scalar4_roundtrip": 330, "three_scalar4_roundtrip": 7},
    "feature": {"owned_string_ascii_nul_shape_roundtrip": 66, "scalar4_roundtrip": 45, "three_scalar4_roundtrip": 2},
    "hazard": {"owned_string_ascii_nul_shape_roundtrip": 3, "scalar4_roundtrip": 8, "three_scalar4_roundtrip": 1},
    "round": {"owned_string_ascii_nul_shape_roundtrip": 161, "raw_preserved_other": 24, "scalar4_roundtrip": 584, "three_scalar4_roundtrip": 10, "two_scalar4_roundtrip": 3},
    "spawner": {"owned_string_ascii_nul_shape_roundtrip": 34, "scalar4_roundtrip": 206, "three_scalar4_roundtrip": 4},
    "unit": {"owned_string_ascii_nul_shape_roundtrip": 511, "raw_preserved_other": 469, "scalar4_roundtrip": 1204, "three_scalar4_roundtrip": 31, "two_scalar4_roundtrip": 123},
    "weapon": {"owned_string_ascii_nul_shape_roundtrip": 15, "raw_preserved_other": 141, "scalar4_roundtrip": 129, "three_scalar4_roundtrip": 1},
    "weapon-mode": {"owned_string_ascii_nul_shape_roundtrip": 334, "scalar4_roundtrip": 1290, "three_scalar4_roundtrip": 76, "two_scalar4_roundtrip": 234},
}

FIXTURE_CLASSES = (
    "scalar4_roundtrip",
    "rounded_scalar4_synthetic",
    "two_scalar4_roundtrip",
    "three_scalar4_roundtrip",
    "owned_string_ascii_nul_shape_roundtrip",
    "raw_preserved_other",
)

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
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
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
    "serialized physicsscript file-format completeness proven",
    "serialized physics-script file-format completeness proven",
    "exact statement/value-list/concrete record layouts proven",
    "complete value-id semantics proven",
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
    fresh = fixture_tool.build_report()
    require(schema == fresh, "tracked schema differs from fresh fixture report", failures)

    require(schema["schemaVersion"] == "physics-script-scalar-string-decoder-fixture.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "schema status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["fixtureStatus"] == STATUS_TOKEN, "fixture status mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)

    source = schema["source"]
    for key in ("programFilesInputUsed", "missionScriptsExcluded", "rawBytesEmitted", "rawNamesOrStringsEmitted", "rawNumericValuesEmitted", "runtimeExecution", "ghidraMutation", "godotWork", "rebuildImplementation"):
        require(source[key] is False if key != "missionScriptsExcluded" else source[key] is True, f"source guard mismatch: {key}", failures)

    aggregate = schema["corpusAggregate"]
    require(aggregate["parsedCopiedCorpusFiles"] == 1, "parsed copied corpus file count mismatch", failures)
    require(aggregate["parsedByteCount"] == 175603, "copied corpus byte count mismatch", failures)
    require(aggregate["topLevelStatementCount"] == 777, "top-level statement count mismatch", failures)
    require(aggregate["valueListNodeCount"] == 6803, "value node count mismatch", failures)
    require(aggregate["fixtureClassCounts"] == EXPECTED_CLASS_COUNTS, "fixture class counts mismatch", failures)
    require(aggregate["copiedCorpusStringsDecodedForPublication"] is False, "copied strings must not be decoded for publication", failures)
    require(aggregate["copiedCorpusNumericValuesDecodedForPublication"] is False, "copied numerics must not be decoded for publication", failures)
    require(aggregate["copiedCorpusRawBytesEmitted"] is False, "copied raw bytes must not be emitted", failures)

    corpus = schema["corpus"]
    require(corpus["parsedFiles"] == 1, "corpus parsed file count mismatch", failures)
    require(corpus["valueNodeCount"] == 6803, "corpus value node count mismatch", failures)
    require(corpus["fixtureClassCounts"] == EXPECTED_CLASS_COUNTS, "corpus fixture class counts mismatch", failures)
    require(corpus["fixtureClassCountsByFamily"] == EXPECTED_FAMILY_CLASS_COUNTS, "family fixture class counts mismatch", failures)
    require(corpus["payloadSizeHistogram"]["4"] == 3912, "payload size 4 count mismatch", failures)
    require(corpus["payloadSizeHistogram"]["8"] == 361, "payload size 8 count mismatch", failures)
    require(corpus["payloadSizeHistogram"]["12"] == 132, "payload size 12 count mismatch", failures)
    require(corpus["stringLengthMin"] == 4, "string length min mismatch", failures)
    require(corpus["stringLengthMax"] == 40, "string length max mismatch", failures)

    synthetic = schema["syntheticFixtures"]
    require(synthetic["syntheticPublicSafeOnly"] is True, "synthetic public-safe flag mismatch", failures)
    require(synthetic["scalar4RoundtripCases"] == 3, "synthetic scalar count mismatch", failures)
    require(synthetic["ownedStringAsciiNulShapeRoundtripCases"] == 3, "synthetic owned string count mismatch", failures)
    require(synthetic["twoScalar4RoundtripCases"] == 2, "synthetic two-scalar count mismatch", failures)
    require(synthetic["threeScalar4RoundtripCases"] == 2, "synthetic three-scalar count mismatch", failures)
    require(synthetic["roundedScalarFiniteNonTieCases"] == 3, "synthetic rounded count mismatch", failures)
    require(synthetic["totalSyntheticFixtureCases"] == 13, "synthetic fixture total mismatch", failures)

    class_ids = [row["id"] for row in schema["fixtureClasses"]]
    require(tuple(class_ids) == FIXTURE_CLASSES, "fixture class list/order mismatch", failures)
    guard = schema["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guard["zeroCounters"][key] == 0, f"counter must be zero: {key}", failures)

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
        "physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json",
        "PhysicsScript Value-ID Semantic Crosswalk Proof Plan",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1179/1179 = 100.00%",
        "175603",
        "0x12",
        "777",
        "6803",
        "3912",
        "1737",
        "361",
        "132",
        "661",
        "13",
        "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer",
        "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer",
        "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
        "CWeaponLaunchAngle__LoadFromMemBuffer",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "rawCopiedStringsEmitted=false",
        "rawNumericValuesEmitted=false",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        for fixture_class in FIXTURE_CLASSES:
            require(fixture_class in text, f"{path.relative_to(ROOT)} missing fixture class: {fixture_class}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physics-script-scalar-string-value-decoder-fixture-proof-plan.md",
        "physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json",
        "fixtureClassCounts=3912/1737/361/132/661",
        "syntheticFixtureCaseCount=13",
        "selectedNextSlice=PhysicsScript Value-ID Semantic Crosswalk Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, PHYSICS_PARSER):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed scalar/string fixture slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks scalar/string fixture active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed value-id crosswalk lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks value-id crosswalk lane active", failures)
    require(f"Completed {COMPLETED_ROLLUP_SLICE}" in backlog, "backlog missing completed PhysicsScript rebuild interface rollup lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROLLUP_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript rebuild interface rollup lane active", failures)
    require(f"Completed {CURRENT_ACTIVE_SLICE}" in backlog, "backlog missing completed PhysicsScript rebuild fixture selection lane", failures)
    require(f"The selected active static-to-proof slice is {CURRENT_ACTIVE_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript rebuild fixture selection lane active", failures)
    require(f"Completed {COMPLETED_EXPLOSION_SLICE}" in backlog, "backlog missing completed PhysicsScript explosion fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_EXPLOSION_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript explosion fixture lane active", failures)
    require(f"Completed {COMPLETED_SPAWNER_SLICE}" in backlog, "backlog missing completed PhysicsScript spawner fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_SPAWNER_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript spawner fixture lane active", failures)
    require(f"Completed {COMPLETED_ROUND_SLICE}" in backlog, "backlog missing completed PhysicsScript round fixture lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROUND_SLICE}. Status: selected" not in backlog, "backlog still marks PhysicsScript round fixture lane active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active PhysicsScript fixture-family completion rollup lane", failures)

    for source, mirror in LORE_FILES:
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:physics-script-scalar-string-value-decoder-fixture-proof-plan")
        == r"py -3 tools\physics_script_scalar_string_value_decoder_fixture_proof_plan_probe.py --check",
        "missing package scalar/string fixture probe script",
        failures,
    )


def check_source_anchors(failures: list[str]) -> None:
    combined = "\n".join(read_text(path) for path in (PHYSICS_CONTRACT, PHYSICS_PARSER, SEMANTIC_LEDGER, FUNCTION_DOC))
    for token in (
        "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer",
        "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer",
        "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
        "CWeaponLaunchAngle__LoadFromMemBuffer",
        "CUnitSoundMaterial__ApplyToUnitData",
        "CWeaponVolleySize__ApplyToWeaponModeByName",
        "CRoundGridOfFear__ApplyToRoundByName",
        "Value-list nodes | `6803`",
        "Raw value payload bytes preserved | `73796`",
    ):
        require(token in combined, f"missing source/static anchor: {token}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    try:
        check_schema(failures)
        check_docs(failures)
        check_source_anchors(failures)
        require(no_bea_process_running(), "BEA process still running after scalar/string fixture probe", failures)
    except Exception as exc:  # keep probe failure output concise for npm logs
        failures.append(str(exc))

    if failures:
        print("PhysicsScript scalar/string value decoder fixture proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript scalar/string value decoder fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
