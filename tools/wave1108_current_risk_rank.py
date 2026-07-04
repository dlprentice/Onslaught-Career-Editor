#!/usr/bin/env python3
"""Generate and validate the Wave1108 current static-risk rank."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
OUT_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
RISK_JSON = OUT_DIR / "wave1108-current-risk-ranked-functions.json"
RISK_TSV = OUT_DIR / "wave1108-current-risk-ranked-functions.tsv"
FOCUSED_JSON = OUT_DIR / "wave1108-current-focused-candidates.json"
FOCUSED_TSV = OUT_DIR / "wave1108-current-focused-candidates.tsv"

NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

LATEST_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

SIGNAL_WEIGHTS = {
    "stale_or_corrected": 8,
    "provisional_or_candidate": 7,
    "exact_layout_deferred": 6,
    "source_identity_deferred": 6,
    "generic_name_shape": 5,
    "critical_family": 4,
    "runtime_or_rebuild_deferred": 2,
}

TOKEN_SETS = {
    "stale_or_corrected": (
        "stale",
        "correct",
        "correction",
        "wrong",
        "mislabel",
        "supersede",
        "renamed",
        "rename",
        "owner correction",
        "signature correction",
    ),
    "provisional_or_candidate": (
        "provisional",
        "candidate",
        "likely",
        "uncertain",
        "unknown",
        "unresolved",
        "hypothesis",
    ),
    "exact_layout_deferred": (
        "exact layout",
        "concrete layout",
        "layout remain",
        "layout remains",
        "object layout",
        "field semantics",
        "hidden abi",
        "register abi",
        "stack-locked",
    ),
    "source_identity_deferred": (
        "source identity",
        "source-body identity",
        "exact source",
        "source method name",
        "source virtual name",
        "source parity remain",
    ),
    "runtime_or_rebuild_deferred": (
        "runtime",
        "gameplay",
        "patching",
        "rebuild parity",
        "clean-room",
        "visual qa",
    ),
}

CRITICAL_FAMILIES = (
    "CUnit",
    "CBattleEngine",
    "CGame",
    "CCareer",
    "CDXTexture",
    "CFastVB",
    "CMesh",
    "CWorld",
    "CWeapon",
    "CScript",
    "IScript",
    "MissionScript",
    "PhysicsScript",
    "CDXEngine",
    "CEngine",
    "CFrontEnd",
    "CController",
    "CMessage",
    "CSound",
    "CParticle",
    "CMonitor",
    "CMemory",
)

GENERIC_NAME_RE = re.compile(
    r"(?:^|__)("
    r".*VFunc.*|.*Thunk.*|.*Wrapper.*|.*ReturnZero.*|.*ReturnTrue.*|.*NoOp.*|"
    r".*ctor_like.*|.*FUN_.*|.*Unwind@.*|.*stub.*"
    r")",
    re.IGNORECASE,
)

FOCUSED_SIGNALS = {
    "stale_or_corrected",
    "provisional_or_candidate",
    "exact_layout_deferred",
    "source_identity_deferred",
    "generic_name_shape",
}


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = ["score", "address", "name", "signals", "signature", "commentPreview"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "score": row["score"],
                    "address": row["address"],
                    "name": row["name"],
                    "signals": ",".join(row["signals"]),
                    "signature": row["signature"],
                    "commentPreview": row["commentPreview"],
                }
            )


def normalize_preview(comment: str) -> str:
    value = " ".join(comment.split())
    return value[:420]


def classify(row: dict[str, str]) -> dict[str, object] | None:
    name = row.get("name", "")
    signature = row.get("signature", "")
    comment = row.get("comment", "")
    haystack = f"{name} {signature} {comment}".lower()
    signals: list[str] = []

    for signal, tokens in TOKEN_SETS.items():
        if any(token in haystack for token in tokens):
            signals.append(signal)

    if GENERIC_NAME_RE.search(name):
        signals.append("generic_name_shape")

    if any(family.lower() in haystack for family in CRITICAL_FAMILIES):
        signals.append("critical_family")

    unique_signals = []
    for signal in signals:
        if signal not in unique_signals:
            unique_signals.append(signal)

    if not unique_signals:
        return None

    score = sum(SIGNAL_WEIGHTS[signal] for signal in unique_signals)
    return {
        "score": score,
        "address": row.get("address", ""),
        "name": name,
        "signals": unique_signals,
        "signature": signature,
        "commentPreview": normalize_preview(comment),
    }


def build_rankings() -> tuple[list[dict[str, str]], list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    queue_rows = read_tsv(QUEUE_TSV)
    ranked = [classified for row in queue_rows if (classified := classify(row)) is not None]
    ranked.sort(key=lambda item: (-int(item["score"]), str(item["address"])))

    focused = [
        row
        for row in ranked
        if int(row["score"]) >= 15 and any(signal in FOCUSED_SIGNALS for signal in row["signals"])
    ]

    signal_counts: dict[str, int] = {signal: 0 for signal in SIGNAL_WEIGHTS}
    for row in ranked:
        for signal in row["signals"]:
            signal_counts[signal] += 1
    return queue_rows, ranked, focused, signal_counts


def summary_payload(
    queue_rows: list[dict[str, str]],
    ranked: list[dict[str, object]],
    focused: list[dict[str, object]],
    signal_counts: dict[str, int],
    *,
    focused_payload: bool,
) -> dict[str, object]:
    rows = focused if focused_payload else ranked
    return {
        "schema": "wave1108-current-focused-candidates.v1" if focused_payload else "wave1108-current-risk-ranked-functions.v1",
        "source": str(QUEUE_TSV.relative_to(ROOT)).replace("/", "\\"),
        "totalFunctions": len(queue_rows),
        "candidateFunctions": len(rows),
        "signalCounts": signal_counts,
        "scoring": {
            "stale_or_corrected": SIGNAL_WEIGHTS["stale_or_corrected"],
            "provisional_or_candidate": SIGNAL_WEIGHTS["provisional_or_candidate"],
            "exact_layout_deferred": SIGNAL_WEIGHTS["exact_layout_deferred"],
            "source_identity_deferred": SIGNAL_WEIGHTS["source_identity_deferred"],
            "generic_name_shape": SIGNAL_WEIGHTS["generic_name_shape"],
            "critical_family": SIGNAL_WEIGHTS["critical_family"],
            "runtime_or_rebuild_deferred": SIGNAL_WEIGHTS["runtime_or_rebuild_deferred"],
            "focusedThreshold": 15,
        },
        "top": rows[:250],
    }


def generate() -> dict[str, int]:
    queue_rows, ranked, focused, signal_counts = build_rankings()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RISK_JSON.write_text(json.dumps(summary_payload(queue_rows, ranked, focused, signal_counts, focused_payload=False), indent=2) + "\n", encoding="utf-8")
    FOCUSED_JSON.write_text(json.dumps(summary_payload(queue_rows, ranked, focused, signal_counts, focused_payload=True), indent=2) + "\n", encoding="utf-8")
    write_tsv(RISK_TSV, ranked)
    write_tsv(FOCUSED_TSV, focused)
    return {
        "total": len(queue_rows),
        "risk": len(ranked),
        "focused": len(focused),
        "top": min(250, len(focused)),
        **signal_counts,
    }


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check(failures: list[str]) -> None:
    expected = generate()
    risk = read_json(RISK_JSON)
    focused = read_json(FOCUSED_JSON)
    risk_rows = read_tsv(RISK_TSV)
    focused_rows = read_tsv(FOCUSED_TSV)

    require(risk.get("schema") == "wave1108-current-risk-ranked-functions.v1", "risk schema mismatch", failures)
    require(focused.get("schema") == "wave1108-current-focused-candidates.v1", "focused schema mismatch", failures)
    require(risk.get("totalFunctions") == expected["total"], "risk total mismatch", failures)
    require(focused.get("totalFunctions") == expected["total"], "focused total mismatch", failures)
    require(risk.get("candidateFunctions") == expected["risk"], "risk candidate count mismatch", failures)
    require(focused.get("candidateFunctions") == expected["focused"], "focused candidate count mismatch", failures)
    require(len(risk_rows) == expected["risk"], "risk TSV row count mismatch", failures)
    require(len(focused_rows) == expected["focused"], "focused TSV row count mismatch", failures)

    core_tokens = (
        "wave1108-current-risk-rank",
        "current-risk denominator",
        f"{expected['total']}/{expected['total']} = 100.00%",
        f"current risk candidates: {expected['risk']}",
        f"current focused candidates: {expected['focused']}",
        "focused threshold `15`",
        "not Wave911 reconstruction",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
    )
    archival_tokens = core_tokens + (LATEST_BACKUP,)
    live_progress = read_json(PROGRESS_JSON)
    live_backup = live_progress.get("latestWave", {}).get("backup", "")
    state_tokens = core_tokens + ((live_backup,) if live_backup else ())

    archival_docs = {
        "wave1108-current-risk-rank.md": read_text(NOTE),
        "wave1108_current_risk_rank_2026-06-04.md": read_text(READINESS),
        "mapped-systems.md": read_text(MAPPED_SYSTEMS),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
        "binary-analysis/_index.md": read_text(BINARY_INDEX),
        "RE-INDEX.md": read_text(RE_INDEX),
    }
    state_docs = {
        "developer_agent_state.json": read_text(DEVELOPER_STATE),
        "documentation_agent_state.json": read_text(DOCUMENTATION_STATE),
        "re_orchestrator_state.json": read_text(RE_STATE),
    }

    for name, text in archival_docs.items():
        for token in archival_tokens:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        require("runtime behavior proven" not in text.lower(), f"overclaim in {name}: runtime behavior proven", failures)
        require("rebuild parity proven" not in text.lower(), f"overclaim in {name}: rebuild parity proven", failures)

    for name, text in state_docs.items():
        for token in state_tokens:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        require("runtime behavior proven" not in text.lower(), f"overclaim in {name}: runtime behavior proven", failures)
        require("rebuild parity proven" not in text.lower(), f"overclaim in {name}: rebuild parity proven", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "current-risk note mirror mismatch", failures)
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get("test:wave1108-current-risk-rank") == r"py -3 tools\wave1108_current_risk_rank.py --check", "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate generated artifacts and docs")
    parser.add_argument("--generate", action="store_true", help="generate current-risk artifacts")
    args = parser.parse_args()

    if args.check:
        failures: list[str] = []
        check(failures)
        if failures:
            print("Wave1108 current-risk rank probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("Wave1108 current-risk rank probe: PASS")
        return 0

    counts = generate()
    print("Wave1108 current-risk rank generated")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(f"output: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
