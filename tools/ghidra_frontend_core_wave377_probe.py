#!/usr/bin/env python3
"""Validate the Wave377 frontend core Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-core-wave377/current")
OUTPUT_NAME = "frontend-core-wave377.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-core-wave377",
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
    "0x00466980": target(
        "CFrontEnd__GetPlayer0ControllerPort",
        "int __thiscall CFrontEnd__GetPlayer0ControllerPort(void * this)",
        [
            "Signature/source-parity hardening",
            "player-0 controller port",
            "offset +0x274",
            "normalizes the unset -1 sentinel to 0",
            "runtime controller behavior remains unproven",
        ],
        ["0x274", "0xffffffff", "return"],
        ["frontend", "controller", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x004669a0": target(
        "CFrontEnd__ReceiveButtonAction",
        "void __thiscall CFrontEnd__ReceiveButtonAction(void * this, void * from_controller, int button, float action_value)",
        [
            "Name/signature/source-parity correction",
            "CFrontEnd::ReceiveButtonAction",
            "RET 0x0c",
            "BUTTON_FRONTEND_MENU_SELECT 0x2c",
            "BUTTON_FRONTEND_CHEAT 0x2d",
            "runtime input behavior remains unproven",
        ],
        ["from_controller", "button", "action_value", "0x2c", "0x2d", "CFrontEnd__HandleModalPanelButton"],
        ["frontend", "controller", "input", "vtable-slot", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00466ab0": target(
        "CFrontEnd__SetLanguage",
        "void __thiscall CFrontEnd__SetLanguage(void * this, int language_index)",
        [
            "Signature/source-parity hardening",
            "CFrontEnd::SetLanguage",
            "one stack language_index",
            "RET 0x4",
            "CText__CopyFrom",
            "runtime localization behavior remains unproven",
        ],
        ["language_index", "CText__CopyFrom", "g_Text"],
        ["frontend", "localization", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x00467200": target(
        "CFrontEnd__DrawSlidingTextBordersAndMask",
        "void __thiscall CFrontEnd__DrawSlidingTextBordersAndMask(void * this, float transition, int dest_page)",
        [
            "Signature/source-parity hardening",
            "transition",
            "dest_page",
            "got_standard_SlidingTextBordersAndMask",
            "FEPShared__RenderSelectionBrackets",
            "runtime frontend rendering remains unproven",
        ],
        ["transition", "dest_page", "FEPShared__RenderSelectionBrackets", "FrontEnd__HasStandardSlidingTextBordersAndMaskPage"],
        ["frontend", "render", "transition", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x004679a0": target(
        "FrontEnd__HasStandardSlidingTextBordersAndMaskPage",
        "int __cdecl FrontEnd__HasStandardSlidingTextBordersAndMaskPage(int dest_page)",
        [
            "Owner/name/source-parity correction",
            "source static got_standard_SlidingTextBordersAndMask",
            "standard page switch set",
            "7,8,9,10,11,13,14,16,17,19",
            "runtime page styling remains unproven",
        ],
        ["dest_page", "case 7", "case 0x13", "return 1"],
        ["frontend", "render", "page-predicate", "source-parity", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00467bd0": target(
        "CFrontEnd__DrawTitleBar",
        "void __stdcall CFrontEnd__DrawTitleBar(short * title_text, float transition, int dest_page)",
        [
            "Signature/source-parity hardening",
            "WCHAR title text",
            "transition",
            "dest_page",
            "CDXFont__DrawTextDynamic",
            "runtime title rendering remains unproven",
        ],
        ["title_text", "transition", "dest_page", "CDXFont__GetTextExtent", "CDXFont__DrawTextDynamic"],
        ["frontend", "render", "title-bar", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x00468700": target(
        "CFrontEnd__RenderCursorEndSceneAndAsyncSave",
        "void __stdcall CFrontEnd__RenderCursorEndSceneAndAsyncSave(int end_scene)",
        [
            "Name/signature/comment hardening",
            "CFrontEnd vtable slot 7",
            "renders the mouse cursor sprite",
            "optionally ends scene",
            "async career save",
            "runtime frame behavior remains unproven",
        ],
        ["end_scene", "CDXEngine__RenderMouseCursorSprite", "PLATFORM__EndScene", "Platform__AsyncSaveCareer"],
        ["frontend", "render", "cursor", "async-save", "vtable-slot", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004691c0": target(
        "CFrontEnd__ReleaseParticleHudWaypointResources",
        "void __fastcall CFrontEnd__ReleaseParticleHudWaypointResources(void * frontend)",
        [
            "Signature/comment hardening",
            "particle-manager state",
            "HUD handle table +0x48",
            "waypoint/mesh/texture level resources",
            "runtime cleanup behavior remains unproven",
        ],
        ["frontend", "CParticleManager__ClearParticleOwnerBacklinks", "+ 0x48", "CWaypoint__CleanupEndLevelVBufTextures", "CTexture__FreeLevelResources"],
        ["frontend", "cleanup", "particles", "hud", "level-resources", "signature-hardened", "comment-hardened"],
    ),
    "0x00469390": target(
        "CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture",
        "uint __cdecl CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture(float x, float y, float width, float height, int dispatch_context)",
        [
            "Signature/comment hardening",
            "modal mouse-input gate",
            "Input__DispatchClickInRect",
            "float rectangle arguments",
            "dispatch_context",
            "runtime mouse behavior remains unproven",
        ],
        ["CFrontEnd__IsMouseInputReady", "Input__DispatchClickInRect", "dispatch_context"],
        ["frontend", "input", "mouse", "signature-hardened", "comment-hardened"],
    ),
    "0x004693d0": target(
        "CFrontEnd__GetCursorStateInRect",
        "uint __cdecl CFrontEnd__GetCursorStateInRect(float x, float y, float width, float height)",
        [
            "Signature/comment hardening",
            "modal mouse-input gate",
            "CDXEngine__GetCursorStateInRect",
            "float rectangle arguments",
            "runtime mouse behavior remains unproven",
        ],
        ["CFrontEnd__IsMouseInputReady", "CDXEngine__GetCursorStateInRect", "width", "height"],
        ["frontend", "input", "mouse", "signature-hardened", "comment-hardened"],
    ),
    "0x00469400": target(
        "CFrontEnd__GetClickStateInRect",
        "uint __cdecl CFrontEnd__GetClickStateInRect(float x, float y, float width, float height)",
        [
            "Signature/comment hardening",
            "modal mouse-input gate",
            "Input__GetClickStateInRect",
            "float rectangle arguments",
            "runtime mouse behavior remains unproven",
        ],
        ["CFrontEnd__IsMouseInputReady", "Input__GetClickStateInRect", "width", "height"],
        ["frontend", "input", "mouse", "signature-hardened", "comment-hardened"],
    ),
    "0x00469430": target(
        "CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady",
        "uint __cdecl CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady(float x, float y, float width, float height)",
        [
            "Name/signature correction",
            "directory cursor-state consume wrapper",
            "Input__GetCursorStateInRectAndConsume",
            "float rectangle arguments",
            "runtime directory mouse behavior remains unproven",
        ],
        ["CFrontEnd__IsMouseInputReady", "Input__GetCursorStateInRectAndConsume", "width", "height"],
        ["frontend", "directory", "input", "mouse", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00469550": target(
        "CFrontEnd__ResolveLevelNameTextByCode",
        "short * __cdecl CFrontEnd__ResolveLevelNameTextByCode(int level_code)",
        [
            "Return/signature hardening",
            "localized level-name text",
            "CText__GetStringById",
            "Text__AsciiToWideScratch",
            "Unnamed Level",
            "runtime localization behavior remains unproven",
        ],
        ["level_code", "CText__GetStringById", "Text__AsciiToWideScratch", "Unnamed_Level"],
        ["frontend", "localization", "level-name", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00466980", "0x0046cf3b", "CGame__LoadLevel", "UNCONDITIONAL_CALL"),
    ("0x00466980", "0x00527a23", "CGame__DrawLocalCoopControllerPrompt", "UNCONDITIONAL_CALL"),
    ("0x004669a0", "0x005db768", "<no_function>", "DATA"),
    ("0x004669a0", "0x00523c5a", "Input__DispatchClickInRect", "UNCONDITIONAL_CALL"),
    ("0x00466ab0", "0x004211a0", "OptionsTail_Read", "UNCONDITIONAL_CALL"),
    ("0x00466ab0", "0x0046234c", "CFEPMain__ButtonPressed", "UNCONDITIONAL_CALL"),
    ("0x00467200", "0x00461da1", "CFEPLoadGame__Render", "UNCONDITIONAL_CALL"),
    ("0x00467200", "0x0051aef9", "CFEPDirectory__RenderSaveFileList", "UNCONDITIONAL_CALL"),
    ("0x004679a0", "0x00467244", "CFrontEnd__DrawSlidingTextBordersAndMask", "UNCONDITIONAL_CALL"),
    ("0x00467bd0", "0x00451906", "CFEPBEConfig__Render", "UNCONDITIONAL_CALL"),
    ("0x00467bd0", "0x0051f31e", "CFEPMultiplayerStart__Render", "UNCONDITIONAL_CALL"),
    ("0x00468700", "0x00540fc4", "CDXFrontEnd__VFunc_07_00540fb0", "UNCONDITIONAL_CALL"),
    ("0x00468700", "0x005db778", "<no_function>", "DATA"),
    ("0x004691c0", "0x0046692a", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00469390", "0x0045333e", "FEPShared__RenderContextHelpPrompt", "UNCONDITIONAL_CALL"),
    ("0x00469390", "0x0051a865", "CFEPCredits__Process", "UNCONDITIONAL_CALL"),
    ("0x004693d0", "0x004a3114", "CMenuItem__IsMouseInBounds", "UNCONDITIONAL_CALL"),
    ("0x004693d0", "0x0051b36d", "CFEPDirectory__RenderSaveFileList", "UNCONDITIONAL_CALL"),
    ("0x00469400", "0x004a3134", "CMenuItem__IsMouseClicked", "UNCONDITIONAL_CALL"),
    ("0x00469400", "0x0051b180", "CFEPDirectory__RenderSaveFileList", "UNCONDITIONAL_CALL"),
    ("0x00469430", "0x0051b148", "CFEPDirectory__RenderSaveFileList", "UNCONDITIONAL_CALL"),
    ("0x00469550", "0x0045a6aa", "CFEPMultiplayerStart__SubObj8848__Render", "UNCONDITIONAL_CALL"),
    ("0x00469550", "0x004618aa", "CFEPLevelSelect__Render", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00466980", "0x0046698f", "RET", "", "c3"),
    ("0x004669a0", "0x00466a5e", "RET", "0xc", "c2 0c 00"),
    ("0x00466ab0", "0x00466ad4", "RET", "0x4", "c2 04 00"),
    ("0x00467200", "0x00467205", "MOV", "EBX, dword ptr [ESP + 0x24]", "8b 5c 24 24"),
    ("0x00467200", "0x00467244", "CALL", "0x004679a0", "e8 57 07 00 00"),
    ("0x004679a0", "0x004679a7", "CMP", "EAX, 0xc", "83 f8 0c"),
    ("0x004679a0", "0x004679c0", "RET", "", "c3"),
    ("0x00468700", "0x00468723", "RET", "0x4", "c2 04 00"),
    ("0x00469390", "0x004693ba", "CALL", "0x00523bc0", "e8 01 a8 0b 00"),
    ("0x004693d0", "0x004693f5", "CALL", "0x00523b50", "e8 56 a7 0b 00"),
    ("0x00469400", "0x00469425", "CALL", "0x00523cc0", "e8 96 a8 0b 00"),
    ("0x00469430", "0x00469455", "CALL", "0x00523d40", "e8 e6 a8 0b 00"),
]

STALE_TOKENS = [
    "VFuncSlot_03_004669a0",
    "CFrontEnd__VFunc_07_00468700",
    "CFEPDirectory__CheckMouseInputReady",
    "CFrontEnd__HasStandardSlidingTextBordersAndMask(",
    "void __cdecl CFrontEnd__ResolveLevelNameTextByCode",
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
    dry_log_path = dry_log_path or root / "frontend_core_wave377_dry.log"
    apply_log_path = apply_log_path or root / "frontend_core_wave377_apply.log"
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
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing_tags = sorted(expected_tags - tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {', '.join(missing_tags)}")

        decompile_text = decompile_text_for(Path(decompile_dir), address)
        if not decompile_text:
            failures.append(f"{address} missing decompile text")
        for token in spec["decompileTokens"]:
            if str(token) not in decompile_text:
                failures.append(f"{address} missing decompile token: {token}")
        for token in STALE_TOKENS:
            if token in decompile_text and str(spec["name"]) not in token:
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
        expected_target = normalize_address(target_addr)
        expected_instruction = normalize_address(instruction_addr)
        hit = any(
            normalize_address(row.get("function_entry", "")) == expected_target
            and normalize_address(row.get("instruction_addr", "")) == expected_instruction
            and row.get("mnemonic") == mnemonic
            and row.get("operands") == operands
            and row.get("bytes") == bytes_
            for row in instructions
        )
        if hit:
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instruction_addr} {mnemonic} {operands}")

    return {
        "schema": "ghidra-frontend-core-wave377/v1",
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
