#!/usr/bin/env python3
"""Validate Wave582 IScript thing-value Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave582-iscript-thing-value-00534fb0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_thing_value_wave582_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave582_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-thing-value-wave582",
    "retail-binary-evidence",
    "mission-script",
    "iscript",
    "command-handler",
    "signature-corrected",
    "comment-hardened",
    "script-context-abi",
    "script-command-registry",
    "thing-value",
}

TARGETS = {
    "0x00534fb0": {
        "name": "IScript__SetThingValueViaVFunc198_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaVFunc198_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"thing-vfunc-198", "argument-getter-38", "flag-guard-10"},
        "comment_tokens": ("vtable slot +0x198", "datatype getter vtable slot +0x38", "RET 0xc"),
        "decompile_file": "00534fb0_IScript__SetThingValueViaVFunc198_FromArg.c",
        "decompile_tokens": ("script_args", "iVar1 + 0x198"),
    },
    "0x00534fe0": {
        "name": "IScript__SetThingValueViaVFunc19C_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaVFunc19C_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"thing-vfunc-19c", "argument-getter-38", "flag-guard-10"},
        "comment_tokens": ("vtable slot +0x19c", "datatype getter vtable slot +0x38", "RET 0xc"),
        "decompile_file": "00534fe0_IScript__SetThingValueViaVFunc19C_FromArg.c",
        "decompile_tokens": ("script_args", "iVar1 + 0x19c"),
    },
    "0x00535010": {
        "name": "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaEngineHelper4FE390_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"engine-helper", "enable-thing-by-name", "argument-getter-38", "flag-guard-10"},
        "comment_tokens": ("CEngine__EnableThingByNameFlag", "datatype getter vtable slot +0x38", "RET 0xc"),
        "decompile_file": "00535010_IScript__SetThingValueViaEngineHelper4FE390_FromArg.c",
        "decompile_tokens": ("CEngine__EnableThingByNameFlag", "thing_name", "script_args"),
    },
    "0x00535040": {
        "name": "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
        "signature": "void __thiscall IScript__SetThingValueViaEngineHelper4FE3F0_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"engine-helper", "disable-thing-by-name", "argument-getter-38", "flag-guard-10"},
        "comment_tokens": ("CEngine__DisableThingByNameFlag", "datatype getter vtable slot +0x38", "RET 0xc"),
        "decompile_file": "00535040_IScript__SetThingValueViaEngineHelper4FE3F0_FromArg.c",
        "decompile_tokens": ("CEngine__DisableThingByNameFlag", "thing_name", "script_args"),
    },
    "0x00535530": {
        "name": "IScript__SetThingFloatViaVFunc1C8_FromArg",
        "signature": "void __thiscall IScript__SetThingFloatViaVFunc1C8_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"thing-vfunc-1c8", "float-input", "argument-getter-34", "flag-guard-10"},
        "comment_tokens": ("vtable slot +0x1c8", "datatype getter vtable slot +0x34", "float"),
        "decompile_file": "00535530_IScript__SetThingFloatViaVFunc1C8_FromArg.c",
        "decompile_tokens": ("script_args", "float10", "iVar1 + 0x1c8"),
    },
    "0x00535560": {
        "name": "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
        "signature": "void __thiscall IScript__SetThingRefViaCUnitHelper4FD830_FromArg(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"unit-helper", "set-faction-hierarchy", "integer-input", "argument-getter-30", "flag-guard-10"},
        "comment_tokens": ("CUnit__SetFactionForHierarchy", "datatype getter vtable slot +0x30", "faction-like state"),
        "decompile_file": "00535560_IScript__SetThingRefViaCUnitHelper4FD830_FromArg.c",
        "decompile_tokens": ("CUnit__SetFactionForHierarchy", "faction_state", "script_args"),
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
        BASE / "wave582_apply_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave582_apply.log",
        {"updated": 6, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave582_apply_final_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 6,
        "post_tags.tsv": 6,
        "post_xrefs.tsv": 6,
        "post_target_instructions.tsv": 534,
        "post_decompile/index.tsv": 6,
        "post_vtables.tsv": 32,
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

    require_tokens(
        "xrefs",
        xrefs,
        ("ScriptCommandRegistry__InitBuiltins", "IScript__SetThingValueViaVFunc198_FromArg", "IScript__SetThingRefViaCUnitHelper4FD830_FromArg"),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        ("RET\t0xc", "dword ptr [EDX + 0x38]", "dword ptr [EDI + 0x198]", "dword ptr [EDI + 0x19c]", "0x004fe390", "0x004fe3f0", "dword ptr [EDX + 0x34]", "dword ptr [EDI + 0x1c8]", "0x004fd830"),
        failures,
    )
    require_tokens("vtables", vtables, ("005e4ea4", "CFloatDataType__Add", "005e4d50", "CBoolDataType__Assign"), failures)

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
            actual_tags = set(filter(None, tag_row["tags"].split(";")))
            missing = sorted(spec["tags"] - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None or decomp_row["status"] != "OK":
            failures.append(f"{address} missing/failed decompile row")
        else:
            require_tokens(
                f"{address} decompile",
                read_text(BASE / "post_decompile" / spec["decompile_file"]),
                spec["decompile_tokens"],
                failures,
            )

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("status") != "PASS":
        failures.append("queue status is not PASS")
    expected_queue = {
        "totalFunctions": 6093,
    }
    for key, value in expected_queue.items():
        if queue.get(key) != value:
            failures.append(f"queue {key} mismatch: {queue.get(key)} != {value}")
    signals = queue.get("qualitySignals", {})
    for key, value in {
        "commentlessFunctionCount": 3143,
        "undefinedSignatureCount": 1413,
        "paramSignatureCount": 1121,
    }.items():
        if signals.get(key) != value:
            failures.append(f"queue signal {key} mismatch: {signals.get(key)} != {value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00535330" or head.get("name") != "CVM__VFunc_01_00535330":
        failures.append(f"unexpected next queue head: {head}")

    if not BACKUP_SUMMARY.is_file():
        failures.append("missing wave582 backup summary")
    else:
        backup = json.loads(read_text(BACKUP_SUMMARY))
        if backup.get("status") != "PASS" or backup.get("diffCount") != 0:
            failures.append(f"backup summary failed: {backup}")
        require_tokens("backup destination", backup.get("destination", ""), ("post_wave582_iscript_thing_value_verified",), failures)

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Wave582",
            "script-context IScript command handlers",
            "runtime mission-script behavior remains unproven",
            "CVM__VFunc_01_00535330",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave582 IScript thing-value command-handler hardening",
            "Post-Wave582 queue telemetry is `6093` functions, `2950` commented, `3143` commentless, `1413` exact-undefined signatures, and `1121` `param_N` signatures.",
            "0x00535330 CVM__VFunc_01_00535330",
        ),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        (
            "## Wave582 Static Read-Back",
            "script-context IScript command ABI",
            "void __thiscall IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
            "CUnit__SetFactionForHierarchy",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Wave582 thing-value command handlers",
            "IScript__SetThingValueViaVFunc198_FromArg",
            "CUnit__SetFactionForHierarchy(context+0x10, faction_state)",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 582: IScript Thing-Value Command Handlers",
            "comment-backed proxy `2950/6093 = 48.42%`",
            "strict clean-signature proxy `2901/6093 = 47.61%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("0x00534fb0,0x00534fe0,0x00535010,0x00535040,0x00535530,0x00535560", "Wave582"), failures)
    require_doc_tokens(LEDGER, ("Ghidra IScript thing-value Wave582", "post_wave582_iscript_thing_value_verified"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("Ghidra IScript thing-value Wave582", "attempt_id\":20237"), failures)

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Return non-zero on failure")
    ap.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = ap.parse_args()

    failures = run_check()
    report = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Wave582 IScript thing-value probe:", report["status"])
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
