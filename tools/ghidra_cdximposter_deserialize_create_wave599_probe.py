#!/usr/bin/env python3
"""Validate Wave599 CDXImposter deserialize/create Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave599-cdximposter-deserialize-create-00543d90"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdximposter_deserialize_create_wave599_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXIMPOSTER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXImposter.cpp" / "_index.md"
IMPOSTER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "imposter.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00543d90": (
        "CDXImposter__Deserialize",
        "void __cdecl CDXImposter__Deserialize(void * chunk_reader)",
    ),
    "0x00543f50": (
        "CDXImposter__Create",
        "void * __cdecl CDXImposter__Create(void * chunk_reader)",
    ),
}

EXPECTED_TAGS = {
    "0x00543d90": {"cdximposter", "deserialize", "imps-chunk", "chunk-reader", "texture-atlas", "cvbuftexture"},
    "0x00543f50": {"cdximposter", "create", "oid-allocation", "frame-data", "cimposter", "chunk-reader"},
}

COMMENT_TOKENS = {
    "0x00543d90": ("0x004d7705", "0x008aa8c0", "0x008aa8c4", "0x008aa8b8", "0x008aa8b4/0x008aa8cc", "0x0067a67c"),
    "0x00543f50": ("0x4c OID type 0x39", "+0x30/+0x38/+0x3c", "0x008aa8bc", "CMesh__FindByRuntimeId", "+0x44 * +0x40 * 0x18", "CImposter__AddToList"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdximposter-deserialize-create-wave599",
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
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
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
    for bad_token in ("LockException", "Function not found", "Input file not found"):
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
        require_tokens(f"{address} comment", row["comment"], ("Static retail evidence only", "BEA patching", "rebuild parity remain unproven"), failures)
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
        "post/instructions_after.tsv": 514,
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
        ("0x00543d90", "CDXImposter__Deserialize", "0x004d7706", "0x004d7200", "CResourceAccumulator__ReadResourceFile", "UNCONDITIONAL_CALL"),
        ("0x00543f50", "CDXImposter__Create", "0x00543e3b", "0x00543d90", "CDXImposter__Deserialize", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instructions = {
        (
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in read_tsv_rows(POST / "instructions_after.tsv")
    }
    expected_instructions = {
        ("0x00543e3a", "CDXImposter__Deserialize", "PUSH", "ESI"),
        ("0x00543e3b", "CDXImposter__Deserialize", "CALL", "0x00543f50"),
        ("0x00543f46", "CDXImposter__Deserialize", "RET", ""),
        ("0x00543f54", "CDXImposter__Create", "PUSH", "0x7e3"),
        ("0x00543fb3", "CDXImposter__Create", "CALL", "0x00423960"),
        ("0x00543fd4", "CDXImposter__Create", "CALL", "0x004ab330"),
        ("0x0054402c", "CDXImposter__Create", "CALL", "0x00488a70"),
        ("0x00544037", "CDXImposter__Create", "RET", ""),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")


def check_docs_and_ledgers(failures: list[str]) -> None:
    texts = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "DXImposter doc": read_text(DXIMPOSTER_DOC),
        "imposter doc": read_text(IMPOSTER_DOC),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    required_tokens = (
        "Wave599",
        "0x00543d90",
        "0x00543f50",
        "3074",
        "3019",
        "1331",
        "1080",
        "3029/6093 = 49.71%",
        "0x00544040 CDXEngine__ClearHudTextureSlots",
        "BEA_20260519-171359_post_wave599_cdximposter_deserialize_create_verified",
    )
    for label, text in texts.items():
        require_tokens(label, text, required_tokens[:3], failures)
        if label in {"public note", "function index", "campaign", "backlog", "ledger", "attempt log"}:
            require_tokens(label, text, required_tokens[3:], failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20255:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    counters = tracking.get("counters", {})
    if counters.get("ledger_rows") != 995 or counters.get("attempt_rows") != 20255 or counters.get("completed") != 986:
        failures.append(f"tracking counters mismatch: {counters}")


def check_backup_and_queue(failures: list[str]) -> None:
    summary = read_json(BACKUP_SUMMARY)
    expected_backup = "G:\\GhidraBackups\\BEA_20260519-171359_post_wave599_cdximposter_deserialize_create_verified"
    if summary.get("backupPath") != expected_backup:
        failures.append(f"backup path mismatch: {summary.get('backupPath')}")
    if summary.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {summary.get('fileCount')}")
    if int(summary.get("totalBytes", 0)) != 161155975:
        failures.append(f"backup totalBytes mismatch: {summary.get('totalBytes')}")
    for key in ("missingCount", "extraCount", "diffCount"):
        if summary.get(key) != 0:
            failures.append(f"backup {key} mismatch: {summary.get(key)}")
    if summary.get("manifestHash") != "df8ccc75f58e1c97db971b748b64b6909d61a4c602e16ce1fbc7c27f95178fa5":
        failures.append(f"backup manifestHash mismatch: {summary.get('manifestHash')}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    expected_quality = {
        "commentlessFunctionCount": 3019,
        "undefinedSignatureCount": 1331,
        "paramSignatureCount": 1080,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00544040" or head.get("name") != "CDXEngine__ClearHudTextureSlots":
        failures.append(f"queue head mismatch: {head}")


def run_check() -> list[str]:
    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs_and_instructions(failures)
    check_docs_and_ledgers(failures)
    check_backup_and_queue(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave599 CDXImposter deserialize/create probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave599 CDXImposter deserialize/create probe: PASS")
    print("Verified 2 saved signatures/comments/tags, read-back exports, docs, ledgers, queue telemetry, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
