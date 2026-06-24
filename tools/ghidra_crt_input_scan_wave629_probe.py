#!/usr/bin/env python3
"""Validate Wave629 CRT input-scan Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave629-crt-input-scan-head"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_input_scan_wave629_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"

TARGETS = {
    "0x00562cef": (
        "CRT__InputFormatCore",
        "int __cdecl CRT__InputFormatCore(void * inputStream, char * format, void * argList)",
        ("sscanf-style core", "vararg cursor", "Static CRT input-parser evidence only"),
        ("crt-runtime", "input-scan", "scanf-core", "vararg-consumer"),
    ),
    "0x00563714": (
        "CRT__NormalizeDigitForBase",
        "uint __cdecl CRT__NormalizeDigitForBase(uint charValue)",
        ("normalizes alphabetic hex digits", "ctype indirection", "Static digit-normalization evidence only"),
        ("crt-runtime", "input-scan", "ctype", "digit-normalization"),
    ),
    "0x0056374b": (
        "CRT__GetCharFromStream",
        "uint __cdecl CRT__GetCharFromStream(void * stream)",
        ("returns the next buffered byte", "CRT__ReadByteWithBufferRefill", "Static stream-input evidence only"),
        ("crt-runtime", "input-scan", "stream-input"),
    ),
    "0x00563765": (
        "CRT__UngetCharIfNotEof",
        "void __cdecl CRT__UngetCharIfNotEof(int charValue, void * stream)",
        ("guards EOF", "CRT__UngetCharToStream", "Static stream-input evidence only"),
        ("crt-runtime", "input-scan", "stream-input"),
    ),
    "0x0056377c": (
        "CRT__GetNonSpaceCharFromStream",
        "uint __cdecl CRT__GetNonSpaceCharFromStream(int * charsRead, void * stream)",
        ("consumed-character counter", "non-whitespace character", "Static stream/ctype evidence only"),
        ("crt-runtime", "input-scan", "stream-input", "ctype"),
    ),
    "0x0056381b": (
        "CRT__EnsureStdStreamBufferForCommitMode",
        "int __cdecl CRT__EnsureStdStreamBufferForCommitMode(void * stream)",
        ("commit-mode stdout/stderr", "0x1000-byte buffer", "Static CRT stream-buffer evidence only"),
        ("crt-runtime", "stream-output", "stdio-buffer"),
    ),
    "0x005638a8": (
        "CRT__FlushStreamIfWritePending",
        "void __cdecl CRT__FlushStreamIfWritePending(int enabled, void * stream)",
        ("pending write-buffer state", "CDXTexture__FlushWriteStreamSegment", "Static CRT stream-output evidence only"),
        ("crt-runtime", "stream-output", "stdio-buffer"),
    ),
    "0x005638d2": (
        "CRT__ParseFloatTextToFloatAndStatus",
        "void __cdecl CRT__ParseFloatTextToFloatAndStatus(void * outRecord, char * text)",
        ("long-double parser", "consumed-character count", "Static float-parser evidence only"),
        ("crt-runtime", "input-scan", "float-parser"),
    ),
    "0x00563951": (
        "CRT__GetCharTypeMask_Compat",
        "uint __cdecl CRT__GetCharTypeMask_Compat(int charValue, int mask)",
        ("stale ECX/EDI-inflated signature", "CRT__GetStringTypeACompat", "Static ctype/locale evidence only"),
        ("crt-runtime", "input-scan", "ctype", "signature-corrected"),
    ),
}

COMMON_TAGS = {"static-reaudit", "crt-input-scan-wave629", "retail-binary-evidence", "comment-hardened", "signature-hardened"}
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
        failures.append(f"{path.name} missing SUMMARY line")
        return {}
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-succeeded marker")
    if "LockException" in text:
        failures.append(f"{path.name} contains LockException")
    return values


def expect_summary(label: str, actual: dict[str, int], expected: dict[str, int], failures: list[str]) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{label} expected {key}={value}, saw {actual.get(key)}")


def check_metadata(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-metadata.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-metadata target set mismatch: {sorted(rows)}")
    for address, (name, signature, comment_tokens, _tags) in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], set(comment_tokens), failures)
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")


def check_tags(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    for address, (_name, _signature, _comment_tokens, tags) in TARGETS.items():
        row = rows.get(address)
        if not row:
            failures.append(f"{address} missing tag row")
            continue
        actual = {tag for tag in row["tags"].split(";") if tag}
        expected = COMMON_TAGS | set(tags)
        missing = expected - actual
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")


def check_counts(failures: list[str]) -> None:
    checks = [
        (BASE / "post-metadata.tsv", 9, "metadata rows"),
        (BASE / "post-tags.tsv", 9, "tag rows"),
        (BASE / "post-xrefs.tsv", 68, "xref rows"),
        (BASE / "post-instructions.tsv", 333, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "post-decompile.log")
    require_tokens("post-decompile.log", decomp, ("targets=9 dumped=9 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2767,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 964,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x00564486" or head["name"] != "CRT__FmodReduceCore":
        failures.append(f"unexpected next queue head: {head}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("G:\\GhidraBackups\\BEA_20260520-081613_post_wave629_crt_input_scan_verified",),
        failures,
    )
    if backup.get("SourceFiles") != 19 or backup.get("BackupFiles") != 19:
        failures.append(f"backup file counts unexpected: {backup}")
    if int(backup.get("SourceBytes", -1)) != 162204551 or int(backup.get("BackupBytes", -1)) != 162204551:
        failures.append(f"backup byte counts unexpected: {backup}")
    if backup.get("DiffCount") != 0:
        failures.append(f"backup DiffCount is {backup.get('DiffCount')}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave629-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave629-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave629-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 9, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 9, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave629",
        "CRT__InputFormatCore",
        "CRT__GetCharTypeMask_Compat",
        "0x00564486 CRT__FmodReduceCore",
        "3326",
        "2767",
        "964",
        "3274/6093 = 53.73%",
        "G:\\GhidraBackups\\BEA_20260520-081613_post_wave629_crt_input_scan_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens[:5], failures)
        for token in OVERCLAIM_TOKENS:
            if token in text.lower():
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-input-scan-wave629",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave629 CRT input-scan hardening", "3274/6093 = 53.73%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20284", "Wave629 CRT input-scan hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20285:
        failures.append(f"tracking next_attempt_id expected 20285, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave629 hardened nine CRT input-scan helper rows",), failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_metadata(failures)
    check_tags(failures)
    check_counts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit nonzero on validation failures.")
    args = parser.parse_args()

    failures = run_check()
    if failures:
        print("Wave629 CRT input-scan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave629 CRT input-scan probe: PASS")
    print("Verified 9 saved metadata rows, 9 tag rows, 68 xref rows, 333 instruction rows, 9 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
