#!/usr/bin/env python3
"""Validate Wave566 FEPWingmen/MixerMap Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave566-cvbuftexture-mixermap-005230e0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fep_mixermap_wave566_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEP_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPWingmen.cpp" / "_index.md"
MIXERMAP_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mixermap.cpp" / "_index.md"
VBUFTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x005230e0": {
        "raw": "005230e0",
        "name": "CFEPWingmen__FindCurrentLevelRecord",
        "signature": "void * __thiscall CFEPWingmen__FindCurrentLevelRecord(void * this)",
        "tags": {
            "fep-wingmen",
            "current-level-record",
            "owner-corrected",
            "signature-corrected",
            "renamed",
            "retail-binary-evidence",
            "no-source-file",
        },
        "comment_tokens": (
            "supersedes the stale CVBufTexture owner label",
            "this+0x30",
            "DAT_0089d94c",
            "CFEPWingmen__Load appending 0x24 records",
        ),
        "decompile_tokens": (
            "CFEPWingmen__FindCurrentLevelRecord(void *this)",
            "*(undefined4 **)((int)this + 0x30) = puVar1;",
            "if (DAT_0089d94c == *piVar2) break;",
            "return piVar2;",
        ),
    },
    "0x00523190": {
        "raw": "00523190",
        "name": "CMixerMap__InitSlot",
        "signature": "void __thiscall CMixerMap__InitSlot(void * this, void * chunk_reader)",
        "tags": {"mixermap", "chunk-reader", "slot-init", "signature-corrected", "retail-binary-evidence", "no-source-file"},
        "comment_tokens": ("RET 0x4", "slot_count*0x51", "line 0x86"),
        "decompile_tokens": (
            "CMixerMap__InitSlot(void *this,void *chunk_reader)",
            "CChunkReader__Read(chunk_reader,this,0x14,1);",
            "OID__AllocObject(*(int *)this * 0x51",
            "CChunkReader__Read(chunk_reader,outBuffer,1,*(int *)this * 0x51);",
        ),
    },
    "0x00523210": {
        "raw": "00523210",
        "name": "CMixerMap__DestroySlot",
        "signature": "void __thiscall CMixerMap__DestroySlot(void * this)",
        "tags": {"mixermap", "slot-cleanup", "destructor-callback", "signature-corrected", "retail-binary-evidence", "no-source-file"},
        "comment_tokens": ("this+0x04", "CDXMemoryManager__Free"),
        "decompile_tokens": (
            "CMixerMap__DestroySlot(void *this)",
            "CDXMemoryManager__Free(&DAT_009c3df0,*(void **)((int)this + 4));",
            "*(undefined4 *)((int)this + 4) = 0;",
        ),
    },
    "0x00523230": {
        "raw": "00523230",
        "name": "CMixerMap__Destroy",
        "signature": "void __thiscall CMixerMap__Destroy(void * this)",
        "tags": {"mixermap", "cleanup", "heightfield-caller", "signature-corrected", "retail-binary-evidence", "no-source-file"},
        "comment_tokens": ("0x14000-byte slot array", "CMixerMap__DestroySlot", "CHeightField__ShutdownAndDestroyMixerMap"),
        "decompile_tokens": (
            "CMixerMap__Destroy(void *this)",
            "CDXLandscape__DestroyArrayWithCallback(iVar2,0x14,*(int *)(iVar2 + -4),CMixerMap__DestroySlot);",
            "*(undefined4 *)this = 0;",
            "*(undefined4 *)((int)this + 4) = 0;",
        ),
    },
    "0x005232b0": {
        "raw": "005232b0",
        "name": "CMixerMap__Init",
        "signature": "void __thiscall CMixerMap__Init(void * this, void * chunk_reader)",
        "tags": {
            "mixermap",
            "chunk-reader",
            "heightfield-caller",
            "slot-array",
            "signature-corrected",
            "retail-binary-evidence",
            "no-source-file",
        },
        "comment_tokens": ("0x14004", "0x1000", "0x40000", "CHeightField__DeserializeMapAndInitResources"),
        "decompile_tokens": (
            "CMixerMap__Init(void *this,void *chunk_reader)",
            "CMixerMap__InitSlot((void *)(iVar3 + *(int *)this),chunk_reader);",
            "CChunkReader__Read(chunk_reader,*(void **)((int)this + 4),1,0x40000);",
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
    callsites = read_text(BASE / "post_fep_callsite_instructions.tsv")

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
            "005230e0\tCFEPWingmen__FindCurrentLevelRecord\t0052206a",
            "005230e0\tCFEPWingmen__FindCurrentLevelRecord\t0052271f",
            "00523190\tCMixerMap__InitSlot\t00523381\t005232b0\tCMixerMap__Init\tUNCONDITIONAL_CALL",
            "00523230\tCMixerMap__Destroy\t00490f4a\t00490f40\tCHeightField__ShutdownAndDestroyMixerMap",
            "005232b0\tCMixerMap__Init\t004910e1\t00491060\tCHeightField__DeserializeMapAndInitResources",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x005230e0\t0x005230e0\tTARGET\t0\t0x005230e0\t0x005230e0\tCFEPWingmen__FindCurrentLevelRecord\tMOV\tEAX, dword ptr [ECX + 0x28]",
            "0x005231f7\t0x00523190\tCMixerMap__InitSlot\tRET\t0x4",
            "0x00523381\t0x005232b0\tCMixerMap__Init\tCALL\t0x00523190",
            "0x005233bb\t0x005232b0\tCMixerMap__Init\tRET\t0x4",
        ),
        failures,
    )
    require_tokens(
        "fep callsites",
        callsites,
        (
            "0x00522065\t<none>\t<no_function>\tMOV\tECX, 0x89da44",
            "0x0052206a\t<none>\t<no_function>\tCALL\t0x005230e0",
            "0x0052271a\t<none>\t<no_function>\tMOV\tECX, 0x89da44",
            "0x0052271f\t<none>\t<no_function>\tCALL\t0x005230e0",
            "0x00522c57\t<none>\t<no_function>\tMOV\tECX, 0x89da44",
            "0x00522c5c\t<none>\t<no_function>\tCALL\t0x005230e0",
        ),
        failures,
    )

    queue = json.loads(read_text(BASE / "post_static_reaudit_queue.json"))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3278,
        "undefinedSignatureCount": 1494,
        "paramSignatureCount": 1179,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")

    docs = {
        "public note": (
            PUBLIC_NOTE,
            ("Wave566", "CFEPWingmen__FindCurrentLevelRecord", "CMixerMap__Init", "3278"),
        ),
        "function index": (
            FUNCTION_INDEX,
            ("Wave566", "CFEPWingmen__FindCurrentLevelRecord", "CMixerMap__Init"),
        ),
        "fep index": (
            FEP_INDEX,
            ("Wave566", "CFEPWingmen__FindCurrentLevelRecord", "0x005230e0"),
        ),
        "mixermap index": (
            MIXERMAP_INDEX,
            ("Wave566", "CMixerMap__InitSlot", "void __thiscall CMixerMap__Init(void * this, void * chunk_reader)"),
        ),
        "vbuftexture index": (
            VBUFTEXTURE_INDEX,
            ("Wave566", "stale CVBufTexture owner label", "CFEPWingmen__FindCurrentLevelRecord"),
        ),
        "ghidra reference": (
            GHIDRA_REFERENCE,
            ("Wave566", "CFEPWingmen__FindCurrentLevelRecord", "CMixerMap__Destroy"),
        ),
        "campaign": (
            CAMPAIGN,
            ("Wave 566", "FEPWingmen/MixerMap", "Input__HandleMouseWindowMessage"),
        ),
        "backlog": (
            BACKLOG,
            ("Wave566", "fep_mixermap", "0x005230e0"),
        ),
        "ledger": (
            LEDGER,
            ("Wave566", "fep_mixermap", "0x005232b0"),
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
        print("Wave566 FEP/MixerMap probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave566 FEP/MixerMap probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
