#!/usr/bin/env python3
"""Validate Wave480 audio-reset wrapper correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave480-engine-audio-reset-004cddf0"

TARGET_AUDIO = "0x004cddf0"
TARGET_SOUND = "0x00517f10"
OLD_AUDIO_NAME = "CEngine__RestoreAudioAfterDeviceReset"
NEW_AUDIO_NAME = "Audio__ReinitializeSoundAndRestoreMusic"
SOUND_NAME = "CSoundManager__ReinitializeAfterDeviceLoss"
EXPECTED_AUDIO_SIGNATURE = "void __cdecl Audio__ReinitializeSoundAndRestoreMusic(int frontend_music_after_reset)"
EXPECTED_SOUND_SIGNATURE = "void __thiscall CSoundManager__ReinitializeAfterDeviceLoss(void * this)"

EXPECTED_SUMMARIES = {
    "apply_audio_reset_wave480_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_audio_reset_wave480_apply.log": {
        "updated": 2,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_audio_reset_wave480_verify_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

EXPECTED_COMMON_TAGS = {
    "audio",
    "audio-reset-wave480",
    "comment-hardened",
    "music",
    "retail-binary-evidence",
    "signature-corrected",
    "sound-manager",
    "static-reaudit",
}

EXPECTED_METADATA = {
    TARGET_AUDIO: {
        "name": NEW_AUDIO_NAME,
        "signature": EXPECTED_AUDIO_SIGNATURE,
        "comment_tokens": [
            "not a CEngine instance method",
            "ECX=&DAT_00896988",
            "low byte of frontend_music_after_reset",
            "CMusic__PlaySelection(&DAT_00889a48, 0, 0)",
            "CGame__PlayMusicForCurrentLevel(&DAT_008a9a98)",
            "OptionsTail_Read",
            "raw config-change thunks",
            "function boundaries remain deferred",
            "runtime audio behavior",
            "rebuild parity remain unproven",
        ],
        "tags": EXPECTED_COMMON_TAGS | {"owner-corrected"},
        "decompile_tokens": [
            NEW_AUDIO_NAME,
            "int frontend_music_after_reset",
            "CSoundManager__ReinitializeAfterDeviceLoss(&DAT_00896988)",
            "(char)frontend_music_after_reset",
            "CMusic__PlaySelection(&DAT_00889a48,0,0)",
            "CGame__PlayMusicForCurrentLevel(&DAT_008a9a98)",
        ],
    },
    TARGET_SOUND: {
        "name": SOUND_NAME,
        "signature": EXPECTED_SOUND_SIGNATURE,
        "comment_tokens": [
            "callers load ECX with &DAT_00896988",
            "CSoundManager instance parameter",
            "stops streams",
            "shuts down global MUSIC",
            "reinitializes the PC sound device",
            "reloads the compressed sample bank",
            "Source CSoundManager::Reset partially aligns",
            "runtime audio behavior",
            "rebuild parity remain unproven",
        ],
        "tags": EXPECTED_COMMON_TAGS,
        "decompile_tokens": [
            SOUND_NAME,
            "void *this",
            "CSoundManager__StopAllStreams()",
            "CMusic__Shutdown(&DAT_00889a48)",
            "CSoundManager__ReleaseAllVoiceBuffers(this)",
            "CPCSoundManager__Init()",
            "CSoundManager__LoadCompressedSampleBank(this,'\\x01')",
            "CSoundManager__GetOrCreateSample",
        ],
    },
}

EXPECTED_XREFS = {
    (TARGET_AUDIO, "0x004211c9", "OptionsTail_Read"),
    (TARGET_SOUND, "0x004cddf5", NEW_AUDIO_NAME),
    (TARGET_SOUND, "0x004cf0a9", "<no_function>"),
    (TARGET_SOUND, "0x004cf139", "<no_function>"),
    (TARGET_SOUND, "0x004cf1a9", "<no_function>"),
    (TARGET_SOUND, "0x004cf259", "<no_function>"),
}

EXPECTED_POST_INSTRUCTIONS = {
    "0x004cddf0": ("MOV", "ECX, 0x896988"),
    "0x004cddf5": ("CALL", "0x00517f10"),
    "0x004cddfa": ("MOV", "AL, byte ptr [ESP + 0x4]"),
    "0x004cde14": ("CALL", "0x004bb8c0"),
    "0x004cde1f": ("JMP", "0x0046dc00"),
    "0x00517f11": ("MOV", "ESI, ECX"),
    "0x00517f22": ("CALL", "0x004e06b0"),
    "0x00517f2c": ("CALL", "0x004bb400"),
    "0x00517f42": ("CALL", "0x005171e0"),
    "0x00517f49": ("CALL", "0x005169b0"),
    "0x00517f69": ("CALL", "0x00517d00"),
}

EXPECTED_RAW_CALLS = {
    "0x004cf0a9": ("CALL", "0x00517f10"),
    "0x004cf0c5": ("CALL", "0x004bb8c0"),
    "0x004cf0d2": ("CALL", "0x0046dc00"),
    "0x004cf139": ("CALL", "0x00517f10"),
    "0x004cf155": ("CALL", "0x004bb8c0"),
    "0x004cf162": ("CALL", "0x0046dc00"),
    "0x004cf1a9": ("CALL", "0x00517f10"),
    "0x004cf1c5": ("CALL", "0x004bb8c0"),
    "0x004cf1d2": ("CALL", "0x0046dc00"),
    "0x004cf259": ("CALL", "0x00517f10"),
    "0x004cf275": ("CALL", "0x004bb8c0"),
    "0x004cf282": ("CALL", "0x0046dc00"),
}

OVERCLAIMS = (
    "runtime audio behavior proven",
    "exact source identity proven",
    "function boundaries proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
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


def check_summary(path: Path, expected: dict[str, int], label: str, failures: list[str]) -> None:
    actual = parse_summary(path)
    if actual != expected:
        failures.append(f"{label}: expected summary {expected}, got {actual or '<missing>'}")
    if "REPORT: Save succeeded" not in read_text(path):
        failures.append(f"{label}: missing REPORT: Save succeeded")


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def strip_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", text)


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, expected in EXPECTED_METADATA.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in EXPECTED_METADATA.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing tag row")
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = expected["tags"] - tags
        if missing:
            failures.append(f"{address}: missing tags {sorted(missing)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in EXPECTED_METADATA.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post-decompile file")
            continue
        for token in expected["decompile_tokens"]:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        code_text = strip_c_comments(text)
        for token in OVERCLAIMS:
            if token_present(code_text, token):
                failures.append(f"{address}: decompile code contains overclaim token {token!r}")
        if address == TARGET_AUDIO and token_present(code_text, OLD_AUDIO_NAME):
            failures.append(f"{address}: decompile still contains old name {OLD_AUDIO_NAME}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("from_function", ""))
        for row in rows
    }
    for expected in EXPECTED_XREFS:
        normalized = (normalize_address(expected[0]), normalize_address(expected[1]), expected[2])
        if normalized not in actual:
            failures.append(f"missing xref {normalized}")


def check_instruction_rows(path: Path, expected_rows: dict[str, tuple[str, str]], label: str, failures: list[str]) -> None:
    rows = read_tsv(path)
    by_addr = {row.get("instruction_addr"): row for row in rows}
    for address, (mnemonic, operands) in expected_rows.items():
        row = by_addr.get(normalize_address(address))
        if row is None:
            failures.append(f"{label}: missing instruction {address}")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(
                f"{label}: {address} expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}"
            )


def run(base: Path) -> list[str]:
    failures: list[str] = []
    for filename, expected in EXPECTED_SUMMARIES.items():
        check_summary(base / filename, expected, filename, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_instruction_rows(base / "post_instructions.tsv", EXPECTED_POST_INSTRUCTIONS, "post_instructions", failures)
    check_instruction_rows(base / "raw_audio_callsite_ranges.tsv", EXPECTED_RAW_CALLS, "raw_audio_callsite_ranges", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="Run checks and exit non-zero on failure.")
    args = parser.parse_args()

    failures = run(args.base)
    if failures:
        print("Wave480 audio-reset probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave480 audio-reset probe: PASS")
    print(f"Base: {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
