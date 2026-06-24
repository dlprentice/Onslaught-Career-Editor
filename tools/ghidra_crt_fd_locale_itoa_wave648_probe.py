#!/usr/bin/env python3
"""Validate Wave648 CRT fd/locale/itoa Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave648-crt-fd-locale-itoa"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_fd_locale_itoa_wave648_2026-05-20.md"
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
    "0x0056db76": (
        "CRT__ChangeFileSizeByFd_NoLock",
        "int __cdecl CRT__ChangeFileSizeByFd_NoLock(uint fdIndex, int targetSize)",
        ("file-size adjustment", "SetEndOfFile", "Wave648"),
        ("crt-runtime", "fd-table", "file-size", "SetEndOfFile", "file-write"),
    ),
    "0x0056dc9b": (
        "CRT__WriteWideCharToStream",
        "uint __cdecl CRT__WriteWideCharToStream(uint wideChar, void * stream)",
        ("wide character", "0xffff", "Wave648"),
        ("crt-runtime", "wide-char", "stream", "fd-write", "FILE"),
    ),
    "0x0056ddc2": (
        "CRT__GetLocaleInfoCopyOrInt",
        "int __cdecl CRT__GetLocaleInfoCopyOrInt(int valueKind, int localeId, int localeInfoType, void * outValue)",
        ("locale-info extractor", "ERROR_INSUFFICIENT_BUFFER", "Wave648"),
        ("crt-runtime", "locale", "GetLocaleInfo", "NLS", "allocation"),
    ),
    "0x0056e0bf": (
        "CRT__IntToAsciiBase",
        "char * __cdecl CRT__IntToAsciiBase(int value, char * outBuffer, int base)",
        ("signed integer-to-ASCII", "minus sign", "Wave648"),
        ("crt-runtime", "itoa", "numeric-format", "string"),
    ),
    "0x0056e0ec": (
        "CRT__UIntToAsciiBase",
        "void __cdecl CRT__UIntToAsciiBase(uint value, char * outBuffer, uint base, int emitMinusSign)",
        ("unsigned integer-to-ASCII core", "reverses the digit span", "Wave648"),
        ("crt-runtime", "itoa", "numeric-format", "string"),
    ),
    "0x0056e148": (
        "CRT__UIntToAsciiBase_ReturnBuffer",
        "char * __cdecl CRT__UIntToAsciiBase_ReturnBuffer(uint value, char * outBuffer, uint base)",
        ("returns the caller output buffer", "Wave648"),
        ("crt-runtime", "itoa", "numeric-format", "string", "wrapper"),
    ),
    "0x0056e170": (
        "CRT__StrNICmpWithLocaleLock",
        "int __cdecl CRT__StrNICmpWithLocaleLock(char * leftText, char * rightText, uint maxChars)",
        ("corrected stale CMCBuggy owner", "CRT__ToLowerWithLocale", "Wave648"),
        ("crt-runtime", "string-compare", "case-insensitive", "locale", "name-corrected"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-fd-locale-itoa-wave648",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
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
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token.replace("\\\\", "\\") not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY line")
        return {}
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
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
        missing = (COMMON_TAGS | set(tags)) - actual
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")


def check_counts(failures: list[str]) -> None:
    checks = [
        (BASE / "post-metadata.tsv", 7, "metadata rows"),
        (BASE / "post-tags.tsv", 7, "tag rows"),
        (BASE / "post-xrefs.tsv", 122, "xref rows"),
        (BASE / "post-instructions.tsv", 903, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=7 dumped=7 missing=0 failed=0", "REPORT: Save succeeded"), failures)


def check_logs(failures: list[str]) -> None:
    expect_summary("dry", parse_log_summary(BASE / "apply-dry.log", failures), {
        "updated": 0, "skipped": 7, "renamed": 0, "would_rename": 3, "signature_updated": 0, "missing": 0, "bad": 0,
    }, failures)
    expect_summary("apply", parse_log_summary(BASE / "apply.log", failures), {
        "updated": 7, "skipped": 0, "renamed": 3, "would_rename": 0, "signature_updated": 7, "missing": 0, "bad": 0,
    }, failures)
    expect_summary("final dry", parse_log_summary(BASE / "apply-final-dry.log", failures), {
        "updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0,
    }, failures)
    if "REPORT: Save succeeded" not in read_text(BASE / "apply.log"):
        failures.append("apply.log missing script save-succeeded marker")
    for log in BASE.glob("*.log"):
        text = read_text(log)
        if "LockException" in text or "BAD:" in text or "BADNAME:" in text or "MISSING:" in text:
            failures.append(f"{log.name} contains failure marker")


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue["qualitySignals"]
    expected = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 2601,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 814,
    }
    for key, value in expected.items():
        actual = queue.get(key) if key == "totalFunctions" else signals.get(key)
        if actual != value:
            failures.append(f"queue {key}: expected {value}, saw {actual}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if normalize_address(head["address"]) != "0x0056e271" or head["name"] != "CRT__GetEnvVarValuePointerCaseInsensitive_0056e271":
        failures.append(f"unexpected next queue head: {head}")
    rows = read_tsv_rows(QUEUE_TSV)
    by_addr = {normalize_address(row["address"]): row for row in rows}
    for address, (name, signature, _comment_tokens, _tags) in TARGETS.items():
        row = by_addr.get(address)
        if not row:
            failures.append(f"queue TSV missing {address}")
        elif row["name"] != name or row["signature"] != signature or row["comment"] == "":
            failures.append(f"queue TSV did not preserve Wave648 metadata for {address}")


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    if "test:ghidra-crt-fd-locale-itoa-wave648" not in package.get("scripts", {}):
        failures.append("package.json missing Wave648 npm script")
    required_docs = {
        PUBLIC_NOTE: ("Wave648", "CRT__StrNICmpWithLocaleLock", "2601", "814", "G:\\GhidraBackups\\BEA_20260520-205347_post_wave648_crt_fd_locale_itoa_verified"),
        FUNCTION_INDEX: ("Wave648", "CRT__GetLocaleInfoCopyOrInt", "0x0056e271"),
        CRT_DOC: ("Wave648", "CRT__UIntToAsciiBase_ReturnBuffer", "CRT__GetEnvVarValuePointerCaseInsensitive_0056e271"),
        GHIDRA_REFERENCE: ("Wave648", "CRT__ChangeFileSizeByFd_NoLock", "crt-fd-locale-itoa-wave648"),
        CAMPAIGN: ("Wave648", "2601", "0x0056e271"),
        BACKLOG: ("Wave648 CRT fd/locale/itoa hardening", "0x0056db76,0x0056dc9b", "DiffCount=0"),
        LEDGER: ("Wave648 CRT fd/locale/itoa hardening", "crt-fd-locale-itoa-wave648", "next head 0x0056e271"),
        ATTEMPT_LOG: ("Wave648 CRT fd/locale/itoa hardening", "\"attempt_id\":20303", "accepted dry/apply/final/post evidence"),
    }
    for path, tokens in required_docs.items():
        require_tokens(str(path.relative_to(ROOT)), read_text(path), tokens, failures)
    tracking = read_json(TRACKING)
    if tracking["counters"]["ledger_rows"] < 1044 or tracking["counters"]["attempt_rows"] < 20304:
        failures.append("tracking counters were not advanced for Wave648")
    require_tokens("tracking notes", json.dumps(tracking), ("Wave648", "0x0056e271", "2601"), failures)


def check_no_overclaim(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN):
        text = read_text(path).lower()
        for token in OVERCLAIM_TOKENS:
            if token in text:
                failures.append(f"{path.relative_to(ROOT)} contains overclaim token: {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate artifacts")
    args = parser.parse_args()
    if not args.check:
        parser.print_help()
        return 2

    failures: list[str] = []
    for check in (check_metadata, check_tags, check_counts, check_logs, check_queue, check_docs, check_no_overclaim):
        try:
            check(failures)
        except Exception as exc:  # pragma: no cover - direct CLI guard
            failures.append(f"{check.__name__}: {exc}")

    print("Wave648 CRT fd/locale/itoa probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Status: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6093 total, 2601 commentless, 1217 exact-undefined, 814 param_N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
