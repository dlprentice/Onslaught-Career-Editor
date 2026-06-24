#!/usr/bin/env python3
"""Validate the Wave406 CGame::IsMultiplayer Ghidra correction."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "range-check-wave406" / "current"
QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cgame_is_multiplayer_wave406_2026-05-14.md"
SOURCE_FILE = ROOT / "references" / "Onslaught" / "game.cpp"

ADDRESS = "0x004725d0"
OLD_NAME = "CExplosionInitThing__CheckValueRange_852_899"
EXPECTED_NAME = "CGame__IsMultiplayer"
EXPECTED_SIGNATURE = "int __thiscall CGame__IsMultiplayer(void * this)"
EXPECTED_TAGS = {
    "static-reaudit",
    "cgame-is-multiplayer-wave406",
    "game",
    "multiplayer",
    "cross-cutting-helper",
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
    "source-parity CGame::IsMultiplayer",
    "CGame+0x2a0",
    "850..899",
    "849 < level < 900",
    "CGame singleton &DAT_008a9a98",
    "sound, career, render",
    "HUD/compass/battleline",
    "runtime multiplayer behavior",
    "rebuild parity remain unproven",
)
DECOMPILE_TOKENS = (
    "int __thiscall CGame__IsMultiplayer(void *this)",
    "this + 0x2a0",
    "0x351",
    "< 900",
    "return 1",
    "return 0",
)
XREF_CALLERS = {
    ("0x0041bb29", "CCareer__DoesBaseThingExist"),
    ("0x0053e47b", "CDXEngine__Render"),
    ("0x00484c7a", "CExplosionInitThing__RenderTacticalRadarContacts"),
    ("0x0042727e", "CDXCompass__Render"),
    ("0x00405131", "CBattleEngine__Init"),
    ("0x004d106c", "CPauseMenu__InitPauseSession"),
    ("0x004e1422", "CSoundManager__UpdateSoundPosition"),
}
SOURCE_TOKENS = (
    "BOOL CGame::IsMultiplayer()",
    "mCurrentlyRunningLevel >849",
    "mCurrentlyRunningLevel < 900",
)
PUBLIC_NOTE_TOKENS = (
    ADDRESS,
    OLD_NAME,
    EXPECTED_NAME,
    EXPECTED_SIGNATURE,
    "Stuart source CGame::IsMultiplayer",
    "mCurrentlyRunningLevel >849",
    "mCurrentlyRunningLevel < 900",
    "850..899",
    "CGame+0x2a0",
    "CCareer__DoesBaseThingExist",
    "CDXEngine__Render",
    "CDXCompass__Render",
    "does not prove exact CGame field layout",
    "does not prove runtime multiplayer behavior",
    "does not prove rebuild parity",
)
OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime multiplayer behavior proven",
    "exact CGame field layout proven",
    "world-type semantics proven",
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
        if "param_1" not in before.get("signature", ""):
            failures.append(f"{ADDRESS} expected previous param_1 signature debt, found {before.get('signature')}")

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
    for from_addr, from_function in sorted(XREF_CALLERS):
        hit = [
            row
            for row in xrefs
            if normalize_address(row.get("target_addr", "")) == ADDRESS
            and normalize_address(row.get("from_addr", "")) == from_addr
            and row.get("from_function") == from_function
            and row.get("ref_type") == "UNCONDITIONAL_CALL"
        ]
        if len(hit) != 1:
            failures.append(f"{ADDRESS} expected one xref from {from_function} at {from_addr}, found {len(hit)}")

    decompile = decompile_text_for(base / "decompile_after", ADDRESS, EXPECTED_NAME)
    if not decompile:
        failures.append(f"{ADDRESS} missing decompile_after export")
    for token in DECOMPILE_TOKENS:
        if not token_present(decompile, token):
            failures.append(f"{ADDRESS} decompile missing token: {token}")

    source = read_text(root / SOURCE_FILE.relative_to(ROOT))
    for token in SOURCE_TOKENS:
        if not token_present(source, token):
            failures.append(f"source game.cpp missing token: {token}")

    dry = parse_summary(base / "apply_cgame_is_multiplayer_wave406_dry.log")
    apply = parse_summary(base / "apply_cgame_is_multiplayer_wave406_apply.log")
    if dry != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, found {dry}")
    if apply != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, found {apply}")
    dry_log = read_text(base / "apply_cgame_is_multiplayer_wave406_dry.log")
    apply_log = read_text(base / "apply_cgame_is_multiplayer_wave406_apply.log")
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
        if signals.get("commentlessFunctionCount") != 4469:
            failures.append(f"queue commentlessFunctionCount expected 4469, found {signals.get('commentlessFunctionCount')}")
        if signals.get("undefinedSignatureCount") != 1909:
            failures.append(f"queue undefinedSignatureCount expected 1909, found {signals.get('undefinedSignatureCount')}")
        if signals.get("paramSignatureCount") != 1857:
            failures.append(f"queue paramSignatureCount expected 1857, found {signals.get('paramSignatureCount')}")
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
        print("Ghidra Wave406 CGame::IsMultiplayer probe")
        print(f"Status: {result.status}")
        print(f"Address: {ADDRESS}")
        print(f"Name: {result.evidence.get('name')}")
        print(f"Signature: {result.evidence.get('signature')}")
        for failure in result.failures:
            print(f"- {failure}")
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
