#!/usr/bin/env python3
"""Validate Wave607 CDXMemoryManager core Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave607-memory-landscape-00548ec0"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxmemorymanager_core_wave607_2026-05-19.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MEMORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MemoryManager.cpp" / "_index.md"
OIDS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "oids.cpp" / "_index.md"
POLYBUCKET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PolyBucket.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

EXPECTED_SIGNATURES = {
    "0x00548ec0": ("CMemoryManager__DeleteTagList_CtorUnwind", "void __thiscall CMemoryManager__DeleteTagList_CtorUnwind(void * this)"),
    "0x00548f90": ("CDXMemoryManager__Init", "uint __thiscall CDXMemoryManager__Init(void * this, uint heap_size)"),
    "0x005490c0": ("CDXMemoryManager__Shutdown", "void __thiscall CDXMemoryManager__Shutdown(void * this)"),
    "0x005490e0": ("CDXMemoryManager__Alloc", "void * __thiscall CDXMemoryManager__Alloc(void * this, uint size, int mem_type, char * source_file, uint line)"),
    "0x005491b0": ("CDXMemoryManager__ReAlloc", "void * __thiscall CDXMemoryManager__ReAlloc(void * this, void * mem, uint new_size)"),
    "0x005492d0": ("CDXMemoryManager__CalcAndShowDeltas", "void __thiscall CDXMemoryManager__CalcAndShowDeltas(void * this)"),
    "0x00549400": ("CMemoryManager__DeleteTagList", "void __thiscall CMemoryManager__DeleteTagList(void * this)"),
}

EXPECTED_TAGS = {
    "0x00548ec0": {"cmemorymanager", "tag-list", "ctor-unwind", "ret-c3"},
    "0x00548f90": {"cdxmemorymanager", "init", "ret-0x4", "heap-bootstrap"},
    "0x005490c0": {"cdxmemorymanager", "shutdown", "tailcall", "default-heap"},
    "0x005490e0": {"cdxmemorymanager", "alloc", "ret-0x10", "heap-dispatch", "oom-codes"},
    "0x005491b0": {"cdxmemorymanager", "realloc", "ret-0x8", "heap-dispatch", "tiny-heap"},
    "0x005492d0": {"cdxmemorymanager", "memory-deltas", "ret-c3", "trace"},
    "0x00549400": {"cmemorymanager", "tag-list", "ret-c3", "destructor-helper"},
}

COMMENT_TOKENS = {
    "0x00548ec0": ("not CDXEngine", "constructor EH/unwind", "CMemoryManager::mFirstTag", "CMemoryTag::mNext", "Static retail decompile/instruction evidence"),
    "0x00548f90": ("RET 0x4", "CLTShell__WinMain", "global MEM_MANAGER", "one stack heap_size", "default heap", "dump/sound/thing heaps"),
    "0x005490c0": ("not CDXEngine", "clears global mInit", "0x009c6334", "tail-jumps into CMemoryHeap__Shutdown"),
    "0x005490e0": ("not OID", "RET 0x10", "1384 xrefs", "this+0x10 + mem_type*4", "0xcd", "0xd0"),
    "0x005491b0": ("not a CPolyBucket", "RET 0x8", "CPolyBucket/FlexArray callsites", "CMemoryBlock header", "mem-0x10", "mem-0x8"),
    "0x005492d0": ("ECX-only", "debug-trace", "CMemoryHeap__CalcAndShowDeltas", "default, dump, and thing heaps"),
    "0x00549400": ("not CDXEngine", "simple CMemoryManager tag-list delete helper", "CMemoryManager::mFirstTag", "unwind metadata"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxmemorymanager-core-wave607",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "owner-corrected",
}
OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully recovered", "fully reverse-engineered")


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


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "Function not found", "Input file not found", "Read-back signature mismatch", "Save blocked"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 6, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 7, "skipped": 0, "renamed": 6, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    for log_name in (
        "ExportFunctionMetadataByAddress-targets.log",
        "ExportFunctionTagsByAddress-targets.log",
        "ExportXrefsForAddresses-targets.log",
        "ExportInstructionsAroundAddresses-targets.log",
        "ExportFunctionsByAddressDecompile-targets.log",
    ):
        text = read_text(POST / log_name)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata_after.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags_after.tsv")}
    if set(metadata_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata_rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], COMMENT_TOKENS[address], failures)
        require_tokens(f"{address} comment", row["comment"], ("BEA patching", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tag_rows.get(address)
        if not tag_row:
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = (COMMON_TAGS | EXPECTED_TAGS[address]) - actual_tags
        if tag_row["name"] != name:
            failures.append(f"{address} tag name mismatch: {tag_row['name']} != {name}")
        if tag_row["status"] != "OK":
            failures.append(f"{address} tag status mismatch: {tag_row['status']}")
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "post/xrefs_after.tsv": 1402,
        "post/instructions_after.tsv": 2695,
        "post/decomp_after/index.tsv": 7,
    }
    actual_counts = {
        "post/xrefs_after.tsv": len(read_tsv_rows(POST / "xrefs_after.tsv")),
        "post/instructions_after.tsv": len(read_tsv_rows(POST / "instructions_after.tsv")),
        "post/decomp_after/index.tsv": len(read_tsv_rows(POST / "decomp_after" / "index.tsv")),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_instructions(failures: list[str]) -> None:
    xref_text = read_text(POST / "xrefs_after.tsv")
    require_tokens(
        "xrefs_after",
        xref_text,
        (
            "CDXMemoryManager__Alloc",
            "CDXMemBuffer__OpenWrite",
            "CLTShell__WinMain",
            "CConsole__RegisterCommand",
            "CPolyBucket__Load",
            "CFlexArray__Resize",
            "CExplosionInitThing__BuildGridPathWithFallbackSearch",
            "CDXMemoryManager__ReAlloc",
            "CMemoryManager__DeleteTagList",
            "Unwind@005d7a80",
        ),
        failures,
    )
    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens(
        "instructions_after",
        instruction_text,
        ("RET\t0x10", "RET\t0x8", "JMP\t0x004a17b0", "0x009c6334", "0x65108c", "0x6510b4", "0x65109c", "PUSH\t0xcd", "PUSH\t0xd0"),
        failures,
    )
    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (POST / "decomp_after").glob("*.c"))
    require_tokens(
        "decomp_after",
        decompile_text,
        (
            "CMemoryManager::mFirstTag",
            "CDXMemoryManager__Init",
            "CMemoryHeap__Init",
            "DAT_009c6334",
            "CDXMemoryManager__Alloc",
            "FatalError_LocalizedStringId",
            "CMemoryHeap__ReallocTiny",
            "CDXMemoryManager__ReAlloc",
            "CMemoryHeap__CalcAndShowDeltas",
            "CMemoryManager__DeleteTagList",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "G:\\GhidraBackups\\BEA_20260519-211737_post_wave607_cdxmemorymanager_core_verified":
        failures.append(f"backup path mismatch: {backup.get('backupPath')}")
    expected_backup = {"fileCount": 19, "totalBytes": 161418119, "diffCount": 0}
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2977,
        "undefinedSignatureCount": 1304,
        "paramSignatureCount": 1065,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x0054b800":
        failures.append("queue head mismatch: expected 0x0054b800")

    rows = read_tsv_rows(QUALITY_TSV)
    strict = [
        row for row in rows
        if row["comment"].strip()
        and not row["signature"].startswith("undefined ")
        and not re.search(r"\bparam_[0-9]+", row["signature"])
    ]
    if len(rows) != 6093:
        failures.append(f"quality row count mismatch: {len(rows)} != 6093")
    if len(strict) != 3071:
        failures.append(f"strict clean signature proxy mismatch: {len(strict)} != 3071")


def check_docs_and_logs(failures: list[str]) -> None:
    package_json = read_text(PACKAGE_JSON)
    public_note = read_text(PUBLIC_NOTE)
    memory_doc = read_text(MEMORY_DOC)
    oids_doc = read_text(OIDS_DOC)
    polybucket_doc = read_text(POLYBUCKET_DOC)
    fn_index = read_text(FUNCTION_INDEX)
    campaign = read_text(CAMPAIGN)
    backlog = read_text(BACKLOG)

    require_tokens(
        "package.json",
        package_json,
        ("test:ghidra-cdxmemorymanager-core-wave607", "tools\\ghidra_cdxmemorymanager_core_wave607_probe.py --check"),
        failures,
    )

    common_doc_tokens = (
        "Wave607",
        "CMemoryManager__DeleteTagList_CtorUnwind",
        "CDXMemoryManager__Init",
        "CDXMemoryManager__Shutdown",
        "CDXMemoryManager__Alloc",
        "CDXMemoryManager__ReAlloc",
        "CDXMemoryManager__CalcAndShowDeltas",
        "CMemoryManager__DeleteTagList",
        "0x0054b800 CHudComponent__RenderPassEntry",
        "2977",
        "commentless",
        "1304",
        "exact-undefined",
        "1065",
        "G:\\GhidraBackups\\BEA_20260519-211737_post_wave607_cdxmemorymanager_core_verified",
    )
    for label, text in {
        "public note": public_note,
        "MemoryManager doc": memory_doc,
        "function index": fn_index,
        "campaign": campaign,
        "backlog": backlog,
    }.items():
        require_tokens(label, text, common_doc_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    require_tokens("OIDs doc", oids_doc, ("Wave607", "retired", "OID__AllocObject", "CDXMemoryManager__Alloc", "not OID-owned"), failures)
    require_tokens("PolyBucket doc", polybucket_doc, ("Wave607", "CDXMemoryManager__ReAlloc", "not CPolyBucket-owned", "caller evidence"), failures)
    require_tokens("public note", public_note, ("updated=7", "renamed=6", "1402 xref rows", "2695 instruction rows", "DiffCount=0", "Strict clean-signature proxy"), failures)

    ledger_rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not any(row.get("task") == "Ghidra CDXMemoryManager core Wave607 signature/comment/owner hardening" and row.get("status") == "completed" for row in ledger_rows):
        failures.append("ledger missing Wave607 completed row")

    attempt_rows = [json.loads(line) for line in ATTEMPT_LOG.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    wave_attempt = next((row for row in attempt_rows if row.get("attempt_id") == 20262), None)
    if not wave_attempt:
        failures.append("attempt log missing attempt_id 20262")
    else:
        require_tokens("attempt 20262 notes", wave_attempt.get("notes", ""), ("Wave607", "renamed=6", "0x0054b800"), failures)

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 1003, "attempt_rows": 20263, "completed": 994, "pending": 9}
    counters = tracking.get("counters", {})
    for key, expected in expected_counters.items():
        if counters.get(key) != expected:
            failures.append(f"tracking counter {key} mismatch: {counters.get(key)} != {expected}")
    if tracking.get("next_attempt_id") != 20263:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20263")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave607", "0x0054b800", "CHudComponent__RenderPassEntry"), failures)


def run_check() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs_and_instructions(failures)
        check_backup_and_queue(failures)
        check_docs_and_logs(failures)
    except Exception as exc:  # noqa: BLE001 - probe should report unexpected read failures.
        failures.append(f"probe exception: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave607 CDXMemoryManager core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave607 CDXMemoryManager core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
