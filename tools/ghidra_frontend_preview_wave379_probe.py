#!/usr/bin/env python3
"""Validate the Wave379 frontend preview/camera Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-preview-wave379/current")
OUTPUT_NAME = "frontend-preview-wave379.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-preview-wave379",
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
    "0x00466130": target(
        "CGenericCamera__ctor",
        "void __fastcall CGenericCamera__ctor(pointer this)",
        [
            "Name/comment correction",
            "sets the CGenericCamera vtable",
            "multiplayer frontend preview setup",
            "runtime camera behavior remains unproven",
        ],
        ["CGenericCamera__ctor", "PTR_CGenericCamera__GetPos_005dbb1c", "return"],
        ["frontend", "camera", "constructor", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00466140": target(
        "CGenericCamera__GetPos",
        "void __thiscall CGenericCamera__GetPos(void * this, pointer out_pos)",
        [
            "Signature/comment hardening",
            "copies four dwords",
            "this+0x34",
            "out_pos",
            "runtime camera position behavior remains unproven",
        ],
        ["out_pos", "+ 0x34", "+ 0x40", "return"],
        ["frontend", "camera", "position", "signature-hardened", "comment-hardened"],
    ),
    "0x00466170": target(
        "CGenericCamera__scalar_deleting_dtor",
        "pointer __thiscall CGenericCamera__scalar_deleting_dtor(void * this, uchar free_flag)",
        [
            "Signature/comment hardening",
            "calls CGenericCamera__dtor",
            "free_flag",
            "runtime camera cleanup remains unproven",
        ],
        ["free_flag", "CGenericCamera__dtor", "OID__FreeObject", "return this"],
        ["frontend", "camera", "destructor", "signature-hardened", "comment-hardened"],
    ),
    "0x004661b0": target(
        "CGenericCamera__dtor",
        "void __fastcall CGenericCamera__dtor(pointer this)",
        [
            "Signature/comment hardening",
            "resets the receiver vtable",
            "0x005d9260",
            "runtime camera cleanup remains unproven",
        ],
        ["PTR_CRT__Purecall_0055df1f_005d9260", "return"],
        ["frontend", "camera", "destructor", "signature-hardened", "comment-hardened"],
    ),
    "0x0046b950": target(
        "CFEPMultiplayerStart__LoadPreviewMeshFromConfig",
        "void __thiscall CFEPMultiplayerStart__LoadPreviewMeshFromConfig(void * this, pointer preview_config)",
        [
            "Signature/comment hardening",
            "preview_config",
            "copies transform/config data",
            "creates the preview object at +0x58",
            "runtime preview mesh behavior remains unproven",
        ],
        ["preview_config", "PCRTID__CreateObject", "+ 0x58", "+ 0x48", "+ 0x4c"],
        ["frontend", "multiplayer", "preview", "mesh", "signature-hardened", "comment-hardened"],
    ),
    "0x0046ba90": target(
        "CFrontEndThing__dtor_base",
        "void __fastcall CFrontEndThing__dtor_base(pointer this)",
        [
            "Name/signature correction",
            "not a constructor",
            "resets the CFrontEndThing vtable",
            "releases the preview object pointer at +0x58",
            "runtime frontend cleanup remains unproven",
        ],
        ["CFrontEndThing__dtor_base", "+ 0x58", "return"],
        ["frontend", "preview", "destructor", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0046bab0": target(
        "CFEPMultiplayerStart__SetPreviewAnimationByName",
        "void __thiscall CFEPMultiplayerStart__SetPreviewAnimationByName(void * this, char * animation_name)",
        [
            "Signature/comment hardening",
            "animation_name",
            "FindAnimationIndex",
            "preview object +0x58",
            "runtime preview animation behavior remains unproven",
        ],
        ["animation_name", "FindAnimationIndex", "+ 0x58", "+ 0x48", "+ 0x4c"],
        ["frontend", "multiplayer", "preview", "animation", "signature-hardened", "comment-hardened"],
    ),
    "0x0046bc20": target(
        "CFEPMultiplayerStart__StopPreviewAnimation",
        "void __fastcall CFEPMultiplayerStart__StopPreviewAnimation(pointer this)",
        [
            "Signature/comment hardening",
            "preview object +0x58",
            "vcall +0x08 with zero",
            "runtime preview animation behavior remains unproven",
        ],
        ["+ 0x58", "+ 8", "return"],
        ["frontend", "multiplayer", "preview", "animation", "signature-hardened", "comment-hardened"],
    ),
    "0x0046c030": target(
        "CThingCamera__scalar_deleting_dtor",
        "pointer __thiscall CThingCamera__scalar_deleting_dtor(void * this, uchar free_flag)",
        [
            "Name/signature correction",
            "scalar deleting destructor",
            "calls CThingCamera__dtor_base",
            "free_flag",
            "runtime thing-camera cleanup remains unproven",
        ],
        ["CThingCamera__dtor_base", "free_flag", "OID__FreeObject", "return this"],
        ["frontend", "camera", "thing-camera", "destructor", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0046c050": target(
        "CThingCamera__dtor_base",
        "void __fastcall CThingCamera__dtor_base(pointer this)",
        [
            "Name/signature correction",
            "not a constructor",
            "removes the linked reader cell",
            "resets the receiver to the base CGenericCamera vtable",
            "runtime thing-camera cleanup remains unproven",
        ],
        ["CThingCamera__dtor_base", "CSPtrSet__Remove", "PTR_CRT__Purecall_0055df1f_005d9260", "return"],
        ["frontend", "camera", "thing-camera", "destructor", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00466130", "0x00465f46", "CFEPMultiplayerStart__ctor", "UNCONDITIONAL_CALL"),
    ("0x00466140", "0x005dbb1c", "<no_function>", "DATA"),
    ("0x00466170", "0x005dbb3c", "<no_function>", "DATA"),
    ("0x004661b0", "0x00466173", "CGenericCamera__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x0046b950", "0x0051dc92", "CFEPMultiplayerStart__Init", "UNCONDITIONAL_CALL"),
    ("0x0046b950", "0x0044fb9e", "CFEPBEConfig__Init", "UNCONDITIONAL_CALL"),
    ("0x0046ba90", "0x0051dd9d", "CFEPMultiplayerStart__Shutdown", "UNCONDITIONAL_CALL"),
    ("0x0046ba90", "0x00521a6d", "CFEPWingmen__Destroy", "UNCONDITIONAL_CALL"),
    ("0x0046bab0", "0x0051dc9f", "CFEPMultiplayerStart__Init", "UNCONDITIONAL_CALL"),
    ("0x0046bab0", "0x0044fbab", "CFEPBEConfig__Init", "UNCONDITIONAL_CALL"),
    ("0x0046bc20", "0x00450c1f", "CFEPBEConfig__Render", "UNCONDITIONAL_CALL"),
    ("0x0046bc20", "0x0051ecaa", "CFEPMultiplayerStart__Render", "UNCONDITIONAL_CALL"),
    ("0x0046c030", "0x005dbba8", "<no_function>", "DATA"),
    ("0x0046c050", "0x0046c033", "CThingCamera__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00466130", "0x00466132", "MOV", "dword ptr [EAX], 0x5dbb1c", "c7 00 1c bb 5d 00"),
    ("0x00466140", "0x00466161", "RET", "0x4", "c2 04 00"),
    ("0x00466170", "0x00466173", "CALL", "0x004661b0", "e8 38 00 00 00"),
    ("0x00466170", "0x00466178", "TEST", "byte ptr [ESP + 0x8], 0x1", "f6 44 24 08 01"),
    ("0x00466170", "0x0046618d", "RET", "0x4", "c2 04 00"),
    ("0x004661b0", "0x004661b0", "MOV", "dword ptr [ECX], 0x5d9260", "c7 01 60 92 5d 00"),
    ("0x0046b950", "0x0046ba11", "MOV", "dword ptr [EBX + 0x58], EAX", "89 43 58"),
    ("0x0046b950", "0x0046ba2d", "CALL", "dword ptr [EDX + 0x38]", "ff 52 38"),
    ("0x0046b950", "0x0046ba30", "FSTP", "float ptr [EBX + 0x48]", "d9 5b 48"),
    ("0x0046ba90", "0x0046ba90", "MOV", "dword ptr [ECX], 0x5db2c4", "c7 01 c4 b2 5d 00"),
    ("0x0046ba90", "0x0046ba96", "MOV", "ECX, dword ptr [ECX + 0x58]", "8b 49 58"),
    ("0x0046ba90", "0x0046ba9f", "PUSH", "0x1", "6a 01"),
    ("0x0046bab0", "0x0046bad0", "CALL", "0x004aa630", "e8 5b eb 03 00"),
    ("0x0046bab0", "0x0046badc", "FSTP", "float ptr [ESI + 0x48]", "d9 5e 48"),
    ("0x0046bab0", "0x0046badf", "MOV", "dword ptr [ESI + 0x4c], 0x0", "c7 46 4c 00 00 00 00"),
    ("0x0046bc20", "0x0046bc20", "MOV", "ECX, dword ptr [ECX + 0x58]", "8b 49 58"),
    ("0x0046bc20", "0x0046bc2b", "CALL", "dword ptr [EAX + 0x8]", "ff 50 08"),
    ("0x0046bc20", "0x0046bc2e", "RET", "", "c3"),
    ("0x0046c030", "0x0046c033", "CALL", "0x0046c050", "e8 18 00 00 00"),
    ("0x0046c030", "0x0046c038", "TEST", "byte ptr [ESP + 0x8], 0x1", "f6 44 24 08 01"),
    ("0x0046c030", "0x0046c04d", "RET", "0x4", "c2 04 00"),
    ("0x0046c050", "0x0046c089", "CALL", "0x004e5bd0", "e8 42 9b 07 00"),
    ("0x0046c050", "0x0046c092", "MOV", "dword ptr [ESI], 0x5d9260", "c7 06 60 92 5d 00"),
]

STALE_TOKENS = [
    "CGenericCamera__ctor_like_00466130",
    "CFrontEndThing__ctor_like_0046ba90",
    "CThingCamera__VFunc_08_0046c030",
    "CCamera__ctor_like_0046c050",
    "int param_2",
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
    dry_log_path = dry_log_path or root / "frontend_preview_wave379_dry.log"
    apply_log_path = apply_log_path or root / "frontend_preview_wave379_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)

    if not has_summary(dry_text, updated=0, skipped=len(TARGETS), renamed=0, would_rename=4):
        failures.append(f"dry-run summary missing/dirty: {relative(dry_log_path)}")
    if not has_summary(apply_text, updated=len(TARGETS), skipped=0, renamed=4, would_rename=0):
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
        "schema": "ghidra-frontend-preview-wave379/v1",
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
