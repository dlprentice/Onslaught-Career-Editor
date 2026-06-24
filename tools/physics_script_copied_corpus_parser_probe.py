#!/usr/bin/env python3
"""Validate the PhysicsScript copied-corpus parser/census proof."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import physics_script_copied_corpus_parser as parser_tool  # noqa: E402


BASE = ROOT / "subagents" / "physics_script_schema_parser_proof_2026-06-08"
SUMMARY = BASE / parser_tool.SUMMARY_NAME
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
READINESS = ROOT / "release" / "readiness" / "physics_script_copied_corpus_parser_proof_2026-06-08.md"
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-schema-parser-proof-plan.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

RESULT_LINK = "physics-script-copied-corpus-parser-proof.md"
ABSOLUTE_USER_SENTINEL = "C:" + "\\Users" + "\\david"

EXPECTED_TYPE_COUNTS = {
    "1": 160,
    "2": 139,
    "3": 145,
    "4": 91,
    "5": 38,
    "6": 118,
    "7": 39,
    "8": 43,
    "9": 4,
}

EXPECTED_MARKERS = {
    "-1": 777,
    "0": 6026,
}

FORBIDDEN_DOC_PHRASES = (
    "runtime physicsscript behavior proven",
    "mission outcomes proven",
    "resource-script outcomes proven",
    "serialized physics-script file-format completeness proven",
    "exact layouts proven",
    "complete nested enum semantics proven",
    "bea patching behavior proven",
    "visual qa complete",
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


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def assert_report(report: dict[str, Any], prefix: str, failures: list[str]) -> None:
    require(report.get("schema") == "physics-script-copied-corpus-parser.v1", f"{prefix} schema mismatch", failures)
    require(report.get("status") == "PASS", f"{prefix} status mismatch", failures)
    require(report.get("failures") == [], f"{prefix} has failures", failures)

    source = report.get("source", {})
    require(source.get("gameRoot") == "game", f"{prefix} game root mismatch", failures)
    require(source.get("copiedAppOwnedInputOnly") is True, f"{prefix} copied input flag mismatch", failures)
    require(source.get("programFilesInputUsed") is False, f"{prefix} Program Files flag mismatch", failures)
    require(source.get("missionScriptsExcluded") is True, f"{prefix} MissionScripts exclusion mismatch", failures)
    require(source.get("excludedInputPattern") == "MissionScripts/*.msl", f"{prefix} exclusion pattern mismatch", failures)

    context = report.get("staticContext", {})
    require(context.get("staticFunctionQuality") == "6411/6411 = 100.00%", f"{prefix} static function mismatch", failures)
    require(context.get("staticDebt") == "0 / 0 / 0", f"{prefix} static debt mismatch", failures)
    require(context.get("expandedStaticSurface") == "1560/1560 = 100.00%", f"{prefix} expanded mismatch", failures)
    require(context.get("currentRiskFocused") == "1179/1179 = 100.00%", f"{prefix} current risk mismatch", failures)
    require(context.get("remainingActiveFocusedWork") == 0, f"{prefix} remaining focused mismatch", failures)

    corpus = report.get("corpus", {})
    require(corpus.get("candidateFiles") == 1, f"{prefix} candidate file count mismatch", failures)
    require(corpus.get("parsedFiles") == 1, f"{prefix} parsed file count mismatch", failures)
    require(corpus.get("totalBytes") == 175603, f"{prefix} byte count mismatch", failures)
    require(corpus.get("defaultPhysicsDatPresent") is True, f"{prefix} default physics.dat missing", failures)
    require(corpus.get("defaultUnderscorePhysicsDatPresent") is False, f"{prefix} stale underscore file present", failures)
    files = corpus.get("files", [])
    require(len(files) == 1, f"{prefix} file row count mismatch", failures)
    if files:
        row = files[0]
        require(row.get("relativePath") == "game/data/default physics.dat", f"{prefix} relative path mismatch", failures)
        require(row.get("fileName") == "default physics.dat", f"{prefix} filename mismatch", failures)
        require(row.get("sizeBytes") == 175603, f"{prefix} file byte mismatch", failures)
        require(len(row.get("sha256", "")) == 64, f"{prefix} private hash missing", failures)
        require(row.get("headerValue") == 0x12, f"{prefix} header mismatch", failures)
        require(row.get("terminatorOffset") == 175599, f"{prefix} terminator offset mismatch", failures)
        require(row.get("terminatorAtEnd") is True, f"{prefix} terminator/end mismatch", failures)
        require(row.get("topLevelRecords") == 777, f"{prefix} top-level records mismatch", failures)
        require(row.get("topLevelTypeCounts") == EXPECTED_TYPE_COUNTS, f"{prefix} type counts mismatch", failures)
        require(row.get("topLevelUnknownRecords") == 0, f"{prefix} unknown top-level mismatch", failures)
        require(row.get("valueNodeCount") == 6803, f"{prefix} value node mismatch", failures)
        require(row.get("uniqueStatementValuePairs") == 185, f"{prefix} unique pair mismatch", failures)
        require(row.get("rawValuePayloadBytesPreserved") == 73796, f"{prefix} raw payload byte mismatch", failures)
        require(row.get("continuationMarkerCounts") == EXPECTED_MARKERS, f"{prefix} marker counts mismatch", failures)
        require(row.get("nameCount") == 777, f"{prefix} name count mismatch", failures)
        require(row.get("nameLength", {}).get("max") == 37, f"{prefix} max name length mismatch", failures)
        require(row.get("valueChainLength", {}).get("max") == 44, f"{prefix} max chain length mismatch", failures)
        require(row.get("rawNamesOrStringsEmitted") is False, f"{prefix} raw names emitted", failures)
        require(row.get("semanticValueDecodeAttempted") is False, f"{prefix} semantic decode flag mismatch", failures)

    aggregate = report.get("aggregate", {})
    require(aggregate.get("topLevelRecords") == 777, f"{prefix} aggregate top-level mismatch", failures)
    require(aggregate.get("topLevelTypeCounts") == EXPECTED_TYPE_COUNTS, f"{prefix} aggregate type counts mismatch", failures)
    require(aggregate.get("unknownTopLevelRecords") == 0, f"{prefix} aggregate unknown top mismatch", failures)
    require(aggregate.get("valueNodeCount") == 6803, f"{prefix} aggregate value nodes mismatch", failures)
    require(aggregate.get("uniqueStatementValuePairs") == 185, f"{prefix} aggregate unique pairs mismatch", failures)
    require(aggregate.get("rawValuePayloadBytesPreserved") == 73796, f"{prefix} aggregate raw payload mismatch", failures)
    require(aggregate.get("continuationMarkerCounts") == EXPECTED_MARKERS, f"{prefix} aggregate markers mismatch", failures)

    public_safety = report.get("publicSafety", {})
    for key in ("rawBytesEmitted", "rawNamesOrStringsEmitted", "absolutePathsEmitted", "launchesGame", "readsOrWritesOriginalExe", "mutatesGameFiles", "mutatesGhidra"):
        require(public_safety.get(key) is False, f"{prefix} public safety should be false: {key}", failures)
    require(public_safety.get("hashesKeptInIgnoredEvidenceOnly") is True, f"{prefix} hash boundary mismatch", failures)

    not_claimed = set(report.get("notClaimed", []))
    for token in (
        "runtime PhysicsScript behavior",
        "mission outcomes",
        "resource-script outcomes",
        "serialized physics-script file-format completeness",
        "exact statement/value-list/concrete record layouts",
        "complete nested enum semantics",
        "BEA patching behavior",
        "visual QA",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in not_claimed, f"{prefix} missing non-claim: {token}", failures)


def check_artifacts(failures: list[str]) -> None:
    require(BASE.is_dir(), "missing ignored PhysicsScript proof root", failures)
    require(SUMMARY.is_file(), "missing PhysicsScript copied-corpus summary", failures)
    stored = read_json(SUMMARY)
    assert_report(stored, "stored report", failures)

    rebuilt = parser_tool.build_report(ROOT / "game")
    assert_report(rebuilt, "rebuilt report", failures)
    for key in ("schema", "status", "source", "staticContext", "corpus", "aggregate", "publicSafety", "claims", "notClaimed", "warnings", "failures"):
        if key == "corpus":
            stored_corpus = dict(stored[key])
            rebuilt_corpus = dict(rebuilt[key])
            for row in stored_corpus.get("files", []):
                row.pop("sha256", None)
            for row in rebuilt_corpus.get("files", []):
                row.pop("sha256", None)
            require(stored_corpus == rebuilt_corpus, "rebuilt/stored corpus mismatch excluding private hashes", failures)
        else:
            require(stored.get(key) == rebuilt.get(key), f"rebuilt/stored mismatch: {key}", failures)

    serialized = json.dumps(stored)
    require(ABSOLUTE_USER_SENTINEL not in serialized, "summary leaks absolute user path", failures)
    require("Program Files" not in serialized, "summary leaks Program Files path", failures)
    require("MissionScripts" in serialized, "summary missing MissionScripts exclusion boundary", failures)

    tracked = subprocess.run(
        ["git", "ls-files", "subagents/physics_script_schema_parser_proof_2026-06-08"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    require(tracked.returncode == 0, "git ls-files failed for PhysicsScript proof root", failures)
    require(not tracked.stdout.strip(), "ignored PhysicsScript proof artifacts are tracked", failures)


def check_docs(failures: list[str]) -> None:
    result = read_text(RESULT)
    require(read_text(LORE_RESULT) == result, "lore result mirror mismatch", failures)

    required_result_tokens = (
        "Status: copied-corpus parser/census proof complete, not runtime proof",
        "not a new static re-audit wave",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        "Remaining active focused work remains `0`",
        "physics-script-copied-corpus-parser.v1",
        "subagents/physics_script_schema_parser_proof_2026-06-08/physics-script-copied-corpus-summary.json",
        "data/default physics.dat",
        "175603",
        "0x12",
        "777",
        "160 / 139 / 145 / 91 / 38 / 118 / 39 / 43 / 4",
        "6803",
        "185",
        "73796",
        "6026",
        "terminating `-1` marker at EOF",
        "0` unknown top-level ids",
        "MissionScripts/*.msl",
        "shallow framed parser/census proof only",
    )
    for path in (RESULT, READINESS):
        text = read_text(path)
        for token in required_result_tokens:
            require(token in text, f"{relative(path)} missing token: {token}", failures)
        require(ABSOLUTE_USER_SENTINEL not in text, f"{relative(path)} leaks absolute user path", failures)
        require("Program Files" not in text, f"{relative(path)} leaks Program Files path", failures)
        summary_hash = read_json(SUMMARY)["corpus"]["files"][0]["sha256"]
        require(summary_hash not in text, f"{relative(path)} leaks private SHA-256", failures)
        for bad in FORBIDDEN_DOC_PHRASES:
            require(bad not in text.lower(), f"{relative(path)} overclaims: {bad}", failures)

    for path in (PLAN, CONTRACT, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(RESULT_LINK in text, f"{relative(path)} missing result link", failures)
        for bad in FORBIDDEN_DOC_PHRASES:
            require(bad not in text.lower(), f"{relative(path)} overclaims: {bad}", failures)


def check_progress_and_package(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk focused mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:physics-script-copied-corpus-parser") == r"py -3 tools\physics_script_copied_corpus_parser_probe.py --check",
        "missing PhysicsScript copied-corpus package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_docs(failures)
    check_progress_and_package(failures)

    if failures:
        print("PhysicsScript copied-corpus parser probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PhysicsScript copied-corpus parser probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
