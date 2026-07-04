#!/usr/bin/env python3
"""Validate Wave738 CDXTexture DCT/inflate-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave738-cdxtexture-dct-inflate-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_dct_inflate_tail_wave738_2026-05-22.md"
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

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-131329_post_wave738_cdxtexture_dct_inflate_tail_verified"

SIGNATURE_TAGS = {
    "static-reaudit",
    "cdxtexture-dct-inflate-tail-wave738",
    "wave738-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cdxtexture-dct-inflate-tail",
}

TARGETS = {
    "0x005bb9b0": (
        "CDXTexture__InverseDct8x8_DequantAndStore_Scalar",
        "void __stdcall CDXTexture__InverseDct8x8_DequantAndStore_Scalar(void * coefficient_block_rows, void * quant_table_rows, void * idct_workspace_rows, int * row_offset_table, int output_base, void * clamp_table)",
        ("Wave738 static read-back", "RET 0x18", "no-function wrapper", "row_offset_table"),
        SIGNATURE_TAGS | {"tranche-head", "dct-scalar", "ret-0x18", "no-function-wrapper"},
    ),
    "0x005bbe70": (
        "CDXTexture__InverseDct8x8_DequantAndStore_Mmx",
        "int __stdcall CDXTexture__InverseDct8x8_DequantAndStore_Mmx(void * coefficient_block_rows, void * quant_table_rows, void * idct_workspace_rows, int * row_offset_table, int output_base, void * clamp_table)",
        ("Wave738 static read-back", "RET 0x18", "constant zero", "clamp_table"),
        SIGNATURE_TAGS | {"dct-mmx", "ret-0x18", "no-function-wrapper"},
    ),
    "0x005bcfa0": (
        "CDXTexture__InflateCodesState_Create",
        "void * __stdcall CDXTexture__InflateCodesState_Create(int literal_bits, int distance_bits, void * literal_table, void * distance_table, void * inflate_stream)",
        ("Wave738 static read-back", "RET 0x14", "0x1c-byte state", "returns the allocated state pointer"),
        SIGNATURE_TAGS | {"inflate-code-state", "ret-0x14", "allocator-callback"},
    ),
    "0x005bcfd3": (
        "CDXTexture__InflateCodesState_Process",
        "int __stdcall CDXTexture__InflateCodesState_Process(void * inflate_state, void * inflate_stream, int status_code)",
        ("Wave738 static read-back", "RET 0xc", "stale void return", "invalid literal/length"),
        SIGNATURE_TAGS | {"inflate-code-state", "ret-0xc", "status-return", "invalid-code-errors"},
    ),
    "0x005bd52a": (
        "CDXTexture__InvokeReleaseCallback",
        "void __stdcall CDXTexture__InvokeReleaseCallback(void * release_payload, void * inflate_stream)",
        ("Wave738 static read-back", "RET 0x8", "release an inflate code-state payload"),
        SIGNATURE_TAGS | {"inflate-callback", "ret-0x8", "release-callback"},
    ),
    "0x005bd8ba": (
        "CDXTexture__InflateDynamicTree_BuildBitLengthTree",
        "int __stdcall CDXTexture__InflateDynamicTree_BuildBitLengthTree(int code_length_count, void * bit_length_count_out, void * tree_workspace, void * bit_length_order_table, void * inflate_stream)",
        ("Wave738 static read-back", "RET 0x14", "oversubscribed/incomplete dynamic bit-length tree"),
        SIGNATURE_TAGS | {"inflate-dynamic-tree", "ret-0x14", "huffman-table", "bit-length-tree"},
    ),
    "0x005bd933": (
        "CDXTexture__InflateDynamicTree_BuildLitDistTrees",
        "int __stdcall CDXTexture__InflateDynamicTree_BuildLitDistTrees(int literal_length_count, int distance_count, void * code_lengths, void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * tree_workspace, void * inflate_stream)",
        ("Wave738 static read-back", "RET 0x24", "stale five-parameter signature", "empty tree"),
        SIGNATURE_TAGS | {"inflate-dynamic-tree", "ret-0x24", "huffman-table", "litdist-tree"},
    ),
    "0x005bda2d": (
        "CDXTexture__InflateFixedTrees_InitDescriptors",
        "int __stdcall CDXTexture__InflateFixedTrees_InitDescriptors(void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * inflate_stream)",
        ("Wave738 static read-back", "RET 0x14", "fixed literal/distance bit counts"),
        SIGNATURE_TAGS | {"inflate-fixed-tree", "ret-0x14", "descriptor-init"},
    ),
    "0x005bda5e": (
        "CDXTexture__InflateOutputWindowFlush",
        "int __stdcall CDXTexture__InflateOutputWindowFlush(void * inflate_state, void * inflate_stream, int status_code)",
        ("Wave738 static read-back", "RET 0xc", "output-window flush", "returns the status code"),
        SIGNATURE_TAGS | {"inflate-output-window", "ret-0xc", "status-return", "output-callback"},
    ),
    "0x005be360": (
        "CDXTexture__InflateFast_DecodeBlockStream",
        "int __stdcall CDXTexture__InflateFast_DecodeBlockStream(int literal_bits, int distance_bits, void * literal_table, void * distance_table, void * inflate_state, void * inflate_stream)",
        ("Wave738 static read-back", "RET 0x18", "invalid distance", "invalid literal/length"),
        SIGNATURE_TAGS | {"tranche-tail", "inflate-fast-decode", "ret-0x18", "status-return", "invalid-code-errors"},
    ),
}

DOC_TOKENS = (
    "Wave738 CDXTexture DCT/inflate tail",
    "cdxtexture-dct-inflate-tail-wave738",
    "0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar",
    "0x005bbe70 CDXTexture__InverseDct8x8_DequantAndStore_Mmx",
    "0x005bcfa0 CDXTexture__InflateCodesState_Create",
    "0x005bcfd3 CDXTexture__InflateCodesState_Process",
    "0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees",
    "0x005be360 CDXTexture__InflateFast_DecodeBlockStream",
    "0x005be622 Direct3DCreate9",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime decompression behavior proven",
    "runtime image behavior proven",
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 18,
        "pre-instructions.tsv": 2810,
        "pre-decompile/index.tsv": 10,
        "pre-callers-decompile/index.tsv": 3,
        "pre-xref-site-instructions.tsv": 1602,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 18,
        "post-instructions.tsv": 2810,
        "post-decompile/index.tsv": 10,
        "post-callers-decompile/index.tsv": 3,
        "post-xref-site-instructions.tsv": 1602,
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "pre-xrefs.log": "Wrote 18 rows",
        "pre-instructions.log": "Wrote 2810 instruction rows",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "pre-callers-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "pre-xref-site-instructions.log": "Wrote 1602 instruction rows",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 18 rows",
        "post-instructions.log": "Wrote 2810 instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-callers-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-xref-site-instructions.log": "Wrote 1602 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=4349",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1749, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1216, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 36, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005be622", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Direct3DCreate9", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4349, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4291, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 166988679, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        TRACKING,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for doc in docs:
        text = read_text(doc)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {doc.relative_to(ROOT)}: {token}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token.lower() not in text.lower(), f"overclaim token in {doc.relative_to(ROOT)}: {token}", failures)

    package_text = read_text(PACKAGE_JSON)
    require(
        "test:ghidra-cdxtexture-dct-inflate-tail-wave738" in package_text,
        "missing npm probe script",
        failures,
    )

    ledger_entries = read_jsonl(LEDGER)
    attempt_entries = read_jsonl(ATTEMPT_LOG)
    require(any(e.get("task") == "Wave738 CDXTexture DCT/inflate tail" for e in ledger_entries), "ledger missing Wave738", failures)
    require(any(e.get("task") == "Wave738 CDXTexture DCT/inflate tail" for e in attempt_entries), "attempt log missing Wave738", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero on validation failure.")
    args = parser.parse_args()

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs):
        try:
            check(failures)
        except Exception as exc:  # noqa: BLE001 - probe should report all available context.
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave738 CDXTexture DCT/inflate tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave738 CDXTexture DCT/inflate tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
