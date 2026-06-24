#!/usr/bin/env python3
"""Validate Wave488 CRadarWarningReceiver static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave488-radarwarning-004d65a0"

TARGET_ORDER = [
    "0x00405a20",
    "0x0044a830",
    "0x004d65a0",
    "0x004d6600",
    "0x004d66b0",
    "0x004d6a10",
]

EXPECTED_SUMMARIES = {
    "apply_radarwarning_wave488_dry.log": {
        "updated": 0,
        "skipped": 4,
        "created": 0,
        "would_create": 1,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_radarwarning_wave488_apply.log": {
        "updated": 5,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_radarwarning_wave488_verify_dry.log": {
        "updated": 0,
        "skipped": 5,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

COMMON_WAVE_TAGS = {
    "radar-warning-receiver",
    "radar-warning-wave488",
    "retail-binary-evidence",
    "static-reaudit",
}

TARGETS = {
    "0x00405a20": {
        "name": "CRadarWarningReceiver__scalar_deleting_dtor",
        "signature": "void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void * this, byte flags)",
        "tags": COMMON_WAVE_TAGS | {"comment-hardened", "destructor", "scalar-deleting-dtor", "signature-preserved", "vtable-readback"},
        "comment_tokens": ["vtable 0x005d8810 slot 1", "delete flag bit 0", "CDXMemoryManager__Free", "DAT_009c3df0", "returns this", "runtime lifetime behavior", "rebuild parity remain unproven"],
        "decompile_tokens": ["void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void *this,byte flags)", "CRadarWarningReceiver__dtor(this)", "CDXMemoryManager__Free(&DAT_009c3df0,this)"],
    },
    "0x0044a830": {
        "name": "VFuncSlot_03_0044a830",
        "signature": "void __thiscall VFuncSlot_03_0044a830(void * this, void * source_vector3)",
        "tags": {"attachment-escape-pause-wave365", "owner-deferred", "retail-binary-evidence", "signature-hardened", "static-reaudit"},
        "comment_tokens": ["shared vtable-slot body", "source_vector3", "this+0x08..this+0x10", "CRadarWarningReceiver__Init", "Owner unresolved"],
        "decompile_tokens": ["void __thiscall VFuncSlot_03_0044a830(void *this,void *source_vector3)"],
    },
    "0x004d65a0": {
        "name": "CRadarWarningReceiver__Init",
        "signature": "void __thiscall CRadarWarningReceiver__Init(void * this, void * config_record)",
        "tags": COMMON_WAVE_TAGS | {"comment-hardened", "event-4000", "init", "signature-corrected"},
        "comment_tokens": ["CBattleEngine__Init", "one config_record argument", "VFuncSlot_03_0044a830", "config_record+0x0c/+0x10", "event 4000", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __thiscall CRadarWarningReceiver__Init(void *this,void *config_record)", "VFuncSlot_03_0044a830(this,config_record)", "CEventManager__AddEvent_AtTime", "0xbf800000"],
    },
    "0x004d6600": {
        "name": "CRadarWarningReceiver__dtor",
        "signature": "void __fastcall CRadarWarningReceiver__dtor(void * this)",
        "tags": COMMON_WAVE_TAGS | {"comment-hardened", "destructor", "signature-corrected", "tracked-threat-list"},
        "comment_tokens": ["CRadarWarningReceiver__scalar_deleting_dtor", "vtable 0x005d8810", "this+0x1c/this+0x24", "active reader", "CMonitor__Shutdown", "rebuild parity remain unproven"],
        "decompile_tokens": ["void __fastcall CRadarWarningReceiver__dtor(void *this)", "CGenericActiveReader__dtor", "CDXMemoryManager__Free", "CMonitor__Shutdown(this)"],
    },
    "0x004d66b0": {
        "name": "CRadarWarningReceiver__Update",
        "signature": "void __fastcall CRadarWarningReceiver__Update(void * this)",
        "tags": COMMON_WAVE_TAGS | {"comment-hardened", "event-0fa2", "event-4000", "signature-corrected", "tracked-threat-list", "update-loop"},
        "comment_tokens": ["event 4000", "DAT_008551a0 candidate list", "0x18-byte threat entries", "owner+0x5e4", "event 0x0fa2", "runtime HUD/audio behavior"],
        "decompile_tokens": ["void __fastcall CRadarWarningReceiver__Update(void *this)", "OID__AllocObject(0x18", "CSPtrSet__AddToHead", "CEventManager__AddEvent_AtTime", "CSPtrSet__Remove"],
    },
    "0x004d6a10": {
        "name": "CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000",
        "signature": "void __thiscall CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000(void * this, void * message)",
        "tags": COMMON_WAVE_TAGS | {"comment-hardened", "event-4000", "function-created", "signature-corrected", "vfunc-slot-00"},
        "comment_tokens": ["function-boundary recovery", "vtable 0x005d8810 slot 0", "previously missing 5-instruction body", "message+0x04", "0x0fa0", "RET 0x4"],
        "decompile_tokens": ["void __thiscall CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000(void *this,void *message)", "== 4000", "CRadarWarningReceiver__Update(this)"],
    },
}

XREF_EXPECTATIONS = {
    "0x00405a20": {("0x005d8814", "<no_function>", "DATA")},
    "0x0044a830": {("0x004d65a9", "CRadarWarningReceiver__Init", "UNCONDITIONAL_CALL")},
    "0x004d65a0": {("0x00405710", "CBattleEngine__Init", "UNCONDITIONAL_CALL")},
    "0x004d6600": {("0x00405a23", "CRadarWarningReceiver__scalar_deleting_dtor", "UNCONDITIONAL_CALL")},
    "0x004d66b0": {("0x004d6a1c", "CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000", "UNCONDITIONAL_CALL")},
    "0x004d6a10": {("0x005d8810", "<no_function>", "DATA")},
}

VTABLE_EXPECTATIONS = {
    0: ("0x004d6a10", "CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000", "OK"),
    1: ("0x00405a20", "CRadarWarningReceiver__scalar_deleting_dtor", "OK"),
    3: ("0x0044a830", "VFuncSlot_03_0044a830", "OK"),
}

OVERCLAIMS = (
    "fully re'ed",
    "source identity proven",
    "runtime behavior proven",
    "exact layout proven",
    "rebuild parity proven",
)

STALE_SIGNATURE_TOKENS = (
    "undefined CRadarWarningReceiver__",
    "param_1",
    "param_2",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "function_entry",
            "instruction_addr",
            "vtable",
            "slot_addr",
            "pointer_addr",
            "function_entry",
            "containing_entry",
        ):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def check_summaries(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        path = base / filename
        actual = parse_summary(path)
        if actual != expected:
            failures.append(f"{filename}: expected summary {expected}, got {actual or '<missing>'}")
        if "REPORT: Save succeeded" not in read_text(path):
            failures.append(f"{filename}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    for address in TARGET_ORDER:
        expected = TARGETS[address]
        row = next((r for r in rows if r.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if compact(row.get("signature", "")) != compact(expected["signature"]):
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        if "undefined" in row.get("signature", "").lower():
            failures.append(f"{address}: signature still contains undefined")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for overclaim in OVERCLAIMS:
            if token_present(comment, overclaim):
                failures.append(f"{address}: comment contains overclaim {overclaim!r}")
        tag_row = next((r for r in tag_rows if r.get("address") == address), None)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            missing_tags = expected["tags"] - actual_tags
            if missing_tags:
                failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address in TARGET_ORDER:
        expected = TARGETS[address]
        path = base / "post-decomp" / f"{address[2:]}_{expected['name']}.c"
        text = read_text(path)
        if not text:
            failures.append(f"{address}: missing decompile file {path.name}")
            continue
        for token in expected["decompile_tokens"]:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        header = "\n".join(text.splitlines()[:40])
        for stale in STALE_SIGNATURE_TOKENS:
            if token_present(header, stale):
                failures.append(f"{address}: stale signature token remains in header: {stale!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for target, refs in XREF_EXPECTATIONS.items():
        for from_addr, from_fn, ref_type in refs:
            row = next((r for r in rows if r.get("target_addr") == target and r.get("from_addr") == from_addr), None)
            if row is None:
                failures.append(f"{target}: missing xref from {from_addr}")
                continue
            if row.get("from_function") != from_fn:
                failures.append(f"{target}: xref {from_addr} expected function {from_fn}, got {row.get('from_function')}")
            if row.get("ref_type") != ref_type:
                failures.append(f"{target}: xref {from_addr} expected {ref_type}, got {row.get('ref_type')}")


def check_vtable(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable.tsv")
    for slot_index, (pointer_addr, function_name, status) in VTABLE_EXPECTATIONS.items():
        row = next((r for r in rows if r.get("vtable") == "0x005d8810" and r.get("slot_index") == str(slot_index)), None)
        if row is None:
            failures.append(f"vtable slot {slot_index}: missing row")
            continue
        if row.get("pointer_addr") != pointer_addr:
            failures.append(f"vtable slot {slot_index}: expected pointer {pointer_addr}, got {row.get('pointer_addr')}")
        if row.get("function_name") != function_name:
            failures.append(f"vtable slot {slot_index}: expected function {function_name}, got {row.get('function_name')}")
        if row.get("status") != status:
            failures.append(f"vtable slot {slot_index}: expected status {status}, got {row.get('status')}")


def check_instruction_tokens(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions.tsv")
    for token in (
        "0x004d65a0",
        "RET\t0x4",
        "0x004d6a10",
        "CMP\tword ptr [EAX + 0x4], 0xfa0",
        "CALL\t0x004d66b0",
        "CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000",
    ):
        if token not in text:
            failures.append(f"post_instructions.tsv missing token {token!r}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_vtable(base, failures)
    check_instruction_tokens(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave488 CRadarWarningReceiver probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave488 CRadarWarningReceiver probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
