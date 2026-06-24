#!/usr/bin/env python3
"""Validate Wave647 CRT long-double tail Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave647-crt-longdouble-tail"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_longdouble_tail_wave647_2026-05-20.md"
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
    "0x0056d525": (
        "CRT__LongDoubleShiftMantissaLeft1",
        "void __cdecl CRT__LongDoubleShiftMantissaLeft1(void * longDouble80)",
        ("mantissa buffer left", "low dword", "Wave647"),
        ("crt-runtime", "floating-point", "long-double", "mantissa", "bit-shift"),
    ),
    "0x0056d553": (
        "CRT__LongDoubleShiftMantissaRight1",
        "void __cdecl CRT__LongDoubleShiftMantissaRight1(void * longDouble80)",
        ("mantissa buffer right", "high dword", "Wave647"),
        ("crt-runtime", "floating-point", "long-double", "mantissa", "bit-shift"),
    ),
    "0x0056d580": (
        "CRT__AccumulateDecimalDigitsToLongDouble",
        "void __cdecl CRT__AccumulateDecimalDigitsToLongDouble(char * digitBytes, int digitCount, void * outLongDouble80)",
        ("digit bytes", "multiply-by-ten", "Wave647"),
        ("crt-runtime", "floating-point", "long-double", "decimal-digits", "normalize"),
    ),
    "0x0056d647": (
        "CRT__ConvertLongDoubleToDecimalRecordCore",
        "int __cdecl CRT__ConvertLongDoubleToDecimalRecordCore(uint longDoubleLow, uint longDoubleMid, uint signExponentWord, int requestedDigits, uint conversionFlags, void * outDecimalRecord)",
        ("decimal-record conversion core", "Wave642 wrapper", "Wave647"),
        ("crt-runtime", "floating-point", "long-double", "decimal-record", "rounding", "digits"),
    ),
    "0x0056d8da": (
        "CRT__LongDoubleMultiply10Byte",
        "void __cdecl CRT__LongDoubleMultiply10Byte(void * accumulatorLongDouble80, void * multiplierLongDouble80)",
        ("10-byte long-double multiplier", "16-bit partial products", "Wave647"),
        ("crt-runtime", "floating-point", "long-double", "multiply", "rounding"),
    ),
    "0x0056dafa": (
        "CRT__LongDoubleScaleByPowerOf10",
        "void __cdecl CRT__LongDoubleScaleByPowerOf10(void * longDouble80, int decimalExponent, int preserveMantissaFlag)",
        ("signed decimal exponent", "power-of-ten constant tables", "Wave647"),
        ("crt-runtime", "floating-point", "long-double", "power-of-ten", "scale"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-longdouble-tail-wave647",
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
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY line")
        return {}
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
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
        missing = (COMMON_TAGS | set(tags)) - actual
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")


def check_counts(failures: list[str]) -> None:
    checks = [
        (BASE / "post-metadata.tsv", 6, "metadata rows"),
        (BASE / "post-tags.tsv", 6, "tag rows"),
        (BASE / "post-xrefs.tsv", 17, "xref rows"),
        (BASE / "post-instructions.tsv", 606, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=6 dumped=6 missing=0 failed=0", "REPORT: Save succeeded"), failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue["qualitySignals"]
    expected = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 2608,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 821,
    }
    for key, value in expected.items():
        actual = queue.get(key) if key == "totalFunctions" else signals.get(key)
        if actual != value:
            failures.append(f"queue {key}: expected {value}, saw {actual}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if normalize_address(head["address"]) != "0x0056db76" or head["name"] != "CRT__ChangeFileSizeByFd_NoLock":
        failures.append(f"unexpected next queue head: {head}")
    rows = read_tsv_rows(QUEUE_TSV)
    by_addr = {normalize_address(row["address"]): row for row in rows}
    for address, (name, signature, _comment_tokens, _tags) in TARGETS.items():
        row = by_addr.get(address)
        if not row:
            failures.append(f"queue TSV missing {address}")
        elif row["name"] != name or row["signature"] != signature or row["comment"] == "":
            failures.append(f"queue TSV did not preserve Wave647 metadata for {address}")


def check_logs(failures: list[str]) -> None:
    expect_summary("dry", parse_log_summary(BASE / "apply-dry.log", failures), {
        "updated": 0, "skipped": 6, "renamed": 0, "would_rename": 4, "signature_updated": 0, "missing": 0, "bad": 0,
    }, failures)
    expect_summary("apply", parse_log_summary(BASE / "apply.log", failures), {
        "updated": 6, "skipped": 0, "renamed": 4, "would_rename": 0, "signature_updated": 6, "missing": 0, "bad": 0,
    }, failures)
    expect_summary("final dry", parse_log_summary(BASE / "apply-final-dry.log", failures), {
        "updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0,
    }, failures)
    for log in BASE.glob("*.log"):
        text = read_text(log)
        if "LockException" in text or "BAD:" in text or "BADNAME:" in text or "MISSING:" in text:
            failures.append(f"{log.name} contains failure marker")


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    if "test:ghidra-crt-longdouble-tail-wave647" not in package.get("scripts", {}):
        failures.append("package.json missing Wave647 npm script")
    required_docs = {
        PUBLIC_NOTE: ("Wave647", "CRT__LongDoubleShiftMantissaLeft1", "2608", "821", "G:\\GhidraBackups\\BEA_20260520-162946_post_wave647_crt_longdouble_tail_verified"),
        FUNCTION_INDEX: ("Wave647", "CRT__ConvertLongDoubleToDecimalRecordCore", "0x0056db76"),
        CRT_DOC: ("Wave647", "CRT__LongDoubleScaleByPowerOf10", "CRT__ChangeFileSizeByFd_NoLock"),
        GHIDRA_REFERENCE: ("Wave647", "CRT__AccumulateDecimalDigitsToLongDouble", "crt-longdouble-tail-wave647"),
        CAMPAIGN: ("Wave647", "6", "2608", "0x0056db76"),
        BACKLOG: ("Wave647 CRT long-double tail hardening", "0x0056d525,0x0056d553", "DiffCount=0"),
        LEDGER: ("Wave647 CRT long-double tail hardening", "crt-longdouble-tail-wave647", "next head 0x0056db76"),
        ATTEMPT_LOG: ("Wave647 CRT long-double tail hardening", "attempt_id", "accepted dry/apply/final/post evidence"),
    }
    for path, tokens in required_docs.items():
        require_tokens(str(path.relative_to(ROOT)), read_text(path), tokens, failures)
    tracking = read_json(TRACKING)
    if tracking["counters"]["ledger_rows"] < 1043 or tracking["counters"]["attempt_rows"] < 20303:
        failures.append("tracking counters were not advanced for Wave647")
    require_tokens("tracking notes", json.dumps(tracking), ("Wave647", "0x0056db76", "2608"), failures)
    note = read_text(PUBLIC_NOTE).lower()
    for token in OVERCLAIM_TOKENS:
        if token in note:
            failures.append(f"public note contains overclaim token: {token}")


def run_checks() -> list[str]:
    failures: list[str] = []
    check_logs(failures)
    check_metadata(failures)
    check_tags(failures)
    check_counts(failures)
    check_queue(failures)
    check_docs(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures = run_checks()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "targets": len(TARGETS),
        "queue": read_json(QUEUE_JSON),
        "failures": failures,
    }
    print("Wave647 CRT long-double tail probe")
    print(f"Status: {result['status']}")
    print(f"Targets: {result['targets']}")
    signals = result["queue"]["qualitySignals"]
    print(
        "Queue: "
        f"{result['queue']['totalFunctions']} total, "
        f"{signals['commentlessFunctionCount']} commentless, "
        f"{signals['undefinedSignatureCount']} exact-undefined, "
        f"{signals['paramSignatureCount']} param_N"
    )
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
