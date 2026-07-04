#!/usr/bin/env python3
"""Validate Wave742 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave742-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave742_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
BOAT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Boat.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
COLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-153147_post_wave742_unwind_continuation_verified"

TARGETS = {
    "0x005d1170": {"scope": "0x00619fcc", "tokens": ("CSPtrSet__Clear", "0x2a4"), "tags": {"unit", "sptrset-clear"}},
    "0x005d117e": {"scope": "0x00619fd4", "tokens": ("CGenericActiveReader__dtor", "0x4c8"), "tags": {"unit", "active-reader"}},
    "0x005d118c": {"scope": "0x00619fdc", "tokens": ("CGenericActiveReader__dtor", "0x4cc"), "tags": {"unit", "active-reader"}},
    "0x005d119a": {"scope": "0x00619fe4", "tokens": ("CGenericActiveReader__dtor", "0x4e0"), "tags": {"unit", "active-reader"}},
    "0x005d11a8": {"scope": "0x00619fec", "tokens": ("CGenericActiveReader__dtor", "0x574"), "tags": {"unit", "active-reader"}},
    "0x005d11b6": {"scope": "0x00619ff4", "tokens": ("CGenericActiveReader__dtor", "0x5e8"), "tags": {"unit", "active-reader"}},
    "0x005d11c4": {"scope": "0x00619ffc", "tokens": ("CParticleManager__RemoveFromGlobalList_Thunk", "0x5f8"), "tags": {"unit", "particle-manager"}},
    "0x005d11d2": {"scope": "0x0061a004", "tokens": ("CSPtrSet__Clear", "0x620"), "tags": {"unit", "sptrset-clear"}},
    "0x005d11f0": {"scope": "0x0061a02c", "tokens": ("BattleEngine.cpp", "line 0x1f5", "memtype 0x15"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d1220": {"scope": "0x0061a054", "tokens": ("CLine__SetBaseVtable_00426360", "EBP-0x180"), "tags": {"line-vtable", "stack-local"}},
    "0x005d1240": {"scope": "0x0061a07c", "tokens": ("CLine__SetBaseVtable_00426360", "EBP-0xb0"), "tags": {"line-vtable", "stack-local"}},
    "0x005d1260": {"scope": "0x0061a0a4", "tokens": ("CLine__SetBaseVtable_00426360", "EBP-0x70"), "tags": {"line-vtable", "stack-local"}},
    "0x005d1280": {"scope": "0x0061a0cc", "tokens": ("CLine__SetBaseVtable_00426360", "EBP-0x134"), "tags": {"line-vtable", "stack-local"}},
    "0x005d128b": {"scope": "0x0061a0d4", "tokens": ("CLine__SetBaseVtable_00426360", "EBP-0x40"), "tags": {"line-vtable", "stack-local"}},
    "0x005d12a0": {"scope": "0x0061a0fc", "tokens": ("CParticleManager__RemoveFromGlobalList_Thunk", "EBP-0x24"), "tags": {"particle-manager", "stack-local"}},
    "0x005d12c0": {"scope": "0x0061a124", "tokens": ("CSPtrSet__Clear", "0x40"), "tags": {"sptrset-clear"}},
    "0x005d12e0": {"scope": "0x0061a14c", "tokens": ("CSPtrSet__Clear", "EBP-0x10"), "tags": {"sptrset-clear"}},
    "0x005d1300": {"scope": "0x0061a174", "tokens": ("CSPtrSet__Clear", "EBP-0x10"), "tags": {"sptrset-clear"}},
    "0x005d1320": {"scope": "0x0061a19c", "tokens": ("CSPtrSet__Clear", "EBP-0x10"), "tags": {"sptrset-clear"}},
    "0x005d1340": {"scope": "0x0061a1c4", "tokens": ("CSPtrSet__Clear", "EBP-0x10"), "tags": {"sptrset-clear"}},
    "0x005d1360": {"scope": "0x0061a1ec", "tokens": ("Boat.cpp", "line 0x1e", "memtype 0x17"), "tags": {"boat", "boat-cpp", "free-object"}},
    "0x005d1376": {"scope": "0x0061a1f4", "tokens": ("Boat.cpp", "line 0x1f", "memtype 0x16"), "tags": {"boat", "boat-cpp", "free-object"}},
    "0x005d13a0": {"scope": "0x0061a21c", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"monitor", "shutdown"}},
    "0x005d13a8": {"scope": "0x0061a224", "tokens": ("CGenericActiveReader__dtor", "0xc"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d13b3": {"scope": "0x0061a22c", "tokens": ("CGenericActiveReader__dtor", "0x24"), "tags": {"active-reader", "embedded-reader"}},
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave742",
    "wave742-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMON_DOC_TOKENS = (
    "Wave742 unwind continuation",
    "unwind-continuation-wave742",
    "0x005d1170 Unwind@005d1170",
    "0x005d11f0 Unwind@005d11f0",
    "0x005d1220 Unwind@005d1220",
    "0x005d1360 Unwind@005d1360",
    "0x005d13b3 Unwind@005d13b3",
    "0x005d13d0 Unwind@005d13d0",
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
        "pre-instructions.tsv": 575,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 575,
        "post-decompile/index.tsv": 25,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue

        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        comment = row.get("comment", "")
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        for token in ("Wave742 static read-back", "compiler-generated SEH unwind cleanup callback", expected["scope"], "Static retail Ghidra metadata/decompile/xref evidence only"):
            require(token in comment, f"missing common comment token at {address}: {token}", failures)
        for token in expected["tokens"]:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required_tags = COMMON_TAGS | expected["tags"]
            require(required_tags.issubset(actual_tags), f"tags missing at {address}: {required_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    for address, expected in TARGETS.items():
        row = xrefs.get(address)
        require(row is not None, f"missing xref for {address}", failures)
        if row is not None:
            require(normalize_address(row.get("from_addr", "")) == expected["scope"], f"xref scope mismatch at {address}", failures)
            require(row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 575 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4411",
        "queue-probe.log": "Commentless functions: 1687",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave742.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave742_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1687, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1164, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d13d0", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d13d0", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4353, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167152519 or backup.get("totalBytes") == 167152519.0, "backup byte count mismatch", failures)
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
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    specialized_docs = {
        UNIT_DOC: ("0x005d1170 Unwind@005d1170", "0x005d13b3 Unwind@005d13b3"),
        BATTLEENGINE_DOC: ("0x005d11f0 Unwind@005d11f0", "0x005d1220 Unwind@005d1220", "0x005d1360 Unwind@005d1360"),
        BOAT_DOC: ("0x005d1170 Unwind@005d1170", "0x005d1360 Unwind@005d1360", "0x005d13b3 Unwind@005d13b3"),
        MONITOR_DOC: ("0x005d11f0 Unwind@005d11f0", "0x005d1220 Unwind@005d1220", "0x005d1360 Unwind@005d1360", "0x005d13b3 Unwind@005d13b3"),
        COLLISION_DOC: ("0x005d1170 Unwind@005d1170", "0x005d1220 Unwind@005d1220", "0x005d13b3 Unwind@005d13b3"),
    }
    for path, tokens in specialized_docs.items():
        text = read_text(path)
        for token in ("Wave742 unwind continuation", "unwind-continuation-wave742", "0x005d13d0 Unwind@005d13d0", "0x0042f220 CSPtrSet__Clear", BACKUP_PATH, *tokens):
            require(contains_token(text, token), f"missing specialized doc token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package_text = read_text(PACKAGE_JSON)
    require("test:ghidra-unwind-continuation-wave742" in package_text, "missing package script", failures)


def check_ledgers(failures: list[str]) -> None:
    ledger = read_jsonl(LEDGER)
    attempt_log = read_jsonl(ATTEMPT_LOG)
    require(len(ledger) >= 1138, "ledger did not grow to expected minimum", failures)
    require(len(attempt_log) >= 20398, "attempt log did not grow to expected minimum", failures)
    for collection, name in ((ledger, "ledger"), (attempt_log, "attempt log")):
        entry = collection[-1]
        text = json.dumps(entry, sort_keys=True)
        require(entry.get("task") == "Wave742 unwind continuation", f"{name} last task mismatch", failures)
        for token in ("0x005d1170", "0x005d13b3", "unwind-continuation-wave742", BACKUP_PATH):
            require(token in text or token.replace("\\", "\\\\") in text, f"{name} missing token: {token}", failures)
        require(entry.get("status") == "completed", f"{name} status mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)
    check_ledgers(failures)

    if failures:
        print("Wave742 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave742 unwind-continuation probe: PASS")
    print("Targets: 25")
    print("Post exports: metadata=25 tags=25 xrefs=25 instructions=575 decompile=25")
    print("Queue: total=6098 commented=4411 commentless=1687 undefined=1164 param_N=27 strict=4353")
    print(f"Backup: {BACKUP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
