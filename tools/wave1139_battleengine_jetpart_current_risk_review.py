#!/usr/bin/env python3
"""Validate Wave1139 BattleEngine JetPart current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1139-battleengine-jetpart-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1139-battleengine-jetpart-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1139-battleengine-jetpart-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1139_battleengine_jetpart_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified"

TARGETS = {
    "0x004074d0": (
        "CBattleEngine__Gravity",
        "float __thiscall CBattleEngine__Gravity(void * this)",
        ("Wave1139 source-backed boundary recovery", "CBattleEngine::Gravity", "this+0x57c", "CBattleEngineJetPart__Gravity"),
    ),
    "0x00410210": (
        "CBattleEngineJetPart__ctor",
        "void * __thiscall CBattleEngineJetPart__ctor(void * this, void * mainPart)",
        ("CBattleEngineJetPart constructor", "ResetConfiguration", "thruster value"),
    ),
    "0x004102a0": (
        "CBattleEngineJetPart__dtor_base",
        "void __thiscall CBattleEngineJetPart__dtor_base(void * this)",
        ("destructor-base loop", "SPtrSet", "weapon ownership"),
    ),
    "0x00410310": (
        "CBattleEngineJetPart__Thrust",
        "void __thiscall CBattleEngineJetPart__Thrust(void * this, float moveY)",
        ("Thrust updates", "hard-forward timing", "last Y input"),
    ),
    "0x00410490": (
        "CBattleEngineJetPart__Turn",
        "void __thiscall CBattleEngineJetPart__Turn(void * this, float moveX)",
        ("yaw and roll velocity", "configuration turn rate", "transform-start interpolation"),
    ),
    "0x00410670": (
        "CBattleEngineJetPart__Pitch",
        "void __thiscall CBattleEngineJetPart__Pitch(void * this, float moveY)",
        ("Pitch applies", "pitch velocity", "transform-start interpolation"),
    ),
    "0x00410740": (
        "CBattleEngineJetPart__YawLeft",
        "void __thiscall CBattleEngineJetPart__YawLeft(void * this, float moveX)",
        ("hard-left timing", "left barrel roll", "strafing acceleration"),
    ),
    "0x004109d0": (
        "CBattleEngineJetPart__YawRight",
        "void __thiscall CBattleEngineJetPart__YawRight(void * this, float moveX)",
        ("hard-right timing", "right barrel roll", "strafing acceleration"),
    ),
    "0x004114d0": (
        "CBattleEngineJetPart__Gravity",
        "float __thiscall CBattleEngineJetPart__Gravity(void * this)",
        ("small gravity factor", "energy field", "returns 0.0"),
    ),
    "0x00411b70": (
        "CBattleEngineJetPart__IsStateMachineActive",
        "int __thiscall CBattleEngineJetPart__IsStateMachineActive(void * this)",
        ("CBattleEngine::Morph", "+0x2c or +0x48", "runtime morph behavior"),
    ),
    "0x004124d0": (
        "CBattleEngineJetPart__GetCurrentWeaponNameField04",
        "char * __thiscall CBattleEngineJetPart__GetCurrentWeaponNameField04(void * this)",
        ("CBattleEngine__ChangeWeapon", "+0x57c", "field +0x04"),
    ),
}

DOC_TOKENS = (
    "Wave1139",
    "wave1139-battleengine-jetpart-current-risk-review",
    "229/1179 = 19.42%",
    "10 current-risk rows",
    "1 function-boundary recovery",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 950",
    "current risk candidates: 6166",
    "BattleEngine JetPart movement/gravity current-risk cluster",
    "CBattleEngine__Gravity",
    "fresh Ghidra export",
    "function-boundary recovery",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime jetpart control behavior proven",
    "runtime flight physics proven",
    "runtime morph behavior proven",
    "weapon_fire_breaks_stealth proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 814,
        "pre-decompile/index.tsv": 10,
        "gravity-xref-callsites.tsv": 90,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 833,
        "post-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    gravity_tags = set(tags["0x004074d0"].get("tags", "").split(";"))
    for tag in (
        "static-reaudit",
        "wave1139-battleengine-jetpart-current-risk-review",
        "wave1139-readback-verified",
        "function-boundary-recovered",
        "source-backed",
        "signature-hardened",
        "comment-hardened",
    ):
        require(tag in gravity_tags, f"missing CBattleEngine__Gravity tag: {tag}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    require(
        any(
            normalize_address(row.get("target_addr", "")) == "0x004114d0"
            and normalize_address(row.get("from_function_addr", "")) == "0x004074d0"
            and row.get("from_function") == "CBattleEngine__Gravity"
            for row in xrefs
        ),
        "CBattleEngineJetPart__Gravity xrefs do not resolve through CBattleEngine__Gravity",
        failures,
    )
    require(
        any(
            normalize_address(row.get("target_addr", "")) == "0x004074d0"
            and normalize_address(row.get("from_addr", "")) == "0x005d8a78"
            and row.get("ref_type") == "DATA"
            for row in xrefs
        ),
        "missing CBattleEngine__Gravity vtable/data xref",
        failures,
    )


def check_logs(failures: list[str]) -> None:
    expected = {
        "create-boundary-dry.log": "would_create=1 already_exists=0 renamed=0 would_rename=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "rows=11 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "Wrote 833 function-body instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6411 commented_functions=6411",
        "queue-probe.log": "Total functions: 6411",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1139.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1139_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_progress_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(any(normalize_address(row["address"]) == "0x004074d0" and row["name"] == "CBattleEngine__Gravity" for row in rows), "quality TSV missing recovered boundary", failures)

    risk = read_json(RISK_JSON)
    focused = read_json(FOCUSED_JSON)
    require(risk.get("totalFunctions") == 6411, "current risk total mismatch", failures)
    require(risk.get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(focused.get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress function total mismatch", failures)
    require(progress["functionQuality"]["commentedFunctions"] == 6411, "progress commented mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 229, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "19.42%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 950, "progress remaining mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "progress broad candidates mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        UNIT_CONTRACT,
        BATTLEENGINE_DOC,
        PROGRESS,
        PROGRESS_MIRROR,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1139-battleengine-jetpart-current-risk-review") == r"py -3 tools\wave1139_battleengine_jetpart_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_progress_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1139 BattleEngine JetPart current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1139 BattleEngine JetPart current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
