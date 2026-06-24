#!/usr/bin/env python3
"""Validate Wave555 CWorld load/core Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave555-cworld-load-core-0050a870"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cworld_load_core_wave555_2026-05-18.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"


TARGETS = {
    "0x0050a870": {
        "raw": "0050a870",
        "name": "CWorld__ClearSetArrays",
        "signature": "void __fastcall CWorld__ClearSetArrays(void * world)",
        "tags": {"cworld", "cworld-load-core-wave555", "owner-corrected", "set-array"},
        "comment_tokens": ("nineteen CSPtrSet slots", "DAT_00855090", "remain unproven"),
        "decompile_tokens": ("CWorld__ClearSetArrays(void *world)", "CSPtrSet__Clear"),
    },
    "0x0050a9c0": {
        "raw": "0050a9c0",
        "name": "CWorld__InitSetArraysAndState",
        "signature": "void * __fastcall CWorld__InitSetArraysAndState(void * world)",
        "tags": {"cworld", "cworld-load-core-wave555", "owner-corrected", "state-init"},
        "comment_tokens": ("nineteen CSPtrSet slots", "+0x26c through +0x278", "returning world"),
        "decompile_tokens": ("CWorld__InitSetArraysAndState(void *world)", "CSPtrSet__Init"),
    },
    "0x0050abb0": {
        "raw": "0050abb0",
        "name": "CWorld__ShutdownAndClear_Thunk",
        "signature": "void __fastcall CWorld__ShutdownAndClear_Thunk(void * world)",
        "tags": {"cworld", "cworld-load-core-wave555", "shutdown", "thunk"},
        "comment_tokens": ("pure jump thunk", "CWorld__ShutdownAndClear", "remain unproven"),
        "decompile_tokens": ("CWorld__ShutdownAndClear_Thunk(void *world)", "DAT_0067a748"),
    },
    "0x0050abc0": {
        "raw": "0050abc0",
        "name": "CWorld__CloneScriptObjectCodeByName",
        "signature": "void * __thiscall CWorld__CloneScriptObjectCodeByName(void * this, char * script_name)",
        "tags": {"cworld", "cworld-load-core-wave555", "phantom-param-removed", "script-events"},
        "comment_tokens": ("RET 0x4", "script_name", "fatal-errors when no script is found"),
        "decompile_tokens": (
            "CWorld__CloneScriptObjectCodeByName(void *this,char *script_name)",
            "CScriptObjectCode__Clone",
        ),
        "forbidden_decompile_tokens": ("param_1", "param_2"),
    },
    "0x0050ac70": {
        "raw": "0050ac70",
        "name": "CWorld__LoadScriptEvents",
        "signature": "void __thiscall CWorld__LoadScriptEvents(void * this, void * mem_buffer)",
        "tags": {"cworld", "cworld-load-core-wave555", "load-world", "script-events"},
        "comment_tokens": ("RET 0x4", "script-event count", "this +0x120"),
        "decompile_tokens": ("CWorld__LoadScriptEvents(void *this,void *mem_buffer)", "this + 0x120"),
        "forbidden_decompile_tokens": ("param_1", "param_2"),
    },
    "0x0050ada0": {
        "raw": "0050ada0",
        "name": "CWorld__ShutdownAndClear",
        "signature": "void __fastcall CWorld__ShutdownAndClear(void * world)",
        "tags": {"cleanup", "cworld", "cworld-load-core-wave555", "shutdown"},
        "comment_tokens": ("BattleEngineConfigurations", "CWorldMeshList", "resets world state"),
        "decompile_tokens": ("CWorld__ShutdownAndClear(void *world)", "CWorldMeshList__Clear"),
    },
    "0x0050af70": {
        "raw": "0050af70",
        "name": "CWorld__FindThingByName",
        "signature": "void * __thiscall CWorld__FindThingByName(void * this, char * thing_name)",
        "tags": {"cworld", "cworld-load-core-wave555", "phantom-param-removed", "thing-lookup"},
        "comment_tokens": ("RET 0x4", "thing_name", "thing set at this +0xa0"),
        "decompile_tokens": ("CWorld__FindThingByName(void *this,char *thing_name)", "this + 0xa0"),
        "forbidden_decompile_tokens": ("param_1", "param_2"),
    },
    "0x0050b520": {
        "raw": "0050b520",
        "name": "CWorld__LoadWorldFile",
        "signature": "int __thiscall CWorld__LoadWorldFile(void * this, int world_id, int is_base_world)",
        "tags": {"cworld", "cworld-load-core-wave555", "load-world", "resource-load"},
        "comment_tokens": ("world_id", "is_base_world=1", "nonzero status"),
        "decompile_tokens": ("CWorld__LoadWorldFile(void *this,int world_id,int is_base_world)", "is_base_world"),
        "forbidden_decompile_tokens": ("param_1", "param_2", "param_3"),
    },
    "0x0050b780": {
        "raw": "0050b780",
        "name": "CWorld__DeserializeWorld",
        "signature": "void __thiscall CWorld__DeserializeWorld(void * this, void * chunk_reader)",
        "tags": {"cworld", "cworld-load-core-wave555", "deserialize", "resource-load"},
        "comment_tokens": ("RET 0x4", "reader/buffer", "+0x26c through +0x278"),
        "decompile_tokens": ("CWorld__DeserializeWorld(void *this,void *chunk_reader)", "chunk_reader"),
        "forbidden_decompile_tokens": ("param_1", "param_2"),
    },
    "0x0050d4c0": {
        "raw": "0050d4c0",
        "name": "CWorld__LoadWorldHeader",
        "signature": "void __thiscall CWorld__LoadWorldHeader(void * this, void * mem_buffer, int is_base_world)",
        "tags": {"cworld", "cworld-load-core-wave555", "load-world", "world-header"},
        "comment_tokens": ("RET 0x8", "mem_buffer", "is_base_world"),
        "decompile_tokens": ("CWorld__LoadWorldHeader(void *this,void *mem_buffer,int is_base_world)", "is_base_world"),
        "forbidden_decompile_tokens": ("param_1", "param_2", "param_3"),
    },
    "0x0050d580": {
        "raw": "0050d580",
        "name": "CWorld__InitLODLists",
        "signature": "void __fastcall CWorld__InitLODLists(void * world)",
        "tags": {"cworld", "cworld-load-core-wave555", "load-world", "lod"},
        "comment_tokens": ("three 0x2004-byte", "35, 45, and 60", "world +0x200"),
        "decompile_tokens": ("CWorld__InitLODLists(void *world)", "CWorld__InitOccupancyBitplanes"),
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

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')}")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status mismatch: {row.get('status')}")
        require_tokens(f"{address} comment", row.get("comment", ""), spec["comment_tokens"], failures)

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing_tags = set(spec["tags"]) - actual_tags
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

        idx_row = decomp_index.get(address)
        if idx_row is None or idx_row.get("status") != "OK":
            failures.append(f"{address} decompile index not OK")
        decomp_file = BASE / "post_decompile" / f"{spec['raw']}_{spec['name']}.c"
        decomp_text = read_text(decomp_file)
        require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)
        for token in spec.get("forbidden_decompile_tokens", ()):
            if token in decomp_text:
                failures.append(f"{address} forbidden decompile token remained: {token}")

    queue = json.loads(read_text(QUEUE))
    expected_queue = {
        "totalFunctions": 6089,
        "commentlessFunctionCount": 3398,
        "undefinedSignatureCount": 1530,
        "paramSignatureCount": 1256,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status not PASS: {queue.get('status')}")
    if queue.get("totalFunctions") != expected_queue["totalFunctions"]:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    quality = queue.get("qualitySignals", {})
    for key, expected in expected_queue.items():
        if key == "totalFunctions":
            continue
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)}")

    docs = {
        "public note": read_text(PUBLIC_NOTE),
        "World.cpp index": read_text(WORLD_DOC),
        "function index": read_text(FUNCTION_INDEX),
        "mutation backlog": read_text(BACKLOG),
        "mutation ledger": read_text(LEDGER),
    }
    for label, text in docs.items():
        require_tokens(
            label,
            text,
            (
                "Wave555",
                "CWorld__ClearSetArrays",
                "CWorld__LoadWorldFile",
                "CWorld__InitLODLists",
            ),
            failures,
        )

    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    try:
        failures = run_check()
    except Exception as exc:  # pragma: no cover - command-line guard
        print(f"Wave555 CWorld load/core probe failed to run: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Wave555 CWorld load/core probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave555 CWorld load/core probe PASS")
    print(f"Validated {len(TARGETS)} targets and queue/docs evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
