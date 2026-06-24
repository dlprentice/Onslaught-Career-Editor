#!/usr/bin/env python3
"""Validate the Wave900+ re-audit probe sweep classification."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave900-plus-audit"
RESULTS = BASE / "wave900-plus-probe-results.tsv"
OUT = BASE / "wave900-plus-audit-summary.json"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

FIRST_WAVE = 900
LAST_WAVE = 981
WAVE_RE = re.compile(r"wave(9\d\d)", re.IGNORECASE)
CURRENT_STATE_TOKENS = (
    "developer_agent_state.json",
    "documentation_agent_state.json",
    "re_orchestrator_state.json",
)
QUEUE_TOKENS = (
    "queue total mismatch",
    "quality TSV row count mismatch",
    "quality TSV commented count mismatch",
    "quality TSV strict-clean count mismatch",
    "queue TSV row count mismatch",
    "strict clean-signature count mismatch",
)
DOC_TOKENS = (
    "missing token in reverse-engineering",
    "missing token in lore-book",
    "missing token in release",
    "missing token in roadmap",
)
DISALLOWED_FAILURE_PATTERNS = (
    "metadata mismatch",
    "signature mismatch",
    "tag mismatch",
    "decompile mismatch",
    "missing metadata",
    "missing tags",
    "missing decompile",
    "backup summary mismatch",
    "backup path mismatch",
    "backup byte",
    "missing log token",
    "unexpected failure token",
    "dry log missing",
    "apply log missing",
    "final dry log missing",
    "LockException",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else ""


def read_json(path: Path) -> dict[str, object]:
    text = read_text(path)
    return json.loads(text) if text else {}


def package_wave_scripts() -> set[str]:
    data = json.loads(read_text(ROOT / "package.json"))
    scripts = data.get("scripts", {})
    rows: set[str] = set()
    for name, command in scripts.items():
        if name in {
            "test:ghidra-wave900-plus-audit",
            "test:ghidra-wave900-plus-evidence-audit",
            "test:ghidra-wave900-plus-through-wave983-recheck",
            "test:ghidra-wave900-plus-through-wave984-recheck",
        }:
            continue
        matches = [*WAVE_RE.finditer(name), *WAVE_RE.finditer(str(command))]
        if any(FIRST_WAVE <= int(match.group(1)) <= LAST_WAVE for match in matches):
            rows.add(name)
    return rows


def read_results() -> list[dict[str, str]]:
    if not RESULTS.is_file():
        return []
    rows: list[dict[str, str]] = []
    with RESULTS.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for raw in reader:
            if len(raw) < 4:
                continue
            rows.append({"status": raw[0], "wave": raw[1], "script": raw[2], "log": raw[3]})
    return rows


def classify_failure(log_text: str) -> set[str]:
    lowered = log_text.lower()
    categories: set[str] = set()
    if any(token.lower() in lowered for token in CURRENT_STATE_TOKENS):
        categories.add("current-state-baton")
    if any(token.lower() in lowered for token in QUEUE_TOKENS):
        categories.add("historical-live-queue")
    if any(token.lower() in lowered for token in DOC_TOKENS):
        categories.add("rolled-current-doc")
    if any(token.lower() in lowered for token in DISALLOWED_FAILURE_PATTERNS):
        categories.add("evidence-mismatch")
    return categories


def failure_lines(log_text: str) -> list[str]:
    return [line[2:].strip() for line in log_text.splitlines() if line.startswith("- ")]


def classify_failure_lines(log_text: str) -> tuple[list[dict[str, object]], set[str]]:
    lines = failure_lines(log_text)
    if not lines:
        categories = classify_failure(log_text)
        if not categories:
            categories.add("unclassified")
        return [{"line": "<whole-log>", "categories": sorted(categories)}], categories

    details: list[dict[str, object]] = []
    aggregate: set[str] = set()
    for line in lines:
        categories = classify_failure(line)
        if not categories:
            categories.add("unclassified")
        aggregate.update(categories)
        details.append({"line": line, "categories": sorted(categories)})

    lowered = log_text.lower()
    if "lockexception" in lowered:
        aggregate.add("evidence-mismatch")
        details.append({"line": "<whole-log LockException>", "categories": ["evidence-mismatch"]})
    return details, aggregate


def current_queue_ok() -> bool:
    queue = read_json(QUEUE)
    quality = queue.get("qualitySignals", {}) if isinstance(queue, dict) else {}
    return (
        queue.get("totalFunctions") == 6411
        and quality.get("commentlessFunctionCount") == 0
        and quality.get("undefinedSignatureCount") == 0
        and quality.get("paramSignatureCount") == 0
    )


def build_report() -> dict[str, object]:
    failures: list[str] = []
    package_scripts = package_wave_scripts()
    rows = read_results()
    row_scripts = {row["script"] for row in rows}
    missing_scripts = sorted(package_scripts - row_scripts)
    extra_scripts = sorted(row_scripts - package_scripts)
    if missing_scripts:
        failures.append(f"missing wave script results: {len(missing_scripts)}")
    if extra_scripts:
        failures.append(f"unexpected wave script results: {len(extra_scripts)}")
    if not current_queue_ok():
        failures.append("current queue is not 6411/6411 with zero debt")

    pass_rows = [row for row in rows if row["status"] == "PASS"]
    fail_rows = [row for row in rows if row["status"] != "PASS"]
    classified: list[dict[str, object]] = []
    disallowed: list[str] = []
    for row in fail_rows:
        log_path = ROOT / row["log"]
        log_text = read_text(log_path)
        line_details, categories = classify_failure_lines(log_text)
        if "evidence-mismatch" in categories or "unclassified" in categories:
            disallowed.append(row["script"])
        classified.append({**row, "categories": sorted(categories), "lineClassifications": line_details})

    if disallowed:
        failures.append(f"wave probes with evidence/unclassified failures: {len(disallowed)}")

    return {
        "schema": "ghidra-wave900-plus-audit.v1",
        "status": "PASS" if not failures else "FAIL",
        "scope": f"Wave{FIRST_WAVE}-Wave{LAST_WAVE}",
        "resultFile": RESULTS.relative_to(ROOT).as_posix(),
        "packageWaveScriptCount": len(package_scripts),
        "resultCount": len(rows),
        "passCount": len(pass_rows),
        "failCount": len(fail_rows),
        "missingScriptCount": len(missing_scripts),
        "extraScriptCount": len(extra_scripts),
        "currentQueue": read_json(QUEUE),
        "failureCategories": classified,
        "failures": failures,
        "interpretation": [
            "Older focused probes that require the current state batons to retain historical wave tokens are stale by repo policy; state files are current batons, not changelogs.",
            "Older focused probes that compare historical wave totals against queue/current are stale after later function-boundary recoveries increased the live function count.",
            "This audit fails if a Wave900+ focused probe reports metadata, signature, tag, decompile, log, backup, lock, or unclassified evidence failures.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Wave900+ re-audit probe sweep classification")
    print("Status:", report["status"])
    print("Results:", report["resultFile"])
    print("Package wave scripts:", report["packageWaveScriptCount"])
    print("Probe results:", report["resultCount"])
    print("Passed:", report["passCount"])
    print("Failed:", report["failCount"])
    for failure in report["failures"]:
        print("-", failure)
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
