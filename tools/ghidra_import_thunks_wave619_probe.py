#!/usr/bin/env python3
"""Validate Wave619 import-thunk Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave619-import-thunks"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_import_thunks_wave619_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
IMPORT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "import-thunks.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x0055d5e0": ("DirectSoundCreate8", "int __stdcall DirectSoundCreate8(void * pcGuidDevice, void * * ppDS8, void * pUnkOuter)", ("six-byte JMP", "0x005d802c", "CPCSoundManager__Init"), ("import-thunks-wave619", "directsound", "iat-005d802c")),
    "0x0055d5e6": ("DirectSoundEnumerateA", "int __stdcall DirectSoundEnumerateA(void * pDSEnumCallback, void * pContext)", ("0x005d8028", "DirectSoundEnumerateA", "CPCSoundManager__Init"), ("import-thunks-wave619", "directsound", "iat-005d8028")),
    "0x0055d5ec": ("AVIStreamWrite", "int __stdcall AVIStreamWrite(void * pavi, int lStart, int lSamples, void * lpBuffer, int cbBuffer, uint dwFlags, int * plSampWritten, int * plBytesWritten)", ("0x005d8018", "Vfw.h", "CDXEngine__CaptureAviFrame"), ("import-thunks-wave619", "vfw", "iat-005d8018")),
    "0x0055d5f2": ("uncompress", "int __cdecl uncompress(void * dest, uint * destLen, void * source, uint sourceLen)", ("0x005d83b8", "zlib", "__ReadLine compressed-read"), ("import-thunks-wave619", "zlib", "iat-005d83b8")),
    "0x0055d5f8": ("compress", "int __cdecl compress(void * dest, uint * destLen, void * source, uint sourceLen)", ("0x005d83bc", "zlib", "CDXMemBuffer__WriteBytes"), ("import-thunks-wave619", "zlib", "iat-005d83bc")),
    "0x0055d5fe": ("ogg_sync_wrote", "int __cdecl ogg_sync_wrote(void * oy, int bytes)", ("0x005d8354", "libogg", "OggVorbisStream__InitDecoder"), ("import-thunks-wave619", "ogg", "iat-005d8354")),
    "0x0055d604": ("ogg_sync_buffer", "char * __cdecl ogg_sync_buffer(void * oy, int size)", ("0x005d8358", "libogg", "OggVorbisStream__ReadPcmSamples"), ("import-thunks-wave619", "ogg", "iat-005d8358")),
    "0x0055d60a": ("ogg_stream_packetout", "int __cdecl ogg_stream_packetout(void * os, void * op)", ("0x005d8368", "libogg", "ogg_packet"), ("import-thunks-wave619", "ogg", "iat-005d8368")),
    "0x0055d610": ("ogg_stream_pagein", "int __cdecl ogg_stream_pagein(void * os, void * og)", ("0x005d8360", "libogg", "ogg_page"), ("import-thunks-wave619", "ogg", "iat-005d8360")),
    "0x0055d616": ("ogg_stream_init", "int __cdecl ogg_stream_init(void * os, int serialno)", ("0x005d8364", "libogg", "serial"), ("import-thunks-wave619", "ogg", "iat-005d8364")),
    "0x0055d61c": ("ogg_page_serialno", "int __cdecl ogg_page_serialno(void * og)", ("0x005d8370", "libogg", "page parsing"), ("import-thunks-wave619", "ogg", "iat-005d8370")),
    "0x0055d622": ("ogg_sync_pageout", "int __cdecl ogg_sync_pageout(void * oy, void * og)", ("0x005d8374", "libogg", "page"), ("import-thunks-wave619", "ogg", "iat-005d8374")),
    "0x0055d628": ("ogg_stream_clear", "int __cdecl ogg_stream_clear(void * os)", ("0x005d8378", "libogg", "COggFileRead__CloseAndReset"), ("import-thunks-wave619", "ogg", "iat-005d8378")),
    "0x0055d62e": ("ogg_sync_clear", "int __cdecl ogg_sync_clear(void * oy)", ("0x005d8350", "libogg", "COggFileRead"), ("import-thunks-wave619", "ogg", "iat-005d8350")),
    "0x0055d634": ("ogg_page_eos", "int __cdecl ogg_page_eos(void * og)", ("0x005d836c", "libogg", "end-of-stream"), ("import-thunks-wave619", "ogg", "iat-005d836c")),
    "0x0055d63a": ("ogg_sync_init", "int __cdecl ogg_sync_init(void * oy)", ("0x005d835c", "libogg", "OggVorbisStream__ReadPcmSamples"), ("import-thunks-wave619", "ogg", "iat-005d835c")),
    "0x0055d640": ("vorbis_block_init", "int __cdecl vorbis_block_init(void * v, void * vb)", ("0x005d8380", "libvorbis", "OggVorbisStream__InitDecoder"), ("import-thunks-wave619", "vorbis", "iat-005d8380")),
    "0x0055d646": ("vorbis_synthesis_init", "int __cdecl vorbis_synthesis_init(void * v, void * vi)", ("0x005d8384", "libvorbis", "OggVorbisStream__InitDecoder"), ("import-thunks-wave619", "vorbis", "iat-005d8384")),
    "0x0055d64c": ("vorbis_synthesis_headerin", "int __cdecl vorbis_synthesis_headerin(void * vi, void * vc, void * op)", ("0x005d838c", "libvorbis", "header"), ("import-thunks-wave619", "vorbis", "iat-005d838c")),
    "0x0055d652": ("vorbis_comment_init", "void __cdecl vorbis_comment_init(void * vc)", ("0x005d8394", "libvorbis", "vorbis_comment"), ("import-thunks-wave619", "vorbis", "iat-005d8394")),
    "0x0055d658": ("vorbis_info_init", "void __cdecl vorbis_info_init(void * vi)", ("0x005d8398", "libvorbis", "vorbis_info"), ("import-thunks-wave619", "vorbis", "iat-005d8398")),
    "0x0055d65e": ("vorbis_info_clear", "void __cdecl vorbis_info_clear(void * vi)", ("0x005d8390", "libvorbis", "COggFileRead__CloseAndReset"), ("import-thunks-wave619", "vorbis", "iat-005d8390")),
    "0x0055d664": ("vorbis_comment_clear", "void __cdecl vorbis_comment_clear(void * vc)", ("0x005d83a0", "libvorbis", "COggFileRead__dtor_body"), ("import-thunks-wave619", "vorbis", "iat-005d83a0")),
    "0x0055d66a": ("vorbis_dsp_clear", "void __cdecl vorbis_dsp_clear(void * v)", ("0x005d83a4", "libvorbis", "COggFileRead__CloseAndReset"), ("import-thunks-wave619", "vorbis", "iat-005d83a4")),
    "0x0055d670": ("vorbis_block_clear", "int __cdecl vorbis_block_clear(void * vb)", ("0x005d839c", "libvorbis", "COggFileRead__dtor_body"), ("import-thunks-wave619", "vorbis", "iat-005d839c")),
    "0x0055d676": ("vorbis_synthesis_read", "int __cdecl vorbis_synthesis_read(void * v, int samples)", ("0x005d8388", "libvorbis", "OggVorbisStream__ReadPcmSamples"), ("import-thunks-wave619", "vorbis", "iat-005d8388")),
    "0x0055d67c": ("vorbis_synthesis_pcmout", "int __cdecl vorbis_synthesis_pcmout(void * v, float * * * pcm)", ("0x005d83ac", "libvorbis", "float PCM"), ("import-thunks-wave619", "vorbis", "iat-005d83ac")),
    "0x0055d682": ("vorbis_synthesis_blockin", "int __cdecl vorbis_synthesis_blockin(void * v, void * vb)", ("0x005d83a8", "libvorbis", "OggVorbisStream__ReadPcmSamples"), ("import-thunks-wave619", "vorbis", "iat-005d83a8")),
    "0x0055d688": ("vorbis_synthesis", "int __cdecl vorbis_synthesis(void * vb, void * op)", ("0x005d83b0", "libvorbis", "ogg_packet"), ("import-thunks-wave619", "vorbis", "iat-005d83b0")),
    "0x0055d68e": ("VerQueryValueA", "BOOL __stdcall VerQueryValueA(LPCVOID pBlock, LPCSTR lpSubBlock, LPVOID * lplpBuffer, PUINT puLen)", ("0x005d82e0", "winver.h", "CLTShell__WinMain"), ("import-thunks-wave619", "version-api", "signature-retained")),
    "0x0055d694": ("GetFileVersionInfoA", "BOOL __stdcall GetFileVersionInfoA(LPCSTR lptstrFilename, DWORD dwHandle, DWORD dwLen, LPVOID lpData)", ("0x005d82dc", "winver.h", "CLTShell__WinMain"), ("import-thunks-wave619", "version-api", "signature-retained")),
    "0x0055d69a": ("GetFileVersionInfoSizeA", "DWORD __stdcall GetFileVersionInfoSizeA(LPCSTR lptstrFilename, LPDWORD lpdwHandle)", ("0x005d82d8", "0x0055d6a0", "CRT__SehPopExceptionFrameAndJump"), ("import-thunks-wave619", "version-api", "island-tail")),
}

OVERCLAIM_TOKENS = (
    "runtime audio proven",
    "runtime video proven",
    "runtime compression proven",
    "library version proven",
    "fully recovered",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_clean_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back signature mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    clean_expectations = {
        "apply-wave619-dry.log": {"updated": 0, "skipped": 32, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave619-apply.log": {"updated": 32, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave619-final-dry.log": {"updated": 0, "skipped": 32, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    }
    for name, expected in clean_expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=32 found=32 missing=0",),
        "post-context-tags.log": ("rows=32 missing=0",),
        "post-context-xrefs.log": ("Wrote 61 rows",),
        "post-context-instructions.log": ("Wrote 96 instruction rows", "targets=32 missing=0"),
        "post-context-decompile.log": ("targets=32 dumped=32 missing=0 failed=0",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3217",),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_and_edges(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 32:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 32")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, tag_tokens) in TARGETS.items():
        row = by_address.get(address)
        if not row:
            failures.append(f"post-context-metadata missing {address}")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} status mismatch: {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in tag_tokens:
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    instructions = read_text(BASE / "post-context-instructions.tsv")
    for token in (
        "0x0055d5e0\t0x0055d5e0\tTARGET\t0\t0x0055d5e0\t0x0055d5e0\tDirectSoundCreate8\tJMP\tdword ptr [0x005d802c]",
        "0x0055d5ec\t0x0055d5ec\tTARGET\t0\t0x0055d5ec\t0x0055d5ec\tAVIStreamWrite\tJMP\tdword ptr [0x005d8018]",
        "0x0055d67c\t0x0055d67c\tTARGET\t0\t0x0055d67c\t0x0055d67c\tvorbis_synthesis_pcmout\tJMP\tdword ptr [0x005d83ac]",
        "0x0055d69a\t0x0055d69a\tAFTER\t1\t0x0055d6a0\t0x0055d6a0\tCRT__SehPopExceptionFrameAndJump\tPUSH\tEBP",
    ):
        require_tokens("post-context-instructions.tsv", instructions, (token,), failures)

    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0055d5e0\tDirectSoundCreate8\t00516aec\t005169b0\tCPCSoundManager__Init",
        "0055d5ec\tAVIStreamWrite\t005141ad\t005140e0\tCDXEngine__CaptureAviFrame",
        "0055d5f2\tuncompress\t00548918\t00548820\tCDXMemBuffer__ReadLine",
        "0055d67c\tvorbis_synthesis_pcmout\t0052428d\t00524180\tOggVorbisStream__ReadPcmSamples",
        "0055d69a\tGetFileVersionInfoSizeA\t0051216f\t00512130\tCLTShell__WinMain",
    ):
        require_tokens("post-context-xrefs.tsv", xrefs, (token,), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    expected_backup = {
        "BackupPath": "G:\\GhidraBackups\\BEA_20260520-032435_post_wave619_import_thunks_verified",
        "SourceFileCount": 19,
        "BackupFileCount": 19,
        "SourceBytes": 161745799,
        "BackupBytes": 161745799,
        "DiffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 2876,
        "undefinedSignatureCount": 1218,
        "paramSignatureCount": 1056,
        "legacyWeakNameCount": 0,
        "uncertainOwnerNameCount": 0,
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 0,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055d6a0" or head.get("name") != "CRT__SehPopExceptionFrameAndJump":
        failures.append(f"queue head mismatch: {head}")


def check_docs(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: ("Wave619", "0x0055d6a0 CRT__SehPopExceptionFrameAndJump", "3169/6093 = 52.01%"),
        FUNCTION_INDEX: ("Latest saved-correction note: Wave619", "import-thunks.md", "3217/6093 = 52.80%"),
        IMPORT_DOC: ("## Wave619 Static Read-Back Note", "DirectSoundCreate8", "vorbis_synthesis_pcmout", "0x0055d6a0 CRT__SehPopExceptionFrameAndJump"),
        CAMPAIGN: ("after Wave619", "Current import-thunk follow-up", "2876"),
        BACKLOG: ("Ghidra import-thunk Wave619", "ApplyImportThunksWave619.java", "DiffCount=0"),
        LEDGER: ("Ghidra import-thunk Wave619", "0x0055d6a0 CRT__SehPopExceptionFrameAndJump", "Runtime audio/video/compression"),
        ATTEMPT_LOG: ("\"attempt_id\":20274", "Ghidra import-thunk Wave619", "\"readback\":\"verified\""),
        PACKAGE_JSON: ("test:ghidra-import-thunks-wave619", "tools\\\\ghidra_import_thunks_wave619_probe.py --check"),
    }
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20275:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    if tracking.get("counters", {}).get("ledger_rows") != 1015:
        failures.append("tracking ledger_rows mismatch")
    if tracking.get("counters", {}).get("attempt_rows") != 20275:
        failures.append("tracking attempt_rows mismatch")
    if "Wave619 import-thunk hardening" not in tracking.get("current_focus", ""):
        failures.append("tracking current_focus missing Wave619")

    for path, tokens in doc_tokens.items():
        text = read_text(path)
        require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.relative_to(ROOT)} overclaims: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    for step in (
        check_logs,
        check_metadata_tags_and_edges,
        check_backup_and_queue,
        check_docs,
    ):
        try:
            step(failures)
        except Exception as exc:  # pragma: no cover - command-line probe reports all hard failures.
            failures.append(f"{step.__name__} raised {exc.__class__.__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave619 import-thunk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave619 import-thunk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
