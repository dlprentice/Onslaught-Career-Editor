#!/usr/bin/env python3
"""Validate Wave584 IScript object/audio command-handler Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave584-iscript-name-audio-00535670"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_object_audio_wave584_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave584_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-object-audio-wave584",
    "retail-binary-evidence",
    "mission-script",
    "iscript",
    "command-handler",
    "signature-corrected",
    "comment-hardened",
    "script-context-abi",
    "script-command-registry",
}

SIGNATURE = "void __thiscall {name}(void * this, void * script_args, void * unused_state, void * out_result)"

TARGETS = {
    "0x00535670": {
        "name": "IScript__GetThingName",
        "tags": COMMON_TAGS | {"object-name", "string-result", "cstring-datatype", "flag-guard-08", "weapon-physics-name"},
        "comment_tokens": ("CStringDataType", "CBattleEngine__GetWeaponPhysicsName", "RET 0xc"),
        "decompile_file": "00535670_IScript__GetThingName.c",
        "decompile_tokens": ("script_args", "out_result", "CBattleEngine__GetWeaponPhysicsName"),
    },
    "0x005357b0": {
        "name": "IScript__GetThingTypeName",
        "tags": COMMON_TAGS | {"object-type-name", "string-result", "cstring-datatype", "flag-guard-08"},
        "comment_tokens": ("CStringDataType", "+0x4b0/+0xa8", "RET 0xc"),
        "decompile_file": "005357b0_IScript__GetThingTypeName.c",
        "decompile_tokens": ("script_args", "out_result", "CStringDataType__InitFromString"),
    },
    "0x00535fa0": {
        "name": "IScript__Attack",
        "tags": COMMON_TAGS | {"attack-command", "target-thing", "argument-getter-40", "unit-target-propagation", "flag-guards"},
        "comment_tokens": ("CUnit__PropagateTargetUnitToHierarchy", "datatype vtable slot +0x40", "RET 0xc"),
        "decompile_file": "00535fa0_IScript__Attack.c",
        "decompile_tokens": ("script_args", "CUnit__PropagateTargetUnitToHierarchy", "+ 0x154"),
    },
    "0x005362a0": {
        "name": "IScript__GetTextWidth",
        "tags": COMMON_TAGS | {"text-width", "float-result", "argument-getter-30", "world-text-slot"},
        "comment_tokens": ("CWorld__GetWorldTextSlotTimerValue", "vtable 0x005e4ea4", "RET 0xc"),
        "decompile_file": "005362a0_IScript__GetTextWidth.c",
        "decompile_tokens": ("script_args", "CWorld__GetWorldTextSlotTimerValue", "out_result"),
    },
    "0x005363e0": {
        "name": "IScript__GetPlayerBattleEngine",
        "tags": COMMON_TAGS | {"player-battle-engine", "thing-pointer-result", "argument-getter-30", "player-table"},
        "comment_tokens": ("CThingPtrDataType", "DAT_008a9d3c", "RET 0xc"),
        "decompile_file": "005363e0_IScript__GetPlayerBattleEngine.c",
        "decompile_tokens": ("script_args", "CThingPtrDataType__ScalarDeletingDestructor", "out_result"),
    },
    "0x00536ca0": {
        "name": "IScript__TriggerHitEffect",
        "tags": COMMON_TAGS | {"trigger-hit-effect", "float-input", "argument-getter-34", "thing-vfunc-1ac", "flag-guard-10"},
        "comment_tokens": ("vtable slot +0x1ac", "datatype getter vtable slot +0x34", "RET 0xc"),
        "decompile_file": "00536ca0_IScript__TriggerHitEffect.c",
        "decompile_tokens": ("script_args", "+ 0x1ac", "+ 0x34"),
    },
    "0x00537410": {
        "name": "IScript__PlaySound",
        "tags": COMMON_TAGS | {"audio-command", "message-box", "default-text", "argument-getter-30", "argument-getter-34"},
        "comment_tokens": ("DAT_008a9d84", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "RET 0xc"),
        "decompile_file": "00537410_IScript__PlaySound.c",
        "decompile_tokens": ("script_args", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "DAT_008a9d84"),
    },
    "0x00537500": {
        "name": "IScript__PlaySoundWithCallback",
        "tags": COMMON_TAGS | {"audio-command", "callback-message", "message-box", "argument-getter-30", "argument-getter-34"},
        "comment_tokens": ("active-reader target", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "RET 0xc"),
        "decompile_file": "00537500_IScript__PlaySoundWithCallback.c",
        "decompile_tokens": ("script_args", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "DAT_008a9d84"),
    },
    "0x005375f0": {
        "name": "IScript__PlaySoundWithFade",
        "tags": COMMON_TAGS | {"audio-command", "fade-event", "message-box", "scheduled-event-7d1", "argument-getter-30", "argument-getter-34"},
        "comment_tokens": ("schedules event 0x7d1", "CScheduledEvent__Set", "RET 0xc"),
        "decompile_file": "005375f0_IScript__PlaySoundWithFade.c",
        "decompile_tokens": ("script_args", "CScheduledEvent__Set", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
    },
    "0x005377e0": {
        "name": "IScript__PlaySoundWithPriority",
        "tags": COMMON_TAGS | {"audio-command", "priority-message", "message-box", "argument-getter-30", "argument-getter-34"},
        "comment_tokens": ("priority value", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "RET 0xc"),
        "decompile_file": "005377e0_IScript__PlaySoundWithPriority.c",
        "decompile_tokens": ("script_args", "script_args + 0xc", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
    },
    "0x005378e0": {
        "name": "IScript__PlaySoundWithFadeAndPriority",
        "tags": COMMON_TAGS | {"audio-command", "fade-event", "priority-message", "message-box", "scheduled-event-7d1", "argument-getter-30", "argument-getter-34"},
        "comment_tokens": ("fade-event setup with priority", "schedules event 0x7d1", "RET 0xc"),
        "decompile_file": "005378e0_IScript__PlaySoundWithFadeAndPriority.c",
        "decompile_tokens": ("script_args", "CScheduledEvent__Set", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance"),
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
        BASE / "wave584_apply_dry.log",
        {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave584_apply.log",
        {"updated": 11, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave584_apply_final_dry.log",
        {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 11,
        "post_tags.tsv": 11,
        "post_xrefs.tsv": 11,
        "post_instructions.tsv": 4059,
        "post_decompile/index.tsv": 11,
        "post_vtables.tsv": 64,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_instructions.tsv")
    vtables = read_text(BASE / "post_vtables.tsv")

    require_tokens("xrefs", xrefs, ("ScriptCommandRegistry__InitBuiltins", "IScript__GetThingName", "IScript__PlaySoundWithFadeAndPriority"), failures)
    require_tokens(
        "instructions",
        instructions,
        ("RET\t0xc", "CALL\t0x0040c570", "CALL\t0x004fda20", "CALL\t0x0050d760", "CALL\t0x004f2580", "PUSH\t0x7d1"),
        failures,
    )
    require_tokens(
        "vtables",
        vtables,
        ("005e4df8", "CThingPtrDataType__ScalarDeletingDestructor", "005e4ea4", "CFloatDataType__Add", "005e4f1c"),
        failures,
    )

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
        expected_signature = SIGNATURE.format(name=spec["name"])
        if row["signature"] != expected_signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {expected_signature}")
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
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    signals = queue.get("qualitySignals", {})
    for key, expected in {
        "commentlessFunctionCount": 3130,
        "undefinedSignatureCount": 1404,
        "paramSignatureCount": 1117,
    }.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00537fd0" or head.get("name") != "CBoolDataType__ctor_like_00537fd0":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    if backup.get("status") != "PASS" or backup.get("diffCount") != 0:
        failures.append(f"backup summary failed: {backup}")
    if backup.get("sourceFileCount") != 19 or backup.get("destinationFileCount") != 19:
        failures.append(f"backup file count mismatch: {backup}")
    if int(backup.get("sourceTotalBytes", 0)) != 160664455:
        failures.append(f"backup source bytes mismatch: {backup.get('sourceTotalBytes')} != 160664455")
    if int(backup.get("destinationTotalBytes", 0)) != 160664455:
        failures.append(f"backup destination bytes mismatch: {backup.get('destinationTotalBytes')} != 160664455")
    if backup.get("sourceManifestSha256") != backup.get("destinationManifestSha256"):
        failures.append("backup manifest hashes differ")
    require_tokens("backup destination", backup.get("destinationRoot", ""), ("post_wave584_iscript_object_audio_verified",), failures)

    require_doc_tokens(
        PUBLIC_NOTE,
        ("Wave584", "IScript object/audio command handlers", "runtime mission-script behavior remains unproven", "CBoolDataType__ctor_like_00537fd0"),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave584 IScript object/audio command-handler hardening",
            "Post-Wave584 queue telemetry is `6093` functions, `2963` commented, `3130` commentless, `1404` exact-undefined signatures, and `1117` `param_N` signatures.",
            "0x00537fd0 CBoolDataType__ctor_like_00537fd0",
        ),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        (
            "## Wave584 Static Read-Back",
            "IScript object/audio command-handler tranche",
            "IScript__PlaySoundWithFadeAndPriority",
            "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Wave584 object/audio command handlers",
            "IScript__GetThingName",
            "IScript__PlaySoundWithFadeAndPriority",
            "2963/6093 = 48.63%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 584: IScript Object/Audio Command Handlers",
            "post_wave584_iscript_object_audio_verified",
            "strict clean-signature proxy `2914/6093 = 47.83%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("0x00535670,0x005357b0,0x00535fa0", "Wave584"), failures)
    require_doc_tokens(LEDGER, ("Ghidra IScript object/audio Wave584", "post_wave584_iscript_object_audio_verified"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("Ghidra IScript object/audio Wave584", '"attempt_id":20239'), failures)

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
        print("Wave584 IScript object/audio probe:", result["status"])
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
