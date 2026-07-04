#!/usr/bin/env python3
"""Validate Wave615 CDXSnow/CAtmosphericsProfile Ghidra boundary artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave615-cdxsnow-init-0055515e"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxsnow_boundary_wave615_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXSNOW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSnow.cpp.md"
ATMOS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Atmospherics.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGET = "0x00555020"
STALE = "0x0055515e"
NAME = "CAtmosphericsProfile__ResetAndInitSnowResources"
SIGNATURE = "void __thiscall CAtmosphericsProfile__ResetAndInitSnowResources(void * this)"

COMMON_TAGS = {
    "static-reaudit",
    "cdxsnow-boundary-wave615",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "boundary-corrected",
    "vtable-verified",
    "catmospherics-profile",
    "snow",
    "resource-init",
    "seh-prologue",
}

OVERCLAIM_TOKENS = (
    "runtime snow behavior proven",
    "runtime weather behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
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
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back signature mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave615-dry.log",
        {
            "updated": 0,
            "skipped": 1,
            "created": 0,
            "would_create": 1,
            "deleted": 0,
            "would_delete": 1,
            "body_set": 0,
            "would_set_body": 1,
            "renamed": 0,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )
    require_log_summary(
        BASE / "apply-wave615-apply.log",
        {
            "updated": 1,
            "skipped": 0,
            "created": 1,
            "would_create": 0,
            "deleted": 1,
            "would_delete": 0,
            "body_set": 1,
            "would_set_body": 0,
            "renamed": 0,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )
    require_log_summary(
        BASE / "apply-wave615-final-dry.log",
        {
            "updated": 0,
            "skipped": 1,
            "created": 0,
            "would_create": 0,
            "deleted": 0,
            "would_delete": 0,
            "body_set": 0,
            "would_set_body": 0,
            "renamed": 0,
            "would_rename": 0,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )

    expected_log_tokens = {
        "post-context-metadata.log": "targets=5 found=4 missing=1",
        "post-context-tags.log": "rows=4 missing=1",
        "post-context-xrefs.log": "Wrote 5 rows",
        "post-instructions.log": "Wrote 339 instruction rows",
        "post-context-decompile.log": "targets=5 dumped=4 missing=1 failed=0",
        "post-vtable-slots.log": "targets=1 rows=8",
        "queue-snapshot-refresh.log": "total_functions=6093 commented_functions=3160",
    }
    for log_name, token in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, (token,), failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    by_address = {normalize_address(row["address"]): row for row in rows}
    target = by_address.get(TARGET)
    if not target:
        failures.append("post-context-metadata missing corrected target")
        return
    if target["name"] != NAME:
        failures.append(f"target name mismatch: {target['name']} != {NAME}")
    if target["signature"] != SIGNATURE:
        failures.append(f"target signature mismatch: {target['signature']} != {SIGNATURE}")
    if target["status"] != "OK":
        failures.append(f"target status mismatch: {target['status']}")
    require_tokens(
        "metadata comment",
        target["comment"],
        ("Wave615", "0x005e5974", STALE, "0x00555020-0x00555403", "remain unproven"),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in target["comment"].lower():
            failures.append(f"metadata comment overclaims: {token}")

    stale = by_address.get(STALE)
    if not stale or stale.get("status") != "MISSING":
        failures.append("stale split address is not recorded as missing in metadata")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    target_tags = None
    for row in tag_rows:
        if normalize_address(row["address"]) == TARGET:
            target_tags = set(filter(None, row["tags"].split(";")))
            break
    if target_tags is None:
        failures.append("post-context-tags missing corrected target")
    else:
        missing = COMMON_TAGS - target_tags
        if missing:
            failures.append(f"missing target tags: {sorted(missing)}")


def check_exports(failures: list[str]) -> None:
    counts = {
        "post-context-xrefs.tsv": (len(read_tsv_rows(BASE / "post-context-xrefs.tsv")), 5),
        "post-instructions.tsv": (len(read_tsv_rows(BASE / "post-instructions.tsv")), 339),
        "post-context-decompile/index.tsv": (len(read_tsv_rows(BASE / "post-context-decompile" / "index.tsv")), 5),
        "post-vtable-slots.tsv": (len(read_tsv_rows(BASE / "post-vtable-slots.tsv")), 8),
    }
    for label, (actual, expected) in counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    require_tokens(
        "post-context-xrefs.tsv",
        read_text(BASE / "post-context-xrefs.tsv"),
        (TARGET[2:], "005e5980", STALE[2:] + "\t<no_function>\t<none>", "00555410"),
        failures,
    )
    require_tokens(
        "post-vtable-slots.tsv",
        read_text(BASE / "post-vtable-slots.tsv"),
        ("005e5980\t0x00555020\t00555020\t00555020\tCAtmosphericsProfile__ResetAndInitSnowResources",),
        failures,
    )
    require_tokens(
        "post-instructions.tsv",
        read_text(BASE / "post-instructions.tsv"),
        (
            "0x00555020\t0x00555020\tTARGET\t0\t0x00555020\t0x00555020\tCAtmosphericsProfile__ResetAndInitSnowResources",
            "0x0055515e\t0x00555020\tCAtmosphericsProfile__ResetAndInitSnowResources",
            "0x00555403\t0x00555020\tCAtmosphericsProfile__ResetAndInitSnowResources\tRET",
            "0x00555410\t0x00555410\tCAtmosphericsProfile__ReleaseResources",
        ),
        failures,
    )
    decompile = read_text(BASE / "post-context-decompile" / "00555020_CAtmosphericsProfile__ResetAndInitSnowResources.c")
    require_tokens(
        "post decompile",
        decompile,
        (
            "void __thiscall CAtmosphericsProfile__ResetAndInitSnowResources(void *this)",
            "CTexture__FindTexture(s_Atmospherics_Snow_Snow_tga_00652560",
            "CConsole__RegisterVariable",
            "CVBufTexture__SetVBFormat",
            "CVBufTexture__UnlockIB",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "[maintainer-local-ghidra-backup-root]\\BEA_20260520-011651_post_wave615_cdxsnow_boundary_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161614727,
        "destBytes": 161614727,
        "diffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")
    if backup.get("diffs"):
        failures.append("backup diffs not empty")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 2933,
        "undefinedSignatureCount": 1271,
        "paramSignatureCount": 1056,
    }
    if queue.get("totalFunctions") != expected_queue["totalFunctions"]:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_queue.items():
        if key == "totalFunctions":
            continue
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x005563d0":
        failures.append("queue next high-signal head mismatch")


def check_public_docs(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        public_note,
        (
            "# Ghidra CDXSnow Boundary Wave615",
            "CAtmosphericsProfile__ResetAndInitSnowResources",
            "0x0055515e` is no longer a function entry",
            "Read-back exports verified `4` context metadata rows plus the expected stale-address miss",
            "Next queue head: `0x005563d0 CDXSurf__RenderSurface`",
            "Runtime snow/weather behavior remains unproven.",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in public_note.lower():
            failures.append(f"public note overclaims: {token}")

    require_tokens(
        "package.json",
        read_text(PACKAGE_JSON),
        ("test:ghidra-cdxsnow-boundary-wave615", "ghidra_cdxsnow_boundary_wave615_probe.py"),
        failures,
    )
    require_tokens(
        "function index",
        read_text(FUNCTION_INDEX),
        ("Wave615 CDXSnow boundary correction", "0x005563d0 CDXSurf__RenderSurface", "3160/6093 = 51.86%", "3115/6093 = 51.12%"),
        failures,
    )
    require_tokens(
        "DXSnow doc",
        read_text(DXSNOW_DOC),
        (
            "Last updated: 2026-05-20",
            "Wave615",
            "0x00555020",
            "0x0055515e",
            "CAtmosphericsProfile__ResetAndInitSnowResources",
            "Runtime snow/weather behavior remains unproven.",
        ),
        failures,
    )
    require_tokens(
        "Atmospherics doc",
        read_text(ATMOS_DOC),
        ("Wave615", "0x005e5980", "CAtmosphericsProfile__ResetAndInitSnowResources", "0x0055515e"),
        failures,
    )
    require_tokens(
        "campaign",
        read_text(CAMPAIGN),
        ("after Wave615", "ghidra_cdxsnow_boundary_wave615_2026-05-20.md", "0x005563d0 CDXSurf__RenderSurface"),
        failures,
    )
    require_tokens(
        "backlog",
        read_text(BACKLOG),
        ("0x00555020/0x0055515e", "Ghidra CDXSnow boundary Wave615 correction", "DiffCount=0"),
        failures,
    )
    require_tokens(
        "ledger",
        read_text(LEDGER),
        ("Ghidra CDXSnow boundary Wave615 correction", "cdxsnow-boundary-wave615", "0x005563d0 CDXSurf__RenderSurface"),
        failures,
    )
    require_tokens(
        "attempt log",
        read_text(ATTEMPT_LOG),
        ("\"attempt_id\":20270", "Ghidra CDXSnow boundary Wave615 correction", "headless_java_delete_stale_create_boundary_signature_comment_tags"),
        failures,
    )
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20271:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    if tracking.get("counters", {}).get("ledger_rows") != 1011:
        failures.append(f"tracking ledger_rows mismatch: {tracking.get('counters', {}).get('ledger_rows')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave615", "0x005563d0 CDXSurf__RenderSurface"), failures)


def run_checks() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_metadata_and_tags(failures)
        check_exports(failures)
        check_backup_and_queue(failures)
        check_public_docs(failures)
    except Exception as exc:  # pragma: no cover - failure reporting path
        failures.append(f"{exc.__class__.__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_checks()
    if failures:
        print("Wave615 CDXSnow boundary probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave615 CDXSnow boundary probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
