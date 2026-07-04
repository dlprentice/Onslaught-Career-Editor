#!/usr/bin/env python3
"""Validate Wave786 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave786-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave786_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-005950_post_wave786_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d7a96": "0x0061fdf4",
    "0x005d7aa4": "0x0061fdfc",
    "0x005d7ac0": "0x0061fe24",
    "0x005d7ac8": "0x0061fe2c",
    "0x005d7ad6": "0x0061fe34",
    "0x005d7ae4": "0x0061fe3c",
    "0x005d7b00": "0x0061fe64",
    "0x005d7b20": "0x0061fe8c",
    "0x005d7b40": "0x0061feb4",
    "0x005d7b4b": "0x0061febc",
    "0x005d7b60": "0x0061fee4",
    "0x005d7b80": "0x0061ff0c",
    "0x005d7b96": "0x0061ff14",
    "0x005d7bac": "0x0061ff1c",
    "0x005d7bc2": "0x0061ff24",
    "0x005d7bf0": "0x0061ff4c",
    "0x005d7bf8": "0x0061ff54",
    "0x005d7c20": "0x0061ff7c",
    "0x005d7c28": "0x0061ff84",
    "0x005d7c50": "0x0061ffac",
    "0x005d7c70": "0x0061ffd4",
    "0x005d7ca0": "0x0061fffc",
    "0x005d7cd0": "0x00620024",
    "0x005d7cf0": "0x0062004c",
    "0x005d7d09": "0x00620054",
}

TARGET_NAMES = {

}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave786",
    "wave786-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

HELPER_NAMES = {
    "DebugTrace",
    "CMemoryManager__DeleteTagList",
    "DeviceObject__ctor_like_00512d50",
    "CDXMemBuffer__dtor_base",
    "CChunkReader__dtor_base",
    "CFrontEndPage__DeActiveNotification",
    "OID__FreeObject_Callback",
    "CRT__EhVectorDestructorIterator_WithUnwind",
}

COMMENT_TOKENS = {
    "0x005d7a96": ("Wave786 static read-back", "DebugTrace", "0x0061fdf4", "(*(EBP-0x10))+0xae0 via ECX before jumping to the retail stub"),
    "0x005d7aa4": ("Wave786 static read-back", "DebugTrace", "0x0061fdfc", "(*(EBP-0x10))+0x13ac via ECX before jumping to the retail stub"),
    "0x005d7ac0": ("Wave786 static read-back", "CMemoryManager__DeleteTagList", "0x0061fe24", "*(EBP-0x10)"),
    "0x005d7ac8": ("Wave786 static read-back", "DebugTrace", "0x0061fe2c", "(*(EBP-0x10))+0x214 via ECX before jumping to the retail stub"),
    "0x005d7ad6": ("Wave786 static read-back", "DebugTrace", "0x0061fe34", "(*(EBP-0x10))+0xae0 via ECX before jumping to the retail stub"),
    "0x005d7ae4": ("Wave786 static read-back", "DebugTrace", "0x0061fe3c", "(*(EBP-0x10))+0x13ac via ECX before jumping to the retail stub"),
    "0x005d7b00": ("Wave786 static read-back", "DeviceObject__ctor_like_00512d50", "0x0061fe64", "*(EBP-0x10)"),
    "0x005d7b20": ("Wave786 static read-back", "DeviceObject__ctor_like_00512d50", "0x0061fe8c", "*(EBP-0x10)"),
    "0x005d7b40": ("Wave786 static read-back", "CDXMemBuffer__dtor_base", "0x0061feb4", "EBP-0x140"),
    "0x005d7b4b": ("Wave786 static read-back", "CChunkReader__dtor_base", "0x0061febc", "EBP-0x150"),
    "0x005d7b60": ("Wave786 static read-back", "CFrontEndPage__DeActiveNotification", "0x0061fee4", "the deactivating front-end page pointer"),
    "0x005d7b80": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061ff0c", "*(EBP+0x4)"),
    "0x005d7b96": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061ff14", "*(EBP+0x4)"),
    "0x005d7bac": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061ff1c", "*(EBP+0x4)"),
    "0x005d7bc2": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061ff24", "*(EBP+0x4)"),
    "0x005d7bf0": ("Wave786 static read-back", "DeviceObject__ctor_like_00512d50", "0x0061ff4c", "*(EBP-0x10)"),
    "0x005d7bf8": ("Wave786 static read-back", "CRT__EhVectorDestructorIterator_WithUnwind", "0x0061ff54", "the 0x20-element CGenericActiveReader array at (*(EBP-0x10))+0x0c"),
    "0x005d7c20": ("Wave786 static read-back", "DeviceObject__ctor_like_00512d50", "0x0061ff7c", "*(EBP-0x10)"),
    "0x005d7c28": ("Wave786 static read-back", "CRT__EhVectorDestructorIterator_WithUnwind", "0x0061ff84", "the 0x20-element CGenericActiveReader array at (*(EBP-0x10))+0x0c"),
    "0x005d7c50": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061ffac", "*(EBP-0x10)"),
    "0x005d7c70": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061ffd4", "*(EBP-0x10)"),
    "0x005d7ca0": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0061fffc", "*(EBP-0x6c)"),
    "0x005d7cd0": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x00620024", "*(EBP-0x10)"),
    "0x005d7cf0": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x0062004c", "*(EBP-0x10)"),
    "0x005d7d09": ("Wave786 static read-back", "OID__FreeObject_Callback", "0x00620054", "*(EBP-0x10)"),
}

CORE_ANCHORS = (
    "Wave786 unwind continuation",
    "unwind-continuation-wave786",
    "0x005d7a96 Unwind@005d7a96",
    "0x005d7ac0 Unwind@005d7ac0",
    "0x005d7b40 Unwind@005d7b40",
    "0x005d7b60 Unwind@005d7b60",
    "0x005d7b80 Unwind@005d7b80",
    "0x005d7bf8 Unwind@005d7bf8",
    "0x005d7c28 Unwind@005d7c28",
    "0x005d7d09 Unwind@005d7d09",
    "0x005d7d30 Unwind@005d7d30",
    "0x0042f220 CSPtrSet__Clear",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260524-005950_post_wave786_unwind_continuation_verified",
)

OVERCLAIM_TOKENS = (
    "runtime exception behavior proven",
    "runtime cleanup behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def expected_name(address: str) -> str:
    return TARGET_NAMES.get(address, f"Unwind@{address[2:]}")


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
        "pre-metadata.tsv": 25,
        "pre-tags.tsv": 25,
        "pre-xrefs.tsv": 25,
        "pre-instructions.tsv": 2125,
        "pre-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 8,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 2125,
        "post-decompile/index.tsv": 25,
        "post-helper-metadata.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in HELPER_NAMES:
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, expected_scope in TARGET_XREFS.items():
        name = expected_name(address)
        signature = f"void __cdecl {name}(void)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ("Wave786 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only")):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

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

        xref_row = xrefs.get(address)
        require(xref_row is not None, f"missing xref for {address}", failures)
        if xref_row is not None:
            require(normalize_address(xref_row.get("from_addr", "")) == expected_scope, f"xref scope mismatch at {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 2125 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=8 found=8 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5512",
        "queue-probe.log": "Commentless functions: 586",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave786.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave786_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 586, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 63, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d7d30", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d7d30", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5512, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5454, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171150215, 171150215.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave786") == r"py -3 tools\ghidra_unwind_continuation_wave786_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave786 unwind continuation" for row in ledger_rows), "missing Wave786 ledger row", failures)
    require(any(row.get("task") == "Wave786 unwind continuation" and row.get("attempt_id") == 20441 for row in attempts), "missing Wave786 attempt row", failures)


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
        print("Wave786 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave786 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
