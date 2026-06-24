#!/usr/bin/env python3
"""Validate Wave454 CMusic static metadata hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave454-music-current"
COMMON_TAGS = {"static-reaudit", "music-wave454", "retail-binary-evidence"}
EXPECTED_APPLY = {
    "updated": 11,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 6,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 11,
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
    "0x004bb380": target(
        "CMusic__Init",
        "void __fastcall CMusic__Init(void * this)",
        ["device initialise", "CAREER_mMusicVolume", "0x7f", "queued-song", "runtime audio playback"],
        ["music", "initialization", "comment-hardened"],
        ["CMusic__Init", "CAREER_mMusicVolume", "s_input_vol"],
    ),
    "0x004bb400": target(
        "CMusic__Shutdown",
        "void __fastcall CMusic__Shutdown(void * this)",
        ["stops active playback", "device shutdown", "playlist entries", "+0x104", "runtime audio playback"],
        ["music", "shutdown", "playlist", "comment-hardened"],
        ["CMusic__Shutdown", "CDXMemoryManager__Free", "0x104"],
    ),
    "0x004bb450": target(
        "CMusic__Play",
        "void __thiscall CMusic__Play(void * this, char * filename)",
        ["filename", "ret 0x4", "DevicePlay", "mPlaying", "runtime audio playback"],
        ["music", "playback", "signature-corrected", "comment-hardened"],
        ["CMusic__Play", "char * filename", "filename"],
    ),
    "0x004bb490": target(
        "CMusic__Stop",
        "void __fastcall CMusic__Stop(void * this)",
        ["+0x08 mPlaying", "platform stop vfunc", "+0x0c", "playing flag", "runtime audio playback"],
        ["music", "stop", "comment-hardened"],
        ["CMusic__Stop", "+ 8", "+ 0xc"],
    ),
    "0x004bb4b0": target(
        "CMusic__FadeVolumes",
        "void __fastcall CMusic__FadeVolumes(void * this)",
        ["source-parity", "FadeVolumes", "steps current volume by 5", "queued song", "CMusic__PlayFromList"],
        ["music", "fade", "source-parity", "name-corrected", "comment-hardened"],
        ["CMusic__FadeVolumes", "CMusic__PlayFromList", "0x30"],
    ),
    "0x004bb530": target(
        "CMusic__UpdateStatus",
        "void __fastcall CMusic__UpdateStatus(void * this)",
        ["source-parity", "UpdateStatus", "track-finished modes", "1 linear playlist", "runtime audio playback"],
        ["music", "update", "source-parity", "name-corrected", "comment-hardened"],
        ["CMusic__UpdateStatus", "CMusic__FadeVolumes", "CMusic__PlaySelection", "s_data_music_BEA_08_Master"],
    ),
    "0x004bb6b0": target(
        "CMusic__AddToPlayList",
        "void __thiscall CMusic__AddToPlayList(void * this, char * track_path)",
        ["source-parity", "AddToPlayList", "sorted playlist insertion", "0x10c", "duplicate"],
        ["music", "playlist", "source-parity", "name-corrected", "comment-hardened"],
        ["CMusic__AddToPlayList", "OID__AllocObject", "s_Added__s_to_playlist"],
    ),
    "0x004bb7c0": target(
        "CMusic__LoadPlaylistFromDir",
        "void __thiscall CMusic__LoadPlaylistFromDir(void * this, char * directory_path)",
        ["directory_path", "DeviceAddDirectoryExts", "0x00630a04", "ret 0x4", "platform-specific extension"],
        ["music", "playlist", "signature-corrected", "comment-hardened"],
        ["CMusic__LoadPlaylistFromDir", "directory_path", "PTR_DAT_00630a04"],
    ),
    "0x004bb7e0": target(
        "CMusic__PlayFromList",
        "void __thiscall CMusic__PlayFromList(void * this, void * song_entry, int fade)",
        ["source-parity", "PlayFromList", "song_entry", "fade", "retail dev/all-cheats"],
        ["music", "playlist", "source-parity", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMusic__PlayFromList", "song_entry", "fade", "s_data_music_BEA_08_Master"],
    ),
    "0x004bb8c0": target(
        "CMusic__PlaySelection",
        "void __thiscall CMusic__PlaySelection(void * this, int music_selection, int fade)",
        ["source-parity", "PlaySelection", "music_selection", "Playing Track", "selection mode"],
        ["music", "selection", "source-parity", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMusic__PlaySelection", "music_selection", "DebugTrace", "s_Playing_Track"],
    ),
    "0x004bba10": target(
        "CMusic__SetVolume",
        "void __thiscall CMusic__SetVolume(void * this, float volume)",
        ["source-parity", "SetVolume", "linearly", "CAREER_mMusicVolume", "runtime audio loudness behavior"],
        ["music", "volume", "source-parity", "name-corrected", "comment-hardened"],
        ["CMusic__SetVolume", "float volume", "CAREER_mMusicVolume"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004bb380", "CLTShell__InitializeRuntimeAndLoadCoreResources"),
    ("0x004bb380", "CSoundManager__ReinitializeAfterDeviceLoss"),
    ("0x004bb400", "CLTShell__ShutdownRuntimeAndReleaseResources"),
    ("0x004bb400", "CSoundManager__ReinitializeAfterDeviceLoss"),
    ("0x004bb4b0", "CMusic__UpdateStatus"),
    ("0x004bb530", "CFrontEnd__Process"),
    ("0x004bb530", "CGame__MainLoop"),
    ("0x004bb530", "CGame__RollCredits"),
    ("0x004bb7c0", "PCPlatform__InitMusicPlaylist"),
    ("0x004bb7e0", "CMusic__FadeVolumes"),
    ("0x004bb8c0", "CMusic__UpdateStatus"),
    ("0x004bb8c0", "CGame__PlayMusicForCurrentLevel"),
    ("0x004bb8c0", "CFEPCredits__TransitionNotification"),
    ("0x004bba10", "CCareer__Load"),
]

INSTRUCTION_TOKENS = {
    "0x004bb380": ["CMusic__Init\tCALL\tdword ptr [EAX]", "CMusic__Init\tPUSH\t0x630a08", "CMusic__Init\tRET"],
    "0x004bb400": ["CMusic__Shutdown\tCALL\tdword ptr [EDX + 0x4]", "CMusic__Shutdown\tCALL\t0x00549220"],
    "0x004bb450": ["CMusic__Play\tCALL\tdword ptr [EAX + 0x8]", "CMusic__Play\tRET\t0x4"],
    "0x004bb490": ["CMusic__Stop\tCALL\tdword ptr [EAX + 0xc]", "CMusic__Stop\tRET"],
    "0x004bb4b0": ["CMusic__FadeVolumes\tCALL\t0x004bb7e0", "CMusic__FadeVolumes\tRET"],
    "0x004bb530": ["CMusic__UpdateStatus\tCALL\t0x004bb4b0", "CMusic__UpdateStatus\tCALL\t0x004bb8c0"],
    "0x004bb6b0": ["CMusic__AddToPlayList\tCALL\t0x0042b840", "CMusic__AddToPlayList\tRET\t0x4"],
    "0x004bb7c0": ["CMusic__LoadPlaylistFromDir\tPUSH\t0x630a04", "CMusic__LoadPlaylistFromDir\tRET\t0x4"],
    "0x004bb7e0": ["CMusic__PlayFromList\tMOV\tdword ptr [ESI + 0x4], 0x2", "CMusic__PlayFromList\tRET\t0x8"],
    "0x004bb8c0": ["CMusic__PlaySelection\tPUSH\t0x630a68", "CMusic__PlaySelection\tRET\t0x8"],
    "0x004bba10": ["CMusic__SetVolume\tFMUL\tfloat ptr [0x005dbc4c]", "CMusic__SetVolume\tRET\t0x4"],
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
                failures.append(f"{address}: overclaim token {token!r} in comment")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
            continue
        actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
        for tag in spec["tags"]:  # type: ignore[index]
            if str(tag) not in actual_tags:
                failures.append(f"{address}: missing tag {tag!r}")


def check_decompiles(base: Path, failures: list[str]) -> None:
    index_rows = read_tsv(base / "post-decomp" / "index.tsv")
    ok_rows = [row for row in index_rows if row.get("status") == "OK"]
    if len(ok_rows) != len(TARGETS):
        failures.append(f"post-decomp/index.tsv: expected {len(TARGETS)} OK rows, got {len(ok_rows)}")
    for address, spec in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post decompile text")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    edges = {(row.get("target_addr", ""), row.get("from_function", "")) for row in rows}
    for address, caller in EXPECTED_XREF_EDGES:
        if (normalize_address(address), caller) not in edges:
            failures.append(f"{address}: missing xref from {caller}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    text = "\n".join(
        "\t".join(
            [
                row.get("target_addr", ""),
                row.get("function_name", ""),
                row.get("mnemonic", ""),
                row.get("operands", ""),
                row.get("flow_type", ""),
            ]
        )
        for row in rows
    )
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if token not in text:
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path = BASE) -> tuple[str, list[str]]:
    failures: list[str] = []
    if not base.is_dir():
        failures.append(f"missing evidence directory: {base}")
        return "FAIL", failures
    check_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instructions(base, failures)
    return ("PASS" if not failures else "FAIL"), failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=str(BASE), help="Wave454 evidence directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    args = parser.parse_args(argv)

    base = Path(args.base)
    status, failures = run_checks(base)
    print(f"Wave454 Music probe: {status}")
    print(f"Base: {base}")
    print(f"Targets: {len(TARGETS)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
