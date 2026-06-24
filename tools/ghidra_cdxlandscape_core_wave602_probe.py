#!/usr/bin/env python3
"""Validate Wave602 CDXLandscape core Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave602-cdxlandscape-core-00544fc0"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxlandscape_core_wave602_2026-05-19.md"
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
    "0x00544fc0": (
        "CDXLandscape__BuildVertexBuffer",
        "void __fastcall CDXLandscape__BuildVertexBuffer(void * this)",
    ),
    "0x00545070": (
        "CDXLandscape__Reset",
        "void __fastcall CDXLandscape__Reset(void * this)",
    ),
    "0x005453d0": (
        "CDXLandscape__LoadCloudShadowTexture",
        "void __fastcall CDXLandscape__LoadCloudShadowTexture(void * this)",
    ),
    "0x005453f0": (
        "CDXLandscape__SetTileData",
        "void __thiscall CDXLandscape__SetTileData(void * this, void * tile_context, int record_index)",
    ),
}

EXPECTED_TAGS = {
    "0x00544fc0": {"cdxlandscape", "vertex-buffer", "heightfield", "terrain-grid", "cvbuffer"},
    "0x00545070": {"cdxlandscape", "reset", "resource-array", "terrain-grid", "landscape-texture", "patch-slots"},
    "0x005453d0": {"cdxlandscape", "cloud-shadow", "texture-load", "init-resources"},
    "0x005453f0": {"cdxlandscape", "set-tile-data", "ret-0x8", "resource-record", "updatepos"},
}

COMMENT_TOKENS = {
    "0x00544fc0": ("CVBuffer__Lock", "0x41 by 0x41", "0x14-byte", "CHeightField__GetHeightSamplePacked16", "unlocks the buffer", "plain RET"),
    "0x00545070": ("+0x24 resource-record array", "CLandscapeTexture update queue", "CDXLandscape__CreateMipLevels", "g_LandscapeDetailLevel2", "64x64", "CDXEngine__ComputeLandscapeTileComplexityScore", "loads the waves texture"),
    "0x005453d0": ("CEngine__InitResources", "CTexture__FindTexture", "clouds_shadow.tga", "+0x38", "plain RET"),
    "0x005453f0": ("RET 0x8", "engine+0x4a8", "engine+0x10", "tile_context", "engine+0x4ac", "record_index * 0x34", "resource_record+0x10"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxlandscape-core-wave602",
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
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 4, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


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
        "post/xrefs_after.tsv": 7,
        "post/instructions_after.tsv": 1476,
        "post/decomp_after/index.tsv": 4,
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
        ("0x00544fc0", "CDXLandscape__BuildVertexBuffer", "0x005451aa", "0x00545070", "CDXLandscape__Reset", "UNCONDITIONAL_CALL"),
        ("0x00544fc0", "CDXLandscape__BuildVertexBuffer", "0x005473c6", "0x005473b0", "CDXEngine__InvalidateLandscapeTilesAndPatchSlots", "UNCONDITIONAL_CALL"),
        ("0x00545070", "CDXLandscape__Reset", "0x0044a1a9", "0x0044a130", "CEngine__InitDamageSystem", "UNCONDITIONAL_CALL"),
        ("0x00545070", "CDXLandscape__Reset", "0x00545424", "0x00545410", "CDXLandscape__Render", "UNCONDITIONAL_CALL"),
        ("0x00545070", "CDXLandscape__Reset", "0x00544fb0", "0x00544fb0", "CDXLandscape__ResetWrapper", "UNCONDITIONAL_CALL"),
        ("0x005453d0", "CDXLandscape__LoadCloudShadowTexture", "0x00449db5", "0x00449d50", "CEngine__InitResources", "UNCONDITIONAL_CALL"),
        ("0x005453f0", "CDXLandscape__SetTileData", "0x0044a1d9", "0x0044a1c0", "CEngine__UpdatePos", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens(
        "instructions_after",
        instruction_text,
        (
            "CALL\t0x005001b0",
            "CALL\t0x0047ea20",
            "CALL\t0x005001e0",
            "CALL\t0x0048e7b0",
            "CALL\t0x005447e0",
            "CALL\t0x00544fc0",
            "CALL\t0x0048f180",
            "CALL\t0x00556470",
            "CALL\t0x004f27f0",
            "MOV\tdword ptr [ESI + 0x38], EAX",
            "MOV\tdword ptr [ECX + EAX*0x4 + 0x10], EDX",
            "RET\t0x8",
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
        "Wave602",
        "CDXLandscape__BuildVertexBuffer",
        "CDXLandscape__Reset",
        "CDXLandscape__LoadCloudShadowTexture",
        "CDXLandscape__SetTileData",
        "0x00545410 CDXLandscape__Render",
        "3001",
        "commentless",
        "1320",
        "exact-undefined",
        "1073",
        "G:\\GhidraBackups\\BEA_20260519-184356_post_wave602_cdxlandscape_core_verified",
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

    require_tokens("public note", public_note, ("updated=4", "skipped=4", "1476", "DiffCount=0", "Strict clean-signature proxy"), failures)

    ledger_rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not any(row.get("task") == "Ghidra CDXLandscape core Wave602 signature/comment hardening" and row.get("status") == "completed" for row in ledger_rows):
        failures.append("ledger missing Wave602 completed row")

    attempt_rows = [json.loads(line) for line in ATTEMPT_LOG.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    wave_attempt = next((row for row in attempt_rows if row.get("attempt_id") == 20257), None)
    if not wave_attempt:
        failures.append("attempt log missing attempt_id 20257")
    else:
        require_tokens("attempt 20257 notes", wave_attempt.get("notes", ""), ("Wave602", "updated=4", "queue telemetry", "0x00545410"), failures)

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 998, "attempt_rows": 20258, "completed": 989, "pending": 9}
    counters = tracking.get("counters", {})
    for key, expected in expected_counters.items():
        if counters.get(key) != expected:
            failures.append(f"tracking counter {key} mismatch: {counters.get(key)} != {expected}")
    if tracking.get("next_attempt_id") != 20258:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20258")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave602", "0x00545410", "CDXLandscape__Render"), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backup") != "G:\\GhidraBackups\\BEA_20260519-184356_post_wave602_cdxlandscape_core_verified":
        failures.append(f"backup path mismatch: {backup.get('backup')}")
    expected = {
        "file_count": 19,
        "byte_count": 161221511,
        "diff_count": 0,
        "manifest_sha256": "ff0bc70f109410ec28abe3a06adadb2b641ffce463c9824cf9ed3e539a2b3be1",
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
        "commentlessFunctionCount": 3001,
        "undefinedSignatureCount": 1320,
        "paramSignatureCount": 1073,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x00545410":
        failures.append("queue head mismatch: expected 0x00545410")


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
        print("Wave602 CDXLandscape core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave602 CDXLandscape core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
