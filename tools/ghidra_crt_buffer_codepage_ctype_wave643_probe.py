#!/usr/bin/env python3
"""Validate Wave643 CRT buffer/codepage/ctype Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave643-crt-buffer-codepage-ctype"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_buffer_codepage_ctype_wave643_2026-05-20.md"
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
    "0x00569d91": (
        "CRT__InitFileBuffer",
        "void __cdecl CRT__InitFileBuffer(void * stream)",
        ("stream buffer", "0x1000-byte heap buffer", "Static CRT I/O evidence only"),
        ("crt-runtime", "stream-buffer", "stdio", "allocation"),
    ),
    "0x00569dd5": (
        "CRT__IsFdCommitMode",
        "int __cdecl CRT__IsFdCommitMode(uint fdIndex)",
        ("file-descriptor table", "0x40 commit/text flag", "Static CRT I/O evidence only"),
        ("crt-runtime", "fd-table", "stdio", "commit-mode"),
    ),
    "0x00569dfe": (
        "CRT__WideCharToCurrentCodePage_WithLocaleGuard",
        "int __cdecl CRT__WideCharToCurrentCodePage_WithLocaleGuard(char * outBytes, int wideChar)",
        ("locale-guard wrapper", "lock 0x13", "Static CRT codepage evidence only"),
        ("crt-runtime", "codepage", "wide-char", "locale-guard"),
    ),
    "0x00569e57": (
        "CRT__WideCharToCurrentCodePage",
        "int __cdecl CRT__WideCharToCurrentCodePage(char * outBytes, int wideChar)",
        ("WideCharToMultiByte", "errno 0x2a", "Static CRT codepage evidence only"),
        ("crt-runtime", "codepage", "wide-char", "errno"),
    ),
    "0x00569f35": (
        "CRT__MultiByteToWideChar_ThreadSafe",
        "int __cdecl CRT__MultiByteToWideChar_ThreadSafe(void * outWideChar, char * inputBytes, uint inputByteCount)",
        ("locale-guard wrapper", "CRT__MultiByteToWideChar_SingleToken", "Static CRT codepage evidence only"),
        ("crt-runtime", "codepage", "multibyte", "wide-char", "locale-guard"),
    ),
    "0x00569f92": (
        "CRT__MultiByteToWideChar_SingleToken",
        "uint __cdecl CRT__MultiByteToWideChar_SingleToken(void * outWideChar, char * inputBytes, uint inputByteCount)",
        ("MBCS lead-byte checks", "MultiByteToWideChar", "Static CRT codepage evidence only"),
        ("crt-runtime", "codepage", "multibyte", "wide-char", "errno"),
    ),
    "0x0056a05b": (
        "CRT__IsAlpha",
        "uint __cdecl CRT__IsAlpha(int charValue)",
        ("mask 0x103", "CRT__GetCharTypeMask_Compat", "Static CRT ctype evidence only"),
        ("crt-runtime", "ctype", "alpha", "codepage"),
    ),
    "0x0056a089": (
        "CRT__IsDigit",
        "uint __cdecl CRT__IsDigit(int charValue)",
        ("mask 0x04", "CRT__GetCharTypeMask_Compat", "Static CRT ctype evidence only"),
        ("crt-runtime", "ctype", "digit", "codepage"),
    ),
    "0x0056a0b1": (
        "CRT__IsCharTypeMask0x80",
        "uint __cdecl CRT__IsCharTypeMask0x80(int charValue)",
        ("mask 0x80", "CRT__GetCharTypeMask_Compat", "Static CRT ctype evidence only"),
        ("crt-runtime", "ctype", "mask-0x80", "codepage"),
    ),
    "0x0056a0de": (
        "CRT__IsCharTypeMask0x08",
        "uint __cdecl CRT__IsCharTypeMask0x08(int charValue)",
        ("mask 0x08", "CRT__GetCharTypeMask_Compat", "Static CRT ctype evidence only"),
        ("crt-runtime", "ctype", "mask-0x08", "codepage"),
    ),
    "0x0056a106": (
        "CRT__GetCharClassMask",
        "uint __cdecl CRT__GetCharClassMask(int charValue)",
        ("combined 0x107 ctype class mask", "CRT__GetCharTypeMask_Compat", "Static CRT ctype evidence only"),
        ("crt-runtime", "ctype", "mask-0x107", "codepage"),
    ),
    "0x0056a15f": (
        "CRT__UngetCharToStream",
        "uint __cdecl CRT__UngetCharToStream(uint character, void * stream)",
        ("ungetc-style stream pushback", "commit/text-mode byte agreement", "Static CRT I/O evidence only"),
        ("crt-runtime", "stdio", "stream-buffer", "ungetc"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-buffer-codepage-ctype-wave643",
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
        (BASE / "post-metadata.tsv", 12, "metadata rows"),
        (BASE / "post-tags.tsv", 12, "tag rows"),
        (BASE / "post-xrefs.tsv", 53, "xref rows"),
        (BASE / "post-instructions.tsv", 3132, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=12 dumped=12 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-dry.log", failures)
    apply = parse_log_summary(BASE / "apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 2, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 12, "skipped": 0, "renamed": 2, "would_rename": 0, "signature_updated": 12, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2656,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 868,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0056a7e7" or head["name"] != "CRT__ValidatePathAttributesForOpen":
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
    if commented != 3437:
        failures.append(f"commented count expected 3437, saw {commented}")
    if strict != 3386:
        failures.append(f"strict clean-signature proxy numerator expected 3386, saw {strict}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("G:\\GhidraBackups\\BEA_20260520-143149_post_wave643_crt_buffer_codepage_ctype_verified",),
        failures,
    )
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count unexpected: {backup}")
    if int(backup.get("totalBytes", -1)) != 162663303:
        failures.append(f"backup byte count unexpected: {backup}")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount is {backup.get('diffCount')}")


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave643",
        "CRT__InitFileBuffer",
        "CRT__IsFdCommitMode",
        "CRT__WideCharToCurrentCodePage_WithLocaleGuard",
        "CRT__MultiByteToWideChar_SingleToken",
        "CRT__IsAlpha",
        "CRT__IsDigit",
        "CRT__UngetCharToStream",
        "3437",
        "2656",
        "3386/6093 = 55.57%",
        "0x0056a7e7 CRT__ValidatePathAttributesForOpen",
        "G:\\GhidraBackups\\BEA_20260520-143149_post_wave643_crt_buffer_codepage_ctype_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-buffer-codepage-ctype-wave643",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave643 CRT buffer/codepage/ctype hardening", "3386/6093 = 55.57%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20298", "Wave643 CRT buffer/codepage/ctype hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20299:
        failures.append(f"tracking next_attempt_id expected 20299, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave643 CRT buffer/codepage/ctype hardening",), failures)


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
        print("Wave643 CRT buffer/codepage/ctype probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave643 CRT buffer/codepage/ctype probe: PASS")
    print("Verified 12 saved metadata rows, 12 tag rows, 53 xref rows, 3132 instruction rows, 12 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
