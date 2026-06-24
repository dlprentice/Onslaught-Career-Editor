#!/usr/bin/env python3
"""Validate Wave585 IScript level/event Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave585-iscript-level-event-00537fd0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_level_event_wave585_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-level-event-wave585",
    "retail-binary-evidence",
    "mission-script",
    "iscript",
    "command-handler",
    "signature-corrected",
    "comment-hardened",
    "script-command-registry",
}

TARGETS = {
    "0x00537fd0": {
        "name": "IScript__IsFriendly",
        "signature": "void __thiscall IScript__IsFriendly(void * this, void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"script-context-abi", "bool-result", "ceventfunctionparam", "isfriendly", "thing-flag-10"},
        "comment_tokens": ("s_IsFriendly_0064f9d4", "CEventFunctionParam", "RET 0xc"),
        "decompile_file": "00537fd0_IScript__IsFriendly.c",
        "decompile_tokens": ("CEventFunctionParam__vtable", "out_result", "+ 0x138"),
    },
    "0x005381a0": {
        "name": "IScript__LevelLost",
        "signature": "void __stdcall IScript__LevelLost(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "level-result", "level-lost", "no-message", "non-death-loss"},
        "comment_tokens": ("LevelLost()", "CGame__DeclareLevelLost(0,0)", "RET 0xc"),
        "decompile_file": "005381a0_IScript__LevelLost.c",
        "decompile_tokens": ("CGame__DeclareLevelLost", "DAT_008a9a98"),
    },
    "0x005381c0": {
        "name": "IScript__LevelLostString",
        "signature": "void __stdcall IScript__LevelLostString(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "level-result", "level-lost-string", "message-id", "non-death-loss"},
        "comment_tokens": ("s_LevelLostString_0064f478", "vtable slot +0x30", "player_died=0"),
        "decompile_file": "005381c0_IScript__LevelLostString.c",
        "decompile_tokens": ("script_args", "+ 0x30", "CGame__DeclareLevelLost"),
    },
    "0x005381e0": {
        "name": "IScript__LevelWon",
        "signature": "void __stdcall IScript__LevelWon(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "level-result", "level-won"},
        "comment_tokens": ("LevelWon()", "CGame__DeclareLevelWon", "RET 0xc"),
        "decompile_file": "005381e0_IScript__LevelWon.c",
        "decompile_tokens": ("CGame__DeclareLevelWon", "DAT_008a9a98"),
    },
    "0x005383c0": {
        "name": "IScript__ScheduleEvent",
        "signature": "void __stdcall IScript__ScheduleEvent(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "post-event", "scheduled-event", "event-manager", "ceventfunctionparam"},
        "comment_tokens": ("s_PostEvent_0064f9e8", "CEventManager__AddEvent_AtTime", "RET 0xc"),
        "decompile_file": "005383c0_IScript__ScheduleEvent.c",
        "decompile_tokens": ("script_args", "CSPtrSet__AddToHead", "CEventManager__AddEvent_AtTime"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


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
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
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
        BASE / "logs" / "apply_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "apply.log",
        {"updated": 5, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "apply_final_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post/metadata.tsv": 5,
        "post/tags.tsv": 5,
        "post/xrefs.tsv": 5,
        "post/instructions.tsv": 1845,
        "post/decompile/index.tsv": 5,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    decomp_index = read_tsv(BASE / "post" / "decompile" / "index.tsv")
    xrefs = read_text(BASE / "post" / "xrefs.tsv")
    instructions = read_text(BASE / "post" / "instructions.tsv")
    registry = read_text(BASE / "post" / "registry-decompile" / "0052ff30_ScriptCommandRegistry__InitBuiltins.c")

    require_tokens("xrefs", xrefs, ("ScriptCommandRegistry__InitBuiltins", "IScript__IsFriendly", "IScript__ScheduleEvent"), failures)
    require_tokens("instructions", instructions, ("RET\t0xc", "CALL\t0x0046f430", "CALL\t0x0046f2f0", "CALL\t0x0044b370"), failures)
    require_tokens("registry", registry, ("s_IsFriendly_0064f9d4", "IScript__IsFriendly", "s_PostEvent_0064f9e8", "s_LevelLostString_0064f478"), failures)

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
                read_text(BASE / "post" / "decompile" / spec["decompile_file"]),
                spec["decompile_tokens"],
                failures,
            )

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("status") != "PASS":
        failures.append("queue status is not PASS")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    signals = queue.get("qualitySignals", {})
    for key, expected in {
        "commentlessFunctionCount": 3128,
        "undefinedSignatureCount": 1400,
        "paramSignatureCount": 1116,
    }.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00538470" or head.get("name") != "CScriptEventNB__UpdateWaypointFollowing":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    if backup.get("diffCount") != 0 or backup.get("missingCount") != 0 or backup.get("extraCount") != 0:
        failures.append(f"backup summary failed: {backup}")
    if backup.get("fileCount") != 19:
        failures.append(f"backup file count mismatch: {backup}")
    if int(backup.get("totalBytes", 0)) != 160664455:
        failures.append(f"backup bytes mismatch: {backup.get('totalBytes')} != 160664455")
    require_tokens("backup destination", backup.get("backupPath", ""), ("post_wave585_iscript_level_event_verified",), failures)

    require_doc_tokens(
        PUBLIC_NOTE,
        ("Wave585", "IScript level/event command handlers", "runtime mission-script behavior remains unproven", "CScriptEventNB__UpdateWaypointFollowing"),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave585 IScript level/event command-handler hardening",
            "Post-Wave585 queue telemetry is `6093` functions, `2965` commented, `3128` commentless, `1400` exact-undefined signatures, and `1116` `param_N` signatures.",
            "0x00538470 CScriptEventNB__UpdateWaypointFollowing",
        ),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        (
            "## Wave585 Static Read-Back",
            "IScript level/event command-handler tranche",
            "IScript__IsFriendly",
            "CEventManager__AddEvent_AtTime",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Wave585 level/event command handlers",
            "IScript__IsFriendly",
            "IScript__ScheduleEvent",
            "2965/6093 = 48.66%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 585: IScript Level/Event Command Handlers",
            "post_wave585_iscript_level_event_verified",
            "strict clean-signature proxy `2919/6093 = 47.91%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("0x00537fd0,0x005381a0,0x005381c0,0x005381e0,0x005383c0", "Wave585"), failures)
    require_doc_tokens(LEDGER, ("Ghidra IScript level/event Wave585", "post_wave585_iscript_level_event_verified"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("Ghidra IScript level/event Wave585", '"attempt_id":20240'), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    failures = run_check()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Wave585 IScript level/event probe:", result["status"])
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
