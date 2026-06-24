#!/usr/bin/env python3
"""Validate Wave450 MessageBox/portrait metadata hardening."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave450-messagebox-portrait-current"
COMMON_TAGS = {"static-reaudit", "messagebox-wave450", "retail-binary-evidence"}
EXPECTED_APPLY = {
    "updated": 17,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 10,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 17,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004b6f10": target(
        "CMessage__scalar_deleting_dtor",
        "void * __thiscall CMessage__scalar_deleting_dtor(void * this, byte flags)",
        ["scalar-deleting destructor", "ret 0x4", "one stack flags argument", "rebuild parity remain unproven"],
        ["message", "destructor", "scalar-deleting-dtor", "signature-corrected", "name-corrected", "comment-hardened"],
        ["CMessage__dtor_base", "CDXMemoryManager__Free", "flags"],
    ),
    "0x004b6f70": target(
        "CMessage__WordWrapToLineBuffer",
        "void __thiscall CMessage__WordWrapToLineBuffer(void * this, void * line_buffer, int max_chars_per_line, int max_visible_lines)",
        ["eight-line", "0x56-wide", "ret 0xc", "phantom fourth argument", "rebuild parity remain unproven"],
        ["message", "word-wrap", "wide-text", "signature-corrected", "comment-hardened"],
        ["line_buffer", "max_chars_per_line", "max_visible_lines", "WcsLen"],
    ),
    "0x004b7160": target(
        "CMessage__dtor_base",
        "void __fastcall CMessage__dtor_base(void * this)",
        ["base destructor", "CMonitor__Shutdown", "+0x30", "rebuild parity remain unproven"],
        ["message", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMonitor__Shutdown", "CSPtrSet__Remove"],
    ),
    "0x004b71e0": target(
        "CMessageBox__ctor_base",
        "void * __fastcall CMessageBox__ctor_base(void * this)",
        ["constructor", "CSPtrSet queue", "queue-advance flag", "returns this", "rebuild parity remain unproven"],
        ["messagebox", "constructor", "portrait", "queue", "name-corrected", "signature-corrected", "comment-hardened"],
        ["RandomSeedPair__Set", "CDXFont__GetTextExtent", "CGenericActiveReader__SetReader"],
    ),
    "0x004b7300": target(
        "CMessageBox__scalar_deleting_dtor",
        "void * __thiscall CMessageBox__scalar_deleting_dtor(void * this, byte flags)",
        ["scalar-deleting destructor", "CMessageBox__dtor_base", "ret 0x4", "rebuild parity remain unproven"],
        ["messagebox", "destructor", "scalar-deleting-dtor", "signature-corrected", "comment-hardened"],
        ["CMessageBox__dtor_base", "CDXMemoryManager__Free", "flags"],
    ),
    "0x004b7320": target(
        "CMessageBox__LoadPortraitTextures",
        "void __fastcall CMessageBox__LoadPortraitTextures(void * this)",
        ["portrait texture table", "MessageBox", "+0x16c", "rebuild parity remain unproven"],
        ["messagebox", "portrait", "textures", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CTexture__FindTexture", "MessageBox", "0x16c"],
    ),
    "0x004b7930": target(
        "CMessageBox__dtor_base",
        "void __fastcall CMessageBox__dtor_base(void * this)",
        ["base destructor", "13x6 portrait table", "active voice", "CMonitor__Shutdown", "rebuild parity remain unproven"],
        ["messagebox", "destructor", "portrait", "voice", "queue", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CHud__DecrementCounter9C", "CSPtrSet__Clear", "CMonitor__Shutdown"],
    ),
    "0x004b7ab0": target(
        "CMessageBox__SelectPortraitIndex",
        "int __thiscall CMessageBox__SelectPortraitIndex(void * this, void * message_text_wide)",
        ["portrait slot", "message_text_wide", "ret 0x4", "phantom second argument", "rebuild parity remain unproven"],
        ["messagebox", "portrait", "text", "name-corrected", "signature-corrected", "comment-hardened"],
        ["message_text_wide", "CText__GetStringById", "s_ERROR__no_portraits"],
    ),
    "0x004b7b60": target(
        "CMessageBox__RequestQueueAdvance",
        "void __fastcall CMessageBox__RequestQueueAdvance(void * this)",
        ["queue-advance flag", "+0x2c0", "tail-jumps", "rebuild parity remain unproven"],
        ["messagebox", "queue", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMessageBox__TryAdvanceQueuedMessage"],
    ),
    "0x004b7b70": target(
        "CMessageBox__ClearQueueAdvanceFlag",
        "void __fastcall CMessageBox__ClearQueueAdvanceFlag(void * this)",
        ["clears", "+0x2c0", "rebuild parity remain unproven"],
        ["messagebox", "queue", "name-corrected", "signature-corrected", "comment-hardened"],
        ["0x2c0"],
    ),
    "0x004b7b80": target(
        "CMessageBox__TryAdvanceQueuedMessage",
        "void __fastcall CMessageBox__TryAdvanceQueuedMessage(void * this)",
        ["queued-message list", "event 0xbbc", "0.2 seconds", "rebuild parity remain unproven"],
        ["messagebox", "queue", "portrait", "event-scheduling", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMessageBox__SelectPortraitIndex", "CEventManager__AddEvent_TimeFromNow", "0xbbc"],
    ),
    "0x004b7ca0": target(
        "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
        "void __thiscall CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance(void * this, void * queued_message)",
        ["queued_message", "sorted", "ret 0x4", "phantom second argument", "rebuild parity remain unproven"],
        ["messagebox", "queue", "script-audio", "name-corrected", "signature-corrected", "comment-hardened"],
        ["queued_message", "CSPtrSet__operator_assign", "CMessageBox__TryAdvanceQueuedMessage"],
    ),
    "0x004b7ea0": target(
        "CMessageBox__StartVoiceOrFallbackTextReveal",
        "void __fastcall CMessageBox__StartVoiceOrFallbackTextReveal(void * this)",
        ["voice playback", "falls back", "Bink", "rebuild parity remain unproven"],
        ["messagebox", "voice", "text-reveal", "signature-corrected", "comment-hardened"],
        ["CText__GetAudioNameById", "CBinkOpenThread__StartAsync", "CMessageBox__AdvanceRevealAndScheduleNextTick"],
    ),
    "0x004b8020": target(
        "CMessageBox__AdvanceRevealAndScheduleNextTick",
        "void __fastcall CMessageBox__AdvanceRevealAndScheduleNextTick(void * this)",
        ["reveal state", "event 3000", "event 0xbba", "rebuild parity remain unproven"],
        ["messagebox", "text-reveal", "voice", "event-scheduling", "signature-corrected", "comment-hardened"],
        ["WcsLen", "CEventManager__AddEvent_TimeFromNow", "CMessageBox__StopVoicePlaybackIfNotInCutscene"],
    ),
    "0x004b82a0": target(
        "CMessageLog__GetEntryField3CByIndex",
        "int __thiscall CMessageLog__GetEntryField3CByIndex(void * this, int entry_index)",
        ["entry_index", "+0x3c", "ret 0x4", "phantom second argument", "rebuild parity remain unproven"],
        ["messagelog", "accessor", "signature-corrected", "comment-hardened"],
        ["entry_index", "0x3c"],
    ),
    "0x004b82b0": target(
        "CDXEngine__RenderBattleLinePulseSprites",
        "void __thiscall CDXEngine__RenderBattleLinePulseSprites(void * this, int screen_x, float screen_y, int viewport_height)",
        ["battle-line pulse", "CVBufTexture__DrawSpriteEx", "ret 0xc", "phantom fourth argument", "rebuild parity remain unproven"],
        ["messagebox", "dxengine", "battleline", "render", "signature-corrected", "comment-hardened"],
        ["screen_x", "screen_y", "viewport_height", "CVBufTexture__DrawSpriteEx"],
    ),
    "0x004b8800": target(
        "CMessageBox__StopVoicePlaybackIfNotInCutscene",
        "void __fastcall CMessageBox__StopVoicePlaybackIfNotInCutscene(void * this)",
        ["cutscene gate", "active voice channel", "StopAndReleaseChannel", "rebuild parity remain unproven"],
        ["messagebox", "voice", "audio", "signature-corrected", "comment-hardened"],
        ["CMessageBox__StopAndReleaseChannel", "DAT_008073d0"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004b6f70", "CDXEngine__RenderMessageBoxOverlay"),
    ("0x004b6f70", "CMessageLog__RenderMessageCard"),
    ("0x004b7160", "CMessage__scalar_deleting_dtor"),
    ("0x004b7320", "CGame__RunLevel"),
    ("0x004b7930", "CMessageBox__scalar_deleting_dtor"),
    ("0x004b7ab0", "CMessageLog__RenderMessageCard"),
    ("0x004b7ab0", "CMessageBox__TryAdvanceQueuedMessage"),
    ("0x004b7b80", "CMessageBox__RequestQueueAdvance"),
    ("0x004b7ca0", "IScript__PlaySoundWithFadeAndPriority"),
    ("0x004b8020", "CMessageBox__StartVoiceOrFallbackTextReveal"),
    ("0x004b82a0", "CMessageLog__RenderMessageCard"),
    ("0x004b82b0", "CHud__RenderBattleline"),
    ("0x004b8800", "CDXEngine__RenderMessageBoxOverlay"),
    ("0x004b8800", "CMessageBox__AdvanceRevealAndScheduleNextTick"),
]

INSTRUCTION_TOKENS = {
    "0x004b6f10": ["CMessage__scalar_deleting_dtor\tRET\t0x4"],
    "0x004b6f70": ["CMessage__WordWrapToLineBuffer\tRET\t0xc"],
    "0x004b7300": ["CMessageBox__scalar_deleting_dtor\tRET\t0x4"],
    "0x004b7ab0": ["CMessageBox__SelectPortraitIndex\tRET\t0x4"],
    "0x004b7ca0": ["CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance\tRET\t0x4"],
    "0x004b82a0": ["CMessageLog__GetEntryField3CByIndex\tRET\t0x4"],
    "0x004b82b0": ["CDXEngine__RenderBattleLinePulseSprites\tRET\t0xc"],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_log(base: Path, filename: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / filename)
    if not text:
        failures.append(f"{filename}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{filename}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{filename}: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{filename}: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(metadata) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(metadata)}")
    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token in comment {token!r}")
        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
            continue
        actual_tags = {tag.strip() for tag in re.split(r"[;,]", tag_row.get("tags", "")) if tag.strip()}
        missing_tags = set(spec["tags"]) - actual_tags  # type: ignore[arg-type]
        if missing_tags:
            failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompiles(base: Path, failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post-decomp text")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    found = {(row.get("target_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in found:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_instruction_tokens(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions_full.tsv") or read_text(base / "post_instructions_xwide.tsv")
    if not text:
        failures.append("post_instructions_full.tsv/post_instructions_xwide.tsv: missing instruction export")
        return
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instruction_tokens(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave450 evidence directory")
    parser.add_argument("--check", action="store_true", help="Fail nonzero on validation failures")
    parser.add_argument("--json", type=Path, help="Optional JSON report path")
    args = parser.parse_args(argv)

    status, failures = run_checks(args.base)
    report = {
        "status": status,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": relative_or_absolute(args.base),
        "targetCount": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Wave450 MessageBox probe: {status}")
    print(f"Base: {relative_or_absolute(args.base)}")
    print(f"Targets: {len(TARGETS)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
