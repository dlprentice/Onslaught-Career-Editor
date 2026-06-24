#!/usr/bin/env python3
"""Validate Wave626 TLS/float/lock Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave626-tls-float-lock-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_tls_float_lock_wave626_2026-05-20.md"
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
    "0x00560b2c": (
        "CTexture__InitializeThreadLocalState",
        "int __cdecl CTexture__InitializeThreadLocalState(void)",
        ("thread-local initialization entry", "TlsSetValue", "0x74-byte per-thread record"),
        ("tls-init", "ctexture", "critical-section"),
    ),
    "0x00560b80": (
        "CTexture__InitializeThreadLocalRecordDefaults",
        "void __cdecl CTexture__InitializeThreadLocalRecordDefaults(void * tlsRecord)",
        ("initializes default fields", "tlsRecord+0x50", "tlsRecord+0x14"),
        ("tls-init", "tls-record", "ctexture"),
    ),
    "0x00560b93": (
        "CRT__GetOrInitThreadLocalRecord",
        "void * __cdecl CRT__GetOrInitThreadLocalRecord(void)",
        ("lazy TLS record accessor", "GetLastError", "__amsg_exit(0x10)"),
        ("tls-init", "tls-record", "crt-runtime"),
    ),
    "0x00560bfa": (
        "CDXTexture__InvokeTlsCleanupCallbackAndFinalize",
        "void __cdecl CDXTexture__InvokeTlsCleanupCallbackAndFinalize(void)",
        ("TLS cleanup/finalize wrapper", "callback pointer at record+0x60", "CRT__FatalRuntimeErrorAndExit"),
        ("tls-cleanup", "cdxtexture", "seh"),
    ),
    "0x00560c5b": (
        "CDXTexture__InvokeGlobalCleanupCallbackAndFinalize",
        "void __cdecl CDXTexture__InvokeGlobalCleanupCallbackAndFinalize(void)",
        ("global cleanup/finalize wrapper", "PTR_CDXTexture__InvokeTlsCleanupCallbackAndFinalize_00653654", "CDXTexture__InvokeTlsCleanupCallbackAndFinalize"),
        ("tls-cleanup", "cdxtexture", "seh"),
    ),
    "0x00560cb1": (
        "CRT__InitFpuControlWord_0x10000_0x30000",
        "void __cdecl CRT__InitFpuControlWord_0x10000_0x30000(void)",
        ("FPU control-word initializer", "0x10000/0x30000", "CRT__ControlFpMasked_0056947e"),
        ("fpu-control", "crt-runtime"),
    ),
    "0x00560cc3": (
        "CDXTexture__ProbeFeatureModuloGate",
        "int __cdecl CDXTexture__ProbeFeatureModuloGate(void)",
        ("fallback processor-feature probe gate", "DAT_005d87e0", "returns 1 or 0"),
        ("processor-feature", "fallback-probe", "cdxtexture"),
    ),
    "0x00560d01": (
        "CDXTexture__ProbeProcessorFeaturePresentOrFallback",
        "void __cdecl CDXTexture__ProbeProcessorFeaturePresentOrFallback(void)",
        ("processor feature probe wrapper", "KERNEL32!IsProcessorFeaturePresent", "feature id 0"),
        ("processor-feature", "kernel32", "cdxtexture"),
    ),
    "0x00560d2a": (
        "CRT__InsertDecimalSeparatorBeforeExponent",
        "void __cdecl CRT__InsertDecimalSeparatorBeforeExponent(char * text)",
        ("decimal-separator insertion helper", "DAT_00653aa0", "shifts the remainder"),
        ("float-format", "locale-decimal", "name-corrected"),
    ),
    "0x00560dea": (
        "__fassign",
        "void __cdecl __fassign(int storeFloat, void * outValue, char * numberText)",
        ("Visual Studio 2003 __fassign helper", "CRT__ParseFloatTextToFloat32", "CRT__ParseFloatTextToFloat64"),
        ("float-parse", "library-match", "vs2003-crt"),
    ),
    "0x00560e28": (
        "CRT__FormatFloatScientificFromLongDouble",
        "char * __cdecl CRT__FormatFloatScientificFromLongDouble(void * longDoubleValue, char * outBuffer, int precision, int uppercaseExponent)",
        ("scientific-format wrapper", "precision+1", "CRT__FormatFloatScientificCore"),
        ("float-format", "scientific-format", "crt-runtime"),
    ),
    "0x00560e89": (
        "CRT__FormatFloatScientificCore",
        "char * __cdecl CRT__FormatFloatScientificCore(char * outBuffer, int precision, int uppercaseExponent, void * decimalRecord, int generalFormatMode)",
        ("scientific-format core", "e+000/E+000", "exponent digits"),
        ("float-format", "scientific-format", "locale-decimal"),
    ),
    "0x00560f4b": (
        "CRT__FormatFloatFixedFromLongDouble",
        "char * __cdecl CRT__FormatFloatFixedFromLongDouble(void * longDoubleValue, char * outBuffer, int precision)",
        ("fixed-format wrapper", "exponent plus requested precision", "CRT__FormatFloatFixedCore"),
        ("float-format", "fixed-format", "crt-runtime"),
    ),
    "0x00560fa0": (
        "CRT__FormatFloatFixedCore",
        "char * __cdecl CRT__FormatFloatFixedCore(char * outBuffer, int precision, void * decimalRecord, int generalFormatMode)",
        ("fixed-format core", "leading zero", "zero-pads fractional gaps"),
        ("float-format", "fixed-format", "locale-decimal"),
    ),
    "0x00561047": (
        "CRT__FormatFloatGeneral_SelectStyle",
        "void __cdecl CRT__FormatFloatGeneral_SelectStyle(void * longDoubleValue, char * outBuffer, int precision, int uppercaseExponent)",
        ("general-format selector", "chooses scientific output", "trims trailing digit text"),
        ("float-format", "general-format", "crt-runtime"),
    ),
    "0x0056112b": (
        "CRT__ShiftStringRightInPlace",
        "void __cdecl CRT__ShiftStringRightInPlace(char * text, int count)",
        ("in-place string right-shift helper", "CRT__MemMoveOverlapSafe", "length+1"),
        ("float-format", "string-shift", "memmove"),
    ),
    "0x00561150": (
        "CTexture__InitializeGlobalCriticalSections",
        "void __cdecl CTexture__InitializeGlobalCriticalSections(void)",
        ("initializes four global critical-section slots", "InitializeCriticalSection", "PTR_DAT_006536b4"),
        ("tls-init", "critical-section", "ctexture"),
    ),
    "0x00561179": (
        "CRT__LockByIndex",
        "void __cdecl CRT__LockByIndex(int lockIndex)",
        ("CRT indexed-lock acquisition helper", "0x18-byte critical section", "lock index 0x11"),
        ("lock-helper", "critical-section", "crt-runtime"),
    ),
    "0x005611da": (
        "CRT__UnlockByIndex",
        "void __cdecl CRT__UnlockByIndex(int lockIndex)",
        ("CRT indexed-lock release helper", "DAT_00653670[lockIndex]", "LeaveCriticalSection"),
        ("lock-helper", "critical-section", "crt-runtime"),
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
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BADNAME:",
        "Read-back mismatch",
        "BAD:",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave626-dry.log",
        {"updated": 0, "skipped": 19, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave626-apply.log",
        {"updated": 19, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave626-final-dry.log",
        {"updated": 0, "skipped": 19, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=19 found=19 missing=0",),
        "post-context-tags.log": ("rows=19 missing=0",),
        "post-context-xrefs.log": ("Wrote 139 rows",),
        "post-context-instructions.log": ("Wrote 1653 instruction rows", "targets=19 missing=0"),
        "post-context-decompile.log": ("targets=19 dumped=19 missing=0 failed=0",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2797", "Param signatures: 993"),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_and_decompile(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 19:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 19")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, _) in TARGETS.items():
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
    if len(tag_rows) != 19:
        failures.append(f"post-context-tags row count mismatch: {len(tag_rows)} != 19")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in (
            "static-reaudit",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "tls-float-lock-wave626",
            *tag_tokens,
        ):
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    decompile_rows = read_tsv_rows(BASE / "post-decompile" / "index.tsv")
    if len(decompile_rows) != 19:
        failures.append(f"post-decompile index row count mismatch: {len(decompile_rows)} != 19")
    for row in decompile_rows:
        if row["status"] != "OK":
            failures.append(f"{row['address']} decompile status mismatch: {row['status']}")


def check_edges(failures: list[str]) -> None:
    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "00560b80\tCTexture__InitializeThreadLocalRecordDefaults\t00560b65\t00560b2c\tCTexture__InitializeThreadLocalState",
        "00560b93\tCRT__GetOrInitThreadLocalRecord\t00560c24\t00560bfa\tCDXTexture__InvokeTlsCleanupCallbackAndFinalize",
        "00560bfa\tCDXTexture__InvokeTlsCleanupCallbackAndFinalize\t00560cac\t00560c5b\tCDXTexture__InvokeGlobalCleanupCallbackAndFinalize",
        "00560cc3\tCDXTexture__ProbeFeatureModuloGate\t00560d25\t00560d01\tCDXTexture__ProbeProcessorFeaturePresentOrFallback",
        "00560e89\tCRT__FormatFloatScientificCore\t005610cd\t00561047\tCRT__FormatFloatGeneral_SelectStyle",
        "0056112b\tCRT__ShiftStringRightInPlace\t00560fe7\t00560fa0\tCRT__FormatFloatFixedCore",
        "00561150\tCTexture__InitializeGlobalCriticalSections\t00560b2d\t00560b2c\tCTexture__InitializeThreadLocalState",
        "00561179\tCRT__LockByIndex\t0055fe62\t0055fe55\tCRT__LockRouteByIndex",
        "005611da\tCRT__UnlockByIndex\t0055feb4\t0055fea7\tCRT__UnlockRouteByIndex",
    ):
        if token not in xrefs:
            failures.append(f"post-context-xrefs missing token: {token}")


def check_queue_backup_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2797,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 993,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x00561618" or head.get("name") != "CRT__ExtractFiniteExponentMaskOrPassThrough_00561618":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "G:\\GhidraBackups\\BEA_20260520-064302_post_wave626_tls_float_lock_verified":
        failures.append(f"backupPath mismatch: {backup.get('backupPath')}")
    if backup.get("fileCount") != 19 or int(backup.get("totalBytes", 0)) != 162106247 or backup.get("diffCount") != 0:
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
        "package.json": ("test:ghidra-tls-float-lock-wave626",),
        "public note": ("Ghidra TLS/Float/Lock Wave626", "CRT__InsertDecimalSeparatorBeforeExponent", "2797", "993"),
        "functions index": ("Wave626 TLS/float/lock hardening", "0x00561618 CRT__ExtractFiniteExponentMaskOrPassThrough_00561618"),
        "crt doc": ("Wave626 Static Read-Back Note", "CRT__InsertDecimalSeparatorBeforeExponent", "CRT__UnlockByIndex"),
        "ghidra reference": ("Current Signature Caveat: TLS/Float/Lock Wave626", "CRT__FormatFloatGeneral_SelectStyle"),
        "campaign": ("ghidra_tls_float_lock_wave626_2026-05-20.md", "0x00561618 CRT__ExtractFiniteExponentMaskOrPassThrough_00561618"),
        "backlog": ("Ghidra TLS/float/lock Wave626 signature/comment hardening", "DiffCount=0"),
        "ledger": ("Ghidra TLS/float/lock Wave626 signature/comment hardening", "strict clean-signature proxy 3244/6093 = 53.24%"),
        "attempt log": ("attempt_id\":20281", "headless_java_apply_signature_comment_tags_with_one_rename_no_boundary_change"),
        "tracking": ("Wave626 hardened nineteen adjacent TLS", "next_attempt_id\": 20282"),
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
    check_metadata_tags_and_decompile(failures)
    check_edges(failures)
    check_queue_backup_and_docs(failures)

    if failures:
        print("Wave626 TLS/float/lock probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave626 TLS/float/lock probe: PASS")
    print("Verified 19 saved metadata rows, 19 tag rows, 139 xref rows, 1653 instruction rows, 19 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
