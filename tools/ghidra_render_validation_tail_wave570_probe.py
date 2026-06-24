#!/usr/bin/env python3
"""Validate Wave570 render-validation Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave570-render-validation-tail-00527cc0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_render_validation_tail_wave570_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
VBUFTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
DXLANDSCAPE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x00527cc0": {
        "raw": "00527cc0",
        "name": "CWaterRenderSystem__ValidateVBufferAndMarkReady",
        "signature": "bool __thiscall CWaterRenderSystem__ValidateVBufferAndMarkReady(void * this, int expected_valid_so_far)",
        "tags": {"static-reaudit", "render-validation-tail-wave570", "retail-binary-evidence", "render-validation", "vbuf-valid", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("expected_valid_so_far", "RET 0x4 confirms", "RM: First time attempt", "Xrefs span CDXBattleLine"),
        "decompile_tokens": ("/* signature: bool __thiscall CWaterRenderSystem__ValidateVBufferAndMarkReady", "this + 0xc", "expected_valid_so_far"),
    },
    "0x00527d20": {
        "raw": "00527d20",
        "name": "CDXLandscape__ValidateDeviceAndUpdateValidSoFar",
        "signature": "bool __thiscall CDXLandscape__ValidateDeviceAndUpdateValidSoFar(void * this)",
        "tags": {"static-reaudit", "render-validation-tail-wave570", "retail-binary-evidence", "render-validation", "device-call", "valid-so-far", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("Plain RET at 0x00527d63/0x00527d98", "CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0)", "RM: Failed ValidSoFar", "decrements this+0x0c"),
        "decompile_tokens": ("CDXLandscape__ValidateDeviceAndUpdateValidSoFar(void *this)", "CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0)", "this + 0x10"),
    },
    "0x00527da0": {
        "raw": "00527da0",
        "name": "CVBufTexture__MarkAccepted",
        "signature": "void __thiscall CVBufTexture__MarkAccepted(void * this)",
        "tags": {"static-reaudit", "render-validation-tail-wave570", "retail-binary-evidence", "render-validation", "acceptance-state", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("Plain RET at 0x00527dcc", "RM: Accepting", "sets this+0x10 to 1", "CVBufTexture owner label is retained only"),
        "decompile_tokens": ("CVBufTexture__MarkAccepted(void *this)", "RM__Accepting", "this + 0x10"),
    },
    "0x00527dd0": {
        "raw": "00527dd0",
        "name": "CDXEngine__GetRenderQueueSortKeyAt0C",
        "signature": "int __thiscall CDXEngine__GetRenderQueueSortKeyAt0C(void * this)",
        "tags": {"static-reaudit", "render-validation-tail-wave570", "retail-binary-evidence", "render-validation", "field-reader", "render-queue", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("MOV EAX,[ECX+0xc]; RET", "CRenderQueue__RenderAll", "sort/key reader", "runtime render-order behavior"),
        "decompile_tokens": ("CDXEngine__GetRenderQueueSortKeyAt0C(void *this)", "this + 0xc"),
    },
    "0x00527e00": {
        "raw": "00527e00",
        "name": "CWaterRenderSystem__CheckVBufValidAndHandleFailure",
        "signature": "bool __thiscall CWaterRenderSystem__CheckVBufValidAndHandleFailure(void * this)",
        "tags": {"static-reaudit", "render-validation-tail-wave570", "retail-binary-evidence", "render-validation", "failure-gate", "vbuf-valid", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("DAT_00854dd8", "RM: Failed CheckVBufValid", "decrements this+0x0c", "returns true"),
        "decompile_tokens": ("CWaterRenderSystem__CheckVBufValidAndHandleFailure(void *this)", "DAT_00854dd8", "this + 0x10"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def require_doc_tokens(path: Path, tokens: tuple[str, ...], failures: list[str]) -> None:
    try:
        text = read_text(path)
    except FileNotFoundError:
        failures.append(f"missing doc: {path}")
        return
    require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)


def run_check() -> list[str]:
    failures: list[str] = []

    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 5, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_verify_dry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    expected_counts = {
        "post_metadata.tsv": 5,
        "post_tags.tsv": 5,
        "post_decompile/index.tsv": 5,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")

    overclaim_tokens = ("runtime behavior proven", "runtime D3D behavior proven", "source identity proven", "rebuild parity proven", "fully RE'ed", "fully REed")
    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")
            for forbidden in ("source-parity", "runtime-proven", "rebuild-parity"):
                if forbidden in present:
                    failures.append(f"{address} unexpectedly has {forbidden} tag")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile index")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        else:
            decomp_file = next((BASE / "post_decompile").glob(f"{spec['raw']}_*.c"), None)
            if decomp_file is None:
                failures.append(f"{address} missing decompile file")
            else:
                require_tokens(f"{address} decompile", read_text(decomp_file), spec["decompile_tokens"], failures)

    require_tokens(
        "xrefs",
        xrefs,
        (
            "00527cc0\tCWaterRenderSystem__ValidateVBufferAndMarkReady\t0053ac7b\t0053abe0\tCDXBattleLine__Render\tUNCONDITIONAL_CALL",
            "00527d20\tCDXLandscape__ValidateDeviceAndUpdateValidSoFar\t00545a3b\t00545590\tCDXLandscape__RenderTerrain\tUNCONDITIONAL_CALL",
            "00527da0\tCVBufTexture__MarkAccepted\t0055d278\t0055b6c0\tCWaterRenderSystem__RenderMainPass\tUNCONDITIONAL_CALL",
            "00527dd0\tCDXEngine__GetRenderQueueSortKeyAt0C\t00552d35\t005528b0\tCRenderQueue__RenderAll\tUNCONDITIONAL_CALL",
            "00527e00\tCWaterRenderSystem__CheckVBufValidAndHandleFailure\t0055c39f\t0055b6c0\tCWaterRenderSystem__RenderMainPass\tUNCONDITIONAL_CALL",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x00527cc0\t0x00527cc0\tAFTER\t5\t0x00527ccd\t0x00527cc0\tCWaterRenderSystem__ValidateVBufferAndMarkReady\tRET\t0x4",
            "0x00527cc0\t0x00527cc0\tAFTER\t17\t0x00527cf0\t0x00527cc0\tCWaterRenderSystem__ValidateVBufferAndMarkReady\tRET\t0x4",
            "0x00527d20\t0x00527d20\tAFTER\t25\t0x00527d63\t0x00527d20\tCDXLandscape__ValidateDeviceAndUpdateValidSoFar\tRET",
            "0x00527d20\t0x00527d20\tAFTER\t45\t0x00527d98\t0x00527d20\tCDXLandscape__ValidateDeviceAndUpdateValidSoFar\tRET",
            "0x00527da0\t0x00527da0\tAFTER\t15\t0x00527dcc\t0x00527da0\tCVBufTexture__MarkAccepted\tRET",
            "0x00527dd0\t0x00527dd0\tTARGET\t0\t0x00527dd0\t0x00527dd0\tCDXEngine__GetRenderQueueSortKeyAt0C\tMOV\tEAX, dword ptr [ECX + 0xc]",
            "0x00527e00\t0x00527e00\tAFTER\t5\t0x00527e0a\t0x00527e00\tCWaterRenderSystem__CheckVBufValidAndHandleFailure\tMOV\tAL, [0x00854dd8]",
            "0x00527e00\t0x00527e00\tAFTER\t23\t0x00527e3e\t0x00527e00\tCWaterRenderSystem__CheckVBufValidAndHandleFailure\tDEC\tEAX",
        ),
        failures,
    )

    require_doc_tokens(PUBLIC_NOTE, ("Wave570", "render validation", "No runtime D3D behavior was claimed", "Post-Wave570"), failures)
    require_doc_tokens(FUNCTION_INDEX, ("Wave570 render-validation", "0x00527cc0", "0x00527e00"), failures)
    require_doc_tokens(VBUFTEXTURE_INDEX, ("Wave570", "CVBufTexture__MarkAccepted", "render validation record"), failures)
    require_doc_tokens(DXLANDSCAPE_INDEX, ("Wave570", "ValidateDeviceAndUpdateValidSoFar", "Static retail evidence only"), failures)
    require_doc_tokens(GHIDRA_REFERENCE, ("Wave570 render-validation", "0x00527cc0", "0x00527e00"), failures)
    require_doc_tokens(CAMPAIGN, ("Wave570", "render-validation", "comment-backed proxy"), failures)
    require_doc_tokens(BACKLOG, ("Wave570", "CWaterRenderSystem__ValidateVBufferAndMarkReady", "queued next"), failures)

    if not QUEUE_JSON.is_file():
        failures.append("missing current queue JSON")
    else:
        data = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
        if data.get("status") != "PASS":
            failures.append(f"queue status is {data.get('status')}")
        quality = data.get("qualitySignals", {})
        for key in ("commentlessFunctionCount", "undefinedSignatureCount", "paramSignatureCount"):
            if quality.get(key) is None:
                failures.append(f"queue JSON missing qualitySignals.{key}")

    if not LEDGER.is_file():
        failures.append("missing mutation ledger")
    else:
        ledger_text = LEDGER.read_text(encoding="utf-8")
        require_tokens("ledger", ledger_text, ("wave570", "render-validation-tail-wave570", "0x00527cc0", "0x00527e00"), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate Wave570 artifacts")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()
    failures = run_check()
    if args.json:
        print(json.dumps({"ok": not failures, "failures": failures}, indent=2))
    else:
        if failures:
            print("FAIL")
            for failure in failures:
                print(f"- {failure}")
        else:
            print("PASS Wave570 render-validation probe")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
