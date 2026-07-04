#!/usr/bin/env python3
"""Validate Wave814 mesh segment-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave814-mesh-segment-tail"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mesh_segment_tail_wave814_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
SEGMENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified"
NEXT_HEAD = "0x004adf80 CMesh__ClearField08"

TARGETS = {
    "0x004aa4e0": (
        "CMesh__SumChainedField1C",
        "int __thiscall CMesh__SumChainedField1C(void * this)",
        ("this+0x08", "field +0x1c", "CRTMesh__Init"),
    ),
    "0x004aa500": (
        "CMesh__GetChainedRecordNameAndIdByIndex",
        "void __thiscall CMesh__GetChainedRecordNameAndIdByIndex(void * this, int record_index, void * out_name, int * out_record_id)",
        ("0x00662b2c", "RET 0xc", "unused_ctx"),
    ),
    "0x004aa6b0": (
        "CMesh__GetNameOrUnknown",
        "void * __thiscall CMesh__GetNameOrUnknown(void * this)",
        ("DAT_00704ad8", "0x0062f8d4", "old controller-specific"),
    ),
    "0x004aa8a0": (
        "CMesh__FindPartByNameI",
        "void * __thiscall CMesh__FindPartByNameI(void * this, char * part_name)",
        ("this+0x160", "stricmp", "RET 0x4"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "mesh-segment-tail-wave814",
    "wave814-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "raw-commentless-tail",
}

DOC_TOKENS = (
    "Wave814 mesh segment tail",
    "mesh-segment-tail-wave814",
    "0x004aa4e0 CMesh__SumChainedField1C",
    "0x004aa500 CMesh__GetChainedRecordNameAndIdByIndex",
    "0x004aa6b0 CMesh__GetNameOrUnknown",
    "0x004aa8a0 CMesh__FindPartByNameI",
    "DAT_00704ad8",
    "0x00662b2c",
    "0x0062f8d4",
    "5595/6098 = 91.75%",
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
        "pre-xrefs.tsv": 24,
        "pre-instructions.tsv": 884,
        "pre-decompile/index.tsv": 4,
        "pre-caller-metadata.tsv": 12,
        "pre-caller-decompile/index.tsv": 12,
        "pre-callsite-instructions.tsv": 504,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 24,
        "post-instructions.tsv": 884,
        "post-decompile/index.tsv": 4,
        "post-caller-metadata.tsv": 12,
        "post-caller-decompile/index.tsv": 12,
        "post-callsite-instructions.tsv": 504,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    require(read_tsv(BASE / "string-00662b2c.tsv")[0].get("cstring") == "", "empty-string sentinel mismatch", failures)
    require(read_tsv(BASE / "string-0062f8d4.tsv")[0].get("cstring") == "unknown mesh name", "unknown mesh string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            comment = row.get("comment", "")
            require("Wave814 static read-back correction" in comment, f"missing Wave814 comment {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing tags {address}: {COMMON_TAGS - actual_tags}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)

    combined_decompile = "\n".join(read_text(path) for path in (BASE / "post-decompile").glob("*.c"))
    for token in ("CMesh__SumChainedField1C", "CMesh__GetChainedRecordNameAndIdByIndex", "DAT_00704ad8", "s_unknown_mesh_name_0062f8d4", "stricmp"):
        require(token in combined_decompile, f"missing decompile token: {token}", failures)

    caller_text = "\n".join(read_text(path) for path in (BASE / "post-caller-decompile").glob("*.c"))
    for token in (
        "CMesh__GetNameOrUnknown",
        "CMesh__FindPartByNameI",
        "CMesh__SumChainedField1C",
        "CMesh__GetChainedRecordNameAndIdByIndex",
        "CDestructableSegmentsController__Init",
        "CMeshPart__CreatePolyBucket",
        "CRTMesh__Init",
    ):
        require(token in caller_text, f"missing caller decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=4 signature_updated=3 comment_only_updated=4 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=4 would_rename=0 signature_updated=3 comment_only_updated=4 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 24 rows",
        "post-instructions.log": "Wrote 884 instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-caller-metadata.log": "targets=12 found=12 missing=0",
        "post-caller-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 504 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5595",
        "queue-probe.log": "Commentless functions: 503",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave814.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave814_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 503, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5595, "quality TSV commented count mismatch", failures)
    require(strict == 5595, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004adf80", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMesh__ClearField08", "raw commentless head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171346823 or backup.get("totalBytes") == 171346823.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, MESH_DOC, MESHPART_DOC, SEGMENT_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in ("runtime mesh behavior proven", "fully reverse-engineered", "rebuild parity proven"):
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get("test:ghidra-mesh-segment-tail-wave814") == r"py -3 tools\ghidra_mesh_segment_tail_wave814_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave814 mesh segment tail" for row in read_jsonl(LEDGER)), "missing Wave814 ledger row", failures)
    require(any(row.get("task") == "Wave814 mesh segment tail" and row.get("attempt_id") == 20469 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave814 attempt row", failures)


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
        print("Wave814 mesh segment-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave814 mesh segment-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
