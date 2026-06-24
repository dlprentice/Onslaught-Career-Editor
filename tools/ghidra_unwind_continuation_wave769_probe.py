#!/usr/bin/env python3
"""Validate Wave769 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave769-unwind-continuation"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave769_2026-05-23.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TREE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "tree.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260523-174151_post_wave769_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d5350": "0x0061dc3c",
    "0x005d5380": "0x0061dc64",
    "0x005d5388": "0x0061dc6c",
    "0x005d53a0": "0x0061dc94",
    "0x005d53c0": "0x0061dcbc",
    "0x005d53e0": "0x0061dce4",
    "0x005d53e8": "0x0061dcec",
    "0x005d53f6": "0x0061dcf4",
    "0x005d5404": "0x0061dcfc",
    "0x005d5412": "0x0061dd04",
    "0x005d5420": "0x0061dd0c",
    "0x005d542e": "0x0061dd14",
    "0x005d543c": "0x0061dd1c",
    "0x005d544a": "0x0061dd24",
    "0x005d5470": "0x0061dd4c",
    "0x005d5478": "0x0061dd54",
    "0x005d5486": "0x0061dd5c",
    "0x005d5494": "0x0061dd64",
    "0x005d54a2": "0x0061dd6c",
    "0x005d54b0": "0x0061dd74",
    "0x005d54be": "0x0061dd7c",
    "0x005d54cc": "0x0061dd84",
    "0x005d54da": "0x0061dd8c",
    "0x005d5500": "0x0061ddb4",
    "0x005d5519": "0x0061ddbc",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave769",
    "wave769-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

HELPER_NAMES = (
    "CActor__dtor_base",
    "CLine__SetBaseVtable_00426360",
    "CSPtrSet__Clear",
    "DeviceObject__ctor_like_00512d50",
    "OID__FreeObject_Callback",
    "CGenericActiveReader__dtor",
    "CParticleManager__RemoveFromGlobalList_Thunk",
)

STRING_EXPECTATIONS = {
    "string-00633a84.tsv": r"C:\dev\ONSLAUGHT2\tree.cpp",
    "string-00633b6c.tsv": r"C:\dev\ONSLAUGHT2\Unit.cpp",
}

COMMENT_TOKENS = {
    "0x005d5350": ("Wave769 static read-back", "tree.cpp", "0x00633a84", "0xf0", "0x07"),
    "0x005d5380": ("Wave769 static read-back", "CLine__SetBaseVtable_00426360", "EBP-0x50"),
    "0x005d5388": ("Wave769 static read-back", "CParticleManager__RemoveFromGlobalList_Thunk", "EBP-0x90"),
    "0x005d53a0": ("Wave769 static read-back", "DeviceObject__ctor_like_00512d50", "Exact helper semantics remain unproven"),
    "0x005d53e0": ("Wave769 static read-back", "CActor__dtor_base", "0x0061dce4"),
    "0x005d53e8": ("Wave769 static read-back", "CGenericActiveReader__dtor", "0x144"),
    "0x005d5404": ("Wave769 static read-back", "CSPtrSet__Clear", "0x17c"),
    "0x005d5470": ("Wave769 static read-back", "CActor__dtor_base", "0x0061dd4c"),
    "0x005d5478": ("Wave769 static read-back", "CGenericActiveReader__dtor", "0x144"),
    "0x005d5494": ("Wave769 static read-back", "CSPtrSet__Clear", "0x17c"),
    "0x005d5500": ("Wave769 static read-back", "Unit.cpp", "0x00633b6c", "0xc0", "0x61"),
    "0x005d5519": ("Wave769 static read-back", "Unit.cpp", "0x00633b6c", "0x139", "0x61"),
}

CORE_ANCHORS = (
    "Wave769 unwind continuation",
    "unwind-continuation-wave769",
    "0x005d5350 Unwind@005d5350",
    "0x005d5380 Unwind@005d5380",
    "0x005d53e0 Unwind@005d53e0",
    "0x005d5404 Unwind@005d5404",
    "0x005d5470 Unwind@005d5470",
    "0x005d5494 Unwind@005d5494",
    "0x005d5500 Unwind@005d5500",
    "0x005d5519 Unwind@005d5519",
    "0x005d5532 Unwind@005d5532",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
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
    return f"Unwind@{address[2:]}"


def expected_signature(address: str) -> str:
    return f"void __cdecl {expected_name(address)}(void)"


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
        "pre-instructions.tsv": 2225,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 2225,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 7,
        "post-helper-metadata.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in HELPER_NAMES:
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, expected_scope in TARGET_XREFS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected_name(address), f"name mismatch at {address}", failures)
            require(row.get("signature") == expected_signature(address), f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            default_tokens = ("Wave769 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only")
            for token in COMMENT_TOKENS.get(address, default_tokens):
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
            require(dec.get("signature") == expected_signature(address), f"decompile signature mismatch at {address}", failures)
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
        "post-instructions.log": "Wrote 2225 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=7 found=7 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5087",
        "queue-probe.log": "Commentless functions: 1011",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave769.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave769_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1011, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 488, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d5532", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d5532", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5087, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5029, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 169708423 or backup.get("totalBytes") == 169708423.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        TREE_DOC: ("Wave769", "unwind-continuation-wave769", "0x005d5350 Unwind@005d5350", "0x005d5380 Unwind@005d5380", BACKUP_PATH),
        UNIT_DOC: ("Wave769", "unwind-continuation-wave769", "0x005d5500 Unwind@005d5500", "0x005d5519 Unwind@005d5519", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave769") == r"py -3 tools\ghidra_unwind_continuation_wave769_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave769 unwind continuation" for row in ledger_rows), "missing Wave769 ledger row", failures)
    require(any(row.get("task") == "Wave769 unwind continuation" and row.get("attempt_id") == 20424 for row in attempts), "missing Wave769 attempt row", failures)


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
        print("Wave769 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave769 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
