#!/usr/bin/env python3
"""Validate the Wave405 CGame::DrawGameStuff Ghidra correction."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "frontend-cheatchecks-wave405" / "current"
QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cgame_draw_game_stuff_wave405_2026-05-14.md"

ADDRESS = "0x004714c0"
OLD_NAME = "FrontendUpdate_CheatChecks"
EXPECTED_NAME = "CGame__DrawGameStuff"
EXPECTED_SIGNATURE = "void __thiscall CGame__DrawGameStuff(void * this)"
EXPECTED_TAGS = {
    "static-reaudit",
    "cgame-draw-game-stuff-wave405",
    "game",
    "debug-overlay",
    "status-overlay",
    "game-over",
    "source-parity",
    "name-corrected",
    "signature-hardened",
    "comment-hardened",
    "retail-binary-evidence",
}
EXPECTED_DRY = {
    "updated": 0,
    "skipped": 1,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 1,
    "skipped": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

COMMENT_TOKENS = (
    "source-parity CGame::DrawGameStuff",
    "CDXEngine__PostRender",
    "CGame__DrawDebugStuff",
    "ECX=&DAT_008a9a98",
    "PC screenshot/selection key branch",
    "periodic FPS trace/status-buffer text",
    "developer/game status overlays",
    "Frontend__XorWideTextBlock100BytesToScratch",
    "console status-history rendering",
    "game-over/objective overlays",
    "runtime overlay behavior",
    "rebuild parity remain unproven",
)
DECOMPILE_TOKENS = (
    "void __thiscall CGame__DrawGameStuff(void *this)",
    "g_bDevModeEnabled",
    "g_bAllCheatsEnabled",
    "PlatformInput__ConsumeKeyOnce(0x42)",
    "CEngine__GrabScreenshot",
    "PCPlatform__GetFPS",
    "CConsole__AppendToStatusBufferV",
    "Frontend__XorWideTextBlock100BytesToScratch",
    "CConsole__RenderStatusHistoryOverlay",
    "CText__GetStringById",
)
CALLER_DECOMPILE_TOKENS = (
    "CGame__DrawDebugStuff(&DAT_008a9a98)",
    "CGame__DrawGameStuff(&DAT_008a9a98)",
)
INSTRUCTION_TOKENS = (
    "MOV\tEDI, ECX",
    "CALL\t0x00472240",
    "CALL\t0x00472270",
    "CALL\t0x004419e0",
)
CALLER_INSTRUCTION_TOKENS = (
    "MOV\tECX, 0x8a9a98",
    "CALL\t0x004714c0",
)
PUBLIC_NOTE_TOKENS = (
    ADDRESS,
    OLD_NAME,
    EXPECTED_NAME,
    EXPECTED_SIGNATURE,
    "Stuart source CGame::DrawGameStuff",
    "CDXEngine__PostRender",
    "0x0053ef9b",
    "DAT_008a9a98",
    "CGame__DrawDebugStuff",
    "Frontend__XorWideTextBlock100BytesToScratch",
    "CConsole__RenderStatusHistoryOverlay",
    "does not prove exact CGame layout",
    "does not prove runtime overlay behavior",
    "does not prove rebuild parity",
)
OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime overlay behavior proven",
    "exact CGame layout proven",
    "all cheat behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


@dataclass
class ValidationResult:
    status: str
    failures: list[str]
    evidence: dict[str, object]


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


def decompile_text_for(directory: Path, address: str, name: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_{name}.c"))
    if matches:
        return read_text(matches[0])
    fallback = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if fallback:
        return read_text(fallback[0])
    return ""


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def validate(root: Path = ROOT, base: Path = BASE) -> ValidationResult:
    failures: list[str] = []

    before = row_by_address(read_tsv(base / "metadata_before.tsv"), ADDRESS)
    if before is None:
        failures.append(f"{ADDRESS} missing metadata_before row")
    else:
        if before.get("name") != OLD_NAME:
            failures.append(f"{ADDRESS} expected previous name {OLD_NAME}, found {before.get('name')}")
        if not before.get("signature", "").startswith("undefined "):
            failures.append(f"{ADDRESS} expected previous undefined signature, found {before.get('signature')}")

    after = row_by_address(read_tsv(base / "metadata_after.tsv"), ADDRESS)
    if after is None:
        failures.append(f"{ADDRESS} missing metadata_after row")
    else:
        if after.get("name") != EXPECTED_NAME:
            failures.append(f"{ADDRESS} expected name {EXPECTED_NAME}, found {after.get('name')}")
        if after.get("signature") != EXPECTED_SIGNATURE:
            failures.append(f"{ADDRESS} expected signature {EXPECTED_SIGNATURE}, found {after.get('signature')}")
        comment = after.get("comment", "")
        for token in COMMENT_TOKENS:
            if not token_present(comment, token):
                failures.append(f"{ADDRESS} comment missing token: {token}")

    tags_row = row_by_address(read_tsv(base / "tags_after.tsv"), ADDRESS)
    if tags_row is None:
        failures.append(f"{ADDRESS} missing tags_after row")
    else:
        tags = {tag for tag in tags_row.get("tags", "").split(";") if tag}
        missing_tags = sorted(EXPECTED_TAGS - tags)
        if missing_tags:
            failures.append(f"{ADDRESS} missing tags: {', '.join(missing_tags)}")

    xrefs = read_tsv(base / "xrefs_after.tsv")
    post_render_call = [
        row
        for row in xrefs
        if normalize_address(row.get("target_addr", "")) == ADDRESS
        and normalize_address(row.get("from_addr", "")) == "0x0053ef9b"
        and row.get("from_function") == "CDXEngine__PostRender"
        and row.get("ref_type") == "UNCONDITIONAL_CALL"
    ]
    if len(post_render_call) != 1:
        failures.append(f"{ADDRESS} expected one CDXEngine__PostRender call xref at 0x0053ef9b, found {len(post_render_call)}")

    decompile = decompile_text_for(base / "decompile_after", ADDRESS, EXPECTED_NAME)
    if not decompile:
        failures.append(f"{ADDRESS} missing decompile_after export")
    for token in DECOMPILE_TOKENS:
        if not token_present(decompile, token):
            failures.append(f"{ADDRESS} decompile missing token: {token}")

    caller = decompile_text_for(base / "caller_decompile_after", "0x0053ecc0", "CDXEngine__PostRender")
    if not caller:
        failures.append("missing CDXEngine__PostRender caller_decompile_after export")
    for token in CALLER_DECOMPILE_TOKENS:
        if not token_present(caller, token):
            failures.append(f"caller decompile missing token: {token}")

    instruction_text = read_text(base / "instructions_after.tsv")
    for token in INSTRUCTION_TOKENS:
        if not token_present(instruction_text, token):
            failures.append(f"{ADDRESS} instructions missing token: {token}")

    caller_instruction_text = read_text(base / "caller_instructions_after.tsv")
    for token in CALLER_INSTRUCTION_TOKENS:
        if not token_present(caller_instruction_text, token):
            failures.append(f"caller instructions missing token: {token}")

    dry = parse_summary(base / "apply_cgame_draw_game_stuff_wave405_dry.log")
    apply = parse_summary(base / "apply_cgame_draw_game_stuff_wave405_apply.log")
    if dry != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, found {dry}")
    if apply != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, found {apply}")
    dry_log = read_text(base / "apply_cgame_draw_game_stuff_wave405_dry.log")
    apply_log = read_text(base / "apply_cgame_draw_game_stuff_wave405_apply.log")
    if "REPORT: Save succeeded" not in dry_log or "REPORT: Save succeeded" not in apply_log:
        failures.append("dry/apply logs must both include REPORT: Save succeeded")
    if "LockException" in dry_log or "LockException" in apply_log:
        failures.append("headless dry/apply log contains LockException")

    queue_path = root / QUEUE_REPORT.relative_to(ROOT)
    queue = {}
    if queue_path.is_file():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        signals = queue.get("qualitySignals", {})
        if queue.get("totalFunctions") != 6028:
            failures.append(f"queue totalFunctions expected 6028, found {queue.get('totalFunctions')}")
        if signals.get("commentlessFunctionCount") != 4470:
            failures.append(f"queue commentlessFunctionCount expected 4470, found {signals.get('commentlessFunctionCount')}")
        if signals.get("undefinedSignatureCount") != 1909:
            failures.append(f"queue undefinedSignatureCount expected 1909, found {signals.get('undefinedSignatureCount')}")
    else:
        failures.append(f"missing queue report: {queue_path}")

    note_path = root / PUBLIC_NOTE.relative_to(ROOT)
    note = read_text(note_path)
    for token in PUBLIC_NOTE_TOKENS:
        if not token_present(note, token):
            failures.append(f"public note missing token: {token}")
    lowered_note = note.lower()
    for token in OVERCLAIM_TOKENS:
        if token in lowered_note:
            failures.append(f"public note contains overclaim token: {token}")

    evidence = {
        "address": ADDRESS,
        "previousName": before.get("name") if before else None,
        "name": after.get("name") if after else None,
        "signature": after.get("signature") if after else None,
        "queue": {
            "totalFunctions": queue.get("totalFunctions"),
            "qualitySignals": queue.get("qualitySignals"),
            "nextHead": (queue.get("priorityQueues", {}).get("commentlessHighSignal", [None]) or [None])[0],
        },
    }
    return ValidationResult("PASS" if not failures else "FAIL", failures, evidence)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    result = validate()
    if args.json:
        print(json.dumps({"status": result.status, "failures": result.failures, "evidence": result.evidence}, indent=2))
    else:
        print("Ghidra Wave405 CGame::DrawGameStuff probe")
        print(f"Status: {result.status}")
        print(f"Address: {ADDRESS}")
        print(f"Name: {result.evidence.get('name')}")
        print(f"Signature: {result.evidence.get('signature')}")
        for failure in result.failures:
            print(f"- {failure}")
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
