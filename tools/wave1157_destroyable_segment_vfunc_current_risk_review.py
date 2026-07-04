#!/usr/bin/env python3
"""Validate Wave1157 destroyable-segment vfunc current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1157-destroyable-segment-vfunc-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1157-destroyable-segment-vfunc-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1157-destroyable-segment-vfunc-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "destroyable-segments-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "destroyable-segments-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1157_destroyable_segment_vfunc_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x00442870": ("CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields", "void __thiscall CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields(void * this, float scaleFactor, float divisor)"),
    "0x00442960": ("CDestroyableSegment__VFunc_03_ApplyDamage", "void __thiscall CDestroyableSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * sourceThing)"),
    "0x00442b20": ("CDestroyableSegment__VFunc_08_HandleSegmentBreak", "void __fastcall CDestroyableSegment__VFunc_08_HandleSegmentBreak(void * this)"),
    "0x00442f60": ("CDestroyableSegment__VFunc_10_SpawnRubbleEffects", "void __fastcall CDestroyableSegment__VFunc_10_SpawnRubbleEffects(void * this)"),
    "0x004434c0": ("CDestroyableCoreSegment__VFunc_07_GetCoreField48", "float __fastcall CDestroyableCoreSegment__VFunc_07_GetCoreField48(void * this)"),
    "0x00443590": ("CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields", "void __thiscall CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields(void * this, float scaleFactor, float divisor)"),
    "0x004435c0": ("CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate", "int __fastcall CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate(void * this)"),
    "0x004435f0": ("CDestroyableCoreSegment__VFunc_03_ApplyDamage", "void __thiscall CDestroyableCoreSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * damageSource)"),
    "0x00443780": ("CDestroyableSwapSegment__VFunc_03_ApplyDamage", "void __thiscall CDestroyableSwapSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * damageSource)"),
    "0x00443810": ("CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak", "void __fastcall CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak(void * this)"),
    "0x00443830": ("CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex", "int __fastcall CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex(void * this)"),
    "0x004439f0": ("CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields", "void __thiscall CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields(void * this, float scaleFactor, float divisor)"),
}

EXPECTED_DATA_XREFS = {
    "0x00442870": {"0x005db058", "0x005db0d8", "0x005db140", "0x005db174"},
    "0x00442960": {"0x005db038"},
    "0x00442b20": {"0x005db04c"},
    "0x00442f60": {"0x005db054", "0x005db094", "0x005db13c", "0x005db170"},
    "0x004434c0": {"0x005db088"},
    "0x00443590": {"0x005db098"},
    "0x004435c0": {"0x005db084"},
    "0x004435f0": {"0x005db078"},
    "0x00443780": {"0x005db154"},
    "0x00443810": {"0x005db168"},
    "0x00443830": {"0x005db158"},
    "0x004439f0": {"0x005db10c"},
}

COMMON_TAGS = {
    "static-reaudit",
    "retail-binary-evidence",
    "destructable-segments",
    "vtable-slot",
}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "AGENTS.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1157",
    "wave1157-destroyable-segment-vfunc-current-risk-review",
    "465/1179 = 39.44%",
    "12 destroyable-segment vfunc current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 714",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "23 xref rows",
    "694 instruction rows",
    "CDestroyableSegment__VFunc_03_ApplyDamage",
    "CDestroyableSegment__VFunc_08_HandleSegmentBreak",
    "CDestroyableSegment__VFunc_10_SpawnRubbleEffects",
    "CDestroyableCoreSegment__VFunc_03_ApplyDamage",
    "CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex",
    "CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime destructable-segment behavior proven",
    "rebuild parity proven",
    "exact layout proven",
    "source identity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 694,
        "pre-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    xrefs_by_target: dict[str, list[dict[str, str]]] = {}
    for row in xrefs:
        xrefs_by_target.setdefault(normalize_address(row.get("target_addr", "")), []).append(row)

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Static retail evidence only", "runtime", "rebuild parity"):
                require(token in comment, f"missing comment boundary token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        actual_data = {normalize_address(xref.get("from_addr", "")) for xref in xrefs_by_target.get(address, []) if xref.get("ref_type") == "DATA"}
        require(EXPECTED_DATA_XREFS[address].issubset(actual_data), f"DATA xrefs missing at {address}", failures)

    actual_ref_types = {row.get("ref_type") for row in xrefs}
    require(actual_ref_types == {"DATA", "UNCONDITIONAL_CALL"}, f"unexpected xref types: {actual_ref_types}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 23 rows",
        "pre-instructions.log": "Wrote 694 function-body instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

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
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1157 Destroyable segment vfunc current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1157-destroyable-segment-vfunc-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 465, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "39.44%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 714, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1157 Destroyable segment vfunc current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1157 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "destroyable contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1157-destroyable-segment-vfunc-current-risk-review")
        == r"py -3 tools\wave1157_destroyable_segment_vfunc_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1157 destroyable-segment vfunc current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1157 destroyable-segment vfunc current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
