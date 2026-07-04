#!/usr/bin/env python3
"""Validate Wave1083 shared unit-family vtable-boundary artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1083-shared-unit-vtable-boundary-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PACKAGE_JSON = ROOT / "package.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
README = ROOT / "release" / "readiness" / "ghidra_shared_unit_vtable_boundary_wave1083_2026-06-02.md"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-114534_post_wave1083_shared_unit_vtable_boundary_verified"

TARGETS = {
    "0x00405d90": ("SharedUnitVFunc__ReturnField130ColorMask_00405d90", "int __thiscall SharedUnitVFunc__ReturnField130ColorMask_00405d90(void * this)", 17),
    "0x00405e60": ("SharedUnitVFunc__ReturnFloat005d8ba0_00405e60", "float __thiscall SharedUnitVFunc__ReturnFloat005d8ba0_00405e60(void * this)", 11),
    "0x004f9260": ("SharedUnitVFunc__BuildField164TargetVectorContext_004f9260", "void __thiscall SharedUnitVFunc__BuildField164TargetVectorContext_004f9260(void * this)", 8),
    "0x004fda90": ("SharedUnitVFunc__FindActiveMemberByField18c_004fda90", "int __thiscall SharedUnitVFunc__FindActiveMemberByField18c_004fda90(void * this)", 10),
    "0x004fdd00": ("SharedUnitVFunc__SetField244ModeAndDispatchF4_004fdd00", "void __thiscall SharedUnitVFunc__SetField244ModeAndDispatchF4_004fdd00(void * this)", 10),
    "0x004fe2b0": ("SharedUnitVFunc__MarkField17cEntriesForName_004fe2b0", "void __thiscall SharedUnitVFunc__MarkField17cEntriesForName_004fe2b0(void * this, void * name)", 10),
    "0x004fe310": ("SharedUnitVFunc__TestField17cEntryNameMatch_004fe310", "int __thiscall SharedUnitVFunc__TestField17cEntryNameMatch_004fe310(void * this, void * name)", 10),
    "0x00417630": ("SharedUnitVFunc__ReturnObject114OrOne_00417630", "int __thiscall SharedUnitVFunc__ReturnObject114OrOne_00417630(void * this)", 10),
    "0x00405e70": ("SharedUnitVFunc__IsField168Null_00405e70", "int __thiscall SharedUnitVFunc__IsField168Null_00405e70(void * this)", 10),
    "0x004fe5c0": ("SharedUnitVFunc__ReturnField164B4ScaledByMode_004fe5c0", "float __thiscall SharedUnitVFunc__ReturnField164B4ScaledByMode_004fe5c0(void * this)", 10),
    "0x00405ea0": ("SharedUnitVFunc__ReturnFloat005d8578_00405ea0", "float __thiscall SharedUnitVFunc__ReturnFloat005d8578_00405ea0(void * this)", 10),
    "0x00405eb0": ("SharedUnitVFunc__CopyVector1cToOut_00405eb0", "void __thiscall SharedUnitVFunc__CopyVector1cToOut_00405eb0(void * this, void * outVector)", 9),
    "0x004fe5f0": ("SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0", "void __thiscall SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0(void * this)", 10),
}

COMMON_TAGS = {
    "static-reaudit",
    "shared-unit-vtable-boundary-review-wave1083",
    "wave1083-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "comment-hardened",
    "signature-hardened",
    "shared-vfunc",
    "unit-family-vtable",
}

CORE_DOCS = [
    README,
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

ANCHORS = (
    "Wave1083",
    "shared-unit-vtable-boundary-review-wave1083",
    "0x00405d90 SharedUnitVFunc__ReturnField130ColorMask_00405d90",
    "0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260",
    "0x004fe5f0 SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0",
    "0x005e3700",
    "0x005dd710",
    "1418/1560 = 90.90%",
    "812/1408 = 57.67%",
    "6307/6307 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "rebuild parity proven",
    "exact source virtual names proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get("status", "")
        counts[status] = counts.get(status, 0) + 1
    return counts


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 425,
        "pre-instructions-around.tsv": 1131,
        "pre-vtable-slots.tsv": 1600,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 425,
        "post-instructions.tsv": 335,
        "post-decompile/index.tsv": 13,
        "post-vtable-slots.tsv": 1600,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    require(status_counts(read_tsv(BASE / "pre-metadata.tsv")) == {"MISSING": 13}, "pre metadata status mismatch", failures)
    require(status_counts(read_tsv(BASE / "pre-tags.tsv")) == {"MISSING": 13}, "pre tags status mismatch", failures)
    require(status_counts(read_tsv(BASE / "post-metadata.tsv")) == {"OK": 13}, "post metadata status mismatch", failures)
    require(status_counts(read_tsv(BASE / "post-decompile" / "index.tsv")) == {"OK": 13}, "post decompile status mismatch", failures)
    require(status_counts(read_tsv(BASE / "pre-vtable-slots.tsv")) == {"OK": 1109, "NO_FUNCTION_AT_POINTER": 491}, "pre vtable status mismatch", failures)
    require(status_counts(read_tsv(BASE / "post-vtable-slots.tsv")) == {"OK": 1244, "NO_FUNCTION_AT_POINTER": 356}, "post vtable status mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    pre_vtable = read_tsv(BASE / "pre-vtable-slots.tsv")
    post_vtable = read_tsv(BASE / "post-vtable-slots.tsv")

    for address, (name, signature, slot_refs) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1083", "Static retail Ghidra", "runtime"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        pre_count = sum(1 for row in pre_vtable if row.get("pointer_raw", "").lower() == address and row.get("status") == "NO_FUNCTION_AT_POINTER")
        post_count = sum(1 for row in post_vtable if row.get("pointer_raw", "").lower() == address and row.get("status") == "OK")
        require(pre_count == slot_refs, f"pre vtable reference count mismatch for {address}", failures)
        require(post_count == slot_refs, f"post vtable reference count mismatch for {address}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 created=13 would_create=0 renamed=0 would_rename=0 signature_updated=13 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "rows=13 missing=0",
        "post-xrefs.log": "Wrote 425 rows",
        "post-instructions.log": "Wrote 335 function-body instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-vtable-slots.log": "rows=1600",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected bad token in {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["status"] == "PASS", "queue status mismatch", failures)
    require(queue["totalFunctions"] == 6307, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174820231, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff mismatch", failures)


def check_docs_and_ledgers(failures: list[str]) -> None:
    for path in CORE_DOCS:
        text = read_text(path)
        for token in ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    script = package.get("scripts", {}).get("test:ghidra-shared-unit-vtable-boundary-wave1083")
    require(script == r"py -3 tools\ghidra_shared_unit_vtable_boundary_wave1083_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1083 shared unit vtable boundary" for row in ledger_rows), "missing Wave1083 ledger row", failures)
    require(any(row.get("task") == "Wave1083 shared unit vtable boundary" and row.get("attempt_id") == 20665 for row in attempt_rows), "missing Wave1083 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs_and_ledgers(failures)

    if failures:
        print("Wave1083 shared unit vtable-boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1083 shared unit vtable-boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
