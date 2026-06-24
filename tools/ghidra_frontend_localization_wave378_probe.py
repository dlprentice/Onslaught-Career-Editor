#!/usr/bin/env python3
"""Validate the Wave378 frontend localization/text Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-localization-wave378/current")
OUTPUT_NAME = "frontend-localization-wave378.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-localization-wave378",
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
    "0x00469c20": target(
        "CFrontEnd__ResolveEpisodeNameTextByIndex",
        "short * __cdecl CFrontEnd__ResolveEpisodeNameTextByIndex(int episode_index)",
        [
            "Return/signature hardening",
            "episode indices 1..8",
            "CText__GetStringById",
            "Unnamed Episode",
            "runtime localization behavior remains unproven",
        ],
        ["episode_index", "CText__GetStringById", "Text__AsciiToWideScratch", "Unnamed_Episode"],
        ["frontend", "localization", "episode-name", "signature-hardened", "comment-hardened"],
    ),
    "0x00469cf0": target(
        "CFrontEnd__ResolveLevelNameTextIdByCode",
        "int __cdecl CFrontEnd__ResolveLevelNameTextIdByCode(int level_code)",
        [
            "Parameter/comment hardening",
            "level/world code",
            "localized text-id",
            "returns -1",
            "runtime level-name localization remains unproven",
        ],
        ["level_code", "return -1", "0x15f8838", "0x162946b"],
        ["frontend", "localization", "level-name", "signature-hardened", "comment-hardened"],
    ),
    "0x0046a1f0": target(
        "FrontEndText__GetLevelNameTextAfterCode",
        "short * __cdecl FrontEndText__GetLevelNameTextAfterCode(int level_code, int after_index)",
        [
            "Owner/return/signature correction",
            "not CUnitAI",
            "CFrontEnd__ResolveLevelNameTextIdByCode",
            "CText__GetStringByIdAfter",
            "no-boundary briefing renderer",
            "runtime briefing rendering remains unproven",
        ],
        ["level_code", "after_index", "CFrontEnd__ResolveLevelNameTextIdByCode", "CText__GetStringByIdAfter"],
        ["frontend", "localization", "briefing", "level-name", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0046a210": target(
        "FrontEnd__GetBriefingLevelListTextColor",
        "uint __cdecl FrontEnd__GetBriefingLevelListTextColor(void)",
        [
            "Name/signature correction",
            "returns literal 0xffffdf5f",
            "only observed caller",
            "draw-color component",
            "not a text-id helper",
            "runtime briefing rendering remains unproven",
        ],
        ["FrontEnd__GetBriefingLevelListTextColor", "0xffffdf5f", "return"],
        ["frontend", "briefing", "render", "color", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0046a220": target(
        "FrontEndText__GetMultiplayerLevelDescriptionByType",
        "short * __cdecl FrontEndText__GetMultiplayerLevelDescriptionByType(int level_type)",
        [
            "Owner/return/signature correction",
            "not CUnitAI",
            "multiplayer level description",
            "CText__GetStringById",
            "Unknown Multiplayer Level Description",
            "runtime multiplayer frontend rendering remains unproven",
        ],
        ["level_type", "CText__GetStringById", "Text__AsciiToWideScratch", "Unknown_Multiplayer_Level"],
        ["frontend", "localization", "multiplayer", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0046a2a0": target(
        "FrontEndText__GetLocalizedOrFallbackTextByToken",
        "short * __cdecl FrontEndText__GetLocalizedOrFallbackTextByToken(int text_token)",
        [
            "Owner/comment correction",
            "broad frontend text-token resolver",
            "not save-game-specific",
            "debug fallback toggle",
            "DAT_00679b88",
            "runtime frontend localization behavior remains unproven",
        ],
        ["text_token", "PlatformInput__ConsumeKeyOnce", "DAT_00679b88", "FrontEndText__GetAsciiFallbackTextByToken", "CText__GetStringById"],
        ["frontend", "localization", "text-token", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0046b1e0": target(
        "FrontEndText__GetAsciiFallbackTextByToken",
        "short * __cdecl FrontEndText__GetAsciiFallbackTextByToken(int text_token)",
        [
            "Owner/return/signature correction",
            "ASCII fallback frontend text-token resolver",
            "Text__AsciiToWideScratch",
            "Unknown Text",
            "not save-game-specific",
            "runtime fallback toggle behavior remains unproven",
        ],
        ["text_token", "Text__AsciiToWideScratch", "Unknown_Text", "return"],
        ["frontend", "localization", "text-token", "fallback", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00469c20", "0x0045a723", "CFEPMultiplayerStart__SubObj8848__Render", "UNCONDITIONAL_CALL"),
    ("0x00469c20", "0x0046199b", "CFEPLevelSelect__Render", "UNCONDITIONAL_CALL"),
    ("0x00469cf0", "0x0048f98c", "CDXEngine__RenderPostMissionOverlayAndMenu", "UNCONDITIONAL_CALL"),
    ("0x00469cf0", "0x0046a1f5", "FrontEndText__GetLevelNameTextAfterCode", "UNCONDITIONAL_CALL"),
    ("0x0046a1f0", "0x004522ad", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x0046a210", "0x0045230c", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x0046a220", "0x0051d8d9", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x0046a2a0", "0x0044d9b9", "CFrontEnd__RenderAndProcessModalPanel", "UNCONDITIONAL_CALL"),
    ("0x0046a2a0", "0x005279fc", "CGame__DrawLocalCoopControllerPrompt", "UNCONDITIONAL_CALL"),
    ("0x0046a2a0", "0x00450e56", "CFEPBEConfig__Render", "UNCONDITIONAL_CALL"),
    ("0x0046a2a0", "0x0051b497", "CFEPDirectory__Render", "UNCONDITIONAL_CALL"),
    ("0x0046a2a0", "0x005211de", "CFEPVirtualKeyboard__Render", "UNCONDITIONAL_CALL"),
    ("0x0046b1e0", "0x0046a2c5", "FrontEndText__GetLocalizedOrFallbackTextByToken", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00469c20", "0x00469c20", "MOV", "EAX, dword ptr [ESP + 0x4]", "8b 44 24 04"),
    ("0x00469c20", "0x00469cb5", "PUSH", "0x62aac4", "68 c4 aa 62 00"),
    ("0x00469cf0", "0x00469e8d", "OR", "EAX, 0xffffffff", "83 c8 ff"),
    ("0x0046a1f0", "0x0046a1f5", "CALL", "0x00469cf0", "e8 f6 fa ff ff"),
    ("0x0046a1f0", "0x0046a208", "CALL", "0x004f2500", "e8 f3 82 08 00"),
    ("0x0046a210", "0x0046a210", "MOV", "EAX, 0xffffdf5f", "b8 5f df ff ff"),
    ("0x0046a220", "0x0046a270", "PUSH", "0x62aad4", "68 d4 aa 62 00"),
    ("0x0046a2a0", "0x0046a2a7", "CALL", "0x00515980", "e8 d4 b6 0a 00"),
    ("0x0046a2a0", "0x0046a2c5", "CALL", "0x0046b1e0", "e8 16 0f 00 00"),
    ("0x0046b1e0", "0x0046b1e0", "MOV", "EAX, dword ptr [ESP + 0x4]", "8b 44 24 04"),
    ("0x0046b1e0", "0x0046b76c", "PUSH", "0x62aafc", "68 fc aa 62 00"),
]

CALLSITE_EVIDENCE = [
    ("0x004522ad", "0x004522ad", "CALL", "0x0046a1f0", "e8 3e 7f 01 00"),
    ("0x004522ad", "0x004522bf", "PUSH", "EAX", "50"),
    ("0x0045230c", "0x0045230c", "CALL", "0x0046a210", "e8 ff 7e 01 00"),
    ("0x0045230c", "0x00452316", "SHR", "ECX, 0x8", "c1 e9 08"),
    ("0x0051d8d9", "0x0051d8d9", "CALL", "0x0046a220", "e8 42 c9 f4 ff"),
    ("0x0051d8d9", "0x0051d8ea", "PUSH", "EAX", "50"),
]

STALE_TOKENS = [
    "CUnitAI__GetStringByResolvedTextIdAfter",
    "CUnitAI__GetMultiplayerLevelDescriptionByType",
    "CFrontEnd__GetFallbackUnnamedLevelTextId",
    "CFEPSaveGame__GetLocalizedOrFallbackTextByToken",
    "CFEPSaveGame__GetAsciiFallbackTextByToken",
    "void __cdecl CFrontEnd__ResolveEpisodeNameTextByIndex",
    "void __cdecl FrontEndText__GetAsciiFallbackTextByToken",
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
    callsites_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "frontend_localization_wave378_dry.log"
    apply_log_path = apply_log_path or root / "frontend_localization_wave378_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    callsites_path = callsites_path or root / "callsite_instructions.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)

    if not has_summary(dry_text, updated=0, skipped=len(TARGETS), renamed=0, would_rename=5):
        failures.append(f"dry-run summary missing/dirty: {relative(dry_log_path)}")
    if not has_summary(apply_text, updated=len(TARGETS), skipped=0, renamed=5, would_rename=0):
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

    callsites = read_tsv(callsites_path)
    callsite_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in CALLSITE_EVIDENCE:
        if evidence_hit(
            callsites,
            target=target_addr,
            instruction_addr=instruction_addr,
            mnemonic=mnemonic,
            operands=operands,
            bytes_=bytes_,
        ):
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {target_addr} {instruction_addr} {mnemonic} {operands}")

    return {
        "schema": "ghidra-frontend-localization-wave378/v1",
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
