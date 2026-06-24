#!/usr/bin/env python3
"""Validate Wave586 CScriptEventNB Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave586-scripteventnb-core-00538470"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_scripteventnb_wave586_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
SCRIPT_EVENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptEventNB.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave586_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "scripteventnb-wave586",
    "retail-binary-evidence",
    "mission-script",
    "scripteventnb",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x00538470": {
        "name": "CScriptEventNB__UpdateWaypointFollowing",
        "signature": "void __fastcall CScriptEventNB__UpdateWaypointFollowing(void * event_nb)",
        "tags": COMMON_TAGS | {"waypoint-following", "event-manager-tick", "ecx-only"},
        "comment_tokens": ("waypoint-following", "CEventManager__AddEvent_AtTime", "message-2000"),
        "decompile_file": "00538470_CScriptEventNB__UpdateWaypointFollowing.c",
        "decompile_tokens": ("CEventManager__AddEvent_AtTime", "IScript__CreateThingRef"),
    },
    "0x005385e0": {
        "name": "CScriptEventNB__HandleMessage",
        "signature": "void __thiscall CScriptEventNB__HandleMessage(void * this, void * message)",
        "tags": COMMON_TAGS | {"message-dispatch", "ret-4", "event-message-2000"},
        "comment_tokens": ("RET 0x4", "message id 2000", "event id 2"),
        "decompile_file": "005385e0_CScriptEventNB__HandleMessage.c",
        "decompile_tokens": ("CScriptEventNB__UpdateWaypointFollowing", "CScriptObjectCode__CallEvent"),
    },
    "0x005386b0": {
        "name": "CScriptEventNB__ScalarDeletingDestructor",
        "signature": "void * __thiscall CScriptEventNB__ScalarDeletingDestructor(void * this, byte delete_flags)",
        "tags": COMMON_TAGS | {"destructor", "scalar-deleting-destructor", "ret-4"},
        "comment_tokens": ("scalar deleting destructor", "RET 0x4", "CDXMemoryManager__Free"),
        "decompile_file": "005386b0_CScriptEventNB__ScalarDeletingDestructor.c",
        "decompile_tokens": ("CScriptEventNB__Destructor", "CDXMemoryManager__Free"),
    },
    "0x005386d0": {
        "name": "CScriptEventNB__Destructor",
        "signature": "void __fastcall CScriptEventNB__Destructor(void * event_nb)",
        "tags": COMMON_TAGS | {"destructor", "base-vtable", "monitor-shutdown", "ecx-only"},
        "comment_tokens": ("base vtable", "DAT_00855190", "CMonitor__Shutdown"),
        "decompile_file": "005386d0_CScriptEventNB__Destructor.c",
        "decompile_tokens": ("PTR_SharedVFunc__NoOpOneArg_004014c0_005e4f34", "CMonitor__Shutdown"),
    },
    "0x00538760": {
        "name": "CScriptEventNB__Init",
        "signature": "void __fastcall CScriptEventNB__Init(void * event_nb)",
        "tags": COMMON_TAGS | {"initializer", "vtable", "ecx-only"},
        "comment_tokens": ("initializer", "0x005e4f44", "zeros fields"),
        "decompile_file": "00538760_CScriptEventNB__Init.c",
        "decompile_tokens": ("PTR_CScriptEventNB__HandleEventMessage_005e4f44",),
    },
    "0x00538780": {
        "name": "CScriptEventNB__ScalarDeletingDestructor2",
        "signature": "void * __thiscall CScriptEventNB__ScalarDeletingDestructor2(void * this, byte delete_flags)",
        "tags": COMMON_TAGS | {"destructor", "scalar-deleting-destructor", "ret-4", "vtable-slot"},
        "comment_tokens": ("0x005e4f44 vtable", "RET 0x4", "CScriptEventNB__BaseDestructor"),
        "decompile_file": "00538780_CScriptEventNB__ScalarDeletingDestructor2.c",
        "decompile_tokens": ("CScriptEventNB__BaseDestructor", "CDXMemoryManager__Free"),
    },
    "0x005387b0": {
        "name": "CScriptEventNB__ClearEventListeners",
        "signature": "void __fastcall CScriptEventNB__ClearEventListeners(void * listener_entry)",
        "tags": COMMON_TAGS | {"listener-cleanup", "csptrset", "ecx-only"},
        "comment_tokens": ("listener-entry cleanup", "CMonitor__DeleteDeletionEvent", "CSPtrSet"),
        "decompile_file": "005387b0_CScriptEventNB__ClearEventListeners.c",
        "decompile_tokens": ("CMonitor__DeleteDeletionEvent", "CSPtrSet__Clear"),
    },
    "0x00538860": {
        "name": "CScriptEventNB__CreateEventListener",
        "signature": "void __fastcall CScriptEventNB__CreateEventListener(void * event_nb)",
        "tags": COMMON_TAGS | {"listener-allocation", "csptrset", "ecx-only"},
        "comment_tokens": ("allocates", "0x10 bytes", "ScriptEventNB.cpp line 0x42"),
        "decompile_file": "00538860_CScriptEventNB__CreateEventListener.c",
        "decompile_tokens": ("OID__AllocObject", "CSPtrSet__Init"),
    },
    "0x005388d0": {
        "name": "CScriptEventNB__DestroyAllEvents",
        "signature": "void __fastcall CScriptEventNB__DestroyAllEvents(void * event_nb)",
        "tags": COMMON_TAGS | {"listener-cleanup", "vtable-slot", "shutdown", "ecx-only"},
        "comment_tokens": ("CMonitor__Shutdown_Core", "CScriptEventNB__ClearEventListeners", "nulls event_nb+0x08"),
        "decompile_file": "005388d0_CScriptEventNB__DestroyAllEvents.c",
        "decompile_tokens": ("CMonitor__Shutdown_Core", "CScriptEventNB__ClearEventListeners"),
    },
    "0x00538950": {
        "name": "CScriptEventNB__BaseDestructor",
        "signature": "void __fastcall CScriptEventNB__BaseDestructor(void * event_nb)",
        "tags": COMMON_TAGS | {"destructor", "monitor-shutdown", "ecx-only"},
        "comment_tokens": ("base-destructor", "0x005e4f44", "CMonitor__Shutdown"),
        "decompile_file": "00538950_CScriptEventNB__BaseDestructor.c",
        "decompile_tokens": ("PTR_CScriptEventNB__HandleEventMessage_005e4f44", "CMonitor__Shutdown"),
    },
    "0x00538960": {
        "name": "CScriptEventNB__RegisterEventListener",
        "signature": "void * __thiscall CScriptEventNB__RegisterEventListener(void * this, void * event_name_ref, void * event_function)",
        "tags": COMMON_TAGS | {"listener-registration", "ret-8", "iscript-xref", "csptrset"},
        "comment_tokens": ("IScript__CallEvent0AndRegisterNestedListeners", "RET 0x8", "vtable-name getter +0x38"),
        "decompile_file": "00538960_CScriptEventNB__RegisterEventListener.c",
        "decompile_tokens": ("OID__AllocObject", "CMonitor__AddDeletionEvent", "CSPtrSet__AddToTail"),
    },
    "0x00538b70": {
        "name": "CScriptEventNB__PostEvent",
        "signature": "void __thiscall CScriptEventNB__PostEvent(void * this, char * event_name)",
        "tags": COMMON_TAGS | {"post-event", "ret-4", "listener-dispatch", "event-function"},
        "comment_tokens": ("RET 0x4", "game playing", "CEventFunction"),
        "decompile_file": "00538b70_CScriptEventNB__PostEvent.c",
        "decompile_tokens": ("CConsole__Printf", "CEventFunction__Execute"),
    },
    "0x00538c70": {
        "name": "CScriptEventNB__HandleEventMessage",
        "signature": "void __thiscall CScriptEventNB__HandleEventMessage(void * this, void * message)",
        "tags": COMMON_TAGS | {"event-message-handler", "ret-4", "vtable-slot", "event-function"},
        "comment_tokens": ("event-manager message handler", "RET 0x4", "payload event name"),
        "decompile_file": "00538c70_CScriptEventNB__HandleEventMessage.c",
        "decompile_tokens": ("CEventFunction__Execute", "CConsole__Printf"),
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


def get_ci(mapping: dict[str, object], key: str, default: object = None) -> object:
    if key in mapping:
        return mapping[key]
    if not mapping:
        return default
    lowered = {k.lower(): v for k, v in mapping.items()}
    return lowered.get(key.lower(), default)


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
        BASE / "logs" / "wave586_apply_dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave586_apply.log",
        {"updated": 13, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave586_apply_final_dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post/metadata.tsv": 13,
        "post/tags.tsv": 13,
        "post/xrefs.tsv": 18,
        "post/instructions.tsv": 5577,
        "post/decompile/index.tsv": 13,
        "post/vtables.tsv": 72,
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
    vtables = read_text(BASE / "post" / "vtables.tsv")

    require_tokens(
        "xrefs",
        xrefs,
        ("IScript__CallEvent0AndRegisterNestedListeners", "CGame__InitRestartLoop", "CGame__StartPlayingState", "CGame__HandleEvent"),
        failures,
    )
    require_tokens("instructions", instructions, ("RET\t0x8", "RET\t0x4", "CALL\t0x00538470", "CALL\t0x005387b0"), failures)
    require_tokens("vtables", vtables, ("CScriptEventNB__HandleEventMessage", "CScriptEventNB__ScalarDeletingDestructor2", "CScriptEventNB__DestroyAllEvents"), failures)

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
        "commentlessFunctionCount": 3115,
        "undefinedSignatureCount": 1387,
        "paramSignatureCount": 1116,
    }.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00538ea0" or head.get("name") != "CScriptObjectCode__scalar_deleting_dtor":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    if get_ci(backup, "DiffCount") != 0 or get_ci(backup, "MissingCount") != 0 or get_ci(backup, "ExtraCount") != 0:
        failures.append(f"backup summary failed: {backup}")
    if get_ci(backup, "FileCount") != 19:
        failures.append(f"backup file count mismatch: {backup}")
    if int(get_ci(backup, "TotalBytes", 0)) != 160729991:
        failures.append(f"backup bytes mismatch: {get_ci(backup, 'TotalBytes')} != 160729991")
    require_tokens("backup destination", str(get_ci(backup, "BackupPath", "")), ("post_wave586_scripteventnb_verified",), failures)

    require_doc_tokens(
        PUBLIC_NOTE,
        ("Wave586", "CScriptEventNB", "runtime mission-script behavior remains unproven", "CScriptObjectCode__scalar_deleting_dtor"),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave586 CScriptEventNB hardening",
            "Post-Wave586 queue telemetry is `6093` functions, `2978` commented, `3115` commentless, `1387` exact-undefined signatures, and `1116` `param_N` signatures.",
            "0x00538ea0 CScriptObjectCode__scalar_deleting_dtor",
        ),
        failures,
    )
    require_doc_tokens(
        SCRIPT_EVENT_DOC,
        (
            "## Wave586 Static Read-Back",
            "CScriptEventNB listener/event-manager tranche",
            "CScriptEventNB__RegisterEventListener",
            "0x00538ea0 and 0x00538ec0 remain CScriptObjectCode",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Wave586 CScriptEventNB",
            "CScriptEventNB__UpdateWaypointFollowing",
            "CScriptEventNB__HandleEventMessage",
            "2978/6093 = 48.88%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 586: CScriptEventNB Listener/Event Manager",
            "post_wave586_scripteventnb_verified",
            "strict clean-signature proxy `2932/6093 = 48.12%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("0x00538470,0x005385e0,0x005386b0", "Wave586"), failures)
    require_doc_tokens(LEDGER, ("Ghidra CScriptEventNB Wave586", "post_wave586_scripteventnb_verified"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("Ghidra CScriptEventNB Wave586", '"attempt_id":20241'), failures)

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
        print("Wave586 CScriptEventNB probe:", result["status"])
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
