#!/usr/bin/env python3
"""Validate Wave728 YCC lookup/resource head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave728-ycc-lookup-resource-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ycc_lookup_resource_head_wave728_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "ycc-lookup-resource-head-wave728",
    "wave728-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "ycc-lookup-resource",
}

TARGETS = {
    "0x005af670": (
        "CDXTexture__InitEntropyDecodeResources",
        "void __stdcall CDXTexture__InitEntropyDecodeResources(void * decode_context)",
        ("initializes entropy/decode resource dispatch state", "allocates a 0xa0-byte controller", "Wave727 adaptive YCC helpers"),
        COMMON_TAGS | {"signature-hardened", "entropy-decode-resources", "component-resampler", "callback-dispatch-table", "allocator", "tranche-head"},
        False,
    ),
    "0x005af860": (
        "CDXTexture__BuildYccToRgbLookupTables",
        "void CDXTexture__BuildYccToRgbLookupTables(void)",
        ("hidden EAX as the texture decode context", "allocates four lookup buffers", "void(void) signature is intentionally retained"),
        COMMON_TAGS | {"comment-only", "hidden-eax-context", "coefficient-table", "ycc-rgb-lut"},
        True,
    ),
    "0x005afbd0": (
        "CDXTexture__InterleaveComponentRowsIntoScanline",
        "void __stdcall CDXTexture__InterleaveComponentRowsIntoScanline(void * decode_context, void * component_row_tables, int source_row_index, void * output_scanline_table, int scanline_count)",
        ("interleaves component row tables", "component count from decode_context +0x24", "output_scanline_table entries"),
        COMMON_TAGS | {"signature-hardened", "component-interleave", "scanline-output", "row-table-callback"},
        False,
    ),
    "0x005afcf0": (
        "CDXTexture__ConvertYccToRgba_WithLookupTables",
        "void __stdcall CDXTexture__ConvertYccToRgba_WithLookupTables(void * decode_context, void * source_component_row_table, int source_row_index, void * output_rgba_row_table, int scanline_count)",
        ("converts source component rows into RGBA output rows", "lookup-table pointers from the controller", "decode_context +0x148"),
        COMMON_TAGS | {"signature-hardened", "lookup-table-conversion", "rgba-output", "row-table-callback", "ycc-rgba-conversion"},
        False,
    ),
    "0x005afe60": (
        "CDXTexture__InitYccLookupTables",
        "void CDXTexture__InitYccLookupTables(void)",
        ("hidden EAX as the texture decode context", "allocates ten lookup buffers", "void(void) signature is intentionally retained"),
        COMMON_TAGS | {"comment-only", "hidden-eax-context", "coefficient-table", "extended-ycc-lut", "tranche-tail"},
        True,
    ),
}

DOC_TOKENS = (
    "Wave728 YCC lookup resource head",
    "ycc-lookup-resource-head-wave728",
    "0x005af670 CDXTexture__InitEntropyDecodeResources",
    "0x005af860 CDXTexture__BuildYccToRgbLookupTables",
    "0x005afbd0 CDXTexture__InterleaveComponentRowsIntoScanline",
    "0x005afcf0 CDXTexture__ConvertYccToRgba_WithLookupTables",
    "0x005afe60 CDXTexture__InitYccLookupTables",
    "0x005b0ee0 CDXTexture__InitScanlineColorConverter",
    "0x0042f220 CSPtrSet__Clear",
    r"[maintainer-local-ghidra-backup-root]\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime jpeg decode behavior proven",
    "runtime color conversion behavior proven",
    "runtime image decode behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 11,
        "pre-instructions.tsv": 2705,
        "pre-decompile/index.tsv": 5,
        "pre-caller-decompile/index.tsv": 1,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 11,
        "post-instructions.tsv": 2705,
        "post-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens, expected_tags, comment_only) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave728 static read-back" in comment, f"missing Wave728 comment at {address}", failures)
        require("Static retail Ghidra metadata" in comment, f"missing static-evidence boundary at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "post-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)

        if comment_only:
            require("comment-only" in set(tags[address[2:]].get("tags", "").split(";")) if address[2:] in tags else True, f"missing comment-only tag at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 11 rows",
        "pre-instructions.log": "Wrote 2705 instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "pre-caller-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-instructions.log": "Wrote 2705 instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BADNAME" not in text, f"unexpected BADNAME in {relative}", failures)
        require("FAIL:" not in text, f"unexpected FAIL in {relative}", failures)
        require("Invalid script" not in text, f"unexpected invalid script in {relative}", failures)
        require("Input file not found" not in text, f"stale failed export in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1813, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 90, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005b0ee0", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CDXTexture__InitScanlineColorConverter", "high-signal head name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    raw_head = next(row for row in rows if not row.get("comment", "").strip())
    require(commented == 4285, "commented count mismatch", failures)
    require(strict_clean == 4227, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    by_address = {normalize_address(row["address"]): row for row in rows}
    for address, (_, _, _, _, comment_only) in TARGETS.items():
        row = by_address.get(address)
        require(row is not None, f"missing queue row for {address}", failures)
        if row is None:
            continue
        require(bool(row.get("comment", "").strip()), f"queue row still commentless for {address}", failures)
        if not comment_only:
            require(re.search(r"\bparam_\d+\b", row.get("signature", "")) is None, f"queue row still has param_N for {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup") == r"[maintainer-local-ghidra-backup-root]\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 166660999, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def json_string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for child in value.values():
            values.extend(json_string_values(child))
        return values
    if isinstance(value, list):
        values: list[str] = []
        for child in value:
            values.extend(json_string_values(child))
        return values
    return []


def text_contains(path: Path, token: str) -> bool:
    if path.suffix.lower() == ".json":
        return any(token in value for value in json_string_values(read_json(path)))
    return token in read_text(path)


def lower_text_for_overclaim(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return "\n".join(json_string_values(read_json(path))).lower()
    return read_text(path).lower()


def check_docs_and_ledgers(failures: list[str]) -> None:
    docs = (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE)
    for path in docs:
        for token in DOC_TOKENS:
            require(text_contains(path, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = lower_text_for_overclaim(path)
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package["scripts"].get("test:ghidra-ycc-lookup-resource-head-wave728")
        == r"py -3 tools\ghidra_ycc_lookup_resource_head_wave728_probe.py --check",
        "missing package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(len(ledger) >= 1124, "ledger row count too low", failures)
    require(len(attempts) >= 20384, "attempt log row count too low", failures)
    latest_ledger = ledger[-1]
    latest_attempt = attempts[-1]
    require(latest_ledger.get("task") == "Wave728 YCC lookup resource head", "latest ledger task mismatch", failures)
    require(latest_ledger.get("status") == "completed", "latest ledger status mismatch", failures)
    require("ycc-lookup-resource-head-wave728" in latest_ledger.get("notes", ""), "latest ledger missing tag", failures)
    require(latest_attempt.get("attempt_id") == 20383, "latest attempt id mismatch", failures)
    require(latest_attempt.get("task") == "Wave728 YCC lookup resource head", "latest attempt task mismatch", failures)
    require(latest_attempt.get("readback") == "verified", "latest attempt readback mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1124, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20384, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1115, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20384, "tracking next_attempt_id mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
    args = parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs_and_ledgers(failures)

    if failures:
        print("Ghidra YCC lookup resource head Wave728 probe")
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Ghidra YCC lookup resource head Wave728 probe")
    print("Status: PASS")
    print("Targets: 5")
    print("Queue: 6098 total, 4285 commented, 1813 commentless, 1216 undefined, 90 param_N")
    print(r"Backup: [maintainer-local-ghidra-backup-root]\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
