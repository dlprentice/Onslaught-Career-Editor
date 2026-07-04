#!/usr/bin/env python3
"""Validate Wave813 CMesh usage-clearout read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave813-cmesh-usage-clearout"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cmesh_usage_clearout_wave813_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

TARGETS = {
    "0x004a52b0": "CMesh__ClearAllUsageMarkers",
    "0x004a52d0": "CMesh__ClearOut",
    "0x004a53f0": "CMesh__StatusLoadingMeshResources",
    "0x004a5430": "CMesh__FreeUnusedAndReportLeaks",
}
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-134919_post_wave813_cmesh_usage_clearout_verified"
NEXT_HEAD = "0x004aa4e0 CRTMesh__SumSubtreeField1C"

COMMON_TAGS = {
    "static-reaudit",
    "cmesh-usage-clearout-wave813",
    "wave813-readback-verified",
    "retail-binary-evidence",
    "signature-verified",
    "comment-hardened",
    "raw-commentless-tail",
    "mesh-resource-lifetime",
    "mesh-usage-markers",
}

DOC_TOKENS = (
    "Wave813 CMesh usage clearout",
    "cmesh-usage-clearout-wave813",
    "0x004a52b0 CMesh__ClearAllUsageMarkers",
    "0x004a52d0 CMesh__ClearOut",
    "0x004a53f0 CMesh__StatusLoadingMeshResources",
    "0x004a5430 CMesh__FreeUnusedAndReportLeaks",
    "DAT_00704ad8",
    "0x0062f938",
    "0x0062f9a0",
    "0x0046ca13",
    "5591/6098 = 91.69%",
    NEXT_HEAD,
    BACKUP_PATH,
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 8,
        "pre-instructions.tsv": 484,
        "pre-decompile/index.tsv": 4,
        "pre-caller-metadata.tsv": 4,
        "pre-caller-decompile/index.tsv": 4,
        "pre-callsite-instructions.tsv": 147,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 484,
        "post-decompile/index.tsv": 4,
        "post-caller-metadata.tsv": 4,
        "post-caller-decompile/index.tsv": 4,
        "post-callsite-instructions.tsv": 147,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row["name"] == name, f"name mismatch {address}", failures)
            require(row["signature"] == f"void __cdecl {name}(void)", f"signature mismatch {address}", failures)
            require("Wave813 static read-back hardening" in row.get("comment", ""), f"missing Wave813 comment {address}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing tags {address}: {COMMON_TAGS - actual_tags}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == f"void __cdecl {name}(void)", f"decompile signature mismatch {address}", failures)

    combined_decompile = "\n".join(read_text(path) for path in (BASE / "post-decompile").glob("*.c"))
    for token in ("DAT_00704ad8", "DAT_00704adc", "DAT_00704ae0", "s_Loading_mesh_resources_0062f9a0", "s_Mesh___s__leaked___refcount__d_0062f938"):
        require(token in combined_decompile, f"missing decompile token: {token}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_from = {normalize_address(row["from_addr"]) for row in xrefs}
    for addr in ("0x004f0166", "0x004f01bf", "0x004f01c4", "0x00468809", "0x0046cdba", "0x0046928d", "0x0046ca13"):
        require(addr in xref_from, f"missing xref/callsite from {addr}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=4 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=4 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 484 instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-caller-metadata.log": "targets=4 found=4 missing=0",
        "post-caller-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 147 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5591",
        "queue-probe.log": "Commentless functions: 507",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave813.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave813_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 507, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5591, "quality TSV commented count mismatch", failures)
    require(strict == 5591, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004aa4e0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CRTMesh__SumSubtreeField1C", "raw commentless head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171346823 or backup.get("totalBytes") == 171346823.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, MESH_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in ("runtime shutdown behavior proven", "fully reverse-engineered", "rebuild parity proven"):
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get("test:ghidra-cmesh-usage-clearout-wave813") == r"py -3 tools\ghidra_cmesh_usage_clearout_wave813_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave813 CMesh usage clearout" for row in read_jsonl(LEDGER)), "missing Wave813 ledger row", failures)
    require(any(row.get("task") == "Wave813 CMesh usage clearout" and row.get("attempt_id") == 20468 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave813 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave813 CMesh usage-clearout probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave813 CMesh usage-clearout probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
