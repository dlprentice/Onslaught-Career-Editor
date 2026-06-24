#!/usr/bin/env python3
"""Validate the Wave376 frontend queue-head Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-queue-wave376/current")
OUTPUT_NAME = "frontend-queue-wave376.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-queue-wave376",
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
    "0x00452fd0": target(
        "FEPShared__RenderSelectionBrackets",
        "void __stdcall FEPShared__RenderSelectionBrackets(float transition_alpha)",
        [
            "Owner/name/signature correction",
            "shared frontend bracket helper",
            "CDXSurf__RenderSurface",
            "RET 0x4",
            "remains unproven",
        ],
        ["CDXSurf__RenderSurface", "DAT_0089d7f0", "0x3f000000"],
        ["frontend", "shared-ui", "render", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004530b0": target(
        "FEPShared__RenderSelectionMarker",
        "void __stdcall FEPShared__RenderSelectionMarker(float x_index, float y_index, float scale, int alpha)",
        [
            "Owner/name/signature correction",
            "shared frontend marker helper",
            "selection marker surface",
            "RET 0x10",
            "remains unproven",
        ],
        ["CDXSurf__RenderSurface", "DAT_0089d838", "DAT_006777c4"],
        ["frontend", "shared-ui", "render", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00453140": target(
        "FEPShared__RenderContextHelpPrompt",
        "void __stdcall FEPShared__RenderContextHelpPrompt(int help_token, float transition)",
        [
            "Owner/name/signature correction",
            "shared frontend help-prompt renderer",
            "localized IDs 0x2b-0x30",
            "transition/progress",
            "remains unproven",
        ],
        ["Localization__GetStringById", "CFrontEnd__IsMouseInputReady", "CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture"],
        ["frontend", "shared-ui", "help-prompt", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00456830": target(
        "GlobalListNode__ClearField4AndPushGlobalList",
        "void * __thiscall GlobalListNode__ClearField4AndPushGlobalList(void * this)",
        [
            "Owner/name/signature correction",
            "shared constructor-style callback",
            "clears field +0x4",
            "PushNodeGlobalList",
            "remain unproven",
        ],
        ["CWorldPhysicsManager__PushNodeGlobalList", "+ 4", "return"],
        ["shared-callback", "global-list", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00456850": target(
        "CFEPDebriefing__Shutdown",
        "void __thiscall CFEPDebriefing__Shutdown(void * this)",
        [
            "Name/signature correction",
            "vtable slot 1",
            "frees an array/object pair",
            "fields +0x20 and +0x24",
            "remains unproven",
        ],
        ["CDXLandscape__DestroyArrayWithCallback", "OID__FreeObject", "+ 0x20"],
        ["frontend", "debriefing", "vtable-slot", "shutdown", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00465a20": target(
        "TextLayout__WrapWideTextToFixedLines",
        "int __stdcall TextLayout__WrapWideTextToFixedLines(short * line_buffer, short * wide_text, float max_width)",
        [
            "Owner/name/signature correction",
            "shared wide-text wrapping helper",
            "fixed 100-wchar line slots",
            "CDXFont__GetTextExtent",
            "remains unproven",
        ],
        ["WcsLen", "CDXFont__GetTextExtent", "CRT__WcsNcpyZeroPad"],
        ["text-layout", "wide-text", "shared-helper", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004661d0": target(
        "CFEPMultiplayerStart__ClearJoinedPlayerSet",
        "void __thiscall CFEPMultiplayerStart__ClearJoinedPlayerSet(void * this)",
        [
            "Signature/comment hardening",
            "tail-call wrapper",
            "adds +0x20",
            "CSPtrSet__Clear",
            "remains unproven",
        ],
        ["CSPtrSet__Clear", "+ 0x20"],
        ["frontend", "multiplayer-start", "tailcall", "signature-hardened", "comment-hardened"],
    ),
    "0x004661e0": target(
        "CFEPMultiplayerStart__ClearSecondaryPlayerSet",
        "void __thiscall CFEPMultiplayerStart__ClearSecondaryPlayerSet(void * this)",
        [
            "Signature/comment hardening",
            "tail-call wrapper",
            "adds +0x28",
            "CSPtrSet__Clear",
            "remains unproven",
        ],
        ["CSPtrSet__Clear", "+ 0x28"],
        ["frontend", "multiplayer-start", "tailcall", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00452fd0", "0x00450c9e", "CFEPBEConfig__Render", "UNCONDITIONAL_CALL"),
    ("0x00452fd0", "0x0051e1d7", "CFEPMultiplayerStart__Render", "UNCONDITIONAL_CALL"),
    ("0x004530b0", "0x004503c4", "CFEPBEConfig__RenderPreCommon", "UNCONDITIONAL_CALL"),
    ("0x004530b0", "0x0051e19c", "CFEPMultiplayerStart__RenderPreCommon", "UNCONDITIONAL_CALL"),
    ("0x00453140", "0x00461e11", "CFEPLoadGame__Render", "UNCONDITIONAL_CALL"),
    ("0x00453140", "0x00464b01", "CFEPSaveGame__Render", "UNCONDITIONAL_CALL"),
    ("0x00456830", "0x004567c9", "CFEPDebriefing__Initialize", "DATA"),
    ("0x00456830", "0x004bf374", "OID__CreateObject", "DATA"),
    ("0x00456850", "0x005db9c4", "<no_function>", "DATA"),
    ("0x00465a20", "0x0044d46c", "CFEPSaveGame__InitDialogAndLayoutState", "UNCONDITIONAL_CALL"),
    ("0x00465a20", "0x0051c760", "CFEPLanguageTest__Render", "UNCONDITIONAL_CALL"),
    ("0x00465a20", "0x00527aa9", "CGame__DrawLocalCoopControllerPrompt", "UNCONDITIONAL_CALL"),
    ("0x004661d0", "0x005d26aa", "Unwind@005d26a1", "UNCONDITIONAL_CALL"),
    ("0x004661e0", "0x005d26b8", "Unwind@005d26af", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00452fd0", "0x00453066", "RET", "0x4", "c2 04 00"),
    ("0x004530b0", "0x00453132", "RET", "0x10", "c2 10 00"),
    ("0x00453140", "0x0045334b", "RET", "0x8", "c2 08 00"),
    ("0x00456830", "0x00456833", "MOV", "[ESI + 0x4]", "c7 46 04 00 00 00 00"),
    ("0x00456830", "0x00456842", "RET", "", "c3"),
    ("0x00456850", "0x00456884", "MOV", "[ESI + 0x20]", "c7 46 20 00 00 00 00"),
    ("0x00456850", "0x00456898", "RET", "", "c3"),
    ("0x00465a20", "0x00465c06", "RET", "0xc", "c2 0c 00"),
    ("0x004661d0", "0x004661d0", "ADD", "ECX, 0x20", "83 c1 20"),
    ("0x004661d0", "0x004661d3", "JMP", "0x004e5c60", "e9 88 fa 07 00"),
    ("0x004661e0", "0x004661e0", "ADD", "ECX, 0x28", "83 c1 28"),
    ("0x004661e0", "0x004661e3", "JMP", "0x004e5c60", "e9 78 fa 07 00"),
]

STALE_TOKENS = [
    "CFEPMultiplayerStart__RenderHelpPromptForSelection",
    "CFEPLanguageTest__WrapWideTextToFixedLines",
    "CFEPDebriefing__VFunc_01_00456850",
    "CFEPDebriefing__ResetStateAndVector",
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
    chunks = []
    for path in decompile_dir.glob(f"{prefix}_*.c"):
        chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


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
    dry_log_path = dry_log_path or root / "frontend_queue_wave376_dry.log"
    apply_log_path = apply_log_path or root / "frontend_queue_wave376_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    if not has_summary(dry_text, updated=0, skipped=len(TARGETS), renamed=0, would_rename=6):
        failures.append("dry-run summary mismatch or missing")
    if not has_summary(apply_text, updated=len(TARGETS), skipped=0, renamed=6, would_rename=0):
        failures.append("apply summary mismatch or missing")
    if "REPORT: Save succeeded" not in apply_text:
        failures.append("apply log missing Ghidra save success")

    metadata = {normalize_address(row.get("address", "")): row for row in read_tsv(metadata_path)}
    tags = {normalize_address(row.get("address", "")): row for row in read_tsv(tags_path)}
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None or row.get("status") != "OK":
            failures.append(f"{address} missing metadata OK row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if str(token) not in comment:
                failures.append(f"{address} missing comment token: {token}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                failures.append(f"{address} overclaim token in comment: {token}")

        tag_row = tags.get(address)
        tag_text = tag_row.get("tags", "") if tag_row else ""
        expected_tags = COMMON_TAGS | set(spec["tags"])
        for tag in expected_tags:
            if tag not in tag_text:
                failures.append(f"{address} missing tag: {tag}")

        decompile_text = decompile_text_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"{address} missing decompile text")
        for token in spec["decompileTokens"]:
            if str(token) not in decompile_text:
                failures.append(f"{address} missing decompile token: {token}")
        for token in STALE_TOKENS:
            if token in decompile_text and token != spec["name"]:
                failures.append(f"{address} stale decompile token: {token}")

    xref_hits = 0
    for target, source, caller, ref_type in XREF_EVIDENCE:
        target_norm = normalize_address(target)[2:]
        source_norm = normalize_address(source)[2:]
        if any(
            row.get("target_addr", "").lower() == target_norm
            and row.get("from_addr", "").lower() == source_norm
            and row.get("from_function") == caller
            and row.get("ref_type") == ref_type
            for row in xrefs
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target} <- {source} {caller} {ref_type}")

    instruction_hits = 0
    for target, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        target_norm = normalize_address(target)
        instruction_norm = normalize_address(instruction_addr)
        if any(
            normalize_address(row.get("target_addr", "")) == target_norm
            and normalize_address(row.get("instruction_addr", "")) == instruction_norm
            and row.get("mnemonic") == mnemonic
            and operands in row.get("operands", "")
            and bytes_ in row.get("bytes", "")
            for row in instructions
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target} {instruction_addr} {mnemonic} {operands} {bytes_}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-frontend-queue-wave376.v1",
        "status": status,
        "inputs": {
            "root": relative(root),
            "metadata": relative(metadata_path),
            "tags": relative(tags_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "decompileDir": relative(decompile_dir),
        },
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata),
            "tagRows": len(tags),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
        },
        "failures": failures,
        "whatIsProven": [
            "The selected frontend queue-head targets have saved names, signatures, comments, and tags matching the Wave376 evidence model.",
            "The first three formerly multiplayer-owned render helpers are treated as shared frontend UI helpers because broad xrefs span multiple FEP pages.",
            "The wide-text wrapping helper is treated as a shared text-layout helper because xrefs span frontend pages, overlays, and game prompts.",
        ],
        "notProven": [
            "This does not prove runtime frontend rendering, debriefing shutdown behavior, language wrapping behavior, or packaged app behavior.",
            "This does not recover concrete class layouts, local-variable names, or exact source identities for every callsite.",
            "This does not mutate or run BEA.exe.",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    report = build_report(root=args.root)
    out = args.root / OUTPUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print("Ghidra frontend queue Wave376 probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {summary['targets']}")
        print(f"Xref evidence hits: {summary['xrefEvidenceHits']}")
        print(f"Instruction evidence hits: {summary['instructionEvidenceHits']}")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
