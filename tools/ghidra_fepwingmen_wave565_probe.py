#!/usr/bin/env python3
"""Validate Wave565 FEPWingmen Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave565-fepwingmen-005230c0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepwingmen_wave565_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEP_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPWingmen.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x005230c0": {
        "raw": "005230c0",
        "name": "CFEPWingmen__TransitionNotification",
        "signature": "void __thiscall CFEPWingmen__TransitionNotification(void * this, int from_page)",
        "tags": {"fep-wingmen", "transition-notification", "vtable-slot", "timestamp-reset", "renamed", "signature-corrected", "retail-only", "no-source-file"},
        "comment_tokens": ("vtable 0x005dba10 slot 6", "RET 0x4", "0x0088a0a8"),
        "decompile_tokens": (
            "CFEPWingmen__TransitionNotification(void *this,int from_page)",
            "PLATFORM__GetSysTimeFloat()",
            "*(undefined4 *)((int)this + 0x18) = 0;",
        ),
    },
    "0x00521650": {
        "raw": "00521650",
        "name": "CFEPWingmen__GetWingmenCount",
        "signature": "char CFEPWingmen__GetWingmenCount(void)",
        "tags": {"fep-wingmen", "wingman-count", "frontend-config", "signature-deferred", "retail-only", "no-source-file"},
        "comment_tokens": ("DAT_0089da6c/DAT_0089da74", "DAT_0089d94c", "runtime menu behavior remain unproven"),
        "decompile_tokens": (
            "DAT_0089da74 = DAT_0089da6c;",
            "DAT_0089d94c == *piVar1",
            "piVar1[3] != 0",
            "return cVar2;",
        ),
    },
    "0x00521a60": {
        "raw": "00521a60",
        "name": "CFEPWingmen__Destroy",
        "signature": "void __fastcall CFEPWingmen__Destroy(void * this)",
        "tags": {"fep-wingmen", "destructor", "frontend-thing-cleanup", "pointer-set", "signature-deferred", "retail-only", "no-source-file"},
        "comment_tokens": ("vtable 0x005dba10 slot 1", "this+0x08/+0x0c/+0x10", "Signature left unchanged"),
        "decompile_tokens": (
            "CFrontEndThing__dtor_base",
            "CSPtrSet__Remove",
            "CFEPBEConfig__CleanupSquads",
            "CDXMemoryManager__Free",
        ),
    },
    "0x00521ae0": {
        "raw": "00521ae0",
        "name": "CFEPWingmen__Load",
        "signature": "void __thiscall CFEPWingmen__Load(void * this, void * stream)",
        "tags": {"fep-wingmen", "load", "cdxmembuffer", "pointer-set", "signature-corrected", "retail-only", "no-source-file"},
        "comment_tokens": ("RET 0x4", "record+0x14", "this+0x28"),
        "decompile_tokens": (
            "CFEPWingmen__Load(void *this,void *stream)",
            "local_14 = this;",
            "this_00 = stream;",
            "CSPtrSet__AddToTail((void *)((int)local_14 + 0x28),local_20);",
        ),
    },
    "0x00521c80": {
        "raw": "00521c80",
        "name": "CFEPWingmen__Update",
        "signature": "void __thiscall CFEPWingmen__Update(void * this, int state)",
        "tags": {"fep-wingmen", "per-frame-update", "spinner-helper", "devmode", "missing-boundary-deferred", "retail-only", "no-source-file"},
        "comment_tokens": ("this+0x14", "vtable slot +0x0c", "0x00521d20 remains deferred"),
        "decompile_tokens": (
            "_DAT_005d8574",
            "CFEPWingmen__UpdateSpinnerTransformAndPulse",
            "g_bDevModeEnabled",
            "(**(code **)(*(int *)this + 0xc))(0x2c,0x3f800000);",
        ),
    },
    "0x0046baf0": {
        "raw": "0046baf0",
        "name": "CFEPWingmen__UpdateSpinnerTransformAndPulse",
        "signature": "void __thiscall CFEPWingmen__UpdateSpinnerTransformAndPulse(void * this)",
        "tags": {"shared-frontend-spinner", "transform", "pulse", "fep-wingmen", "frontend-render", "retail-only", "no-source-file"},
        "comment_tokens": ("shared frontend spinner helper", "DAT_00672fd0", "Existing owner name is retained"),
        "decompile_tokens": (
            "CFEPWingmen__UpdateSpinnerTransformAndPulse(void *this)",
            "fcos",
            "fsin",
            "*(float *)((int)this + 0x4c)",
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
    vtables = read_text(BASE / "post_vtable_primary.tsv")

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
            "005dba28\t<none>\t<no_function>\tDATA",
            "00450d4d\t004505b0\tCFEPBEConfig__Render\tUNCONDITIONAL_CALL",
            "0051df5b\t0051ded0\tCFEPMultiplayerStart__Process\tUNCONDITIONAL_CALL",
            "00450043\t00450010\tCFEPBEConfig__UpdateTransitionTimers\tUNCONDITIONAL_CALL",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x005230d8\t0x005230c0\tCFEPWingmen__TransitionNotification\tRET\t0x4",
            "0x00521c7c\t0x00521ae0\tCFEPWingmen__Load\tRET\t0x4",
            "0x00521c96\t0x00521c80\tCFEPWingmen__Update\tCALL\t0x0046baf0",
        ),
        failures,
    )
    require_tokens(
        "vtable",
        vtables,
        (
            "005dba10\t0\t005dba10\t0x005216c0",
            "005dba10\t3\t005dba1c\t0x00521d20",
            "005dba10\t6\t005dba28\t0x005230c0\t005230c0\t005230c0\tCFEPWingmen__TransitionNotification",
        ),
        failures,
    )

    queue = json.loads(read_text(BASE / "post_static_reaudit_queue.json"))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3283,
        "undefinedSignatureCount": 1498,
        "paramSignatureCount": 1180,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")

    docs = {
        "public note": (
            PUBLIC_NOTE,
            ("Wave565", "FEPWingmen", "CFEPWingmen__TransitionNotification", "3283"),
        ),
        "function index": (
            FUNCTION_INDEX,
            ("Wave565", "FEPWingmen", "CFEPWingmen__TransitionNotification"),
        ),
        "fep index": (
            FEP_INDEX,
            ("Wave565", "CFEPWingmen__TransitionNotification", "0x005216c0", "0x00521d20"),
        ),
        "ghidra reference": (
            GHIDRA_REFERENCE,
            ("Wave565", "FEPWingmen", "CFEPWingmen__Load"),
        ),
        "campaign": (
            CAMPAIGN,
            ("Wave 565", "FEPWingmen", "CVBufTexture"),
        ),
        "backlog": (
            BACKLOG,
            ("Wave565", "fepwingmen", "0x005230c0"),
        ),
        "ledger": (
            LEDGER,
            ("Wave565", "fepwingmen", "0x00521ae0"),
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
        print("Wave565 FEPWingmen probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave565 FEPWingmen probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
