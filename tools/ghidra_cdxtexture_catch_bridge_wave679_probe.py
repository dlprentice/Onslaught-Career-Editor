#!/usr/bin/env python3
"""Validate Wave679 CDXTexture catch-bridge read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave679-catch-bridge"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_catch_bridge_wave679_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

BASE_TAGS = {
    "static-reaudit",
    "cdxtexture-catch-bridge-wave679",
    "wave679-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
}

TARGETS = {
    "0x00589200": (
        "Catch@00589200",
        "void * __cdecl Catch@00589200(void)",
        ("compiler catch/unwind landing pad", "0x00589212", "0x006202fc"),
        BASE_TAGS | {"signature-hardened", "compiler-artifact", "seh-catch", "catch-landing-pad", "continuation-address"},
    ),
    "0x0058920c": (
        "CDXTexture__DetectCpuSimdFlags",
        "int CDXTexture__DetectCpuSimdFlags(void)",
        ("Ghidra-split continuation", "0x02000000", "0x04000000"),
        BASE_TAGS | {"signature-preserved", "ghidra-split-continuation", "cpuid", "simd-feature-flags"},
    ),
}

DOC_TOKENS = (
    "Wave679 CDXTexture catch bridge",
    "cdxtexture-catch-bridge-wave679",
    "0x00589200 Catch@00589200",
    "0x0058920c CDXTexture__DetectCpuSimdFlags",
    "0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive",
)

OVERCLAIM_TOKENS = (
    "runtime exception behavior proven",
    "runtime dispatch policy proven",
    "feature-bit names proven",
    "msvc eh model proven",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    require(len(metadata) == len(TARGETS), f"metadata row count is {len(metadata)}", failures)
    require(len(tags) == len(TARGETS), f"tag row count is {len(tags)}", failures)
    require(len(decompile_index) == len(TARGETS), f"decompile index row count is {len(decompile_index)}", failures)
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 2, "xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 98, "instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "post-context-xrefs.tsv")) == 64, "context xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-context-instructions.tsv")) == 244, "context instruction row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave679 static read-back" in comment, f"missing Wave679 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected_signature, f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / f"{address[2:]}_{name.replace('@', '_')}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected_exact = {
        "apply-wave679-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=1 missing=0 bad=0",
        "apply-wave679-apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=1 missing=0 bad=0",
        "apply-wave679-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "post-instructions.log": "targets=2 missing=0",
        "post-xrefs.log": "Wrote 2 rows",
        "post-context-metadata.log": "targets=4 found=4 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-context-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-context-instructions.log": "targets=4 missing=0",
        "post-context-xrefs.log": "Wrote 64 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)
    require("Wrote 98 instruction rows" in read_text(BASE / "post-instructions.log"), "instruction row count mismatch", failures)
    require("Wrote 244 instruction rows" in read_text(BASE / "post-context-instructions.log"), "context instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-cdxtexture-catch-bridge-wave679" in package.get("scripts", {}), "package script missing", failures)
    require((ROOT / "tools" / "ApplyCDXTextureCatchBridgeWave679.java").is_file(), "apply script missing", failures)

    docs = (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG)
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave679 CDXTexture catch bridge" in text, f"Wave679 missing from {path.relative_to(ROOT)}", failures)
        require("cdxtexture-catch-bridge-wave679" in text, f"Wave679 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(float(backup.get("byteCount", 0))) == 164367239, "backup byteCount mismatch", failures)
    require("post_wave679_cdxtexture_catch_bridge_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2257, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 478, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x00589367", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__ReleaseIncludeNodeTreeRecursive", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave679 CDXTexture catch bridge", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave679 CDXTexture catch bridge", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20334, "attempt id mismatch", failures)
    require(len(ledger) == 1075, "ledger row count mismatch", failures)
    require(len(attempts) == 20335, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave679 CDXTexture catch bridge"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1075, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20335, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1066, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20335, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave679 CDXTexture catch bridge" in text, f"Wave679 missing from {path.name}", failures)
        require("cdxtexture-catch-bridge-wave679" in text, f"Wave679 tag missing from {path.name}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_docs(failures)
        check_state(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "FAIL"
    print("Ghidra CDXTexture catch bridge Wave679 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
