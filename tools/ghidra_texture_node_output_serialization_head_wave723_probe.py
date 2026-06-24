#!/usr/bin/env python3
"""Validate Wave723 texture node output serialization head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave723-texture-node-output-serialization-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_node_output_serialization_head_wave723_2026-05-22.md"
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
    "texture-node-output-serialization-head-wave723",
    "wave723-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "texture-node-output-serialization",
}

TARGETS = {
    "0x005ab0ed": (
        "CDXTexture__EvalNodeOutputSizeUnits",
        "int __stdcall CDXTexture__EvalNodeOutputSizeUnits(void * node_tree)",
        ("recursively evaluates a texture/node-tree output-unit count", "kind 7 multiplies", "RET 0x4 evidence"),
        COMMON_TAGS | {"node-tree", "output-units", "recursive", "ret-0x4", "tranche-head"},
    ),
    "0x005ab14b": (
        "CTexture__SerializeNodeTreeToBitstream",
        "int __stdcall CTexture__SerializeNodeTreeToBitstream(void * chunk_builder, void * node_tree, uint output_unit_scale, uint * out_chunk_offset)",
        ("serializes a texture node tree", "CDXTexture__RegisterSerializedChunk", "RET 0x10 evidence"),
        COMMON_TAGS | {"bitstream", "node-tree", "recursive", "ret-0x10", "serialized-chunk", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave723 texture node output serialization head",
    "texture-node-output-serialization-head-wave723",
    "0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits",
    "0x005ab14b CTexture__SerializeNodeTreeToBitstream",
    "0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime texture behavior proven",
    "chunk-builder layout proven",
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
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 666,
        "pre-decompile/index.tsv": 2,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 666,
        "post-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave723 static read-back" in comment, f"missing Wave723 comment at {address}", failures)
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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=2 found=2 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 666 instruction rows",
        "pre-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 666 instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("MISSING:" not in text, f"unexpected MISSING in {relative}", failures)
        require("BAD:" not in text, f"unexpected BAD in {relative}", failures)
        require("FAIL" not in text, f"unexpected FAIL in {relative}", failures)

    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save evidence", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-final-dry.log"), "missing final dry save evidence", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1843, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 111, "param count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005ab4d0", "high-signal head address mismatch", failures)
    require(high_signal["name"] == "CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh", "high-signal head name mismatch", failures)

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
    require(commented == 4255, "commented count mismatch", failures)
    require(strict_clean == 4197, "strict clean-signature proxy mismatch", failures)
    require(raw_head["address"] == "0x0042f220", "raw commentless head address mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    by_address = {normalize_address(row["address"]): row for row in rows}
    for address in TARGETS:
        row = by_address.get(address)
        require(row is not None, f"missing queue row for {address}", failures)
        if row is None:
            continue
        require(bool(row.get("comment", "").strip()), f"queue row still commentless for {address}", failures)
        require("undefined " not in row.get("signature", ""), f"queue row still undefined for {address}", failures)
        require(re.search(r"\bparam_\d+\b", row.get("signature", "")) is None, f"queue row still has param_N for {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup["backup"] == r"G:\GhidraBackups\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified", "backup destination mismatch", failures)
    require(backup["sourceFileCount"] == 19, "backup source file count mismatch", failures)
    require(backup["backupFileCount"] == 19, "backup file count mismatch", failures)
    require(int(backup["backupBytes"]) == 166529927, "backup byte count mismatch", failures)
    require(backup["diffCount"] == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            escaped = token.replace("\\", "\\\\")
            require(token in text or escaped in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lower, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    require("test:ghidra-texture-node-output-serialization-head-wave723" in read_text(PACKAGE_JSON), "missing package script", failures)

    ledgers = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave723 texture node output serialization head" for row in ledgers), "missing Wave723 ledger row", failures)
    require(any(row.get("attempt_id") == 20378 and row.get("task") == "Wave723 texture node output serialization head" for row in attempts), "missing Wave723 attempt row", failures)

    tracking = read_json(TRACKING)
    require(tracking["next_attempt_id"] == 20379, "tracking next_attempt_id mismatch", failures)
    require("Wave723 texture node output serialization head" in tracking.get("current_focus", ""), "tracking focus mismatch", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave723 texture node output serialization head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave723 texture node output serialization head probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6098 total, 4255 commented, 1843 commentless, 1216 undefined, 111 param_N")
    print(r"Backup: G:\GhidraBackups\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
