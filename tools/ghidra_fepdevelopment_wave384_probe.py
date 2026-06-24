#!/usr/bin/env python3
"""Validate the Wave384 CFEPDevelopment Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/fepdevelopment-wave384/current")
OUTPUT_NAME = "fepdevelopment-wave384.json"

COMMON_TAGS = {
    "static-reaudit",
    "fepdevelopment-wave384",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    stale_tokens: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
        "staleTokens": stale_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00458050": target(
        "CFEPDevelopment__CompareWorldFileNamePtrs",
        "int __cdecl CFEPDevelopment__CompareWorldFileNamePtrs(char * * left, char * * right)",
        [
            "Wave384 boundary recovery",
            "qsort comparator",
            "char** element pointers",
            "strcmp-style ordering",
            "runtime menu behavior remain unproven",
        ],
        ["CFEPDevelopment__CompareWorldFileNamePtrs", "left", "right", "return 0"],
        ["fepdevelopment", "world-list", "sort-comparator", "function-boundary", "signature-hardened", "comment-hardened"],
    ),
    "0x00458090": target(
        "CFEPDevelopment__EnumerateWorldFiles",
        "bool __fastcall CFEPDevelopment__EnumerateWorldFiles(void * this)",
        [
            "Wave384 boundary correction",
            "moved the saved boundary back from 0x00458100",
            "FindFirstFileA/FindNextFileA",
            "CFEPDevelopment__CompareWorldFileNamePtrs",
            "No source body is present",
            "runtime world-list behavior, and rebuild parity remain unproven",
        ],
        [
            "CFEPDevelopment__EnumerateWorldFiles",
            "FindNextFileA",
            "FindClose",
            "Sort__QuickSortGeneric",
            "CFEPDevelopment__CompareWorldFileNamePtrs",
        ],
        ["fepdevelopment", "world-list", "function-boundary", "boundary-corrected", "signature-hardened", "comment-hardened"],
        ["unaff_EBP", "unaff_EBX", "unaff_EDI", "Unknown calling convention", "bool CFEPDevelopment__EnumerateWorldFiles(void)"],
    ),
    "0x004581e0": target(
        "CFEPDevelopment__Shutdown",
        "void __fastcall CFEPDevelopment__Shutdown(void * this)",
        [
            "Wave384 comment hardening",
            "frees each allocated world-list filename entry",
            "clears this+0x04 and this+0x08",
            "runtime shutdown behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__Shutdown", "OID__FreeObject", "+ 4", "+ 8"],
        ["fepdevelopment", "world-list", "shutdown", "comment-hardened"],
    ),
    "0x004583c0": target(
        "CFEPDevelopment__RenderWorldListEntries",
        "void __fastcall CFEPDevelopment__RenderWorldListEntries(void * this)",
        [
            "Wave384 comment hardening",
            "ASCII filename to a wide scratch string",
            "highlights the selected index",
            "second column after 0x0f rows",
            "visual runtime behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__RenderWorldListEntries", "Text__AsciiToWideScratch", "CDXFont__DrawTextDynamic"],
        ["fepdevelopment", "world-list", "rendering", "comment-hardened"],
    ),
    "0x004584d0": target(
        "CFEPDevelopment__Render",
        "void __thiscall CFEPDevelopment__Render(void * this, float transition, int dest)",
        [
            "Wave384 calling-convention correction",
            "render is thiscall, not stdcall",
            "RET 0x8",
            "CFEPDevelopment__RenderWorldListEntries",
            "visual runtime behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__Render", "CFEPDevelopment__RenderWorldListEntries(this)"],
        ["fepdevelopment", "rendering", "calling-convention-corrected", "signature-hardened", "comment-hardened"],
        ["void CFEPDevelopment__Render(void *this,float transition,int dest)", "in_ECX"],
    ),
    "0x00458710": target(
        "CFEPDevelopment__RefreshWorldListCore",
        "bool __fastcall CFEPDevelopment__RefreshWorldListCore(void * this)",
        [
            "Wave384 comment hardening",
            "storage-device state",
            "save/load mode",
            "boolean-like handled result",
            "runtime storage-device behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__RefreshWorldListCore", "PCPlatform__GetStorageDeviceInfo", "CFrontEnd__SetPage"],
        ["fepdevelopment", "storage-device", "save-list", "comment-hardened"],
    ),
    "0x004589f0": target(
        "CFEPDevelopment__RefreshWorldList",
        "void __fastcall CFEPDevelopment__RefreshWorldList(void * this)",
        [
            "Wave384 comment hardening",
            "pushes a zero refresh argument",
            "CFEPDevelopment__RefreshWorldListCore",
            "caller page-action semantics, runtime behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__RefreshWorldList", "CFEPDevelopment__ResolveActiveStorageDevice(this,0)", "CFEPDevelopment__RefreshWorldListCore(this)"],
        ["fepdevelopment", "storage-device", "save-list", "comment-hardened"],
        ["in_EDX"],
    ),
    "0x00458ce0": target(
        "CFEPDevelopment__ResolveActiveStorageDevice",
        "void __thiscall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int unused_refresh_arg)",
        [
            "Wave384 calling-convention correction",
            "thiscall with one stack argument and RET 0x4, not fastcall",
            "all observed callsites push 0",
            "storage-device fields at this+0x08/+0x0c/+0x10",
            "exact unused argument semantics, source identity, runtime storage behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__ResolveActiveStorageDevice", "unused_refresh_arg", "+ 0x10", "+ 0xc"],
        ["fepdevelopment", "storage-device", "calling-convention-corrected", "signature-hardened", "comment-hardened"],
        ["__fastcall CFEPDevelopment__ResolveActiveStorageDevice", "force_refresh", "in_EDX"],
    ),
    "0x00459580": target(
        "CFEPDevelopment__ScheduleWorldListRefresh",
        "void __thiscall CFEPDevelopment__ScheduleWorldListRefresh(void * this, int ignored_arg)",
        [
            "Wave384 calling-convention correction",
            "thiscall with one ignored stack argument and RET 0x4",
            "not fastcall",
            "this+0x04",
            "runtime timer behavior, and rebuild parity remain unproven",
        ],
        ["CFEPDevelopment__ScheduleWorldListRefresh", "ignored_arg", "CFEPDevelopment__ResolveActiveStorageDevice(this,0)"],
        ["fepdevelopment", "storage-device", "timer", "calling-convention-corrected", "signature-hardened", "comment-hardened"],
        ["__fastcall CFEPDevelopment__ScheduleWorldListRefresh", "force_refresh"],
    ),
}

BOUNDARY_GUARDS = {
    "0x00458100": "old partial CFEPDevelopment__EnumerateWorldFiles boundary must be absent after Wave384",
}

INSTRUCTION_EVIDENCE = [
    ("0x00458050", "0x00458050", "MOV", "EAX, dword ptr [ESP + 0x8]", "8b 44 24 08"),
    ("0x00458050", "0x00458086", "RET", "", "c3"),
    ("0x00458090", "0x00458090", "SUB", "ESP, 0x15c", "81 ec 5c 01 00 00"),
    ("0x00458090", "0x0045809d", "MOV", "EBP, ECX", "8b e9"),
    ("0x00458090", "0x00458100", "PUSH", "0x62921c", "68 1c 92 62 00"),
    ("0x00458090", "0x004581bd", "PUSH", "0x458050", "68 50 80 45 00"),
    ("0x004584d0", "0x004584d1", "MOV", "ESI, ECX", "8b f1"),
    ("0x004584d0", "0x00458520", "RET", "0x8", "c2 08 00"),
    ("0x004589f0", "0x004589f3", "PUSH", "0x0", "6a 00"),
    ("0x004589f0", "0x004589f5", "CALL", "0x00458ce0", "e8 e6 02 00 00"),
    ("0x00458ce0", "0x00458df5", "RET", "0x4", "c2 04 00"),
    ("0x00459580", "0x00459583", "PUSH", "0x0", "6a 00"),
    ("0x00459580", "0x0045959e", "RET", "0x4", "c2 04 00"),
]

CALLSITE_EVIDENCE = [
    ("0x004589f5", "PUSH", "0x0"),
    ("0x004589f5", "CALL", "0x00458ce0"),
    ("0x00459585", "PUSH", "0x0"),
    ("0x00459585", "CALL", "0x00458ce0"),
    ("0x0046242c", "CALL", "0x004589f0"),
    ("0x004624ea", "CALL", "0x004589f0"),
    ("0x00462556", "CALL", "0x004589f0"),
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime proof",
    "rebuild parity proven",
    "exact source identity proven",
    "complete source identity",
]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if not value or value in {"<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key, value in list(row.items()):
            row[key] = unescape_tsv(value or "")
    return rows


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def decompile_text_for(decompile_dir: Path, address: str) -> str:
    prefix = normalize_address(address)[2:]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in decompile_dir.glob(f"{prefix}_*.c")
    )


def has_summary(
    text: str,
    *,
    updated: int,
    skipped: int,
    created: int,
    would_create: int,
    boundary_moved: int,
    would_boundary_move: int,
    renamed: int,
    would_rename: int,
) -> bool:
    pattern = (
        rf"SUMMARY:\s+updated={updated}\s+skipped={skipped}\s+created={created}\s+"
        rf"would_create={would_create}\s+boundary_moved={boundary_moved}\s+"
        rf"would_boundary_move={would_boundary_move}\s+renamed={renamed}\s+"
        rf"would_rename={would_rename}\s+missing=0\s+bad=0"
    )
    return re.search(pattern, text) is not None


def evidence_hit(
    rows: list[dict[str, str]],
    *,
    target: str,
    instruction_addr: str,
    mnemonic: str,
    operands: str,
    bytes_: str,
) -> bool:
    expected_target = normalize_address(target)
    expected_instruction = normalize_address(instruction_addr)
    return any(
        normalize_address(row.get("target_addr", "")) == expected_target
        and normalize_address(row.get("instruction_addr", "")) == expected_instruction
        and row.get("mnemonic") == mnemonic
        and row.get("operands") == operands
        and row.get("bytes") == bytes_
        for row in rows
    )


def callsite_hit(rows: list[dict[str, str]], *, target: str, mnemonic: str, operands: str) -> bool:
    expected_target = normalize_address(target)
    return any(
        normalize_address(row.get("target_addr", "")) == expected_target
        and row.get("mnemonic") == mnemonic
        and row.get("operands") == operands
        for row in rows
    )


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    instructions_path: Path | None = None,
    callsite_instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "fepdevelopment_wave384_dry.log"
    apply_log_path = apply_log_path or root / "fepdevelopment_wave384_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    callsite_instructions_path = callsite_instructions_path or root / "callsite_instructions_wave384.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_log = read_text(dry_log_path)
    apply_log = read_text(apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    tag_rows = read_tsv(tags_path)
    instruction_rows = read_tsv(instructions_path)
    callsite_rows = read_tsv(callsite_instructions_path)

    target_count = len(TARGETS)
    if not has_summary(
        dry_log,
        updated=0,
        skipped=8,
        created=0,
        would_create=1,
        boundary_moved=0,
        would_boundary_move=1,
        renamed=0,
        would_rename=0,
    ):
        failures.append("dry-run summary did not prove expected create/boundary move plan")
    if not has_summary(
        apply_log,
        updated=target_count,
        skipped=0,
        created=1,
        would_create=0,
        boundary_moved=1,
        would_boundary_move=0,
        renamed=0,
        would_rename=0,
    ):
        failures.append("apply summary did not prove expected create/boundary move results")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing Ghidra save success")
    if "LockException" in dry_log or "LockException" in apply_log:
        failures.append("Ghidra log contains LockException")

    metadata_by_address = {normalize_address(row.get("address", "")): row for row in metadata_rows}
    tags_by_address = {normalize_address(row.get("address", "")): row for row in tag_rows}

    for address, reason in BOUNDARY_GUARDS.items():
        row = metadata_by_address.get(normalize_address(address))
        if row is None:
            failures.append(f"missing boundary guard metadata row for {address}: {reason}")
        elif row.get("status") != "MISSING":
            failures.append(f"boundary guard failed for {address}: expected MISSING, got {row.get('status')}")

    for address, spec in TARGETS.items():
        row = metadata_by_address.get(normalize_address(address))
        if row is None:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status mismatch for {address}: {row.get('status')}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"signature mismatch for {address}: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if str(token) not in comment:
                failures.append(f"missing comment token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                failures.append(f"comment overclaim for {address}: {token}")

        tag_row = tags_by_address.get(normalize_address(address))
        if tag_row is None or tag_row.get("status") != "OK":
            failures.append(f"missing tag row for {address}")
        else:
            observed_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing_tags = expected_tags - observed_tags
            if missing_tags:
                failures.append(f"missing tags for {address}: {sorted(missing_tags)}")

        decompile_text = decompile_text_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"missing decompile output for {address}")
        for token in spec["decompileTokens"]:
            if str(token) not in decompile_text:
                failures.append(f"missing decompile token for {address}: {token}")
        for token in spec["staleTokens"]:
            if str(token) in decompile_text:
                failures.append(f"stale decompile token for {address}: {token}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if evidence_hit(
            instruction_rows,
            target=target_addr,
            instruction_addr=instruction_addr,
            mnemonic=mnemonic,
            operands=operands,
            bytes_=bytes_,
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instruction_addr} {mnemonic} {operands} {bytes_}")

    callsite_hits = 0
    for target_addr, mnemonic, operands in CALLSITE_EVIDENCE:
        if callsite_hit(callsite_rows, target=target_addr, mnemonic=mnemonic, operands=operands):
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {target_addr} {mnemonic} {operands}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": target_count,
            "boundaryGuards": len(BOUNDARY_GUARDS),
            "instructionEvidenceHits": instruction_hits,
            "callsiteEvidenceHits": callsite_hits,
        },
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "tags": relative(tags_path),
            "instructions": relative(instructions_path),
            "callsiteInstructions": relative(callsite_instructions_path),
            "decompileDir": relative(decompile_dir),
        },
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true", help="Return non-zero when the report fails")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if report["status"] == "PASS":
        print(f"PASS: Wave384 CFEPDevelopment tranche validated -> {relative(out_path)}")
        return 0
    print(f"FAIL: Wave384 CFEPDevelopment tranche validation failed -> {relative(out_path)}")
    for failure in report["failures"]:
        print(f"- {failure}")
    return 1 if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
