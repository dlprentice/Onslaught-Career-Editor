#!/usr/bin/env python3
"""Validate Wave614 CDXShadows head Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave614-cdxshadows-head-00552060-00552330"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxshadows_head_wave614_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXSHADOWS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXShadows.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

SIGNATURES = {
    "0x00552060": "void __thiscall CDXShadows__Destructor(void * this)",
    "0x005520f0": "void __thiscall CDXShadows__Init(void * this)",
    "0x00552330": "void __thiscall CDXShadows__InitBlobShadows(void * this)",
}

NAMES = {
    "0x00552060": "CDXShadows__Destructor",
    "0x005520f0": "CDXShadows__Init",
    "0x00552330": "CDXShadows__InitBlobShadows",
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxshadows-wave614",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "callsite-verified",
    "cdxshadows",
}

OVERCLAIM_TOKENS = (
    "runtime shadow behavior proven",
    "runtime blob-shadow rendering proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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
    for bad_token in (
        "LockException",
        "Function not found",
        "Input file not found",
        "BADADDR",
        "MISSING:",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back signature mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave614-dry.log",
        {"updated": 0, "skipped": 3, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave614-apply.log",
        {"updated": 3, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave614-final-dry.log",
        {"updated": 0, "skipped": 3, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_log_tokens = {
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "rows=3 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "targets=3 missing=0",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-callsite-instructions.log": "targets=3 missing=0",
        "queue-snapshot-refresh.log": "total_functions=6093 commented_functions=3159",
    }
    for log_name, token in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, (token,), failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-metadata.tsv")
    if len(rows) != len(SIGNATURES):
        failures.append(f"post-metadata row count mismatch: {len(rows)} != {len(SIGNATURES)}")
        return
    for row in rows:
        address = normalize_address(row["address"])
        if address not in SIGNATURES:
            failures.append(f"unexpected metadata address: {row['address']}")
            continue
        if row["name"] != NAMES[address]:
            failures.append(f"metadata name mismatch for {address}: {row['name']} != {NAMES[address]}")
        if row["signature"] != SIGNATURES[address]:
            failures.append(f"metadata signature mismatch for {address}: {row['signature']} != {SIGNATURES[address]}")
        if row["status"] != "OK":
            failures.append(f"metadata status mismatch for {address}: {row['status']}")
        require_tokens("metadata comment", row["comment"], ("Wave614", "Static retail", "remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"metadata comment overclaims for {address}: {token}")

    tag_rows = read_tsv_rows(BASE / "post-tags.tsv")
    if len(tag_rows) != len(SIGNATURES):
        failures.append(f"post-tags row count mismatch: {len(tag_rows)} != {len(SIGNATURES)}")
        return
    for row in tag_rows:
        address = normalize_address(row["address"])
        tags = set(filter(None, row["tags"].split(";")))
        missing = COMMON_TAGS - tags
        if missing:
            failures.append(f"missing common tags for {address}: {sorted(missing)}")
        if address == "0x00552060" and not {"destructor", "shadow-texture-release", "cshaderbase-unlink"}.issubset(tags):
            failures.append("missing destructor tags for 0x00552060")
        if address == "0x005520f0" and not {"init", "cvar-registration", "cumtexture", "debug-path-00652410"}.issubset(tags):
            failures.append("missing init tags for 0x005520f0")
        if address == "0x00552330" and not {"blob-shadows", "texture-resource", "cvbuftexture", "debug-path-00652410"}.issubset(tags):
            failures.append("missing blob-shadow tags for 0x00552330")


def check_exports(failures: list[str]) -> None:
    counts = {
        "post-xrefs.tsv": (len(read_tsv_rows(BASE / "post-xrefs.tsv")), 3),
        "post-instructions.tsv": (len(read_tsv_rows(BASE / "post-instructions.tsv")), 783),
        "post-decompile/index.tsv": (len(read_tsv_rows(BASE / "post-decompile" / "index.tsv")), 3),
        "post-callsite-instructions.tsv": (len(read_tsv_rows(BASE / "post-callsite-instructions.tsv")), 141),
    }
    for label, (actual, expected) in counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    require_tokens(
        "post-xrefs.tsv",
        read_text(BASE / "post-xrefs.tsv"),
        ("004498a4", "CEngine__Shutdown", "00449d05", "CEngine__Init", "00449d62", "CEngine__InitResources"),
        failures,
    )
    require_tokens(
        "post-instructions.tsv",
        read_text(BASE / "post-instructions.tsv"),
        ("CALL\t0x00512ca0", "CALL\t0x004f79d0", "CALL\t0x004f27f0", "CALL\t0x005490e0", "0x652410", "0x652430", "RET"),
        failures,
    )
    require_tokens(
        "post-callsite-instructions.tsv",
        read_text(BASE / "post-callsite-instructions.tsv"),
        ("CALL\t0x00552060", "CALL\t0x005520f0", "CALL\t0x00552330", "MOV\tECX, 0x9c7550"),
        failures,
    )
    decompile_blob = "\n".join(path.read_text(encoding="utf-8-sig") for path in sorted((BASE / "post-decompile").glob("005*.c")))
    require_tokens(
        "post-decompile",
        decompile_blob,
        ("s_shadowblob_tga_00652430", "CConsole__RegisterVariable", "CUMTexture__ConfigureByMode", "CVBufTexture__SetVBFormat"),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "G:\\GhidraBackups\\BEA_20260520-004026_post_wave614_cdxshadows_head_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161614727,
        "destBytes": 161614727,
        "diffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")
    if backup.get("diffs"):
        failures.append("backup diffs not empty")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 2934,
        "undefinedSignatureCount": 1272,
        "paramSignatureCount": 1056,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != expected_queue["totalFunctions"]:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key in ("commentlessFunctionCount", "undefinedSignatureCount", "paramSignatureCount"):
        if quality.get(key) != expected_queue[key]:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_queue[key]}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055515e" or head.get("name") != "CDXSnow__Init":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public readiness note",
        public_note,
        (
            "Ghidra CDXShadows Head Wave614",
            "0x00552060 CDXShadows__Destructor",
            "0x005520f0 CDXShadows__Init",
            "0x00552330 CDXShadows__InitBlobShadows",
            "Read-back exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `783` instruction rows, `3` decompile rows, and `141` callsite instruction rows.",
            "Next queue head: `0x0055515e CDXSnow__Init`",
            "Runtime shadow behavior, runtime blob-shadow rendering, concrete D3D output, BEA patching, and rebuild parity remain unproven.",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in public_note.lower():
            failures.append(f"public note overclaims: {token}")

    require_tokens(
        "package.json",
        read_text(PACKAGE_JSON),
        ("test:ghidra-cdxshadows-head-wave614", "ghidra_cdxshadows_head_wave614_probe.py"),
        failures,
    )
    require_tokens(
        "function index",
        read_text(FUNCTION_INDEX),
        ("Wave614 CDXShadows head hardening", "0x0055515e CDXSnow__Init", "3159/6093 = 51.85%", "3114/6093 = 51.11%"),
        failures,
    )
    require_tokens(
        "DXShadows doc",
        read_text(DXSHADOWS_DOC),
        (
            "Last updated: 2026-05-20",
            "Wave614",
            "CDXShadows__Destructor",
            "CDXShadows__Init",
            "CDXShadows__InitBlobShadows",
            "shadowblob.tga",
            "Runtime shadow behavior remains unproven.",
        ),
        failures,
    )
    require_tokens(
        "campaign",
        read_text(CAMPAIGN),
        ("after Wave614", "0x0055515e CDXSnow__Init", "ghidra_cdxshadows_head_wave614_2026-05-20.md"),
        failures,
    )
    require_tokens(
        "backlog",
        read_text(BACKLOG),
        ("0x00552060,0x005520f0,0x00552330", "Ghidra CDXShadows head Wave614 signature/comment hardening", "DiffCount=0"),
        failures,
    )
    require_tokens(
        "ledger",
        read_text(LEDGER),
        ("Ghidra CDXShadows head Wave614 signature/comment hardening", "cdxshadows-wave614", "0x0055515e CDXSnow__Init"),
        failures,
    )
    require_tokens(
        "attempt log",
        read_text(ATTEMPT_LOG),
        ("\"attempt_id\":20269", "Ghidra CDXShadows head Wave614 signature/comment hardening", "headless_java_apply_signature_comment_tags_no_renames"),
        failures,
    )
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20270:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    if tracking.get("counters", {}).get("ledger_rows") != 1010:
        failures.append(f"tracking ledger_rows mismatch: {tracking.get('counters', {}).get('ledger_rows')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave614", "0x0055515e CDXSnow__Init"), failures)


def run_checks() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_metadata_and_tags(failures)
        check_exports(failures)
        check_backup_and_queue(failures)
        check_public_docs(failures)
    except Exception as exc:  # pragma: no cover - failure reporting path
        failures.append(f"{exc.__class__.__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_checks()
    if failures:
        print("Wave614 CDXShadows head probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave614 CDXShadows head probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
