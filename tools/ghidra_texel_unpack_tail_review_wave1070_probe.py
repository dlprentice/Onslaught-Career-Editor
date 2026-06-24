#!/usr/bin/env python3
"""Validate Wave1070 texel-unpack tail read-only review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1070-texel-unpack-tail-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texel_unpack_tail_review_wave1070_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1070_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

CORE_DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

OWNER_DOC_TOKENS = {
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md": (
        "Wave1070",
        "texel-unpack-tail-review-wave1070",
        "0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4",
        "0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4",
        "0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne",
        "0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel",
        "1278/1560 = 81.92%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md": (
        "Wave1070",
        "texel-unpack-tail-review-wave1070",
        "0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor",
        "0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne",
        "0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4",
        "0x00586bb7 CFastVB__FlushPendingConvertedRows16",
        "0x00586f37 CFastVB__DecodeRowWindowToScratchPairs",
        "1278/1560 = 81.92%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md": (
        "Wave1070",
        "texel-unpack-tail-review-wave1070",
        "0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG",
        "0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ",
        "0x0058686f CTexture__UnpackTexels_CopyRaw128",
        "1278/1560 = 81.92%",
        BACKUP_PATH,
    ),
}

TARGETS = {
    "0x0058609e": ("CFastVB__TexelUnpackProfile_005ea020__ctor", "void * __thiscall CFastVB__TexelUnpackProfile_005ea020__ctor(void * this, void * format_descriptor)"),
    "0x005860ba": ("CTexture__UnpackTexels_Signed16_16_ToFloat4_RG", "void __thiscall CTexture__UnpackTexels_Signed16_16_ToFloat4_RG(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x005861b4": ("CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4", "void __thiscall CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x00586305": ("CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4", "void __thiscall CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x00586438": ("CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ", "void __thiscall CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x00586609": ("CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne", "void __thiscall CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x005866d2": ("CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne", "void __thiscall CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x0058677b": ("CDXTexture__UnpackTexels_CallbackSingleTexel", "void __thiscall CDXTexture__UnpackTexels_CallbackSingleTexel(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x0058686f": ("CTexture__UnpackTexels_CopyRaw128", "void __thiscall CTexture__UnpackTexels_CopyRaw128(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x005868d1": ("CFastVB__UnpackTexels_L16A16_ToFloat4", "void __thiscall CFastVB__UnpackTexels_L16A16_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)"),
    "0x00586bb7": ("CFastVB__FlushPendingConvertedRows16", "int __fastcall CFastVB__FlushPendingConvertedRows16(void * profile)"),
    "0x00586f37": ("CFastVB__DecodeRowWindowToScratchPairs", "int __thiscall CFastVB__DecodeRowWindowToScratchPairs(void * this, int row_index, uint column_index, uint decode_if_needed)"),
}

COMMENT_TOKENS = {
    "0x0058609e": ("Wave674", "0x00588098", "vtable 0x005ea020"),
    "0x005860ba": ("Wave674", "signed 16-16 RG", "+0x1058/+0x105c/+0x20"),
    "0x005861b4": ("Wave674", "signed 2-10-10-10", "top 2-bit lane"),
    "0x00586305": ("Wave674", "signed 16-16-16-16", "RGBA"),
    "0x00586438": ("Wave674", "normal-map", "sqrt(max(0"),
    "0x00586609": ("Wave674", "stride-2", "forces G/B/A to 1.0"),
    "0x005866d2": ("Wave674", "stride-4", "forces Z/A to 1.0"),
    "0x0058677b": ("Wave674", "single-callback", "DispatchIndirect"),
    "0x0058686f": ("Wave674", "raw 128-bit copy", "16 bytes"),
    "0x005868d1": ("Wave674", "L16A16", "luminance"),
    "0x00586bb7": ("Wave675", "dirty flag", "YUV-to-RGB"),
    "0x00586f37": ("Wave675", "row-window decoder", "scratch float4 pairs"),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened"}

EXPECTED_XREFS = {
    ("0x0058609e", "0x00588098", "UNCONDITIONAL_CALL"),
    ("0x005860ba", "0x005ea0fc", "DATA"),
    ("0x005861b4", "0x005ea10c", "DATA"),
    ("0x00586305", "0x005ea11c", "DATA"),
    ("0x00586438", "0x005ea12c", "DATA"),
    ("0x00586609", "0x005ea16c", "DATA"),
    ("0x005866d2", "0x005ea19c", "DATA"),
    ("0x0058677b", "0x005ea1ac", "DATA"),
    ("0x0058686f", "0x005ea1f8", "DATA"),
    ("0x005868d1", "0x005ea208", "DATA"),
    ("0x00586bb7", "0x00586f81", "UNCONDITIONAL_CALL"),
    ("0x00586bb7", "0x00587db8", "UNCONDITIONAL_CALL"),
    ("0x00586f37", "0x005873b3", "UNCONDITIONAL_CALL"),
    ("0x00586f37", "0x00587416", "UNCONDITIONAL_CALL"),
}

CONTEXT_TARGETS = {
    "0x00585fa3": "CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4",
    "0x0058609e": "CFastVB__TexelUnpackProfile_005ea020__ctor",
    "0x00586994": "CFastVB__InitTexelUnpackVTable_005ea118",
    "0x005869b0": "CTexture__UnpackTexels_Bits16_16_16_ToFloat4",
    "0x00586a71": "CFastVB__TexelUnpackProfileRegistry_005ea138__ctor",
    "0x00586ec7": "CFastVB__InitTexelUnpackVTable_005ea198",
    "0x00587dd6": "CFastVB__TexelUnpackProfileRegistry_005ea254__ctor",
}

DOC_TOKENS = (
    "Wave1070",
    "texel-unpack-tail-review-wave1070",
    "0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor",
    "0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG",
    "0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4",
    "0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4",
    "0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ",
    "0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne",
    "0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne",
    "0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel",
    "0x0058686f CTexture__UnpackTexels_CopyRaw128",
    "0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4",
    "0x00586bb7 CFastVB__FlushPendingConvertedRows16",
    "0x00586f37 CFastVB__DecodeRowWindowToScratchPairs",
    "812/1408 = 57.67%",
    "1278/1560 = 81.92%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime texture output behavior proven",
    "runtime codec behavior proven",
    "exact source identity proven",
    "rebuild parity proven",
)


def norm(address: str) -> str:
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 12,
        "primary-tags.tsv": 12,
        "primary-xrefs.tsv": 14,
        "primary-instructions.tsv": 1100,
        "primary-decompile/index.tsv": 12,
        "context-metadata.tsv": 7,
        "context-xrefs.tsv": 10,
        "context-instructions.tsv": 254,
        "context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    xrefs = {
        (norm(row["target_addr"]), norm(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "primary-xrefs.tsv")
    }

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"tags missing at {address}: {COMMON_TAGS - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref tuple: {expected}", failures)

    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=12 found=12 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "primary-xrefs.log": "Wrote 14 rows",
        "primary-instructions.log": "Wrote 1100 function-body instruction rows",
        "primary-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-xrefs.log": "Wrote 10 rows",
        "context-instructions.log": "Wrote 254 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(float(backup.get("totalBytes")) == 174721927.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    for path in CORE_DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-texel-unpack-tail-review-wave1070")
        == r"py -3 tools\ghidra_texel_unpack_tail_review_wave1070_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1070-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1070 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1070 texel unpack tail review" for row in ledger), "missing ledger row", failures)
    require(any(row.get("task") == "Wave1070 texel unpack tail review" and row.get("attempt_id") == 20652 for row in attempts), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1070 texel-unpack tail review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1070 texel-unpack tail review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
