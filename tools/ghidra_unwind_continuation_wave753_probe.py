#!/usr/bin/env python3
"""Validate Wave753 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave753-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave753_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
HIVEBOSS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HiveBoss.cpp" / "_index.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
IMPOSTER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "imposter.cpp" / "_index.md"
INFANTRY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Infantry.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-221626_post_wave753_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d2c48": "0x0061ba14",
    "0x005d2c53": "0x0061ba1c",
    "0x005d2c70": "0x0061ba44",
    "0x005d2c90": "0x0061ba6c",
    "0x005d2c98": "0x0061ba74",
    "0x005d2cb0": "0x0061ba9c",
    "0x005d2cc6": "0x0061baa4",
    "0x005d2cdc": "0x0061baac",
    "0x005d2d00": "0x0061bad4",
    "0x005d2d16": "0x0061badc",
    "0x005d2d40": "0x0061bb04",
    "0x005d2d59": "0x0061bb0c",
    "0x005d2d80": "0x0061bb34",
    "0x005d2d88": "0x0061bb3c",
    "0x005d2d90": "0x0061bb44",
    "0x005d2d98": "0x0061bb4c",
    "0x005d2db0": "0x0061bb74",
    "0x005d2dd0": "0x0061bb9c",
    "0x005d2df0": "0x0061bbc4",
    "0x005d2e10": "0x0061bbec",
    "0x005d2e26": "0x0061bbf4",
    "0x005d2e2e": "0x0061bbfc",
    "0x005d2e44": "0x0061bc04",
    "0x005d2e70": "0x0061bc2c",
    "0x005d2e78": "0x0061bc34",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave753",
    "wave753-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

STRING_EXPECTATIONS = {
    "string-0062cc98.tsv": r"[maintainer-local-source-export-root]\HiveBoss.cpp",
    "string-0062ce78.tsv": r"[maintainer-local-source-export-root]\Hud.cpp",
    "string-0062d3f0.tsv": r"[maintainer-local-source-export-root]\imposter.cpp",
    "string-0062d4a8.tsv": r"[maintainer-local-source-export-root]\Infantry.cpp",
}

COMMENT_TOKENS = {
    "0x005d2c48": ("Wave753 static read-back", "CDXLandscape__FreeObjectCallback", "0x0061ba14"),
    "0x005d2c53": ("Wave753 static read-back", "CUnitAI__FreeOwnedObjects_10_18", "0x0061ba1c"),
    "0x005d2c90": ("Wave753 static read-back", "CMonitor__Shutdown_Thunk", "0x0061ba6c"),
    "0x005d2cb0": ("Wave753 static read-back", "HiveBoss.cpp", "0x0062cc98", "0x21"),
    "0x005d2d00": ("Wave753 static read-back", "Hud.cpp", "0x0062ce78", "0x5d"),
    "0x005d2d80": ("Wave753 static read-back", "CSPtrSet__Clear", "EBP-0x4c"),
    "0x005d2db0": ("Wave753 static read-back", "DeviceObject__ctor_like_00512d50", "exact helper semantics"),
    "0x005d2df0": ("Wave753 static read-back", "imposter.cpp", "0x0062d3f0", "0x29"),
    "0x005d2e10": ("Wave753 static read-back", "Infantry.cpp", "0x0062d4a8", "0x1c"),
    "0x005d2e26": ("Wave753 static read-back", "CCollisionSeekingRound__Destructor", "0x0061bbf4"),
    "0x005d2e70": ("Wave753 static read-back", "CMonitor__Shutdown", "0x0061bc2c"),
    "0x005d2e78": ("Wave753 static read-back", "CGenericActiveReader__dtor", "0x0061bc34"),
}

CORE_ANCHORS = (
    "Wave753 unwind continuation",
    "unwind-continuation-wave753",
    "0x005d2c48 Unwind@005d2c48",
    "0x005d2cb0 Unwind@005d2cb0",
    "0x005d2d00 Unwind@005d2d00",
    "0x005d2d80 Unwind@005d2d80",
    "0x005d2df0 Unwind@005d2df0",
    "0x005d2e10 Unwind@005d2e10",
    "0x005d2e78 Unwind@005d2e78",
    "0x005d2e83 Unwind@005d2e83",
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
        "pre-instructions.tsv": 725,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 925,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 9,
        "post-helper-metadata.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in (
        "CDXLandscape__FreeObjectCallback",
        "CUnitAI__FreeOwnedObjects_10_18",
        "CMonitor__Shutdown_Thunk",
        "OID__FreeObject_Callback",
        "CSPtrSet__Clear",
        "DeviceObject__ctor_like_00512d50",
        "CCollisionSeekingRound__Destructor",
        "CMonitor__Shutdown",
        "CGenericActiveReader__dtor",
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
        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ("Wave753 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only")):
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
        "post-instructions.log": "Wrote 925 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=9 found=9 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4687",
        "queue-probe.log": "Commentless functions: 1411",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave753.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave753_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1411, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 888, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d2e83", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d2e83", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4687, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4629, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 168168327 or backup.get("totalBytes") == 168168327.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    function_docs = {
        HIVEBOSS_DOC: ("Wave753", "unwind-continuation-wave753", "0x005d2cb0 Unwind@005d2cb0", "0x0062cc98", BACKUP_PATH),
        HUD_DOC: ("Wave753", "unwind-continuation-wave753", "0x005d2d00 Unwind@005d2d00", "0x005d2d80 Unwind@005d2d80", BACKUP_PATH),
        IMPOSTER_DOC: ("Wave753", "unwind-continuation-wave753", "0x005d2df0 Unwind@005d2df0", "0x0062d3f0", BACKUP_PATH),
        INFANTRY_DOC: ("Wave753", "unwind-continuation-wave753", "0x005d2e10 Unwind@005d2e10", "0x005d2e78 Unwind@005d2e78", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave753") == r"py -3 tools\ghidra_unwind_continuation_wave753_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave753 unwind continuation" for row in ledger_rows), "missing Wave753 ledger row", failures)
    require(any(row.get("task") == "Wave753 unwind continuation" and row.get("attempt_id") == 20408 for row in attempts), "missing Wave753 attempt row", failures)


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
        print("Wave753 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave753 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
