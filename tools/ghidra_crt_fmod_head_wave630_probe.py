#!/usr/bin/env python3
"""Validate Wave630 CRT fmod/FPU Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave630-crt-fmod-head"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_fmod_head_wave630_2026-05-20.md"
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
    "0x00563ada": (
        "CRT__FpuIntDispatch2_Handle",
        "void CRT__FpuIntDispatch2_Handle(void)",
        ("custom FPU dispatch helper", "CRT__HandleFloatingPointException", "Static FPU-dispatch evidence only"),
        ("crt-runtime", "fpu-dispatch", "fpu-exception", "custom-stack"),
    ),
    "0x00563c0b": (
        "__ctrandisp1",
        "undefined __ctrandisp1(void)",
        ("Visual Studio library-match __ctrandisp1", "__fload", "Static library-helper evidence only"),
        ("crt-runtime", "fpu-transcendental", "library-match", "fpu-dispatch"),
    ),
    "0x00563c3e": (
        "__fload",
        "undefined __fload(void)",
        ("Visual Studio library-match __fload", "split IEEE-754 double", "Static library-helper evidence only"),
        ("crt-runtime", "fpu-load", "library-match", "split-double"),
    ),
    "0x00564486": (
        "CRT__FmodReduceCore",
        "int __cdecl CRT__FmodReduceCore(int param_1, uint param_2, int param_3)",
        ("custom-stack long-double remainder reduction helper", "FPREM-based reductions", "Static FPU remainder evidence only"),
        ("crt-runtime", "fmod-core", "fpu-remainder", "custom-stack"),
    ),
    "0x0056468c": (
        "CRT__FmodCore",
        "double CRT__FmodCore(void)",
        ("fmod-family core", "CRT__FmodReduceCore", "Static FPU remainder evidence only"),
        ("crt-runtime", "fmod-core", "fpu-remainder", "custom-stack"),
    ),
}

COMMON_TAGS = {"static-reaudit", "crt-fmod-head-wave630", "retail-binary-evidence", "comment-hardened"}
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
        (BASE / "post-metadata.tsv", 5, "metadata rows"),
        (BASE / "post-tags.tsv", 5, "tag rows"),
        (BASE / "post-xrefs.tsv", 9, "xref rows"),
        (BASE / "post-instructions.tsv", 505, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "post-decompile.log")
    require_tokens("post-decompile.log", decomp, ("targets=5 dumped=5 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        safe_name = re.sub(r"[^A-Za-z0-9_]+", "_", name)
        file_name = f"{address[2:]}_{safe_name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2764,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 964,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x00564a0b" or head["name"] != "CDXTexture__LoadFromPathWithFallbackExtensions":
        failures.append(f"unexpected next queue head: {head}")

    backup = read_json(BASE / "backup-summary.json")
    require_tokens(
        "backup summary",
        json.dumps(backup),
        ("G:\\GhidraBackups\\BEA_20260520-084254_post_wave630_crt_fmod_verified",),
        failures,
    )
    if backup.get("SourceFiles") != 19 or backup.get("BackupFiles") != 19:
        failures.append(f"backup file counts unexpected: {backup}")
    if int(backup.get("SourceBytes", -1)) != 162204551 or int(backup.get("BackupBytes", -1)) != 162204551:
        failures.append(f"backup byte counts unexpected: {backup}")
    if backup.get("DiffCount") != 0:
        failures.append(f"backup DiffCount is {backup.get('DiffCount')}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-wave630-dry.log", failures)
    apply = parse_log_summary(BASE / "apply-wave630-apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-wave630-final-dry.log", failures)
    expect_summary("dry", dry, {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    expect_summary("apply", apply, {"updated": 5, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    expect_summary("final dry", final_dry, {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


def check_docs(failures: list[str]) -> None:
    expected_tokens = (
        "Wave630",
        "CRT__FmodReduceCore",
        "CRT__FmodCore",
        "0x00564a0b CDXTexture__LoadFromPathWithFallbackExtensions",
        "3329",
        "2764",
        "3276/6093 = 53.77%",
        "G:\\GhidraBackups\\BEA_20260520-084254_post_wave630_crt_fmod_verified",
    )
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, CRT_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        require_tokens(path.name, text, expected_tokens, failures)
        for token in OVERCLAIM_TOKENS:
            if token in text.lower():
                failures.append(f"{path.name} contains overclaim token: {token}")
    require_tokens("package.json", read_text(PACKAGE_JSON), ("test:ghidra-crt-fmod-head-wave630",), failures)
    require_tokens("ledger", read_text(LEDGER), ("Wave630 CRT fmod/FPU head hardening", "3276/6093 = 53.77%"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("\"attempt_id\":20285", "Wave630 CRT fmod/FPU head hardening"), failures)
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20286:
        failures.append(f"tracking next_attempt_id expected 20286, saw {tracking.get('next_attempt_id')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave630 hardened five CRT FPU/fmod helper rows",), failures)


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
        print("Wave630 CRT fmod/FPU probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave630 CRT fmod/FPU probe: PASS")
    print("Verified 5 saved metadata rows, 5 tag rows, 9 xref rows, 505 instruction rows, 5 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
