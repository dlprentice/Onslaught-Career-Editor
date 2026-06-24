#!/usr/bin/env python3
"""Validate Wave563 CFastVB tail Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave563-cfastvb-tail-0051a270"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_tail_wave563_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x0051a270": {
        "raw": "0051a270",
        "name": "CFastVB__Create",
        "signature": "int __thiscall CFastVB__Create(void * this)",
        "tags": {"cfastvb", "create", "dynamic-vbuffer"},
        "comment_tokens": ("CVBuffer__CreateDynamic", "vertex_stride 0x1c", "FVF/format 0x144"),
        "decompile_tokens": ("CFastVB__Create(void *this)", "CVBuffer__CreateDynamic", "0x1c,0x144"),
    },
    "0x0051a340": {
        "raw": "0051a340",
        "name": "CFastVB__Destroy",
        "signature": "void __thiscall CFastVB__Destroy(void * this)",
        "tags": {"cfastvb", "destroy", "index-buffer"},
        "comment_tokens": ("shared static index buffer", "DAT_00897a90", "clears the global"),
        "decompile_tokens": ("CFastVB__Destroy(void *this)", "DAT_00897a90"),
    },
    "0x0051a380": {
        "raw": "0051a380",
        "name": "CFastVB__LockAligned",
        "signature": "ushort __thiscall CFastVB__LockAligned(void * this, void * * out_vertex_data, int vertex_count)",
        "tags": {"cfastvb", "lock-range", "quad-aligned"},
        "comment_tokens": ("RET 0x8", "out_vertex_data", "0x2800"),
        "decompile_tokens": ("CFastVB__LockAligned(void *this,void **out_vertex_data,int vertex_count)", "CVBuffer__LockRange", "0x1800"),
    },
    "0x0051a430": {
        "raw": "0051a430",
        "name": "CFastVB__Lock",
        "signature": "ushort __thiscall CFastVB__Lock(void * this, void * * out_vertex_data, int vertex_count)",
        "tags": {"cfastvb", "lock-range", "render-batching"},
        "comment_tokens": ("CFastVB__LockAligned", "CFastVB__Render", "0x1c-byte vertices"),
        "decompile_tokens": ("CFastVB__Lock(void *this,void **out_vertex_data,int vertex_count)", "CFastVB__Render", "CVBuffer__LockRange"),
    },
    "0x0051a510": {
        "raw": "0051a510",
        "name": "CFastVB__Render",
        "signature": "void __thiscall CFastVB__Render(void * this)",
        "tags": {"cfastvb", "index-buffer", "quad-render"},
        "comment_tokens": ("CIBuffer__Create with index_count 0x1d4c", "0x144", "draws indexed primitive type 4"),
        "decompile_tokens": ("CFastVB__Render(void *this)", "CIBuffer__Create(DAT_00897a90,0x1d4c)", "CEngine__DrawIndexedPrimitives"),
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


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")

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

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

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
            "CDXFont__DrawTextScaled",
            "CRenderQueue__RenderAll",
            "CVBufTexture__DrawSpriteEx",
            "CLTShell__ShutdownRuntimeAndReleaseResources",
            "CDXCompass__Render",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x0051a215\t<none>\t<no_function>\tMOV\tdword ptr [0x00897aa4], 0x1388",
            "0x0051a2d5\t0x0051a270\tCFastVB__Create\tPUSH\t0x144",
            "0x0051a392\t0x0051a380\tCFastVB__LockAligned\tRET\t0x8",
            "0x0051a444\t0x0051a430\tCFastVB__Lock\tRET\t0x8",
            "0x0051a59a\t0x0051a510\tCFastVB__Render\tPUSH\t0x1d4c",
        ),
        failures,
    )

    queue = json.loads(read_text(BASE / "post_static_reaudit_queue.json"))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3293,
        "undefinedSignatureCount": 1498,
        "paramSignatureCount": 1185,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")

    docs = {
        "public note": (
            PUBLIC_NOTE,
            ("Wave563", "CFastVB tail", "CFastVB__Render", "3293"),
        ),
        "function index": (
            FUNCTION_INDEX,
            ("Wave563", "CFastVB tail", "CFastVB__LockAligned"),
        ),
        "fastvb index": (
            FASTVB_INDEX,
            ("Wave563", "0x1388", "index_count 0x1d4c"),
        ),
        "ghidra reference": (
            GHIDRA_REFERENCE,
            ("Wave563", "CFastVB tail", "CFastVB__Render"),
        ),
        "campaign": (
            CAMPAIGN,
            ("Wave 563", "CFastVB tail", "CFEPVirtualKeyboard"),
        ),
        "backlog": (
            BACKLOG,
            ("Wave563", "CFastVB tail", "0x0051a270"),
        ),
        "ledger": (
            LEDGER,
            ("Wave563", "cfastvb_tail", "0x0051a510"),
        ),
    }
    for label, (path, tokens) in docs.items():
        require_tokens(label, read_text(path), tokens, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run checks and exit nonzero on failure")
    args = parser.parse_args(argv)
    failures = run_check()
    if failures:
        print("Wave563 CFastVB tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave563 CFastVB tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
