#!/usr/bin/env python3
"""Validate the Wave397 HelpText/HiveBoss Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "help-hive-hud-wave397" / "current"

COMMON_TAGS = {"static-reaudit", "help-hive-wave397", "retail-binary-evidence"}


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
    "0x0047fab0": target(
        "CHelpTextDisplay__ctor",
        "void * __thiscall CHelpTextDisplay__ctor(void * this)",
        ["CHelpTextDisplay constructor", "two queued-message slots", "vtable", "allocated by CGame", "runtime HelpText behavior", "rebuild parity remain unproven"],
        ["PTR_CHelpTextDisplay__scalar_deleting_dtor_005dbdf8", "this", "return"],
        ["0x5dbdf8", "[EAX + 0xc]", "RET"],
        ["helptext", "constructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CGame__InitRestartLoop"],
    ),
    "0x0047fad0": target(
        "CHelpTextDisplay__scalar_deleting_dtor",
        "void * __thiscall CHelpTextDisplay__scalar_deleting_dtor(void * this, byte flags)",
        ["scalar deleting destructor", "HelpTextDisplay vtable", "flags bit 1", "OID allocator", "runtime HelpText behavior", "rebuild parity remain unproven"],
        ["PTR_CHelpTextDisplay__scalar_deleting_dtor_005dbdf8", "flags", "OID__FreeObject"],
        ["0x5dbdf8", "[ESP + 0x4]", "0x9c3df0", "RET 0x4"],
        ["helptext", "destructor", "function-boundary", "signature-corrected", "comment-hardened"],
        [],
    ),
    "0x0047fb00": target(
        "CHelpTextDisplay__QueueMessageWithTimestamp",
        "void __thiscall CHelpTextDisplay__QueueMessageWithTimestamp(void * this, void * message)",
        ["corrects the older CUnitAI owner label", "two queued-message slots", "global timestamp", "too many messages", "runtime HelpText behavior", "rebuild parity remain unproven"],
        ["DAT_00672fd0", "s_ERROR__Added_too_many_messages", "CConsole__Printf"],
        ["[0x00672fd0]", "RET 0x4"],
        ["helptext", "message-queue", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["00533b5d"],
    ),
    "0x0047fb50": target(
        "CHelpTextDisplay__RenderQueuedMessages",
        "void __fastcall CHelpTextDisplay__RenderQueuedMessages(void * this)",
        ["corrects the older CExplosionInitThing owner label", "two queued HelpText messages", "age/fade", "TextLayout__WrapWideTextToFixedLines", "runtime HelpText behavior", "rebuild parity remain unproven"],
        ["TextLayout__WrapWideTextToFixedLines", "CDXFont__DrawTextDynamic", "CAREER_mControllerConfig_P1"],
        ["[0x00672fd0]", "RET"],
        ["helptext", "rendering", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CExplosionInitThing__AccumulateOverlayMarkerFromViewpoint"],
    ),
    "0x0047fe30": target(
        "CHiveBoss__Init",
        "void __thiscall CHiveBoss__Init(void * this, void * init_data)",
        ["corrects the undefined saved signature", "core2", "destructable-segment controller", "guide object", "HiveBoss floats", "runtime HiveBoss behavior", "rebuild parity remain unproven"],
        ["CDestructableSegmentsController__Ctor", "CUnit__Init", "s_core2_0062cc90", "CGuide__ctor_base"],
        ["0x41200000", "0x41f00000", "RET 0x4"],
        ["hiveboss", "init", "signature-corrected", "comment-hardened"],
        ["005e1704"],
    ),
    "0x004804c0": target(
        "CHiveBoss__SetVar",
        "void __thiscall CHiveBoss__SetVar(void * this, void * name, void * data)",
        ["corrects the older CExplosionInitThing owner label", "hb_*", "config float fields", "falls back to the base SetVar", "runtime HiveBoss behavior", "rebuild parity remain unproven"],
        ["s_hb_maxvelx", "s_hb_rotate_speed", "s_hb_safe_dist", "CExplosionInitThing__InvokeAndWarnUnknownVar"],
        ["RET 0x8"],
        ["hiveboss", "setvar", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["005e17d8"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 5, "created": 0, "would_create": 1, "renamed": 0, "would_rename": 4, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 6, "skipped": 0, "created": 1, "would_create": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime helptext behavior proven",
    "runtime hiveboss behavior proven",
    "source identity proven",
    "concrete layout proven",
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
    public_note_text = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing or empty metadata: {args.metadata}")
    if not tags_rows:
        failures.append(f"missing or empty tags: {args.tags}")
    if not xref_text:
        failures.append(f"missing or empty xrefs: {args.xrefs}")
    if not instruction_text:
        failures.append(f"missing or empty instructions: {args.instructions}")
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

    for token in (
        "0x0047fab0",
        "0x0047fad0",
        "0x0047fb00",
        "0x0047fb50",
        "0x0047fe30",
        "0x004804c0",
        "CHelpTextDisplay__ctor",
        "CHelpTextDisplay__scalar_deleting_dtor",
        "CHelpTextDisplay__QueueMessageWithTimestamp",
        "CHelpTextDisplay__RenderQueuedMessages",
        "CHiveBoss__Init",
        "CHiveBoss__SetVar",
        "does not prove runtime HelpText behavior",
        "does not prove runtime HiveBoss behavior",
        "does not prove rebuild parity",
    ):
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
        "schema": "ghidra-help-hive-wave397.v1",
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
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_help_hive_wave397_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "help-hive-wave397.json")
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
