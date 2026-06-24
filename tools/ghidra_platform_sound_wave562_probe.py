#!/usr/bin/env python3
"""Validate Wave562 platform/PC sound Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave562-platform-sound-005154e0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_platform_sound_wave562_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PCPLATFORM_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
PCSOUND_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "pcsoundmanager.cpp" / "_index.md"
SOUNDMANAGER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x005154e0": {
        "raw": "005154e0",
        "name": "PCPlatform__Init",
        "signature": "bool __thiscall PCPlatform__Init(void * this)",
        "tags": {"pc-platform", "frame-timer", "shader-init"},
        "comment_tokens": ("CFrameTimer", "performance-counter frequency", "InitShaderCapabilityFlagsAndCVar"),
        "decompile_tokens": ("PCPlatform__Init(void *this)", "CFrameTimer__ctor", "QueryPerformanceFrequency"),
    },
    "0x005155e0": {
        "raw": "005155e0",
        "name": "PCPlatform__LoadFonts",
        "signature": "void __thiscall PCPlatform__LoadFonts(void * this)",
        "tags": {"pc-platform", "fonts", "font-load"},
        "comment_tokens": ("font22_512.tga", "Terminal", "Font13PS.tga", "TitleFont.tga"),
        "decompile_tokens": ("PCPlatform__LoadFonts(void *this)", "Terminal", "font22_512.tga"),
    },
    "0x005157b0": {
        "raw": "005157b0",
        "name": "CPCPlatform__UnloadFonts",
        "signature": "void __thiscall CPCPlatform__UnloadFonts(void * this)",
        "tags": {"pc-platform", "fonts", "shutdown"},
        "comment_tokens": ("this+0x18", "this+0x2c", "this+0x00"),
        "decompile_tokens": ("CPCPlatform__UnloadFonts(void *this)", "CDXMemoryManager__Free"),
    },
    "0x005169b0": {
        "raw": "005169b0",
        "name": "CPCSoundManager__Init",
        "signature": "bool __thiscall CPCSoundManager__Init(void * this)",
        "tags": {"pc-sound", "directsound", "device-enumeration"},
        "comment_tokens": ("DirectSound", "g_SoundDeviceIndex", "IDirectSound3DListener"),
        "decompile_tokens": ("CPCSoundManager__Init(void *this)", "DirectSoundEnumerateA", "DirectSoundCreate8"),
    },
    "0x005172a0": {
        "raw": "005172a0",
        "name": "CPCSoundManager__CreateSampleFromFile",
        "signature": "void * __stdcall CPCSoundManager__CreateSampleFromFile(void * sample_source, int channel_type, void * reusable_sample)",
        "tags": {"pc-sound", "sample-create", "adpcm", "directsound-buffer"},
        "comment_tokens": ("RET 0x0c", "ADPCM", "DirectSound buffer"),
        "decompile_tokens": ("CPCSoundManager__CreateSampleFromFile", "CPCSoundManager__DecodeADPCM", "CPCSoundManager__ConvertAudioFormat"),
    },
    "0x00517440": {
        "raw": "00517440",
        "name": "CPCSoundManager__CreateSoundBuffer",
        "signature": "void * __cdecl CPCSoundManager__CreateSoundBuffer(void * out_ds_buffer, uint source_byte_count)",
        "tags": {"pc-sound", "directsound-buffer", "format-conversion"},
        "comment_tokens": ("DAT_00896a44", "DAT_00896a48", "locked write pointer"),
        "decompile_tokens": ("CPCSoundManager__CreateSoundBuffer(void *out_ds_buffer", "source_byte_count"),
    },
    "0x00517600": {
        "raw": "00517600",
        "name": "CPCSoundManager__ConvertAudioFormat",
        "signature": "void __cdecl CPCSoundManager__ConvertAudioFormat(void * destination, short * source_pcm16, uint source_byte_count)",
        "tags": {"pc-sound", "format-conversion", "sample-rate"},
        "comment_tokens": ("Quality 0", "quality 1", "unsigned 8-bit"),
        "decompile_tokens": ("CPCSoundManager__ConvertAudioFormat(void *destination", "source_byte_count"),
    },
    "0x005176d0": {
        "raw": "005176d0",
        "name": "CPCSoundManager__CreateSampleFromData",
        "signature": "void * __stdcall CPCSoundManager__CreateSampleFromData(void * pcm_data, uint byte_count, int unused_arg, void * reusable_sample)",
        "tags": {"pc-sound", "bink-voice", "sample-create"},
        "comment_tokens": ("RET 0x10", "Bink", "unused"),
        "decompile_tokens": ("CPCSoundManager__CreateSampleFromData", "byte_count", "unused_arg"),
    },
    "0x00517fa0": {
        "raw": "00517fa0",
        "name": "CPCSoundManager__DecodeADPCM",
        "signature": "void __cdecl CPCSoundManager__DecodeADPCM(char * source_adpcm, short * destination_pcm16, uint sample_count, short * decoder_state)",
        "tags": {"pc-sound", "adpcm", "decode"},
        "comment_tokens": ("0x0063e85c", "0x0063e89c", "signed 16-bit PCM"),
        "decompile_tokens": ("CPCSoundManager__DecodeADPCM", "source_adpcm", "decoder_state"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile index")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        else:
            decomp_file = next((BASE / "post_decompile").glob(f"{spec['raw']}_*.c"), None)
            if decomp_file is None:
                failures.append(f"{address} missing decompile file")
            else:
                require_tokens(f"{address} decompile", read_text(decomp_file), spec["decompile_tokens"], failures)

    require_tokens(
        "xrefs",
        xrefs,
        (
            "CLTShell__InitializeRuntimeAndLoadCoreResources",
            "CLTShell__ShutdownRuntimeAndReleaseResources",
            "CSoundManager__Init",
            "CSoundManager__CreateSample",
            "CGame__PumpBinkVoiceSampleQueue",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x00517372\t0x005172a0\tCPCSoundManager__CreateSampleFromFile\tRET\t0xc",
            "0x00517785\t0x005176d0\tCPCSoundManager__CreateSampleFromData\tRET\t0x10",
        ),
        failures,
    )

    queue = json.loads(read_text(BASE / "post_static_reaudit_queue.json"))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3298,
        "undefinedSignatureCount": 1503,
        "paramSignatureCount": 1185,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")

    docs = {
        "public note": (
            PUBLIC_NOTE,
            ("Wave562", "PCPlatform / PCSound", "CPCSoundManager__DecodeADPCM", "3298"),
        ),
        "function index": (
            FUNCTION_INDEX,
            ("Wave562", "PCPlatform / PCSound", "CPCSoundManager__CreateSampleFromData"),
        ),
        "pcplatform index": (
            PCPLATFORM_INDEX,
            ("Wave562", "PCPlatform / PCSound", "PCPlatform__LoadFonts", "CPCPlatform__UnloadFonts"),
        ),
        "pcsound index": (
            PCSOUND_INDEX,
            ("Wave562", "CPCSoundManager__CreateSoundBuffer", "CPCSoundManager__DecodeADPCM"),
        ),
        "soundmanager index": (
            SOUNDMANAGER_INDEX,
            ("Wave562", "PC backend", "CPCSoundManager__CreateSampleFromFile"),
        ),
        "ghidra reference": (
            GHIDRA_REFERENCE,
            ("Wave562", "PCPlatform / PCSound", "CPCSoundManager__DecodeADPCM"),
        ),
        "campaign": (
            CAMPAIGN,
            ("Wave 562", "PCPlatform / PCSound", "CFastVB__Create"),
        ),
        "backlog": (
            BACKLOG,
            ("Wave562", "PCPlatform / PCSound", "0x005154e0"),
        ),
        "ledger": (
            LEDGER,
            ("Wave562", "platform_sound", "0x00517fa0"),
        ),
    }
    for label, (path, tokens) in docs.items():
        require_tokens(label, read_text(path), tokens, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run checks and exit nonzero on failure")
    args = parser.parse_args(argv)
    failures = run_check()
    if failures:
        print("Wave562 platform/PC sound probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Wave562 platform/PC sound probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
