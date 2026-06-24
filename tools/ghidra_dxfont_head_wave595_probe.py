#!/usr/bin/env python3
"""Validate Wave595 DX font-head Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave595-dxfont-head-0053f730"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxfont_head_wave595_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXFONT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFont.cpp" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
PLATFORM_DOC = ROOT / "reverse-engineering" / "source-code" / "core" / "platform-system.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave595_backup_summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x0053f730": (
        "CDXBitmapFont__ctor_base",
        "void * __fastcall CDXBitmapFont__ctor_base(void * this)",
    ),
    "0x0053f770": (
        "CDXBitmapFont__ReleaseFontResources",
        "void __fastcall CDXBitmapFont__ReleaseFontResources(void * this)",
    ),
    "0x0053f7d0": (
        "CDXBitmapFont__InitNamedFontSlot",
        "void __thiscall CDXBitmapFont__InitNamedFontSlot(void * this, char * font_face, int font_size, int font_style_flags)",
    ),
    "0x0053f830": (
        "CDXBitmapFont__InitTextureFontSlot",
        "void __thiscall CDXBitmapFont__InitTextureFontSlot(void * this, char * texture_name, int glyph_cell_width)",
    ),
    "0x0053f880": (
        "CDXFont__CreateFromTexture",
        "void __fastcall CDXFont__CreateFromTexture(void * this)",
    ),
    "0x0053fb00": (
        "CDXFont__CreateGDIFont",
        "void __fastcall CDXFont__CreateGDIFont(void * this)",
    ),
    "0x00540010": (
        "CDXFont__DrawTextScaled",
        "int __thiscall CDXFont__DrawTextScaled(void * this, float x, float y, float depth_z, float x_scale, float y_scale, uint packed_argb, short * text, uint flags, float * per_char_argb)",
    ),
    "0x00540640": (
        "CDXFont__DrawText",
        "void __thiscall CDXFont__DrawText(void * this, float x, float y, uint packed_argb, short * text, uint flags, float * per_char_argb, float depth_z)",
    ),
}

EXPECTED_TAGS = {
    "0x0053f730": {"dxfont-head-wave595", "cdxbitmapfont", "constructor", "font-loading"},
    "0x0053f770": {"dxfont-head-wave595", "cdxbitmapfont", "resource-release", "font-unload", "owner-corrected"},
    "0x0053f7d0": {"dxfont-head-wave595", "cdxbitmapfont", "named-font-slot", "gdi-font", "ret-0xc", "phantom-param-removed"},
    "0x0053f830": {"dxfont-head-wave595", "cdxbitmapfont", "texture-font-slot", "font-loading", "ret-0x8", "phantom-param-removed", "owner-corrected"},
    "0x0053f880": {"dxfont-head-wave595", "cdxfont", "texture-font", "glyph-metrics", "lazy-create"},
    "0x0053fb00": {"dxfont-head-wave595", "cdxfont", "gdi-font", "glyph-metrics", "lazy-create", "seh-wrapped"},
    "0x00540010": {"dxfont-head-wave595", "cdxfont", "text-render", "wide-text", "ret-0x24", "render-state"},
    "0x00540640": {"dxfont-head-wave595", "cdxfont", "text-render", "wide-text", "ret-0x1c", "wrapper"},
}

COMMENT_TOKENS = {
    "0x0053f730": ("PCPlatform__LoadFonts", "PCPlatform__DeserializeFontsAndAssets", "this+0x168", "vtable 0x005e504c"),
    "0x0053f770": ("CPCPlatform__UnloadFonts", "PCPlatform__DeserializeFontsAndAssets", "this+0x170", "returns without freeing the object"),
    "0x0053f7d0": ("RET 0xc", "Terminal/debug font slot", "this+4", "this+0x15c"),
    "0x0053f830": ("RET 0x8", "texture-backed main/small/title", "this+0x5c", "glyph_cell_width"),
    "0x0053f880": ("this+0x15c", "texture-backed path", "this+0x5c", "glyph UV/width metrics"),
    "0x0053fb00": ("GDI/font-face path", "CTexture at this+0x170", "rasterizes printable characters", "SystemFont"),
    "0x00540010": ("RET 0x24", "UTF-16 text", "CFastVB quads", "returns 0"),
    "0x00540640": ("RET 0x1c", "default x/y scale of 1.0", "CDXFont__DrawTextScaled"),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "signature-corrected", "comment-hardened"}
OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully recovered", "fully reverse-engineered")


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 3, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 8, "skipped": 0, "renamed": 3, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "final-dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post" / "metadata.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post" / "tags.tsv")}
    if set(metadata_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata_rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], COMMENT_TOKENS[address], failures)
        require_tokens(f"{address} comment", row["comment"], ("Static retail evidence only", "BEA patching", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tag_rows.get(address)
        if not tag_row:
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = (COMMON_TAGS | EXPECTED_TAGS[address]) - actual_tags
        if tag_row["name"] != name:
            failures.append(f"{address} tag name mismatch: {tag_row['name']} != {name}")
        if tag_row["status"] != "OK":
            failures.append(f"{address} tag status mismatch: {tag_row['status']}")
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "post/xrefs.tsv": 84,
        "post/instructions.tsv": 392,
        "post/decompile/index.tsv": 10,
    }
    actual_counts = {
        "post/xrefs.tsv": row_count(BASE / "post" / "xrefs.tsv"),
        "post/instructions.tsv": row_count(BASE / "post" / "instructions.tsv"),
        "post/decompile/index.tsv": row_count(BASE / "post" / "decompile" / "index.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_instructions(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(BASE / "post" / "xrefs.tsv")
    }
    expected_xrefs = {
        ("0x0053f730", "CDXBitmapFont__ctor_base", "0x00515634", "0x005155e0", "PCPlatform__LoadFonts", "UNCONDITIONAL_CALL"),
        ("0x0053f730", "CDXBitmapFont__ctor_base", "0x00515c94", "0x00515b10", "PCPlatform__DeserializeFontsAndAssets", "UNCONDITIONAL_CALL"),
        ("0x0053f770", "CDXBitmapFont__ReleaseFontResources", "0x005157c0", "0x005157b0", "CPCPlatform__UnloadFonts", "UNCONDITIONAL_CALL"),
        ("0x0053f770", "CDXBitmapFont__ReleaseFontResources", "0x00515b49", "0x00515b10", "PCPlatform__DeserializeFontsAndAssets", "UNCONDITIONAL_CALL"),
        ("0x0053f7d0", "CDXBitmapFont__InitNamedFontSlot", "0x005156d0", "0x005155e0", "PCPlatform__LoadFonts", "UNCONDITIONAL_CALL"),
        ("0x0053f830", "CDXBitmapFont__InitTextureFontSlot", "0x00515651", "0x005155e0", "PCPlatform__LoadFonts", "UNCONDITIONAL_CALL"),
        ("0x0053f880", "CDXFont__CreateFromTexture", "0x00540123", "0x00540010", "CDXFont__DrawTextScaled", "UNCONDITIONAL_CALL"),
        ("0x0053fb00", "CDXFont__CreateGDIFont", "0x005406b4", "0x00540680", "CDXFont__GetTextExtent", "UNCONDITIONAL_CALL"),
        ("0x00540010", "CDXFont__DrawTextScaled", "0x0054066d", "0x00540640", "CDXFont__DrawText", "UNCONDITIONAL_CALL"),
        ("0x00540640", "CDXFont__DrawText", "0x0042ce0e", "0x0042c810", "CConsole__RenderLoadingScreen", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instructions = {
        (
            normalize_address(row["target_addr"]),
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in read_tsv_rows(BASE / "post" / "instructions.tsv")
    }
    expected_instructions = {
        ("0x0053f7d0", "0x0053f826", "CDXBitmapFont__InitNamedFontSlot", "RET", "0xc"),
        ("0x0053f830", "0x0053f871", "CDXBitmapFont__InitTextureFontSlot", "RET", "0x8"),
        ("0x00540640", "0x0054063a", "CDXFont__DrawTextScaled", "RET", "0x24"),
        ("0x00540640", "0x00540672", "CDXFont__DrawText", "RET", "0x1c"),
        ("0x00540640", "0x0054066d", "CDXFont__DrawText", "CALL", "0x00540010"),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 3047,
        "undefinedSignatureCount": 1343,
        "paramSignatureCount": 1091,
    }
    if queue["totalFunctions"] != 6093:
        failures.append(f"queue total mismatch: {queue['totalFunctions']} != 6093")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x00540840" or head.get("name") != "PCPlatform__ReadHeaderPairAndResetByteCount":
        failures.append(f"queue head mismatch: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    expected_backup = {
        "backupPath": "G:\\GhidraBackups\\BEA_20260519-151349_post_wave595_dxfont_head_verified",
        "fileCount": 19,
        "totalBytes": 161057671,
        "diffCount": 0,
        "manifestHash": "e07246471f4c0b1390ed79adae1b1649c1f31e25b5e8c555709e87ca289a529c",
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")


def check_docs(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: (
            "Wave595 hardened the DX bitmap/font queue head",
            "CDXBitmapFont__ctor_base",
            "CDXBitmapFont__ReleaseFontResources",
            "CDXBitmapFont__InitTextureFontSlot",
            "Post-save read-back verified 8 metadata rows",
            "`3046` commented",
            "0x00540840 PCPlatform__ReadHeaderPairAndResetByteCount",
            "G:\\GhidraBackups\\BEA_20260519-151349_post_wave595_dxfont_head_verified",
        ),
        FUNCTION_INDEX: (
            "Latest saved-correction note: Wave595 DX font-head hardening",
            "CDXBitmapFont__InitTextureFontSlot",
            "Post-Wave595 queue telemetry is `6093` functions, `3046` commented",
        ),
        DXFONT_DOC: (
            "Wave595 static read-back update",
            "CDXBitmapFont__ctor_base",
            "int __thiscall CDXFont__DrawTextScaled",
            "RET 0x24",
        ),
        PCPLATFORM_DOC: (
            "Wave595 DXFont head note",
            "CDXBitmapFont__InitTextureFontSlot",
            "CDXBitmapFont__ReleaseFontResources",
        ),
        PLATFORM_DOC: (
            "Wave595 retail read-back",
            "font22_512.tga",
            "CDXBitmapFont__InitTextureFontSlot",
        ),
        CAMPAIGN: (
            "### Wave 595: DX Font Head",
            "CDXBitmapFont__ReleaseFontResources",
            "strict clean-signature proxy `3001/6093 = 49.25%`",
        ),
        BACKLOG: (
            "0x0053f730,0x0053f770,0x0053f7d0,0x0053f830,0x0053f880,0x0053fb00,0x00540010,0x00540640",
            "Ghidra DX font-head Wave595 signature/comment hardening",
            "DiffCount=0",
        ),
    }
    for path, tokens in doc_tokens.items():
        text = read_text(path)
        require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.relative_to(ROOT)} overclaims: {token}")

    ledger_text = read_text(LEDGER)
    attempt_text = read_text(ATTEMPT_LOG)
    require_tokens("ledger", ledger_text, ("Wave595", "CDXBitmapFont__ctor_base", "strict clean-signature proxy 3001/6093 = 49.25%"), failures)
    require_tokens("attempt log", attempt_text, ("\"attempt_id\":20250", "Wave595", "headless_java_apply_signature_comment_tags_and_three_renames"), failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    for check in (check_logs, check_post_exports, check_xrefs_and_instructions, check_queue_and_backup, check_docs):
        try:
            check(failures)
        except Exception as exc:  # noqa: BLE001 - report all focused artifact issues together.
            failures.append(f"{check.__name__} raised {exc.__class__.__name__}: {exc}")

    if failures:
        print("Wave595 DX font-head probe FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave595 DX font-head probe PASS")
    print("Verified 8 metadata rows, 8 tag rows, 84 xref rows, 392 instruction rows, 10 decompile rows, queue telemetry, docs, ledgers, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
