#!/usr/bin/env python3
"""Validate Wave500 CSoundManager event-lifecycle static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave500-csoundmanager-events-004e0f70"

COMMON_TAGS = {
    "audio",
    "comment-hardened",
    "csoundmanager-wave500",
    "retail-binary-evidence",
    "signature-corrected",
    "sound-event",
    "sound-manager",
    "static-reaudit",
}


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004e0f70": target(
        "CSoundManager__StopSoundEvent",
        "void __stdcall CSoundManager__StopSoundEvent(void * sound_event, int block_until_stopped)",
        (
            "RET 0x8",
            "not a hidden CSoundManager this parameter",
            "SampleFinishedPlaying",
            "CSoundManager__StopAndReleaseChannel(&DAT_00896988, sound_event, block_until_stopped)",
            "clears mPlaying",
            "clears the active reader",
            "runtime audio behavior",
            "rebuild parity remain unproven",
        ),
        {"event-stop", "active-reader"},
        (
            "void CSoundManager__StopSoundEvent(void *sound_event,int block_until_stopped)",
            "sound_event + 0x7c",
            "CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event)",
            "CGenericActiveReader__SetReader(sound_event,(void *)0x0)",
        ),
    ),
    "0x004e0fb0": target(
        "CSoundManager__AllocateSoundEvent",
        "void * __thiscall CSoundManager__AllocateSoundEvent(void * this, int insert_at_top)",
        (
            "CSoundManager::GetSoundEvent(BOOL insertattop)",
            "pool at this+0x34",
            "mFirstSoundEvent at this+0x0c",
            "currently channel-assigned events",
            "event count at this+0x08",
            "out-of-sound-events DebugTrace",
            "runtime allocation behavior",
            "rebuild parity remain unproven",
        ),
        {"event-pool", "source-parity"},
        (
            "void * __thiscall CSoundManager__AllocateSoundEvent(void *this,int insert_at_top)",
            "this + 0x34",
            "insert_at_top == 0",
            "DebugTrace(s_Warning___out_of_sound_events__006324d8)",
            "return pvVar1",
        ),
    ),
    "0x004e1040": target(
        "CSoundManager__SortEventList",
        "void __thiscall CSoundManager__SortEventList(void * this)",
        (
            "CSoundManager::SortEventList",
            "bubble-sorts active events",
            "current attenuated volume at +0x68",
            "three-quarter channel budget",
            "DAT_00896c54",
            "CSoundManager__PlaySoundOnChannel",
            "runtime mixing behavior",
            "rebuild parity remain unproven",
        ),
        {"event-sort", "channel-budget", "source-parity"},
        (
            "void __thiscall CSoundManager__SortEventList(void *this)",
            "DAT_00896c54",
            "CSoundManager__StopAndReleaseChannel(&DAT_00896988,pvVar4)",
            "CSoundManager__FindFreeChannel(&DAT_00896988)",
            "CSoundManager__PlaySoundOnChannel(&DAT_00896988,pvVar4)",
        ),
    ),
    "0x004e1130": target(
        "CSoundManager__KillSamplesForThing",
        "void __thiscall CSoundManager__KillSamplesForThing(void * this, void * owner)",
        (
            "CSoundManager::KillSamplesForThing",
            "active-reader owner equals owner",
            "block_until_stopped=0",
            "active-reader clear",
            "runtime audio behavior",
            "rebuild parity remain unproven",
        ),
        {"event-stop", "owner-filter", "source-parity"},
        (
            "void __thiscall CSoundManager__KillSamplesForThing(void *this,void *owner)",
            "sound_event = *(int **)((int)this + 0xc)",
            "piVar1 == owner",
            "CGenericActiveReader__SetReader(sound_event,(void *)0x0)",
        ),
    ),
    "0x004e1190": target(
        "CSoundManager__KillSample",
        "void __thiscall CSoundManager__KillSample(void * this, void * owner, void * sample)",
        (
            "CSoundManager::KillSample",
            "owner active-reader plus sample pointer",
            "block_until_stopped=0",
            "runtime audio behavior",
            "rebuild parity remain unproven",
        ),
        {"event-stop", "owner-filter", "sample-filter", "source-parity"},
        (
            "void __thiscall CSoundManager__KillSample(void *this,void *owner,void *sample)",
            "piVar1 == owner",
            "(void *)sound_event[3] == sample",
            "CGenericActiveReader__SetReader(sound_event,(void *)0x0)",
        ),
    ),
    "0x004e12b0": target(
        "CSoundManager__KillAllSamples",
        "void __thiscall CSoundManager__KillAllSamples(void * this)",
        (
            "CSoundManager::KillAllSamples",
            "active sound-event list",
            "owner-complete callbacks",
            "block_until_stopped=0",
            "clears each event's active reader",
            "runtime audio behavior",
            "rebuild parity remain unproven",
        ),
        {"event-stop", "bulk-stop", "source-parity"},
        (
            "void __thiscall CSoundManager__KillAllSamples(void *this)",
            "sound_event = *(int **)((int)this + 0xc)",
            "CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event)",
            "CGenericActiveReader__SetReader(sound_event,(void *)0x0)",
        ),
    ),
    "0x004e1300": target(
        "CSoundManager__PauseAllSamples",
        "void __thiscall CSoundManager__PauseAllSamples(void * this)",
        (
            "CSoundManager::PauseAllSamples",
            "retail body is documented by the binary",
            "CSoundManager__StopChannel(&DAT_00896988, sound_event)",
            "paused flag at +0x84",
            "runtime pause behavior",
            "rebuild parity remain unproven",
        ),
        {"pause", "channel-state", "source-parity"},
        (
            "void __thiscall CSoundManager__PauseAllSamples(void *this)",
            "CSoundManager__StopChannel(&DAT_00896988,sound_event)",
            "sound_event + 0x84",
        ),
    ),
    "0x004e1330": target(
        "CSoundManager__UnPauseAllSamples",
        "void __thiscall CSoundManager__UnPauseAllSamples(void * this)",
        (
            "CSoundManager::UnPauseAllSamples",
            "retail body is documented by the binary",
            "CSoundManager__UpdateChannelLooping(&DAT_00896988, sound_event)",
            "paused flag at +0x84",
            "runtime unpause behavior",
            "rebuild parity remain unproven",
        ),
        {"pause", "channel-state", "source-parity"},
        (
            "void __thiscall CSoundManager__UnPauseAllSamples(void *this)",
            "CSoundManager__UpdateChannelLooping(&DAT_00896988,sound_event)",
            "sound_event + 0x84",
        ),
    ),
    "0x004e1360": target(
        "CSoundManager__UpdateSoundPosition",
        "void __stdcall CSoundManager__UpdateSoundPosition(void * sound_event, int first_time)",
        (
            "no hidden CSoundManager this parameter",
            "CSoundManager::UpdateSoundPosition(CSoundEvent *se, BOOL firsttime)",
            "game camera 0/1",
            "nearest multiplayer camera frame",
            "g_InvertXAxisFlag",
            "recalculates pan for followed owners",
            "runtime 3D audio behavior",
            "rebuild parity remain unproven",
        ),
        {"positioning", "tracking", "camera", "source-parity"},
        (
            "void CSoundManager__UpdateSoundPosition(void *sound_event,int first_time)",
            "CGame__GetCamera(&DAT_008a9a98,0)",
            "CGame__IsMultiplayer(&DAT_008a9a98)",
            "g_InvertXAxisFlag",
            "first_time == 0",
        ),
    ),
    "0x004e18d0": target(
        "CSoundManager__SetPitch",
        "void __thiscall CSoundManager__SetPitch(void * this, void * sound_event, float desired_pitch_factor, float fade_time_seconds)",
        (
            "CSoundManager::SetPitch",
            "desired_pitch_factor at event+0x3c",
            "round(fade_time_seconds * 20.0)",
            "event+0x40",
            "runtime pitch behavior",
            "rebuild parity remain unproven",
        ),
        {"pitch", "source-parity"},
        (
            "void *this,void *sound_event,float desired_pitch_factor,float fade_time_seconds",
            "fade_time_seconds * _DAT_005d857c",
            "sound_event + 0x3c",
            "desired_pitch_factor",
            "sound_event + 0x40",
        ),
    ),
}

XREF_EXPECTATIONS = (
    ("0x004e0f70", "0x00517c31", "CSoundManager__UpdateChannelParams", "UNCONDITIONAL_CALL"),
    ("0x004e0f70", "0x004dffe1", "CSample__VFunc_00_004dffc0", "UNCONDITIONAL_CALL"),
    ("0x004e0fb0", "0x004e0bfd", "CSoundManager__PlaySound", "UNCONDITIONAL_CALL"),
    ("0x004e1040", "0x004e1c15", "CSoundManager__UpdateStatus", "UNCONDITIONAL_CALL"),
    ("0x004e1130", "0x004fd153", "CUnit__MarkDestroyedAndCleanupLinks", "UNCONDITIONAL_CALL"),
    ("0x004e1130", "0x0044cbe9", "CFeature__ShutdownAndRemoveFromWorld", "UNCONDITIONAL_CALL"),
    ("0x004e1130", "0x0047e6e9", "CHazard__VFunc02_CleanupWorldSoundAndLinkedState", "UNCONDITIONAL_CALL"),
    ("0x004e1190", "0x004fb1eb", "CUnit__UpdateMotionAttachmentsAndEffects", "UNCONDITIONAL_CALL"),
    ("0x004e12b0", "0x0046e19f", "CGame__RestartLoopRunLevel", "UNCONDITIONAL_CALL"),
    ("0x004e12b0", "0x0043f9b7", "CCutscene__Update", "UNCONDITIONAL_CALL"),
    ("0x004e1300", "0x0046ec46", "CGame__Update", "UNCONDITIONAL_CALL"),
    ("0x004e1330", "0x0046ec22", "CGame__Update", "UNCONDITIONAL_CALL"),
    ("0x004e1360", "0x004e0d68", "CSoundManager__PlaySound", "UNCONDITIONAL_CALL"),
    ("0x004e1360", "0x004e1c68", "CSoundManager__UpdateStatus", "UNCONDITIONAL_CALL"),
    ("0x004e1360", "0x00517909", "CSoundManager__PlaySoundOnChannel", "UNCONDITIONAL_CALL"),
    ("0x004e18d0", "0x00408d22", "CMonitor__Process", "UNCONDITIONAL_CALL"),
)

INSTRUCTION_EXPECTATIONS = (
    ("0x004e0fac", "CSoundManager__StopSoundEvent", "RET", "0x8"),
    ("0x004e0f8e", "CSoundManager__StopSoundEvent", "MOV", "ECX, dword ptr [ESP + 0xc]"),
    ("0x004e101f", "CSoundManager__AllocateSoundEvent", "RET", "0x4"),
    ("0x004e112c", "CSoundManager__SortEventList", "RET", ""),
    ("0x004e1184", "CSoundManager__KillSamplesForThing", "RET", "0x4"),
    ("0x004e11ef", "CSoundManager__KillSample", "RET", "0x8"),
    ("0x004e12f3", "CSoundManager__KillAllSamples", "RET", ""),
    ("0x004e132b", "CSoundManager__PauseAllSamples", "RET", ""),
    ("0x004e135b", "CSoundManager__UnPauseAllSamples", "RET", ""),
    ("0x004e1901", "CSoundManager__SetPitch", "RET", "0xc"),
)

EXPECTED_LOG_SUMMARIES = {
    "apply_csoundmanager_events_wave500_dry.log": {
        "updated": 0,
        "skipped": 10,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_csoundmanager_events_wave500_apply.log": {
        "updated": 10,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_csoundmanager_events_wave500_final_verify_dry.log": {
        "updated": 0,
        "skipped": 10,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

OVERCLAIM_TOKENS = (
    "runtime audio behavior proven",
    "runtime 3D audio behavior proven",
    "runtime pause behavior proven",
    "runtime pitch behavior proven",
    "exact layout proven",
    "exact CSoundEvent layout proven",
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


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing TSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def read_text(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def require_token(text: str, token: str, label: str) -> None:
    if not token_present(text, token):
        raise AssertionError(f"{label} missing token: {token}")


def decompile_text(base: Path, address: str, expected_name: str) -> str:
    stem = normalize_address(address)[2:]
    decomp_dir = base / "post-decomp"
    preferred = sorted(decomp_dir.glob(f"{stem}_{expected_name}*.c"))
    candidates = preferred or sorted(decomp_dir.glob(f"{stem}_*.c"))
    if not candidates:
        raise AssertionError(f"missing post-decompile for {address}")
    return read_text(candidates[0])


def check_metadata(base: Path) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            raise AssertionError(f"missing metadata row for {address}")
        if row["status"] != "OK":
            raise AssertionError(f"{address} metadata status {row['status']}")
        if row["name"] != spec["name"]:
            raise AssertionError(f"{address} name {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            raise AssertionError(f"{address} signature {row['signature']} != {spec['signature']}")
        comment = row["comment"]
        for token in spec["comment_tokens"]:
            require_token(comment, str(token), f"{address} comment")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                raise AssertionError(f"{address} overclaim token present: {token}")


def check_tags(base: Path) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            raise AssertionError(f"missing tag row for {address}")
        tags = {tag for tag in row["tags"].split(";") if tag}
        missing = sorted(spec["tags"] - tags)
        if missing:
            raise AssertionError(f"{address} missing tags: {missing}")


def check_decompiles(base: Path) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text(base, address, str(spec["name"]))
        for token in spec["decompile_tokens"]:
            require_token(text, str(token), f"{address} decompile")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for target, from_addr, from_function, ref_type in XREF_EXPECTATIONS:
        found = any(
            row["target_addr"] == normalize_address(target)
            and row["from_addr"] == normalize_address(from_addr)
            and row["from_function"] == from_function
            and row["ref_type"] == ref_type
            for row in rows
        )
        if not found:
            raise AssertionError(f"missing xref {target} from {from_addr} {from_function} {ref_type}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    for addr, function_name, mnemonic, operands in INSTRUCTION_EXPECTATIONS:
        found = any(
            row["instruction_addr"] == normalize_address(addr)
            and row["function_name"] == function_name
            and row["mnemonic"] == mnemonic
            and (not operands or row["operands"] == operands)
            for row in rows
        )
        if not found:
            raise AssertionError(f"missing instruction {addr} {function_name} {mnemonic} {operands}")


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"SUMMARY:?\s+(.+)", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(1))}


def check_logs(base: Path) -> None:
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        text = read_text(base / name)
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{name} missing REPORT: Save succeeded")
        actual = parse_summary(text)
        if actual != expected:
            raise AssertionError(f"{name} expected summary {expected}, got {actual or '<missing>'}")
        if "FAIL:" in text or "MISSING:" in text:
            raise AssertionError(f"{name} contains failure marker")


def check_export_counts(base: Path) -> None:
    metadata_rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    xref_rows = read_tsv(base / "post_xrefs.tsv")
    index_rows = read_tsv(base / "post-decomp" / "index.tsv")
    if len(metadata_rows) != len(TARGETS):
        raise AssertionError(f"metadata row count {len(metadata_rows)} != {len(TARGETS)}")
    if len(tag_rows) != len(TARGETS):
        raise AssertionError(f"tag row count {len(tag_rows)} != {len(TARGETS)}")
    ok_decomp = [row for row in index_rows if row.get("status") == "OK"]
    if len(ok_decomp) != len(TARGETS):
        raise AssertionError(f"decompile OK count {len(ok_decomp)} != {len(TARGETS)}")
    if len(xref_rows) < len(XREF_EXPECTATIONS):
        raise AssertionError(f"xref rows {len(xref_rows)} < expected {len(XREF_EXPECTATIONS)}")


def run_checks(base: Path) -> None:
    check_logs(base)
    check_export_counts(base)
    check_metadata(base)
    check_tags(base)
    check_decompiles(base)
    check_xrefs(base)
    check_instructions(base)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        run_checks(args.base)
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"PASS: Wave500 CSoundManager event evidence verified at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
