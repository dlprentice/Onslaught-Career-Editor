#!/usr/bin/env python3
"""Validate Wave561 platform/shell and device-object Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave561-platform-shell-00512130"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_platform_shell_wave561_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
LTSHELL_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
PLATFORM_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Platform.cpp" / "_index.md"
PCPLATFORM_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
VERTEX_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x00512130": {
        "raw": "00512130",
        "name": "CLTShell__WinMain",
        "signature": "int __stdcall CLTShell__WinMain(void * module_handle, void * previous_instance, char * command_line, int show_command)",
        "tags": {"platform-shell-wave561", "winmain"},
        "comment_tokens": ("RET 0x10", "defaultoptions.bea", "CCareer::Load(flag=0)", "D3D application"),
        "decompile_tokens": ("CLTShell__WinMain(void *module_handle", "PeekMessageA"),
    },
    "0x00512470": {
        "raw": "00512470",
        "name": "PlatformInput__ClearTransientKeyStateTable",
        "signature": "void __thiscall PlatformInput__ClearTransientKeyStateTable(void * this)",
        "tags": {"platform-input", "key-state", "phantom-param-removed"},
        "comment_tokens": ("this+0x332e4", "0x40 dword stores", "CFrontEnd__Process", "CGame__Update"),
        "decompile_tokens": ("PlatformInput__ClearTransientKeyStateTable(void *this)", "this+0x332e4"),
    },
    "0x00512490": {
        "raw": "00512490",
        "name": "PLATFORM__ProcessSystemMessages",
        "signature": "int __thiscall PLATFORM__ProcessSystemMessages(void * this, bool poll_pad_edges)",
        "tags": {"message-pump", "device-reset", "phantom-param-removed"},
        "comment_tokens": ("GetMessageA", "PeekMessageA", "CD3DApplication__Reset3DEnvironment", "polls four pad states"),
        "decompile_tokens": ("PLATFORM__ProcessSystemMessages(void *this,bool poll_pad_edges)", "GetMessageA", "PeekMessageA"),
    },
    "0x00512630": {
        "raw": "00512630",
        "name": "Platform__HandleDeviceLostAndRestore",
        "signature": "void __thiscall Platform__HandleDeviceLostAndRestore(void * this)",
        "tags": {"device-loss", "direct3d"},
        "comment_tokens": ("PCPlatform__DeviceFlip", "this+0x32ea0", "DAT_0082b5b0"),
        "decompile_tokens": ("Platform__HandleDeviceLostAndRestore(void *this)", "DAT_0082b5b0"),
    },
    "0x00512670": {
        "raw": "00512670",
        "name": "PCLTShell__ctor",
        "signature": "void * __thiscall PCLTShell__ctor(void * this)",
        "tags": {"constructor", "renamed"},
        "comment_tokens": ("ECX=0x00855bb0", "0x005e488c", "Battle Engine Aquila"),
        "decompile_tokens": ("PCLTShell__ctor(void *this)", "0x005e488c"),
    },
    "0x00512c40": {
        "raw": "00512c40",
        "name": "PCLTShell__ConfirmDevice",
        "signature": "int __stdcall PCLTShell__ConfirmDevice(void * d3d_caps, uint behavior_flags)",
        "tags": {"confirm-device", "vtable-slot", "renamed"},
        "comment_tokens": ("PCLTShell vtable slot 1", "E_FAIL", "S_OK"),
        "decompile_tokens": ("PCLTShell__ConfirmDevice(void *d3d_caps,uint behavior_flags)", "0x80004005"),
    },
    "0x00512ca0": {
        "raw": "00512ca0",
        "name": "CShaderBase__Init",
        "signature": "void __thiscall CShaderBase__Init(void * this)",
        "tags": {"shader-base", "render-list"},
        "comment_tokens": ("DAT_00889074", "this+0x04", "CVertexShader"),
        "decompile_tokens": ("CShaderBase__Init(void *this)", "DAT_00889074"),
    },
    "0x00512cc0": {
        "raw": "00512cc0",
        "name": "CShaderBase__UnlinkFromRenderObjectLists",
        "signature": "uint __stdcall CShaderBase__UnlinkFromRenderObjectLists(void * render_object)",
        "tags": {"shader-base", "device-object", "renamed"},
        "comment_tokens": ("DAT_00889074", "DAT_00889078", "CDXLandscape", "CWaterRenderSystem"),
        "decompile_tokens": ("CShaderBase__UnlinkFromRenderObjectLists(void *render_object)", "DAT_00889074", "DAT_00889078"),
    },
    "0x00512dc0": {
        "raw": "00512dc0",
        "name": "DeviceObject__scalar_deleting_dtor",
        "signature": "void * __thiscall DeviceObject__scalar_deleting_dtor(void * this, byte flags)",
        "tags": {"device-object", "scalar-deleting-dtor", "renamed"},
        "comment_tokens": ("0x005e48c8", "DAT_00889074", "DAT_00889078", "flags bit 0"),
        "decompile_tokens": ("DeviceObject__scalar_deleting_dtor(void *this,byte flags)", "DAT_00889074", "DAT_00889078"),
    },
    "0x00512fc0": {
        "raw": "00512fc0",
        "name": "PlatformInput__ClearAllKeyStateTables",
        "signature": "void __thiscall PlatformInput__ClearAllKeyStateTables(void * this)",
        "tags": {"platform-input", "key-state"},
        "comment_tokens": ("this+0x330e4", "this+0x331e4", "this+0x332e4"),
        "decompile_tokens": ("PlatformInput__ClearAllKeyStateTables(void *this)", "this+0x330e4"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row["address"]): row for row in rows}


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
    vtables = read_text(BASE / "post_vtable_slots.tsv")

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
            "CFrontEnd__Process",
            "CGame__Update",
            "PLATFORM__Process",
            "PCPlatform__DeviceFlip",
            "CVBuffer__ctor_base",
            "CIBuffer__Constructor",
            "CVertexShader__CVertexShader",
            "CDXLandscape__Init",
            "CUMTexture__dtor_base",
            "CDXLandscape__Shutdown",
            "CWaterRenderSystem__dtor",
        ),
        failures,
    )
    require_tokens(
        "vtable slots",
        vtables,
        (
            "005e4890\t0x00512c40\t00512c40\t00512c40\tPCLTShell__ConfirmDevice",
            "005e48c8\t0x00512dc0\t00512dc0\t00512dc0\tDeviceObject__scalar_deleting_dtor",
        ),
        failures,
    )

    docs = {
        "public note": (
            PUBLIC_NOTE,
            ("Wave561", "platform/shell", "PCLTShell__ConfirmDevice", "CShaderBase__UnlinkFromRenderObjectLists"),
        ),
        "function index": (
            FUNCTION_INDEX,
            ("Wave561", "platform/shell", "PCLTShell__ConfirmDevice", "CShaderBase__UnlinkFromRenderObjectLists"),
        ),
        "ltshell index": (
            LTSHELL_INDEX,
            ("Wave561", "platform/shell", "CLTShell__WinMain", "PCLTShell__ConfirmDevice"),
        ),
        "platform index": (
            PLATFORM_INDEX,
            ("Wave561", "platform/shell", "PLATFORM__ProcessSystemMessages", "PlatformInput__ClearAllKeyStateTables"),
        ),
        "pcplatform index": (
            PCPLATFORM_INDEX,
            ("Wave561", "platform/shell", "Platform__HandleDeviceLostAndRestore", "PCPlatform__DeviceFlip"),
        ),
        "vertex index": (
            VERTEX_INDEX,
            ("Wave561", "CShaderBase__Init", "CShaderBase__UnlinkFromRenderObjectLists", "DeviceObject__scalar_deleting_dtor"),
        ),
        "ghidra reference": (
            GHIDRA_REFERENCE,
            ("Wave561", "platform/shell", "PCLTShell__ConfirmDevice", "CShaderBase__UnlinkFromRenderObjectLists"),
        ),
        "campaign": (
            CAMPAIGN,
            ("Wave 561", "platform/shell", "PCLTShell__ConfirmDevice", "CShaderBase__UnlinkFromRenderObjectLists"),
        ),
        "backlog": (
            BACKLOG,
            ("Wave561", "platform/shell", "PCLTShell__ConfirmDevice", "CShaderBase__UnlinkFromRenderObjectLists"),
        ),
        "ledger": (
            LEDGER,
            ("Wave561", "platform/shell", "PCLTShell__ConfirmDevice", "CShaderBase__UnlinkFromRenderObjectLists"),
        ),
    }
    for label, (path, tokens) in docs.items():
        text = read_text(path)
        require_tokens(label, text, tokens, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run checks and exit nonzero on failure")
    args = parser.parse_args(argv)
    failures = run_check()
    if failures:
        print("Wave561 platform/shell probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave561 platform/shell probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
