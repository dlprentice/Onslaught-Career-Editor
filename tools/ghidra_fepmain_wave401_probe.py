#!/usr/bin/env python3
"""Validate the Wave401 CFEPMain Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "fepmain-wave401" / "current"

COMMON_TAGS = {"static-reaudit", "fepmain-wave401", "frontend", "retail-binary-evidence"}


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
    "0x004621b0": target(
        "CFEPMain__Init",
        "int __fastcall CFEPMain__Init(void * this)",
        ["seeds selection/timer state", "+0x14/+0x1c/+0x20", "CFEPMain vtable slice", "runtime frontend behavior", "rebuild parity remain unproven"],
        ["this + 0x14", "this + 0x1c", "return 1"],
        ["MOV\tdword ptr [ECX + 0x14], 0xbf800000", "MOV\tdword ptr [ECX + 0x1c], EAX"],
        ["fepmain", "init", "comment-hardened"],
        ["005dbae4", "005db7a8"],
    ),
    "0x004621d0": target(
        "CFEPMain__GetMenuType",
        "int __cdecl CFEPMain__GetMenuType(void)",
        ["no-argument menu-type getter", "returns constant 7", "exact source identity", "runtime frontend behavior", "rebuild parity remain unproven"],
        ["return 7"],
        ["MOV\tEAX, 0x7"],
        ["fepmain", "menu-type", "signature-corrected", "comment-hardened"],
        ["005dbb0c"],
    ),
    "0x004621e0": target(
        "CFEPMain__GetActionCount",
        "int __stdcall CFEPMain__GetActionCount(int menu_state)",
        ["stack-only menu_state switch", "career-in-progress gating", "controller-count gating", "memory-card/dialog flag", "default zero", "runtime frontend behavior", "rebuild parity remain unproven"],
        ["menu_state", "CAREER_mCareerInProgress", "CFrontEnd__NumControllersPresent", "return 1"],
        ["MOV\tEAX, dword ptr [ESP + 0x4]", "MOV\tEAX, [0x00662aa8]", "RET\t0x4"],
        ["fepmain", "action-count", "signature-corrected", "comment-hardened"],
        ["005dbb08"],
    ),
    "0x00462250": target(
        "CFEPMain__ButtonPressed",
        "void __thiscall CFEPMain__ButtonPressed(void * this, int button, float val)",
        ["button handler", "0x2a/0x2b/0x2c/0x36/0x37", "+0x8/+0xc/+0x14/+0x18/+0x1c/+0x20", "language-cycling", "runtime input behavior", "rebuild parity remain unproven"],
        ["switch(button)", "g_UseAmericanEnglish", "CFrontEnd__SetLanguage", "CFrontEnd__PlaySound"],
        ["MOV\tEAX, dword ptr [ESP + 0x4]", "MOV\tESI, ECX", "MOV\tdword ptr [ESI + 0x8], EDX"],
        ["fepmain", "input", "comment-hardened"],
        ["005dbaf0", "005db7b4"],
    ),
    "0x004623e0": target(
        "CFEPMain__DoAction",
        "void __fastcall CFEPMain__DoAction(void * this)",
        ["action handler", "New Game/Continue/Load/Options/Multiplayer/Goodies/Credits/Return", "DAT_0089d94c", "FEPMain.cpp is absent", "runtime frontend behavior", "rebuild parity remain unproven"],
        ["CCareer__Blank", "CFEPOptions__EnumerateSaveFiles", "CFEPDevelopment__RefreshWorldList", "CFrontEnd__SetPage", "CFEPSaveGame__InitDialogAndLayoutState"],
        ["CALL\t0x0041b7c0", "CALL\t0x0051fff0", "MOV\tdword ptr [0x008a968c], 0x7"],
        ["fepmain", "action", "comment-hardened", "source-boundary"],
        ["005dbb10", "CFEPDemoMain__DoAction"],
    ),
    "0x00462640": target(
        "CFEPMain__Process",
        "void __thiscall CFEPMain__Process(void * this, int state)",
        ["process loop", "career nodes 800/0x2e5", "CCareer__Save", "CFEPOptions__WriteDefaultOptionsFile", "debug-path allocation", "runtime save/frontend behavior", "rebuild parity remain unproven"],
        ["CCareer__GetNodeFromWorld", "OID__AllocObject", "s_C__dev_ONSLAUGHT2_FEPMain_cpp_00629414", "CFEPOptions__WriteDefaultOptionsFile"],
        ["PUSH\t0x320", "PUSH\t0x2e5", "CALL\t0x0041b8f0"],
        ["fepmain", "process", "comment-hardened"],
        ["005dbaec", "005db7b0"],
    ),
    "0x00462b70": target(
        "CFEPMain__RenderPreCommon",
        "void __stdcall CFEPMain__RenderPreCommon(float transition, int dest)",
        ["stack-only transition/dest helper", "dest 0x0c", "front-end video fade values", "shared main-menu pre-render layer", "runtime rendering behavior", "rebuild parity remain unproven"],
        ["CFrontEnd__RenderVideoQuadScaledToWindow", "PLATFORM__GetWindowWidth", "PLATFORM__GetWindowHeight"],
        ["CMP\tdword ptr [ESP + 0x18], 0xc", "CALL\t0x00452ce0"],
        ["fepmain", "render-precommon", "signature-corrected", "comment-hardened"],
        ["005dbaf4", "005db7b8"],
    ),
    "0x00462c90": target(
        "CFEPMain__Update",
        "void __stdcall CFEPMain__Update(int menu_state)",
        ["stack-only menu_state helper", "FrontEndText token lookups", "0,1,2,4,5,6,3", "fallback 8", "runtime localization behavior", "rebuild parity remain unproven"],
        ["FrontEndText__GetLocalizedOrFallbackTextByToken(0)", "FrontEndText__GetLocalizedOrFallbackTextByToken(8)", "FrontEndText__GetLocalizedOrFallbackTextByToken(3)"],
        ["MOV\tEAX, dword ptr [ESP + 0x4]", "RET\t0x4"],
        ["fepmain", "localization", "signature-corrected", "comment-hardened"],
        ["005dbb14"],
    ),
    "0x00462d40": target(
        "CFEPMain__Render",
        "void __thiscall CFEPMain__Render(void * this, float transition, int dest)",
        ["main render path", "+0x8 selection state", "transition/dest arguments", "language arrows/pulse state", "runtime rendering behavior", "rebuild parity remain unproven"],
        ["g_UseAmericanEnglish", "CDXSurf__RenderSurface", "CFrontEnd__GetClickStateInRect"],
        ["MOV\tESI, ECX", "CALL\t0x005563d0"],
        ["fepmain", "render", "comment-hardened"],
        ["005dbaf8", "005db7bc"],
    ),
    "0x004644d0": target(
        "CFEPMain__TransitionNotification",
        "void __fastcall CFEPMain__TransitionNotification(void * this, int from)",
        ["transition hook", "+0x14 to -1.0", "PLATFORM time", "CAREER_mCareerInProgress", "mirrors selection", "runtime transition behavior", "rebuild parity remain unproven"],
        ["PLATFORM__GetSysTimeFloat", "CAREER_mCareerInProgress", "this + 0x10"],
        ["MOV\tdword ptr [ECX + 0x14], 0xbf800000", "RET\t0x4"],
        ["fepmain", "transition", "comment-hardened"],
        ["005dbafc", "005db7c0"],
    ),
    "0x00464520": target(
        "CFEPMain__ActiveNotification",
        "void __fastcall CFEPMain__ActiveNotification(void * this, int from_page)",
        ["active-notification hook", "clears +0x14 and +0x18", "ignored page argument", "runtime activation behavior", "rebuild parity remain unproven"],
        ["this + 0x14", "this + 0x18"],
        ["XOR\tEAX, EAX", "MOV\tdword ptr [ECX + 0x14], EAX", "RET\t0x4"],
        ["fepmain", "active-notification", "comment-hardened"],
        ["005dbb00", "005db7c4"],
    ),
}

EXPECTED_VTABLE_TOKENS = (
    "005dbae4\t0\t005dbae4\t0x004621b0",
    "005dbae4\t2\t005dbaec\t0x00462640",
    "005dbae4\t3\t005dbaf0\t0x00462250",
    "005dbae4\t7\t005dbb00\t0x00464520",
    "005dbae4\t11\t005dbb10\t0x004623e0",
    "005dbaf0\t0\t005dbaf0\t0x00462250",
    "005dbaf0\t4\t005dbb00\t0x00464520",
)

EXPECTED_PUBLIC_NOTE_TOKENS = (
    "0x004621b0",
    "0x004621d0",
    "0x004621e0",
    "0x00462250",
    "0x004623e0",
    "0x00462640",
    "0x00462b70",
    "0x00462c90",
    "0x00462d40",
    "0x004644d0",
    "0x00464520",
    "CFEPMain__Init",
    "CFEPMain__GetMenuType",
    "CFEPMain__GetActionCount",
    "CFEPMain__ButtonPressed",
    "CFEPMain__DoAction",
    "CFEPMain__Process",
    "CFEPMain__RenderPreCommon",
    "CFEPMain__Update",
    "CFEPMain__Render",
    "CFEPMain__TransitionNotification",
    "CFEPMain__ActiveNotification",
    "0x005dbae4",
    "0x005dbaf0 starts with CFEPMain__ButtonPressed",
    "0x005dbb00 points to CFEPMain__ActiveNotification",
    "FEPMain.cpp is absent from the current Stuart source snapshot",
    "does not prove runtime frontend behavior",
    "does not prove exact source identity",
    "does not prove rebuild parity",
)

EXPECTED_DRY = {"updated": 0, "skipped": 11, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 11, "skipped": 0, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime frontend behavior proven",
    "runtime input behavior proven",
    "runtime rendering behavior proven",
    "source identity proven",
    "exact source identity proven",
    "concrete cfepmain layout proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
    "0x005dbaf0 starts with CFEPMain__Process",
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "entry_addr"):
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
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {
            "updated": -1,
            "skipped": -1,
            "created": -1,
            "would_create": -1,
            "renamed": -1,
            "would_rename": -1,
            "missing": -1,
            "bad": -1,
        }
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "created": int(match.group(3)),
        "would_create": int(match.group(4)),
        "renamed": int(match.group(5)),
        "would_rename": int(match.group(6)),
        "missing": int(match.group(7)),
        "bad": int(match.group(8)),
    }


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    metadata_rows = read_tsv(args.metadata)
    tags_rows = read_tsv(args.tags)
    xref_text = read_text(args.xrefs)
    instruction_text = read_text(args.instructions)
    vtable_text = read_text(args.vtables)
    public_note_text = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing or empty metadata: {args.metadata}")
    if not tags_rows:
        failures.append(f"missing or empty tags: {args.tags}")
    if not xref_text:
        failures.append(f"missing or empty xrefs: {args.xrefs}")
    if not instruction_text:
        failures.append(f"missing or empty instructions: {args.instructions}")
    if not vtable_text:
        failures.append(f"missing or empty vtables: {args.vtables}")
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
            if not token_present(xref_text, str(token)):
                failures.append(f"{address}: missing xref token {token!r}")

    for token in EXPECTED_VTABLE_TOKENS:
        if not token_present(vtable_text, token):
            failures.append(f"vtable export missing token {token!r}")

    for token in EXPECTED_PUBLIC_NOTE_TOKENS:
        if not token_present(public_note_text, token):
            failures.append(f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        if token_present(public_note_text, token):
            failures.append(f"public note overclaim token present: {token!r}")

    dry_summary = parse_summary(read_text(args.dry_log))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, got {dry_summary}")
    apply_log_text = read_text(args.apply_log)
    apply_summary = parse_summary(apply_log_text)
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, got {apply_summary}")
    if "REPORT: Save succeeded" not in apply_log_text:
        failures.append("apply log missing REPORT: Save succeeded")

    report = {
        "schema": "ghidra-fepmain-wave401.v1",
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targets": len(TARGETS),
        "failures": failures,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
    }
    return report, 0 if not failures else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_after.tsv")
    parser.add_argument("--vtables", type=Path, default=BASE / "vtable_slots_combined_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_fepmain_wave401_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "fepmain-wave401.json")
    parser.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report, status = validate(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        print(f"status={report['status']} targets={report['targets']} failures={len(report['failures'])} out={args.out}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
