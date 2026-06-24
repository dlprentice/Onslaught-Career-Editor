#!/usr/bin/env python3
"""Validate Wave579 IScript slot/goodie Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave579-iscript-slot-goodie-005338a0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_slot_goodie_wave579_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-slot-goodie-wave579",
    "retail-binary-evidence",
    "mission-script",
    "iscript",
    "command-handler",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x005338a0": {
        "name": "IScript__SetPlayerLives",
        "signature": "void __stdcall IScript__SetPlayerLives(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "player-lives", "script-command-registry"},
        "comment_tokens": ("SetPlayerLives(player_index,lives)", "RET 0xc", "CGame__SetPlayerLives"),
        "decompile_file": "005338a0_IScript__SetPlayerLives.c",
        "decompile_tokens": ("script_args", "CGame__SetPlayerLives", "DAT_008a9a98"),
    },
    "0x005338d0": {
        "name": "IScript__SetSlot",
        "signature": "void __stdcall IScript__SetSlot(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "slot-bit", "runtime-slot-only", "script-command-registry"},
        "comment_tokens": ("SetSlot(slot,val)", "runtime script/game slot bitset only", "does not persist"),
        "decompile_file": "005338d0_IScript__SetSlot.c",
        "decompile_tokens": ("CGame__SetSlot", "DAT_008a9a98", "0x3c"),
    },
    "0x00533900": {
        "name": "IScript__SetSlotSave",
        "signature": "void __stdcall IScript__SetSlotSave(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "slot-bit", "persistent-slot", "career-save", "script-command-registry"},
        "comment_tokens": ("SetSlotSave(slot,val)", "CCareer__SetSlot", "0x00660620"),
        "decompile_file": "00533900_IScript__SetSlotSave.c",
        "decompile_tokens": ("CGame__SetSlot", "CCareer__SetSlot", "CAREER"),
    },
    "0x005339a0": {
        "name": "IScript__GetSlotBitValue",
        "signature": "void __stdcall IScript__GetSlotBitValue(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "slot-bit", "bool-result", "script-command-registry", "result-object"},
        "comment_tokens": ("GetSlot(slot)", "0x005e4d50", "out_result"),
        "decompile_file": "005339a0_IScript__GetSlotBitValue.c",
        "decompile_tokens": ("OID__AllocObject(8", "CGame__GetSlot", "out_result"),
    },
    "0x00533a70": {
        "name": "IScript__SetGoodieState",
        "signature": "void __stdcall IScript__SetGoodieState(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "goodie-state", "career-save", "one-based-index", "script-command-registry"},
        "comment_tokens": ("SetGoodieState(index,state)", "g_Career_mGoodies[index-1]", "index 0 would underflow"),
        "decompile_file": "00533a70_IScript__SetGoodieState.c",
        "decompile_tokens": ("DAT_00662560", "script_args", "0x30"),
    },
    "0x00533aa0": {
        "name": "IScript__GetGoodieState",
        "signature": "void __stdcall IScript__GetGoodieState(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "goodie-state", "career-save", "one-based-index", "int-result", "script-command-registry", "result-object"},
        "comment_tokens": ("GetGoodieState(index)", "0x005e4af8", "out_result"),
        "decompile_file": "00533aa0_IScript__GetGoodieState.c",
        "decompile_tokens": ("OID__AllocObject(8", "g_Career_mGoodies", "out_result"),
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

    require_log_summary(
        BASE / "wave579_apply_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave579_apply.log",
        {"updated": 6, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave579_apply_final_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 6,
        "post_tags.tsv": 6,
        "post_xrefs.tsv": 6,
        "post_target_instructions.tsv": 1326,
        "post_decompile/index.tsv": 6,
        "post_vtables.tsv": 24,
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
    vtables = read_text(BASE / "post_vtables.tsv")

    require_tokens("xrefs", xrefs, ("ScriptCommandRegistry__InitBuiltins", "IScript__SetSlotSave", "IScript__GetGoodieState"), failures)
    require_tokens("instructions", instructions, ("RET\t0xc", "0x662560", "0x662564", "0x5e4d50", "0x5e4af8"), failures)
    require_tokens("vtables", vtables, ("005e4d50", "CBoolDataType__Assign", "005e4af8", "CIntDataType__Add"), failures)

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime mission-script behavior proven",
        "source identity proven",
        "rebuild parity proven",
        "fully RE'ed",
        "fully REed",
    )
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
            missing = spec["tags"] - present
            if missing:
                failures.append(f"{address} missing tags: {sorted(missing)}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None or decomp_row.get("status") != "OK":
            failures.append(f"{address} decompile index missing or not OK")
        decompile_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
        require_tokens(f"{address} decompile", decompile_text, spec["decompile_tokens"], failures)

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3160,
        "undefinedSignatureCount": 1420,
        "paramSignatureCount": 1131,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00533b70":
        failures.append(f"queue head mismatch: {head.get('address')} != 0x00533b70")

    backup = json.loads(read_text(BASE / "wave579_backup_summary.json"))
    if backup.get("status") != "PASS" or backup.get("diffCount") != 0:
        failures.append(f"backup summary not PASS: {backup}")

    require_doc_tokens(
        PUBLIC_NOTE,
        ("Wave579 IScript Slot/Goodie Static Ghidra Readiness", "0x005338a0", "0x00533b70 IScript__Create3PointPanCamera", "runtime mission-script behavior remains unproven"),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        ("Wave579 static read-back", "void __stdcall IScript__GetSlotBitValue", "runtime SetSlot from persistent SetSlotSave", "runtime mission-script behavior remains unproven"),
        failures,
    )
    require_doc_tokens(FUNCTION_INDEX, ("Wave579", "IScript", "0x00533b70"), failures)
    require_doc_tokens(GHIDRA_REFERENCE, ("Wave579", "SetSlotSave", "GetGoodieState"), failures)
    require_doc_tokens(CAMPAIGN, ("Wave579", "2933", "3160", "1420", "0x00533b70"), failures)
    require_doc_tokens(BACKLOG, ("0x005338a0,0x005338d0,0x00533900,0x005339a0,0x00533a70,0x00533aa0", "Wave579"), failures)
    require_doc_tokens(LEDGER, ("wave579", "iscript_slot_goodie", "0x00533aa0"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("wave579", "iscript_slot_goodie", "0x005338a0"), failures)

    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    result = {"status": "PASS" if not failures else "FAIL", "failureCount": len(failures), "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave579 IScript slot/goodie probe: {result['status']}")
        for failure in failures:
            print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
