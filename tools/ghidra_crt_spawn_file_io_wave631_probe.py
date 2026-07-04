#!/usr/bin/env python3
"""Validate Wave631 CRT spawn/file I/O Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave631-crt-spawn-file-io-head"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_spawn_file_io_wave631_2026-05-20.md"
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
    "0x0055e412": (
        "CRT__SpawnPathVarargsNoEnv_Thunk",
        "void __cdecl CRT__SpawnPathVarargsNoEnv_Thunk(int spawnMode, char * commandPath)",
        ("fixed stale CDXTexture owner label", "forwards to CRT__SpawnSearchPathWithFallbackExtensions", "Static CRT spawn wrapper evidence only"),
        ("crt-runtime", "spawn", "stale-owner-corrected", "varargs-thunk"),
    ),
    "0x0055e45f": (
        "CRT__OpenFileByModeString_AutoUnlock",
        "void * __cdecl CRT__OpenFileByModeString_AutoUnlock(char * path, char * modeString, int shareFlags)",
        ("fopen-facing wrapper", "CRT__UnlockRouteByAddress", "Static CRT file-open evidence only"),
        ("crt-runtime", "file-open", "stdio", "auto-unlock"),
    ),
    "0x005638a8": (
        "CRT__FlushStreamIfWritePending",
        "void __cdecl CRT__FlushStreamIfWritePending(int enabled, void * stream)",
        ("fixes the stale callee owner", "CRT__FlushWriteStreamSegment", "Static CRT stream-output evidence only"),
        ("crt-runtime", "stream-output", "stdio-buffer", "stale-callee-corrected"),
    ),
    "0x00564a0b": (
        "CRT__SpawnSearchPathWithFallbackExtensions",
        "int __cdecl CRT__SpawnSearchPathWithFallbackExtensions(int spawnMode, char * commandPath, void * argv, void * envp)",
        ("fixed stale CDXTexture owner label", "validates candidates through CRT__ValidatePathAttributesForOpen", "Static CRT spawn/path-probe evidence only"),
        ("crt-runtime", "spawn", "path-probe", "stale-owner-corrected"),
    ),
    "0x00564b54": (
        "CRT__SpawnResolvedPathWithBuiltCommandEnv",
        "int __cdecl CRT__SpawnResolvedPathWithBuiltCommandEnv(int spawnMode, char * resolvedPath, void * argv, void * envp)",
        ("CRT__BuildSpawnCommandAndEnv_0056ab1f", "CRT__SpawnVe_0056a936", "Static CRT spawn/CreateProcess evidence only"),
        ("crt-runtime", "spawn", "createprocess", "stale-owner-corrected"),
    ),
    "0x00564ba5": (
        "CRT__UnhandledExceptionFilterDispatch",
        "int __stdcall CRT__UnhandledExceptionFilterDispatch(void * exceptionPointers)",
        ("0xe06d7363", "0x19930520", "Static CRT/SEH evidence only"),
        ("crt-runtime", "seh", "unhandled-exception-filter"),
    ),
    "0x00564c09": (
        "CRT__OpenFileByModeString",
        "void * __cdecl CRT__OpenFileByModeString(char * path, char * modeString, int shareFlags, void * stream)",
        ("fopen-style mode strings", "CRT__OpenFd", "Static CRT file-open evidence only"),
        ("crt-runtime", "file-open", "stdio", "mode-parser"),
    ),
    "0x00564d79": (
        "CRT__AcquireFileStreamSlot",
        "void * __cdecl CRT__AcquireFileStreamSlot(void)",
        ("locks the global stream table", "0x38-byte descriptor", "Static CRT stream-table evidence only"),
        ("crt-runtime", "stdio", "stream-table", "lock"),
    ),
    "0x00564e41": (
        "CRT__CloseFd",
        "int __cdecl CRT__CloseFd(uint fdIndex)",
        ("validates an fd-table entry", "CRT__CloseFd_NoLock", "Static CRT fd-table evidence only"),
        ("crt-runtime", "file-close", "fd-table", "lock"),
    ),
    "0x00564e9e": (
        "CRT__CloseFd_NoLock",
        "int __cdecl CRT__CloseFd_NoLock(uint fdIndex)",
        ("CloseHandle", "CRT__SetErrnoAndDosErrnoFromWinError_00567a35", "Static CRT fd-table evidence only"),
        ("crt-runtime", "file-close", "fd-table", "win32-handle"),
    ),
    "0x00564f4c": (
        "CRT__FlushAndCommitFileStream",
        "int __cdecl CRT__FlushAndCommitFileStream(void * stream)",
        ("CRT__FlushWriteStreamSegment", "CRT__CommitFileHandle", "Static CRT stream-output evidence only"),
        ("crt-runtime", "stream-output", "flush", "commit"),
    ),
    "0x00564f7a": (
        "CRT__FlushWriteStreamSegment",
        "int __cdecl CRT__FlushWriteStreamSegment(void * stream)",
        ("fixed stale CDXTexture owner label", "CRT__WriteFdTextMode_Locking_00567505", "Static CRT stream-output evidence only"),
        ("crt-runtime", "stream-output", "flush", "stale-owner-corrected"),
    ),
    "0x00564fdf": (
        "CRT__FlushAllFileStreamsByMode",
        "int __cdecl CRT__FlushAllFileStreamsByMode(int flushMode)",
        ("walks active stream descriptors", "Mode 1 flushes and commits", "Static CRT stream-table evidence only"),
        ("crt-runtime", "stream-output", "flush-all", "stream-table"),
    ),
}

COMMON_TAGS = {"static-reaudit", "crt-spawn-file-io-wave631", "retail-binary-evidence", "comment-hardened", "signature-hardened"}
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
        (BASE / "post-metadata.tsv", 13, "metadata rows"),
        (BASE / "post-tags.tsv", 13, "tag rows"),
        (BASE / "post-xrefs.tsv", 24, "xref rows"),
        (BASE / "post-instructions.tsv", 1313, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "post-decompile.log")
    require_tokens("post-decompile.log", decomp, ("targets=13 dumped=13 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2754,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 953,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x00565083" or head["name"] != "ControlsUI__FormatWideStringCore":
        failures.append(f"unexpected next queue head: {head}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("[maintainer-local-ghidra-backup-root]\\BEA_20260520-092034_post_wave631_crt_spawn_file_io_verified",),
        failures,
    )
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count unexpected: {backup}")
    if int(backup.get("totalBytes", -1)) != 162302855:
        failures.append(f"backup byte count unexpected: {backup}")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount is {backup.get('diffCount')}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave631-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave631-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave631-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 0, "renamed": 0, "would_rename": 5, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 13, "skipped": 0, "renamed": 5, "would_rename": 0, "signature_updated": 12, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave631",
        "CRT__SpawnSearchPathWithFallbackExtensions",
        "CRT__SpawnResolvedPathWithBuiltCommandEnv",
        "CRT__FlushWriteStreamSegment",
        "CRT__FlushAllFileStreamsByMode",
        "3339",
        "2754",
        "3287/6093 = 53.95%",
        "0x00565083 ControlsUI__FormatWideStringCore",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260520-092034_post_wave631_crt_spawn_file_io_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        for token in OVERCLAIM_TOKENS:
            if token in text.lower():
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-spawn-file-io-wave631",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave631 CRT spawn/file I/O head correction", "3287/6093 = 53.95%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20286", "Wave631 CRT spawn/file I/O head correction"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20287:
        failures.append(f"tracking next_attempt_id expected 20287, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave631 corrected stale CDXTexture spawn/file I/O labels",), failures)


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
        print("Wave631 CRT spawn/file I/O probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave631 CRT spawn/file I/O probe: PASS")
    print("Verified 13 saved metadata rows, 13 tag rows, 24 xref rows, 1313 instruction rows, 13 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
