#!/usr/bin/env python3
"""Validate Wave596 DXFont/CDXFrontEnd Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave596-platform-frontend-head-00540840"
POST = BASE / "post_applied"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxfont_frontend_head_wave596_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXFONT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFont.cpp" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00540840": (
        "CDXBitmapFont__Deserialize",
        "void __thiscall CDXBitmapFont__Deserialize(void * this, void * chunk_reader)",
    ),
    "0x00540970": (
        "CDXBitmapFont__HasAnimatedTexture",
        "int __fastcall CDXBitmapFont__HasAnimatedTexture(void * this)",
    ),
    "0x00540b60": (
        "CDXFrontEnd__DestructorBody",
        "void __fastcall CDXFrontEnd__DestructorBody(void * this)",
    ),
    "0x00540bf0": (
        "CDXFrontEnd__Constructor",
        "void * __fastcall CDXFrontEnd__Constructor(void * this)",
    ),
    "0x00540c10": (
        "CDXFrontEnd__scalar_deleting_dtor",
        "void * __thiscall CDXFrontEnd__scalar_deleting_dtor(void * this, byte delete_flags)",
    ),
    "0x00540f70": (
        "CDXFrontEnd__RenderStart",
        "void __fastcall CDXFrontEnd__RenderStart(void * this)",
    ),
    "0x00540fb0": (
        "CDXFrontEnd__VFunc_07_00540fb0",
        "void __stdcall CDXFrontEnd__VFunc_07_00540fb0(int render_particles)",
    ),
}

EXPECTED_TAGS = {
    "0x00540840": {"dxfont-frontend-head-wave596", "cdxbitmapfont", "font-deserialize", "ret-0x4", "owner-corrected", "phantom-param-removed"},
    "0x00540970": {"dxfont-frontend-head-wave596", "cdxbitmapfont", "animated-texture", "loading-screen", "owner-corrected"},
    "0x00540b60": {"dxfont-frontend-head-wave596", "cdxfrontend", "destructor-body", "seh-wrapped", "owner-corrected"},
    "0x00540bf0": {"dxfont-frontend-head-wave596", "cdxfrontend", "constructor", "vtable-005e5054", "owner-corrected"},
    "0x00540c10": {"dxfont-frontend-head-wave596", "cdxfrontend", "scalar-deleting-dtor", "vtable-slot-1", "ret-0x4", "phantom-param-removed"},
    "0x00540f70": {"dxfont-frontend-head-wave596", "cdxfrontend", "render-start", "vtable-slot-6", "source-bridge", "owner-corrected"},
    "0x00540fb0": {"dxfont-frontend-head-wave596", "cdxfrontend", "render-tail", "vtable-slot-7", "ret-0x4", "param-renamed"},
}

COMMENT_TOKENS = {
    "0x00540840": ("PCPlatform__DeserializeFontsAndAssets", "RET 0x4", "this+0x170", "CVBufTexture"),
    "0x00540970": ("CConsole__RenderLoadingScreen", "this+0x170", "CDXTexture__GetAnimatedFrame"),
    "0x00540b60": ("CDXFrontEnd__scalar_deleting_dtor", "SEH-framed", "this+8", "CMonitor__Shutdown"),
    "0x00540bf0": ("raw startup/init", "CFEPMultiplayerStart__ctor", "vtable at 0x005e5054"),
    "0x00540c10": ("vtable 0x005e5054 slot 1", "RET 0x4", "delete_flags bit 0", "CDXMemoryManager"),
    "0x00540f70": ("vtable 0x005e5054 slot 6", "RenderStart", "CFrontEnd__RenderStart"),
    "0x00540fb0": ("vtable 0x005e5054 slot 7", "RET 0x4", "render_particles", "CFrontEnd__RenderCursorEndSceneAndAsyncSave"),
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


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    require_log_summary(BASE / "dry.log", {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 6, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 7, "skipped": 0, "renamed": 6, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "final-dry.log", {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags.tsv")}
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
        "post_applied/xrefs.tsv": 13,
        "post_applied/instructions.tsv": 679,
        "post_applied/decompile/index.tsv": 7,
        "post/vtables.tsv": 48,
    }
    actual_counts = {
        "post_applied/xrefs.tsv": row_count(POST / "xrefs.tsv"),
        "post_applied/instructions.tsv": row_count(POST / "instructions.tsv"),
        "post_applied/decompile/index.tsv": row_count(POST / "decompile" / "index.tsv"),
        "post/vtables.tsv": row_count(BASE / "post" / "vtables.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_instructions_vtables(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(POST / "xrefs.tsv")
    }
    expected_xrefs = {
        ("0x00540840", "CDXBitmapFont__Deserialize", "0x00515d65", "0x00515b10", "PCPlatform__DeserializeFontsAndAssets", "UNCONDITIONAL_CALL"),
        ("0x00540970", "CDXBitmapFont__HasAnimatedTexture", "0x0042cd3e", "0x0042c810", "CConsole__RenderLoadingScreen", "UNCONDITIONAL_CALL"),
        ("0x00540b60", "CDXFrontEnd__DestructorBody", "0x00540c13", "0x00540c10", "CDXFrontEnd__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("0x00540c10", "CDXFrontEnd__scalar_deleting_dtor", "0x005e5058", "<none>", "<no_function>", "DATA"),
        ("0x00540f70", "CDXFrontEnd__RenderStart", "0x00468227", "0x00468200", "CFrontEnd__Render", "UNCONDITIONAL_CALL"),
        ("0x00540f70", "CDXFrontEnd__RenderStart", "0x005e506c", "<none>", "<no_function>", "DATA"),
        ("0x00540fb0", "CDXFrontEnd__VFunc_07_00540fb0", "0x00468484", "0x00468200", "CFrontEnd__Render", "UNCONDITIONAL_CALL"),
        ("0x00540fb0", "CDXFrontEnd__VFunc_07_00540fb0", "0x005e5070", "<none>", "<no_function>", "DATA"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instructions = {
        (
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in read_tsv_rows(POST / "instructions.tsv")
    }
    expected_instructions = {
        ("0x0054096a", "CDXBitmapFont__Deserialize", "RET", "0x4"),
        ("0x00540c13", "CDXFrontEnd__scalar_deleting_dtor", "CALL", "0x00540b60"),
        ("0x00540c2d", "CDXFrontEnd__scalar_deleting_dtor", "RET", "0x4"),
        ("0x00540fac", "CDXFrontEnd__RenderStart", "RET", ""),
        ("0x00540fbc", "CDXFrontEnd__VFunc_07_00540fb0", "CALL", "0x00540c30"),
        ("0x00540fcb", "CDXFrontEnd__VFunc_07_00540fb0", "RET", "0x4"),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")

    slots = {
        (normalize_address(row["vtable"]), int(row["slot_index"])): row
        for row in read_tsv_rows(BASE / "post" / "vtables.tsv")
    }
    expected_slots = {
        ("0x005e5054", 1): ("0x00540c10", "CDXFrontEnd__scalar_deleting_dtor"),
        ("0x005e5054", 6): ("0x00540f70", "CDXFrontEnd__RenderStart"),
        ("0x005e5054", 7): ("0x00540fb0", "CDXFrontEnd__VFunc_07_00540fb0"),
    }
    for key, (entry, name) in expected_slots.items():
        row = slots.get(key)
        if row is None:
            failures.append(f"missing vtable slot {key}")
            continue
        if normalize_address(row["function_entry"]) != entry or row["function_name"] != name:
            failures.append(f"vtable slot {key} mismatch: {row['function_entry']} {row['function_name']} != {entry} {name}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 3040,
        "undefinedSignatureCount": 1343,
        "paramSignatureCount": 1085,
    }
    if queue["totalFunctions"] != 6093:
        failures.append(f"queue total mismatch: {queue['totalFunctions']} != 6093")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if normalize_address(head["address"]) != "0x00541200" or head["name"] != "CDXFrontEndVideo__CDXFrontEndVideo":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != r"G:\GhidraBackups\BEA_20260519-155113_post_wave596_dxfont_frontend_head_verified":
        failures.append(f"backup path mismatch: {backup.get('backupPath')}")
    expected_backup = {
        "fileCount": 19,
        "totalBytes": 161057671,
        "missingCount": 0,
        "extraCount": 0,
        "diffCount": 0,
        "manifestHash": "eb9f038af50b5a97a210b4447f8692b993547d896f5c51d622b89c73718672a2",
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")


def check_docs(failures: list[str]) -> None:
    expected_tokens = {
        PUBLIC_NOTE: (
            "Wave596",
            "CDXBitmapFont__Deserialize",
            "CDXFrontEnd__RenderStart",
            "3053",
            "3040",
            "0x00541200 CDXFrontEndVideo__CDXFrontEndVideo",
            "BEA_20260519-155113_post_wave596_dxfont_frontend_head_verified",
        ),
        FUNCTION_INDEX: (
            "Latest saved-correction note: Wave596",
            "CDXBitmapFont__Deserialize",
            "CDXFrontEnd__scalar_deleting_dtor",
            "CDXFrontEndVideo__CDXFrontEndVideo",
        ),
        DXFONT_DOC: (
            "Wave596 static read-back update",
            "CDXBitmapFont__Deserialize",
            "CDXBitmapFont__HasAnimatedTexture",
            "RET 0x4",
        ),
        PCPLATFORM_DOC: (
            "Wave596 note",
            "CDXBitmapFont__Deserialize",
            "PCPlatform__DeserializeFontsAndAssets",
        ),
        FRONTEND_DOC: (
            "Wave596 CDXFrontEnd wrapper hardening",
            "CDXFrontEnd__Constructor",
            "CDXFrontEnd__RenderStart",
            "CDXFrontEnd__VFunc_07_00540fb0",
        ),
        CAMPAIGN: (
            "Current DX font / CDXFrontEnd follow-up",
            "ghidra_dxfont_frontend_head_wave596_2026-05-19.md",
            "CDXFrontEndVideo__CDXFrontEndVideo",
        ),
        BACKLOG: (
            "Ghidra DX font / CDXFrontEnd head Wave596 signature/comment hardening",
            "CDXBitmapFont__Deserialize",
            "CDXFrontEnd__RenderStart",
            "BEA_20260519-155113_post_wave596_dxfont_frontend_head_verified",
        ),
    }
    for path, tokens in expected_tokens.items():
        text = read_text(path)
        require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.relative_to(ROOT)} overclaims: {token}")

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require_tokens(str(path.relative_to(ROOT)), text, ("Wave596", "CDXBitmapFont__Deserialize", "CDXFrontEnd__RenderStart", "3040", "1085"), failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs_instructions_vtables(failures)
        check_queue_and_backup(failures)
        check_docs(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"exception: {exc}")

    if failures:
        print("Wave596 DXFont/CDXFrontEnd probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave596 DXFont/CDXFrontEnd probe: PASS")
    print("Validated 7 saved signatures/comments/tags, dry/apply/final-dry logs, post exports, vtable slots, queue telemetry, backup summary, and public docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
