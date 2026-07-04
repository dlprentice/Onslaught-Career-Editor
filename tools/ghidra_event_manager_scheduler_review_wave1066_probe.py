#!/usr/bin/env python3
"""Validate Wave1066 EventManager scheduler tag-normalization artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1066-event-manager-scheduler-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_event_manager_scheduler_review_wave1066_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1066_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "eventmanager.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "scheduledevent.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

EXPECTED_SIGNATURES = {
    "0x0044afa0": ("CEventManager__ctor", "void * __fastcall CEventManager__ctor(void * this)"),
    "0x0044afe0": ("CEventManager__scalar_deleting_dtor", "void * __thiscall CEventManager__scalar_deleting_dtor(void * this, uchar free_flag)"),
    "0x0044b000": ("CEventManager__dtor", "void __fastcall CEventManager__dtor(void * this)"),
    "0x0044b060": ("CEventManager__Init", "void __fastcall CEventManager__Init(void * this)"),
    "0x0044b1f0": ("CEventManager__Shutdown", "void __fastcall CEventManager__Shutdown(void * this)"),
    "0x0044b2a0": ("CEventManager__GetNextFreeEvent", "void * __fastcall CEventManager__GetNextFreeEvent(void * this)"),
    "0x0044b2d0": ("CEventManager__AddEvent_TimeFromNow", "void __thiscall CEventManager__AddEvent_TimeFromNow(void * this, float * time_from_now, int event_num, void * to_call, int start_or_end, void * data, void * re_use_event)"),
    "0x0044b310": ("CEventManager__AddEvent_ScheduledEvent", "void __thiscall CEventManager__AddEvent_ScheduledEvent(void * this, void * event)"),
    "0x0044b5c0": ("CEventManager__Update", "void __fastcall CEventManager__Update(void * this)"),
    "0x0044b600": ("CEventManager__AdvanceTime", "int __fastcall CEventManager__AdvanceTime(void * this)"),
    "0x0044b640": ("CEventManager__Flush", "void __fastcall CEventManager__Flush(void * this)"),
    "0x004de1f0": ("CScheduledEvent__Set", "void __thiscall CScheduledEvent__Set(void * this, short event_num, float * time, void * to_call, void * data)"),
    "0x004de230": ("CScheduledEvent__dtor", "void __fastcall CScheduledEvent__dtor(void * this)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "event-manager-scheduler-review-wave1066",
    "wave1066-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-reviewed",
    "signature-reviewed",
    "event-manager",
    "scheduler",
}

EXPECTED_XREFS = {
    ("0x0044afa0", "0x0044af75", "UNCONDITIONAL_CALL"),
    ("0x0044afe0", "0x005db28c", "DATA"),
    ("0x0044b060", "0x0046630b", "UNCONDITIONAL_CALL"),
    ("0x0044b060", "0x0046c587", "UNCONDITIONAL_CALL"),
    ("0x0044b1f0", "0x004f01dd", "UNCONDITIONAL_CALL"),
    ("0x0044b2d0", "0x00470018", "UNCONDITIONAL_CALL"),
    ("0x0044b5c0", "0x00466bfe", "UNCONDITIONAL_CALL"),
    ("0x0044b600", "0x0046eb5d", "UNCONDITIONAL_CALL"),
    ("0x0044b640", "0x0046ebce", "UNCONDITIONAL_CALL"),
    ("0x004de1f0", "0x0044b4ab", "UNCONDITIONAL_CALL"),
    ("0x004de230", "0x0044b115", "DATA"),
    ("0x004de230", "0x0044b26b", "DATA"),
}

DOC_TOKENS = (
    "Wave1066",
    "event-manager-scheduler-review-wave1066",
    "0x0044afa0 CEventManager__ctor",
    "0x0044b060 CEventManager__Init",
    "0x0044b2d0 CEventManager__AddEvent_TimeFromNow",
    "0x0044b310 CEventManager__AddEvent_ScheduledEvent",
    "0x0044b600 CEventManager__AdvanceTime",
    "0x0044b640 CEventManager__Flush",
    "0x004de1f0 CScheduledEvent__Set",
    "0x004de230 CScheduledEvent__dtor",
    "812/1408 = 57.67%",
    "1232/1560 = 78.97%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "tag normalization",
)

OVERCLAIMS = (
    "runtime event scheduling behavior proven",
    "runtime scheduler behavior proven",
    "runtime flush behavior proven",
    "runtime dispatch behavior proven",
    "runtime gameplay behavior proven",
    "rebuild parity proven",
    "exact source-layout identity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def norm(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 13,
        "primary-tags.tsv": 13,
        "primary-xrefs.tsv": 47,
        "primary-instructions.tsv": 549,
        "primary-decompile/index.tsv": 13,
        "context-metadata.tsv": 11,
        "context-tags.tsv": 11,
        "context-xrefs.tsv": 573,
        "context-instructions.tsv": 993,
        "context-decompile/index.tsv": 11,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 47,
        "post-instructions.tsv": 549,
        "post-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_tags = {norm(row["address"]): row.get("tags", "") for row in read_tsv(BASE / "primary-tags.tsv")}
    for address in EXPECTED_SIGNATURES:
        require(pre_tags.get(address, "") == "", f"pre tag row unexpectedly populated {address}", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    tags = {norm(row["address"]): set(row.get("tags", "").split(";")) for row in read_tsv(BASE / "post-tags.tsv")}
    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)
        require(COMMON_TAGS.issubset(tags.get(address, set())), f"post tags missing {address}", failures)

    xrefs = {
        (norm(row.get("target_addr", "")), norm(row.get("from_addr", "")), row.get("ref_type"))
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }
    for target, source, ref_type in EXPECTED_XREFS:
        require((target, source, ref_type) in xrefs, f"missing xref {target} from {source} {ref_type}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=166 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 tags_added=166 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=13 tags_added=0 missing=0 bad=0",
        "primary-metadata.log": "targets=13 found=13 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "primary-xrefs.log": "Wrote 47 rows",
        "primary-instructions.log": "Wrote 549 function-body instruction rows",
        "primary-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "context-metadata.log": "targets=11 found=11 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "context-xrefs.log": "Wrote 573 rows",
        "context-instructions.log": "Wrote 993 function-body instruction rows",
        "context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 47 rows",
        "post-instructions.log": "Wrote 549 function-body instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    require("REPORT: Save succeeded" in apply_text, "apply log missing save-succeeded report", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174721927, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-event-manager-scheduler-review-wave1066")
        == r"py -3 tools\ghidra_event_manager_scheduler_review_wave1066_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1066-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1066 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    task = "Wave1066 event manager scheduler review"
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1066 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20648 for row in attempt_rows), "missing Wave1066 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1066 EventManager scheduler probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1066 EventManager scheduler probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
