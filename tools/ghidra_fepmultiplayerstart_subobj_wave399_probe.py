#!/usr/bin/env python3
"""Validate the Wave399 FEPMultiplayerStart embedded-helper Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "fepmultiplayerstart-subobj-wave399" / "current"

COMMON_TAGS = {
    "static-reaudit",
    "fepmultiplayerstart-subobj-wave399",
    "frontend",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    instruction_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "instructionTokens": instruction_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00459810": target(
        "CFEPMultiplayerStart__SubObj39B8__QueuePageId",
        "void __thiscall CFEPMultiplayerStart__SubObj39B8__QueuePageId(void * this, int page_id)",
        ["Wave399", "SubObj39B8", "queues", "page id", "+0xc", "+0x10", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["+ 0xc", "+ 0x10", "page_id"],
        ["MOV dword ptr [ECX + 0xc], 0x1", "MOV dword ptr [ECX + 0x10], EAX", "RET 0x4"],
        ["queue-helper", "comment-hardened"],
        ["CFrontEnd__Init"],
    ),
    "0x00459920": target(
        "CFEPMultiplayerStart__SubObj8848__ctor",
        "void * __thiscall CFEPMultiplayerStart__SubObj8848__ctor(void * this)",
        ["Wave399", "SubObj8848", "constructor", "vtable 0x005db4fc", "zeros", "300-entry", "signature", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["PTR_CFEPMultiplayerStart__SubObj8848__Init_005db4fc", "300", "+ 0x345c"],
        ["MOV dword ptr [EDX], 0x5db4fc", "MOV dword ptr [EDX + 0x345c], 0x4", "RET"],
        ["constructor", "signature-corrected", "comment-hardened"],
        ["CFEPMultiplayerStart__ctor"],
    ),
    "0x004599a0": target(
        "CFEPMultiplayerStart__SubObj8848__Init",
        "int __thiscall CFEPMultiplayerStart__SubObj8848__Init(void * this)",
        ["Wave399", "vtable slot 0", "DAT_0089d94c", "selection row/column", "scroll target/offset", "timestamps", "signature", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["DAT_0089d94c", "+ 0x3468", "+ 0x346c", "PLATFORM__GetSysTimeFloat"],
        ["MOV ESI, ECX", "MOV dword ptr [ESI + 0x3468], 0x0", "RET"],
        ["vtable-slot-0", "init", "signature-corrected", "comment-hardened"],
        ["005db4fc"],
    ),
    "0x00459a60": target(
        "CFEPMultiplayerStart__SubObj8848__ActiveNotification",
        "void __thiscall CFEPMultiplayerStart__SubObj8848__ActiveNotification(void * this, int from_page)",
        ["Wave399", "active-notification", "pages 5/6", "selection highlight", "inactivity timer", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["from_page == 5", "+ 0x57c", "+ 0x347c"],
        ["RET 0x4"],
        ["active-notification", "comment-hardened"],
        ["005db518"],
    ),
    "0x00459aa0": target(
        "CFEPMultiplayerStart__SubObj8848__TransitionNotification",
        "void __thiscall CFEPMultiplayerStart__SubObj8848__TransitionNotification(void * this, int from_page)",
        ["Wave399", "transition-notification", "timestamp", "300-entry", "selection/highlight grid", "pages 5/6", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["PLATFORM__GetSysTimeFloat", "300", "+ 0x3478", "+ 0x57c"],
        ["RET 0x4"],
        ["transition-notification", "comment-hardened"],
        ["005db514"],
    ),
    "0x00459b00": target(
        "CFEPMultiplayerStart__SubObj8848__Process",
        "void __thiscall CFEPMultiplayerStart__SubObj8848__Process(void * this, int menu_state)",
        ["Wave399", "process hook", "scroll offset", "selection/highlight grid", "timeout", "page 0x0c", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["ABS", "+ 0x3460", "+ 0x57c", "CFrontEnd__SetPage"],
        ["RET 0x4"],
        ["process-hook", "comment-hardened"],
        ["005db504"],
    ),
    "0x00459c10": target(
        "CFEPMultiplayerStart__SubObj8848__ButtonPressed",
        "void __thiscall CFEPMultiplayerStart__SubObj8848__ButtonPressed(void * this, int button)",
        ["Wave399", "button handler", "horizontal", "vertical", "select/back", "DAT_0089d94c", "timestamp refreshes", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["switch(button)", "CFrontEnd__SetPage", "CFrontEnd__PlaySound", "DAT_0089d94c"],
        ["RET 0x8"],
        ["button-handler", "comment-hardened"],
        ["005db508"],
    ),
    "0x00459e50": target(
        "CFEPMultiplayerStart__SubObj8848__RenderPreCommon",
        "void __stdcall CFEPMultiplayerStart__SubObj8848__RenderPreCommon(float transition, int dest)",
        ["Wave399", "signature/comment correction", "RET 0x8", "transition", "no saved this use", "video quad", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["CFrontEnd__RenderVideoQuadScaledToWindow", "_DAT_005d85ec", "_DAT_005d8c70"],
        ["FLD float ptr [ESP + 0x4]", "RET 0x8"],
        ["render-precommon", "signature-corrected", "comment-hardened"],
        ["005db50c"],
    ),
    "0x00459ee0": target(
        "CFEPMultiplayerStart__SubObj8848__Render",
        "void __thiscall CFEPMultiplayerStart__SubObj8848__Render(void * this, float transition, int dest)",
        ["Wave399", "render hook", "selection grid", "level and episode text", "E3 2002", "title bar", "runtime multiplayer behavior", "source identity", "rebuild parity remain unproven"],
        ["FEPShared__RenderSelectionBrackets", "CFrontEnd__ResolveLevelNameTextByCode", "CFrontEnd__ResolveEpisodeNameTextByIndex", "E3_2002_Build", "CFrontEnd__DrawTitleBar"],
        ["CALL 0x00452fd0", "CALL 0x004681c0", "CALL 0x004681e0"],
        ["render-hook", "comment-hardened"],
        ["005db510"],
    ),
}

EXPECTED_VTABLE_SLOTS = {
    "0": "0x004599a0",
    "2": "0x00459b00",
    "3": "0x00459c10",
    "4": "0x00459e50",
    "5": "0x00459ee0",
    "6": "0x00459aa0",
    "7": "0x00459a60",
}

EXPECTED_DRY = {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 9, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime multiplayer behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
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


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "pointer_raw", "pointer_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "would_rename": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "would_rename": int(match.group(4)),
        "missing": int(match.group(5)),
        "bad": int(match.group(6)),
    }


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    metadata_rows = read_tsv(args.metadata)
    tags_rows = read_tsv(args.tags)
    xref_text = read_text(args.xrefs)
    instruction_text = read_text(args.instructions)
    vtable_rows = read_tsv(args.vtable_slots)
    public_note_text = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing or empty metadata: {args.metadata}")
    if not tags_rows:
        failures.append(f"missing or empty tags: {args.tags}")
    if not xref_text:
        failures.append(f"missing or empty xrefs: {args.xrefs}")
    if not instruction_text:
        failures.append(f"missing or empty instructions: {args.instructions}")
    if not vtable_rows:
        failures.append(f"missing or empty vtable slots: {args.vtable_slots}")
    if not public_note_text:
        failures.append(f"missing or empty public note: {args.public_note}")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: expected name {spec['name']}, got {row.get('name')}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: expected signature {spec['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present in comment: {token!r}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            for tag in spec["tags"]:  # type: ignore[index]
                if str(tag) not in tags:
                    failures.append(f"{address}: missing tag {tag!r}")

        decompile = decompile_text_for(args.decompile_dir, address)
        if not decompile:
            failures.append(f"{address}: missing decompile export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")
        for token in spec["instructionTokens"]:  # type: ignore[index]
            if not token_present(instruction_text, str(token)):
                failures.append(f"{address}: missing instruction token {token!r}")
        for token in spec["xrefTokens"]:  # type: ignore[index]
            if not token_present(xref_text, str(token)) and not token_present(read_text(args.vtable_slots), str(token)):
                failures.append(f"{address}: missing xref/vtable token {token!r}")

    for slot, address in EXPECTED_VTABLE_SLOTS.items():
        matches = [row for row in vtable_rows if row.get("slot_index") == slot]
        if not matches:
            failures.append(f"vtable slot {slot}: missing row")
            continue
        row = matches[0]
        if normalize_address(row.get("function_entry", "")) != normalize_address(address):
            failures.append(f"vtable slot {slot}: expected {address}, got {row.get('function_entry')}")
        expected_name = str(TARGETS[address]["name"])
        if row.get("function_name") != expected_name:
            failures.append(f"vtable slot {slot}: expected {expected_name}, got {row.get('function_name')}")

    for token in (
        "0x00459810",
        "0x00459920",
        "0x004599a0",
        "0x00459e50",
        "RenderPreCommon",
        "does not prove runtime multiplayer behavior",
        "does not prove exact source identity",
        "does not prove rebuild parity",
    ):
        if not token_present(public_note_text, token):
            failures.append(f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        if token_present(public_note_text, token):
            failures.append(f"public note overclaim token present: {token!r}")

    dry_summary = parse_summary(read_text(args.dry_log))
    apply_summary = parse_summary(read_text(args.apply_log))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, got {dry_summary}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, got {apply_summary}")
    if "REPORT: Save succeeded" not in read_text(args.apply_log):
        failures.append("apply log missing Ghidra save success")

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "checkedAtUtc": datetime.now(timezone.utc).isoformat(),
        "wave": "fepmultiplayerstart-subobj-wave399",
        "targets": len(TARGETS),
        "failures": failures,
    }
    return report, 0 if not failures else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate current Wave399 artifacts")
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_wide.tsv")
    parser.add_argument("--vtable-slots", type=Path, default=BASE / "vtable_slots.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_fepmultiplayerstart_subobj_wave399_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "ghidra-fepmultiplayerstart-subobj-wave399.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, status = validate(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']} ghidra_fepmultiplayerstart_subobj_wave399_probe targets={report['targets']} failures={len(report['failures'])}")
    if status != 0:
        for failure in report["failures"]:  # type: ignore[index]
            print(f"FAIL: {failure}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
