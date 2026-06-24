#!/usr/bin/env python3
"""Validate Wave501 CSoundManager sample playback static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave501-csoundmanager-sample-playback-004dff30"
)

COMMON_TAGS = {
    "audio",
    "comment-hardened",
    "csoundmanager-wave501",
    "retail-binary-evidence",
    "sample-playback",
    "signature-corrected",
    "sound-manager",
    "source-parity",
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
    "0x004dff30": target(
        "CSample__DestructorBody",
        "void __fastcall CSample__DestructorBody(void * this)",
        (
            "CSample destructor body",
            "not a constructor",
            "installs the CSample vtable",
            "walks active sound events whose sample pointer equals this",
            "unlinks this sample from the global first-sample list",
            "runtime sample unload behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "sample-lifecycle", "destructor"},
        (
            "void __fastcall CSample__DestructorBody(void *this)",
            "PTR_CSample__DeletingDestructor_005dee6c",
            "CGenericActiveReader__SetReader(sound_event,(void *)0x0)",
            "DAT_00896988",
        ),
    ),
    "0x004dffc0": target(
        "CSample__DeletingDestructor",
        "void * __thiscall CSample__DeletingDestructor(void * this, int delete_flags, int unused)",
        (
            "CSample vtable 0x005dee6c slot 0",
            "stops events referencing this sample",
            "block_until_stopped=1",
            "CDXMemoryManager__Free",
            "delete_flags bit 0",
            "returns this",
            "unused",
            "runtime sample unload behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "sample-lifecycle", "deleting-destructor", "vtable"},
        (
            "void * __thiscall CSample__DeletingDestructor(void *this,int delete_flags,int unused)",
            "PTR_CSample__DeletingDestructor_005dee6c",
            "CSoundManager__StopSoundEvent(pvVar1,1)",
            "CDXMemoryManager__Free(&DAT_009c3df0,this)",
        ),
    ),
    "0x004e0890": target(
        "CSoundManager__CreateSample",
        "void * __thiscall CSoundManager__CreateSample(void * this, char * name, int channel_type, void * sample_source, int reuse_existing)",
        (
            "source-aligns to CSoundManager sample creation",
            "retail PC backend differences",
            "chooses sounds/music path context from channel_type",
            "CPCSoundManager__CreateSampleFromFile",
            "copies the name into the sample+0x08 buffer",
            "_L/_R suffixes",
            "runtime file loading behavior",
            "rebuild parity remain unproven",
        ),
        {"sample-create", "pc-sound"},
        (
            "void * __thiscall CSoundManager__CreateSample",
            "CPCSoundManager__CreateSampleFromFile(sample_source,channel_type",
            "*(int *)((int)pvVar3 + 0x6c) = channel_type",
            "*(undefined4 *)((int)pvVar3 + 0x74)",
        ),
    ),
    "0x004e0a00": target(
        "CSoundManager__GetOrCreateSample",
        "void * __thiscall CSoundManager__GetOrCreateSample(void * this, char * name, int channel_type, int reload_if_exists)",
        (
            "source-aligns to CSoundManager::GetSample",
            "requires the manager initialized flag",
            "non-empty sample name",
            "case-insensitive name match",
            "reload_if_exists",
            "CSoundManager__CreateSample",
            "runtime loading behavior",
            "rebuild parity remain unproven",
        ),
        {"sample-lookup", "sample-create"},
        (
            "void * __thiscall CSoundManager__GetOrCreateSample",
            "*(char *)((int)this + 4) != '\\0'",
            "stricmp(name,(char *)((int)pvVar3 + 8))",
            "CSoundManager__CreateSample",
        ),
    ),
    "0x004e0a90": target(
        "CSoundManager__PlayNamedSample",
        "void __thiscall CSoundManager__PlayNamedSample(void * this, char * sample_name, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)",
        (
            "source-aligns to CSoundManager::PlayNamedSample",
            "RET 0x34",
            "CSoundManager__GetOrCreateSample(this, sample_name, 0, 0)",
            "CSoundManager__PlaySample",
            "logs an error if lookup fails",
            "runtime playback behavior",
            "rebuild parity remain unproven",
        ),
        {"playback-wrapper", "sample-lookup"},
        (
            "void __thiscall CSoundManager__PlayNamedSample",
            "CSoundManager__GetOrCreateSample(this,sample_name,0,0)",
            "CSoundManager__PlaySample",
            "CConsole__Printf(&DAT_0066f580,s_ERROR__PlayNamedSample_failed_to_006322b8,sample_name)",
        ),
    ),
    "0x004e0b30": target(
        "CSoundManager__PlaySample",
        "void __thiscall CSoundManager__PlaySample(void * this, void * sample, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)",
        (
            "source-aligns to CSoundManager::PlaySample",
            "RET 0x34",
            "GAME_STATE_PRE_RUNNING",
            "duplicate once-only events",
            "CSoundManager__StartSoundEvent",
            "callers in this evidence set use the function as a void playback wrapper",
            "runtime once-only/playback behavior",
            "rebuild parity remain unproven",
        ),
        {"playback-wrapper", "start-event-caller"},
        (
            "void __thiscall CSoundManager__PlaySample",
            "DAT_008a9ac0 != 1",
            "(char)once != '\\0'",
            "CSoundManager__StartSoundEvent",
        ),
    ),
    "0x004e0bd0": target(
        "CSoundManager__StartSoundEvent",
        "void * __thiscall CSoundManager__StartSoundEvent(void * this, void * owner, void * sample, int tracking_type, float volume, float fade_seconds, float from_point_seconds, float to_point_seconds, int loop, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)",
        (
            "older PlaySound label is superseded",
            "CSoundManager::StartSoundEvent",
            "allocates a CSoundEvent",
            "stores owner/sample/tracking/volume/fade/range/loop/pitch/completion/ignore/sound-type fields",
            "deletes too-distant non-looping events back to the pool",
            "CSoundManager__PlaySoundOnChannel",
            "returns the event pointer or NULL",
            "runtime playback/mixing behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "start-event", "playback-core"},
        (
            "void * __thiscall CSoundManager__StartSoundEvent",
            "CSoundManager__AllocateSoundEvent(this,iVar7)",
            "CGenericActiveReader__SetReader(this_00,owner)",
            "CSoundManager__UpdateSoundPosition(this_00,1)",
            "CSoundManager__PlaySoundOnChannel(&DAT_00896988,this_00)",
        ),
    ),
}

XREF_EXPECTATIONS = (
    ("0x004dff30", "0x00516943", "CPCSoundManager__dtor", "UNCONDITIONAL_CALL"),
    ("0x004dffc0", "0x005dee6c", "<no_function>", "DATA"),
    ("0x004e0890", "0x004e0a64", "CSoundManager__GetOrCreateSample", "UNCONDITIONAL_CALL"),
    ("0x004e0a00", "0x004e0abd", "CSoundManager__PlayNamedSample", "UNCONDITIONAL_CALL"),
    ("0x004e0a90", "0x0051c072", "CFEPLanguageTest__PlaySound", "UNCONDITIONAL_CALL"),
    ("0x004e0b30", "0x004e0b05", "CSoundManager__PlayNamedSample", "UNCONDITIONAL_CALL"),
    ("0x004e0bd0", "0x004e0bc4", "CSoundManager__PlaySample", "UNCONDITIONAL_CALL"),
)

INSTRUCTION_EXPECTATIONS = (
    ("0x004dff34", "CSample__DestructorBody", "MOV", "dword ptr [EDI], 0x5dee6c"),
    ("0x004dffe1", "CSample__DeletingDestructor", "CALL", "0x004e0f70"),
    ("0x004e0890", "CSoundManager__CreateSample", "SUB", "ESP, 0x104"),
    ("0x004e0916", "CSoundManager__CreateSample", "CALL", "0x005172a0"),
    ("0x004e0abd", "CSoundManager__PlayNamedSample", "CALL", "0x004e0a00"),
    ("0x004e0b05", "CSoundManager__PlayNamedSample", "CALL", "0x004e0b30"),
    ("0x004e0bc4", "CSoundManager__PlaySample", "CALL", "0x004e0bd0"),
    ("0x004e0bfd", "CSoundManager__StartSoundEvent", "CALL", "0x004e0fb0"),
    ("0x004e0c77", "CSoundManager__StartSoundEvent", "MOV", "byte ptr [ESI + 0x8], 0x1"),
)

EXPECTED_LOG_SUMMARIES = {
    "apply_csoundmanager_sample_playback_wave501_dry.log": {
        "updated": 0,
        "skipped": 7,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 3,
        "missing": 0,
        "bad": 0,
    },
    "apply_csoundmanager_sample_playback_wave501_apply.log": {
        "updated": 7,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 3,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_csoundmanager_sample_playback_wave501_final_verify_dry.log": {
        "updated": 0,
        "skipped": 7,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

OVERCLAIM_TOKENS = (
    "runtime sample unload behavior proven",
    "runtime file loading behavior proven",
    "runtime loading behavior proven",
    "runtime playback behavior proven",
    "runtime once-only/playback behavior proven",
    "runtime playback/mixing behavior proven",
    "exact layout proven",
    "exact CSample layout proven",
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
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "from_function_addr",
            "instruction_addr",
            "function_entry",
        ):
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
    for target_addr, from_addr, from_function, ref_type in XREF_EXPECTATIONS:
        found = any(
            row["target_addr"] == normalize_address(target_addr)
            and row["from_addr"] == normalize_address(from_addr)
            and row["from_function"] == from_function
            and row["ref_type"] == ref_type
            for row in rows
        )
        if not found:
            raise AssertionError(f"missing xref {target_addr} from {from_addr} {from_function} {ref_type}")


def check_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    for addr, function_name, mnemonic, operands in INSTRUCTION_EXPECTATIONS:
        found = any(
            row["instruction_addr"] == normalize_address(addr)
            and row["function_name"] == function_name
            and row["mnemonic"] == mnemonic
            and row["operands"] == operands
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
        if "FAIL:" in text or "MISSING:" in text or "BADNAME:" in text:
            raise AssertionError(f"{name} contains failure marker")


def check_export_counts(base: Path) -> None:
    metadata_rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    xref_rows = read_tsv(base / "post_xrefs.tsv")
    instruction_rows = read_tsv(base / "post_instructions.tsv")
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
    if len(instruction_rows) != 847:
        raise AssertionError(f"instruction row count {len(instruction_rows)} != 847")


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

    print(f"PASS: Wave501 CSoundManager sample playback evidence verified at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
