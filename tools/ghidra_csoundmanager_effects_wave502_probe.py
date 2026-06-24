#!/usr/bin/env python3
"""Validate Wave502 CSoundManager/CEffect static RE evidence."""

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
    / "wave502-soundmanager-effects-scout-004e1800"
)

COMMON_TAGS = {
    "audio",
    "comment-hardened",
    "csoundmanager-wave502",
    "effect-playback",
    "retail-binary-evidence",
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
    "0x004e00d0": target(
        "CSoundManager__Init",
        "bool __thiscall CSoundManager__Init(void * this)",
        (
            "CSoundManager::Init",
            "loads data\\\\\\\\sounds\\\\\\\\sounds.sfx",
            "allocates 256 pooled CSoundEvent records",
            "registers the sound debug menu/cvars/playsound command",
            "PC sound manager init",
            "runtime device initialization",
            "rebuild parity remain unproven",
        ),
        {"init", "pc-sound", "event-pool", "cvars"},
        (
            "bool __thiscall CSoundManager__Init(void *this)",
            "CEffect__LoadSFXFile",
            "CConsole__RegisterCommand",
            "CPCSoundManager__Init",
        ),
    ),
    "0x004e1800": target(
        "CSoundManager__StopSample",
        "void __thiscall CSoundManager__StopSample(void * this, char * sample_name, void * owner)",
        (
            "CSoundManager::StopSample",
            "not a CMonitor method",
            "matches playing events by owner reader and sample-name string",
            "clears the active reader",
            "runtime stop behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "sample-query", "stop-sample"},
        (
            "void __thiscall CSoundManager__StopSample",
            "stricmp",
            "CSoundManager__StopAndReleaseChannel",
            "CGenericActiveReader__SetReader",
        ),
    ),
    "0x004e1880": target(
        "CSoundManager__GetSoundEventForThing",
        "void * __thiscall CSoundManager__GetSoundEventForThing(void * this, char * sample_name, void * owner)",
        (
            "CSoundManager::GetSoundEventForThing",
            "not a CMonitor method",
            "returns the first playing event",
            "owner/name pair",
            "event lifetime guarantees",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "sample-query", "event-lookup"},
        (
            "void * __thiscall CSoundManager__GetSoundEventForThing",
            "stricmp",
            "return piVar1",
        ),
    ),
    "0x004e1910": target(
        "CSoundManager__GetEffectByName",
        "void * __thiscall CSoundManager__GetEffectByName(void * this, char * name, int ordinal)",
        (
            "CSoundManager::GetEffectByName",
            "not BattleEngine",
            "delegates name/ordinal lookup",
            "static CEffect list lookup",
            "runtime lookup behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "effect-lookup"},
        (
            "void * __thiscall CSoundManager__GetEffectByName",
            "CEffect__GetEffectByName(name,ordinal)",
        ),
    ),
    "0x004e1940": target(
        "CSoundManager__PlayEffect",
        "void __thiscall CSoundManager__PlayEffect(void * this, void * effect, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int sound_type, int ignore_owner_pos)",
        (
            "CSoundManager::PlayEffect",
            "extra retail stack flag preserved by RET 0x30",
            "randomly selects one entry",
            "sets the language-dependent sample flag",
            "forwards to CSoundManager__PlaySample",
            "runtime random selection/playback behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "effect-playback", "chain-random"},
        (
            "void __thiscall CSoundManager__PlayEffect",
            "CSoundManager__GetOrCreateSample",
            "CSoundManager__PlaySample",
            "DAT_0083cfa0",
        ),
    ),
    "0x004e1ab0": target(
        "CSoundManager__IsEffectPlaying",
        "bool __thiscall CSoundManager__IsEffectPlaying(void * this, void * effect, void * owner)",
        (
            "CSoundManager::IsEffectPlaying",
            "not a CMonitor method",
            "walks a chained CEffect list",
            "owner reader matches the supplied owner",
            "sample name matches the effect sample name",
            "runtime playback-state behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "effect-query", "chain-scan"},
        (
            "bool __thiscall CSoundManager__IsEffectPlaying",
            "stricmp",
            "return true",
        ),
    ),
    "0x004e2360": target(
        "CSoundManager__GetDebugMenuText",
        "void __thiscall CSoundManager__GetDebugMenuText(void * this, int entry_index, char * text)",
        (
            "CSoundManager::GetDebugMenuText",
            "[no sound]",
            "sample/channel text",
            "volume/current-attenuated-volume",
            "tracking-mode owner/dead-target text",
            "debug menu wrapper boundary near 0x004e2500",
            "rebuild parity remain unproven",
        ),
        {"debug-menu", "event-debug-text"},
        (
            "void __thiscall CSoundManager__GetDebugMenuText",
            "s__no_sound__0063261c",
            "s_No_tracking_006325d0",
            "s_Follow_and_die_tracking",
        ),
    ),
    "0x004e2530": target(
        "CEffect__LoadSFXFile",
        "void __cdecl CEffect__LoadSFXFile(char * filename)",
        (
            "CEffect::LoadSFXFile",
            "not a CSoundManager method",
            "opens the supplied SFX filename",
            "allocates 0xDC-byte CEffect records",
            "reads looping/language-dependent flags by version",
            "chains duplicate effect names",
            "runtime parse behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "effect-definition", "sfx-parser"},
        (
            "void __cdecl CEffect__LoadSFXFile(char *filename)",
            "CDXMemBuffer__InitFromFile",
            "OID__AllocObject(0xdc",
            "g_pSoundDefinitionListHead",
        ),
    ),
    "0x004e2a90": target(
        "CEffect__GetEffectByName",
        "void * __cdecl CEffect__GetEffectByName(char * name, int ordinal)",
        (
            "CEffect::GetEffectByName",
            "normalizes repeated backslashes",
            "walks the CEffect main list",
            "compares names case-insensitively",
            "returns the nth matching effect",
            "runtime lookup behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "effect-lookup", "sfx-parser"},
        (
            "void * __cdecl CEffect__GetEffectByName(char *name,int ordinal)",
            "g_pSoundDefinitionListHead",
            "stricmp",
        ),
    ),
    "0x004e2b30": target(
        "CSoundEvent__DestructorBody",
        "void __thiscall CSoundEvent__DestructorBody(void * this)",
        (
            "CSoundEvent destructor body",
            "not a CSoundManager release helper",
            "unlinks/frees the debug marker",
            "removes this active reader from its owner deletion-event set",
            "destructor flavor",
            "runtime event deletion behavior",
            "rebuild parity remain unproven",
        ),
        {"name-corrected", "event-lifecycle", "destructor"},
        (
            "void __thiscall CSoundEvent__DestructorBody(void *this)",
            "CDebugMarker__UnlinkFromGlobalList",
            "CSPtrSet__Remove",
        ),
    ),
    "0x004e2c50": target(
        "CSoundManager__ReloadLanguageSampleBank",
        "void __thiscall CSoundManager__ReloadLanguageSampleBank(void * this)",
        (
            "retail PC language-sample-bank reload helper",
            "language XAP path differs",
            "moves active sound events back to the pool",
            "stops active voices",
            "reloads the compressed sample bank",
            "runtime language reload behavior",
            "rebuild parity remain unproven",
        ),
        {"language-audio", "sample-bank", "pc-sound"},
        (
            "void __thiscall CSoundManager__ReloadLanguageSampleBank(void *this)",
            "CSoundManager__StopAllActiveVoices",
            "CSoundManager__LoadCompressedSampleBank",
            "s_Loading_XAP_00632628",
        ),
    ),
}

XREF_EXPECTATIONS = (
    ("0x004e00d0", "0x004efcb2", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x004e1800", "0x004099bc", "CMonitor__UpdateSoundEventPlaybackForReader", "UNCONDITIONAL_CALL"),
    ("0x004e1880", "0x0040a691", "CBattleEngine__Morph", "UNCONDITIONAL_CALL"),
    ("0x004e1910", "0x004687a1", "CFrontEnd__PlaySound", "UNCONDITIONAL_CALL"),
    ("0x004e1940", "0x004687cb", "CFrontEnd__PlaySound", "UNCONDITIONAL_CALL"),
    ("0x004e1ab0", "0x00408cbc", "CMonitor__Process", "UNCONDITIONAL_CALL"),
    ("0x004e2360", "0x004e250f", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004e2530", "0x004e013e", "CSoundManager__Init", "UNCONDITIONAL_CALL"),
    ("0x004e2a90", "0x004e1926", "CSoundManager__GetEffectByName", "UNCONDITIONAL_CALL"),
    ("0x004e2b30", "0x004e0747", "CSoundManager__Shutdown", "UNCONDITIONAL_CALL"),
    ("0x004e2c50", "0x00466301", "CFrontEnd__Init", "UNCONDITIONAL_CALL"),
)

INSTRUCTION_EXPECTATIONS = (
    ("0x004e1800", "CSoundManager__StopSample", "MOV", "AL, byte ptr [ECX + 0x4]"),
    ("0x004e1880", "CSoundManager__GetSoundEventForThing", "MOV", "AL, byte ptr [ECX + 0x4]"),
    ("0x004e1910", "CSoundManager__GetEffectByName", "MOV", "AL, byte ptr [ECX + 0x4]"),
    ("0x004e1940", "CSoundManager__PlayEffect", "PUSH", "EBP"),
    ("0x004e1a8d", "CSoundManager__PlayEffect", "RET", "0x30"),
    ("0x004e2360", "CSoundManager__GetDebugMenuText", "SUB", "ESP, 0x100"),
    ("0x004e250f", "<no_function>", "CALL", "0x004e2360"),
    ("0x004e2530", "CEffect__LoadSFXFile", "PUSH", "-0x1"),
    ("0x004e2a90", "CEffect__GetEffectByName", "MOV", "AL, [0x0089698c]"),
    ("0x004e2b30", "CSoundEvent__DestructorBody", "PUSH", "-0x1"),
    ("0x004e2c50", "CSoundManager__ReloadLanguageSampleBank", "SUB", "ESP, 0xc8"),
)

EXPECTED_LOG_SUMMARIES = {
    "apply_csoundmanager_effects_wave502_dry.log": {
        "updated": 0,
        "skipped": 11,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 8,
        "missing": 0,
        "bad": 0,
    },
    "apply_csoundmanager_effects_wave502_apply.log": {
        "updated": 11,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 8,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_csoundmanager_effects_wave502_final_verify_dry.log": {
        "updated": 0,
        "skipped": 11,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

OVERCLAIM_TOKENS = (
    "runtime device initialization proven",
    "runtime stop behavior proven",
    "runtime lookup behavior proven",
    "runtime random selection/playback behavior proven",
    "runtime playback-state behavior proven",
    "runtime parse behavior proven",
    "runtime event deletion behavior proven",
    "runtime language reload behavior proven",
    "rebuild parity proven",
    "fully reverse engineered",
)


def normalize_addr(value: str) -> str:
    value = value.strip().lower()
    if not value.startswith("0x"):
        value = "0x" + value
    return "0x" + value[2:].zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"Missing TSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def require_contains(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise AssertionError(f"{label}: missing token {needle!r}")


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(
        r"SUMMARY: updated=(\d+) skipped=(\d+) created=(\d+) would_create=(\d+) "
        r"renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    if not match:
        raise AssertionError("Missing SUMMARY line")
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def verify_metadata(base: Path) -> None:
    rows = {normalize_addr(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    for address, spec in TARGETS.items():
        key = normalize_addr(address)
        if key not in rows:
            raise AssertionError(f"metadata missing {address}")
        row = rows[key]
        if row["status"] != "OK":
            raise AssertionError(f"metadata status for {address}: {row['status']}")
        if row["name"] != spec["name"]:
            raise AssertionError(f"{address}: expected name {spec['name']}, got {row['name']}")
        if row["signature"] != spec["signature"]:
            raise AssertionError(f"{address}: expected signature {spec['signature']}, got {row['signature']}")
        comment = row["comment"]
        for token in spec["comment_tokens"]:
            require_contains(comment, token, f"{address} comment")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                raise AssertionError(f"{address} comment overclaims with token {token!r}")


def verify_tags(base: Path) -> None:
    rows = {normalize_addr(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        key = normalize_addr(address)
        if key not in rows:
            raise AssertionError(f"tags missing {address}")
        tags = {tag for tag in rows[key]["tags"].split(";") if tag}
        missing = set(spec["tags"]) - tags
        if missing:
            raise AssertionError(f"{address}: missing tags {sorted(missing)}")


def verify_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    normalized = {
        (
            normalize_addr(row["target_addr"]),
            normalize_addr(row["from_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    for address, from_addr, from_function, ref_type in XREF_EXPECTATIONS:
        expected = (normalize_addr(address), normalize_addr(from_addr), from_function, ref_type)
        if expected not in normalized:
            raise AssertionError(f"missing xref {expected}")


def verify_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {normalize_addr(row["instruction_addr"]): row for row in rows}
    for address, function_name, mnemonic, operand_token in INSTRUCTION_EXPECTATIONS:
        key = normalize_addr(address)
        if key not in by_addr:
            raise AssertionError(f"missing instruction {address}")
        row = by_addr[key]
        if row["function_name"] != function_name:
            raise AssertionError(f"{address}: expected function {function_name}, got {row['function_name']}")
        if row["mnemonic"] != mnemonic:
            raise AssertionError(f"{address}: expected mnemonic {mnemonic}, got {row['mnemonic']}")
        require_contains(row["operands"], operand_token, f"{address} operands")


def verify_decompile(base: Path) -> None:
    decomp_dir = base / "post-decomp"
    index = read_tsv(decomp_dir / "index.tsv")
    rows = {normalize_addr(row["address"]): row for row in index}
    for address, spec in TARGETS.items():
        key = normalize_addr(address)
        if key not in rows:
            raise AssertionError(f"decompile index missing {address}")
        row = rows[key]
        if row["status"] != "OK":
            raise AssertionError(f"decompile status for {address}: {row['status']}")
        if row["name"] != spec["name"]:
            raise AssertionError(f"decompile name for {address}: {row['name']}")
        decomp_file = decomp_dir / f"{key[2:]}_{row['name']}.c"
        if not decomp_file.exists():
            raise AssertionError(f"decompile file missing for {address}: {decomp_file.name}")
        content = decomp_file.read_text(encoding="utf-8")
        for token in spec["decompile_tokens"]:
            require_contains(content, token, f"{address} decompile")


def verify_logs(base: Path) -> None:
    for name, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / name
        if not path.exists():
            raise AssertionError(f"missing log {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if "REPORT: Save succeeded" not in text:
            raise AssertionError(f"{name}: missing save success")
        actual = parse_summary(text)
        if actual != expected:
            raise AssertionError(f"{name}: expected {expected}, got {actual}")


def verify_queue(base: Path) -> None:
    queue_json = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
    if not queue_json.exists():
        raise AssertionError(f"missing queue report {queue_json}")
    text = queue_json.read_text(encoding="utf-8")
    for token in (
        '"totalFunctions": 6078',
        '"commentlessFunctionCount"',
        '"undefinedSignatureCount"',
        '"paramSignatureCount"',
    ):
        require_contains(text, token, "queue report")


def verify(base: Path) -> None:
    verify_logs(base)
    verify_metadata(base)
    verify_tags(base)
    verify_xrefs(base)
    verify_instructions(base)
    verify_decompile(base)
    verify_queue(base)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="Run validation and exit nonzero on failure.")
    args = parser.parse_args()

    base = args.base.resolve()
    try:
        verify(base)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: Wave502 CSoundManager/CEffect evidence verified at {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
