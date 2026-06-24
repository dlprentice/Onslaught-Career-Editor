#!/usr/bin/env python3
"""Validate Wave568 Ogg/Vorbis and COggFileRead Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave568-ogg-vorbis-stream-00523df0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ogg_vorbis_wave568_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
OGG_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "OggLoader.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x00523df0": {
        "raw": "00523df0",
        "name": "OggVorbisStream__InitDecoder",
        "signature": "int __thiscall OggVorbisStream__InitDecoder(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-vorbis", "decoder-init", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("initializes one Ogg/Vorbis decode stream", "+0x2008", "+0x200c/+0x2010", "runtime streaming behavior"),
        "decompile_tokens": ("OggVorbisStream__InitDecoder(void *this)", "ogg_sync_buffer", "vorbis_synthesis_headerin", "vorbis_block_init"),
    },
    "0x00524180": {
        "raw": "00524180",
        "name": "OggVorbisStream__ReadPcmSamples",
        "signature": "int __thiscall OggVorbisStream__ReadPcmSamples(void * this, void * out_pcm_bytes, uint requested_byte_count)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-vorbis", "pcm-decode", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("RET 0x8 confirms", "older third param_N was a decompiler artifact", "this+4/+0x22d8"),
        "decompile_tokens": ("OggVorbisStream__ReadPcmSamples(void *this,void *out_pcm_bytes,uint requested_byte_count)", "OggVorbisStream__InitDecoder(this);", "vorbis_synthesis_pcmout", "CRT__MemMoveOverlapSafe"),
    },
    "0x005245a0": {
        "raw": "005245a0",
        "name": "COggFileRead__ctor_base",
        "signature": "void * __thiscall COggFileRead__ctor_base(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "constructor", "name-corrected", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("installs the COggFileRead vtable", "0x005e4a44", "PCPlatform async music stream initialization"),
        "decompile_tokens": ("COggFileRead__ctor_base(void *this)", "PTR_COggFileRead__scalar_deleting_dtor_005e4a44", "0x1000", "return this;"),
    },
    "0x005245e0": {
        "raw": "005245e0",
        "name": "COggFileRead__scalar_deleting_dtor",
        "signature": "void * __thiscall COggFileRead__scalar_deleting_dtor(void * this, byte flags)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "destructor", "scalar-deleting-dtor", "name-corrected", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("scalar-deleting destructor wrapper", "RET 0x4 confirms", "flags bit 0"),
        "decompile_tokens": ("COggFileRead__dtor_body(this);", "if ((flags & 1) != 0)", "CDXMemoryManager__Free", "return this;"),
    },
    "0x00524600": {
        "raw": "00524600",
        "name": "COggFileRead__dtor_body",
        "signature": "void __thiscall COggFileRead__dtor_body(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "destructor", "close-reset", "name-corrected", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("destructor/close body", "+0x2008", "restores the base CWaveSoundRead vtable"),
        "decompile_tokens": ("COggFileRead__dtor_body(void *this)", "ogg_stream_clear", "vorbis_block_clear", "fclose", "PTR_CWaveSoundRead__BaseScalarDeletingDestructor_005dfc6c"),
    },
    "0x005246a0": {
        "raw": "005246a0",
        "name": "COggFileRead__OpenFileAndPrimeDecoder",
        "signature": "int __thiscall COggFileRead__OpenFileAndPrimeDecoder(void * this, char * file_path)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "vtable-slot", "open", "decoder-prime", "name-corrected", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("slot 1", "vtable slot 3", "OggVorbisStream__ReadPcmSamples with null output"),
        "decompile_tokens": ("COggFileRead__OpenFileAndPrimeDecoder(void *this,char *file_path)", "fopen(file_path,&DAT_00629038);", "OggVorbisStream__ReadPcmSamples(this,(void *)0x0,0)", "return -0x7fffbffb;"),
    },
    "0x00524710": {
        "raw": "00524710",
        "name": "COggFileRead__ReadDecodedPcm",
        "signature": "int __thiscall COggFileRead__ReadDecodedPcm(void * this, uint requested_byte_count, void * out_pcm_bytes, int * out_bytes_read)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "vtable-slot", "function-boundary", "pcm-decode", "boundary-recovered", "argument-order-corrected", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("slot 2 boundary", "first stack argument as the requested byte count", "second stack argument as the output buffer"),
        "decompile_tokens": ("COggFileRead__ReadDecodedPcm", "uint requested_byte_count,void *out_pcm_bytes", "OggVorbisStream__ReadPcmSamples(this,out_pcm_bytes,requested_byte_count);", "*out_bytes_read = iVar1;"),
    },
    "0x00524770": {
        "raw": "00524770",
        "name": "COggFileRead__CloseAndReset",
        "signature": "int __thiscall COggFileRead__CloseAndReset(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "vtable-slot", "close-reset", "name-corrected", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("slot 3", "closes and resets", "+0x200c/+0x2010"),
        "decompile_tokens": ("COggFileRead__CloseAndReset(void *this)", "ogg_stream_clear", "fclose", "return 0;"),
    },
    "0x00524800": {
        "raw": "00524800",
        "name": "COggFileRead__IsOpen",
        "signature": "int __thiscall COggFileRead__IsOpen(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "vtable-slot", "function-boundary", "field-reader", "boundary-recovered", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("slot 4 boundary", "+0x2008", "open-state value"),
        "decompile_tokens": ("COggFileRead__IsOpen(void *this)", "return (uint)(*(int *)((int)this + 0x2008) != 0);"),
    },
    "0x00524810": {
        "raw": "00524810",
        "name": "COggFileRead__GetSampleRate",
        "signature": "int __thiscall COggFileRead__GetSampleRate(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "vtable-slot", "function-boundary", "field-reader", "sample-rate", "boundary-recovered", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("slot 5 boundary", "this+0x21d0", "channel count"),
        "decompile_tokens": ("COggFileRead__GetSampleRate(void *this)", "return *(int *)((int)this + 0x21d0);"),
    },
    "0x00524820": {
        "raw": "00524820",
        "name": "COggFileRead__GetChannelCount",
        "signature": "int __thiscall COggFileRead__GetChannelCount(void * this)",
        "tags": {"static-reaudit", "ogg-vorbis-wave568", "retail-binary-evidence", "ogg-file-read", "vtable-slot", "function-boundary", "field-reader", "channel-count", "boundary-recovered", "signature-corrected", "comment-hardened"},
        "comment_tokens": ("slot 6 boundary", "this+0x21cc", "channel-count"),
        "decompile_tokens": ("COggFileRead__GetChannelCount(void *this)", "return *(int *)((int)this + 0x21cc);"),
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


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def run_check() -> list[str]:
    failures: list[str] = []

    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 11, "created": 0, "would_create": 4, "renamed": 0, "would_rename": 5, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 11, "skipped": 0, "created": 4, "would_create": 0, "renamed": 5, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_verify_dry.log", {"updated": 0, "skipped": 11, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "slot2_argument_order_correction_dry.log", {"updated": 0, "skipped": 0, "would_update": 1, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "slot2_argument_order_correction_apply.log", {"updated": 1, "skipped": 0, "would_update": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "slot2_argument_order_correction_verify.log", {"updated": 0, "skipped": 1, "would_update": 0, "missing": 0, "bad": 0}, failures)

    if not (BASE / "post_before_slot2_argument_order_correction" / "post_metadata.tsv").is_file():
        failures.append("missing preserved pre-correction post snapshot")

    expected_counts = {
        "post_metadata.tsv": 11,
        "post_tags.tsv": 11,
        "post_xrefs.tsv": 20,
        "post_target_instructions.tsv": 2607,
        "post_callsite_instructions.tsv": 348,
        "post_vtable_slots.tsv": 24,
        "post_decompile/index.tsv": 11,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")
    callsites = read_text(BASE / "post_callsite_instructions.tsv")
    vtables = read_text(BASE / "post_vtable_slots.tsv")

    overclaim_tokens = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully RE'ed", "fully REed")
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
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")
            for forbidden in ("source-parity", "runtime-proven", "rebuild-parity"):
                if forbidden in present:
                    failures.append(f"{address} unexpectedly has {forbidden} tag")

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
            "00523df0\tOggVorbisStream__InitDecoder\t005241b5\t00524180\tOggVorbisStream__ReadPcmSamples\tUNCONDITIONAL_CALL",
            "00524180\tOggVorbisStream__ReadPcmSamples\t005246ca\t005246a0\tCOggFileRead__OpenFileAndPrimeDecoder\tUNCONDITIONAL_CALL",
            "00524180\tOggVorbisStream__ReadPcmSamples\t00524740\t00524710\tCOggFileRead__ReadDecodedPcm\tUNCONDITIONAL_CALL",
            "005245a0\tCOggFileRead__ctor_base\t004b6d60\t004b6d30\tCOggLoader__ctor_base\tUNCONDITIONAL_CALL",
            "005245a0\tCOggFileRead__ctor_base\t00528428\t005282b0\tPCPlatform__InitAsyncMusicStream\tUNCONDITIONAL_CALL",
            "005245e0\tCOggFileRead__scalar_deleting_dtor\t005e4a44\t<none>\t<no_function>\tDATA",
            "00524820\tCOggFileRead__GetChannelCount\t005e4a5c\t<none>\t<no_function>\tDATA",
        ),
        failures,
    )
    require_tokens(
        "target instructions",
        instructions,
        (
            "0x005246a0\t0x005246a0\tAFTER\t3\t0x005246a5\t0x005246a0\tCOggFileRead__OpenFileAndPrimeDecoder\tCALL\tdword ptr [EAX + 0xc]",
            "0x005246a0\t0x005246a0\tAFTER\t15\t0x005246ca\t0x005246a0\tCOggFileRead__OpenFileAndPrimeDecoder\tCALL\t0x00524180",
            "0x00524710\t0x00524710\tAFTER\t14\t0x00524740\t0x00524710\tCOggFileRead__ReadDecodedPcm\tCALL\t0x00524180",
            "0x00524710\t0x00524710\tAFTER\t15\t0x00524745\t0x00524710\tCOggFileRead__ReadDecodedPcm\tMOV\tECX, dword ptr [ESP + 0xc]",
            "0x00524710\t0x00524710\tAFTER\t23\t0x00524760\t0x00524710\tCOggFileRead__ReadDecodedPcm\tRET\t0xc",
            "0x00524800\t0x00524800\tTARGET\t0\t0x00524800\t0x00524800\tCOggFileRead__IsOpen\tMOV\tEDX, dword ptr [ECX + 0x2008]",
            "0x00524810\t0x00524810\tTARGET\t0\t0x00524810\t0x00524810\tCOggFileRead__GetSampleRate\tMOV\tEAX, dword ptr [ECX + 0x21d0]",
            "0x00524820\t0x00524820\tTARGET\t0\t0x00524820\t0x00524820\tCOggFileRead__GetChannelCount\tMOV\tEAX, dword ptr [ECX + 0x21cc]",
        ),
        failures,
    )
    require_tokens(
        "callsite instructions",
        callsites,
        (
            "0x004b6d60\t0x004b6d60\tTARGET\t0\t0x004b6d60\t0x004b6d30\tCOggLoader__ctor_base\tCALL\t0x005245a0",
            "0x00528428\t0x00528428\tTARGET\t0\t0x00528428\t0x005282b0\tPCPlatform__InitAsyncMusicStream\tCALL\t0x005245a0",
            "0x005246a5\t0x005246a5\tTARGET\t0\t0x005246a5\t0x005246a0\tCOggFileRead__OpenFileAndPrimeDecoder\tCALL\tdword ptr [EAX + 0xc]",
            "0x00524740\t0x00524740\tTARGET\t0\t0x00524740\t0x00524710\tCOggFileRead__ReadDecodedPcm\tCALL\t0x00524180",
        ),
        failures,
    )
    require_tokens(
        "vtable slots",
        vtables,
        (
            "005e4a44\t0\t005e4a44\t0x005245e0\t005245e0\t005245e0\tCOggFileRead__scalar_deleting_dtor",
            "005e4a44\t1\t005e4a48\t0x005246a0\t005246a0\t005246a0\tCOggFileRead__OpenFileAndPrimeDecoder",
            "005e4a44\t2\t005e4a4c\t0x00524710\t00524710\t00524710\tCOggFileRead__ReadDecodedPcm",
            "005e4a44\t3\t005e4a50\t0x00524770\t00524770\t00524770\tCOggFileRead__CloseAndReset",
            "005e4a44\t4\t005e4a54\t0x00524800\t00524800\t00524800\tCOggFileRead__IsOpen",
            "005e4a44\t5\t005e4a58\t0x00524810\t00524810\t00524810\tCOggFileRead__GetSampleRate",
            "005e4a44\t6\t005e4a5c\t0x00524820\t00524820\t00524820\tCOggFileRead__GetChannelCount",
            "005dc690\t2\t005dc698\t0x00524710\t00524710\t00524710\tCOggFileRead__ReadDecodedPcm",
        ),
        failures,
    )

    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3265,
        "undefinedSignatureCount": 1494,
        "paramSignatureCount": 1167,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    first_queue = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if first_queue.get("address") != "0x00527960" or first_queue.get("name") != "CFEPMultiplayerStart__SetCurrentSelection":
        failures.append(f"unexpected next queue head: {first_queue}")

    docs = {
        "public note": (PUBLIC_NOTE, ("Wave568", "OggVorbisStream__InitDecoder", "COggFileRead__ReadDecodedPcm", "3265")),
        "function index": (FUNCTION_INDEX, ("Wave568", "OggVorbisStream__ReadPcmSamples", "COggFileRead__GetChannelCount")),
        "OggLoader index": (OGG_INDEX, ("Wave568", "COggFileRead__OpenFileAndPrimeDecoder", "argument-order-corrected", "0x00524820")),
        "ghidra reference": (GHIDRA_REFERENCE, ("Wave568", "COggFileRead__ReadDecodedPcm", "OggVorbisStream__ReadPcmSamples")),
        "campaign": (CAMPAIGN, ("Wave568", "2828", "3265", "CFEPMultiplayerStart__SetCurrentSelection")),
        "backlog": (BACKLOG, ("Wave568", "Ogg/Vorbis", "COggFileRead__GetChannelCount")),
        "ledger": (LEDGER, ("Wave568", "0x00523df0,0x00524180,0x005245a0", "comment-backed proxy 2828/6093")),
    }
    for label, (path, tokens) in docs.items():
        require_tokens(label, read_text(path), tokens, failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation and exit nonzero on failure")
    args = parser.parse_args()

    failures = run_check()
    print("Ghidra Ogg/Vorbis Wave568 probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Status: PASS")
    print(f"Artifacts: {BASE}")
    print("Targets: 11")
    print("Queue: 6093 total, 2828 commented, 3265 commentless, 1494 undefined signatures, 1167 param_N signatures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
