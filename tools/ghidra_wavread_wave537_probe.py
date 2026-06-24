#!/usr/bin/env python3
"""Validate Wave537 WavRead Ghidra metadata and boundary recovery."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave537-wavread-00505210"
COMMON_TAGS = {
    "static-reaudit",
    "wavread-wave537",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
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
    "0x00505210": target(
        "WavRead__ReadMMIO",
        "int __cdecl WavRead__ReadMMIO(void * hmmio, void * riff_chunk, void * * wave_format_out)",
        ["mmioDescend", "RIFF/WAVE/fmt", "WAVEFORMATEX", "rebuild parity remain unproven"],
        ["wavread", "riff-wave", "mmio", "format-parser"],
        ["mmioDescend", "mmioRead", "CDXMemoryManager__Free"],
    ),
    "0x005053d0": target(
        "WavRead__WaveReadFile",
        "int __cdecl WavRead__WaveReadFile(void * hmmio, uint byte_count, byte * out_buffer, void * data_chunk, uint * bytes_read_out)",
        ["mmioGetInfo", "mmioAdvance", "bytes_read_out", "rebuild parity remain unproven"],
        ["wavread", "mmio", "data-reader", "buffer-copy"],
        ["mmioGetInfo", "mmioAdvance", "mmioSetInfo"],
    ),
    "0x005054a0": target(
        "CWaveSoundRead__Constructor",
        "void __fastcall CWaveSoundRead__Constructor(void * this)",
        ["vtable 0x005dfc4c", "this+0x04", "rebuild parity remain unproven"],
        ["wavread", "constructor", "vtable-readback"],
        ["PTR_CWaveSoundRead__ScalarDeletingDestructor_005dfc4c"],
    ),
    "0x005054b0": target(
        "CWaveSoundRead__HasFormat",
        "bool __fastcall CWaveSoundRead__HasFormat(void * this)",
        ["vtable 0x005dfc4c slot 4", "WAVEFORMATEX pointer at this+0x04", "rebuild parity remain unproven"],
        ["wavread", "created-function", "vtable-readback", "format-state"],
        ["return *(int *)((int)this + 4) != 0"],
    ),
    "0x005054c0": target(
        "CWaveSoundRead__GetSampleRate",
        "uint __fastcall CWaveSoundRead__GetSampleRate(void * this)",
        ["vtable 0x005dfc4c slot 5", "WAVEFORMATEX+0x04", "rebuild parity remain unproven"],
        ["wavread", "created-function", "vtable-readback", "format-field"],
        ["return *(uint *)(*(int *)((int)this + 4) + 4)"],
    ),
    "0x005054d0": target(
        "CWaveSoundRead__GetChannelCount",
        "uint __fastcall CWaveSoundRead__GetChannelCount(void * this)",
        ["vtable 0x005dfc4c slot 6", "WAVEFORMATEX+0x02", "rebuild parity remain unproven"],
        ["wavread", "created-function", "vtable-readback", "format-field"],
        ["return (uint)*(ushort *)(*(int *)((int)this + 4) + 2)"],
    ),
    "0x005054e0": target(
        "CWaveSoundRead__ScalarDeletingDestructor",
        "void * __thiscall CWaveSoundRead__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["vtable 0x005dfc4c slot 0", "RET 0x4", "delete_flags", "rebuild parity remain unproven"],
        ["wavread", "destructor", "scalar-deleting-destructor", "renamed", "vtable-readback"],
        ["CWaveSoundRead__Close", "delete_flags", "CDXMemoryManager__Free"],
    ),
    "0x00505500": target(
        "CWaveSoundRead__Close",
        "void __fastcall CWaveSoundRead__Close(void * this)",
        ["mmio close import", "this+0x08", "this+0x04", "rebuild parity remain unproven"],
        ["wavread", "close", "mmio", "vtable-transition"],
        ["mmioClose", "CDXMemoryManager__Free", "PTR_CWaveSoundRead__BaseScalarDeletingDestructor_005dfc6c"],
    ),
    "0x00505570": target(
        "CWaveSoundRead__BaseConstructor",
        "void __fastcall CWaveSoundRead__BaseConstructor(void * this)",
        ["base vtable 0x005dfc6c", "purecall slots", "rebuild parity remain unproven"],
        ["wavread", "constructor", "base-vtable", "vtable-readback"],
        ["PTR_CWaveSoundRead__BaseScalarDeletingDestructor_005dfc6c"],
    ),
    "0x00505580": target(
        "CWaveSoundRead__BaseScalarDeletingDestructor",
        "void * __thiscall CWaveSoundRead__BaseScalarDeletingDestructor(void * this, byte delete_flags)",
        ["base vtable 0x005dfc6c slot 0", "RET 0x4", "delete_flags", "rebuild parity remain unproven"],
        ["wavread", "created-function", "destructor", "scalar-deleting-destructor", "base-vtable", "vtable-readback"],
        ["delete_flags", "PTR_CWaveSoundRead__BaseScalarDeletingDestructor_005dfc6c", "CDXMemoryManager__Free"],
    ),
    "0x005055b0": target(
        "CWaveSoundRead__Open",
        "int __thiscall CWaveSoundRead__Open(void * this, char * filename)",
        ["RET 0x4", "mmioOpenA", "WavRead__ReadMMIO", "rebuild parity remain unproven"],
        ["wavread", "open", "mmio", "riff-wave", "vtable-readback"],
        ["mmioOpenA", "WavRead__ReadMMIO", "mmioDescend"],
    ),
    "0x00505680": target(
        "CWaveSoundRead__Read",
        "int __thiscall CWaveSoundRead__Read(void * this, uint byte_count, byte * out_buffer, uint * bytes_read_out)",
        ["vtable 0x005dfc4c slot 2", "RET 0x0c", "WavRead__WaveReadFile", "rebuild parity remain unproven"],
        ["wavread", "created-function", "read-wrapper", "mmio", "vtable-readback"],
        ["WavRead__WaveReadFile", "byte_count", "bytes_read_out"],
    ),
    "0x005056b0": target(
        "CWaveSoundRead__CloseHandle",
        "int __fastcall CWaveSoundRead__CloseHandle(void * this)",
        ["vtable 0x005dfc4c slot 3", "mmio close import", "this+0x08", "rebuild parity remain unproven"],
        ["wavread", "created-function", "mmio", "handle-close", "vtable-readback"],
        ["mmioClose", "return 0"],
    ),
}

EXPECTED_XREFS = {
    ("0x00505210", "00505607", "CWaveSoundRead__Open"),
    ("0x005053d0", "00505697", "CWaveSoundRead__Read"),
    ("0x005054a0", "00516a16", "CPCSoundManager__Init"),
    ("0x005054b0", "005dfc5c", "<no_function>"),
    ("0x005054c0", "005dfc60", "<no_function>"),
    ("0x005054d0", "005dfc64", "<no_function>"),
    ("0x005054e0", "005dfc4c", "<no_function>"),
    ("0x00505500", "005054e3", "CWaveSoundRead__ScalarDeletingDestructor"),
    ("0x00505570", "005d5843", "Unwind@005d5840"),
    ("0x00505580", "005dfc6c", "<no_function>"),
    ("0x005055b0", "005dfc50", "<no_function>"),
    ("0x00505680", "005dfc54", "<no_function>"),
    ("0x005056b0", "005dfc58", "<no_function>"),
}

EXPECTED_VTABLES = {
    ("005dfc4c", "0", "005054e0", "CWaveSoundRead__ScalarDeletingDestructor", "OK"),
    ("005dfc4c", "1", "005055b0", "CWaveSoundRead__Open", "OK"),
    ("005dfc4c", "2", "00505680", "CWaveSoundRead__Read", "OK"),
    ("005dfc4c", "3", "005056b0", "CWaveSoundRead__CloseHandle", "OK"),
    ("005dfc4c", "4", "005054b0", "CWaveSoundRead__HasFormat", "OK"),
    ("005dfc4c", "5", "005054c0", "CWaveSoundRead__GetSampleRate", "OK"),
    ("005dfc4c", "6", "005054d0", "CWaveSoundRead__GetChannelCount", "OK"),
    ("005dfc6c", "0", "00505580", "CWaveSoundRead__BaseScalarDeletingDestructor", "OK"),
    ("005dfc6c", "1", "0055df1f", "CRT__Purecall_0055df1f", "OK"),
    ("005dfc6c", "2", "0055df1f", "CRT__Purecall_0055df1f", "OK"),
    ("005dfc6c", "3", "0055df1f", "CRT__Purecall_0055df1f", "OK"),
    ("005dfc6c", "4", "0055df1f", "CRT__Purecall_0055df1f", "OK"),
    ("005dfc6c", "5", "0055df1f", "CRT__Purecall_0055df1f", "OK"),
    ("005dfc6c", "6", "0055df1f", "CRT__Purecall_0055df1f", "OK"),
}

EXPECTED_APPLY = {
    "updated": 13,
    "skipped": 0,
    "renamed": 1,
    "would_rename": 0,
    "created": 6,
    "would_create": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 13,
    "renamed": 0,
    "would_rename": 0,
    "created": 0,
    "would_create": 0,
    "missing": 0,
    "bad": 0,
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
        for key in ("address", "target_addr"):
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


def decompile_text_for(address: str) -> str:
    directory = BASE / "post_decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+"
        r"created=(\d+)\s+would_create=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "renamed", "would_rename", "created", "would_create", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_metadata(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
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
                failures.append(f"{address}: comment missing token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
        else:
            actual = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing = sorted(set(spec["tags"]) - actual)  # type: ignore[arg-type]
            if missing:
                failures.append(f"{address}: missing tags {missing}")


def check_decompile(failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text_for(address)
        if not text:
            failures.append(f"{address}: missing post decompile")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: decompile overclaim token present {token!r}")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    actual = {
        (row.get("target_addr", ""), row.get("from_addr", "").lower(), row.get("from_function", ""))
        for row in rows
    }
    for target_addr, from_addr, from_function in EXPECTED_XREFS:
        key = (normalize_address(target_addr), from_addr.lower(), from_function)
        if key not in actual:
            failures.append(f"{target_addr}: missing xref from {from_addr} / {from_function}")


def check_vtables(failures: list[str]) -> None:
    rows = read_tsv(BASE / "post_vtables.tsv")
    actual = {
        (row.get("vtable", "").lower(), row.get("slot_index", ""), row.get("pointer_addr", "").lower(),
         row.get("function_name", ""), row.get("status", ""))
        for row in rows
    }
    for vtable, slot_index, pointer_addr, function_name, status in EXPECTED_VTABLES:
        key = (vtable.lower(), slot_index, pointer_addr.lower(), function_name, status)
        if key not in actual:
            failures.append(f"vtable {vtable} slot {slot_index}: missing {pointer_addr} / {function_name} / {status}")


def check_logs(failures: list[str]) -> None:
    apply_log = read_text(BASE / "apply_wavread_wave537_apply.log")
    verify_log = read_text(BASE / "apply_wavread_wave537_verify_dry.log")
    if parse_summary(apply_log) != EXPECTED_APPLY:
        failures.append("apply log summary mismatch")
    if parse_summary(verify_log) != EXPECTED_VERIFY_DRY:
        failures.append("verify-dry log summary mismatch")
    for label, text in (("apply", apply_log), ("verify-dry", verify_log)):
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{label} log missing save-success marker")
        for token in ("FAIL:", "Exception", "LockException", "BADNAME:", "MISSING:"):
            if token in text:
                failures.append(f"{label} log unexpected token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    _ = parser.parse_args()

    failures: list[str] = []
    check_metadata(failures)
    check_decompile(failures)
    check_xrefs(failures)
    check_vtables(failures)
    check_logs(failures)

    if failures:
        print("Wave537 WavRead probe FAILED:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"Wave537 WavRead probe PASS: {len(TARGETS)} functions, {len(EXPECTED_VTABLES)} vtable slots, logs and xrefs verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
