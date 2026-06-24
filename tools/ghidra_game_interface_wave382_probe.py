#!/usr/bin/env python3
"""Validate the Wave382 GameInterface Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/game-interface-wave382/current")
OUTPUT_NAME = "game-interface-wave382.json"

COMMON_TAGS = {
    "static-reaudit",
    "game-interface-wave382",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    previous_names: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
        "previousNames": previous_names,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004729d0": target(
        "CGameInterface__ctor_base",
        "void __fastcall CGameInterface__ctor_base(void * this)",
        [
            "Name/signature correction",
            "global GameInterface object",
            "0x005dbc2c vtable",
            "runtime menu behavior, and rebuild parity remain unproven",
        ],
        ["CGameInterface__ctor_base", "this", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dbc2c"],
        ["game-interface", "constructor", "monitor", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGameInterface__ctor_like_004729d0"],
    ),
    "0x004729e0": target(
        "CGameInterface__ResetMenuState",
        "void __fastcall CGameInterface__ResetMenuState(void * this)",
        [
            "Name/signature correction",
            "CGame::Init and CGame::InitRestartLoop",
            "enabling six menu entries",
            "setting menu mode 1",
            "runtime pause/menu behavior, and rebuild parity remain unproven",
        ],
        ["CGameInterface__ResetMenuState", "+ 0x44", "+ 0x2c", "this"],
        ["game-interface", "pause-menu", "menu-state", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__InitMouseInputState"],
    ),
    "0x00472a10": target(
        "CGameInterface__InitResources",
        "void __fastcall CGameInterface__InitResources(void * this)",
        [
            "Name/signature correction",
            "GAMEINTERFACE.InitResources",
            "Interface_Joypad.tga",
            "Menu_background.tga",
            "runtime rendering behavior, and rebuild parity remain unproven",
        ],
        ["CGameInterface__InitResources", "Interface_Joypad_tga", "hud_Menu_background_tga", "+ 0xc", "+ 8"],
        ["game-interface", "resources", "textures", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGameInterface__LoadHudTextures"],
    ),
    "0x00472a50": target(
        "CGameInterface__Shutdown",
        "void __fastcall CGameInterface__Shutdown(void * this)",
        [
            "Name/signature correction",
            "GAMEINTERFACE.Shutdown",
            "texture references",
            "CMonitor shutdown core",
            "runtime shutdown behavior, and rebuild parity remain unproven",
        ],
        ["CGameInterface__Shutdown", "CHud__DecrementCounter9C", "CMonitor__Shutdown_Core", "+ 0xc", "+ 8"],
        ["game-interface", "shutdown", "textures", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGameInterface__VFunc_02_00472a50"],
    ),
    "0x00472a90": target(
        "CGameInterface__ToggleMenuDisplay",
        "void __fastcall CGameInterface__ToggleMenuDisplay(void * this)",
        [
            "Name/signature correction",
            "GAMEINTERFACE.ToggleMenuDisplay",
            "menu-active byte",
            "first enabled entry",
            "mouse input",
            "runtime pause/menu behavior, and rebuild parity remain unproven",
        ],
        ["CGameInterface__ToggleMenuDisplay", "PlatformInput__ShutdownMouse", "PlatformInput__InitMouse", "+ 0x1c", "+ 0x20"],
        ["game-interface", "pause-menu", "mouse-input", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__ToggleMouseInputState"],
    ),
    "0x00472ad0": target(
        "CGameInterface__AdvanceMenuSelectionWithWrap",
        "void __fastcall CGameInterface__AdvanceMenuSelectionWithWrap(void * this)",
        [
            "Name/signature correction",
            "selected menu entry",
            "wrap-around",
            "disabled entry flags",
            "frontend move sound",
            "runtime input behavior, and rebuild parity remain unproven",
        ],
        ["CGameInterface__AdvanceMenuSelectionWithWrap", "CFrontEnd__PlaySound", "+ 0x44", "+ 0x20", "+ 0x2c"],
        ["game-interface", "pause-menu", "selection", "name-corrected", "signature-hardened", "comment-hardened"],
        ["UISelectionList__AdvanceToNextEnabledWithWrap"],
    ),
    "0x00472b40": target(
        "CGameInterface__HandleMenuSelection",
        "void __thiscall CGameInterface__HandleMenuSelection(void * this, void * controller)",
        [
            "Name/signature correction",
            "controlling CController",
            "message log/message box focus transfer",
            "god-option notification",
            "prior third parameter was a decompiler artifact",
            "runtime menu behavior, and rebuild parity remain unproven",
        ],
        [
            "CGameInterface__HandleMenuSelection",
            "controller",
            "CController__RelinquishControl",
            "CController__SetToControl",
            "CEngine__SetOptionValueAndNotifyTarget",
            "DAT_008a9ab8",
        ],
        ["game-interface", "pause-menu", "controller", "options", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CDXEngine__HandlePauseOptionsSelection"],
    ),
    "0x00472f10": target(
        "CGameInterface__Render",
        "void __fastcall CGameInterface__Render(void * this)",
        [
            "Name/signature correction",
            "GAMEINTERFACE.Render",
            "CDXEngine::PostRender",
            "localized text",
            "cursor/click selection",
            "runtime visual/menu behavior and rebuild parity remain unproven",
        ],
        [
            "CGameInterface__Render",
            "CDXSurf__RenderSurface",
            "CVBufTexture__DrawSpriteEx",
            "CDXEngine__RenderMouseCursorSprite",
            "CGameInterface__HandleMenuSelection",
        ],
        ["game-interface", "pause-menu", "render", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CDXEngine__RenderAndProcessPauseOptionsOverlay"],
    ),
}

XREF_EVIDENCE = [
    ("0x004729e0", "0x0046c3ce", "CGame__Init", "UNCONDITIONAL_CALL"),
    ("0x004729e0", "0x0046c5b7", "CGame__InitRestartLoop", "UNCONDITIONAL_CALL"),
    ("0x00472a10", "0x0046e34e", "CGame__RunLevel", "UNCONDITIONAL_CALL"),
    ("0x00472a90", "0x0046ee6a", "CGame__Update", "UNCONDITIONAL_CALL"),
    ("0x00472b40", "0x004740a4", "CGameInterface__Render", "UNCONDITIONAL_CALL"),
    ("0x00472f10", "0x0053efd1", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x004729d0", "0x004729d9", "MOV", "dword ptr [EAX], 0x5dbc2c", "c7 00 2c bc 5d 00"),
    ("0x004729e0", "0x004729f1", "MOV", "byte ptr [ECX + 0x1c], DL", "88 51 1c"),
    ("0x004729e0", "0x00472a08", "STOSD.REP", "ES:EDI", "f3 ab"),
    ("0x00472a10", "0x00472a11", "PUSH", "0x1", "6a 01"),
    ("0x00472a50", "0x00472a5d", "CALL", "0x004f27e0", "e8 7e fd 07 00"),
    ("0x00472a90", "0x00472ac0", "CALL", "0x0042d3b0", "e8 eb a8 fb ff"),
    ("0x00472a90", "0x00472ac6", "JMP", "0x0042d310", "e9 45 a8 fb ff"),
    ("0x00472ad0", "0x00472b35", "CALL", "0x00468770", "e8 36 5c ff ff"),
    ("0x00472b40", "0x00472b70", "CALL", "0x0042e6e0", "e8 6b bb fb ff"),
    ("0x00472f10", "0x00472f2a", "MOV", "ESI, ECX", "8b f1"),
]

CALLSITE_EVIDENCE = [
    ("0x0046c3ce", "MOV", "ECX, 0x679fa8"),
    ("0x0046c5b7", "MOV", "ECX, 0x679fa8"),
    ("0x0046e34e", "MOV", "ECX, 0x679fa8"),
    ("0x0053efd1", "MOV", "ECX, 0x679fa8"),
    ("0x004740a4", "PUSH", "EAX"),
    ("0x004740a4", "MOV", "ECX, ESI"),
    ("0x004740a4", "CALL", "0x00472b40"),
]

STALE_TOKENS = [
    "CGameInterface__ctor_like_004729d0",
    "CGame__InitMouseInputState",
    "CGameInterface__LoadHudTextures",
    "CGameInterface__VFunc_02_00472a50",
    "CGame__ToggleMouseInputState",
    "UISelectionList__AdvanceToNextEnabledWithWrap",
    "CDXEngine__HandlePauseOptionsSelection",
    "CDXEngine__RenderAndProcessPauseOptionsOverlay",
    "int param_1",
    "void * param_2",
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


def expected_rename_count() -> int:
    return sum(1 for spec in TARGETS.values() if spec["previousNames"])


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
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    callsite_instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "game_interface_wave382_dry.log"
    apply_log_path = apply_log_path or root / "game_interface_wave382_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    callsite_instructions_path = callsite_instructions_path or root / "callsite_instructions_wave382.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    rename_count = expected_rename_count()

    if not has_summary(dry_text, updated=0, skipped=len(TARGETS), renamed=0, would_rename=rename_count):
        failures.append(f"dry-run summary missing/dirty: {relative(dry_log_path)}")
    if not has_summary(apply_text, updated=len(TARGETS), skipped=0, renamed=rename_count, would_rename=0):
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

    callsite_instructions = read_tsv(callsite_instructions_path)
    callsite_hits = 0
    for target_addr, mnemonic, operands in CALLSITE_EVIDENCE:
        if callsite_hit(callsite_instructions, target=target_addr, mnemonic=mnemonic, operands=operands):
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {target_addr} {mnemonic} {operands}")

    return {
        "schema": "ghidra-game-interface-wave382/v1",
        "status": "PASS" if not failures else "FAIL",
        "root": relative(root),
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata_rows),
            "tagRows": len(tag_rows),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "callsiteEvidenceHits": callsite_hits,
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
    print(f"callsiteEvidenceHits={report['summary']['callsiteEvidenceHits']}")
    print(f"wrote={relative(output_path)}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
