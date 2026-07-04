#!/usr/bin/env python3
"""Validate Wave603 CDXLandscape render Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave603-cdxlandscape-render-00545410"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxlandscape_render_wave603_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00545410": (
        "CDXLandscape__Render",
        "void __thiscall CDXLandscape__Render(void * this, void * engine_context_470, int record_index)",
    ),
    "0x00545590": (
        "CDXLandscape__RenderTerrain",
        "void __thiscall CDXLandscape__RenderTerrain(void * this, int record_index)",
    ),
}

EXPECTED_TAGS = {
    "0x00545410": {"cdxlandscape", "render-entry", "ret-0x8", "lod-forwarder", "cached-lights", "world-matrix"},
    "0x00545590": {"cdxlandscape", "render-terrain", "ret-0x4", "resource-record", "texture-stages", "shadow-map"},
}

COMMENT_TOKENS = {
    "0x00545410": (
        "RET 0x8",
        "engine+0x4a8",
        "engine+0x10",
        "engine+0x470",
        "CDXLandscape__UpdateLOD",
        "DAT_008c0280",
        "DAT_008aa9c0",
        "CDXLandscape__RenderTerrain(record_index)",
        "cached lights with flag 0",
    ),
    "0x00545590": (
        "RET 0x4",
        "record_index*0x34",
        "cloud-shadow scroll offsets",
        "CWaterRenderSystem__ValidateVBufferAndMarkReady",
        "this+0x30",
        "DAT_0067a7d0",
        "this+0x38",
        "this+0x2c",
        "this+0x28",
        "CDXLandscape__RenderShadowMap(0)",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxlandscape-render-wave603",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}
OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully recovered", "fully reverse-engineered")


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "Function not found", "Input file not found", "Read-back signature mismatch"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 2, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata_after.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags_after.tsv")}
    if set(metadata_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata_rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], COMMENT_TOKENS[address], failures)
        require_tokens(f"{address} comment", row["comment"], ("BEA patching", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tag_rows.get(address)
        if not tag_row:
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = (COMMON_TAGS | EXPECTED_TAGS[address]) - actual_tags
        if tag_row["name"] != name:
            failures.append(f"{address} tag name mismatch: {tag_row['name']} != {name}")
        if tag_row["status"] != "OK":
            failures.append(f"{address} tag status mismatch: {tag_row['status']}")
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "post/xrefs_after.tsv": 2,
        "post/instructions_after.tsv": 1818,
        "post/decomp_after/index.tsv": 2,
    }
    actual_counts = {
        "post/xrefs_after.tsv": row_count(POST / "xrefs_after.tsv"),
        "post/instructions_after.tsv": row_count(POST / "instructions_after.tsv"),
        "post/decomp_after/index.tsv": row_count(POST / "decomp_after" / "index.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_instructions(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(POST / "xrefs_after.tsv")
    }
    expected_xrefs = {
        ("0x00545410", "CDXLandscape__Render", "0x0053e688", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
        ("0x00545590", "CDXLandscape__RenderTerrain", "0x00545520", "0x00545410", "CDXLandscape__Render", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens(
        "instructions_after",
        instruction_text,
        (
            "PUSH\tEDI",
            "PUSH\tEDX",
            "RET\t0x8",
            "CALL\t0x00546b40",
            "CALL\t0x00545590",
            "RET\t0x4",
            "CALL\t0x00527cc0",
            "CALL\t0x00527d20",
            "CALL\t0x00500320",
            "CALL\t0x00500360",
            "CALL\t0x00513c70",
            "CALL\t0x00546490",
        ),
        failures,
    )


def check_docs_and_logs(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    dx_doc = read_text(DXLANDSCAPE_DOC)
    fn_index = read_text(FUNCTION_INDEX)
    campaign = read_text(CAMPAIGN)
    backlog = read_text(BACKLOG)

    common_doc_tokens = (
        "Wave603",
        "CDXLandscape__Render",
        "CDXLandscape__RenderTerrain",
        "0x00546220 CDXLandscape__SetRenderTarget",
        "2999",
        "commentless",
        "1318",
        "exact-undefined",
        "1073",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260519-191021_post_wave603_cdxlandscape_render_verified",
    )
    for label, text in {
        "public note": public_note,
        "DXLandscape doc": dx_doc,
        "function index": fn_index,
        "campaign": campaign,
        "backlog": backlog,
    }.items():
        require_tokens(label, text, common_doc_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    require_tokens("public note", public_note, ("updated=2", "skipped=2", "1818", "DiffCount=0", "Strict clean-signature proxy"), failures)

    ledger_rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not any(row.get("task") == "Ghidra CDXLandscape render Wave603 signature/comment hardening" and row.get("status") == "completed" for row in ledger_rows):
        failures.append("ledger missing Wave603 completed row")

    attempt_rows = [json.loads(line) for line in ATTEMPT_LOG.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    wave_attempt = next((row for row in attempt_rows if row.get("attempt_id") == 20258), None)
    if not wave_attempt:
        failures.append("attempt log missing attempt_id 20258")
    else:
        require_tokens("attempt 20258 notes", wave_attempt.get("notes", ""), ("Wave603", "updated=2", "queue telemetry", "0x00546220"), failures)

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 999, "attempt_rows": 20259, "completed": 990, "pending": 9}
    counters = tracking.get("counters", {})
    for key, expected in expected_counters.items():
        if counters.get(key) != expected:
            failures.append(f"tracking counter {key} mismatch: {counters.get(key)} != {expected}")
    if tracking.get("next_attempt_id") != 20259:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20259")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave603", "0x00546220", "CDXLandscape__SetRenderTarget"), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("destination") != "[maintainer-local-ghidra-backup-root]\\BEA_20260519-191021_post_wave603_cdxlandscape_render_verified":
        failures.append(f"backup path mismatch: {backup.get('destination')}")
    expected = {
        "fileCount": 19,
        "totalBytes": 161254279,
        "diffCount": 0,
        "manifestHash": "bfb0b4f044d5d6c0aa6708eeee074e5ec1c4a65f6ab66448d51d0efa573f22ba",
    }
    for key, expected_value in expected.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2999,
        "undefinedSignatureCount": 1318,
        "paramSignatureCount": 1073,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x00546220":
        failures.append("queue head mismatch: expected 0x00546220")


def run_check() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs_and_instructions(failures)
        check_backup_and_queue(failures)
        check_docs_and_logs(failures)
    except Exception as exc:  # noqa: BLE001 - probe should report all unexpected read failures.
        failures.append(f"probe exception: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave603 CDXLandscape render probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave603 CDXLandscape render probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
