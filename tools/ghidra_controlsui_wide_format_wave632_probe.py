#!/usr/bin/env python3
"""Validate Wave632 ControlsUI wide-format Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave632-controlsui-wide-format-head"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_controlsui_wide_format_wave632_2026-05-20.md"
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
    "0x00565083": (
        "ControlsUI__FormatWideStringCore",
        "int __cdecl ControlsUI__FormatWideStringCore(void * outputTarget, short * formatWide, void * argList)",
        ("core wide formatted-output formatter", "ControlsUI__FormatWideStringSafe", "Static decompile/xref evidence only"),
        ("controlsui", "wide-format", "format-output"),
    ),
    "0x005657d0": (
        "ControlsUI__WriteWideCharAndCount",
        "void __cdecl ControlsUI__WriteWideCharAndCount(uint wideChar, void * outputTarget, int * count)",
        ("single wide-character output/count helper", "CRT__WriteWideCharToStreamWithConversion", "Static wide-output evidence only"),
        ("controlsui", "wide-output", "format-output"),
    ),
    "0x005657f0": (
        "ControlsUI__WriteRepeatedWideChar",
        "void __cdecl ControlsUI__WriteRepeatedWideChar(uint wideChar, int repeatCount, void * outputTarget, int * count)",
        ("repeated wide-character padding helper", "ControlsUI__WriteWideCharAndCount", "Static padding/output evidence only"),
        ("controlsui", "wide-output", "format-output", "padding"),
    ),
    "0x00565821": (
        "ControlsUI__WriteWideStringAndCount",
        "void __cdecl ControlsUI__WriteWideStringAndCount(short * wideText, int wideCharCount, void * outputTarget, int * count)",
        ("bounded wide-string output helper", "used only by ControlsUI__FormatWideStringCore", "Static wide-string output evidence only"),
        ("controlsui", "wide-output", "format-output", "name-corrected"),
    ),
    "0x0056585a": (
        "CRT__ReadLongLongAndAdvanceArgList",
        "longlong __cdecl CRT__ReadLongLongAndAdvanceArgList(void * argListPtr)",
        ("printf-style arg-list reader for 64-bit values", "EDX:EAX", "Static vararg-reader evidence only"),
        ("crt-runtime", "format-output", "vararg-reader", "name-corrected"),
    ),
}

COMMON_TAGS = {"static-reaudit", "controlsui-wide-format-wave632", "retail-binary-evidence", "comment-hardened", "signature-hardened"}
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
        (BASE / "post-metadata.tsv", 5, "metadata rows"),
        (BASE / "post-tags.tsv", 5, "tag rows"),
        (BASE / "post-xrefs.tsv", 12, "xref rows"),
        (BASE / "post-instructions.tsv", 505, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=5 dumped=5 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave632-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave632-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave632-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 2, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 5, "skipped": 0, "renamed": 2, "would_rename": 0, "signature_updated": 5, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2749,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 948,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0056586a" or head["name"] != "CRT__SetLocale":
        failures.append(f"unexpected next queue head: {head}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("[maintainer-local-ghidra-backup-root]\\BEA_20260520-094434_post_wave632_controlsui_wide_format_verified",),
        failures,
    )
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count unexpected: {backup}")
    if int(backup.get("totalBytes", -1)) != 162302855:
        failures.append(f"backup byte count unexpected: {backup}")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount is {backup.get('diffCount')}")


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave632",
        "ControlsUI__FormatWideStringCore",
        "ControlsUI__WriteWideStringAndCount",
        "CRT__ReadLongLongAndAdvanceArgList",
        "3344",
        "2749",
        "3292/6093 = 54.03%",
        "0x0056586a CRT__SetLocale",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260520-094434_post_wave632_controlsui_wide_format_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        for token in OVERCLAIM_TOKENS:
            if token in text.lower():
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-controlsui-wide-format-wave632",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave632 ControlsUI wide-format hardening", "3292/6093 = 54.03%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20287", "Wave632 ControlsUI wide-format hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20288:
        failures.append(f"tracking next_attempt_id expected 20288, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave632 ControlsUI wide-format hardening",), failures)


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
        print("Wave632 ControlsUI wide-format probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave632 ControlsUI wide-format probe: PASS")
    print("Verified 5 saved metadata rows, 5 tag rows, 12 xref rows, 505 instruction rows, 5 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
