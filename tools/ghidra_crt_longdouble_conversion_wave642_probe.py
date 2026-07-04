#!/usr/bin/env python3
"""Validate Wave642 CRT long-double conversion Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave642-crt-longdouble-conversion"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_longdouble_conversion_wave642_2026-05-20.md"
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
    "0x005698e3": (
        "CRT__ConvertLongDoubleByFormatSpec",
        "int __cdecl CRT__ConvertLongDoubleByFormatSpec(void * longDouble80, void * outBits, void * formatSpec)",
        ("format-spec table", "Wave641 96-bit mantissa helpers", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "format-spec", "rounding", "float32", "float64"),
    ),
    "0x00569a4f": (
        "CRT__ConvertLongDoubleToFloat32",
        "void __cdecl CRT__ConvertLongDoubleToFloat32(void * longDouble80, void * outFloat32Bits)",
        ("DAT_006561c0", "CRT__ConvertLongDoubleByFormatSpec", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "format-spec", "float32"),
    ),
    "0x00569a65": (
        "CRT__ConvertLongDoubleToFloat64",
        "void __cdecl CRT__ConvertLongDoubleToFloat64(void * longDouble80, void * outFloat64Bits)",
        ("DAT_006561d8", "CRT__ConvertLongDoubleByFormatSpec", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "format-spec", "float64"),
    ),
    "0x00569a7b": (
        "CRT__ParseFloatTextToFloat32",
        "void __cdecl CRT__ParseFloatTextToFloat32(void * outFloat32Bits, int parseFlags)",
        ("12-byte long-double scratch", "CRT__ConvertLongDoubleToFloat32", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "parser", "float32"),
    ),
    "0x00569aa8": (
        "CRT__ParseFloatTextToFloat64",
        "void __cdecl CRT__ParseFloatTextToFloat64(void * outFloat64Bits, int parseFlags)",
        ("12-byte long-double scratch", "CRT__ConvertLongDoubleToFloat64", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "parser", "float64"),
    ),
    "0x00569ad5": (
        "CRT__BuildRoundedMantissaDigits",
        "void __cdecl CRT__BuildRoundedMantissaDigits(char * outDigits, int requestedDigits, void * decimalRecord)",
        ("rounds upward", "decimal exponent field", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "decimal-record", "rounding", "digits"),
    ),
    "0x00569b4c": (
        "CRT__ConvertLongDoubleToDecimalRecord",
        "int * __cdecl CRT__ConvertLongDoubleToDecimalRecord(int inputLowBits, int inputHighBits, void * decimalRecord, char * digitsBuffer)",
        ("CRT__NormalizeLongDouble80MantissaExp", "returns decimalRecord", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "decimal-record", "digits"),
    ),
    "0x00569ba8": (
        "CRT__NormalizeLongDouble80MantissaExp",
        "void __cdecl CRT__NormalizeLongDouble80MantissaExp(void * outLongDouble80, void * float64Bits)",
        ("IEEE-754-style float64 bits", "Inf/NaN", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "long-double", "normalize", "float64"),
    ),
    "0x00569cc1": (
        "CRT__HandleFloatingPointException",
        "void __cdecl CRT__HandleFloatingPointException(int unusedStatus, void * fpExceptionRecord, void * controlWordPtr)",
        ("CRT__FpuIntDispatch2_Handle", "sets errno", "Static CRT floating-point conversion evidence only"),
        ("crt-runtime", "floating-point", "fpu-exception", "errno"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-longdouble-conversion-wave642",
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
        (BASE / "post-metadata.tsv", 9, "metadata rows"),
        (BASE / "post-tags.tsv", 9, "tag rows"),
        (BASE / "post-xrefs.tsv", 16, "xref rows"),
        (BASE / "post-instructions.tsv", 2349, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=9 dumped=9 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave642-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave642-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave642-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
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


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2668,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 880,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x00569d91" or head["name"] != "CRT__InitFileBuffer":
        failures.append(f"unexpected next queue head: {head}")

    rows = read_tsv_rows(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    if commented != 3425:
        failures.append(f"commented count expected 3425, saw {commented}")
    if strict != 3374:
        failures.append(f"strict clean-signature proxy numerator expected 3374, saw {strict}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("[maintainer-local-ghidra-backup-root]\\BEA_20260520-140845_post_wave642_crt_longdouble_conversion_verified",),
        failures,
    )
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count unexpected: {backup}")
    if int(backup.get("totalBytes", -1)) != 162597767:
        failures.append(f"backup byte count unexpected: {backup}")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount is {backup.get('diffCount')}")


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave642",
        "CRT__ConvertLongDoubleByFormatSpec",
        "CRT__ConvertLongDoubleToFloat32",
        "CRT__ConvertLongDoubleToFloat64",
        "CRT__ParseFloatTextToFloat32",
        "CRT__ParseFloatTextToFloat64",
        "CRT__BuildRoundedMantissaDigits",
        "CRT__ConvertLongDoubleToDecimalRecord",
        "CRT__NormalizeLongDouble80MantissaExp",
        "CRT__HandleFloatingPointException",
        "3425",
        "2668",
        "3374/6093 = 55.37%",
        "0x00569d91 CRT__InitFileBuffer",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260520-140845_post_wave642_crt_longdouble_conversion_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-longdouble-conversion-wave642",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave642 CRT long-double conversion hardening", "3374/6093 = 55.37%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20297", "Wave642 CRT long-double conversion hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20298:
        failures.append(f"tracking next_attempt_id expected 20298, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave642 CRT long-double conversion hardening",), failures)


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
        print("Wave642 CRT long-double conversion probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave642 CRT long-double conversion probe: PASS")
    print("Verified 9 saved metadata rows, 9 tag rows, 16 xref rows, 2349 instruction rows, 9 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
