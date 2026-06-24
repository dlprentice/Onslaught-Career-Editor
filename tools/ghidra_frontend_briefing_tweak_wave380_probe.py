#!/usr/bin/env python3
"""Validate the Wave380 frontend briefing/tweak Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-briefing-wave380/current")
OUTPUT_NAME = "frontend-briefing-tweak-wave380.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-briefing-tweak-wave380",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00452430": target(
        "CFEPBriefing__ResetTimerAndClearState",
        "void __thiscall CFEPBriefing__ResetTimerAndClearState(void * this, int reset_state)",
        [
            "Name/signature correction",
            "vtable slot",
            "PLATFORM__GetSysTimeFloat",
            "this+0x04",
            "clears this+0x08",
            "runtime briefing behavior, and rebuild parity remain unproven",
        ],
        ["CFEPBriefing__ResetTimerAndClearState", "PLATFORM__GetSysTimeFloat", "_DAT_005db3b4", "+ 8", "+ 4"],
        ["frontend", "briefing", "timer", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004530a0": target(
        "CTweak__dtor_base_thunk_004530a0",
        "void __fastcall CTweak__dtor_base_thunk_004530a0(void * this)",
        [
            "Name/signature correction",
            "one-instruction jump thunk",
            "CTweak__dtor_base",
            "0x005286b0",
            "runtime tweak cleanup, and rebuild parity remain unproven",
        ],
        ["CTweak__dtor_base_thunk_004530a0", "DAT_0089c018", "return"],
        ["frontend", "tweak", "destructor", "thunk", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00528690": target(
        "CTweak__ctor_base",
        "void * __thiscall CTweak__ctor_base(void * this, void * callback_context)",
        [
            "Name/signature correction",
            "constructor-style CTweak base body",
            "stores callback_context at this+0x08",
            "links this into the DAT_0089c018 global tweak list",
            "runtime tweak registration, and rebuild parity remain unproven",
        ],
        ["CTweak__ctor_base", "callback_context", "PTR_CRT__Purecall_0055df1f_005e4a94", "DAT_0089c018"],
        ["tweak", "constructor", "global-list", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x005286b0": target(
        "CTweak__dtor_base",
        "void __fastcall CTweak__dtor_base(void * this)",
        [
            "Name/signature correction",
            "not a constructor",
            "unlinks this from the DAT_0089c018 global tweak list",
            "resets the CTweak base vtable",
            "runtime tweak cleanup, and rebuild parity remain unproven",
        ],
        ["CTweak__dtor_base", "DAT_0089c018", "+ 4", "return"],
        ["tweak", "destructor", "global-list", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00528b20": target(
        "CTweakInt_SetNumViewpoints__ctor",
        "void * __thiscall CTweakInt_SetNumViewpoints__ctor(void * this, void * callback_context, int initial_value)",
        [
            "Name/signature correction",
            "derived CTweak integer constructor",
            "PTR_CEngine__SetNumViewpoints_005e4aa4",
            "initial_value at this+0x0c",
            "runtime viewpoint tweak behavior, and rebuild parity remain unproven",
        ],
        [
            "CTweakInt_SetNumViewpoints__ctor",
            "callback_context",
            "initial_value",
            "PTR_CEngine__SetNumViewpoints_005e4aa4",
            "+ 0xc",
        ],
        ["tweak", "engine", "viewpoint", "constructor", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00452430", "0x005dba00", "<no_function>", "DATA"),
    ("0x004530a0", "0x00453095", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004530a0", "0x00550865", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00528690", "0x00527c99", "CReconnectInterface__ctor", "UNCONDITIONAL_CALL"),
    ("0x005286b0", "0x004530a0", "CTweak__dtor_base_thunk_004530a0", "UNCONDITIONAL_JUMP"),
    ("0x00528b20", "0x0055084f", "<no_function>", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00452430", "0x00452438", "CALL", "0x005159e0", "e8 a3 35 0c 00"),
    ("0x00452430", "0x00452443", "MOV", "dword ptr [ESI + 0x8], 0x0", "c7 46 08 00 00 00 00"),
    ("0x00452430", "0x0045244a", "FSTP", "float ptr [ESI + 0x4]", "d9 5e 04"),
    ("0x00452430", "0x0045244e", "RET", "0x4", "c2 04 00"),
    ("0x004530a0", "0x004530a0", "JMP", "0x005286b0", "e9 0b 56 0d 00"),
    ("0x00528690", "0x00528696", "MOV", "dword ptr [EAX], 0x5e4a94", "c7 00 94 4a 5e 00"),
    ("0x00528690", "0x0052869c", "MOV", "dword ptr [EAX + 0x8], ECX", "89 48 08"),
    ("0x00528690", "0x005286a8", "MOV", "[0x0089c018], EAX", "a3 18 c0 89 00"),
    ("0x00528690", "0x005286ad", "RET", "0x4", "c2 04 00"),
    ("0x005286b0", "0x005286b0", "MOV", "dword ptr [ECX], 0x5e4a94", "c7 01 94 4a 5e 00"),
    ("0x005286b0", "0x005286bd", "MOV", "EDX, 0x89c018", "ba 18 c0 89 00"),
    ("0x005286b0", "0x005286c4", "CMP", "EAX, ECX", "3b c1"),
    ("0x005286b0", "0x005286d6", "MOV", "dword ptr [EDX], EAX", "89 02"),
    ("0x00528b20", "0x00528b26", "MOV", "dword ptr [EAX], 0x5e4a94", "c7 00 94 4a 5e 00"),
    ("0x00528b20", "0x00528b3c", "MOV", "[0x0089c018], EAX", "a3 18 c0 89 00"),
    ("0x00528b20", "0x00528b41", "MOV", "dword ptr [EAX], 0x5e4aa4", "c7 00 a4 4a 5e 00"),
    ("0x00528b20", "0x00528b47", "MOV", "dword ptr [EAX + 0xc], ECX", "89 48 0c"),
    ("0x00528b20", "0x00528b4a", "RET", "0x8", "c2 08 00"),
]

STALE_TOKENS = [
    "CFEPBriefing__VFunc_06_00452430",
    "CTweak__ctor_like_00528690",
    "CTweak__ctor_like_005286b0",
    "CTweak__ctor_like_00528b20",
    "int param_2",
    "int param_3",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime proof",
    "rebuild parity proven",
    "exact source identity proven",
]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
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


def has_summary(text: str, *, updated: int, skipped: int, renamed: int, would_rename: int) -> bool:
    pattern = (
        rf"SUMMARY:\s+updated={updated}\s+skipped={skipped}\s+renamed={renamed}\s+"
        rf"would_rename={would_rename}\s+missing=0\s+bad=0"
    )
    return re.search(pattern, text) is not None


def decompile_text_for(decompile_dir: Path, address: str) -> str:
    prefix = normalize_address(address)[2:]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in decompile_dir.glob(f"{prefix}_*.c")
    )


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


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "frontend_briefing_tweak_wave380_dry.log"
    apply_log_path = apply_log_path or root / "frontend_briefing_tweak_wave380_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)

    if not has_summary(dry_text, updated=0, skipped=len(TARGETS), renamed=0, would_rename=len(TARGETS)):
        failures.append(f"dry-run summary missing/dirty: {relative(dry_log_path)}")
    if not has_summary(apply_text, updated=len(TARGETS), skipped=0, renamed=len(TARGETS), would_rename=0):
        failures.append(f"apply summary missing/dirty: {relative(apply_log_path)}")
    if "REPORT: Save succeeded" not in apply_text:
        failures.append(f"apply log missing save success: {relative(apply_log_path)}")

    metadata_rows = {
        normalize_address(row.get("address", "")): row
        for row in read_tsv(metadata_path)
        if row.get("address")
    }
    tag_rows = {
        normalize_address(row.get("address", "")): row
        for row in read_tsv(tags_path)
        if row.get("address")
    }

    for address, spec in TARGETS.items():
        metadata = metadata_rows.get(address)
        if metadata is None:
            failures.append(f"{address} missing metadata")
            continue
        if metadata.get("status") != "OK":
            failures.append(f"{address} metadata status not OK: {metadata.get('status')}")
        if metadata.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {metadata.get('name')} != {spec['name']}")
        if metadata.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {metadata.get('signature')} != {spec['signature']}")
        comment = metadata.get("comment", "")
        for token in spec["commentTokens"]:
            if str(token) not in comment:
                failures.append(f"{address} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                failures.append(f"{address} comment overclaim token present: {token}")

        tag_row = tag_rows.get(address)
        if tag_row is None:
            failures.append(f"{address} missing tags")
        else:
            tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing_tags = sorted((COMMON_TAGS | set(spec["tags"])) - tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {', '.join(missing_tags)}")

        decompile_text = decompile_text_for(Path(decompile_dir), address)
        if not decompile_text:
            failures.append(f"{address} missing decompile text")
        for token in spec["decompileTokens"]:
            if str(token) not in decompile_text:
                failures.append(f"{address} missing decompile token: {token}")
        for token in STALE_TOKENS:
            if token in decompile_text and token != str(spec["name"]):
                failures.append(f"{address} stale decompile token present: {token}")

    xrefs = read_tsv(xrefs_path)
    xref_hits = 0
    for target_addr, from_addr, from_function, ref_type in XREF_EVIDENCE:
        expected_target = normalize_address(target_addr)
        expected_from = normalize_address(from_addr)
        hit = any(
            normalize_address(row.get("target_addr", "")) == expected_target
            and normalize_address(row.get("from_addr", "")) == expected_from
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
            for row in xrefs
        )
        if hit:
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target_addr} <- {from_addr} {from_function} {ref_type}")

    instructions = read_tsv(instructions_path)
    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if evidence_hit(
            instructions,
            target=target_addr,
            instruction_addr=instruction_addr,
            mnemonic=mnemonic,
            operands=operands,
            bytes_=bytes_,
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instruction_addr} {mnemonic} {operands}")

    return {
        "schema": "ghidra-frontend-briefing-tweak-wave380/v1",
        "status": "PASS" if not failures else "FAIL",
        "root": relative(root),
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata_rows),
            "tagRows": len(tag_rows),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
        },
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    output_path = args.out or args.root / OUTPUT_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status={report['status']}")
    print(f"targets={report['summary']['targets']}")
    print(f"xrefEvidenceHits={report['summary']['xrefEvidenceHits']}")
    print(f"instructionEvidenceHits={report['summary']['instructionEvidenceHits']}")
    print(f"wrote={relative(output_path)}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
