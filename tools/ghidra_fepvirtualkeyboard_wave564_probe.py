#!/usr/bin/env python3
"""Validate Wave564 FEP virtual keyboard Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave564-fepvirtualkeyboard-00520530"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepvirtualkeyboard_wave564_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEP_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPVirtualKeyboard.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x00520530": {
        "raw": "00520530",
        "name": "CFEPVirtualKeyboard__InitKeyboardLayout",
        "signature": "void __thiscall CFEPVirtualKeyboard__InitKeyboardLayout(void * this)",
        "tags": {"fep-virtual-keyboard", "keyboard-layout", "frontend-input", "retail-only", "no-source-file"},
        "comment_tokens": ("retail-binary-first", "this+0x6e4..0x6f4", "control-token pages"),
        "decompile_tokens": (
            "CFEPVirtualKeyboard__InitKeyboardLayout(void *this)",
            "*(undefined4 *)((int)this + 0x6e4) = 0;",
            "*(undefined2 *)((int)this + 0x54) = 9;",
        ),
    },
    "0x00520cc0": {
        "raw": "00520cc0",
        "name": "CFEPVirtualKeyboard__HandleKeyToken",
        "signature": "void __thiscall CFEPVirtualKeyboard__HandleKeyToken(void * this, int key_token)",
        "tags": {"fep-virtual-keyboard", "key-token", "edit-buffer", "frontend-input", "retail-only", "no-source-file"},
        "comment_tokens": ("RET 0x4", "DAT_008a1388", "_DAT_0089bcb8"),
        "decompile_tokens": (
            "CFEPVirtualKeyboard__HandleKeyToken(void *this,int key_token)",
            "switch(key_token & 0xffff)",
            "CRT__WStrCpy(&DAT_008a1388",
            "CDXFont__GetTextExtent",
        ),
    },
    "0x00520f70": {
        "raw": "00520f70",
        "name": "CFEPVirtualKeyboard__MoveSelectionToRow",
        "signature": "void __thiscall CFEPVirtualKeyboard__MoveSelectionToRow(void * this, int target_row)",
        "tags": {"fep-virtual-keyboard", "row-navigation", "selection-state", "frontend-input", "retail-only", "no-source-file"},
        "comment_tokens": ("RET 0x4", "this+0x6f4", "CFEPVirtualKeyboard__IsSpecialKeyBlocked"),
        "decompile_tokens": (
            "CFEPVirtualKeyboard__MoveSelectionToRow(void *this,int target_row)",
            "iVar7 = target_row;",
            "*(int *)((int)this + 0x6e8) = iVar7;",
            "CFEPVirtualKeyboard__IsSpecialKeyBlocked(this)",
        ),
    },
    "0x00521260": {
        "raw": "00521260",
        "name": "CFEPVirtualKeyboard__DrawPanel",
        "signature": "void __thiscall CFEPVirtualKeyboard__DrawPanel(void * this, float panel_y, float transition, int alpha)",
        "tags": {"fep-virtual-keyboard", "draw-panel", "edit-buffer", "frontend-render", "retail-only", "no-source-file"},
        "comment_tokens": ("RET 0x0c", "DAT_0063fd30 panel_y", "blinking cursor"),
        "decompile_tokens": (
            "CFEPVirtualKeyboard__DrawPanel(void *this,float panel_y,float transition,int alpha)",
            "uVar6 = alpha * 0xa00000;",
            "CDXFont__GetTextExtent",
            "CDXFont__DrawTextDynamic",
        ),
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
    drawpanel_range = read_text(BASE / "post_drawpanel_range.tsv")
    button_caller = read_text(BASE / "post_caller_decompile" / "00520370_CFEPVirtualKeyboard__ButtonPressed.c")
    render_caller = read_text(BASE / "post_caller_decompile" / "00521100_CFEPVirtualKeyboard__Render.c")

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
            if "source-parity" in present:
                failures.append(f"{address} unexpectedly has source-parity tag")

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
            "0051ffbd\t0051ff90\tCFEPVirtualKeyboard__Init",
            "005203c7\t00520370\tCFEPVirtualKeyboard__ButtonPressed",
            "005211c6\t00521100\tCFEPVirtualKeyboard__Render",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x00520cba\t0x00520530\tCFEPVirtualKeyboard__InitKeyboardLayout\tRET\t\tc3\tTERMINATOR",
            "0x00520dbd\t0x00520cc0\tCFEPVirtualKeyboard__HandleKeyToken\tRET\t0x4\tc2 04 00\tTERMINATOR",
            "0x005210fc\t0x00520f70\tCFEPVirtualKeyboard__MoveSelectionToRow\tRET\t0x4\tc2 04 00\tTERMINATOR",
            "0x005211c6\t0x00521100\tCFEPVirtualKeyboard__Render\tCALL\t0x00521260",
        ),
        failures,
    )
    require_tokens("drawpanel range", drawpanel_range, ("005214c2\tC2 0C 00\tRET\t0xc",), failures)
    require_tokens(
        "button caller",
        button_caller,
        (
            "CFEPVirtualKeyboard__MoveSelectionToRow(this,*(int *)((int)this + 0x6e8) + 1);",
            "CFEPVirtualKeyboard__MoveSelectionToRow(this,4);",
            "CFEPVirtualKeyboard__HandleKeyToken",
        ),
        failures,
    )
    require_tokens(
        "render caller",
        render_caller,
        ("CFEPVirtualKeyboard__DrawPanel(this,DAT_0063fd30,transition,local_8);",),
        failures,
    )

    queue = json.loads(read_text(BASE / "post_static_reaudit_queue.json"))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3289,
        "undefinedSignatureCount": 1498,
        "paramSignatureCount": 1181,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")

    docs = {
        "public note": (
            PUBLIC_NOTE,
            ("Wave564", "FEP virtual keyboard", "CFEPVirtualKeyboard__DrawPanel", "3289"),
        ),
        "function index": (
            FUNCTION_INDEX,
            ("Wave564", "FEP virtual keyboard", "CFEPVirtualKeyboard__HandleKeyToken"),
        ),
        "fep index": (
            FEP_INDEX,
            ("Wave564", "retail-binary-first", "DrawPanel", "RET 0x0c"),
        ),
        "ghidra reference": (
            GHIDRA_REFERENCE,
            ("Wave564", "FEP virtual keyboard", "CFEPVirtualKeyboard__DrawPanel"),
        ),
        "campaign": (
            CAMPAIGN,
            ("Wave 564", "FEP virtual keyboard", "CFEPWingmen"),
        ),
        "backlog": (
            BACKLOG,
            ("Wave564", "fep_virtual_keyboard", "0x00521260"),
        ),
        "ledger": (
            LEDGER,
            ("Wave564", "fep_virtual_keyboard", "0x00521260"),
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
        print("Wave564 FEP virtual keyboard probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave564 FEP virtual keyboard probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
