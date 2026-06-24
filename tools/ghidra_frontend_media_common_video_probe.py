#!/usr/bin/env python3
"""Validate the Wave374 frontend/common video Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-media-wave374/current")
OUTPUT_NAME = "frontend-media-common-video.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-media-wave374",
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
    "0x00452b00": target(
        "CFEPCommon__Init",
        "bool __thiscall CFEPCommon__Init(void * this)",
        [
            "previously missing as a function object",
            "FEBack128.vid",
            "CDXFrontEndVideo__Open",
            "this+0x4",
            "remain unproven",
        ],
        ["CDXFrontEndVideo__Open", "s_data_video_FEBack128_vid_00629068", "return true"],
        ["frontend", "common-page", "video", "boundary-created", "signature-hardened", "comment-hardened"],
    ),
    "0x00452b30": target(
        "CFEPCommon__Shutdown",
        "void __thiscall CFEPCommon__Shutdown(void * this)",
        [
            "CFEPCommon teardown",
            "CDXFrontEndVideo__CloseVideo",
            "OID__FreeObject",
            "this+0x4",
            "remain unproven",
        ],
        ["CDXFrontEndVideo__CloseVideo", "OID__FreeObject", "+ 4) = 0"],
        ["frontend", "common-page", "video", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00452b60": target(
        "CFrontEndPage__Process_NoOp",
        "void __thiscall CFrontEndPage__Process_NoOp(void * this, int state)",
        [
            "shared frontend page process no-op",
            "RET 0x4",
            "thiscall receiver",
            "state stack argument",
            "remain unproven",
        ],
        ["CFrontEndPage__Process_NoOp", "return"],
        ["frontend", "frontend-page", "shared-noop", "signature-hardened", "comment-hardened"],
    ),
    "0x00452ce0": target(
        "CFrontEnd__RenderVideoQuadScaledToWindow",
        "void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)",
        [
            "frontend video-quad render helper",
            "PLATFORM window dimensions",
            "CDXFrontEndVideo__Render",
            "ARGB",
            "remain unproven",
        ],
        ["PLATFORM__GetWindowWidth", "D3DStateCache__SetStateCached", "CDXFrontEndVideo__Render"],
        ["frontend", "video", "render", "signature-hardened", "comment-hardened"],
    ),
    "0x00452da0": target(
        "SharedVFunc__NoOp_Ret08",
        "void __stdcall SharedVFunc__NoOp_Ret08(int unused0, int unused1)",
        [
            "zero-body shared vtable target",
            "RET 0x8",
            "older slot-specific label was too narrow",
            "remain unproven",
        ],
        ["SharedVFunc__NoOp_Ret08", "return"],
        ["shared-noop", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00452db0": target(
        "CFEPCommon__StartVideo",
        "void __thiscall CFEPCommon__StartVideo(void * this, int start_flag)",
        [
            "CFEPCommon::StartVideo-style helper",
            "Goodies FMV return path",
            "FEBack128.vid",
            "start_flag",
            "remain unproven",
        ],
        ["CDXFrontEndVideo__Open", "s_data_video_FEBack128_vid_00629068"],
        ["frontend", "common-page", "video", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00452de0": target(
        "CFEPCommon__StopVideo",
        "void __thiscall CFEPCommon__StopVideo(void * this)",
        [
            "CFEPCommon::StopVideo-style helper",
            "Goodies FMV path",
            "CDXFrontEndVideo__CloseVideo",
            "remain unproven",
        ],
        ["CDXFrontEndVideo__CloseVideo"],
        ["frontend", "common-page", "video", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00452b00", "0x005dba68", "DATA"),
    ("0x00452b30", "0x005dba6c", "DATA"),
    ("0x00452b60", "0x005dba70", "DATA"),
    ("0x00452ce0", "0x00467ad0", "UNCONDITIONAL_CALL"),
    ("0x00452ce0", "0x00459ed3", "UNCONDITIONAL_CALL"),
    ("0x00452ce0", "0x00462c7e", "UNCONDITIONAL_CALL"),
    ("0x00452da0", "0x004bac2b", "UNCONDITIONAL_CALL"),
    ("0x00452db0", "0x00451c5d", "UNCONDITIONAL_CALL"),
    ("0x00452db0", "0x0045dbaa", "UNCONDITIONAL_CALL"),
    ("0x00452de0", "0x0045db2b", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00452b00", "0x00452b0b", "MOV", "[ECX + 0x4]"),
    ("0x00452b00", "0x00452b21", "CALL", "0x005412e0"),
    ("0x00452b00", "0x00452b26", "MOV", "0x1"),
    ("0x00452b30", "0x00452b38", "CALL", "0x00541650"),
    ("0x00452b30", "0x00452b4a", "CALL", "0x00549220"),
    ("0x00452b60", "0x00452b60", "RET", "0x4"),
    ("0x00452ce0", "0x00452d34", "CALL", "0x00513820"),
    ("0x00452ce0", "0x00452d94", "CALL", "0x00541790"),
    ("0x00452ce0", "0x00452d99", "RET", "0x10"),
    ("0x00452da0", "0x00452da0", "RET", "0x8"),
    ("0x00452db0", "0x00452dca", "CALL", "0x005412e0"),
    ("0x00452db0", "0x00452dcf", "RET", "0x4"),
    ("0x00452de0", "0x00452de5", "JMP", "0x00541650"),
]

VTABLE_EVIDENCE = [
    ("0x005dba68", "0", "0x00452b00", "CFEPCommon__Init"),
    ("0x005dba68", "1", "0x00452b30", "CFEPCommon__Shutdown"),
    ("0x005dba68", "2", "0x00452b60", "CFrontEndPage__Process_NoOp"),
    ("0x005dba68", "9", "0x00452da0", "SharedVFunc__NoOp_Ret08"),
]

STALE_TOKENS = [
    "CFEPGoodies__OpenVideo",
    "CFEPGoodies__CloseVideo",
    "CFEPGoodies__Helper_00452db0",
    "CFEPGoodies__Helper_00452de0",
    "CFEPCommon__VFunc_01_00452b30",
    "VFuncSlot_06_00452da0",
    "param_",
    "unaff_",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(
        r"SUMMARY:\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "created": int(match.group(3)),
        "would_create": int(match.group(4)),
        "renamed": int(match.group(5)),
        "would_rename": int(match.group(6)),
        "missing": int(match.group(7)),
        "bad": int(match.group(8)),
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def decompile_for(decompile_dir: Path, address: str) -> str:
    matches = sorted(decompile_dir.glob(f"{norm_addr(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    vtable_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "frontend_media_common_video_dry.log"
    apply_log_path = apply_log_path or root / "frontend_media_common_video_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    expected_dry = {
        "updated": 0,
        "skipped": expected_count,
        "created": 0,
        "would_create": 1,
        "renamed": 0,
        "would_rename": 4,
        "missing": 0,
        "bad": 0,
    }
    expected_apply = {
        "updated": expected_count,
        "skipped": 0,
        "created": 1,
        "would_create": 0,
        "renamed": 4,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }
    if dry_summary != expected_dry:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != expected_apply:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    vtables = read_tsv(vtable_path)

    xref_hits = 0
    instruction_hits = 0
    vtable_hits = 0
    stale_hits = 0
    overclaim_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status mismatch: {row.get('status')}")
        if name != spec["name"]:
            failures.append(f"{address} name mismatch: {name} != {spec['name']}")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        for token in STALE_TOKENS:
            if token_present(name, token) or token_present(signature, token):
                stale_hits += 1
                failures.append(f"{address} stale token present in name/signature: {token}")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits += 1
                failures.append(f"{address} overclaim token present: {token}")

        tag_row = tags.get(norm_addr(address))
        if not tag_row or tag_row.get("status") != "OK":
            failures.append(f"{address} tag row missing or bad")
        else:
            actual_tags = {tag.strip() for tag in tag_row.get("tags", "").split(";") if tag.strip()}
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing_tags = expected_tags - actual_tags
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

        decompile_text = decompile_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} missing decompile token: {token}")

    for target, source, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target=target, source=source, ref_type=ref_type: norm_addr(row.get("target_addr", "")) == norm_addr(target)
            and norm_addr(row.get("from_addr", "")) == norm_addr(source)
            and row.get("ref_type", "") == ref_type,
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target} <- {source} {ref_type}")

    for target, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target=target, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: norm_addr(row.get("target_addr", "")) == norm_addr(target)
            and norm_addr(row.get("instruction_addr", "")) == norm_addr(instruction_addr)
            and row.get("mnemonic", "") == mnemonic
            and token_present(row.get("operands", ""), operand_token),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target} {instruction_addr} {mnemonic} {operand_token}")

    for vtable, slot_index, pointer, function_name in VTABLE_EVIDENCE:
        if any_row(
            vtables,
            lambda row, vtable=vtable, slot_index=slot_index, pointer=pointer, function_name=function_name: norm_addr(row.get("vtable", "")) == norm_addr(vtable)
            and row.get("slot_index", "") == slot_index
            and norm_addr(row.get("pointer_addr", "")) == norm_addr(pointer)
            and row.get("function_name", "") == function_name,
        ):
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence: {vtable} slot {slot_index} -> {function_name}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-frontend-media-common-video.v1",
        "status": status,
        "root": root.as_posix(),
        "summary": {
            "targets": expected_count,
            "drySummary": dry_summary,
            "applySummary": apply_summary,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "vtableEvidenceHits": vtable_hits,
            "staleTokenHits": stale_hits,
            "overclaimHits": overclaim_hits,
        },
        "targets": TARGETS,
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has a CFEPCommon init function object at 0x00452b00.",
            "The saved Ghidra names/signatures/comments/tags now classify the common frontend video helpers as CFEPCommon rather than CFEPGoodies-owned helpers.",
            "The saved Ghidra project now classifies 0x00452da0 as a shared RET 0x8 no-op target instead of an owner-specific slot label.",
        ],
        "notProven": [
            "This does not prove exact local variable types, complete CFEPCommon class layout, or every adjacent vtable slot.",
            "This does not prove runtime video playback behavior, packaged-app behavior, BEA launch behavior, or rebuild parity.",
            "This does not mutate the installed game or BEA.exe.",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    report = build_report(root=args.root)
    out = args.out or (args.root / OUTPUT_NAME)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra frontend/media common video probe")
        print(f"Status: {report['status']}")
        print(f"Output: {out.as_posix()}")
        summary = report["summary"]
        print(f"Targets: {summary['targets']}")
        print(f"Xref evidence hits: {summary['xrefEvidenceHits']}")
        print(f"Instruction evidence hits: {summary['instructionEvidenceHits']}")
        print(f"Vtable evidence hits: {summary['vtableEvidenceHits']}")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
