#!/usr/bin/env python3
"""Validate Wave620 CRT/SEH head Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave620-crt-seh-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_seh_head_wave620_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x0055d6a0": (
        "CRT__SehPopExceptionFrameAndJump",
        "void __stdcall CRT__SehPopExceptionFrameAndJump(void * param_1)",
        ("FS:[0]", "ESP/EBP", "indirect jump"),
        ("crt-seh-wave620", "seh-frame", "fs-exception-list", "indirect-jump"),
    ),
    "0x0055d6d4": (
        "CRT__InvokeCallbackWithLockGuards",
        "void __stdcall CRT__InvokeCallbackWithLockGuards(int param_1, void * param_2)",
        ("pops EAX/ECX", "LOCK/UNLOCK", "CRT__DestroyCatchObject"),
        ("crt-seh-wave620", "callback-wrapper", "lock-unlock-pseudo", "indirect-jump"),
    ),
    "0x0055d6db": (
        "CRT__SehLockUnlockAndJump",
        "void __stdcall CRT__SehLockUnlockAndJump(int param_1, void * param_2)",
        ("pops EAX/ECX", "LOCK/UNLOCK", "CRT__BuildCatchObject"),
        ("crt-seh-wave620", "callback-wrapper", "lock-unlock-pseudo", "indirect-jump"),
    ),
    "0x0055d6e2": (
        "CRT__SehRtlUnwindAndRestoreFrame",
        "void __stdcall CRT__SehRtlUnwindAndRestoreFrame(int param_1, int param_2)",
        ("RtlUnwind", "0x0055d70a", "flag bit 0x2"),
        ("crt-seh-wave620", "seh-frame", "fs-exception-list", "rtlunwind"),
    ),
    "0x0055d7bb": (
        "CRT__SehCallback_Call_005602d2",
        "void __cdecl CRT__SehCallback_Call_005602d2(int param_1, int param_2, int param_3)",
        ("data reference", "eight stack arguments", "0x005602d2"),
        ("crt-seh-wave620", "callback-wrapper", "data-xref"),
    ),
    "0x0055d896": (
        "CRT__SehFilterCppException",
        "int __cdecl CRT__SehFilterCppException(int param_1, int param_2, int param_3)",
        ("0x66", "frame+0x24", "frame callback at +0x18"),
        ("crt-seh-wave620", "exception-filter", "data-xref", "indirect-jump"),
    ),
    "0x0055d90b": (
        "CRT__GetRangeOfTryBlocksForState",
        "int __cdecl CRT__GetRangeOfTryBlocksForState(int param_1, int param_2, int param_3, void * param_4, void * param_5)",
        ("0x14-byte try-block records", "+0x10", "CDXTexture__InvokeGlobalCleanupCallbackAndFinalize"),
        ("crt-seh-wave620", "try-block-range", "eh-metadata"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime exception behavior proven",
    "msvc crt version proven",
    "fully recovered",
    "fully reverse-engineered",
    "rebuild parity proven",
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
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_clean_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    expectations = {
        "apply-wave620-dry.log": {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave620-apply.log": {"updated": 7, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave620-final-dry.log": {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    }
    for name, expected in expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=7 found=7 missing=0",),
        "post-context-tags.log": ("rows=7 missing=0",),
        "post-context-xrefs.log": ("Wrote 10 rows",),
        "post-context-instructions.log": ("Wrote 259 instruction rows", "targets=7 missing=0"),
        "post-context-decompile.log": ("targets=7 dumped=7 missing=0 failed=0",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3224",),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_and_edges(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 7:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 7")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, tag_tokens) in TARGETS.items():
        row = by_address.get(address)
        if not row:
            failures.append(f"post-context-metadata missing {address}")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} status mismatch: {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in ("static-reaudit", "retail-binary-evidence", "comment-hardened", *tag_tokens):
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0055d6a0\tCRT__SehPopExceptionFrameAndJump\t00560736\t005606c5\tCRT__SehUnwindAndResumeSearch",
        "0055d6d4\tCRT__InvokeCallbackWithLockGuards\t00560a1e\t00560885\tCRT__BuildCatchObject",
        "0055d6db\tCRT__SehLockUnlockAndJump\t00560a04\t00560885\tCRT__BuildCatchObject",
        "0055d6e2\tCRT__SehRtlUnwindAndRestoreFrame\t0055d8f2\t0055d896\tCRT__SehFilterCppException",
        "0055d7bb\tCRT__SehCallback_Call_005602d2\t0055d77d\t0055d767\tCRT__SehInvokeCallSettingFrame12\tDATA",
        "0055d896\tCRT__SehFilterCppException\t0055d7ed\t0055d7e0\tCRT__CallExceptionTranslator\tDATA",
        "0055d90b\tCRT__GetRangeOfTryBlocksForState\t0056043f\t0056036d\tCRT__SehLookupAndInvokeScopeHandler",
    ):
        require_tokens("post-context-xrefs.tsv", xrefs, (token,), failures)

    instructions = read_text(BASE / "post-context-instructions.tsv")
    for token in (
        "0x0055d6a0\t0x0055d6a0\tAFTER\t16\t0x0055d6cb\t0x0055d6a0\tCRT__SehPopExceptionFrameAndJump\tJMP\tEAX",
        "0x0055d6d4\t0x0055d6d4\tAFTER\t3\t0x0055d6d9\t0x0055d6d4\tCRT__InvokeCallbackWithLockGuards\tJMP\tEAX",
        "0x0055d6e2\t0x0055d6e2\tAFTER\t14\t0x0055d705\t0x0055d6e2\tCRT__SehRtlUnwindAndRestoreFrame\tCALL\t0x005d04e6",
        "0x0055d7bb\t0x0055d7bb\tAFTER\t12\t0x0055d7d6\t0x0055d7bb\tCRT__SehCallback_Call_005602d2\tCALL\t0x005602d2",
        "0x0055d90b\t0x0055d90b\tBEFORE\t-6\t0x0055d900\t0x0055d896\tCRT__SehFilterCppException\tJMP\tdword ptr [EBX + 0x18]",
    ):
        require_tokens("post-context-instructions.tsv", instructions, (token,), failures)

    decompile = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "post-decompile").glob("*.c"))
    for token in ("RtlUnwind", "CRT__SehDispatchWithScopeTable", "CDXTexture__InvokeGlobalCleanupCallbackAndFinalize"):
        require_tokens("post-decompile", decompile, (token,), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    expected_backup = {
        "BackupPath": "[maintainer-local-ghidra-backup-root]\\BEA_20260520-035125_post_wave620_crt_seh_head_verified",
        "SourceFileCount": 19,
        "BackupFileCount": 19,
        "SourceBytes": 161811335,
        "BackupBytes": 161811335,
        "DiffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 2869,
        "undefinedSignatureCount": 1218,
        "paramSignatureCount": 1056,
        "legacyWeakNameCount": 0,
        "uncertainOwnerNameCount": 0,
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 0,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055dac5" or head.get("name") != "type_info__ctor_like_0055dac5":
        failures.append(f"queue head mismatch: {head}")


def check_docs(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: ("Wave620", "0x0055dac5 type_info__ctor_like_0055dac5", "3224/6093 = 52.91%"),
        FUNCTION_INDEX: ("Latest saved-correction note: Wave620", "crt-seh.md", "3224/6093 = 52.91%"),
        CRT_DOC: ("## Wave620 Static Read-Back Note", "CRT__SehFilterCppException", "0x0055dac5 type_info__ctor_like_0055dac5"),
        CAMPAIGN: ("after Wave620", "Current CRT/SEH head follow-up", "2869"),
        BACKLOG: ("Ghidra CRT/SEH head Wave620", "ApplyCrtSehHeadWave620.java", "DiffCount=0"),
        LEDGER: ("Ghidra CRT/SEH head Wave620", "0x0055dac5 type_info__ctor_like_0055dac5", "runtime exception behavior"),
        ATTEMPT_LOG: ("\"attempt_id\":20275", "Ghidra CRT/SEH head Wave620", "\"readback\":\"verified\""),
        TRACKING: ("Wave620", "0x0055dac5 type_info__ctor_like_0055dac5", "\"next_attempt_id\": 20276"),
        PACKAGE_JSON: ("test:ghidra-crt-seh-head-wave620", "tools\\\\ghidra_crt_seh_head_wave620_probe.py --check"),
    }
    for path, tokens in doc_tokens.items():
        require_tokens(path.name, read_text(path), tokens, failures)

    combined = "\n".join(read_text(path) for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, CAMPAIGN))
    lowered = combined.lower()
    for token in OVERCLAIM_TOKENS:
        if token in lowered:
            failures.append(f"docs overclaim: {token}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_tags_and_edges(failures)
    check_backup_and_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave620 CRT/SEH head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave620 CRT/SEH head probe: PASS")
    print("Verified 7 metadata rows, 7 tag rows, logs, queue, backup, docs, and package script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
