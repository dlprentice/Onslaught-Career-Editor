#!/usr/bin/env python3
"""Validate Wave649 CRT env/locale/string Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave649-crt-env-locale-string"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_env_locale_string_wave649_2026-05-20.md"
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
    "0x0056e271": (
        "CRT__GetEnvVarValuePointerCaseInsensitive",
        "char * __cdecl CRT__GetEnvVarValuePointerCaseInsensitive(char * variableName)",
        ("environment lookup", "NAME=value", "Wave649"),
        ("crt-runtime", "environment", "case-insensitive", "string-compare", "name-corrected"),
    ),
    "0x0056e2ee": (
        "CRT__SetFdTextBinaryModeFlag_NoLock",
        "int __cdecl CRT__SetFdTextBinaryModeFlag_NoLock(uint fdIndex, int modeFlag)",
        ("text/binary mode flag", "EINVAL", "Wave649"),
        ("crt-runtime", "fd-table", "text-mode", "binary-mode", "file-io"),
    ),
    "0x0056e34f": (
        "CRT__GetLocaleInfoAsWide",
        "int __cdecl CRT__GetLocaleInfoAsWide(uint localeId, int localeInfoType, ushort * outWideBuffer, int outWideChars, uint codePage)",
        ("GetLocaleInfoW", "MultiByteToWideChar", "Wave649"),
        ("crt-runtime", "locale", "GetLocaleInfo", "wide-char", "NLS"),
    ),
    "0x0056e462": (
        "CRT__GetLocaleInfoAsMultiByte",
        "int __cdecl CRT__GetLocaleInfoAsMultiByte(uint localeId, int localeInfoType, char * outBuffer, int outChars, uint codePage)",
        ("GetLocaleInfoA", "WideCharToMultiByte", "Wave649"),
        ("crt-runtime", "locale", "GetLocaleInfo", "multibyte", "NLS"),
    ),
    "0x0056e5bf": (
        "CRT__ProcessWideEnvTableToMultibyte",
        "int __cdecl CRT__ProcessWideEnvTableToMultibyte(void)",
        ("corrected stale Argv", "wide environment table", "Wave649"),
        ("crt-runtime", "environment", "wide-char", "multibyte", "name-corrected"),
    ),
    "0x0056e62d": (
        "CRT__CompareLocaleStringsWithMBCSFallback",
        "int __cdecl CRT__CompareLocaleStringsWithMBCSFallback(uint localeId, uint compareFlags, char * leftText, int leftCount, char * rightText, int rightCount, uint codePage)",
        ("CompareString", "lead-byte edge", "Wave649"),
        ("crt-runtime", "locale", "string-compare", "multibyte", "CompareString"),
    ),
    "0x0056e8aa": (
        "CRT__StrNLen",
        "int __cdecl CRT__StrNLen(char * text, int maxChars)",
        ("bounded strlen", "maxChars", "Wave649"),
        ("crt-runtime", "string", "bounded-length"),
    ),
    "0x0056e8d5": (
        "CRT__PutEnvStringAndUpdateProcessEnv",
        "int __cdecl CRT__PutEnvStringAndUpdateProcessEnv(char * envAssignment, int updateProcessEnv)",
        ("putenv-style updater", "SetEnvironmentVariableA", "Wave649"),
        ("crt-runtime", "environment", "putenv", "SetEnvironmentVariable", "allocation"),
    ),
    "0x0056ea5c": (
        "CRT__FindEnvVarIndexOrInsertionPoint",
        "int __cdecl CRT__FindEnvVarIndexOrInsertionPoint(char * envAssignment, int nameLength)",
        ("negative insertion index", "case-insensitive", "Wave649"),
        ("crt-runtime", "environment", "case-insensitive", "string-compare", "table-scan"),
    ),
    "0x0056eab4": (
        "CRT__CloneEnvironmentTable",
        "char * * __cdecl CRT__CloneEnvironmentTable(char * * envTable)",
        ("null-terminated CRT environment", "CRT__StrDup", "Wave649"),
        ("crt-runtime", "environment", "allocation", "string-dup", "table-clone"),
    ),
    "0x0056eb1b": (
        "CRT__StrDup",
        "char * __cdecl CRT__StrDup(char * sourceText)",
        ("strdup-style helper", "allocation failure", "Wave649"),
        ("crt-runtime", "string", "allocation", "string-dup"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-env-locale-string-wave649",
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
        (BASE / "post-metadata.tsv", 11, "metadata rows"),
        (BASE / "post-tags.tsv", 11, "tag rows"),
        (BASE / "post-xrefs.tsv", 19, "xref rows"),
        (BASE / "post-instructions.tsv", 3091, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=11 dumped=11 missing=0 failed=0", "REPORT: Save succeeded"), failures)


def check_logs(failures: list[str]) -> None:
    expect_summary("dry", parse_log_summary(BASE / "apply-dry.log", failures), {
        "updated": 0, "skipped": 11, "renamed": 0, "would_rename": 2, "signature_updated": 0, "missing": 0, "bad": 0,
    }, failures)
    expect_summary("apply", parse_log_summary(BASE / "apply.log", failures), {
        "updated": 11, "skipped": 0, "renamed": 2, "would_rename": 0, "signature_updated": 11, "missing": 0, "bad": 0,
    }, failures)
    expect_summary("final dry", parse_log_summary(BASE / "apply-final-dry.log", failures), {
        "updated": 0, "skipped": 11, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0,
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
        "commentlessFunctionCount": 2590,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 805,
    }
    for key, value in expected.items():
        actual = queue.get(key) if key == "totalFunctions" else signals.get(key)
        if actual != value:
            failures.append(f"queue {key}: expected {value}, saw {actual}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if normalize_address(head["address"]) != "0x0056eb50" or head["name"] != "CDXMeshVB__SetTriangleStripDebugFlag":
        failures.append(f"unexpected next queue head: {head}")
    rows = read_tsv_rows(QUEUE_TSV)
    by_addr = {normalize_address(row["address"]): row for row in rows}
    for address, (name, signature, _comment_tokens, _tags) in TARGETS.items():
        row = by_addr.get(address)
        if not row:
            failures.append(f"queue TSV missing {address}")
        elif row["name"] != name or row["signature"] != signature or row["comment"] == "":
            failures.append(f"queue TSV did not preserve Wave649 metadata for {address}")


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    if "test:ghidra-crt-env-locale-string-wave649" not in package.get("scripts", {}):
        failures.append("package.json missing Wave649 npm script")
    required_docs = {
        PUBLIC_NOTE: ("Wave649", "CRT__ProcessWideEnvTableToMultibyte", "2590", "805", "G:\\GhidraBackups\\BEA_20260520-222000_post_wave649_crt_env_locale_string_verified"),
        FUNCTION_INDEX: ("Wave649", "CRT__CloneEnvironmentTable", "0x0056eb50"),
        CRT_DOC: ("Wave649", "CRT__GetEnvVarValuePointerCaseInsensitive", "CDXMeshVB__SetTriangleStripDebugFlag"),
        GHIDRA_REFERENCE: ("Wave649", "CRT__CompareLocaleStringsWithMBCSFallback", "crt-env-locale-string-wave649"),
        CAMPAIGN: ("Wave649", "2590", "0x0056eb50"),
        BACKLOG: ("Wave649 CRT env/locale/string hardening", "0x0056e271,0x0056e2ee", "DiffCount=0"),
        LEDGER: ("Wave649 CRT env/locale/string hardening", "crt-env-locale-string-wave649", "next head 0x0056eb50"),
        ATTEMPT_LOG: ("Wave649 CRT env/locale/string hardening", "\"attempt_id\":20304", "accepted dry/apply/final/post evidence"),
    }
    for path, tokens in required_docs.items():
        require_tokens(str(path.relative_to(ROOT)), read_text(path), tokens, failures)
    tracking = read_json(TRACKING)
    if tracking["counters"]["ledger_rows"] < 1045 or tracking["counters"]["attempt_rows"] < 20305:
        failures.append("tracking counters were not advanced for Wave649")
    require_tokens("tracking notes", json.dumps(tracking), ("Wave649", "0x0056eb50", "2590"), failures)


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

    print("Wave649 CRT env/locale/string probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Status: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6093 total, 2590 commentless, 1217 exact-undefined, 805 param_N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
