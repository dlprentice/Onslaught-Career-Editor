#!/usr/bin/env python3
"""Validate Wave638 CRT command-line/runtime Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave638-crt-commandline-runtime"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_commandline_runtime_wave638_2026-05-20.md"
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
    "0x00568dc6": (
        "CRT__ParseCommandLineToken",
        "char * __cdecl CRT__ParseCommandLineToken(void)",
        ("command-line cursor helper", "DAT_009d35f4", "Static CRT command-line evidence only"),
        ("crt-runtime", "command-line", "startup"),
    ),
    "0x00568e1e": (
        "CRT__BuildEnvironTable",
        "void __cdecl CRT__BuildEnvironTable(void)",
        ("process-start environment table builder", "DAT_009d090c", "Static CRT environment evidence only"),
        ("crt-runtime", "environment", "startup"),
    ),
    "0x00568ed7": (
        "CRT__BuildArgvTable",
        "void __cdecl CRT__BuildArgvTable(void)",
        ("process-start argv table builder", "CRT__ParseCommandLineToArgv", "Static CRT argv evidence only"),
        ("crt-runtime", "command-line", "argv", "startup"),
    ),
    "0x00568f70": (
        "CRT__ParseCommandLineToArgv",
        "void __cdecl CRT__ParseCommandLineToArgv(char * commandLine, char * * argvTable, char * argTextBuffer, int * outArgvSlotCount, int * outArgTextBytes)",
        ("two-pass command-line parser", "backslash/quote runs", "Static CRT argv parsing evidence only"),
        ("crt-runtime", "command-line", "argv", "parser"),
    ),
    "0x00569124": (
        "CRT__GetEnvironmentStringsDupA",
        "char * __cdecl CRT__GetEnvironmentStringsDupA(void)",
        ("duplicated ANSI environment-block helper", "GetEnvironmentStringsW", "Static CRT environment evidence only"),
        ("crt-runtime", "environment", "startup", "spawn", "name-corrected"),
    ),
    "0x00569256": (
        "CRT__ReportRuntimeErrorIfCriticalMode",
        "void __cdecl CRT__ReportRuntimeErrorIfCriticalMode(void)",
        ("critical-mode runtime-error reporter", "runtime code 0xfc", "Static CRT runtime-error evidence only"),
        ("crt-runtime", "runtime-error", "startup"),
    ),
    "0x0056928f": (
        "CRT__ReportRuntimeError",
        "void __cdecl CRT__ReportRuntimeError(int runtimeErrorCode)",
        ("runtime-error message dispatcher", "CRT__MessageBoxA_WithActivePopupFallback", "Static CRT runtime-error evidence only"),
        ("crt-runtime", "runtime-error", "message"),
    ),
    "0x005693e2": (
        "CRT__IsReadablePtr",
        "bool __cdecl CRT__IsReadablePtr(void * ptr, uint byteCount)",
        ("readable-pointer probe", "IsBadReadPtr", "Static CRT pointer-probe evidence only"),
        ("crt-runtime", "pointer-probe", "seh"),
    ),
    "0x005693fe": (
        "CRT__IsWritablePtr",
        "bool __cdecl CRT__IsWritablePtr(void * ptr, uint byteCount)",
        ("writable-pointer probe", "IsBadWritePtr", "Static CRT pointer-probe evidence only"),
        ("crt-runtime", "pointer-probe", "seh"),
    ),
    "0x0056941a": (
        "CRT__IsExecutablePtr",
        "bool __cdecl CRT__IsExecutablePtr(void * codePtr)",
        ("executable-pointer probe", "IsBadCodePtr", "Static CRT pointer-probe evidence only"),
        ("crt-runtime", "pointer-probe", "seh"),
    ),
    "0x00569432": (
        "CRT__FatalRuntimeErrorAndExit",
        "void __cdecl CRT__FatalRuntimeErrorAndExit(void)",
        ("fatal runtime-error exit helper", "reports runtime error code 10", "Static CRT fatal-exit evidence only"),
        ("crt-runtime", "runtime-error", "fatal-exit"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-commandline-runtime-wave638",
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
        (BASE / "post-metadata.tsv", 11, "metadata rows"),
        (BASE / "post-tags.tsv", 11, "tag rows"),
        (BASE / "post-xrefs.tsv", 26, "xref rows"),
        (BASE / "post-instructions.tsv", 1331, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=11 dumped=11 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave638-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave638-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave638-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 1, "signature_updated": 0, "varargs": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 11, "skipped": 0, "renamed": 1, "would_rename": 0, "signature_updated": 11, "varargs": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 0, "signature_updated": 0, "varargs": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2690,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 902,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x00569449" or head["name"] != "CRT__ControlFp":
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
    if commented != 3403:
        failures.append(f"commented count expected 3403, saw {commented}")
    if strict != 3352:
        failures.append(f"strict clean-signature proxy numerator expected 3352, saw {strict}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("[maintainer-local-ghidra-backup-root]\\BEA_20260520-122438_post_wave638_crt_commandline_runtime_verified",),
        failures,
    )
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count unexpected: {backup}")
    if int(backup.get("totalBytes", -1)) != 162532231:
        failures.append(f"backup byte count unexpected: {backup}")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount is {backup.get('diffCount')}")


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave638",
        "CRT__ParseCommandLineToken",
        "CRT__BuildEnvironTable",
        "CRT__BuildArgvTable",
        "CRT__ParseCommandLineToArgv",
        "CRT__GetEnvironmentStringsDupA",
        "CRT__ReportRuntimeErrorIfCriticalMode",
        "CRT__ReportRuntimeError",
        "CRT__IsReadablePtr",
        "CRT__IsWritablePtr",
        "CRT__IsExecutablePtr",
        "CRT__FatalRuntimeErrorAndExit",
        "3403",
        "2690",
        "3352/6093 = 55.01%",
        "0x00569449 CRT__ControlFp",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260520-122438_post_wave638_crt_commandline_runtime_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-commandline-runtime-wave638",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave638 CRT command-line/runtime hardening", "3352/6093 = 55.01%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20293", "Wave638 CRT command-line/runtime hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20294:
        failures.append(f"tracking next_attempt_id expected 20294, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave638 CRT command-line/runtime hardening",), failures)


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
        print("Wave638 CRT command-line/runtime probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave638 CRT command-line/runtime probe: PASS")
    print("Verified 11 saved metadata rows, 11 tag rows, 26 xref rows, 1331 instruction rows, 11 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
