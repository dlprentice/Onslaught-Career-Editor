#!/usr/bin/env python3
"""Validate Wave815 meshpart-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave815-meshpart-tail"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_meshpart_tail_wave815_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-144421_post_wave815_meshpart_tail_verified"
NEXT_HEAD = "0x004b0cd0 CMesh__SelectModeSpecificPtr"

TARGETS = {
    "0x004adf80": (
        "CMesh__ClearField08",
        "void __thiscall CMesh__ClearField08(void * this)",
        ("field +0x08", "0x24-byte", "CMesh__InitStatic", "CMesh__ReleaseEmbeddedResources"),
    ),
    "0x004ae640": (
        "CMeshPart__FreeOwnedResourcePointers",
        "void __thiscall CMeshPart__FreeOwnedResourcePointers(void * this)",
        ("0x004a51f0 CMeshPart__FreeResources", "CMeshPart__CreatePolyBucket", "+0x104", "+0x138"),
    ),
    "0x004aede0": (
        "CMeshPart__LoadOldStyle_VersionA",
        "int __thiscall CMeshPart__LoadOldStyle_VersionA(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)",
        ("RET 0x14", "0x60-byte", "material_index_limit", "CMeshPart__RebuildPerVertexNormalsAndTangents"),
    ),
    "0x004af110": (
        "CMeshPart__LoadOldStyle_VersionB_WithExtraBlock",
        "int __thiscall CMeshPart__LoadOldStyle_VersionB_WithExtraBlock(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)",
        ("RET 0x14", "part offset +0xb8", "extra 4-byte block", "CMeshPart__RebuildPerVertexNormalsAndTangents"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "meshpart-tail-wave815",
    "wave815-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "raw-commentless-tail",
}

XREFS = {
    ("0x004adf80", "0x004a525e", "UNCONDITIONAL_CALL"),
    ("0x004adf80", "0x004a5d66", "DATA"),
    ("0x004adf80", "0x004a89ca", "DATA"),
    ("0x004adf80", "0x004aaef5", "DATA"),
    ("0x004ae640", "0x004a51f0", "UNCONDITIONAL_JUMP"),
    ("0x004ae640", "0x004ae40e", "UNCONDITIONAL_CALL"),
    ("0x004aede0", "0x004a8f05", "UNCONDITIONAL_CALL"),
    ("0x004af110", "0x004a8f49", "UNCONDITIONAL_CALL"),
}

DOC_TOKENS = (
    "Wave815 meshpart tail",
    "meshpart-tail-wave815",
    "0x004adf80 CMesh__ClearField08",
    "0x004ae640 CMeshPart__FreeOwnedResourcePointers",
    "0x004aede0 CMeshPart__LoadOldStyle_VersionA",
    "0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock",
    "RET 0x14",
    "0x004a8f05",
    "0x004a8f49",
    "0x004af462",
    "5599/6098 = 91.82%",
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
        "pre-instructions.tsv": 420,
        "pre-decompile/index.tsv": 4,
        "pre-caller-metadata.tsv": 5,
        "pre-caller-decompile/index.tsv": 5,
        "pre-callsite-instructions.tsv": 344,
        "pre-epilogue-instructions.tsv": 161,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 420,
        "post-decompile/index.tsv": 4,
        "post-caller-metadata.tsv": 5,
        "post-caller-decompile/index.tsv": 5,
        "post-callsite-instructions.tsv": 344,
        "post-epilogue-instructions.tsv": 161,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            comment = row.get("comment", "")
            require("Wave815 static read-back" in comment, f"missing Wave815 comment {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing tags {address}: {COMMON_TAGS - actual_tags}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)

    require(XREFS.issubset(xrefs), f"missing xrefs: {XREFS - xrefs}", failures)

    combined_decompile = "\n".join(read_text(path) for path in (BASE / "post-decompile").glob("*.c"))
    for token in (
        "CMesh__ClearField08",
        "CMeshPart__FreeOwnedResourcePointers",
        "CMeshPart__LoadOldStyle_VersionA",
        "CMeshPart__LoadOldStyle_VersionB_WithExtraBlock",
        "CMeshPart__RebuildPerVertexNormalsAndTangents",
        "material_index_limit",
    ):
        require(token in combined_decompile, f"missing decompile token: {token}", failures)

    callsite = read_text(BASE / "post-callsite-instructions.tsv")
    for token in ("0x004a8f05", "0x004a8f49", "PUSH\t0x0", "MOV\tECX, ESI", "CALL\t0x004af110"):
        require(token in callsite, f"missing callsite token: {token}", failures)
    epilogue = read_text(BASE / "post-epilogue-instructions.tsv")
    for token in ("0x004af462", "RET\t0x14", "CMeshPart__LoadOldStyle_VersionB_WithExtraBlock"):
        require(token in epilogue, f"missing epilogue token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 420 instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-caller-metadata.log": "targets=5 found=5 missing=0",
        "post-caller-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 344 instruction rows",
        "post-epilogue-instructions.log": "Wrote 161 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5599",
        "queue-probe.log": "Commentless functions: 499",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave815.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave815_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 499, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5599, "quality TSV commented count mismatch", failures)
    require(strict == 5599, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004b0cd0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMesh__SelectModeSpecificPtr", "raw commentless head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171346823 or backup.get("totalBytes") == 171346823.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    paths = (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        MESH_DOC,
        MESHPART_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in paths:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in ("runtime mesh loading proven", "fully reverse-engineered", "rebuild parity proven"):
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get("test:ghidra-meshpart-tail-wave815") == r"py -3 tools\ghidra_meshpart_tail_wave815_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave815 meshpart tail" for row in read_jsonl(LEDGER)), "missing Wave815 ledger row", failures)
    require(any(row.get("task") == "Wave815 meshpart tail" and row.get("attempt_id") == 20470 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave815 attempt row", failures)


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
        print("Wave815 meshpart-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave815 meshpart-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
