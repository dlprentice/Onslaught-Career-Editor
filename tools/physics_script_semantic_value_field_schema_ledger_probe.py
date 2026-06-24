#!/usr/bin/env python3
"""Validate the PhysicsScript semantic value-field schema ledger."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger.v1.json"
READINESS = ROOT / "release" / "readiness" / "physics_script_semantic_value_field_schema_ledger_2026-06-10.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PHYSICS_PARSER = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
FUNCTION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
SUMMARY = ROOT / "subagents" / "physics_script_schema_parser_proof_2026-06-08" / "physics-script-copied-corpus-summary.json"
PACKAGE_JSON = ROOT / "package.json"

LORE_FILES = (
    (PLAN, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger-proof-plan.md"),
    (SCHEMA, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-semantic-value-field-schema-ledger.v1.json"),
    (BACKLOG, ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"),
    (MAPPED, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"),
    (BIN_INDEX, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"),
    (RE_INDEX, ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"),
    (PHYSICS_CONTRACT, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"),
    (PHYSICS_PARSER, ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"),
)

THIS_SLICE = "PhysicsScript Semantic Value-Field Schema Ledger Proof Plan"
THIS_SCOPE = "physics-script-semantic-value-field-schema-ledger-proof-plan"
STATUS_TOKEN = "physics-script-semantic-value-field-schema-ledger-complete-static-semantic-ledger-not-runtime-proof"
NEXT_SLICE = "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan"
NEXT_SCOPE = "physics-script-scalar-string-value-decoder-fixture-proof-plan"
COMPLETED_CROSSWALK_SLICE = "PhysicsScript Value-ID Semantic Crosswalk Proof Plan"
COMPLETED_ROLLUP_SLICE = "PhysicsScript Rebuild Interface Rollup Proof Plan"
CURRENT_ACTIVE_SLICE = "PhysicsScript Rebuild Fixture Selection Proof Plan"
COMPLETED_EXPLOSION_SLICE = "PhysicsScript Explosion Rebuild Fixture Proof Plan"
COMPLETED_SPAWNER_SLICE = "PhysicsScript Spawner Rebuild Fixture Proof Plan"
COMPLETED_ROUND_SLICE = "PhysicsScript Round Rebuild Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan"

EXPECTED_FAMILIES = {
    "unit": (1, 160, 2338, 54, 28840, 50284),
    "weapon": (2, 139, 286, 14, 4082, 8894),
    "weapon-mode": (3, 145, 1934, 32, 15007, 33261),
    "round": (4, 91, 782, 33, 5431, 16167),
    "spawner": (5, 38, 244, 10, 1441, 5279),
    "explosion": (6, 118, 869, 14, 14616, 27335),
    "component": (7, 39, 225, 20, 2921, 6337),
    "feature": (8, 43, 113, 5, 1375, 3319),
    "hazard": (9, 4, 12, 3, 83, 273),
}

SEMANTIC_BUCKETS = (
    "scalar4",
    "rounded_scalar4",
    "owned_string_at_08",
    "two_scalar4",
    "three_scalar4",
    "nested_enum_child",
    "flag_from_scalar_nonzero",
    "based_on_copy",
    "registry_by_name_apply",
    "indexed_scalar",
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
    "runtimePhysicsScriptOutcomesProven",
    "serializedPhysicsScriptCompletenessProven",
    "exactPhysicsScriptLayoutProven",
    "completeNestedEnumSemanticsProven",
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
    "beProcessesAfterLedger",
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
    "complete nested enum semantics proven",
    "godot parity proven",
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
    summary = read_json(SUMMARY)
    summary_file = summary["corpus"]["files"][0]

    require(schema["schemaVersion"] == "physics-script-semantic-value-field-schema-ledger.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "schema status mismatch", failures)
    require(schema["ledgerStatus"] == STATUS_TOKEN, "ledger status mismatch", failures)
    require(schema["proofPlan"] == THIS_SLICE, "proof plan mismatch", failures)
    require(schema["scope"] == THIS_SCOPE, "scope mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(schema["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)

    static = schema["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)

    corpus = schema["corpusCounts"]
    require(corpus["parsedCopiedCorpusFiles"] == summary["corpus"]["parsedFiles"] == 1, "parsed file count mismatch", failures)
    require(corpus["parsedByteCount"] == summary["corpus"]["totalBytes"] == 175603, "byte count mismatch", failures)
    require(corpus["streamHeader"] == "0x12" and summary_file["headerValue"] == 0x12, "stream header mismatch", failures)
    require(corpus["topLevelStatementCount"] == summary["aggregate"]["topLevelRecords"] == 777, "top-level count mismatch", failures)
    require(corpus["topLevelTypeCounts"] == summary["aggregate"]["topLevelTypeCounts"], "top-level type counts mismatch", failures)
    require(corpus["unknownTopLevelIdCount"] == summary["aggregate"]["unknownTopLevelRecords"] == 0, "unknown top-level count mismatch", failures)
    require(corpus["valueListNodeCount"] == summary["aggregate"]["valueNodeCount"] == 6803, "value node count mismatch", failures)
    require(corpus["uniqueStatementValuePairCount"] == summary_file["uniqueStatementValuePairs"] == 185, "unique statement/value pair count mismatch", failures)
    require(corpus["rawValuePayloadBytesPreserved"] == summary["aggregate"]["rawValuePayloadBytesPreserved"] == 73796, "raw payload count mismatch", failures)
    require(corpus["continueMarkerCount"] == summary["aggregate"]["continuationMarkerCounts"]["0"] == 6026, "continue marker count mismatch", failures)
    require(corpus["terminatingMarkerCount"] == summary["aggregate"]["continuationMarkerCounts"]["-1"] == 777, "terminating marker count mismatch", failures)

    families = {row["family"]: row for row in schema["topLevelFamilies"]}
    require(set(families) == set(EXPECTED_FAMILIES), "top-level family set mismatch", failures)
    for family, (type_id, records, nodes, unique_ids, raw_bytes, declared_bytes) in EXPECTED_FAMILIES.items():
        row = families[family]
        require(row["typeId"] == type_id, f"type id mismatch for {family}", failures)
        require(row["topLevelRecords"] == records, f"top-level records mismatch for {family}", failures)
        require(row["valueNodes"] == nodes, f"value nodes mismatch for {family}", failures)
        require(row["uniqueValueIds"] == unique_ids, f"unique value ids mismatch for {family}", failures)
        require(row["rawValuePayloadBytes"] == raw_bytes, f"raw payload bytes mismatch for {family}", failures)
        require(row["declaredPayloadBytes"] == declared_bytes, f"declared payload bytes mismatch for {family}", failures)

    require(schema["valueCountsByFamily"] == summary_file["valueCountsByFamily"], "valueCountsByFamily mismatch", failures)
    bucket_ids = [row["id"] for row in schema["semanticBuckets"]]
    require(tuple(bucket_ids) == SEMANTIC_BUCKETS, "semantic bucket order/count mismatch", failures)

    guard = schema["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guard["zeroCounters"][key] == 0, f"counter must be zero: {key}", failures)

    require(schema["publicSafety"]["publicLeakCheck"] == "PASS", "public leak status mismatch", failures)
    require("runtime PhysicsScript behavior" in schema["claimBoundary"]["doesNotProve"], "claim boundary missing runtime PhysicsScript behavior", failures)
    check_no_bad_public_content(SCHEMA, failures)
    require(no_bea_process_running(), "BEA process still running after ledger probe", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        STATUS_TOKEN,
        "physics-script-semantic-value-field-schema-ledger.v1.json",
        "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1179/1179 = 100.00%",
        "175603",
        "0x12",
        "777",
        "6803",
        "185",
        "73796",
        "CPhysicsScript__Load",
        "CPhysicsScript__CreateStatement",
        "CPhysicsScriptStatements__CreateStatementType2",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer",
        "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer",
        "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
        "CWeaponLaunchAngle__LoadFromMemBuffer",
        "CComponentIndexedScalar164__ApplyToComponentByName",
        "DAT_008553e8",
        "DAT_008553ec",
        "DAT_008553f0",
        "DAT_008553f4",
        "DAT_008553f8",
        "DAT_00855400",
        "DAT_00855404",
        "DAT_00855408",
        "DAT_008553fc",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        for bucket in SEMANTIC_BUCKETS:
            require(bucket in text, f"{path.relative_to(ROOT)} missing semantic bucket: {bucket}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "physics-script-semantic-value-field-schema-ledger-proof-plan.md",
        "physics-script-semantic-value-field-schema-ledger.v1.json",
        "semanticBucketCount=10",
        "physicsScriptTopLevelStatementCount=777",
        "physicsScriptValueListNodeCount=6803",
        "physicsScriptStatementValuePairCount=185",
        "physicsScriptRawValuePayloadBytesPreserved=73796",
        "selectedNextSlice=PhysicsScript Scalar/String Value Decoder Fixture Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PHYSICS_CONTRACT, PHYSICS_PARSER):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed ledger slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks ledger slice active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed scalar/string decoder lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks scalar/string decoder lane active", failures)
    require(f"Completed {COMPLETED_CROSSWALK_SLICE}" in backlog, "backlog missing completed value-ID semantic crosswalk lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_CROSSWALK_SLICE}. Status: selected" not in backlog, "backlog still marks value-ID semantic crosswalk lane active", failures)
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
        package.get("scripts", {}).get("test:physics-script-semantic-value-field-schema-ledger")
        == r"py -3 tools\physics_script_semantic_value_field_schema_ledger_probe.py --check",
        "missing package ledger probe script",
        failures,
    )


def check_source_anchors(failures: list[str]) -> None:
    function_text = read_text(FUNCTION_DOC)
    contract_text = read_text(PHYSICS_CONTRACT)
    parser_text = read_text(PHYSICS_PARSER)
    for token in (
        "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer",
        "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer",
        "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
        "CWeaponLaunchAngle__LoadFromMemBuffer",
        "CComponentIndexedScalar164__ApplyToComponentByName",
        "DAT_008553e8",
        "DAT_008553ec",
        "DAT_008553f0",
        "DAT_008553f4",
        "DAT_008553f8",
        "DAT_00855400",
        "DAT_00855404",
        "DAT_00855408",
        "DAT_008553fc",
    ):
        require(token in function_text or token in contract_text, f"missing source anchor: {token}", failures)
    for token in (
        "Top-level statements | `777`",
        "Value-list nodes | `6803`",
        "Unique statement/value id pairs | `185`",
        "Raw value payload bytes preserved | `73796`",
        "Value-list records can be counted and raw-preserved without decoding semantic value fields.",
    ):
        require(token in parser_text, f"parser proof missing token: {token}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_source_anchors(failures)

    if failures:
        print("PhysicsScript semantic value-field schema ledger probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript semantic value-field schema ledger probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
