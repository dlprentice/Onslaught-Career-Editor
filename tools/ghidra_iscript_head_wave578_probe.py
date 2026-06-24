#!/usr/bin/env python3
"""Validate Wave578 IScript Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave578-iscript-head-005333b0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_head_wave578_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-head-wave578",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "mission-script",
    "iscript",
}

TARGETS = {
    "0x005333b0": {
        "raw": "005333b0",
        "name": "IScript__Constructor",
        "signature": "void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)",
        "tags": COMMON_TAGS | {"constructor", "owner-correction", "rename-corrected", "monitor-base", "script-back-pointer"},
        "comment_tokens": ("RET 0x8", "0x005e4f08", "script_object_code+0x68"),
        "decompile_file": "005333b0_IScript__Constructor.c",
        "decompile_tokens": ("CSPtrSet__Init", "PTR_CScriptEventNB__HandleMessage_005e4f08", "script_object_code + 0x68"),
    },
    "0x00533430": {
        "raw": "00533430",
        "name": "IScript__ScalarDeletingDestructor",
        "signature": "void * __thiscall IScript__ScalarDeletingDestructor(void * this, byte flags)",
        "tags": COMMON_TAGS | {"destructor", "scalar-deleting-destructor", "vtable-slot"},
        "comment_tokens": ("RET 0x4", "flags&1", "IScript__Destructor"),
        "decompile_file": "00533430_IScript__ScalarDeletingDestructor.c",
        "decompile_tokens": ("IScript__Destructor", "flags & 1", "CDXMemoryManager__Free"),
    },
    "0x00533450": {
        "raw": "00533450",
        "name": "IScript__Destructor",
        "signature": "void __thiscall IScript__Destructor(void * this)",
        "tags": COMMON_TAGS | {"destructor", "rename-corrected", "listener-cleanup", "monitor-cleanup"},
        "comment_tokens": ("not a constructor", "this+0x28", "CMonitor__Shutdown"),
        "decompile_file": "00533450_IScript__Destructor.c",
        "decompile_tokens": ("CSPtrSet__Clear", "CMonitor__Shutdown", "PTR_CScriptEventNB__HandleMessage_005e4f08"),
    },
    "0x00533500": {
        "raw": "00533500",
        "name": "IScript__CallEvent0AndRegisterNestedListeners",
        "signature": "void __thiscall IScript__CallEvent0AndRegisterNestedListeners(void * this)",
        "tags": COMMON_TAGS | {"event-dispatch", "event-id-0", "listener-registration"},
        "comment_tokens": ("event id 0", "CScriptEventNB__RegisterEventListener", "DAT_008a9ac0"),
        "decompile_file": "00533500_IScript__CallEvent0AndRegisterNestedListeners.c",
        "decompile_tokens": ("CScriptObjectCode__CallEvent", "CScriptEventNB__RegisterEventListener", "DAT_008a9ac0"),
    },
    "0x005335a0": {
        "raw": "005335a0",
        "name": "IScript__CallEventId6_OrReset",
        "signature": "void __thiscall IScript__CallEventId6_OrReset(void * this)",
        "tags": COMMON_TAGS | {"event-dispatch", "event-id-6", "reset-gate"},
        "comment_tokens": ("event id 6", "DAT_0089c528", "final flag 0"),
        "decompile_file": "005335a0_IScript__CallEventId6_OrReset.c",
        "decompile_tokens": ("CScriptObjectCode__CallEvent", "DAT_0089c528", "CScriptObjectCode__Reset"),
    },
    "0x005335d0": {
        "raw": "005335d0",
        "name": "IScript__CreateThingRef",
        "signature": "void __thiscall IScript__CreateThingRef(void * this, void * referenced_thing)",
        "tags": COMMON_TAGS | {"thing-ref", "event-dispatch", "event-id-1", "script-result-object"},
        "comment_tokens": ("RET 0x4", "0x005e4af8", "event id 1"),
        "decompile_file": "005335d0_IScript__CreateThingRef.c",
        "decompile_tokens": ("OID__AllocObject(8", "0x10d", "CScriptObjectCode__CallEvent"),
    },
    "0x00533660": {
        "raw": "00533660",
        "name": "IScript__CallEventId5_OrReset",
        "signature": "void __thiscall IScript__CallEventId5_OrReset(void * this)",
        "tags": COMMON_TAGS | {"event-dispatch", "event-id-5", "reset-gate", "death-cleanup-callback"},
        "comment_tokens": ("event id 5", "CUnit", "death/cleanup"),
        "decompile_file": "00533660_IScript__CallEventId5_OrReset.c",
        "decompile_tokens": ("CScriptObjectCode__CallEvent", "DAT_0089c528", "CScriptObjectCode__Reset"),
    },
    "0x00533690": {
        "raw": "00533690",
        "name": "IScript__CreateThingRefWithSquad",
        "signature": "void __thiscall IScript__CreateThingRefWithSquad(void * this, void * referenced_thing)",
        "tags": COMMON_TAGS | {"thing-ref", "event-dispatch", "event-id-4", "pointer-tracking", "script-result-object"},
        "comment_tokens": ("RET 0x4", "0x005e4df8", "event id 4"),
        "decompile_file": "00533690_IScript__CreateThingRefWithSquad.c",
        "decompile_tokens": ("CSPtrSet__AddToHead", "PTR_CThingPtrDataType__ScalarDeletingDestructor_005e4df8", "CScriptObjectCode__CallEvent"),
    },
    "0x005337e0": {
        "raw": "005337e0",
        "name": "IScript__CallEventId3_OrReset",
        "signature": "void __thiscall IScript__CallEventId3_OrReset(void * this)",
        "tags": COMMON_TAGS | {"event-dispatch", "event-id-3", "reset-gate", "shutdown-callback"},
        "comment_tokens": ("event id 3", "BattleEngine", "shutdown/deploy"),
        "decompile_file": "005337e0_IScript__CallEventId3_OrReset.c",
        "decompile_tokens": ("CScriptObjectCode__CallEvent", "DAT_0089c528", "CScriptObjectCode__Reset"),
    },
    "0x00533840": {
        "raw": "00533840",
        "name": "IScript__RestoreSavedStateAndGotoInstruction",
        "signature": "void __thiscall IScript__RestoreSavedStateAndGotoInstruction(void * this)",
        "tags": COMMON_TAGS | {"state-restore", "goto-instruction", "animation-callback", "reset-gate"},
        "comment_tokens": ("this+0x38", "CSPtrSet", "CScriptObjectCode__GotoInstruction"),
        "decompile_file": "00533840_IScript__RestoreSavedStateAndGotoInstruction.c",
        "decompile_tokens": ("CScriptObjectCode__CopyState", "CSPtrSet__Remove", "CScriptObjectCode__GotoInstruction"),
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
        BASE / "wave578_apply_dry.log",
        {"updated": 0, "skipped": 10, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave578_apply.log",
        {"updated": 10, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave578_apply_final_dry.log",
        {"updated": 0, "skipped": 10, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 10,
        "post_tags.tsv": 10,
        "post_xrefs.tsv": 17,
        "post_target_instructions.tsv": 2610,
        "post_decompile/index.tsv": 10,
        "post_vtables.tsv": 288,
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
        "iscript vtables",
        vtables,
        ("005e4f08", "IScript__ScalarDeletingDestructor", "005e4df8", "CThingPtrDataType__ScalarDeletingDestructor", "005e4b4c"),
        failures,
    )
    require_tokens(
        "xrefs",
        xrefs,
        (
            "CComplexThing__SetScript",
            "CComplexThing__HandleEvent",
            "CScriptEventNB__UpdateWaypointFollowing",
            "CComplexThing__Hit",
            "CBattleEngine__StartDieProcess",
            "CComplexThing__FinishedPlayingCurrentAnimation",
        ),
        failures,
    )
    require_tokens("instructions", instructions, ("RET\t0x8", "RET\t0x4", "5e4f08", "5e4df8"), failures)

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime event behavior proven",
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
        "commentlessFunctionCount": 3161,
        "undefinedSignatureCount": 1423,
        "paramSignatureCount": 1131,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x005339a0":
        failures.append(f"queue head mismatch: {head.get('address')} != 0x005339a0")

    backup = json.loads(read_text(BASE / "wave578_backup_summary.json"))
    if backup.get("status") != "PASS" or backup.get("diffCount") != 0:
        failures.append(f"backup summary not PASS: {backup}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Wave578 IScript Head Static Ghidra Readiness",
            "0x005333b0",
            "0x005339a0 IScript__GetSlotBitValue",
            "runtime mission-script behavior remains unproven",
        ),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        (
            "Wave578 static read-back",
            "void * __thiscall IScript__Constructor",
            "CreateThingRef helpers are IScript thiscall helpers with RET 0x4",
            "runtime mission-script behavior remains unproven",
        ),
        failures,
    )
    require_doc_tokens(FUNCTION_INDEX, ("Wave578", "IScript", "0x005339a0"), failures)
    require_doc_tokens(GHIDRA_REFERENCE, ("Wave578", "IScript", "thing-ref"), failures)
    require_doc_tokens(CAMPAIGN, ("Wave578", "2932", "3161", "1423", "0x005339a0"), failures)
    require_doc_tokens(BACKLOG, ("0x005333b0,0x00533430,0x00533450,0x00533500,0x005335a0,0x005335d0,0x00533660,0x00533690,0x005337e0,0x00533840", "Wave578"), failures)
    require_doc_tokens(LEDGER, ("wave578", "iscript_head", "0x00533840"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("wave578", "iscript_head", "0x005333b0"), failures)

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
        print(f"Wave578 IScript head probe: {result['status']}")
        for failure in failures:
            print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
