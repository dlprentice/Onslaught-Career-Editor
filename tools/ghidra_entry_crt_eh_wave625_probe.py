#!/usr/bin/env python3
"""Validate Wave625 entry/CRT EH Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave625-entry-crt-eh-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_entry_crt_eh_wave625_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x00560181": (
        "entry",
        "void __cdecl entry(void)",
        ("process entry routine", "CLTShell__WinMain", "CRT__CExit"),
        ("process-entry", "crt-startup", "winmain"),
    ),
    "0x005602ae": (
        "CDXTexture__ReportFatalAndExitProcess",
        "void __cdecl CDXTexture__ReportFatalAndExitProcess(int runtimeErrorId)",
        ("fatal runtime-report wrapper", "ExitProcess(0xff)", "runtimeErrorId"),
        ("fatal-exit", "runtime-error", "cdxtexture"),
    ),
    "0x005605ca": (
        "CRT__TypeMatchForCatch",
        "int __cdecl CRT__TypeMatchForCatch(void * handlerType, void * catchableType, void * throwInfo)",
        ("catch-type matcher", "type descriptor names", "flag compatibility"),
        ("crt-runtime", "seh", "cxx-exception", "type-match"),
    ),
    "0x00560627": (
        "CRT__SehUnwindToTargetState",
        "void __cdecl CRT__SehUnwindToTargetState(void * frameInfo, int registrationFrame, void * functionInfo, int targetState)",
        ("unwind-map walker", "__CallSettingFrame_12", "targetState"),
        ("crt-runtime", "seh", "cxx-exception", "unwind-map"),
    ),
    "0x00560740": (
        "CRT__CallCatchBlock",
        "int __cdecl CRT__CallCatchBlock(void * exceptionRecord, void * frameInfo, void * contextRecord)",
        ("catch-block invocation wrapper", "per-thread CRT record", "CRT__CleanupCatchContext"),
        ("crt-runtime", "seh", "cxx-exception", "catch-invoke"),
    ),
    "0x00560885": (
        "CRT__BuildCatchObject",
        "void __cdecl CRT__BuildCatchObject(void * exceptionRecord, int frameObjectBase, void * handlerType, void * catchableType)",
        ("catch-object materialization helper", "CRT__AdjustPointerByPMD", "CRT__MemMoveOverlapSafe"),
        ("crt-runtime", "seh", "cxx-exception", "catch-object"),
    ),
    "0x00560a49": (
        "CRT__DestroyCatchObject",
        "void __cdecl CRT__DestroyCatchObject(void * exceptionRecord)",
        ("catch-object cleanup helper", "destructor callback", "temporary SEH frame"),
        ("crt-runtime", "seh", "cxx-exception", "catch-object"),
    ),
    "0x00560ab0": (
        "CRT__AdjustPointerByPMD",
        "int __cdecl CRT__AdjustPointerByPMD(int basePtr, void * pmd)",
        ("pointer-to-member-displacement adjuster", "primary displacement", "vbtable offset"),
        ("crt-runtime", "seh", "cxx-exception", "pmd-adjust"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "crt identity proven",
    "crt version proven",
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


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str], *, allow_bad: bool = False) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    bad_tokens = ("LockException", "Input file not found", "BADADDR", "ERROR REPORT SCRIPT ERROR", "BADNAME:", "Read-back mismatch")
    for bad_token in bad_tokens:
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")
    if not allow_bad and "BAD:" in text:
        failures.append(f"{path.name} contains BAD:")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave625-dry.log",
        {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave625-apply-initial-readback-mismatch.log",
        {"updated": 7, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 1},
        failures,
        allow_bad=True,
    )
    require_tokens(
        "initial apply mismatch",
        read_text(BASE / "apply-wave625-apply-initial-readback-mismatch.log"),
        ("void __cdecl entry(void) != void __cdecl entry()",),
        failures,
    )
    require_log_summary(
        BASE / "apply-wave625-apply.log",
        {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave625-final-dry.log",
        {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=8 found=8 missing=0",),
        "post-context-tags.log": ("rows=8 missing=0",),
        "post-context-xrefs.log": ("Wrote 15 rows",),
        "post-context-instructions.log": ("Wrote 968 instruction rows", "targets=8 missing=0"),
        "post-context-decompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2815", "Param signatures: 1003"),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_decompile_and_edges(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 8:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 8")
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
    if len(tag_rows) != 8:
        failures.append(f"post-context-tags row count mismatch: {len(tag_rows)} != 8")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened", "entry-crt-eh-wave625", *tag_tokens):
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    decompile_rows = read_tsv_rows(BASE / "post-decompile" / "index.tsv")
    if len(decompile_rows) != 8:
        failures.append(f"post-decompile index row count mismatch: {len(decompile_rows)} != 8")
    for row in decompile_rows:
        if row["status"] != "OK":
            failures.append(f"{row['address']} decompile status mismatch: {row['status']}")

    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "00560181\tentry\tEntry Point\t<none>\t<no_function>\tEXTERNAL",
        "005602ae\tCDXTexture__ReportFatalAndExitProcess\t005601e6\t00560181\tentry",
        "005605ca\tCRT__TypeMatchForCatch\t00560488\t0056036d\tCRT__SehLookupAndInvokeScopeHandler",
        "00560627\tCRT__SehUnwindToTargetState\t00560306\t005602d2\tCRT__SehDispatchWithScopeTable",
        "00560740\tCRT__CallCatchBlock\t00560728\t005606c5\tCRT__SehUnwindAndResumeSearch",
        "00560885\tCRT__BuildCatchObject\t005606df\t005606c5\tCRT__SehUnwindAndResumeSearch",
        "00560a49\tCRT__DestroyCatchObject\t005604e9\t0056036d\tCRT__SehLookupAndInvokeScopeHandler",
        "00560ab0\tCRT__AdjustPointerByPMD\t00560914\t00560885\tCRT__BuildCatchObject",
    ):
        if token not in xrefs:
            failures.append(f"post-context-xrefs missing token: {token}")


def check_queue_backup_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2815,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 1003,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x00560b80" or head.get("name") != "CTexture__InitializeThreadLocalRecordDefaults":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "G:\\GhidraBackups\\BEA_20260520-061702_post_wave625_entry_crt_eh_verified":
        failures.append(f"backupPath mismatch: {backup.get('backupPath')}")
    if backup.get("fileCount") != 19 or int(backup.get("totalBytes", 0)) != 162040711 or backup.get("diffCount") != 0:
        failures.append(f"backup summary mismatch: {backup}")

    docs = {
        "package.json": read_text(PACKAGE_JSON),
        "public note": read_text(PUBLIC_NOTE),
        "functions index": read_text(FUNCTION_INDEX),
        "crt doc": read_text(CRT_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
        "tracking": read_text(TRACKING),
    }
    expected_doc_tokens = {
        "package.json": ("test:ghidra-entry-crt-eh-wave625",),
        "public note": ("Ghidra Entry/CRT EH Wave625", "void __cdecl entry(void)", "2815", "1003"),
        "functions index": ("Wave625 entry/CRT EH hardening", "0x00560b80 CTexture__InitializeThreadLocalRecordDefaults"),
        "crt doc": ("Wave625 Static Read-Back Note", "CRT__BuildCatchObject", "CRT__AdjustPointerByPMD"),
        "ghidra reference": ("Wave625 Entry/CRT EH Read-Back", "CRT__TypeMatchForCatch", "CRT__AdjustPointerByPMD"),
        "campaign": ("ghidra_entry_crt_eh_wave625_2026-05-20.md", "0x00560b80 CTexture__InitializeThreadLocalRecordDefaults"),
        "backlog": ("Ghidra entry/CRT EH Wave625 signature/comment hardening", "DiffCount=0"),
        "ledger": ("Ghidra entry/CRT EH Wave625 signature/comment hardening", "strict clean-signature proxy 3226/6093 = 52.95%"),
        "attempt log": ("attempt_id\":20280", "headless_java_apply_signature_comment_tags_with_preserved_zero_param_readback_correction_no_boundary_change"),
        "tracking": ("Wave625 hardened eight adjacent process-entry", "next_attempt_id\": 20281"),
    }
    for label, tokens in expected_doc_tokens.items():
        require_tokens(label, docs[label], tokens, failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run validation")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_tags_decompile_and_edges(failures)
    check_queue_backup_and_docs(failures)

    if failures:
        print("Wave625 entry/CRT EH probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave625 entry/CRT EH probe: PASS")
    print("Verified 8 saved metadata rows, 8 tag rows, 15 xref rows, 968 instruction rows, 8 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
