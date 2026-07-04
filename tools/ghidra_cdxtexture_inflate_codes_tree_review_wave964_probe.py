#!/usr/bin/env python3
"""Validate Wave964 CDXTexture inflate codes/tree review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave964-cdxtexture-inflate-codes-tree-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_inflate_codes_tree_review_wave964_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-141856_post_wave964_cdxtexture_inflate_codes_tree_review_verified"

EXPECTED_METADATA = {
    "0x0059c8c1": ("CDXTexture__InflateStream_ProcessZlibState", "int __stdcall CDXTexture__InflateStream_ProcessZlibState(void * inflate_stream, int flush_mode)"),
    "0x005b1e16": ("CDXTexture__InflateBuildFixedHuffmanTables", "void * __stdcall CDXTexture__InflateBuildFixedHuffmanTables(void * inflate_stream, void * state_callback, uint window_size_bytes)"),
    "0x005b1e94": ("CDXTexture__InflateProcessBlockHeader", "int __stdcall CDXTexture__InflateProcessBlockHeader(void * inflate_state, void * inflate_stream, int status_code)"),
    "0x005bcfa0": ("CDXTexture__InflateCodesState_Create", "void * __stdcall CDXTexture__InflateCodesState_Create(int literal_bits, int distance_bits, void * literal_table, void * distance_table, void * inflate_stream)"),
    "0x005bcfd3": ("CDXTexture__InflateCodesState_Process", "int __stdcall CDXTexture__InflateCodesState_Process(void * inflate_state, void * inflate_stream, int status_code)"),
    "0x005bd52a": ("CDXTexture__InvokeReleaseCallback", "void __stdcall CDXTexture__InvokeReleaseCallback(void * release_payload, void * inflate_stream)"),
    "0x005bd53b": ("CDXTexture__BuildInflateHuffmanTable", "int CDXTexture__BuildInflateHuffmanTable(void)"),
    "0x005bd8ba": ("CDXTexture__InflateDynamicTree_BuildBitLengthTree", "int __stdcall CDXTexture__InflateDynamicTree_BuildBitLengthTree(int code_length_count, void * bit_length_count_out, void * tree_workspace, void * bit_length_order_table, void * inflate_stream)"),
    "0x005bd933": ("CDXTexture__InflateDynamicTree_BuildLitDistTrees", "int __stdcall CDXTexture__InflateDynamicTree_BuildLitDistTrees(int literal_length_count, int distance_count, void * code_lengths, void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * tree_workspace, void * inflate_stream)"),
    "0x005bda2d": ("CDXTexture__InflateFixedTrees_InitDescriptors", "int __stdcall CDXTexture__InflateFixedTrees_InitDescriptors(void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * inflate_stream)"),
    "0x005bda5e": ("CDXTexture__InflateOutputWindowFlush", "int __stdcall CDXTexture__InflateOutputWindowFlush(void * inflate_state, void * inflate_stream, int status_code)"),
    "0x005be360": ("CDXTexture__InflateFast_DecodeBlockStream", "int __stdcall CDXTexture__InflateFast_DecodeBlockStream(int literal_bits, int distance_bits, void * literal_table, void * distance_table, void * inflate_state, void * inflate_stream)"),
}

WAVE964_TAGS = (
    "cdxtexture-inflate-codes-tree-review-wave964",
    "wave964-readback-verified",
    "extraout-eax-gap-resolved",
    "inflate-stream",
    "state-machine",
    "ret-0x8",
)

BODY_EVIDENCE = (
    ("0x0059c8c1", "0x0059c9ce", "CALL", "0x005b1e94"),
    ("0x005b1e94", "0x005b1f00", "CALL", "0x005bda5e"),
    ("0x005b1e94", "0x005b20a6", "CALL", "0x005bda5e"),
    ("0x005b1e94", "0x005b23f3", "CALL", "0x005bd933"),
    ("0x005b1e94", "0x005b2455", "CALL", "0x005bcfd3"),
    ("0x005b1e94", "0x005b245a", "CMP", "EAX, 0x1"),
    ("0x005b1e94", "0x005b2574", "CALL", "0x005bda5e"),
    ("0x005bcfd3", "0x005bd067", "CALL", "0x005be360"),
    ("0x005bd8ba", "0x005bd8f6", "CALL", "0x005bd53b"),
    ("0x005bd933", "0x005bd982", "CALL", "0x005bd53b"),
    ("0x005bd933", "0x005bd9b9", "CALL", "0x005bd53b"),
)

CORE_TOKENS = (
    "Wave964",
    "cdxtexture-inflate-codes-tree-review-wave964",
    "0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState",
    "0x0059c9ce CALL 0x005b1e94",
    "0x005b1e94 CDXTexture__InflateProcessBlockHeader",
    "0x005bcfd3 CDXTexture__InflateCodesState_Process",
    "0x005bd53b CDXTexture__BuildInflateHuffmanTable",
    "0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees",
    "0x005be360 CDXTexture__InflateFast_DecodeBlockStream",
    "extraout-eax-gap-resolved",
    "323/1408 = 22.94%",
    "6152/6152 = 100.00%",
    BACKUP_PATH,
    "comment/tag mutation only",
)

OVERCLAIMS = (
    "runtime inflate behavior proven",
    "runtime decode behavior proven",
    "z_stream layout proven",
    "inflate-state layout proven",
    "callback abi proven",
    "zlib source identity proven",
    "patching proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_counts(failures: list[str]) -> None:
    expected = {
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 1740,
        "pre-body-instructions.tsv": 2271,
        "pre-decompile/index.tsv": 12,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 23,
        "post-instructions.tsv": 1740,
        "post-body-instructions.tsv": 2271,
        "post-decompile/index.tsv": 12,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    body = read_tsv(BASE / "post-body-instructions.tsv")

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)

    corrected = metadata.get("0x0059c8c1", {})
    comment = corrected.get("comment", "")
    for token in (
        "Wave964 re-audit correction",
        "Wave731 block-header signature/read-back",
        "0x0059c9ce",
        "CDXTexture__InflateProcessBlockHeader",
        "no longer contains an extraout_ variable at that call",
        "runtime inflate behavior",
        "rebuild parity remain unproven",
    ):
        require(token in comment, f"missing corrected comment token: {token}", failures)

    tag_text = tags.get("0x0059c8c1", {}).get("tags", "")
    for token in WAVE964_TAGS:
        require(token in tag_text, f"missing Wave964 tag: {token}", failures)
    actual_tags = set(filter(None, tag_text.split(";")))
    require("extraout-eax-gap" not in actual_tags, "stale extraout-eax-gap tag still present", failures)

    decompile = read_text(BASE / "post-decompile" / "0059c8c1_CDXTexture__InflateStream_ProcessZlibState.c")
    require("iVar4 = CDXTexture__InflateProcessBlockHeader" in decompile, "missing decompile status assignment", failures)

    for target, instr_addr, mnemonic, operand_token in BODY_EVIDENCE:
        require(
            any(
                norm(row.get("target_addr", "")) == target
                and norm(row.get("instruction_addr", "")) == instr_addr
                and row.get("mnemonic", "") == mnemonic
                and operand_token in row.get("operands", "")
                for row in body
            ),
            f"missing body-instruction evidence: {target} {instr_addr} {mnemonic} {operand_token}",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 23 rows",
        "pre-instructions.log": "Wrote 1740 instruction rows",
        "pre-body-instructions.log": "Wrote 2271 function-body instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "Wrote 1740 instruction rows",
        "post-body-instructions.log": "Wrote 2271 function-body instruction rows",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative.startswith("apply"):
            for bad in ("LockException", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "failed=1", "bad=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save success", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6152, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    require(len(rows) == 6152, "quality TSV row count mismatch", failures)
    require(commented == 6152, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6152, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cdxtexture-inflate-codes-tree-review-wave964")
        == r"py -3 tools\ghidra_cdxtexture_inflate_codes_tree_review_wave964_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave964 CDXTexture inflate codes/tree probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave964 CDXTexture inflate codes/tree probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
