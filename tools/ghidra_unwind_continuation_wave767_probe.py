#!/usr/bin/env python3
"""Validate Wave767 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave767-unwind-continuation"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave767_2026-05-23.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
SQUADRELAXED_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadRelaxed.cpp" / "_index.md"
STATICSHADOWS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "StaticShadows.cpp" / "_index.md"
SQUADNORMAL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
SUBMARINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Submarine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260523-164622_post_wave767_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d4e00": "0x0061d6a4",
    "0x005d4e30": "0x0061d6cc",
    "0x005d4e60": "0x0061d6f4",
    "0x005d4e90": "0x0061d71c",
    "0x005d4e98": "0x0061d724",
    "0x005d4eb0": "0x0061d74c",
    "0x005d4eb8": "0x0061d754",
    "0x005d4ed0": "0x0061d77c",
    "0x005d4ef0": "0x0061d7a4",
    "0x005d4f0c": "0x0061d7ac",
    "0x005d4f28": "0x0061d7b4",
    "0x005d4f33": "0x0061d7bc",
    "0x005d4f3e": "0x0061d7c4",
    "0x005d4f49": "0x0061d7cc",
    "0x005d4f54": "0x0061d7d4",
    "0x005d4f5f": "0x0061d7dc",
    "0x005d4f6a": "0x0061d7e4",
    "0x005d4f75": "0x0061d7ec",
    "0x005d4f90": "0x0061d814",
    "0x005d4fc0": "0x0061d83c",
    "0x005d4fd6": "0x0061d844",
    "0x005d5000": "0x0061d86c",
    "0x005d5008": "0x0061d874",
    "0x005d5013": "0x0061d87c",
    "0x005d5030": "0x0061d8a4",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave767",
    "wave767-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMENT_TOKENS = {
    "0x005d4e00": ("Wave767 static read-back", "SquadNormal.cpp", "0x0063283c", "0x437", "0x08"),
    "0x005d4e30": ("Wave767 static read-back", "SquadNormal.cpp", "0x0063283c", "0x48b", "0x08"),
    "0x005d4e60": ("Wave767 static read-back", "SquadRelaxed.cpp", "0x00632918", "0xa0", "0x08"),
    "0x005d4e90": ("Wave767 static read-back", "CComplexThing__dtor_base", "0x0061d71c"),
    "0x005d4e98": ("Wave767 static read-back", "CGenericActiveReader__dtor", "0x7c"),
    "0x005d4ed0": ("Wave767 static read-back", "CParticleManager__RemoveFromGlobalList_Thunk", "0x0061d77c"),
    "0x005d4ef0": ("Wave767 static read-back", "StaticShadows.cpp", "0x006329f8", "0x18a", "0x70"),
    "0x005d4f0c": ("Wave767 static read-back", "StaticShadows.cpp", "0x006329f8", "0x1a7", "0x61"),
    "0x005d4f28": ("Wave767 static read-back", "CLine__SetBaseVtable_00426360", "EBP-0x31c"),
    "0x005d4f90": ("Wave767 static read-back", "StaticShadows.cpp", "0x006329f8", "0x43d", "0x70"),
    "0x005d4fc0": ("Wave767 static read-back", "Submarine.cpp", "0x00632abc", "0x1d", "0x16"),
    "0x005d4fd6": ("Wave767 static read-back", "Submarine.cpp", "0x00632abc", "0x1e", "0x17"),
    "0x005d5000": ("Wave767 static read-back", "CMonitor__Shutdown", "0x0061d86c"),
    "0x005d5008": ("Wave767 static read-back", "CGenericActiveReader__dtor", "0x0c"),
    "0x005d5013": ("Wave767 static read-back", "CGenericActiveReader__dtor", "0x24"),
    "0x005d5030": ("Wave767 static read-back", "CController__dtor_Thunk", "EBP-0x184"),
}

STRING_EXPECTATIONS = {
    "string-00632918.tsv": r"C:\dev\ONSLAUGHT2\SquadRelaxed.cpp",
    "string-006329f8.tsv": r"C:\dev\ONSLAUGHT2\StaticShadows.cpp",
    "string-00632abc.tsv": r"C:\dev\ONSLAUGHT2\Submarine.cpp",
}

CORE_ANCHORS = (
    "Wave767 unwind continuation",
    "unwind-continuation-wave767",
    "0x005d4e00 Unwind@005d4e00",
    "0x005d4e60 Unwind@005d4e60",
    "0x005d4e90 Unwind@005d4e90",
    "0x005d4ef0 Unwind@005d4ef0",
    "0x005d4f28 Unwind@005d4f28",
    "0x005d4f90 Unwind@005d4f90",
    "0x005d4fc0 Unwind@005d4fc0",
    "0x005d5000 Unwind@005d5000",
    "0x005d5008 Unwind@005d5008",
    "0x005d5013 Unwind@005d5013",
    "0x005d5030 Unwind@005d5030",
    "0x005d5050 Unwind@005d5050",
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
        "pre-instructions.tsv": 925,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 925,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 7,
        "post-helper-metadata.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in (
        "OID__FreeObject_Callback",
        "CGenericActiveReader__dtor",
        "CMonitor__Shutdown",
        "CParticleManager__RemoveFromGlobalList_Thunk",
        "CLine__SetBaseVtable_00426360",
        "CComplexThing__dtor_base",
        "CController__dtor_Thunk",
    ):
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
            for token in COMMENT_TOKENS.get(address, ("Wave767 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only")):
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
        "post-instructions.log": "Wrote 925 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=7 found=7 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5037",
        "queue-probe.log": "Commentless functions: 1061",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave767.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave767_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1061, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 538, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d5050", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d5050", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5037, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4979, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 169511815 or backup.get("totalBytes") == 169511815.0, "backup byte count mismatch", failures)
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
        SQUADNORMAL_DOC: ("Wave767", "unwind-continuation-wave767", "0x005d4e00 Unwind@005d4e00", "0x005d4e30 Unwind@005d4e30", BACKUP_PATH),
        SQUADRELAXED_DOC: ("Wave767", "unwind-continuation-wave767", "0x005d4e60 Unwind@005d4e60", "0x005d4e90 Unwind@005d4e90", "0x005d4ed0 Unwind@005d4ed0", BACKUP_PATH),
        STATICSHADOWS_DOC: ("Wave767", "unwind-continuation-wave767", "0x005d4ef0 Unwind@005d4ef0", "0x005d4f28 Unwind@005d4f28", "0x005d4f90 Unwind@005d4f90", BACKUP_PATH),
        SUBMARINE_DOC: ("Wave767", "unwind-continuation-wave767", "0x005d4fc0 Unwind@005d4fc0", "0x005d5000 Unwind@005d5000", "0x005d5030 Unwind@005d5030", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave767") == r"py -3 tools\ghidra_unwind_continuation_wave767_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave767 unwind continuation" for row in ledger_rows), "missing Wave767 ledger row", failures)
    require(any(row.get("task") == "Wave767 unwind continuation" and row.get("attempt_id") == 20422 for row in attempts), "missing Wave767 attempt row", failures)


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
        print("Wave767 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave767 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
