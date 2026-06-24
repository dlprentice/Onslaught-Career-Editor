#!/usr/bin/env python3
"""Validate the Wave381 CGame/CEndLevelData/console Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/game-helper-wave381/current")
OUTPUT_NAME = "game-helper-wave381.json"

COMMON_TAGS = {
    "static-reaudit",
    "game-helper-wave381",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    previous_names: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
        "previousNames": previous_names or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004496e0": target(
        "CEndLevelData__IsAllSecondaryObjectivesComplete",
        "bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)",
        [
            "Name/signature correction",
            "CEndLevelData::IsAllSecondaryObjectivesComplete",
            "secondary objective status slots",
            "ERROR: No secondary objectives",
            "runtime progression behavior, and rebuild parity remain unproven",
        ],
        [
            "CEndLevelData__IsAllSecondaryObjectivesComplete",
            "this + 0x4d0",
            "CConsole__Printf",
            "ERROR__No_secondary_objectives",
        ],
        ["end-level-data", "secondary-objectives", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CCareer__AreSecondaryObjectivesComplete"],
    ),
    "0x00470650": target(
        "CGame__DrawDebugStuff",
        "void __fastcall CGame__DrawDebugStuff(void * this)",
        [
            "Name/signature correction",
            "CGame::DrawDebugStuff",
            "heap and memory pressure",
            "selected squad/unit debug overlay",
            "runtime debug overlay behavior, and rebuild parity remain unproven",
        ],
        [
            "CGame__DrawDebugStuff",
            "CGame__ResetRenderStateForWorldRender",
            "SQUAD_INFO",
            "UNIT_INFO",
            "+ 0xa04",
            "+ 0x9f8",
        ],
        ["game", "debug-overlay", "source-parity", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__RenderDebugMemoryAndSelectionInfo"],
    ),
    "0x00472240": target(
        "CConsole__AppendToStatusBufferV",
        "void __cdecl CConsole__AppendToStatusBufferV(void * console, char * format)",
        [
            "Name/signature correction",
            "formatted status/debug overlay text",
            "vsprintf",
            "console+0x2710",
            "variadic stack arguments",
            "runtime console overlay behavior, and rebuild parity remain unproven",
        ],
        [
            "CConsole__AppendToStatusBufferV",
            "vsprintf",
            "format",
            "console",
            "+ 10000",
        ],
        ["console", "status-overlay", "varargs", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__AppendToStatusBufferV"],
    ),
    "0x00472270": target(
        "Frontend__XorWideTextBlock100BytesToScratch",
        "short * __cdecl Frontend__XorWideTextBlock100BytesToScratch(short * encoded_text, short * xor_mask)",
        [
            "Name/signature correction",
            "0x64-byte wide-text block",
            "into the DAT_00679e18 scratch buffer",
            "FrontendUpdate_CheatChecks",
            "runtime frontend text behavior, and rebuild parity remain unproven",
        ],
        [
            "Frontend__XorWideTextBlock100BytesToScratch",
            "_DAT_00679e18",
            "encoded_text[0x31]",
            "encoded_text",
            "xor_mask",
        ],
        ["frontend", "wide-text", "xor", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__XorBlock64Words"],
    ),
    "0x00472570": target(
        "CGame__DoWeWantMesh",
        "bool __thiscall CGame__DoWeWantMesh(void * this, char * mesh)",
        [
            "Signature/comment/tag correction",
            "CGame::DoWeWantMesh",
            "player cockpit and wingman mesh strings",
            "wingman mesh string",
            "runtime resource loading behavior, and rebuild parity remain unproven",
        ],
        [
            "CGame__DoWeWantMesh",
            "mesh",
            "stricmp",
            "+ 0x22c",
            "+ 0x25e",
            "+ 300",
        ],
        ["game", "mesh", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x004725f0": target(
        "CGame__GetPlayerLives",
        "int __thiscall CGame__GetPlayerLives(void * this, int player_index)",
        [
            "Signature/comment/tag correction",
            "CGame::GetPlayerLives",
            "mPlayer1Lives for player_index 1",
            "mPlayer2Lives for player_index 2",
            "runtime lives behavior, and rebuild parity remain unproven",
        ],
        [
            "CGame__GetPlayerLives",
            "player_index",
            "+ 0x290",
            "+ 0x294",
            "== 1",
            "== 2",
        ],
        ["game", "lives", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x00472650": target(
        "CGame__IsRunningResources",
        "bool __fastcall CGame__IsRunningResources(void * this)",
        [
            "Signature/comment/tag correction",
            "CGame::IsRunningResources",
            "current level",
            "last resource-loaded level global",
            "runtime resource loading behavior, and rebuild parity remain unproven",
        ],
        [
            "CGame__IsRunningResources",
            "DAT_006317cc",
            "+ 0x30",
        ],
        ["game", "resources", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x00472670": target(
        "CGame__GetNumPrimaryObjectives",
        "int __fastcall CGame__GetNumPrimaryObjectives(void * this)",
        [
            "Name/signature correction",
            "CGame::GetNumPrimaryObjectives",
            "mPrimaryObjectives",
            "non-MOS_NOT_DEFINED entries",
            "runtime objective UI behavior, and rebuild parity remain unproven",
        ],
        [
            "CGame__GetNumPrimaryObjectives",
            "+ 0x4c",
            "10",
            "!= 0",
        ],
        ["game", "objectives", "primary-objectives", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__CountActiveSlots_A"],
    ),
    "0x00472690": target(
        "CGame__GetNumSecondaryObjectives",
        "int __fastcall CGame__GetNumSecondaryObjectives(void * this)",
        [
            "Name/signature correction",
            "CGame::GetNumSecondaryObjectives",
            "mSecondaryObjectives",
            "non-MOS_NOT_DEFINED entries",
            "runtime objective UI behavior, and rebuild parity remain unproven",
        ],
        [
            "CGame__GetNumSecondaryObjectives",
            "+ 0x9c",
            "10",
            "!= 0",
        ],
        ["game", "objectives", "secondary-objectives", "name-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__CountActiveSlots_B"],
    ),
}

XREF_EVIDENCE = [
    ("0x004496e0", "0x0041bf5d", "CCareer__ReCalcLinks", "UNCONDITIONAL_CALL"),
    ("0x004496e0", "0x0046d7bd", "CGame__FillOutEndLevelData", "UNCONDITIONAL_CALL"),
    ("0x004496e0", "0x0046da6a", "CGame__RunOutroFMV", "UNCONDITIONAL_CALL"),
    ("0x00470650", "0x0053ef91", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
    ("0x00472240", "0x00471655", "FrontendUpdate_CheatChecks", "UNCONDITIONAL_CALL"),
    ("0x00472240", "0x004fe851", "CWarspite__Init", "UNCONDITIONAL_CALL"),
    ("0x00472270", "0x004717e7", "FrontendUpdate_CheatChecks", "UNCONDITIONAL_CALL"),
    ("0x00472570", "0x004aac73", "CMesh__Deserialize", "UNCONDITIONAL_CALL"),
    ("0x004725f0", "0x00486128", "CExplosionInitThing__RenderObjectiveStatusPanel", "UNCONDITIONAL_CALL"),
    ("0x00472650", "0x0050d9fe", "CWorldMeshList__Add", "UNCONDITIONAL_CALL"),
    ("0x00472670", "0x004d1050", "CPauseMenu__InitPauseSession", "UNCONDITIONAL_CALL"),
    ("0x00472690", "0x004d105e", "CPauseMenu__InitPauseSession", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x004496e0", "0x004496e9", "LEA", "EDX, [ECX + 0x4d0]", "8d 91 d0 04 00 00"),
    ("0x004496e0", "0x00449722", "CALL", "0x00441740", "e8 19 80 ff ff"),
    ("0x00470650", "0x0047065e", "CALL", "0x004eb1e0", "e8 7d ab 07 00"),
    ("0x00470650", "0x00470663", "MOV", "ECX, dword ptr [EBX + 0xa04]", "8b 8b 04 0a 00 00"),
    ("0x00472240", "0x0047224f", "MOV", "EDX, dword ptr [ESI + 0x2710]", "8b 96 10 27 00 00"),
    ("0x00472240", "0x00472256", "CALL", "0x0055e38c", "e8 31 c1 0e 00"),
    ("0x00472270", "0x00472278", "MOV", "DX, word ptr [EAX]", "66 8b 10"),
    ("0x00472570", "0x00472574", "MOV", "EDI, dword ptr [ESP + 0xc]", "8b 7c 24 0c"),
    ("0x00472570", "0x00472580", "CALL", "0x00568390", "e8 0b 5e 0f 00"),
    ("0x00472570", "0x00472593", "RET", "0x4", "c2 04 00"),
    ("0x004725f0", "0x004725f4", "CMP", "EAX, 0x1", "83 f8 01"),
    ("0x004725f0", "0x004725f9", "MOV", "EAX, dword ptr [ECX + 0x290]", "8b 81 90 02 00 00"),
    ("0x00472650", "0x00472650", "MOV", "EDX, dword ptr [0x006317cc]", "8b 15 cc 17 63 00"),
    ("0x00472650", "0x00472657", "MOV", "ESI, dword ptr [ECX + 0x30]", "8b 71 30"),
    ("0x00472670", "0x00472672", "ADD", "ECX, 0x4c", "83 c1 4c"),
    ("0x00472670", "0x00472675", "MOV", "EDX, 0xa", "ba 0a 00 00 00"),
    ("0x00472690", "0x00472692", "ADD", "ECX, 0x9c", "81 c1 9c 00 00 00"),
    ("0x00472690", "0x00472698", "MOV", "EDX, 0xa", "ba 0a 00 00 00"),
]

STALE_TOKENS = [
    "CCareer__AreSecondaryObjectivesComplete",
    "CGame__RenderDebugMemoryAndSelectionInfo",
    "CGame__AppendToStatusBufferV",
    "CGame__XorBlock64Words",
    "CGame__CountActiveSlots_A",
    "CGame__CountActiveSlots_B",
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
    dry_log_path = dry_log_path or root / "game_helper_wave381_dry.log"
    apply_log_path = apply_log_path or root / "game_helper_wave381_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
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

    return {
        "schema": "ghidra-game-helper-wave381/v1",
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
